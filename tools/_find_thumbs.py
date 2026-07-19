# -*- coding: utf-8 -*-
"""Find thum_* CG thumbnails in Angelic extracts / game."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"D:/gamedev/Angelic")
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
FULL = ROOT / "docs/ui-extract/full-static"
GAME = Path(r"E:/GAL/天使☆嚣嚣")


def main():
    patterns = ["**/thum_*.jpg", "**/thum_*.png", "**/thum_*.tlg"]
    for root in [FILT, FULL / "evimage", FULL / "image", FULL / "data", GAME / "Extractor_Output"]:
        if not root.exists():
            print("MISS", root)
            continue
        hits = []
        for pat in patterns:
            hits.extend(root.glob(pat))
        print(root, "thum hits", len(hits))
        for h in hits[:5]:
            print(" ", h)


if __name__ == "__main__":
    main()
