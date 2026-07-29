# -*- coding: utf-8 -*-
"""Cafe-style: bake Angelic UI into renpy-angelic from official unpack.

Order matters: build plates/sprites first, then merge pbd2json coords (never strip idle paths).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\gamedev\Angelic")
TOOLS = ROOT / "tools"
PY = sys.executable


def run(script: str, *args: str) -> None:
    cmd = [PY, str(TOOLS / script), *args]
    print("\n>>>", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=str(ROOT))


def bake_bg_ui() -> None:
    from PIL import Image

    title = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title")
    logo_p = title / "logo_cn.png"
    if not logo_p.exists():
        raise SystemExit(f"missing {logo_p}")
    logo = Image.open(logo_p).convert("RGBA")
    for i in range(8):
        bg = Image.open(title / f"bg{i}.png").convert("RGBA")
        out = bg.copy()
        out.alpha_composite(logo)
        out.save(title / f"bg{i}_ui.png")
        print("wrote", f"bg{i}_ui.png")
    # mirror into preview
    prev = ROOT / "ui-preview" / "assets" / "title"
    prev.mkdir(parents=True, exist_ok=True)
    for i in range(8):
        src = title / f"bg{i}_ui.png"
        if src.exists():
            (prev / f"bg{i}_ui.png").write_bytes(src.read_bytes())


def main() -> int:
    # 1) geometry dump (idempotent)
    run("unpack_pbd2json_ui.py")
    run("build_settings_from_pbd2json.py")

    # 2) title sprites + hotspots with idle paths
    run("build_title_1to1.py")

    # 3) FreeMote title layers (intro) - AFTER build_title (merge-copy safe)
    form = TOOLS / "_form_title_from_mtn.py"
    if form.exists():
        run("_form_title_from_mtn.py")
    else:
        print("SKIP title mtn form missing; keep existing layers")

    # 4) bake static title finals (logo composite) before wire/sync
    bake_bg_ui()

    # 5) merge official PBD hitboxes without wiping idle/icons
    sys.path.insert(0, str(TOOLS))
    from complete_ui_unpack import wire_title_hotspots, wire_screen_hotspots, export_screen_atlas

    doc = wire_title_hotspots()
    print("title buttons", [(b["id"], b.get("idle"), b["x"], b["y"]) for b in doc["buttons"][:3]])
    print("icons", list((doc.get("icons") or {}).keys()))
    wire_screen_hotspots()
    export_screen_atlas()

    # 6) settings (pbd2json uistates authority) / other plates
    # Do NOT call rebuild_settings_1to1.py - it overwrites plates with empty label shells.
    run("bake_settings_from_pbd_uistates.py")
    run("build_other_screens_1to1.py")

    # 7) sync preview -> renpy
    run("sync_all_ui_to_renpy.py")

    # re-bake settings AFTER sync_all (sync may refresh assets but must not leave empty plates)
    run("bake_settings_from_pbd_uistates.py")

    # re-merge title wire after sync (preserve idle/icons from preview)
    doc = wire_title_hotspots()
    import shutil

    src_hs = ROOT / "ui-preview" / "assets" / "title" / "hotspots.json"
    if src_hs.exists():
        for dst in (
            Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\hotspots.json"),
            Path(r"D:\gamedev\renpy-angelic\game\images\angelic\assets\title\hotspots.json"),
        ):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_hs, dst)

    # selfcheck
    sc = Path(r"D:\gamedev\renpy-angelic\tools\_selfcheck_ui.py")
    if sc.exists():
        subprocess.call([PY, str(sc)])

    report = {
        "ok": True,
        "title_btn0": doc["buttons"][0] if doc.get("buttons") else None,
        "has_icons": list((doc.get("icons") or {}).keys()),
    }
    out = ROOT / "docs" / "ui-extract" / "pixel-reverse" / "RECREATE-RENPY-REPORT.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
