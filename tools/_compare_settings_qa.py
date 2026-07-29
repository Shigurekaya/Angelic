# -*- coding: utf-8 -*-
"""Side-by-side QA: renpy plates vs official bg / previous QA, write report."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:/gamedev/Angelic")
PLATES = ROOT.parent / "renpy-angelic/game/images/angelic/settings/plates"
QA = ROOT / "tools/_qa_tab0_official.png"
OUT = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture"
BG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png/option__bg0.png"


def mad(a: Image.Image, b: Image.Image) -> float:
    a = a.convert("RGB").resize((480, 270))
    b = b.convert("RGB").resize((480, 270))
    diff = 0
    n = 0
    for pa, pb in zip(a.getdata(), b.getdata()):
        for x, y in zip(pa, pb):
            diff += abs(x - y)
            n += 1
    return diff / max(1, n)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"plates": {}, "qa_vs_tab0": None, "note": "pbd-uistates bake; orig live capture optional"}
    tab0 = Image.open(PLATES / "tab_0.png")
    if QA.exists():
        report["qa_vs_tab0"] = round(mad(tab0, Image.open(QA)), 4)
        # composite strip
        q = Image.open(QA).convert("RGBA").resize((960, 540))
        t = tab0.convert("RGBA").resize((960, 540))
        strip = Image.new("RGBA", (1920, 560), (20, 30, 50, 255))
        strip.paste(q, (0, 20))
        strip.paste(t, (960, 20))
        dr = ImageDraw.Draw(strip)
        try:
            font = ImageFont.truetype(r"C:/Windows/Fonts/msyh.ttc", 18)
        except Exception:
            font = ImageFont.load_default()
        dr.text((20, 0), "QA / bake truth", font=font, fill=(255, 255, 255, 255))
        dr.text((980, 0), "renpy plate tab_0", font=font, fill=(255, 255, 255, 255))
        strip.save(OUT / "compare_tab0_qa_vs_plate.png")

    for p in sorted(PLATES.glob("tab_*.png")):
        im = Image.open(p).convert("RGBA")
        # density vs bare bg
        dens = 0
        sample = im.resize((192, 108))
        for r, g, b, a in sample.getdata():
            if a > 40 and (r < 200 or g < 210 or b < 230):
                dens += 1
        report["plates"][p.name] = {"size": list(im.size), "dense_preview": dens}

    (OUT / "REBAKE-COMPARE-REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
