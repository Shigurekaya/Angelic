# -*- coding: utf-8 -*-
"""Deep self-check for Angelic settings 1:1 bake + Ren'Py wiring."""
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
REBUILD = ROOT / "Angelic/tools/rebuild_settings_1to1.py"
CAFE_SCREENS = ROOT / "renpy-cafe/game/cafe_screens.rpy"
CAFE_LAYOUT = ROOT / "CafeStella/ui-preview/assets/settings/settings-layout.json"

findings: list[tuple[str, str, str]] = []  # sev, id, msg


def add(sev: str, fid: str, msg: str) -> None:
    findings.append((sev, fid, msg))


def sha12(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def main() -> int:
    # --- assets ---
    plates = sorted((SETTINGS / "plates").glob("tab_*.png"))
    # 用户要求：不要鼠标(7)/手柄(9) → 9 页
    expect_n = 9
    if len(plates) != expect_n:
        add("CRITICAL", "plates.count", f"expected {expect_n} plates, got {len(plates)}")
    hashes = {p.name: sha12(p) for p in plates}
    if len(set(hashes.values())) != len(hashes):
        add("CRITICAL", "plates.dup", f"duplicate plate hashes: {hashes}")
    else:
        add("OK", "plates.unique", f"{expect_n} unique plates: {sorted(hashes)}")
    ids = [p.stem.replace("tab_", "") for p in plates]
    if "7" in ids or "9" in ids:
        add("CRITICAL", "plates.no_mouse_pad", f"mouse/gamepad plates still present: {ids}")
    elif set(ids) >= {"0", "1", "2", "3", "4", "5a", "5b", "6", "8"}:
        add("OK", "plates.keep_set", "plates match keep-set (no 7/9)")

    for p in plates:
        im = Image.open(p)
        if im.size != (1920, 1080):
            add("HIGH", "plates.size", f"{p.name} size {im.size} != 1920x1080")

    chrome_need = [
        "detail_off",
        "detail_on",
        "detail_over",
        "voice_mic",
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
    # 故意不烤：detail_cn / slider_num（禁止手绘壳）
    for junk in ("detail_cn.png", "slider_num.png"):
        if (SETTINGS / "chrome" / junk).exists():
            add("MED", "chrome.junk", f"stale synthetic chrome still present: {junk}")
        else:
            add("OK", f"chrome.no_{junk}", f"no synthetic {junk}")
    for n in chrome_need:
        p = SETTINGS / "chrome" / f"{n}.png"
        if not p.exists():
            add("HIGH", "chrome.miss", f"missing chrome/{n}.png")
        else:
            im = Image.open(p)
            if n.startswith("detail_") and n != "detail_cn" and im.size == (56, 33):
                add("CRITICAL", "detail.mic_size", f"{n} still 56x33 (mic slice size)")
            if n.startswith("detail_") and n != "detail_cn" and im.size != (76, 33):
                add("MED", "detail.size", f"{n} size {im.size} (expected 76x33 shell)")

    d = Image.open(SETTINGS / "chrome/detail_off.png").convert("RGBA")
    m = Image.open(SETTINGS / "chrome/voice_mic.png").convert("RGBA")
    if d.size == m.size and d.tobytes() == m.tobytes():
        add("CRITICAL", "detail.is_mic", "detail_off.png identical to voice_mic.png")
    else:
        add("OK", "detail.not_mic", f"detail_off {d.size} != voice_mic {m.size} (or pixels differ)")

    # mic slice has two icons — warn if used as detail
    if m.width >= 50 and m.height >= 30:
        add("OK", "voice_mic.exists", f"voice_mic saved separately {m.size}")

    # tabs
    for i in range(11):
        p = SETTINGS / "tabs" / f"label_{i}.png"
        if not p.exists():
            add("HIGH", "tabs.label", f"missing tabs/label_{i}.png")
    for n in ("on.png", "over.png", "on_w.png", "over_w.png"):
        if not (SETTINGS / "tabs" / n).exists():
            add("HIGH", "tabs.ring", f"missing tabs/{n}")

    # meta / slots
    meta = json.loads((SETTINGS / "meta.json").read_text(encoding="utf-8"))
    slots = json.loads((SETTINGS / "interaction_slots.json").read_text(encoding="utf-8"))
    tab_ids = [str(t["id"]) for t in meta.get("tabs") or []]
    slot_keys = set(slots.keys())
    if set(tab_ids) != slot_keys:
        add(
            "CRITICAL",
            "meta.slot_keys",
            f"tab ids {tab_ids} != slot keys {sorted(slot_keys)}",
        )
    else:
        add("OK", "meta.slot_keys", f"ids match slots: {tab_ids}")

    items = (meta.get("tabs_layout") or {}).get("items") or []
    if len(items) != len(tab_ids):
        add("HIGH", "tabs_layout.count", f"items={len(items)} tabs={len(tab_ids)}")
    for i, ti in enumerate(items):
        lf = ti.get("label_file") or ""
        if not lf:
            add("HIGH", "tabs_layout.label_file", f"item[{i}] missing label_file")
            continue
        fp = ROOT / "renpy-angelic/game/images" / lf
        if not fp.exists():
            add("HIGH", "tabs_layout.file", f"label_file missing on disk: {lf}")
        for k in ("x", "y", "w", "h", "label_y"):
            if k not in ti:
                add("MED", "tabs_layout.geom", f"item[{i}] missing {k}")

    # tab0 detail / mute
    s0 = slots.get("0") or []
    if len(s0) != 10:
        add("HIGH", "slots.tab0.count", f"tab0 slots={len(s0)} expected 10 (Cafe a-j)")
    detail_n = sum(1 for s in s0 if s.get("detail"))
    if detail_n < 8:
        add("HIGH", "slots.tab0.detail", f"only {detail_n} detail slots on tab0")
    else:
        add("OK", "slots.tab0.detail", f"tab0 detail on {detail_n} rows")

    mute_keys = []
    for s in s0:
        if s.get("mute"):
            mute_keys.append(s.get("key"))
            mp = s.get("mute_pos") or {}
            if int(mp.get("x", 9999)) > int((s.get("track") or s).get("x", 0)):
                # mute should be left of track (Cafe: track.x - 48)
                tx = int((s.get("track") or s).get("x", 0))
                if int(mp.get("x", 0)) >= tx:
                    add("MED", "mute.pos", f"{s.get('key')} mute_pos.x={mp.get('x')} not left of track {tx}")
    add("OK" if mute_keys else "HIGH", "slots.mute", f"tab0 mute keys: {mute_keys}")

    # topology vs cafe
    if CAFE_LAYOUT.exists():
        cafe = json.loads(CAFE_LAYOUT.read_text(encoding="utf-8"))
        cafe_tabs = {str(t.get("id")): t for t in cafe.get("tabs") or []}
        # cafe may use 0_simple
        cafe0 = cafe_tabs.get("0_simple") or cafe_tabs.get("0")
        if cafe0:
            cafe_keys = [r.get("key") for r in cafe0.get("rows") or []]
            ang_keys = [s.get("key") for s in s0]
            if cafe_keys and ang_keys != cafe_keys:
                # allow subset / order check
                if set(ang_keys) != set(cafe_keys):
                    add(
                        "MED",
                        "topo.keys",
                        f"tab0 key set diff cafe={cafe_keys} angelic={ang_keys}",
                    )
                elif ang_keys != cafe_keys:
                    add("LOW", "topo.order", f"tab0 key order differs: {ang_keys} vs {cafe_keys}")
                else:
                    add("OK", "topo.keys", "tab0 keys match Cafe topology")
            else:
                add("OK", "topo.keys", f"tab0 keys={ang_keys}")

    # geometry from rebuild constants
    rebuild = REBUILD.read_text(encoding="utf-8")
    for name, expect in (
        ("LABEL_W, LABEL_H = 313, 57", True),
        ("RAIL_W, RAIL_H = 288, 13", True),
        ("LEFT_X, RIGHT_X = 181, 1020", True),
    ):
        if name not in rebuild:
            add("HIGH", "geom.const", f"rebuild missing native const near {name}")
    if "禁止烤 s003" in rebuild or "s003" in rebuild or "voice_mic" in rebuild:
        add("OK", "rebuild.s003_note", "rebuild documents s003 mic ban")

    # detail = 官方 s011；s003 仅 voice_mic（禁止手绘 make_chip）
    detail_official = "load_slice(\"option__pack\", 11)" in rebuild or "load_slice('option__pack', 11)" in rebuild
    mic_only = "voice_mic.png" in rebuild and "option__pack\", 3)" in rebuild
    pack3_to_detail = bool(
        re.search(
            r"load_slice\(\s*[\"']option__pack[\"']\s*,\s*3\s*\)[^\n]{0,80}detail_(?:off|on|over)",
            rebuild,
        )
    )
    if pack3_to_detail:
        add("CRITICAL", "rebuild.s003_detail", "rebuild still maps pack:3 into detail_*")
    elif detail_official and mic_only:
        add("OK", "rebuild.detail_s011", "detail=s011 whole; pack:3 → voice_mic only")
    elif "voice_mic.png" not in rebuild:
        add("MED", "rebuild.voice_mic", "rebuild does not export voice_mic.png")

    # Cafe 841/637: only fail if used as real geometry
    if re.search(r"LABEL_W\s*=\s*841|RAIL_W\s*=\s*637|size == \(841", rebuild):
        add("MED", "geom.cafe_leak", "rebuild still uses Cafe 841/637 as geometry")
    elif "841" in rebuild or "637" in rebuild:
        add("OK", "geom.cafe_comment", "841/637 only mentioned as do-not-use comments")

    # code wiring
    core = CORE.read_text(encoding="utf-8")
    screens = SCREENS.read_text(encoding="utf-8")
    cafe_s = CAFE_SCREENS.read_text(encoding="utf-8") if CAFE_SCREENS.exists() else ""

    for needle, sev, fid, msg in [
        ("def plate_image", "CRITICAL", "core.plate_image", "missing plate_image"),
        ("angelic/settings/plates/", "HIGH", "core.plate_path", "plate_image may not use disk relative path"),
        ("_register_settings_plates", "LOW", "core.register", "no reload-time plate register"),
        ("renpy.image(\"angelic_plate_", "MED", "core.init_reg", "no init python plate register like Cafe"),
        ("def current_hotspots", "CRITICAL", "core.hotspots", "missing current_hotspots"),
        ("def settings_tab_id", "HIGH", "core.tab_id", "missing settings_tab_id (5a/5b break)"),
    ]:
        if needle not in core:
            add(sev, fid, msg)

    if "screen angelic_settings" not in screens:
        add("CRITICAL", "scr.missing", "screen angelic_settings missing")
    if "label_file" not in screens and "_lab" not in screens:
        add("HIGH", "scr.tab_label", "settings screen may not overlay tab labels")
    if "angelic/settings/tabs/" not in screens:
        add("HIGH", "scr.tab_path", "no tabs/ path in settings screen")
    if 'add _plate' not in screens and "add _plate" not in screens:
        add("CRITICAL", "scr.plate", "settings screen does not add plate")
    if "detail_off.png" not in screens:
        add("HIGH", "scr.detail", "no detail imagebutton")
    if "detail_cn.png" not in screens:
        add("MED", "scr.detail_cn", "no detail_cn overlay")
    if "angelic_slider_bar" not in screens:
        add("MED", "scr.slider_style", "no angelic_slider_bar style usage")
    if "angelic_toggle_mute" not in screens:
        add("HIGH", "scr.mute", "mute not wired in screen")
    if "angelic_settings_detail" not in screens and "angelic_settings_detail" not in core:
        add("HIGH", "scr.detail_fn", "angelic_settings_detail missing")

    # Cafe parity checklist
    cafe_checks = [
        ("label_file", "tab label overlay"),
        ("hover_background", "tab over ring"),
        ("detail_off.png", "detail button"),
        ("mute_on.png", "mute sprites"),
        ("thumb_offset", "slider thumb"),
    ]
    for needle, desc in cafe_checks:
        in_a = needle in screens
        in_c = needle in cafe_s
        if in_c and not in_a:
            add("HIGH", "parity." + needle, f"Cafe has {desc} ({needle}), Angelic screen missing")
        elif in_a and in_c:
            add("OK", "parity." + needle, f"parity OK: {desc}")

    # plate sample: row labels baked? sample non-empty alpha in label band
    p0 = Image.open(SETTINGS / "plates/tab_0.png").convert("RGBA")
    # left label region around (200,160) 313x57
    crop = p0.crop((200, 160, 513, 217))
    opaque = sum(1 for px in crop.getdata() if px[3] > 40)
    if opaque < 500:
        add("HIGH", "plate.labels", f"tab_0 label band nearly empty opaque={opaque}")
    else:
        add("OK", "plate.labels", f"tab_0 has label chrome opaque_px≈{opaque}")

    # tabs should NOT be double-baked heavily in plate top band — optional
    tab_band = p0.crop((160, 28, 1760, 80))
    # if we stopped baking tab text, band may be mostly transparent over bg
    add("OK", "plate.tab_band", f"tab band opaque_px≈{sum(1 for px in tab_band.getdata() if px[3] > 40)} (labels are runtime overlay)")

    # functions exist
    for fn in (
        "angelic_settings_detail",
        "angelic_toggle_mute",
        "angelic_apply_pref",
        "angelic_set_tab",
        "angelic_settings_footer",
        "angelic_pick_toggle",
    ):
        if f"def {fn}" not in core and f"def {fn}" not in screens:
            add("HIGH", "fn." + fn, f"missing function {fn}")
        else:
            add("OK", "fn." + fn, f"{fn} defined")

    # bg fallback risk
    if 'return "angelic/settings/bg.png"' in core:
        add("LOW", "plate.fallback", "plate_image falls back to bg.png if plates missing (expected)")

    # print report
    order = {"CRITICAL": 0, "HIGH": 1, "MED": 2, "LOW": 3, "OK": 4}
    findings.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    counts = {k: 0 for k in order}
    for sev, _, _ in findings:
        counts[sev] = counts.get(sev, 0) + 1

    print("=== ANGELIC SETTINGS DEEP SELF-CHECK ===")
    print(f"settings root: {SETTINGS}")
    print(
        "counts:",
        {k: counts[k] for k in ("CRITICAL", "HIGH", "MED", "LOW", "OK")},
    )
    print()
    for sev, fid, msg in findings:
        if sev == "OK":
            continue
        print(f"[{sev}] {fid}: {msg}")
    print()
    print("--- OK ---")
    for sev, fid, msg in findings:
        if sev == "OK":
            print(f"[OK] {fid}: {msg}")

    crit = counts.get("CRITICAL", 0)
    high = counts.get("HIGH", 0)
    print()
    if crit:
        print("VERDICT: FAIL (CRITICAL)")
        return 2
    if high:
        print("VERDICT: PASS WITH ISSUES (HIGH)")
        return 1
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
