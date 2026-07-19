# -*- coding: utf-8 -*-
"""Analyze original title_menu capture vs title_locale button crops; emit placement."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

CAP = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
AUDIT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_text_preview")
SLICES = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_pack_slices/title_locale_cn__pack")
OUT = CAP / "analysis"


def to_1080(im: Image.Image) -> Image.Image:
    if im.size == (1920, 1080):
        return im.convert("RGBA")
    return im.convert("RGBA").resize((1920, 1080), Image.Resampling.LANCZOS)


def score_match(hay: Image.Image, needle: Image.Image, step: int = 3) -> tuple[float, int, int]:
    """Brute force SAD match (needle over hay). Returns (score, x, y) lower better."""
    hay = hay.convert("RGBA")
    needle = needle.convert("RGBA")
    # strip near-black from needle for mask
    nw, nh = needle.size
    hw, hh = hay.size
    npx = needle.load()
    hpx = hay.load()
    mask = []
    for y in range(nh):
        for x in range(nw):
            r, g, b, a = npx[x, y]
            if a > 40 and (r + g + b) > 60:
                mask.append((x, y, r, g, b))
    if len(mask) < 30:
        return 1e18, 0, 0
    best = 1e18
    bx = by = 0
    # search right half + bottom for menu
    x0, x1 = int(hw * 0.55), hw - nw
    y0, y1 = int(hh * 0.20), hh - nh
    for y in range(y0, max(y0 + 1, y1), step):
        for x in range(x0, max(x0 + 1, x1), step):
            s = 0
            n = 0
            for dx, dy, r, g, b in mask:
                rr, gg, bb, aa = hpx[x + dx, y + dy]
                s += abs(rr - r) + abs(gg - g) + abs(bb - b)
                n += 1
                if s > best * n / max(1, len(mask)) and n > 40:
                    break
            score = s / max(1, n)
            if score < best:
                best = score
                bx, by = x, y
    return best, bx, by


def analyze_capture(path: Path) -> dict:
    im = to_1080(Image.open(path))
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / "base_1080.png")
    # save quadrants for human check
    w, h = im.size
    im.crop((0, 0, w // 2, h // 2)).save(OUT / "q_tl.png")
    im.crop((w // 2, 0, w, h // 2)).save(OUT / "q_tr.png")
    im.crop((0, h // 2, w // 2, h)).save(OUT / "q_bl.png")
    im.crop((w // 2, h // 2, w, h)).save(OUT / "q_br.png")
    im.crop((0, int(h * 0.82), w, h)).save(OUT / "bottom_strip.png")
    im.crop((int(w * 0.78), int(h * 0.25), w, int(h * 0.95))).save(OUT / "right_strip.png")

    # match known button crops
    # verified mapping from earlier session
    keys = {
        "start": (11, 20),  # idle cyan, hover yellow indices in title_btn_XX
        "continue": (15, 12),
        "load": (14, 16),
        "flowchart": (0, 3),
        "extra": (17, 4),
        "after": (18, 6),
        "system": (8, 10),
        "exit": (2, 1),
    }
    hits = {}
    for key, (idle_i, hover_i) in keys.items():
        for state, idx in (("idle", idle_i), ("hover", hover_i)):
            p = AUDIT / f"title_btn_{idx:02d}.png"
            if not p.exists():
                continue
            needle = Image.open(p)
            # try match
            score, x, y = score_match(im, needle, step=4)
            hits[f"{key}_{state}"] = {"score": round(score, 2), "x": x, "y": y, "idx": idx, "size": list(needle.size)}
            print(f"{key}_{state}: score={score:.1f} @ ({x},{y}) size={needle.size}")
    return {"capture": str(path), "size": [w, h], "matches": hits}


def main():
    # prefer title_menu_1080
    for name in ["title_menu_1080.png", "title_menu.png", "title_content_1080.png"]:
        p = CAP / name
        if p.exists():
            print("using", name)
            report = analyze_capture(p)
            (OUT / "title_match.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            # pick best idle matches (lowest score) for layout
            layout = []
            for key in ["start", "continue", "load", "flowchart", "extra", "after", "system", "exit"]:
                m = report["matches"].get(f"{key}_idle") or report["matches"].get(f"{key}_hover")
                if m:
                    layout.append({"id": key, **m})
            layout.sort(key=lambda d: d["y"])
            (OUT / "title_layout_guess.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
            print("layout order:", [x["id"] for x in layout])
            return
    print("NO capture")


if __name__ == "__main__":
    main()
