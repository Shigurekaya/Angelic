# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/ui-extract/pixel-reverse/_text_preview/orig_only"
OUT.mkdir(parents=True, exist_ok=True)


def magenta_only(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)
            elif r >= 200 and b >= 200 and g <= 90 and abs(r - b) < 40:
                px[x, y] = (0, 0, 0, 0)
    return im


def main() -> None:
    roots = [
        ROOT / "docs/ui-extract/pixel-reverse/tlg-png",
        ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp",
        ROOT / "docs/ui-extract/pixel-reverse/_pack_slices",
    ]
    for root in roots:
        if not root.exists():
            continue
        print("==", root)
        for p in sorted(root.rglob("*.png")):
            n = p.name.lower()
            if not any(k in n for k in ("title", "lang", "bgsel")):
                continue
            try:
                im = Image.open(p)
                print(f"{im.size[0]:4}x{im.size[1]:4} {p.relative_to(ROOT)}")
            except Exception as e:
                print("ERR", p, e)

    for pack in ("langselect__pack", "title__pack", "title_locale_cn__pack"):
        d = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices" / pack
        for p in sorted(d.glob("s*.png")):
            im = magenta_only(Image.open(p))
            dest = OUT / f"{pack}__{p.name}"
            im.save(dest)
            print("saved", dest.name, im.size)


if __name__ == "__main__":
    main()
