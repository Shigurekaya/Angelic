# -*- coding: utf-8 -*-
"""Bake title char layers + positions strictly from FreeMote title_bg.mtn."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
MTN = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json")
LAYERS = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\layers")
META = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title\title_chars.json")
OUT = Path(r"D:\gamedev\Angelic\tools\_title_fm_compose")
OUT.mkdir(parents=True, exist_ok=True)

# id from JP name; order = mtn children back→front (来海→乃愛→かぐ耶→天音)
ID_BY_KEY = {
    "通常|キャラ|通常来海 (結合)": "kur",
    "通常|キャラ|通常乃愛 (結合) ": "noa",  # trailing space in mtn key
    "通常|キャラ|通常かぐ耶 (結合)": "kag",
    "通常|キャラ|通常天音 (結合)": "ama",
}


def log(m: str) -> None:
    print(m, flush=True)


def center_crop(im: Image.Image, view_h: int = 1080) -> Image.Image:
    if im.height <= view_h:
        return im
    top = (im.height - view_h) // 2
    return im.crop((0, top, im.width, top + view_h))


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


def tl(cx: float, cy: float, ox: float, oy: float) -> tuple[float, float]:
    return 960 + cx - ox, 540 + cy - oy


def find_slots(mtn: dict) -> list[dict]:
    icons = mtn["source"]["normal"]["icon"]
    slots = []

    def walk(L):
        lab = L.get("label") or ""
        fl = L.get("frameList") or []
        src = None
        for fr in fl:
            c = fr.get("content") or {}
            if c.get("src"):
                src = c["src"]
        if src and "結合" in lab:
            key = src.replace("src/normal/", "")
            ic = icons[key]
            t0 = t1 = None
            for fr in fl:
                c = fr.get("content") or {}
                if c.get("coord") is None:
                    continue
                t = fr.get("time")
                if t in (30, 30.0):
                    t0 = c["coord"]
                if t in (90, 90.0):
                    t1 = c["coord"]
            cid = ID_BY_KEY.get(key)
            if not cid:
                # fallback by size
                wh = (ic["width"], ic["height"])
                cid = { (400, 497): "kur", (1332, 1208): "noa", (1290, 1120): "kag", (1642, 725): "ama" }[wh]
            slots.append({
                "id": cid,
                "key": key,
                "label": lab,
                "ic": ic,
                "t0": (t0[0], t0[1]),
                "t1": (t1[0], t1[1]),
            })
        for ch in L.get("children") or []:
            walk(ch)

    for L in mtn["object"]["title_bg"]["motion"]["char_move"]["layer"]:
        walk(L)
    return slots


def png_by_size(w: int, h: int) -> Path:
    cands = [p for p in SRC.glob("*.png") if Image.open(p).size == (w, h)]
    return max(cands, key=lambda p: p.stat().st_size)


def main() -> None:
    mtn = json.loads(MTN.read_text(encoding="utf-8"))
    slots = find_slots(mtn)
    assert len(slots) == 4, slots
    log("mtn draw order (back→front):")
    for s in slots:
        log(f"  {s['id']} {s['ic']['width']}x{s['ic']['height']} t0={s['t0']} t1={s['t1']}")

    LAYERS.mkdir(parents=True, exist_ok=True)
    by_wh = {}
    for s in slots:
        wh = (s["ic"]["width"], s["ic"]["height"])
        src = png_by_size(*wh)
        im = Image.open(src).convert("RGBA")
        by_wh[wh] = im
        im.save(LAYERS / f"ch_{s['id']}.png")
        view = center_crop(im)
        view.save(LAYERS / f"ch_{s['id']}_view.png")
        log(f"  copy {s['id']} <- {src.name}")

    bg = Image.open(png_by_size(1920, 1208)).convert("RGBA")
    bg.save(LAYERS / "bg_plain.png")
    center_crop(bg).save(LAYERS / "bg_plain_view.png")
    deco = Image.open(png_by_size(1885, 1208)).convert("RGBA")
    deco.save(LAYERS / "deco_set.png")
    center_crop(deco).save(LAYERS / "deco_set_view.png")
    Image.open(png_by_size(1905, 1035)).convert("RGBA").save(LAYERS / "frame.png")
    Image.open(png_by_size(1920, 148)).convert("RGBA").save(LAYERS / "lower_gradient.png")
    charall = Image.open(png_by_size(1920, 1080)).convert("RGBA")
    charall.save(LAYERS / "charall.png")
    logo = max(SRC.glob("logo_cn*.png"), key=lambda p: p.stat().st_size)
    Image.open(logo).convert("RGBA").save(LAYERS / "logo_cn_layer.png")

    icons = mtn["source"]["normal"]["icon"]
    bg_v = center_crop(bg)
    canvas = bg_v.copy()
    chars_out = []
    order = []
    for s in slots:
        ic = s["ic"]
        im = by_wh[(ic["width"], ic["height"])]
        sx, sy = tl(s["t0"][0], s["t0"][1], ic["originX"], ic["originY"])
        ex, ey = tl(s["t1"][0], s["t1"][1], ic["originX"], ic["originY"])
        place(canvas, im, ex, ey)
        top = (ic["height"] - 1080) // 2 if ic["height"] > 1080 else 0
        chars_out.append({
            "id": s["id"],
            "image": f"angelic/title/layers/ch_{s['id']}_view.png",
            "sx": int(round(sx + 0)),
            "sy": int(round(sy + top)),
            "ex": int(round(ex + 0)),
            "ey": int(round(ey + top)),
            "full_ex": int(round(ex)),
            "full_ey": int(round(ey)),
            "fade0": 0.5,
            "fade1": 1.5,
            "move_end": 1.5,
            "fm_t0": [s["t0"][0], s["t0"][1]],
            "fm_t1": [s["t1"][0], s["t1"][1]],
            "origin": [ic["originX"], ic["originY"]],
            "size": [ic["width"], ic["height"]],
            "view_top": top,
            "mtn_key": s["key"],
        })
        order.append(s["id"])
        log(f"  {s['id']}: view ({chars_out[-1]['sx']},{chars_out[-1]['sy']})->({chars_out[-1]['ex']},{chars_out[-1]['ey']})")

    # add deco for MSE
    dic = icons["通常|通常羽"]
    dx, dy = tl(16, 0, dic["originX"], dic["originY"])
    place(canvas, deco, dx, dy)
    err = mse(canvas, charall)
    canvas.save(OUT / "fix_final.png")
    side = Image.new("RGB", (3840, 1080))
    side.paste(charall.convert("RGB"), (0, 0))
    side.paste(canvas.convert("RGB"), (1920, 0))
    side.save(OUT / "side_charall_vs_compose.png")
    log(f"MSE vs 通常セット (bg+4chars+羽) = {err:.1f}")

    gic = icons["lower_gradient"]
    fic = icons["frame"]
    lic = mtn["source"]["logo_cn"]["icon"]["logo_cn"]
    d_top = (1208 - 1080) // 2
    meta = {
        "chars": chars_out,
        "order": order,
        "draw_order_back_to_front": order,
        "fps": 60,
        "char_move_last": 121,
        "logo_last": 41,
        "fm_formula": "TL = (960+cx-originX, 540+cy-originY); view_y += center_crop_top",
        "fm_mse_vs_charall": round(err, 2),
        "note": "slots from title_bg.mtn src keys; order 来海→乃愛→かぐ耶→天音",
        "extras": {
            "bg_plain": {
                "image": "angelic/title/layers/bg_plain_view.png",
                "zx0": 1.1,
                "zoom_frames": 90,
            },
            "deco_set": {
                "image": "angelic/title/layers/deco_set_view.png",
                "fade0": 0.5,
                "fade1": 1.5,
                "zx0": 1.5,
                "xy": [int(round(dx)), int(round(dy + d_top))],
            },
            "lower_gradient": {
                "image": "angelic/title/layers/lower_gradient.png",
                "fade0": 1.5,
                "fade1": 2.0,
                "y0": int(round(tl(0, 530, gic["originX"], gic["originY"])[1])),
                "y1": int(round(tl(0, 466, gic["originX"], gic["originY"])[1])),
                "opa1": 0.8,
            },
            "frame": {
                "image": "angelic/title/layers/frame.png",
                "fade0": 1.5,
                "fade1": 2.0,
                "xy": [int(round(v)) for v in tl(1, -15, fic["originX"], fic["originY"])],
            },
            "logo_cn": {
                "image": "angelic/title/layers/logo_cn_layer.png",
                "xy": [int(round(v)) for v in tl(-566, 300, lic["originX"], lic["originY"])],
                "zx0": 1.1,
                "fade1": 41 / 60.0,
            },
        },
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"wrote {META}")
    log(f"grad {meta['extras']['lower_gradient']['y0']}->{meta['extras']['lower_gradient']['y1']}")
    log(f"frame {meta['extras']['frame']['xy']} deco {meta['extras']['deco_set']['xy']} logo {meta['extras']['logo_cn']['xy']}")


if __name__ == "__main__":
    main()
