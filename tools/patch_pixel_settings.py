# -*- coding: utf-8 -*-
"""Patch Angelic data.js for LimeLight-style pixel settings hotspots on option__bg0."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(r"E:\网站\测试框架\Angelic\ui-preview")
raw = (OUT / "data.js").read_text(encoding="utf-8")
data = json.loads(raw[len("window.UI_DATA = ") :].rstrip().rstrip(";"))

# option frame approx (from typical KRKR option shell)
FRAME = {"x": 109, "y": 120, "w": 1701, "h": 839}
SIMPLE = [
    {"key": "fullscreen", "label": "画面尺寸", "type": "toggle", "options": ["窗口", "全屏"], "col": 0, "row": 0},
    {"key": "sqscr", "label": "画面比例", "type": "toggle", "options": ["16:9", "4:3"], "col": 0, "row": 1},
    {"key": "textspeed", "label": "文本速度", "type": "slider", "col": 0, "row": 2},
    {"key": "autospeed", "label": "自动速度", "type": "slider", "col": 0, "row": 3},
    {"key": "skipall", "label": "未读跳过", "type": "toggle", "options": ["仅已读", "全部"], "col": 0, "row": 4},
    {"key": "wave", "label": "主音量", "type": "slider", "col": 1, "row": 0},
    {"key": "bgm", "label": "BGM", "type": "slider", "col": 1, "row": 1},
    {"key": "se", "label": "音效", "type": "slider", "col": 1, "row": 2},
    {"key": "voice", "label": "语音", "type": "slider", "col": 1, "row": 3},
    {"key": "movie", "label": "影片", "type": "slider", "col": 1, "row": 4},
]

fx, fy, fw, fh = FRAME["x"], FRAME["y"], FRAME["w"], FRAME["h"]
pad_x, pad_y, gap_x, gap_y = 20, 28, 16, 8
cell_w = (fw - pad_x * 2 - gap_x) // 2
cell_h = (fh - pad_y * 2 - gap_y * 4) // 5
hits = []
for item in SIMPLE:
    c, r = item["col"], item["row"]
    hits.append(
        {
            **item,
            "x": fx + pad_x + c * (cell_w + gap_x),
            "y": fy + pad_y + r * (cell_h + gap_y),
            "w": cell_w,
            "h": cell_h,
        }
    )

# rebuild tabs: first tab pixel, rest keep rows from previous
old_tabs = data.get("settings", {}).get("tabs") or []
new_tabs = [
    {"id": "0", "label": "基本设置", "mode": "pixel", "hotspots": hits, "pack": None},
]
for t in old_tabs:
    if t.get("id") == "0":
        continue
    new_tabs.append(
        {
            "id": t["id"],
            "label": t["label"],
            "mode": "panel",
            "rows": t.get("rows") or [],
            "pack": t.get("pack"),
        }
    )

data["settings"] = {
    **data.get("settings", {}),
    "style": "pixel-stack",
    "bg": "assets/settings/bg.png",
    "chassis": "assets/settings/option__pack.png",
    "frame": FRAME,
    "pixel_ui_default": True,
    "tabs": new_tabs,
    "sources": [
        "uipsd/option__bg0 + option__pack",
        "option_0simple 2×5 热区",
        "locale/cn/help_opt_cn.txt",
    ],
}
data["layout"] = "angelic-bottom-menu+pixel-settings"

(OUT / "data.js").write_text(
    "window.UI_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
print("Angelic settings pixel hotspots", len(hits), "tabs", len(new_tabs))
