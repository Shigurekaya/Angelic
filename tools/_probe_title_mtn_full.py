# -*- coding: utf-8 -*-
"""Probe FreeMote title_bg.mtn geometry for Angelic chars."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
RESX = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.resx.json")
SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
LAYERS = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\layers")


def walk(L, depth=0):
    lab = L.get("label") or ""
    pad = "  " * depth
    meta = {
        "label": lab,
        "type": L.get("type"),
        "coordinate": L.get("coordinate"),
        "transformOrder": L.get("transformOrder"),
        "inheritMask": L.get("inheritMask"),
        "visible": L.get("visible"),
    }
    print(pad + json.dumps(meta, ensure_ascii=False))
    for fr in L.get("frameList") or []:
        c = fr.get("content") or {}
        if not c and fr.get("type") == 0:
            print(pad + f"  t={fr.get('time')} END")
            continue
        keep = {}
        for k in ("coord", "opa", "zx", "zy", "ox", "oy", "src", "mask"):
            if k in c:
                keep[k] = c[k]
        if keep:
            print(pad + f"  t={fr.get('time')} " + json.dumps(keep, ensure_ascii=False))
    for ch in L.get("children") or []:
        walk(ch, depth + 1)


def main():
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    print("root keys", list(mtn.keys()))
    print("object keys", list(mtn["object"].keys()))

    cm = mtn["object"]["title_bg"]["motion"]["char_move"]
    print("\n=== char_move lastTime", cm.get("lastTime"), "===")
    for L in cm.get("layer") or []:
        walk(L)

    print("\n=== logo_cn ===")
    for L in mtn["object"]["logo"]["motion"]["logo_cn"].get("layer") or []:
        walk(L)

    print("\n=== resx ===")
    resx = json.loads(RESX.read_text(encoding="utf-8"))
    print(json.dumps(resx.get("Resources"), ensure_ascii=False, indent=2))

    print("\n=== source PNG sizes ===")
    for p in sorted(SRC.glob("*.png")):
        im = Image.open(p)
        print(f"{p.stat().st_size:8d} {im.size[0]:4d}x{im.size[1]:4d}  {p.name}")

    # Logo coord vs logo image: infer pivot convention
    logo_layer = mtn["object"]["logo"]["motion"]["logo_cn"]["layer"][0]
    # find coord
    for fr in logo_layer.get("frameList") or []:
        c = fr.get("content") or {}
        if "coord" in c:
            print("\nlogo first coord", c["coord"], "src", c.get("src"))
            logo_im = Image.open(SRC / "logo_cn-logo_cn.png")
            print("logo_cn size", logo_im.size)
            cx, cy = c["coord"][0], c["coord"][1]
            # if coord is center:
            print("  if center->TL", (cx - logo_im.width / 2, cy - logo_im.height / 2))
            # if coord is TL:
            print("  if TL->pos", (cx, cy))
            # if coord is center of 1920x1080 parent:
            print("  if center+origin960,540 TL", (960 + cx - logo_im.width / 2, 540 + cy - logo_im.height / 2))
            print("  if center+origin960,604 TL", (960 + cx - logo_im.width / 2, 604 + cy - logo_im.height / 2))
            break


if __name__ == "__main__":
    main()
