# -*- coding: utf-8 -*-
"""Fast atlas band-split for Angelic option packs (no BFS)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OP = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_pack_slices/option__pack")
OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_gap_preview/crops")
OUT.mkdir(parents=True, exist_ok=True)


def opaque_cols(im: Image.Image, thr: int = 20) -> list[bool]:
    px = im.load()
    w, h = im.size
    return [any(px[x, y][3] > thr for y in range(h)) for x in range(w)]


def opaque_rows(im: Image.Image, thr: int = 20) -> list[bool]:
    px = im.load()
    w, h = im.size
    return [any(px[x, y][3] > thr for x in range(w)) for y in range(h)]


def runs(mask: list[bool], min_len: int = 2) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start = None
    for i, on in enumerate(mask):
        if on and start is None:
            start = i
        if (not on or i == len(mask) - 1) and start is not None:
            end = i if not on else i + 1
            if end - start >= min_len:
                out.append((start, end))
            start = None
    return out


def grid_cells(im: Image.Image, min_w: int = 8, min_h: int = 8) -> list[tuple[int, int, int, int]]:
    """Split atlas into cells by transparent gutters."""
    xs = runs(opaque_cols(im), 2)
    ys = runs(opaque_rows(im), 2)
    cells = []
    for y0, y1 in ys:
        for x0, x1 in xs:
            if x1 - x0 < min_w or y1 - y0 < min_h:
                continue
            # tighten to actual content in this cell
            cell = im.crop((x0, y0, x1, y1))
            bb = cell.split()[-1].getbbox()
            if not bb:
                continue
            cells.append((x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]))
    return cells


def main() -> None:
    for fname in [
        "s002_412x383.png",
        "s015_421x265.png",
        "s010_76x54.png",
        "s011_124x32.png",
        "s003_56x33.png",
    ]:
        im = Image.open(OP / fname).convert("RGBA")
        cells = grid_cells(im)
        print(f"=== {fname} cells={len(cells)}")
        preview = im.copy()
        dr = ImageDraw.Draw(preview)
        for i, (x0, y0, x1, y1) in enumerate(cells):
            w, h = x1 - x0, y1 - y0
            print(f"  #{i} {w}x{h} @({x0},{y0})")
            dr.rectangle((x0, y0, x1 - 1, y1 - 1), outline=(255, 80, 80, 255))
            im.crop((x0, y0, x1, y1)).save(OUT / f"{fname[:-4]}_c{i}_{w}x{h}.png")
        preview.save(OUT / f"{fname[:-4]}_grid.png")

    # fixed half-splits for known strips
    s11 = Image.open(OP / "s011_124x32.png").convert("RGBA")
    s11.crop((0, 0, 62, 32)).save(OUT / "detail_off_from_s011.png")
    s11.crop((62, 0, 124, 32)).save(OUT / "detail_over_from_s011.png")
    s10 = Image.open(OP / "s010_76x54.png").convert("RGBA")
    # 2x2 assumed
    cw, ch = 38, 27
    for i, (x, y, name) in enumerate(
        [
            (0, 0, "mute_off_y"),
            (38, 0, "mute_off_c"),
            (0, 27, "mute_on_y"),
            (38, 27, "mute_on_c"),
        ]
    ):
        s10.crop((x, y, x + cw, y + ch)).save(OUT / f"{name}.png")
        print("mute crop", name)
    print("done", OUT)


if __name__ == "__main__":
    main()
