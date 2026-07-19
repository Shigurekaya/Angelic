# -*- coding: utf-8 -*-
"""Map mtn char slots → PNG by src path; brute-check size assignment vs charall."""
from __future__ import annotations

import json
from itertools import permutations
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
OUT = Path(r"D:\gamedev\Angelic\tools\_title_fm_compose")


def walk_chars(mtn):
    cm = mtn["object"]["title_bg"]["motion"]["char_move"]
    # find キャラ group children
    slots = []

    def walk(L, path=""):
        lab = L.get("label") or ""
        fl = L.get("frameList") or []
        coords = []
        src = None
        for fr in fl:
            c = fr.get("content") or {}
            if c.get("src"):
                src = c["src"]
            if "coord" in c:
                coords.append((fr.get("time"), c["coord"], c.get("opa")))
        children = L.get("children") or []
        if coords and src and "キャラ" in (path + lab) or (
            coords and src and "結合" in (src or "")
        ):
            if "結合" in (src or "") or "結合" in lab:
                slots.append({"label": lab, "src": src, "coords": coords})
        for ch in children:
            walk(ch, path + "/" + lab)

    for L in cm.get("layer") or []:
        walk(L)
    return slots


def center_crop(im):
    if im.height <= 1080:
        return im
    top = (im.height - 1080) // 2
    return im.crop((0, top, im.width, top + 1080))


def place(canvas, layer, tlx, tly):
    x, y = int(round(tlx)), int(round(tly))
    tmp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tmp.alpha_composite(layer, (x, y))
    canvas.alpha_composite(tmp)


def mse(a, b):
    aa = np.asarray(a.convert("RGBA"), dtype=np.float32)
    bb = np.asarray(b.convert("RGBA"), dtype=np.float32)
    m = (aa[..., 3] > 8) | (bb[..., 3] > 8)
    d = (aa[..., :3] - bb[..., :3])[m]
    return float(np.mean(d * d))


def tl(cx, cy, ox, oy):
    return 960 + cx - ox, 540 + cy - oy


def main():
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    slots = walk_chars(mtn)
    print("SLOTS from mtn:", len(slots))
    for s in slots:
        print(" ", s["label"])
        print("   src=", s["src"])
        print("   coords=", s["coords"])

    # icons
    icons = {(ic["width"], ic["height"]): ic for ic in mtn["source"]["normal"]["icon"].values()}
    # also print icon keys with names
    print("\nICONS:")
    for name, ic in mtn["source"]["normal"]["icon"].items():
        print(f"  {name!r}: {ic['width']}x{ic['height']} origin=({ic['originX']},{ic['originY']})")

    # map slot src → size via icon name in src path
    # src like src/normal/通常|キャラ|通常天音 (結合)
    print("\nSlot→icon match:")
    for s in slots:
        src = s["src"]
        matched = None
        for name, ic in mtn["source"]["normal"]["icon"].items():
            # name uses | separators
            if name.replace("|", "/") in src.replace("|", "/") or name in src:
                matched = (name, ic)
                break
            # fuzzy: last segment
            last = name.split("|")[-1]
            if last and last in src:
                matched = (name, ic)
                break
        s["icon"] = matched[1] if matched else None
        s["icon_name"] = matched[0] if matched else None
        print(f"  {s['label'][:20]} -> {s['icon_name']!r} size={None if not s['icon'] else (s['icon']['width'], s['icon']['height'])}")

    # load PNGs by size
    by_wh = {}
    for p in SRC.glob("*.png"):
        im = Image.open(p)
        by_wh[im.size] = max([by_wh[im.size], p], key=lambda x: x.stat().st_size) if im.size in by_wh else p

    charall = Image.open(by_wh[(1920, 1080)]).convert("RGBA")
    bg = center_crop(Image.open(by_wh[(1920, 1208)]).convert("RGBA"))

    # If icons matched, compose directly
    if all(s.get("icon") for s in slots):
        canvas = bg.copy()
        for s in slots:
            ic = s["icon"]
            wh = (ic["width"], ic["height"])
            im = Image.open(by_wh[wh]).convert("RGBA")
            # end coord = last with coord
            end = [c for c in s["coords"] if c[0] and c[0] >= 90] or s["coords"]
            t, coord, opa = end[-1]
            cx, cy = coord[0], coord[1]
            x, y = tl(cx, cy, ic["originX"], ic["originY"])
            place(canvas, im, x, y)
            print(f"place {s['icon_name'][-20:]} at ({x:.0f},{y:.0f}) t={t}")
        err = mse(canvas, charall)
        canvas.save(OUT / "fix_src_matched.png")
        print(f"src-matched MSE={err:.1f}")

    # Also: for each slot end coord, which image size fits best alone on bg vs charall residual
    print("\n=== per-slot best image ===")
    # residual start = charall (we'll score each layer placement vs charall in opaque region)
    sizes = [(1642, 725), (1332, 1208), (1290, 1120), (400, 497)]
    end_coords = []
    for s in slots:
        end = [c for c in s["coords"] if c[1] is not None]
        # prefer t~90
        end90 = [c for c in end if c[0] is not None and abs(float(c[0]) - 90) < 1]
        pick = end90[-1] if end90 else end[-1]
        end_coords.append((s["label"], pick[1][0], pick[1][1]))

    for lab, cx, cy in end_coords:
        best = None
        for wh in sizes:
            ic = icons[wh]
            im = Image.open(by_wh[wh]).convert("RGBA")
            x, y = tl(cx, cy, ic["originX"], ic["originY"])
            canvas = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
            place(canvas, im, x, y)
            ca = np.asarray(canvas)
            ra = np.asarray(charall)
            m = ca[..., 3] > 40
            if not m.any():
                continue
            d = (ca[..., :3].astype(np.float32) - ra[..., :3].astype(np.float32))[m]
            e = float(np.mean(d * d))
            if best is None or e < best[0]:
                best = (e, wh, int(x), int(y))
        print(f"  slot {lab[:30]} coord=({cx},{cy}) best_size={best}")

    # brute permute 4 sizes onto 4 slots
    print("\n=== brute permutations ===")
    best_p = None
    for perm in permutations(sizes):
        canvas = bg.copy()
        for (lab, cx, cy), wh in zip(end_coords, perm):
            ic = icons[wh]
            im = Image.open(by_wh[wh]).convert("RGBA")
            x, y = tl(cx, cy, ic["originX"], ic["originY"])
            place(canvas, im, x, y)
        err = mse(canvas, charall)
        if best_p is None or err < best_p[0]:
            best_p = (err, perm, [(lab, wh) for (lab, cx, cy), wh in zip(end_coords, perm)])
    print(f"BEST perm MSE={best_p[0]:.1f}")
    for lab, wh in best_p[2]:
        print(f"  {lab[:40]} -> {wh}")


if __name__ == "__main__":
    main()
