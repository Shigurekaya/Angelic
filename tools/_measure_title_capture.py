# -*- coding: utf-8 -*-
"""Measure title menu bands from original capture; rebuild title to match."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

CAP = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
OUT = CAP / "measure"


def measure(path: Path) -> dict:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    rows = []
    for y in range(h):
        hits = 0
        xmin, xmax = w, 0
        for x in range(int(w * 0.70), w):
            r, g, b, a = px[x, y]
            yellow = r > 200 and g > 170 and b < 140
            cyan = b > 180 and g > 140 and r < 160
            white = r > 230 and g > 230 and b > 230
            if yellow or cyan or (white and x > int(w * 0.78)):
                hits += 1
                xmin = min(xmin, x)
                xmax = max(xmax, x)
        if hits > 10:
            rows.append((y, hits, xmin, xmax))
    bands = []
    cur = None
    for y, hits, xmin, xmax in rows:
        if cur is None or y - cur["y1"] > 8:
            if cur:
                bands.append(cur)
            cur = {"y0": y, "y1": y, "hits": hits, "xmin": xmin, "xmax": xmax}
        else:
            cur["y1"] = y
            cur["hits"] += hits
            cur["xmin"] = min(cur["xmin"], xmin)
            cur["xmax"] = max(cur["xmax"], xmax)
    if cur:
        bands.append(cur)
    # filter short noise
    bands = [b for b in bands if (b["y1"] - b["y0"]) >= 8 and (b["xmax"] - b["xmin"]) > 40]
    return {
        "source": str(path),
        "size": [w, h],
        "bands": [
            {
                "i": i,
                "y0": b["y0"],
                "y1": b["y1"],
                "cy": (b["y0"] + b["y1"]) // 2,
                "x0": b["xmin"],
                "x1": b["xmax"],
                "w": b["xmax"] - b["xmin"],
                "h": b["y1"] - b["y0"] + 1,
            }
            for i, b in enumerate(bands)
        ],
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    candidates = [
        CAP / "title_content_1080.png",
        CAP / "title_after_input.png",
        CAP / "title_view_1080.png",
        CAP / "title_view.png",
    ]
    for p in candidates:
        if not p.exists():
            print("miss", p.name)
            continue
        m = measure(p)
        print(p.name, "bands", len(m["bands"]))
        for b in m["bands"]:
            print(" ", b)
        (OUT / f"{p.stem}_bands.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
        # crop each band preview
        im = Image.open(p)
        for b in m["bands"][:12]:
            crop = im.crop((b["x0"] - 4, b["y0"] - 2, b["x1"] + 4, b["y1"] + 2))
            crop.save(OUT / f"{p.stem}_band{b['i']:02d}.png")


if __name__ == "__main__":
    main()
