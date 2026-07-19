# -*- coding: utf-8 -*-
"""Dump Angelic title_bg.mtn char_move + rematch 4 chars onto bg0 precisely."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"D:\gamedev\Angelic")
MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
SRC = ROOT / "ui-preview/_mtn/title_bg"
LAYERS = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\layers")
BG0 = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\bg0.png")
OUT = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\title_chars.json")


def dump_mtn() -> None:
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    cm = mtn["object"]["title_bg"]["motion"]["char_move"]
    print("char_move lastTime", cm["lastTime"])

    def walk(L, depth=0):
        lab = L.get("label") or ""
        fl = L.get("frameList") or []
        src = None
        for fr in fl:
            c = fr.get("content") or {}
            if c.get("src"):
                src = c["src"]
                break
        pad = "  " * depth
        print(f"{pad}label={lab!r}")
        if src:
            print(f"{pad}  src={src}")
        for fr in fl:
            c = fr.get("content") or {}
            if not c:
                if fr.get("type") == 0:
                    print(f"{pad}  t={fr.get('time')} (end)")
                continue
            bits = []
            for k in ("coord", "opa", "zx", "zy", "ox", "oy"):
                if k in c:
                    bits.append(f"{k}={c[k]}")
            if bits:
                print(f"{pad}  t={fr.get('time')} " + " ".join(bits))
        for ch in L.get("children") or []:
            walk(ch, depth + 1)

    for L in cm.get("layer") or []:
        walk(L)

    print("\n--- source PNGs ---")
    for p in sorted(SRC.glob("*.png")):
        im = Image.open(p)
        print(f"{p.stat().st_size:8d} {im.size[0]:4d}x{im.size[1]:4d}  {p.name}")


def copy_layers_by_size() -> dict[str, Path]:
    """Map by exact file size to ASCII names (JP filenames mojibake on Windows)."""
    LAYERS.mkdir(parents=True, exist_ok=True)
    by_size = {
        2431752: "bg_plain.png",
        3011613: "charall.png",
        1008433: "ch_noa.png",  # 乃愛
        834473: "ch_kag.png",  # かぐ耶
        725467: "ch_ama.png",  # 天音
        234467: "ch_kur.png",  # 来海
        305381: "deco_set.png",  # 通常セ
        44372: "frame.png",
        1992: "lower_gradient.png",
        12529: "siro.png",
        472949: "logo_cn_layer.png",
        446917: "logo_jp.png",
    }
    mapping = {}
    for p in SRC.glob("*.png"):
        name = by_size.get(p.stat().st_size)
        if not name:
            continue
        dst = LAYERS / name
        Image.open(p).convert("RGBA").save(dst)
        mapping[name] = dst
        print("copy", p.stat().st_size, "->", name, Image.open(dst).size)
    return mapping


def prep_display(path: Path, canvas_h: int = 1208, view_h: int = 1080) -> Path:
    """Crop FreeMote 1208 canvas to 1080 view (drop top)."""
    im = Image.open(path).convert("RGBA")
    if im.height >= canvas_h:
        top = canvas_h - view_h  # 128
        # if image is canvas-sized height
        if im.height == canvas_h:
            im = im.crop((0, top, im.width, im.height))
        elif im.height > view_h:
            # bottom-align crop
            top = im.height - view_h
            im = im.crop((0, top, im.width, im.height))
    out = path.with_name(path.stem + "_view.png")
    im.save(out)
    return out


def ncc_match(hay: np.ndarray, needle: np.ndarray, step: int = 4) -> tuple[float, int, int]:
    """Alpha-masked MAE match; returns (score, x, y). Lower score better."""
    H, W = hay.shape[:2]
    nh, nw = needle.shape[:2]
    if nh > H or nw > W:
        scale = min(H / nh, W / nw)
        nim = Image.fromarray(needle).resize(
            (max(1, int(nw * scale)), max(1, int(nh * scale))), Image.Resampling.BILINEAR
        )
        needle = np.asarray(nim)
        nh, nw = needle.shape[:2]
    mask = needle[:, :, 3] > 40
    if int(mask.sum()) < 80:
        return 1e18, 0, 0
    ys, xs = np.where(mask)
    if len(xs) > 8000:
        idx = np.linspace(0, len(xs) - 1, 8000).astype(int)
        ys, xs = ys[idx], xs[idx]
    rgb = needle[:, :, :3].astype(np.float32)
    best = (1e18, 0, 0)
    for y in range(0, H - nh + 1, step):
        for x in range(0, W - nw + 1, step):
            patch = hay[y : y + nh, x : x + nw, :3].astype(np.float32)
            score = float(np.mean(np.abs(patch[ys, xs] - rgb[ys, xs])))
            if score < best[0]:
                best = (score, x, y)
    return best


def refine(hay: np.ndarray, needle: np.ndarray, x: int, y: int, rad: int = 24) -> tuple[float, int, int]:
    H, W = hay.shape[:2]
    nh, nw = needle.shape[:2]
    x0, y0 = max(0, x - rad), max(0, y - rad)
    x1, y1 = min(W, x + nw + rad), min(H, y + nh + rad)
    sub = hay[y0:y1, x0:x1]
    score, lx, ly = ncc_match(sub, needle, step=1)
    return score, x0 + lx, y0 + ly


def main() -> int:
    dump_mtn()
    print("\n=== copy layers ===")
    copy_layers_by_size()

    # FreeMote char_move keyframes (from dump; labels mojibake but order fixed)
    # children under キャラ: 天音, 乃愛, かぐ耶, 来海
    FM = {
        "ama": {"file": "ch_ama.png", "t0": (-69.0, -79.0), "t1": (-85, -31), "f0": 30, "f1": 90},
        "noa": {"file": "ch_noa.png", "t0": (-422.0, -24.0), "t1": (-358, 0), "f0": 30, "f1": 90},
        "kag": {"file": "ch_kag.png", "t0": (387.0, -108.0), "t1": (347, -44), "f0": 30, "f1": 90},
        "kur": {"file": "ch_kur.png", "t0": (236.0, 281.0), "t1": (164, 241), "f0": 30, "f1": 90},
    }

    bg = Image.open(BG0).convert("RGBA")
    hay = np.asarray(bg)
    print("\n=== match onto bg0", bg.size, "===")

    chars = []
    # draw order back→front = mtn children order
    for cid in ("ama", "noa", "kag", "kur"):
        meta = FM[cid]
        src = LAYERS / meta["file"]
        view = prep_display(src)
        im = Image.open(view).convert("RGBA")
        # clip width to screen if needed
        if im.width > 1920:
            im = im.crop((0, 0, 1920, im.height))
            im.save(view)
        needle = np.asarray(im)
        print(f"match {cid} {view.name} {im.size}")
        score, x, y = ncc_match(hay, needle, step=8)
        print(f"  coarse {score:.3f} @ ({x},{y})")
        score, x, y = refine(hay, needle, x, y, rad=20)
        print(f"  fine   {score:.3f} @ ({x},{y})")

        dx = meta["t1"][0] - meta["t0"][0]
        dy = meta["t1"][1] - meta["t0"][1]
        # Cafe: start = end + dxy_start where dxy = FM start - FM end (motion from start toward end)
        # FM moves from t0→t1, so screen start = end - (t1-t0) = end - delta
        # Wait cafe: dxy_start = FM displacement at start relative to end = t0-t1
        # sx = ex + dxy_start = ex + (t0x-t1x) = ex - dx
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
                "match_score": round(score, 3),
                "size": [im.width, im.height],
            }
        )

    # Also record deco / bg / gradient / frame timings for full intro
    extras = {
        "bg_plain": {
            "image": "angelic/title/layers/bg_plain.png",
            "zx0": 1.1,
            "note": "通常bg t0 zx1.1",
        },
        "deco_set": {
            "image": "angelic/title/layers/deco_set.png",
            "fade0": 30 / 60.0,
            "fade1": 90 / 60.0,
            "zx0": 1.5,
            "coord": [16, 0],
            "note": "通常セ t30 opa0 zx1.5 → t90",
        },
        "charall_crossfade": {
            "image": "angelic/title/layers/charall.png",
            "fade0": 90 / 60.0,
            "opa0": 0,
            "note": "通常セット appears at t90 opa0 (crossfade marker in mtn)",
        },
        "lower_gradient": {
            "image": "angelic/title/layers/lower_gradient.png",
            "fade0": 90 / 60.0,
            "fade1": 120 / 60.0,
            "y0": 530,
            "y1": 466,
            "opa1": 204 / 255.0,
        },
        "frame": {
            "image": "angelic/title/layers/frame.png",
            "fade0": 90 / 60.0,
            "fade1": 120 / 60.0,
            "xy": [1, -15],
        },
    }

    data = {
        "chars": chars,
        "extras": extras,
        "order": ["ama", "noa", "kag", "kur"],
        "fps": 60,
        "char_move_last": 121,
        "logo_last": 41,
        "note": "Positions matched to bg0; motion deltas from title_bg.mtn char_move",
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nWrote", OUT)
    print(json.dumps(chars, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
