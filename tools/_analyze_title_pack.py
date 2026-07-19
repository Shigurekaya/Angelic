# -*- coding: utf-8 -*-
"""Analyze Angelic title_locale_cn pack + find layout clues."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(r"D:/gamedev/Angelic")
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
PBD = ROOT / "docs/ui-extract/pixel-reverse/pbd-layers"
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
OUT = ROOT / "docs/ui-extract/pixel-reverse/_text_preview"
OUT.mkdir(parents=True, exist_ok=True)


def magenta_mask(im: Image.Image):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)
    return im


def connected_components(im: Image.Image, min_area=80):
    """Find non-transparent bounding boxes."""
    w, h = im.size
    px = im.load()
    seen = [[False] * w for _ in range(h)]
    boxes = []

    def neigh(x, y):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                    r, g, b, a = px[nx, ny]
                    if a > 10:
                        yield nx, ny

    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                continue
            r, g, b, a = px[x, y]
            if a <= 10:
                seen[y][x] = True
                continue
            # BFS
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
                for nx, ny in neigh(cx, cy):
                    seen[ny][nx] = True
                    stack.append((nx, ny))
            if area >= min_area and (maxx - minx) > 20 and (maxy - miny) > 10:
                boxes.append((minx, miny, maxx + 1, maxy + 1, area))
    boxes.sort(key=lambda b: (b[1], b[0]))
    return boxes


def main():
    pack = magenta_mask(Image.open(TLG / "title_locale_cn__pack.png"))
    pack.save(OUT / "title_locale_cn_alpha.png")
    boxes = connected_components(pack, min_area=200)
    print("title_locale_cn boxes", len(boxes))
    for i, (x0, y0, x1, y1, area) in enumerate(boxes):
        crop = pack.crop((x0, y0, x1, y1))
        crop.save(OUT / f"title_btn_{i:02d}.png")
        print(f"  {i:02d}: ({x0},{y0})-({x1},{y1}) {x1-x0}x{y1-y0} area={area}")

    # also title pack chrome
    chrome = magenta_mask(Image.open(TLG / "title__pack.png"))
    chrome.save(OUT / "title_pack_alpha.png")
    print("title__pack size", chrome.size)

    # option bg size
    for n in ["option__bg0.png", "file_load__bg0.png", "extra__bg0.png", "scnchart__bg0.png"]:
        im = Image.open(TLG / n)
        print(n, im.size)

    # look for cglist / flow data
    for pat in ["**/cglist*", "**/flow_texts*", "**/musictitle*", "**/*chart*", "**/extra*.csv", "**/extra*.ini"]:
        hits = list(FILT.glob(pat)) + list((ROOT / "docs/ui-extract/full-static").glob(pat))
        print(pat, len(hits), [str(h.relative_to(ROOT))[:80] for h in hits[:5]])

    # title.json layer ids that look like buttons
    doc = json.loads((PBD / "title.json").read_text(encoding="utf-8"))
    ids = [L.get("layer_id") for L in doc.get("layers") or []]
    print("title layer_ids sample:", ids[:40])
    interesting = [i for i in ids if i and any(k in str(i).lower() for k in (
        "start", "load", "cont", "flow", "extra", "after", "system", "exit", "opt", "lang", "btn", "menu"
    ))]
    print("interesting:", interesting)

    loc = json.loads((PBD / "title_locale_cn.json").read_text(encoding="utf-8"))
    lids = [L.get("layer_id") for L in loc.get("layers") or []]
    print("title_locale_cn layers:", lids)


if __name__ == "__main__":
    main()
