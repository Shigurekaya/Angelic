# -*- coding: utf-8 -*-
"""Template-match official pack slices onto ig_option_*_1080 captures.

Skips mouse(7) / gamepad(9). Writes placements JSON for rebuild_settings_1to1.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
OUT = ROOT / "docs/ui-extract/pixel-reverse/settings-layout/slice_placements.json"

# pages to process (no mouse / gamepad)
PAGES = {
    "0": None,  # shared option__pack only
    "1": None,
    "2": None,
    "3": None,
    "4": "option_4text__pack",
    "5a": "option_5sound1__pack",
    "5b": "option_5sound2__pack",
    "6": "option_6dialog__pack",
    "8": "option_8keyboard1__pack",
}

SHARED = "option__pack"
# shared slices useful as anchors (label / rail / header / sidebar / footer cmds)
SHARED_MATCH = [0, 5, 9, 12, 13, 14, 18]
CMDS = "option_cmds__pack"


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def slice_paths(pack: str) -> list[tuple[int, Path]]:
    d = SLICES / pack
    out = []
    for p in sorted(d.glob("s*.png")):
        # s000_WxH.png
        idx = int(p.name.split("_", 1)[0][1:])
        out.append((idx, p))
    return out


def ncc_match(hay: np.ndarray, needle: np.ndarray, step: int = 4) -> tuple[float, int, int]:
    """Normalized cross-correlation (higher better). hay/needle RGB float."""
    hh, hw = hay.shape[:2]
    nh, nw = needle.shape[:2]
    if nh >= hh or nw >= hw:
        return -1.0, 0, 0
    # use alpha mask of needle if available → build from variance
    n = needle.astype(np.float32)
    n_mean = n.mean(axis=(0, 1), keepdims=True)
    n_std = n.std() + 1e-6
    n0 = (n - n_mean) / n_std
    best = -1.0
    bx = by = 0
    ys = range(0, hh - nh + 1, step)
    xs = range(0, hw - nw + 1, step)
    for y in ys:
        for x in xs:
            patch = hay[y : y + nh, x : x + nw].astype(np.float32)
            p0 = (patch - patch.mean(axis=(0, 1), keepdims=True)) / (patch.std() + 1e-6)
            score = float((n0 * p0).mean())
            if score > best:
                best = score
                bx, by = x, y
    # refine around best
    if step > 1 and best > 0.15:
        y0 = max(0, by - step)
        x0 = max(0, bx - step)
        y1 = min(hh - nh, by + step)
        x1 = min(hw - nw, bx + step)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                patch = hay[y : y + nh, x : x + nw].astype(np.float32)
                p0 = (patch - patch.mean(axis=(0, 1), keepdims=True)) / (patch.std() + 1e-6)
                score = float((n0 * p0).mean())
                if score > best:
                    best = score
                    bx, by = x, y
    return best, bx, by


def sad_match_masked(hay: np.ndarray, needle_rgba: np.ndarray, step: int = 3) -> tuple[float, int, int]:
    """Lower SAD better; only opaque-ish pixels. Returns (score, x, y) with score = -mean_sad/255."""
    alpha = needle_rgba[:, :, 3]
    mask = alpha > 40
    if mask.sum() < 80:
        return -1.0, 0, 0
    rgb = needle_rgba[:, :, :3].astype(np.float32)
    nh, nw = rgb.shape[:2]
    hh, hw = hay.shape[:2]
    best = 1e18
    bx = by = 0
    ys = list(range(0, hh - nh + 1, step))
    xs = list(range(0, hw - nw + 1, step))
    # coarse
    for y in ys:
        for x in xs:
            patch = hay[y : y + nh, x : x + nw].astype(np.float32)
            diff = np.abs(patch - rgb)
            sad = float(diff[mask].mean())
            if sad < best:
                best = sad
                bx, by = x, y
    # refine
    if step > 1:
        y0 = max(0, by - step)
        x0 = max(0, bx - step)
        y1 = min(hh - nh, by + step)
        x1 = min(hw - nw, bx + step)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                patch = hay[y : y + nh, x : x + nw].astype(np.float32)
                diff = np.abs(patch - rgb)
                sad = float(diff[mask].mean())
                if sad < best:
                    best = sad
                    bx, by = x, y
    score = 1.0 - best / 255.0
    return score, bx, by


def match_slice(hay_rgb: np.ndarray, path: Path, step: int = 4) -> dict:
    im = load_rgba(path)
    w, h = im.size
    # skip tiny noise / huge that won't fit
    if w < 20 or h < 12:
        return {"ok": False, "reason": "too_small"}
    if w > 1800 or h > 1000:
        return {"ok": False, "reason": "too_large"}
    arr = np.asarray(im)
    # prefer masked SAD for UI chrome
    score, x, y = sad_match_masked(hay_rgb, arr, step=step)
    return {
        "ok": score >= 0.55,
        "score": round(score, 4),
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "file": path.name,
    }


def main() -> None:
    result: dict = {"source": "ig_option_*_1080 ImageGrab + SAD match", "pages": {}}

    # shared chrome from page 0
    hay0 = np.asarray(load_rgba(CAP / "ig_option_0_1080.png").convert("RGB"))
    shared_hits = []
    for idx in SHARED_MATCH:
        paths = {i: p for i, p in slice_paths(SHARED)}
        if idx not in paths:
            continue
        # label/rail: finer step
        step = 3 if idx in (5, 9, 14) else 5
        hit = match_slice(hay0, paths[idx], step=step)
        hit["i"] = idx
        hit["pack"] = SHARED
        shared_hits.append(hit)
        print(f"shared s{idx:03d}: ok={hit.get('ok')} score={hit.get('score')} @ ({hit.get('x')},{hit.get('y')})")

    # footer cmds
    cmds = slice_paths(CMDS)
    if cmds:
        hit = match_slice(hay0, cmds[0][1], step=4)
        hit["i"] = cmds[0][0]
        hit["pack"] = CMDS
        shared_hits.append(hit)
        print(f"cmds s000: ok={hit.get('ok')} score={hit.get('score')} @ ({hit.get('x')},{hit.get('y')})")

    # label bars: find ALL occurrences of s005 via multi-match
    label_path = {i: p for i, p in slice_paths(SHARED)}.get(5)
    labels = []
    if label_path:
        im = load_rgba(label_path)
        arr = np.asarray(im)
        hay = hay0.astype(np.float32)
        rgb = arr[:, :, :3].astype(np.float32)
        alpha = arr[:, :, 3]
        mask = alpha > 40
        nh, nw = rgb.shape[:2]
        hh, hw = hay.shape[:2]
        # scan and keep local peaks
        step = 4
        candidates = []
        for y in range(100, 960, step):
            for x in range(80, 1600, step):
                if y + nh > hh or x + nw > hw:
                    continue
                patch = hay[y : y + nh, x : x + nw]
                sad = float(np.abs(patch - rgb)[mask].mean())
                score = 1.0 - sad / 255.0
                if score >= 0.62:
                    candidates.append((score, x, y))
        # non-max suppression
        candidates.sort(reverse=True)
        for score, x, y in candidates:
            if any(abs(x - ox) < 40 and abs(y - oy) < 40 for _, ox, oy in labels):
                continue
            labels.append((round(score, 4), x, y))
            if len(labels) >= 12:
                break
        print(f"label s005 matches: {len(labels)}")
        for s, x, y in labels:
            print(f"  {s} @ ({x},{y})")

    rail_path = {i: p for i, p in slice_paths(SHARED)}.get(14)
    rails = []
    if rail_path:
        im = load_rgba(rail_path)
        arr = np.asarray(im)
        hay = hay0.astype(np.float32)
        rgb = arr[:, :, :3].astype(np.float32)
        alpha = arr[:, :, 3]
        mask = alpha > 40
        nh, nw = rgb.shape[:2]
        hh, hw = hay.shape[:2]
        step = 3
        candidates = []
        for y in range(120, 980, step):
            for x in range(80, 1600, step):
                if y + nh > hh or x + nw > hw:
                    continue
                patch = hay[y : y + nh, x : x + nw]
                sad = float(np.abs(patch - rgb)[mask].mean())
                score = 1.0 - sad / 255.0
                if score >= 0.70:
                    candidates.append((score, x, y))
        candidates.sort(reverse=True)
        for score, x, y in candidates:
            if any(abs(x - ox) < 30 and abs(y - oy) < 20 for _, ox, oy in rails):
                continue
            rails.append((round(score, 4), x, y))
            if len(rails) >= 12:
                break
        print(f"rail s014 matches: {len(rails)}")
        for s, x, y in rails:
            print(f"  {s} @ ({x},{y})")

    result["shared"] = {
        "hits": shared_hits,
        "labels_s005": [{"score": s, "x": x, "y": y, "w": 313, "h": 57} for s, x, y in labels],
        "rails_s014": [{"score": s, "x": x, "y": y, "w": 288, "h": 13} for s, x, y in rails],
    }

    for tid, pack in PAGES.items():
        hay = np.asarray(load_rgba(CAP / f"ig_option_{tid}_1080.png").convert("RGB"))
        page: dict = {"pack": pack, "slices": []}
        if pack:
            for idx, path in slice_paths(pack):
                # large pieces coarser step
                im = Image.open(path)
                w, h = im.size
                step = 6 if max(w, h) > 400 else 4
                hit = match_slice(hay, path, step=step)
                hit["i"] = idx
                hit["pack"] = pack
                page["slices"].append(hit)
                print(
                    f"tab{tid} {pack} s{idx:03d} {w}x{h}: "
                    f"ok={hit.get('ok')} score={hit.get('score')} @ ({hit.get('x')},{hit.get('y')})"
                )
        result["pages"][tid] = page

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
