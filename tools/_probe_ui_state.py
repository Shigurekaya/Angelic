# -*- coding: utf-8 -*-
"""Probe Angelic UI extract readiness for renpy recreation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(r"D:/gamedev/Angelic")
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
PBD = ROOT / "docs/ui-extract/pixel-reverse/pbd-layers"
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
PREV = ROOT / "ui-preview/assets"


def summarize_hotspots(stem: str) -> None:
    p = PBD / f"{stem}.hotspots.json"
    if not p.exists():
        print(f"[MISS] {stem}.hotspots.json")
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    hs = d.get("hotspots") or []
    bd = d.get("bindings") or []
    with_xy = sum(1 for h in hs if any(k in h for k in ("left", "top", "x", "y", "cx", "cy")))
    print(f"[{stem}] hotspots={len(hs)} with_xy={with_xy} bindings={len(bd)}")
    for b in bd[:8]:
        print("  bind:", b.get("layer_id"), b.get("bindings"), b.get("geometry"))
    for h in hs[:5]:
        print("  hs:", {k: h.get(k) for k in ("layer_id", "left", "top", "x", "y", "cx", "cy", "width", "height", "cw", "ch")})


def main() -> None:
    print("=== packs tlg-png ===")
    packs = sorted(TLG.glob("*.png"))
    print("count", len(packs))
    for name in [
        "title__pack.png",
        "title_locale_cn__pack.png",
        "option__bg0.png",
        "option__pack.png",
        "file_load__bg0.png",
        "extra__bg0.png",
        "extra_cg__pack.png",
        "scnchart__bg0.png",
    ]:
        p = TLG / name
        print(f"  {name}: {'OK' if p.exists() else 'MISS'} {p.stat().st_size if p.exists() else ''}")

    print("=== title bgs filtered ===")
    for i in range(8):
        p = FILT / f"title_bg{i}.png"
        print(f"  title_bg{i}: {'OK' if p.exists() else 'MISS'}")
    logo = FILT / "locale/cn/title_logo_cn.png"
    print("  logo_cn:", "OK" if logo.exists() else "MISS", logo)

    print("=== locale cn files ===")
    loc = FILT / "locale/cn"
    if loc.exists():
        for f in sorted(loc.iterdir())[:30]:
            print(" ", f.name)

    print("=== preview assets ===")
    for sub in ["title", "settings", "load", "flowchart", "cg", "hotspots", "packs"]:
        d = PREV / sub
        n = len(list(d.glob("*"))) if d.exists() else -1
        print(f"  {sub}: {n}")

    for stem in ["title", "title_locale_cn", "option", "option_0simple", "file_load", "extra", "extra_cg", "scnchart"]:
        summarize_hotspots(stem)

    # title func
    func = FILT / "uipsd/func"
    if func.exists():
        print("=== title funcs ===")
        for f in sorted(func.glob("*.func")):
            print(" ", f.name, f.stat().st_size)


if __name__ == "__main__":
    main()
