# -*- coding: utf-8 -*-
"""Fast match of 4 title char layers onto charall.png (same composite source)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

LAYERS = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\layers")
OUT = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\title_chars.json")
CHARALL = LAYERS / "charall.png"

# mtn char_move keyframes (60fps)
FM = {
    "ama": {"src": "ch_ama.png", "t0": (-69.0, -79.0), "t1": (-85, -31), "f0": 30, "f1": 90},
    "noa": {"src": "ch_noa.png", "t0": (-422.0, -24.0), "t1": (-358, 0), "f0": 30, "f1": 90},
    "kag": {"src": "ch_kag.png", "t0": (387.0, -108.0), "t1": (347, -44), "f0": 30, "f1": 90},
    "kur": {"src": "ch_kur.png", "t0": (236.0, 281.0), "t1": (164, 241), "f0": 30, "f1": 90},
}


def to_view(src: Path) -> Path:
    """Crop to 1080h bottom-aligned; save *_view.png."""
    im = Image.open(src).convert("RGBA")
    if im.height > 1080:
        top = im.height - 1080
        im = im.crop((0, top, im.width, im.height))
    if im.width > 1920:
        im = im.crop((0, 0, 1920, im.height))
    out = src.with_name(src.stem.replace("_view", "") + "_view.png")
    im.save(out)
    return out


def match_downscale(hay_rgba: Image.Image, needle_rgba: Image.Image, scale: float = 0.25):
    """Coarse match at low res, then refine at full res in a window."""
    hw, hh = hay_rgba.size
    nw, nh = needle_rgba.size
    if nh > hh or nw > hw:
        s = min(hh / nh, hw / nw)
        needle_rgba = needle_rgba.resize((max(1, int(nw * s)), max(1, int(nh * s))), Image.Resampling.BILINEAR)
        nw, nh = needle_rgba.size

    # coarse
    sw, sh = max(1, int(hw * scale)), max(1, int(hh * scale))
    snw, snh = max(1, int(nw * scale)), max(1, int(nh * scale))
    hay_s = np.asarray(hay_rgba.resize((sw, sh), Image.Resampling.BILINEAR))
    nd_s = np.asarray(needle_rgba.resize((snw, snh), Image.Resampling.BILINEAR))
    mask = nd_s[:, :, 3] > 40
    if mask.sum() < 20:
        return 1e9, 0, 0, nw, nh
    ys, xs = np.where(mask)
    if len(xs) > 2000:
        idx = np.linspace(0, len(xs) - 1, 2000).astype(int)
        ys, xs = ys[idx], xs[idx]
    rgb = nd_s[:, :, :3].astype(np.float32)
    best = (1e18, 0, 0)
    step = 1
    for y in range(0, sh - snh + 1, step):
        for x in range(0, sw - snw + 1, step):
            patch = hay_s[y : y + snh, x : x + snw, :3].astype(np.float32)
            sc = float(np.mean(np.abs(patch[ys, xs] - rgb[ys, xs])))
            if sc < best[0]:
                best = (sc, x, y)
    # map to full
    fx = int(best[1] / scale)
    fy = int(best[2] / scale)

    # refine full-res in ±16px
    hay = np.asarray(hay_rgba)
    nd = np.asarray(needle_rgba)
    mask = nd[:, :, 3] > 40
    ys, xs = np.where(mask)
    if len(xs) > 5000:
        idx = np.linspace(0, len(xs) - 1, 5000).astype(int)
        ys, xs = ys[idx], xs[idx]
    rgb = nd[:, :, :3].astype(np.float32)
    rad = 16
    x0, y0 = max(0, fx - rad), max(0, fy - rad)
    x1, y1 = min(hw - nw, fx + rad), min(hh - nh, fy + rad)
    best2 = (1e18, fx, fy)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            patch = hay[y : y + nh, x : x + nw, :3].astype(np.float32)
            sc = float(np.mean(np.abs(patch[ys, xs] - rgb[ys, xs])))
            if sc < best2[0]:
                best2 = (sc, x, y)
    return best2[0], best2[1], best2[2], nw, nh


def main() -> int:
    hay = Image.open(CHARALL).convert("RGBA")
    print("charall", hay.size)
    chars = []
    for cid in ("ama", "noa", "kag", "kur"):
        meta = FM[cid]
        view = to_view(LAYERS / meta["src"])
        needle = Image.open(view).convert("RGBA")
        print("match", cid, view.name, needle.size)
        score, x, y, nw, nh = match_downscale(hay, needle, scale=0.2)
        print(f"  -> score={score:.2f} pos=({x},{y}) size={nw}x{nh}")
        dx = meta["t1"][0] - meta["t0"][0]
        dy = meta["t1"][1] - meta["t0"][1]
        chars.append(
            {
                "id": cid,
                "image": "angelic/title/layers/" + view.name,
                "ex": int(x),
                "ey": int(y),
                "sx": int(x - dx),
                "sy": int(y - dy),
                "fade0": meta["f0"] / 60.0,
                "fade1": meta["f1"] / 60.0,
                "move_end": meta["f1"] / 60.0,
                "fm_t0": list(meta["t0"]),
                "fm_t1": list(meta["t1"]),
                "match_score": round(float(score), 3),
                "size": [nw, nh],
            }
        )

    extras = {
        "bg_plain": {"image": "angelic/title/layers/bg_plain.png", "zx0": 1.1, "zoom_end_frame": 90},
        "deco_set": {
            "image": "angelic/title/layers/deco_set.png",
            "fade0": 0.5,
            "fade1": 1.5,
            "zx0": 1.5,
            "xy": [16, 0],
        },
        "lower_gradient": {
            "image": "angelic/title/layers/lower_gradient.png",
            "fade0": 1.5,
            "fade1": 2.0,
            "y0": 530,
            "y1": 466,
            "opa1": 204 / 255.0,
        },
        "frame": {
            "image": "angelic/title/layers/frame.png",
            "fade0": 1.5,
            "fade1": 2.0,
            "xy": [1, -15],
        },
        "charall": {"image": "angelic/title/layers/charall.png", "crossfade_at": 1.5},
    }
    data = {
        "chars": chars,
        "extras": extras,
        "order": ["ama", "noa", "kag", "kur"],
        "draw_order_back_to_front": ["ama", "noa", "kag", "kur"],
        "fps": 60,
        "char_move_last": 121,
        "logo_last": 41,
        "matched_against": "charall.png",
        "note": "Individual layers + mtn deltas; intro crossfades to bgN at ~t120",
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)
    for c in chars:
        print(c["id"], "end", c["ex"], c["ey"], "start", c["sx"], c["sy"], "score", c["match_score"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
