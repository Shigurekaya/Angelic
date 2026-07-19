# -*- coding: utf-8 -*-
"""Composite FreeMote title layers using unpack origins; MSE vs charall/bg0."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
OUT = Path(r"D:\gamedev\Angelic\tools\_title_fm_compose")
OUT.mkdir(parents=True, exist_ok=True)

# filesize-stable ASCII names (from earlier bake)
# Map by exact pixel size
CHARS = [
    # id, w, h, coord_t30, coord_t90
    ("ama", 400, 497, (-69.0, -79.0), (-85, -31)),
    ("noa", 1332, 1208, (-422.0, -24.0), (-358, 0)),
    ("kag", 1290, 1120, (387.0, -108.0), (347, -44)),
    ("kur", 1642, 725, (236.0, 281.0), (164, 241)),
]


def find_png(w: int, h: int) -> Path:
    for p in SRC.glob("*.png"):
        im = Image.open(p)
        if im.size == (w, h) and "logo" not in p.name.lower() and "frame" not in p.name and "gradient" not in p.name and "白" not in p.name:
            # prefer 通常 char layers
            if "通常" in p.name or "normal" in p.name.lower():
                if w == 1920 and h == 1208 and "bg" in p.name.lower():
                    continue
                if w == 1920 and h == 1080:
                    continue
                if w == 1885:
                    continue
                return p
    raise FileNotFoundError((w, h))


def find_by_size(w: int, h: int) -> Path:
    cands = []
    for p in SRC.glob("*.png"):
        im = Image.open(p)
        if im.size == (w, h):
            cands.append(p)
    if not cands:
        raise FileNotFoundError((w, h))
    # prefer largest file among same size (actual art)
    return max(cands, key=lambda p: p.stat().st_size)


def mse_rgb(a: Image.Image, b: Image.Image, mask: np.ndarray | None = None) -> float:
    aa = np.asarray(a.convert("RGBA"), dtype=np.float32)
    bb = np.asarray(b.convert("RGBA"), dtype=np.float32)
    if mask is None:
        # where either has alpha
        m = (aa[..., 3] > 8) | (bb[..., 3] > 8)
    else:
        m = mask
    if not m.any():
        return 0.0
    d = (aa[..., :3] - bb[..., :3])[m]
    return float(np.mean(d * d))


def place(canvas: Image.Image, layer: Image.Image, tlx: float, tly: float):
    x, y = int(round(tlx)), int(round(tly))
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.alpha_composite(layer, (x, y))
    canvas.alpha_composite(tmp)


def tl_screen_center_icon(cx, cy, ox, oy, parent_ox=0, parent_oy=0, sw=1920, sh=1080):
    return sw / 2 + cx + parent_ox - ox, sh / 2 + cy + parent_oy - oy


def tl_canvas_center_icon(cx, cy, ox, oy, parent_ox=0, parent_oy=0, cw=1920, ch=1208):
    return cw / 2 + cx + parent_ox - ox, ch / 2 + cy + parent_oy - oy


def tl_topleft_pivot(cx, cy, parent_ox=0, parent_oy=0, sw=1920, sh=1080):
    # frame ox=0,oy=0 override → pivot at image TL; coord relative to screen center
    return sw / 2 + cx + parent_ox, sh / 2 + cy + parent_oy


def crop_view(im: Image.Image, canvas_h=1208, view_h=1080) -> Image.Image:
    if im.height == view_h:
        return im
    top = (canvas_h - view_h) // 2
    return im.crop((0, top, im.width, top + view_h))


def main():
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    icons = mtn["source"]["normal"]["icon"]
    icon_by_wh = {(ic["width"], ic["height"]): ic for ic in icons.values()}

    charall = find_by_size(1920, 1080)  # 通常セット
    bg_plain = find_by_size(1920, 1208)  # could be bg or 白 — pick 通常bg by size+name
    # disambiguate bg
    for p in SRC.glob("*.png"):
        im = Image.open(p)
        if im.size == (1920, 1208) and p.stat().st_size > 2_000_000:
            bg_plain = p
            break

    print("charall", charall.name, charall.stat().st_size)
    print("bg", bg_plain.name, bg_plain.stat().st_size)
    ref = Image.open(charall).convert("RGBA")

    # load layers
    layers = []
    for cid, w, h, t0, t1 in CHARS:
        p = find_by_size(w, h)
        ic = icon_by_wh[(w, h)]
        im = Image.open(p).convert("RGBA")
        layers.append((cid, im, ic, t0, t1, p.name))
        print(cid, p.name, "origin", ic["originX"], ic["originY"])

    formulas = []

    # A: screen-center + icon origin, parent -16
    formulas.append(("A_sc+icon+p16", lambda cx, cy, ic: tl_screen_center_icon(
        cx, cy, ic["originX"], ic["originY"], -16, -16)))
    # B: screen-center + icon origin, no parent
    formulas.append(("B_sc+icon", lambda cx, cy, ic: tl_screen_center_icon(
        cx, cy, ic["originX"], ic["originY"], 0, 0)))
    # C: canvas-center + icon, crop to view, parent -16
    formulas.append(("C_cv+icon+p16", lambda cx, cy, ic: tl_canvas_center_icon(
        cx, cy, ic["originX"], ic["originY"], -16, -16)))
    # D: screen-center + TL pivot (ox=0 override), parent -16
    formulas.append(("D_sc+tl+p16", lambda cx, cy, ic: tl_topleft_pivot(cx, cy, -16, -16)))
    # E: screen-center + TL pivot, no parent
    formulas.append(("E_sc+tl", lambda cx, cy, ic: tl_topleft_pivot(cx, cy, 0, 0)))
    # F: screen top-left origin (screenSize.origin=0,0) + icon
    formulas.append(("F_abs+icon", lambda cx, cy, ic: (cx - ic["originX"], cy - ic["originY"])))
    # G: abs + icon + 960/540 offset explicit
    formulas.append(("G_abs960+icon", lambda cx, cy, ic: (
        960 + cx - ic["originX"], 540 + cy - ic["originY"])))
    # H: double parent -16 (通常 + キャラ)
    formulas.append(("H_sc+icon+p32", lambda cx, cy, ic: tl_screen_center_icon(
        cx, cy, ic["originX"], ic["originY"], -32, -32)))

    results = []
    for name, fn in formulas:
        # compose on 1920x1208 then crop, OR direct 1080
        use_canvas = name.startswith("C_")
        if use_canvas:
            canvas = Image.new("RGBA", (1920, 1208), (0, 0, 0, 0))
        else:
            canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))

        # bg under
        bg = Image.open(bg_plain).convert("RGBA")
        if use_canvas:
            canvas.alpha_composite(bg, (0, 0))
        else:
            canvas.alpha_composite(crop_view(bg), (0, 0))

        positions = {}
        for cid, im, ic, t0, t1, _ in layers:
            cx, cy = t1
            tlx, tly = fn(cx, cy, ic)
            place(canvas, im, tlx, tly)
            positions[cid] = (round(tlx, 1), round(tly, 1))

        view = crop_view(canvas) if use_canvas else canvas
        # compare opaque region of charall vs our compose
        ref_a = np.asarray(ref)[..., 3] > 8
        err = mse_rgb(view, ref)
        # also pixel diff count
        va = np.asarray(view.convert("RGBA"), dtype=np.int16)
        ra = np.asarray(ref, dtype=np.int16)
        diff = np.abs(va[..., :3] - ra[..., :3]).sum(axis=-1)
        bad = ((diff > 40) & ref_a).mean()
        results.append((err, bad, name, positions))
        view.save(OUT / f"compose_{name}.png")
        print(f"{name}: MSE={err:.1f} badpx={bad:.3%} pos={positions}")

    results.sort()
    print("\nBEST:", results[0][2], "MSE", results[0][0], "bad", results[0][1])
    print("positions", results[0][3])

    # Also: char-only composite (no bg) vs charall with bg subtracted? 
    # Better: match each char alone by sliding near predicted pos
    print("\n=== per-char local refine around formula B ===")
    fn = formulas[1][1]  # B
    bg_v = crop_view(Image.open(bg_plain).convert("RGBA"))
    # isolate charall characters roughly: charall - bg? charall is full composite
    # Instead template match each layer alpha bbox against charall near predicted TL
    for cid, im, ic, t0, t1, _ in layers:
        cx, cy = t1
        px, py = fn(cx, cy, ic)
        best = None
        # search ±40
        for dy in range(-40, 41, 2):
            for dx in range(-40, 41, 2):
                canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
                place(canvas, im, px + dx, py + dy)
                # compare only where layer alpha > 0
                la = np.asarray(im)[..., 3]
                # extract region
                x0, y0 = int(round(px + dx)), int(round(py + dy))
                # mse of overlay vs ref in opaque layer pixels
                ca = np.asarray(canvas)
                ra = np.asarray(ref)
                m = ca[..., 3] > 32
                if not m.any():
                    continue
                # where we drew, does ref look similar (non-bg)?
                d = (ca[..., :3].astype(np.float32) - ra[..., :3].astype(np.float32))[m]
                e = float(np.mean(d * d))
                if best is None or e < best[0]:
                    best = (e, x0, y0, dx, dy)
        print(cid, "pred", (round(px), round(py)), "best", best)


if __name__ == "__main__":
    main()
