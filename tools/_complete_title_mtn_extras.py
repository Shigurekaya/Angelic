# -*- coding: utf-8 -*-
"""Extract missing title_bg.mtn layers into title_chars.json extras."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
META = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\title_chars.json")
SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
LAYERS = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\layers")
FPS = 60.0


def tl(cx, cy, ox, oy):
    return 960 + cx - ox, 540 + cy - oy


def find_frames(label_substr: str):
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    hits = []

    def walk(L, path=""):
        lab = L.get("label") or ""
        p = f"{path}/{lab}"
        if label_substr in lab or label_substr in p:
            frames = []
            for fr in L.get("frameList") or []:
                c = fr.get("content") or {}
                frames.append({
                    "t": fr.get("time"),
                    "type": fr.get("type"),
                    "coord": c.get("coord"),
                    "opa": c.get("opa"),
                    "zx": c.get("zx"),
                    "zy": c.get("zy"),
                    "src": c.get("src"),
                })
            hits.append({"label": lab, "path": p, "visible": L.get("visible"), "frames": frames})
        for ch in L.get("children") or []:
            walk(ch, p)

    for L in mtn["object"]["title_bg"]["motion"]["char_move"]["layer"]:
        walk(L)
    return hits, mtn


def center_crop(im, h=1080):
    if im.height <= h:
        return im
    top = (im.height - h) // 2
    return im.crop((0, top, im.width, top + h))


def png_by_size(w, h):
    cands = [p for p in SRC.glob("*.png") if Image.open(p).size == (w, h)]
    return max(cands, key=lambda p: p.stat().st_size)


def main():
    meta = json.loads(META.read_text(encoding="utf-8"))
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    icons = mtn["source"]["normal"]["icon"]

    # Ensure siro + charall layers on disk
    siro_src = png_by_size(2048, 1208)  # 背景 is 2048; 白 might be same size
    # prefer exact 白 from resx size 12529
    for p in SRC.glob("*.png"):
        if p.stat().st_size in (12529, 12616) and Image.open(p).size == (2048, 1208):
            siro_src = p
            break
    siro = Image.open(siro_src).convert("RGBA")
    # crop to 1920x1080 center of 2048x1208
    left = (siro.width - 1920) // 2
    top = (siro.height - 1080) // 2
    siro_v = siro.crop((left, top, left + 1920, top + 1080))
    LAYERS.mkdir(parents=True, exist_ok=True)
    siro_v.save(LAYERS / "siro_view.png")
    print("siro", siro_src.name, "->", siro_v.size)

    charall = png_by_size(1920, 1080)
    Image.open(charall).convert("RGBA").save(LAYERS / "charall.png")

    # Parse key layers
    for name in ("siro", "通常bg", "通常セット", "通常羽", "lower_gradient", "frame"):
        hits, _ = find_frames(name if name != "通常bg" else "通常bg")
        # refine: 通常bg label exact
        print(f"\n== {name} ==")
        for h in hits:
            if name == "通常bg" and h["label"] != "通常bg":
                continue
            if name == "通常セット" and h["label"] != "通常セット":
                continue
            if name == "通常羽" and h["label"] != "通常羽":
                continue
            print(" ", h["label"], "vis", h["visible"])
            for fr in h["frames"]:
                print("   ", fr)

    # Build extras from known FM facts + icon origins
    gic = icons["lower_gradient"]
    fic = icons["frame"]
    dic = icons["通常|通常羽"]
    lic = mtn["source"]["logo_cn"]["icon"]["logo_cn"]
    d_top = (1208 - 1080) // 2
    dx, dy = tl(16, 0, dic["originX"], dic["originY"])

    # logo_cn motion timing
    logo_m = mtn["object"]["logo"]["motion"]["logo_cn"]
    logo_last = float(logo_m.get("lastTime") or 41)

    # When is logo triggered in char_move? type3 motion link at t~80
    logo_trigger = 80.0

    meta["extras"] = {
        "siro": {
            "image": "angelic/title/layers/siro_view.png",
            "fade0": 0.0,
            "fade1": 50 / FPS,  # t50 opa0
            "note": "白闪 t0→t50 fade out",
        },
        "bg_plain": {
            "image": "angelic/title/layers/bg_plain_view.png",
            "zx0": 1.1,
            "zoom_end": 90 / FPS,
            "alpha_start": 1.0,
            "note": "通常bg t0 zx1.1 → t90 zx1; no opa fade",
        },
        "deco_set": {
            "image": "angelic/title/layers/deco_set_view.png",
            "fade0": 30 / FPS,
            "fade1": 90 / FPS,
            "zx0": 1.5,
            "xy": [int(round(dx)), int(round(dy + d_top))],
        },
        "lower_gradient": {
            "image": "angelic/title/layers/lower_gradient.png",
            "fade0": 90 / FPS,
            "fade1": 120 / FPS,
            "y0": int(round(tl(0, 530, gic["originX"], gic["originY"])[1])),
            "y1": int(round(tl(0, 466, gic["originX"], gic["originY"])[1])),
            "opa1": 204 / 255.0,
        },
        "frame": {
            "image": "angelic/title/layers/frame.png",
            "fade0": 90 / FPS,
            "fade1": 120 / FPS,
            "xy": [int(round(v)) for v in tl(1, -15, fic["originX"], fic["originY"])],
        },
        "logo_cn": {
            "image": "angelic/title/layers/logo_cn_layer.png",
            "xy": [int(round(v)) for v in tl(-566, 300, lic["originX"], lic["originY"])],
            "zx0": 1.1,
            "trigger": logo_trigger / FPS,
            "fade1": logo_last / FPS,
            "note": "char_move embeds logo at t80; logo_cn lastTime=41",
        },
        "charall": {
            "image": "angelic/title/layers/charall.png",
            "fade0": 90 / FPS,
            "fade1": 100 / FPS,
            "note": "通常セット settle plate before final bgN",
        },
    }
    meta["timing"] = {
        "fps": FPS,
        "char_move_last": 121 / FPS,
        "btn_at": 120 / FPS,
        "finish_at": 121 / FPS + 0.35,
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nwrote", META)
    print("extras keys", list(meta["extras"]))
    print("logo", meta["extras"]["logo_cn"])
    print("grad", meta["extras"]["lower_gradient"])


if __name__ == "__main__":
    main()
