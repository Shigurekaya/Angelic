# -*- coding: utf-8 -*-
"""Self-check Angelic title bake vs unpack tiles + optional orig ref."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PREV = ROOT / "ui-preview/assets/title"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
ORIG = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture/manual/title_orig_1080.png"
OUT = ROOT / "docs/ui-extract/pixel-reverse/_text_preview/title_qa"
OUT.mkdir(parents=True, exist_ok=True)

LABELS = {
    0: "流程图",
    1: "退出黄?",
    2: "退出",
    3: "流程图黄",
    4: "鉴赏黄",
    5: "鉴赏选",
    6: "追加黄",
    8: "系统",
    10: "系统黄",
    11: "从头开始",
    12: "继续黄",
    13: "继续选",
    14: "载入",
    15: "继续",
    16: "载入黄",
    17: "鉴赏",
    18: "追加",
    19: "载入选",
    20: "从头黄",
    22: "退出选",
    23: "流程图选",
}


def mean_diff(a: Image.Image, b: Image.Image) -> float:
    a = a.convert("RGB").resize((a.width, a.height))
    b = b.convert("RGB").resize(a.size)
    d = ImageChops.difference(a, b)
    hist = d.histogram()
    # rough mean over RGB
    s = 0
    n = 0
    for i, c in enumerate(hist):
        s += (i % 256) * c
        n += c
    return s / max(1, n)


def crop_nonblack(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    xs, ys = [], []
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a > 20 and (r + g + b) > 40:
                xs.append(x)
                ys.append(y)
    if not xs:
        return im
    return im.crop((min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def main() -> None:
    hs = json.loads((PREV / "hotspots.json").read_text(encoding="utf-8"))
    issues = []

    # 1) buttons exist and match slice sizes
    for b in hs["buttons"]:
        p = PREV / b["idle"]
        if not p.exists():
            issues.append(f"missing {b['idle']}")
            continue
        im = Image.open(p)
        if im.size != (b["w"], b["h"]):
            issues.append(f"size mismatch {b['id']}: file {im.size} meta {b['w']}x{b['h']}")
        # opaque black leftover?
        px = im.convert("RGBA").load()
        black = 0
        for y in range(im.height):
            for x in range(im.width):
                r, g, bgr, a = px[x, y]
                if a > 10 and r <= 18 and g <= 18 and bgr <= 18:
                    black += 1
        if black > 50:
            issues.append(f"opaque black leftover {b['id']}: {black}px")

    # 2) icons
    for key in ("lang", "reload"):
        ic = hs["icons"][key]
        for f in (ic["idle"], ic.get("hover")):
            if f and not (PREV / f).exists():
                issues.append(f"missing icon {f}")
        if key == "lang":
            ovs = ic.get("overlays") or []
            if len(ovs) < 2:
                issues.append(f"lang overlays too few: {len(ovs)}")
            for ov in ovs:
                if not (PREV / ov["file"]).exists():
                    issues.append(f"missing overlay {ov['file']}")
                # must stay inside plate
                if ov["x"] < 0 or ov["y"] < 0 or ov["x"] + ov["w"] > ic["w"] or ov["y"] + ov["h"] > ic["h"]:
                    issues.append(f"overlay OOB {ov}")

    # 3) rebuild lang plate preview for eye check
    plate = Image.open(PREV / hs["icons"]["lang"]["idle"]).convert("RGBA")
    for ov in hs["icons"]["lang"].get("overlays") or []:
        plate.alpha_composite(Image.open(PREV / ov["file"]), (ov["x"], ov["y"]))
    plate.save(OUT / "lang_layered.png")

    # 4) compare composite vs orig if present
    comp = Image.open(PREV / "composite.png").convert("RGBA")
    if ORIG.exists():
        orig = Image.open(ORIG).convert("RGBA")
        if orig.size != comp.size:
            issues.append(f"orig size {orig.size} != comp {comp.size}")
        else:
            # bottom bar band
            band_o = orig.crop((0, 980, 1920, 1080))
            band_c = comp.crop((0, 980, 1920, 1080))
            md = mean_diff(band_o, band_c)
            print(f"bottom band mean_diff={md:.2f}")
            # side-by-side
            side = Image.new("RGB", (1920, 220), (0, 0, 0))
            side.paste(band_o.convert("RGB"), (0, 0))
            side.paste(band_c.convert("RGB"), (0, 110))
            side.save(OUT / "compare_bottom.png")
            # TR / BR
            for name, box in (("tr", (1750, 0, 1920, 130)), ("br", (1750, 940, 1920, 1080))):
                o = orig.crop(box)
                c = comp.crop(box)
                Image.new("RGB", (box[2] - box[0], (box[3] - box[1]) * 2)).paste
                s = Image.new("RGB", (box[2] - box[0], (box[3] - box[1]) * 2))
                s.paste(o.convert("RGB"), (0, 0))
                s.paste(c.convert("RGB"), (0, box[3] - box[1]))
                s.save(OUT / f"compare_{name}.png")
                print(f"{name} mean_diff={mean_diff(o, c):.2f}")

            # template-match each idle button on orig bottom to see position error
            print("--- button match on orig ---")
            for b in hs["buttons"]:
                tile = Image.open(PREV / b["idle"]).convert("RGBA")
                # search near claimed pos
                best = None
                tw, th = tile.size
                x0 = max(0, b["x"] - 40)
                y0 = max(980, b["y"] - 20)
                x1 = min(1920 - tw, b["x"] + 40)
                y1 = min(1080 - th, b["y"] + 20)
                tp = tile.load()
                # precompute opaque mask
                mask = []
                for yy in range(th):
                    for xx in range(tw):
                        r, g, bb, a = tp[xx, yy]
                        if a > 40 and (r + g + bb) > 80:
                            mask.append((xx, yy, r, g, bb))
                for y in range(y0, y1 + 1, 2):
                    for x in range(x0, x1 + 1, 2):
                        s = 0
                        for xx, yy, r, g, bb in mask:
                            or_, og, ob, _ = orig.getpixel((x + xx, y + yy))
                            s += abs(r - or_) + abs(g - og) + abs(bb - ob)
                        score = s / max(1, len(mask))
                        if best is None or score < best[0]:
                            best = (score, x, y)
                if best:
                    dx = best[1] - b["x"]
                    dy = best[2] - b["y"]
                    print(f"  {b['id']:10} claim=({b['x']},{b['y']}) best=({best[1]},{best[2]}) d=({dx},{dy}) score={best[0]:.1f}")
                    if abs(dx) > 12 or abs(dy) > 8:
                        issues.append(f"pos drift {b['id']}: dx={dx} dy={dy}")

    # 5) contact of current idle buttons
    sheet = Image.new("RGBA", (8 * 140, 60), (30, 30, 30, 255))
    for i, b in enumerate(hs["buttons"]):
        im = Image.open(PREV / b["idle"]).convert("RGBA")
        sheet.alpha_composite(im, (i * 140 + 10, 10))
    sheet.save(OUT / "idle_row.png")

    print("--- issues ---")
    for it in issues:
        print("!", it)
    print("issue_count", len(issues))
    (OUT / "issues.json").write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
