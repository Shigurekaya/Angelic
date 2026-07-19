# -*- coding: utf-8 -*-
"""Optimize 4 title char positions by MSE vs charall (fast numpy)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

LAYERS = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\layers")
OUT = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\title_chars.json")

FM_T1 = {
    "ama": (-85, -31),
    "noa": (-358, 0),
    "kag": (347, -44),
    "kur": (164, 241),
}
FM_T0 = {
    "ama": (-69.0, -79.0),
    "noa": (-422.0, -24.0),
    "kag": (387.0, -108.0),
    "kur": (236.0, 281.0),
}
ORDER = ("ama", "noa", "kag", "kur")


def load_rgba(name: str) -> np.ndarray:
    return np.asarray(Image.open(LAYERS / name).convert("RGBA"))


def alpha_blit(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    """In-place alpha over onto dst (H,W,4) uint8."""
    H, W = dst.shape[:2]
    sh, sw = src.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + sw), min(H, y + sh)
    if x0 >= x1 or y0 >= y1:
        return
    sx0, sy0 = x0 - x, y0 - y
    tile = src[sy0 : sy0 + (y1 - y0), sx0 : sx0 + (x1 - x0)].astype(np.float32)
    a = tile[:, :, 3:4] / 255.0
    base = dst[y0:y1, x0:x1].astype(np.float32)
    out = base * (1.0 - a) + tile * a
    dst[y0:y1, x0:x1] = np.clip(out, 0, 255).astype(np.uint8)


def compose(layers: dict[str, np.ndarray], pos: dict[str, tuple[int, int]], H: int, W: int) -> np.ndarray:
    canvas = np.zeros((H, W, 4), dtype=np.uint8)
    for cid in ORDER:
        alpha_blit(canvas, layers[cid], int(pos[cid][0]), int(pos[cid][1]))
    return canvas


def mse(canvas: np.ndarray, target: np.ndarray, mask: np.ndarray) -> float:
    d = canvas[:, :, :3].astype(np.float32) - target[:, :, :3].astype(np.float32)
    return float(np.mean(np.abs(d[mask])))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    layers = {cid: load_rgba(f"ch_{cid}_view.png") for cid in ORDER}
    for cid, arr in layers.items():
        print(cid, arr.shape, flush=True)

    charall = load_rgba("charall.png")
    H, W = charall.shape[:2]
    mask = charall[:, :, 3] > 40

    def score(pos):
        return mse(compose(layers, pos, H, W), charall, mask)

    def f_center1208(cid, coord):
        h, w = layers[cid].shape[:2]
        cx, cy = 960 + coord[0], 604 + coord[1] - 128
        return (int(cx - w / 2), int(cy - h / 2))

    def f_center1080(cid, coord):
        h, w = layers[cid].shape[:2]
        cx, cy = 960 + coord[0], 540 + coord[1]
        return (int(cx - w / 2), int(cy - h / 2))

    prev = {"ama": (276, 355), "noa": (0, 0), "kag": (630, 0), "kur": (675, 261)}
    cands = {
        "center1208": {cid: f_center1208(cid, FM_T1[cid]) for cid in ORDER},
        "center1080": {cid: f_center1080(cid, FM_T1[cid]) for cid in ORDER},
        "prev_match": prev,
    }
    best_name, best_pos, best_err = None, None, 1e18
    for name, pos in cands.items():
        e = score(pos)
        print(f"{name:12s} mse={e:.2f} {pos}", flush=True)
        if e < best_err:
            best_name, best_pos, best_err = name, pos, e
    print("seed", best_name, best_err, flush=True)

    pos = dict(best_pos)
    err = best_err
    # coarse descent
    for pass_i in range(2):
        for cid in ORDER:
            x0, y0 = pos[cid]
            local_best = (err, (x0, y0))
            for dy in range(-32, 33, 4):
                for dx in range(-32, 33, 4):
                    trial = dict(pos)
                    trial[cid] = (x0 + dx, y0 + dy)
                    e = score(trial)
                    if e < local_best[0]:
                        local_best = (e, trial[cid])
            pos[cid] = local_best[1]
            err = local_best[0]
            print(f"pass{pass_i} {cid} {pos[cid]} mse={err:.2f}", flush=True)

    # fine
    for cid in ORDER:
        x0, y0 = pos[cid]
        local_best = (err, (x0, y0))
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                trial = dict(pos)
                trial[cid] = (x0 + dx, y0 + dy)
                e = score(trial)
                if e < local_best[0]:
                    local_best = (e, trial[cid])
        pos[cid] = local_best[1]
        err = local_best[0]
        print(f"fine {cid} {pos[cid]} mse={err:.2f}", flush=True)

    # previews
    preview = compose(layers, pos, H, W)
    Image.fromarray(preview).save(LAYERS / "preview_chars_end.png")
    diff = np.abs(preview[:, :, :3].astype(np.int16) - charall[:, :, :3].astype(np.int16))
    Image.fromarray(np.clip(diff, 0, 255).astype(np.uint8)).save(LAYERS / "preview_chars_diff.png")

    chars = []
    for cid in ORDER:
        x, y = pos[cid]
        t0, t1 = FM_T0[cid], FM_T1[cid]
        dx, dy = t1[0] - t0[0], t1[1] - t0[1]
        h, w = layers[cid].shape[:2]
        chars.append(
            {
                "id": cid,
                "image": f"angelic/title/layers/ch_{cid}_view.png",
                "ex": int(x),
                "ey": int(y),
                "sx": int(x - dx),
                "sy": int(y - dy),
                "fade0": 0.5,
                "fade1": 1.5,
                "move_end": 1.5,
                "fm_t0": list(t0),
                "fm_t1": list(t1),
                "size": [w, h],
            }
        )

    data = {
        "chars": chars,
        "order": list(ORDER),
        "draw_order_back_to_front": list(ORDER),
        "fps": 60,
        "char_move_last": 121,
        "logo_last": 41,
        "positioning": f"MSE vs charall from {best_name}",
        "final_mse": round(err, 3),
        "extras": {
            "bg_plain": {"image": "angelic/title/layers/bg_plain_view.png", "zx0": 1.1},
            "deco_set": {
                "image": "angelic/title/layers/deco_set_view.png",
                "fade0": 0.5,
                "fade1": 1.5,
                "zx0": 1.5,
                "xy": [16, 0],
            },
            "lower_gradient": {
                "image": "angelic/title/layers/lower_gradient.png",
                "fade0": 1.5,
                "fade1": 2.0,
                "y0": 402,
                "y1": 338,
                "opa1": 0.8,
            },
            "frame": {
                "image": "angelic/title/layers/frame.png",
                "fade0": 1.5,
                "fade1": 2.0,
                "xy": [1, -15],
            },
            "charall": {"image": "angelic/title/layers/charall.png", "crossfade_at": 1.5},
        },
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT, "mse", err, flush=True)
    print(json.dumps(chars, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
