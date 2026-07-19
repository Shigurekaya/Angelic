# -*- coding: utf-8 -*-
"""Bake logo_cn into each title bg so logo cannot be skipped at runtime."""
from pathlib import Path
from PIL import Image

TITLE = Path(r"D:\gamedev\renpy-angelic\game\images\angelic\title")
logo = Image.open(TITLE / "logo_cn.png").convert("RGBA")
for i in range(8):
    bg = Image.open(TITLE / f"bg{i}.png").convert("RGBA")
    out = bg.copy()
    out.alpha_composite(logo)
    out.save(TITLE / f"bg{i}_ui.png")
    print("wrote", f"bg{i}_ui.png", out.size)
# also chrome-only for intro mid layers
logo.save(TITLE / "title_chrome.png")
print("done")
