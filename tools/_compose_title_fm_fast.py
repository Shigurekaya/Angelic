# -*- coding: utf-8 -*-
"""Fast FreeMote coord formula test vs 通常セット."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
OUT = Path(r"D:\gamedev\Angelic\tools\_title_fm_compose")
OUT.mkdir(parents=True, exist_ok=True)

CHARS = [
    ("ama", 400, 497, (-85, -31)),
    ("noa", 1332, 1208, (-358, 0)),
    ("kag", 1290, 1120, (347, -44)),
    ("kur", 1642, 725, (164, 241)),
]


def log(msg: str) -> None:
    print(msg, flush=True)


def find_by_size(w: int, h: int) -> Path:
    cands = [p for p in SRC.glob("*.png") if Image.open(p).size == (w, h)]
    if not cands:
        raise FileNotFoundError((w, h))
    return max(cands, key=lambda p: p.stat().st_size)


def crop_view(im: Image.Image) -> Image.Image:
    if im.height == 1080:
        return im
    top = (im.height - 1080) // 2
    return im.crop((0, top, im.width, top + 1080))


def place(canvas: Image.Image, layer: Image.Image, tlx: float, tly: float) -> None:
    x, y = int(round(tlx)), int(round(tly))
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.alpha_composite(layer, (x, y))
    canvas.alpha_composite(tmp)


def mse(a: Image.Image, b: Image.Image) -> float:
    aa = np.asarray(a.convert("RGBA"), dtype=np.float32)
    bb = np.asarray(b.convert("RGBA"), dtype=np.float32)
    m = (aa[..., 3] > 8) | (bb[..., 3] > 8)
    d = (aa[..., :3] - bb[..., :3])[m]
    return float(np.mean(d * d))


def main() -> None:
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    icon_by_wh = {
        (ic["width"], ic["height"]): ic for ic in mtn["source"]["normal"]["icon"].values()
    }

    charall = find_by_size(1920, 1080)
    bg = max(
        (p for p in SRC.glob("*.png") if Image.open(p).size == (1920, 1208)),
        key=lambda p: p.stat().st_size,
    )
    log(f"charall={charall.name} bg={bg.name}")
    ref = Image.open(charall).convert("RGBA")
    bg_im = Image.open(bg).convert("RGBA")
    bg_v = crop_view(bg_im)

    layers = []
    for cid, w, h, t1 in CHARS:
        p = find_by_size(w, h)
        ic = icon_by_wh[(w, h)]
        im = Image.open(p).convert("RGBA")
        layers.append((cid, im, ic, t1))
        log(f"{cid}: {p.name} origin=({ic['originX']},{ic['originY']})")

    def sc_icon(cx, cy, ic, pox, poy):
        return 960 + cx + pox - ic["originX"], 540 + cy + poy - ic["originY"]

    def cv_icon(cx, cy, ic, pox, poy):
        return 960 + cx + pox - ic["originX"], 604 + cy + poy - ic["originY"]

    def sc_tl(cx, cy, ic, pox, poy):
        return 960 + cx + pox, 540 + cy + poy

    formulas = [
        ("A_sc+icon+p16", lambda c, y, ic: sc_icon(c, y, ic, -16, -16), False),
        ("B_sc+icon", lambda c, y, ic: sc_icon(c, y, ic, 0, 0), False),
        ("C_cv+icon+p16", lambda c, y, ic: cv_icon(c, y, ic, -16, -16), True),
        ("D_sc+tl+p16", lambda c, y, ic: sc_tl(c, y, ic, -16, -16), False),
        ("E_sc+tl", lambda c, y, ic: sc_tl(c, y, ic, 0, 0), False),
        ("H_sc+icon+p32", lambda c, y, ic: sc_icon(c, y, ic, -32, -32), False),
        # view-crop of full layer first, then place as if canvas TL shifted by -64
        ("I_sc+icon_view", None, False),
    ]

    best = None
    for name, fn, use_cv in formulas:
        if name == "I_sc+icon_view":
            canvas = bg_v.copy()
            positions = {}
            for cid, im, ic, t1 in layers:
                cx, cy = t1
                # place full layer on 1208 canvas then crop — equivalent to adjusting y
                tlx = 960 + cx - ic["originX"]
                tly = 604 + cy - ic["originY"]
                # after center-crop, view TL y = canvas_tl_y - 64
                place(canvas, im, tlx, tly - 64)
                positions[cid] = (round(tlx), round(tly - 64))
        else:
            if use_cv:
                canvas = Image.new("RGBA", (1920, 1208), (0, 0, 0, 0))
                canvas.alpha_composite(bg_im, (0, 0))
            else:
                canvas = bg_v.copy()
            positions = {}
            for cid, im, ic, t1 in layers:
                cx, cy = t1
                tlx, tly = fn(cx, cy, ic)
                place(canvas, im, tlx, tly)
                positions[cid] = (round(tlx), round(tly))
            if use_cv:
                canvas = crop_view(canvas)

        err = mse(canvas, ref)
        canvas.save(OUT / f"compose_{name}.png")
        log(f"{name}: MSE={err:.1f} pos={positions}")
        if best is None or err < best[0]:
            best = (err, name, positions)

    log(f"\nBEST {best[1]} MSE={best[0]:.1f}")
    log(f"positions {best[2]}")

    # also test logo
    logo = max(
        (p for p in SRC.glob("logo_cn*.png")),
        key=lambda p: p.stat().st_size,
    )
    lic = mtn["source"]["logo_cn"]["icon"]["logo_cn"]
    lim = Image.open(logo).convert("RGBA")
    cx, cy = -566, 300
    for tag, pox, poy in [("sc", 0, 0)]:
        tlx = 960 + cx + pox - lic["originX"]
        tly = 540 + cy + poy - lic["originY"]
        log(f"logo_cn TL ({tlx:.1f},{tly:.1f}) size={lim.size} origin=({lic['originX']},{lic['originY']})")

    # Write derived title_chars positions for best formula
    meta_path = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\title_chars.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    # compute start+end with best formula B or winner
    win_name = best[1]
    log(f"deriving coords with {win_name}")

    def pos_for(cx, cy, ic, formula_name):
        if formula_name.startswith("A_"):
            return sc_icon(cx, cy, ic, -16, -16)
        if formula_name.startswith("B_") or formula_name.startswith("I_"):
            if formula_name.startswith("I_"):
                return 960 + cx - ic["originX"], 604 + cy - ic["originY"] - 64
            return sc_icon(cx, cy, ic, 0, 0)
        if formula_name.startswith("C_"):
            x, y = cv_icon(cx, cy, ic, -16, -16)
            return x, y - 64
        if formula_name.startswith("D_"):
            return sc_tl(cx, cy, ic, -16, -16)
        if formula_name.startswith("E_"):
            return sc_tl(cx, cy, ic, 0, 0)
        if formula_name.startswith("H_"):
            return sc_icon(cx, cy, ic, -32, -32)
        return sc_icon(cx, cy, ic, 0, 0)

    starts = {
        "ama": (-69.0, -79.0),
        "noa": (-422.0, -24.0),
        "kag": (387.0, -108.0),
        "kur": (236.0, 281.0),
    }
    ends = {c[0]: c[3] for c in CHARS}
    for ch in meta["chars"]:
        cid = ch["id"]
        ic = icon_by_wh[next(x[1:3] for x in CHARS if x[0] == cid)]
        sx, sy = pos_for(*starts[cid], ic, win_name)
        ex, ey = pos_for(*ends[cid], ic, win_name)
        ch["sx"], ch["sy"] = int(round(sx)), int(round(sy))
        ch["ex"], ch["ey"] = int(round(ex)), int(round(ey))
        ch["fm_t0"] = list(starts[cid])
        ch["fm_t1"] = list(ends[cid])
        log(f"  {cid}: start=({ch['sx']},{ch['sy']}) end=({ch['ex']},{ch['ey']})")

    # extras from FM
    # lower_gradient: coord y 530→466, origin 960,74 → TL y = 540+y-74
    meta["extras"]["lower_gradient"]["y0"] = int(round(540 + 530 - 74))
    meta["extras"]["lower_gradient"]["y1"] = int(round(540 + 466 - 74))
    # frame: (1,-15) origin 953,518
    fx = int(round(960 + 1 - 953))
    fy = int(round(540 - 15 - 518))
    meta["extras"]["frame"]["xy"] = [fx, fy]
    # deco: coord (16,0) size 1885x1208 origin 942,604 — view
    dx = int(round(960 + 16 - 942))
    dy = int(round(604 + 0 - 604 - 64))  # canvas then crop
    meta["extras"]["deco_set"]["xy"] = [dx, dy]
    meta["note"] = f"positions from FreeMote unpack formula {win_name}; icon origin + screen center"
    meta["fm_formula"] = win_name
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"wrote {meta_path}")
    log(f"grad y {meta['extras']['lower_gradient']['y0']}->{meta['extras']['lower_gradient']['y1']}")
    log(f"frame xy {meta['extras']['frame']['xy']} deco xy {meta['extras']['deco_set']['xy']}")


if __name__ == "__main__":
    main()
