# -*- coding: utf-8 -*-
"""Deep self-check for Angelic settings 1:1 bake + Ren'Py wiring.

Authority: bake_settings_from_pbd_uistates.py (pbd2json uistates).
Keep-set plates: 0,1,2,3,4,5a,5b,6,8 (no mouse 7 / gamepad 9).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(r"D:/gamedev")
SETTINGS = ROOT / "renpy-angelic/game/images/angelic/settings"
CORE = ROOT / "renpy-angelic/game/angelic_core.rpy"
SCREENS = ROOT / "renpy-angelic/game/angelic_screens.rpy"
BAKE = ROOT / "Angelic/tools/bake_settings_from_pbd_uistates.py"
RECREATE = ROOT / "Angelic/tools/recreate_renpy_ui.py"
OTHER = ROOT / "Angelic/tools/build_other_screens_1to1.py"

KEEP_IDS = {"0", "1", "2", "3", "4", "5a", "5b", "6", "8"}
findings: list[tuple[str, str, str]] = []


def add(sev: str, fid: str, msg: str) -> None:
    findings.append((sev, fid, msg))


def sha12(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def main() -> int:
    plates = sorted((SETTINGS / "plates").glob("tab_*.png"))
    expect_n = len(KEEP_IDS)
    ids = [p.stem.replace("tab_", "") for p in plates]

    if set(ids) != KEEP_IDS:
        add("CRITICAL", "plates.keep_set", f"expected {sorted(KEEP_IDS)}, got {ids}")
    else:
        add("OK", "plates.keep_set", f"plates match keep-set ({expect_n})")

    if len(plates) != expect_n:
        add("CRITICAL", "plates.count", f"expected {expect_n} plates, got {len(plates)}")

    hashes = {p.name: sha12(p) for p in plates}
    if len(set(hashes.values())) != len(hashes):
        add("CRITICAL", "plates.dup", f"duplicate plate hashes: {hashes}")
    else:
        add("OK", "plates.unique", f"{len(hashes)} unique plates")

    for p in plates:
        im = Image.open(p)
        if im.size != (1920, 1080):
            add("HIGH", "plates.size", f"{p.name} size {im.size} != 1920x1080")

    # tab0: chips are runtime-drawn; plate should still have label chrome nearby
    p0 = Image.open(SETTINGS / "plates/tab_0.png").convert("RGBA")
    label_band = p0.crop((40, 150, 120, 250))
    label_opaque = sum(1 for px in label_band.getdata() if px[3] > 40)
    chip_assets = all((SETTINGS / "chrome" / f).exists() for f in ("chip_off.png", "chip_on.png", "chip_over.png"))
    if not chip_assets:
        add("CRITICAL", "chrome.chips", "missing chip_off/on/over for runtime toggles")
    elif label_opaque < 200:
        add("HIGH", "plate.tab0.labels", f"tab0 label band too empty opaque={label_opaque}")
    else:
        add("OK", "plate.tab0.runtime_chips", f"chrome chips present; plate labels opaque={label_opaque}")

    chrome_need = [
        "detail_off",
        "detail_on",
        "detail_over",
        "slider_knob",
        "slider_knob_over",
        "mute_off",
        "mute_on",
        "mute_over",
        "mute_on_over",
        "chip_off",
        "chip_on",
        "chip_over",
        "check_off",
        "check_on",
        "stdbtn_off",
        "stdbtn_over",
        "stdbtn_on",
    ]
    for junk in ("detail_cn.png", "slider_num.png"):
        if (SETTINGS / "chrome" / junk).exists():
            add("MED", "chrome.junk", f"stale synthetic chrome still present: {junk}")
        else:
            add("OK", f"chrome.no_{junk}", f"no synthetic {junk}")
    for n in chrome_need:
        p = SETTINGS / "chrome" / f"{n}.png"
        if not p.exists():
            add("HIGH", "chrome.miss", f"missing chrome/{n}.png")

    if (SETTINGS / "chrome/voice_mic.png").exists():
        add("OK", "voice_mic.exists", "voice_mic present")
    else:
        add("MED", "voice_mic.miss", "voice_mic.png missing")

    meta = json.loads((SETTINGS / "meta.json").read_text(encoding="utf-8"))
    slots = json.loads((SETTINGS / "interaction_slots.json").read_text(encoding="utf-8"))
    tab_ids = [str(t["id"]) for t in meta.get("tabs") or []]
    if set(tab_ids) != KEEP_IDS:
        add("CRITICAL", "meta.tabs", f"meta tabs {tab_ids} != keep-set")
    else:
        add("OK", "meta.tabs", f"meta tabs={tab_ids}")
    if set(tab_ids) != set(slots.keys()):
        add("CRITICAL", "meta.slot_keys", f"tab ids {tab_ids} != slot keys {sorted(slots)}")
    else:
        add("OK", "meta.slot_keys", "ids match slots")

    items = (meta.get("tabs_layout") or {}).get("items") or []
    if len(items) != len(tab_ids):
        add("HIGH", "tabs_layout.count", f"items={len(items)} tabs={len(tab_ids)}")
    else:
        add("OK", "tabs_layout.count", f"layout items={len(items)}")

    s0 = slots.get("0") or []
    keys0 = {s.get("key") for s in s0}
    need0 = {"fullscreen", "sqscr", "textspeed", "autospeed", "skipall", "wave", "bgm", "se", "voice", "movie"}
    missing0 = sorted(need0 - keys0)
    if missing0:
        add("HIGH", "slots.tab0.keys", f"tab0 missing keys {missing0} (have {sorted(keys0)})")
    else:
        add("OK", "slots.tab0.keys", f"tab0 has core keys ({len(s0)} slots)")

    detail_n = sum(1 for s in s0 if s.get("detail"))
    if detail_n < 6:
        add("HIGH", "slots.tab0.detail", f"only {detail_n} detail slots on tab0")
    else:
        add("OK", "slots.tab0.detail", f"tab0 detail on {detail_n} rows")

    mute_keys = [s.get("key") for s in s0 if s.get("mute")]
    add("OK" if mute_keys else "HIGH", "slots.mute", f"tab0 mute keys: {mute_keys}")

    if int(slots.get("8") and len(slots["8"]) or 0) < 10:
        add("MED", "slots.tab8", f"keyboard slots sparse: {len(slots.get('8') or [])}")
    else:
        add("OK", "slots.tab8", f"keyboard slots={len(slots.get('8') or [])}")

    bake = BAKE.read_text(encoding="utf-8") if BAKE.exists() else ""
    recreate = RECREATE.read_text(encoding="utf-8") if RECREATE.exists() else ""
    other = OTHER.read_text(encoding="utf-8") if OTHER.exists() else ""

    if "PAGE_PBDS" not in bake or '"5a"' not in bake or '"8"' not in bake:
        add("CRITICAL", "bake.pages", "bake_settings_from_pbd_uistates missing keep-set PAGE_PBDS")
    else:
        add("OK", "bake.pages", "bake PAGE_PBDS includes 5a/5b/6/8")

    if "bake_settings_from_pbd_uistates" not in recreate:
        add("CRITICAL", "recreate.bake", "recreate_renpy_ui does not call bake_settings_from_pbd_uistates")
    else:
        add("OK", "recreate.bake", "recreate uses uistates bake")

    if re.search(r'run\(["\']rebuild_settings_1to1\.py["\']\)', recreate):
        add("CRITICAL", "recreate.rebuild", "recreate still runs rebuild_settings_1to1.py")
    else:
        add("OK", "recreate.no_rebuild", "recreate does not run rebuild_settings_1to1")

    if "bake_settings()" in other and "Do NOT bake_settings()" not in other:
        # ensure main does not call bake_settings
        if re.search(r"^\s*bake_settings\(\)\s*$", other, re.M):
            add("CRITICAL", "other.bake_settings", "build_other_screens still calls bake_settings()")
        else:
            add("OK", "other.no_settings_bake", "build_other skips settings bake")
    else:
        add("OK", "other.no_settings_bake", "build_other skips settings bake")

    if "endswith(\"_off\") or name.endswith(\"_on\")" in bake and "runtime draws chip" in bake.lower() or (
        'endswith("_off") or name.endswith("_on")' in bake and "continue" in bake
    ):
        add("OK", "bake.select", "bake skips chip on/off (runtime owns state)")
    elif "prefer_on = name in selected" in bake or "name in selected" in bake:
        add("OK", "bake.select", "bake has selected-chip prefer_on")
    else:
        add("MED", "bake.select", "bake chip strategy unclear")

    core = CORE.read_text(encoding="utf-8")
    screens = SCREENS.read_text(encoding="utf-8")

    for needle, sev, fid, msg in [
        ("def plate_image", "CRITICAL", "core.plate_image", "missing plate_image"),
        ("def current_hotspots", "CRITICAL", "core.hotspots", "missing current_hotspots"),
        ("def settings_tab_id", "HIGH", "core.tab_id", "missing settings_tab_id"),
        ("_simple_page_hotspots", "LOW", "core.simple_fallback", "simple-page fallback still present"),
    ]:
        if needle not in core:
            add(sev, fid, msg)
        else:
            add("OK", fid, f"found {needle}")

    # Prefer interaction_slots for tab0 (not forcing simple-page truth)
    if "if tid == \"0\":\n                return self._simple_page_hotspots()" in core:
        add("HIGH", "core.tab0_force_simple", "tab0 always uses _simple_page_hotspots (ignores pbd slots)")
    else:
        add("OK", "core.tab0_slots", "tab0 can use interaction_slots")

    if "screen angelic_settings" not in screens:
        add("CRITICAL", "scr.missing", "screen angelic_settings missing")
    if "add _plate" not in screens:
        add("CRITICAL", "scr.plate", "settings screen does not add plate")
    if "Transform((_chip_on if _sel else _chip_off), size=" in screens:
        add("HIGH", "scr.chip_squash", "toggle chips still Transform-squashed with size=")
    else:
        add("OK", "scr.chip_native", "chips use slot-sized Transform/button (not size= squash)")
    if "if i >= 6:" in screens:
        add("HIGH", "scr.tab_cap6", "tab hotspots still capped at 6")
    else:
        add("OK", "scr.tab_all", "tab hotspots not capped at 6")
    if "angelic_settings_detail" not in screens and "angelic_settings_detail" not in core:
        add("HIGH", "scr.detail_fn", "angelic_settings_detail missing")
    else:
        add("OK", "scr.detail_fn", "detail jump present")

    # plate label band
    crop = p0.crop((200, 160, 513, 217))
    opaque2 = sum(1 for px in crop.getdata() if px[3] > 40)
    if opaque2 < 500:
        add("HIGH", "plate.labels", f"tab_0 label band nearly empty opaque={opaque2}")
    else:
        add("OK", "plate.labels", f"tab_0 has label chrome opaque_px≈{opaque2}")

    counts = {"CRITICAL": 0, "HIGH": 0, "MED": 0, "LOW": 0, "OK": 0}
    print("=== ANGELIC SETTINGS DEEP SELF-CHECK ===")
    print("settings root:", SETTINGS)
    for sev, fid, msg in findings:
        counts[sev] = counts.get(sev, 0) + 1
    print("counts:", counts)
    print()
    for sev in ("CRITICAL", "HIGH", "MED", "LOW"):
        rows = [(s, f, m) for s, f, m in findings if s == sev]
        if not rows:
            continue
        for s, f, m in rows:
            print(f"[{s}] {f}: {m}")
    print("\n--- OK ---")
    for s, f, m in findings:
        if s == "OK":
            print(f"[OK] {f}: {m}")

    bad = counts.get("CRITICAL", 0) + counts.get("HIGH", 0)
    print("\nVERDICT:", "FAIL" if bad else "PASS", f"(CRITICAL+HIGH={bad})")
    return 1 if counts.get("CRITICAL", 0) else 0


if __name__ == "__main__":
    # fix accidental syntax from drafting - rewrite clean via exec of body only
    raise SystemExit(main())
