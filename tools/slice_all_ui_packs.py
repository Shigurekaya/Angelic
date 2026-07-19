# -*- coding: utf-8 -*-
"""Slice ALL Angelic UI pack atlases (magenta→alpha + connected components)."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

TLG = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/tlg-png")
OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_pack_slices")


def magenta_to_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)
            elif r >= 200 and b >= 200 and g <= 90 and abs(r - b) < 40:
                px[x, y] = (0, 0, 0, 0)
    return im


def connected_boxes(im: Image.Image, min_area: int = 80):
    w, h = im.size
    px = im.load()
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                continue
            if px[x, y][3] <= 10:
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
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                            if px[nx, ny][3] > 10:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                            else:
                                seen[ny][nx] = True
            if area >= min_area and (maxx - minx) >= 4 and (maxy - miny) >= 4:
                boxes.append((minx, miny, maxx + 1, maxy + 1, area))
    boxes.sort(key=lambda b: (b[1], b[0]))
    return boxes


def slice_one(png: Path) -> dict:
    stem = png.stem
    dest = OUT / stem
    dest.mkdir(parents=True, exist_ok=True)
    im = magenta_to_alpha(Image.open(png))
    im.save(dest / "_atlas_alpha.png")
    boxes = connected_boxes(im)
    meta = []
    for i, (x0, y0, x1, y1, area) in enumerate(boxes):
        crop = im.crop((x0, y0, x1, y1))
        name = f"s{i:03d}_{x1-x0}x{y1-y0}.png"
        crop.save(dest / name)
        meta.append({"i": i, "box": [x0, y0, x1, y1], "w": x1 - x0, "h": y1 - y0, "area": area, "file": name})
    (dest / "slices.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"stem": stem, "slices": len(meta), "atlas": list(im.size)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for png in sorted(TLG.glob("*.png")):
        if png.name == "manifest.json":
            continue
        info = slice_one(png)
        results.append(info)
        print(f"{info['stem']}: {info['slices']} slices @ {info['atlas']}")
    (OUT / "index.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "README.md").write_text(
        "# UI pack slices\n\n洋红透明后的连通域切片，供查看态/交互态像素对齐使用。\n"
        "落点需对照 `_orig_capture` 原作截图，勿照搬 CafeStella 布局。\n",
        encoding="utf-8",
    )
    print("TOTAL packs", len(results), "TOTAL slices", sum(r["slices"] for r in results))


if __name__ == "__main__":
    main()
