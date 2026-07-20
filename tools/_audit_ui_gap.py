# -*- coding: utf-8 -*-
"""Deep gap audit: original option packs vs renpy-angelic settings vs cafe."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from PIL import Image

ROOT = Path(r"D:/gamedev")
SLICES = ROOT / "Angelic/docs/ui-extract/pixel-reverse/_pack_slices"
TLG = ROOT / "Angelic/docs/ui-extract/pixel-reverse/tlg-png"
ANG = ROOT / "renpy-angelic/game/images/angelic/settings"
CAFE = ROOT / "renpy-cafe/game/images/cafe/settings"
PREV = ROOT / "Angelic/ui-preview/assets/settings"
REBUILD = ROOT / "Angelic/tools/rebuild_settings_1to1.py"


def list_png(d: Path):
    if not d.exists():
        return []
    return sorted(p for p in d.rglob("*.png") if p.is_file())


def pack_inventory():
    """Group slice folders / option-related assets."""
    by_pack = defaultdict(list)
    for p in SLICES.iterdir() if SLICES.exists() else []:
        if p.is_dir():
            pngs = list(p.glob("*.png"))
            by_pack[p.name] = pngs
        elif p.suffix.lower() == ".png":
            by_pack["_root"].append(p)
    return by_pack


def main():
    print("=== FILE COUNTS ===")
    for name, d in [
        ("angelic_settings", ANG),
        ("cafe_settings", CAFE),
        ("angelic_preview", PREV),
        ("pack_slices", SLICES),
        ("tlg_png", TLG),
    ]:
        n = len(list_png(d)) if d.exists() else -1
        print(f"  {name}: {n} png @ {d}")

    print("\n=== ANGELIC SETTINGS TREE ===")
    for sub in ["", "plates", "chrome", "tabs"]:
        d = ANG / sub if sub else ANG
        files = [p.name for p in d.glob("*") if p.is_file()] if d.exists() else []
        print(f"  {sub or '.'}: {len(files)} files -> {sorted(files)[:30]}{'...' if len(files)>30 else ''}")

    print("\n=== CAFE SETTINGS TREE (top-level dirs) ===")
    if CAFE.exists():
        for p in sorted(CAFE.iterdir()):
            if p.is_dir():
                print(f"  {p.name}/: {len(list_png(p))} png")
            else:
                print(f"  {p.name}")

    print("\n=== OPTION-RELATED PACK SLICES ===")
    packs = pack_inventory()
    option_packs = {k: v for k, v in packs.items() if "option" in k.lower() or k.startswith("opt")}
    # also print largest packs
    ranked = sorted(packs.items(), key=lambda kv: -len(kv[1]))
    print(f"  total pack dirs: {len(packs)}")
    print("  top packs by slice count:")
    for k, v in ranked[:25]:
        print(f"    {k}: {len(v)}")
    print("  option* packs:")
    for k, v in sorted(option_packs.items()):
        sizes = []
        for p in v[:5]:
            try:
                im = Image.open(p)
                sizes.append(f"{p.stem}{im.size}")
            except Exception:
                sizes.append(p.name)
        print(f"    {k}: {len(v)}  sample={sizes}")

    print("\n=== TLG option bg / chrome ===")
    if TLG.exists():
        opts = sorted(TLG.glob("*option*")) + sorted(TLG.glob("*opt*"))
        for p in opts:
            try:
                im = Image.open(p)
                print(f"  {p.name}: {im.size}")
            except Exception:
                print(f"  {p.name}")

    print("\n=== REBUILD: what real slices does it load? ===")
    text = REBUILD.read_text(encoding="utf-8")
    import re
    loads = re.findall(r'load_slice\(\s*[\"\']([^\"\']+)[\"\']\s*,\s*(\d+)\s*\)', text)
    print(f"  load_slice calls: {loads}")
    make_chip = text.count("make_chip(")
    print(f"  make_chip( synthetic count: {make_chip}")
    # which slices exist for option__pack
    op = SLICES / "option__pack"
    if op.exists():
        ops = sorted(op.glob("*.png"))
        print(f"  option__pack slices on disk: {len(ops)}")
        for p in ops:
            im = Image.open(p)
            print(f"    {p.name}: {im.size}")
    else:
        # maybe naming differs
        cand = [k for k in packs if "option" in k and "pack" in k]
        print(f"  option__pack dir missing; candidates {cand}")
        for k in cand:
            for p in sorted(packs[k])[:40]:
                im = Image.open(p)
                print(f"    {k}/{p.name}: {im.size}")

    print("\n=== CAFE CHROME vs ANGELIC CHROME ===")
    cafe_chrome = {p.name for p in (CAFE / "chrome").glob("*.png")} if (CAFE / "chrome").exists() else set()
    ang_chrome = {p.name for p in (ANG / "chrome").glob("*.png")} if (ANG / "chrome").exists() else set()
    print(f"  cafe chrome: {len(cafe_chrome)}  angelic chrome: {len(ang_chrome)}")
    print(f"  only in cafe: {sorted(cafe_chrome - ang_chrome)[:40]}")
    print(f"  only in angelic: {sorted(ang_chrome - cafe_chrome)}")

    print("\n=== CAFE EXTRA DIRS NOT IN ANGELIC ===")
    cafe_dirs = {p.name for p in CAFE.iterdir() if p.is_dir()} if CAFE.exists() else set()
    ang_dirs = {p.name for p in ANG.iterdir() if p.is_dir()} if ANG.exists() else set()
    print(f"  cafe dirs: {sorted(cafe_dirs)}")
    print(f"  angelic dirs: {sorted(ang_dirs)}")
    print(f"  missing dirs: {sorted(cafe_dirs - ang_dirs)}")

    # plate content density: how much non-bg unique content
    print("\n=== PLATE CONTENT DENSITY (non-near-bg pixels) ===")
    bg = Image.open(ANG / "bg.png").convert("RGBA") if (ANG / "bg.png").exists() else None
    for p in sorted((ANG / "plates").glob("tab_*.png"))[:3]:
        im = Image.open(p).convert("RGBA")
        if bg and bg.size == im.size:
            # count pixels differing from bg
            import numpy as np
            a = np.array(im)
            b = np.array(bg)
            diff = (np.abs(a.astype(int) - b.astype(int)).sum(axis=2) > 30).sum()
            print(f"  {p.name}: diff_from_bg_px={int(diff)} ({100*diff/(im.width*im.height):.1f}%)")
        else:
            opaque = sum(1 for px in im.getdata() if px[3] > 40)
            print(f"  {p.name}: opaque={opaque}")

    # screen refs existence
    print("\n=== SCREEN-REFERENCED PATHS EXIST? ===")
    screens = (ROOT / "renpy-angelic/game/angelic_screens.rpy").read_text(encoding="utf-8")
    refs = sorted(set(re.findall(r'angelic/settings/[a-zA-Z0-9_./%-]+', screens)))
    miss = []
    for r in refs:
        # skip format strings
        if "%" in r:
            continue
        fp = ROOT / "renpy-angelic/game/images" / r
        if not fp.exists():
            miss.append(r)
    print(f"  refs={len(refs)} missing={len(miss)}")
    for m in miss:
        print(f"    MISS {m}")

    # meta footer cn paths
    meta = json.loads((ANG / "meta.json").read_text(encoding="utf-8"))
    for f in meta.get("footer") or []:
        cn = f.get("cn") or ""
        if cn:
            fp = ROOT / "renpy-angelic/game/images" / cn
            print(f"  footer cn {cn}: exists={fp.exists()}")


if __name__ == "__main__":
    main()
