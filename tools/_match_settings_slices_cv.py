# -*- coding: utf-8 -*-
"""Fast OpenCV match of official slices onto ig_option captures. No mouse/gamepad."""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
OUT = ROOT / "docs/ui-extract/pixel-reverse/settings-layout/slice_placements.json"
KEEP = ["0", "1", "2", "3", "4", "5a", "5b", "6", "8"]

def load_bgr(path: Path):
    arr = np.asarray(Image.open(path).convert("RGBA"))
    bgr = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR)
    return bgr, arr[:, :, 3]

def load_hay(path: Path):
    im = np.asarray(Image.open(path).convert("RGB"))
    return cv2.cvtColor(im, cv2.COLOR_RGB2BGR)

def match_multi(hay, needle, alpha, thr=0.72, maxn=14, nms=40):
    mask = (alpha > 40).astype(np.uint8) * 255
    if int(mask.sum()) < 200:
        return []
    res = cv2.matchTemplate(hay, needle, cv2.TM_CCORR_NORMED, mask=mask)
    h, w = needle.shape[:2]
    hits, work = [], res.copy()
    for _ in range(maxn):
        _mn, maxv, _ml, maxl = cv2.minMaxLoc(work)
        if maxv < thr:
            break
        x, y = int(maxl[0]), int(maxl[1])
        hits.append({"score": round(float(maxv), 4), "x": x, "y": y, "w": w, "h": h})
        work[max(0, y - nms): y + nms, max(0, x - nms): x + nms] = 0
    return hits

def slice_file(pack, idx):
    d = SLICES / pack
    for p in d.glob(f"s{idx:03d}_*.png"):
        return p
    return None

def all_slices(pack):
    out = []
    for p in sorted((SLICES / pack).glob("s*.png")):
        out.append((int(p.name.split("_", 1)[0][1:]), p))
    return out

def main():
    hay0 = load_hay(CAP / "ig_option_0_1080.png")
    shared = {}
    specs = [
        ("labels_s005", "option__pack", 5, 0.78, 45, 12),
        ("rails_s014", "option__pack", 14, 0.82, 22, 12),
        ("knobs_s018", "option__pack", 18, 0.70, 28, 12),
        ("details_s011", "option__pack", 11, 0.70, 30, 10),
        ("mutes_s010", "option__pack", 10, 0.70, 30, 10),
        ("sidebar_s000", "option__pack", 0, 0.65, 80, 2),
    ]
    for key, pack, idx, thr, nms, maxn in specs:
        p = slice_file(pack, idx)
        if not p:
            continue
        nb, al = load_bgr(p)
        hits = match_multi(hay0, nb, al, thr=thr, maxn=maxn, nms=nms)
        shared[key] = hits
        print(key, len(hits), hits[:2])

    cmds = all_slices("option_cmds__pack")
    if cmds:
        nb, al = load_bgr(cmds[0][1])
        shared["footer_cmds"] = match_multi(hay0, nb, al, thr=0.62, maxn=4, nms=60)
        print("footer", shared["footer_cmds"])

    pack_map = {
        "4": "option_4text__pack",
        "5a": "option_5sound1__pack",
        "5b": "option_5sound2__pack",
        "6": "option_6dialog__pack",
        "8": "option_8keyboard1__pack",
    }
    caps = ["0", "3", "4", "5a", "5b", "6", "8"]
    pack_best = {}
    for tid, pack in pack_map.items():
        slices = all_slices(pack)
        if not slices:
            continue
        best_i, best_p = max(slices, key=lambda t: Image.open(t[1]).size[0] * Image.open(t[1]).size[1])
        nb, al = load_bgr(best_p)
        best_score, best_cap, best_hit = -1.0, "0", None
        for cid in caps:
            hay = load_hay(CAP / f"ig_option_{cid}_1080.png")
            hits = match_multi(hay, nb, al, thr=0.40, maxn=1, nms=100)
            if hits and hits[0]["score"] > best_score:
                best_score, best_cap, best_hit = hits[0]["score"], cid, hits[0]
        pack_best[tid] = best_cap
        print(f"pack {pack} -> cap {best_cap} score={best_score:.3f}", best_hit)

    pages = {}
    for tid, pack in pack_map.items():
        cid = pack_best.get(tid, "0")
        hay = load_hay(CAP / f"ig_option_{cid}_1080.png")
        items = []
        for idx, path in all_slices(pack):
            nb, al = load_bgr(path)
            w, h = nb.shape[1], nb.shape[0]
            thr = 0.55 if max(w, h) > 200 else 0.65
            hits = match_multi(hay, nb, al, thr=thr, maxn=1, nms=100)
            item = {"i": idx, "pack": pack, "file": path.name, "w": w, "h": h, "cap": cid, "ok": bool(hits)}
            if hits:
                item.update(hits[0])
            items.append(item)
            print(f"  {tid} s{idx:03d} ok={item['ok']} score={item.get('score')} @({item.get('x')},{item.get('y')})")
        pages[tid] = {"pack": pack, "cap": cid, "slices": items}

    labels = shared.get("labels_s005") or []
    left = sorted([h for h in labels if h["x"] < 900], key=lambda h: h["y"])
    right = sorted([h for h in labels if h["x"] >= 900], key=lambda h: h["y"])
    grid = {
        "left_x": int(np.median([h["x"] for h in left])) if left else 200,
        "right_x": int(np.median([h["x"] for h in right])) if right else 1020,
        "row_ys": [h["y"] for h in left] if left else [160, 300, 440, 580, 720],
        "right_ys": [h["y"] for h in right],
    }
    print("grid", grid)
    doc = {
        "source": "ig_option + cv2.matchTemplate",
        "exclude_pages": ["7", "9"],
        "keep_tabs": KEEP,
        "shared": shared,
        "grid": grid,
        "pages": pages,
        "pack_best_cap": pack_best,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)

if __name__ == "__main__":
    main()
