# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/ui-extract/pixel-reverse/_text_preview/orig_only"
PREV = ROOT / "ui-preview/assets/title"


def stats(path: Path) -> None:
    im = Image.open(path).convert("RGBA")
    px = im.load()
    black = trans = other = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a <= 10:
                trans += 1
            elif r <= 18 and g <= 18 and b <= 18:
                black += 1
            else:
                other += 1
    print(path.name, im.size, "trans", trans, "black", black, "other", other)


def main() -> None:
    for name in [
        "buttons/start_idle.png",
        "buttons/start_hover.png",
        "icon_lang.png",
        "icon_reload.png",
        "logo_cn.png",
        "bg0.png",
        "composite.png",
    ]:
        p = PREV / name
        if p.exists():
            stats(p)

    # Build language from ORIGINAL tiles only, layered like cafe stamp (no font, no invent)
    # plate s002, 文 from atlas white glyph ~23x24, A from s004, arrows if small glyphs
    atlas = Image.open(
        ROOT / "docs/ui-extract/pixel-reverse/tlg-png/langselect__pack.png"
    ).convert("RGBA")
    px = atlas.load()
    for y in range(atlas.height):
        for x in range(atlas.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)

    # extract white components
    w, h = atlas.size
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                continue
            r, g, b, a = px[x, y]
            if a < 40 or not (r > 200 and g > 200 and b > 200):
                seen[y][x] = True
                continue
            stack = [(x, y)]
            seen[y][x] = True
            minx = maxx = x
            miny = maxy = y
            area = 0
            while stack:
                cx, cy = stack.pop()
                area += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                            seen[ny][nx] = True
                            rr, gg, bb, aa = px[nx, ny]
                            if aa > 40 and rr > 200 and gg > 200 and bb > 200:
                                stack.append((nx, ny))
            bw, bh = maxx - minx + 1, maxy - miny + 1
            if 20 <= area <= 800 and bw <= 40 and bh <= 40:
                boxes.append((area, minx, miny, maxx + 1, maxy + 1, bw, bh))
    boxes.sort(reverse=True)
    print("glyph boxes", len(boxes))
    for i, row in enumerate(boxes[:8]):
        print(i, row)
        _a, x0, y0, x1, y1, bw, bh = row
        atlas.crop((x0, y0, x1, y1)).save(OUT / f"glyph_{i}_{bw}x{bh}.png")

    plate = Image.open(
        ROOT / "docs/ui-extract/pixel-reverse/_pack_slices/langselect__pack/s002_68x68.png"
    ).convert("RGBA")
    # only magenta key on plate, keep black border as original
    pp = plate.load()
    for y in range(plate.height):
        for x in range(plate.width):
            r, g, b, a = pp[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                pp[x, y] = (0, 0, 0, 0)

    # Use original slices: A = s004; 文 = best ~23x24 glyph
    A = Image.open(
        ROOT / "docs/ui-extract/pixel-reverse/_pack_slices/langselect__pack/s004_19x21.png"
    ).convert("RGBA")
    # key black on A
    ap = A.load()
    for y in range(A.height):
        for x in range(A.width):
            r, g, b, a = ap[x, y]
            if r <= 18 and g <= 18 and b <= 18:
                ap[x, y] = (0, 0, 0, 0)

    wen = None
    for row in boxes:
        _a, x0, y0, x1, y1, bw, bh = row
        if 20 <= bw <= 28 and 20 <= bh <= 28:
            wen = atlas.crop((x0, y0, x1, y1))
            break
    print("wen", None if wen is None else wen.size, "A", A.size)

    # Save pieces separately for Ren'Py layered display (NO homemade resize stamp)
    plate.save(OUT / "lang_plate_off.png")
    if wen is not None:
        wen.save(OUT / "lang_wen.png")
    A.save(OUT / "lang_A.png")


if __name__ == "__main__":
    main()
