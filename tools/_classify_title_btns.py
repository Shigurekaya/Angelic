# -*- coding: utf-8 -*-
"""Classify title_locale_cn crops by glow + approximate glyph width."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

AUDIT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_text_preview")


def glow_kind(im: Image.Image) -> str:
    im = im.convert("RGBA")
    px = im.load()
    ys = cs = ws = 0
    n = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            # skip near-white glyph core
            if r > 220 and g > 220 and b > 220:
                ws += 1
                continue
            n += 1
            # yellow/lime glow
            if r > 140 and g > 140 and b < 120:
                ys += 1
            # cyan/blue glow
            elif b > 140 and g > 80 and r < 160:
                cs += 1
    if n == 0:
        return "white"
    if ys > cs * 1.2 and ys > n * 0.25:
        return "yellow"
    if cs > ys * 1.2 and cs > n * 0.25:
        return "cyan"
    return "blue" if cs >= ys else "yellow"


def main():
    for i in range(24):
        p = AUDIT / f"title_btn_{i:02d}.png"
        if not p.exists():
            continue
        im = Image.open(p)
        print(f"{i:02d} {im.size[0]:3d}x{im.size[1]:2d} {glow_kind(im)}")


if __name__ == "__main__":
    main()
