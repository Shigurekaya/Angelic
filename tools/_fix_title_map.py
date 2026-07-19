# -*- coding: utf-8 -*-
"""Re-map title buttons from audited crops (manual label verification)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(r"D:/gamedev/Angelic")
AUDIT = ROOT / "docs/ui-extract/pixel-reverse/_text_preview"
PREV = ROOT / "ui-preview/assets/title"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/title"
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"

# Explicit: (key, idle_idx, hover_idx) — indices into title_btn_XX.png
# Verified by reading crops in session.
MAP = [
    ("start", 20, 20),       # only yellow verified; idle use cyan sibling if distinct
    ("continue", 15, 12),
    ("load", 14, 16),
    ("flowchart", 0, 3),
    ("extra", 17, 4),
    ("after", 18, 6),
    ("system", 8, 10),
    ("exit", 2, 1),
]
# Fix start idle: crop 11 was verified 从头开始 cyan
MAP[0] = ("start", 11, 20)

BTN_X, BTN_Y0, BTN_DY = 1560, 380, 58
BTN_W, BTN_H = 130, 44
LOGO_XY = (36, 36)
LOGO_W = 560

ACTIONS = {
    "start": "toast",
    "continue": "toast",
    "load": "load",
    "flowchart": "flowchart",
    "extra": "cg",
    "after": "toast",
    "system": "settings",
    "exit": "quit",
}
LABELS = {
    "start": "从头开始",
    "continue": "继续游戏",
    "load": "载入进度",
    "flowchart": "流程图",
    "extra": "鉴赏模式",
    "after": "追加剧情",
    "system": "系统设定",
    "exit": "退出游戏",
}


def pad(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    # strip residual black bg to alpha for cleaner composite? keep as-is (official has black)
    out = Image.new("RGBA", (BTN_W, BTN_H), (0, 0, 0, 0))
    x = max(0, (BTN_W - im.width) // 2)
    y = max(0, (BTN_H - im.height) // 2)
    out.alpha_composite(im, (x, y))
    return out


def black_to_alpha(im: Image.Image, thr: int = 18) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r <= thr and g <= thr and b <= thr:
                px[x, y] = (0, 0, 0, 0)
    return im


def main():
    btn_dir = PREV / "buttons"
    btn_dir.mkdir(parents=True, exist_ok=True)
    for key, idle_i, hover_i in MAP:
        idle = black_to_alpha(Image.open(AUDIT / f"title_btn_{idle_i:02d}.png"))
        hover = black_to_alpha(Image.open(AUDIT / f"title_btn_{hover_i:02d}.png"))
        pad(idle).save(btn_dir / f"{key}_idle.png")
        pad(hover).save(btn_dir / f"{key}_hover.png")

    for i in range(8):
        src = FILT / f"title_bg{i}.png"
        if src.exists():
            shutil.copy2(src, PREV / f"bg{i}.png")
    logo = FILT / "locale/cn/title_logo_cn.png"
    if logo.exists():
        lim = Image.open(logo).convert("RGBA")
        nh = int(lim.height * LOGO_W / lim.width)
        lim.resize((LOGO_W, nh), Image.Resampling.LANCZOS).save(PREV / "logo_cn.png")

    canvas = Image.open(PREV / "bg0.png").convert("RGBA")
    if (PREV / "logo_cn.png").exists():
        canvas.alpha_composite(Image.open(PREV / "logo_cn.png"), LOGO_XY)
    for i, (key, _, _) in enumerate(MAP):
        canvas.alpha_composite(Image.open(btn_dir / f"{key}_idle.png"), (BTN_X, BTN_Y0 + i * BTN_DY))
    canvas.save(PREV / "composite.png")

    hs = {
        "resolution": [1920, 1080],
        "logo": {"x": LOGO_XY[0], "y": LOGO_XY[1], "w": LOGO_W, "file": "logo_cn.png"},
        "bg_count": 8,
        "buttons": [
            {
                "id": key,
                "label": LABELS[key],
                "action": ACTIONS[key],
                "x": BTN_X,
                "y": BTN_Y0 + i * BTN_DY,
                "w": BTN_W,
                "h": BTN_H,
                "idle": f"buttons/{key}_idle.png",
                "hover": f"buttons/{key}_hover.png",
            }
            for i, (key, _, _) in enumerate(MAP)
        ],
    }
    (PREV / "hotspots.json").write_text(json.dumps(hs, ensure_ascii=False, indent=2), encoding="utf-8")

    if RENPY.exists():
        shutil.rmtree(RENPY)
    shutil.copytree(PREV, RENPY)
    print("ok", [k for k, _, _ in MAP])


if __name__ == "__main__":
    main()
