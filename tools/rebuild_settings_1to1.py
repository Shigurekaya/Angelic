# -*- coding: utf-8 -*-
"""Rebuild Angelic settings plates from static unpack + 原版结构.

Topology: Angelic help_opt / PBD keys（内置 ANGELIC_PAGES）
Geometry: 原版画面设置截图 + settings_truth（箭头/滑轨）；toggle=并排实心/角括号
Chrome:   滑轨/静音/详细=官方整片；开关=解包色剖面实心条+角括号；禁止 s005 当分类标签
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
LAYOUT_DIR = ROOT / "docs/ui-extract/pixel-reverse/settings-layout"
LOCALE_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/uitexts_cn.toml"
HELP_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/help_opt_cn.txt"
CAFE_LAYOUT = Path(r"D:/gamedev/CafeStella/ui-preview/assets/settings/settings-layout.json")  # 仅对照，不再读取
VALUE_PARTS = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices/option__pack_s002_parts"
LAYOUT_OUT = LAYOUT_DIR / "angelic_settings_layout.json"
TRUTH_JSON = LAYOUT_DIR / "settings_truth.json"
PLACEMENTS_JSON = LAYOUT_DIR / "slice_placements.json"
ARROW_PNG = LAYOUT_DIR / "label_arrow_truth.png"
PREV = ROOT / "ui-preview/assets/settings"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/settings"
FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")

# Angelic page id ↔ Cafe topology page id (keys/types only)
PAGE_MAP = [
    ("0", "0_simple", "基本设置"),
    ("1", "1_display", "画面设置"),
    ("2", "2_game1", "游戏设置1"),
    ("3", "3_game2", "游戏设置2"),
    ("4", "4_text", "文本设置"),
    ("5a", "5a_sound1", "音频1"),
    ("5b", "5b_sound2", "音频2"),
    ("6", "6_dialog", "确认信息"),
]
# 不包含鼠标/键盘/手柄（用户明确不要）

# 官方 chrome：滑轨/静音/详细用整片
# 开关真值（原版游戏设置1截图 1920 缩放）：
#   未选=实心蓝条 ~175×44；选中=浅底+四角括号；双钮间距约 20
RAIL_W, RAIL_H = 288, 13
CHIP_OFFICIAL_W, CHIP_OFFICIAL_H = 313, 57
DUAL_W, DUAL_H, DUAL_GAP = 175, 44, 20
QUAD_W, QUAD_H, QUAD_GAP = 90, 44, 14
TRI_W, TRI_H, TRI_GAP = 120, 44, 16
WIDE_CHIP_W, WIDE_CHIP_H = 571, 75
CHIP_W, CHIP_H = DUAL_W, DUAL_H
DETAIL_W, DETAIL_H = 124, 32
MUTE_W, MUTE_H = 76, 54

LEFT_ICON_X, LEFT_LABEL_X, LEFT_CTRL_X = 164, 270, 195
RIGHT_ICON_X, RIGHT_LABEL_X, RIGHT_CTRL_X, RIGHT_RAIL_X = 1515, 1620, 1655, 1655
MUTE_X = 1544
ROW_YS = [237, 483, 728, 880]
CTRL_DY = 75
RAIL_DY = 101
FOOTER_Y = 989
HELP_BOX = {"x": 27, "y": 979, "w": 731, "h": 77}
FOOTER_BTNS = [
    ("init", "恢复默认设置", 923),
    ("title", "标题画面", 1252),
    ("back", "游戏画面", 1581),
]
FOOTER_W, FOOTER_H = 315, 58

SIMPLE_LEFT = ["fullscreen", "sqscr", "textspeed", "autospeed"]
SIMPLE_RIGHT = ["wave", "bgm", "se", "voice"]

# 文本页：这些键存 HSV list，UI 上是「选中后用色盘编辑」而不是 0/1 开关
COLOR_TARGET_KEYS = {
    "color_win",
    "color_owin",
    "color_hwin",
    "color_text",
    "color_read",
}
COLOR_TARGET_LABEL = {
    "color_win": "普通对话框",
    "color_owin": "选项框",
    "color_hwin": "历史对话框",
    "color_text": "未读文字",
    "color_read": "已读文字",
}

# 拓扑：uitexts config_label_* + help_opt keys；游戏设置1对齐原版截图
ANGELIC_PAGES: dict[str, dict[str, list[tuple[str, str]]]] = {
    "0": {
        "left": [("fullscreen", "toggle"), ("sqscr", "toggle"), ("textspeed", "slider"), ("autospeed", "slider")],
        "right": [("wave", "slider"), ("bgm", "slider"), ("se", "slider"), ("voice", "slider")],
    },
    "1": {
        "left": [
            ("fullscreen", "toggle"), ("sqscr", "toggle"), ("noeffect", "toggle"),
            ("scanim", "toggle"), ("esccancel", "toggle"), ("panictype", "choice"),
        ],
        "right": [
            ("stayontop", "toggle"), ("showitems", "choice"), ("chapthidetime", "slider"),
            ("bgmhidetime", "slider"), ("talkface", "toggle"), ("popup", "toggle"),
        ],
    },
    "2": {
        "left": [
            ("readskip", "toggle"), ("readjump", "toggle"), ("curmove", "toggle"),
            ("curmoveyes", "toggle"), ("curhidestep", "choice"), ("filedclk", "toggle"),
        ],
        "right": [
            ("hselfix", "toggle"), ("hfin", "choice"), ("allflow", "toggle"),
            ("deactive", "toggle"), ("preview", "toggle"), ("suspend", "toggle"),
        ],
    },
    "3": {
        "left": [
            ("drawspeed", "slider"), ("voplspeed", "slider"), ("skipspeed", "slider"), ("skipstyle", "choice"),
        ],
        "right": [
            ("rclkmvskip", "toggle"), ("skipmvskip", "toggle"), ("dramatic", "choice"), ("snapshot", "toggle"),
        ],
    },
    "4": {
        "left": [
            ("textspeed", "slider"), ("autospeed", "slider"), ("atextwait", "slider"), ("autovwait", "choice"),
            ("skipall", "toggle"), ("ctrlskip", "toggle"), ("afterskip", "toggle"), ("afterauto", "toggle"),
        ],
        "right": [
            ("winopac", "slider"),
        ],
    },
    "5a": {
        "left": [
            ("wave", "slider"), ("bgm", "slider"), ("movie", "slider"), ("bgv", "slider"), ("bgv2", "slider"),
        ],
        "right": [
            ("bgmdown", "slider"), ("se", "slider"), ("sysse", "slider"),
            ("voice", "slider"), ("voicecut", "toggle"), ("voeffect", "toggle"),
        ],
    },
    "5b": {
        "left": [
            ("sysvo", "slider"), ("bgv", "slider"), ("sysse_en", "toggle"), ("sysvo_en", "toggle"),
        ],
        "right": [],
    },
    "6": {
        "left": [
            ("cfall", "toggle"), ("cf_save", "toggle"), ("cf_overwrite", "toggle"), ("cf_load", "toggle"),
        ],
        "right": [
            ("cf_qsave", "toggle"), ("cf_qload", "toggle"), ("cf_title", "toggle"), ("cf_exit", "toggle"),
        ],
    },
}

PAGE_PACKS = {
    "4": "option_4text__pack",
    "5a": "option_5sound1__pack",
    "5b": "option_5sound2__pack",
    "6": "option_6dialog__pack",
}
PAGE_PACK_PLACEMENTS = {
    "4": [(0, 1030, 543), (1, 1031, 775)],
    "5a": [(3, 1100, 420)],
    "5b": [(0, 1100, 200)],
    "6": [(0, 1680, 220)],
}


def load_truth() -> dict:
    if not TRUTH_JSON.exists():
        return {}
    return json.loads(TRUTH_JSON.read_text(encoding="utf-8"))


def apply_truth(truth: dict) -> None:
    """几何：完整采用 settings_truth 官方裸像素（ig_option_*_1080）。"""
    global LEFT_ICON_X, LEFT_LABEL_X, LEFT_CTRL_X
    global RIGHT_ICON_X, RIGHT_LABEL_X, RIGHT_CTRL_X, RIGHT_RAIL_X, MUTE_X
    global ROW_YS, CTRL_DY, RAIL_DY, FOOTER_Y, FOOTER_BTNS
    global WIDE_CHIP_W, WIDE_CHIP_H, RAIL_W, RAIL_H
    g = truth.get("grid") or {}
    p0 = truth.get("page0") or {}
    src = {**p0, **g}

    def _i(key: str, default: int | None = None) -> int | None:
        v = src.get(key)
        return int(v) if isinstance(v, (int, float)) else default

    LEFT_ICON_X = _i("left_icon_x", LEFT_ICON_X) or LEFT_ICON_X
    LEFT_LABEL_X = _i("left_label_x", LEFT_LABEL_X) or LEFT_LABEL_X
    LEFT_CTRL_X = _i("left_ctrl_x", LEFT_CTRL_X) or LEFT_CTRL_X
    RIGHT_ICON_X = _i("right_icon_x", RIGHT_ICON_X) or RIGHT_ICON_X
    RIGHT_LABEL_X = _i("right_label_x", RIGHT_LABEL_X) or RIGHT_LABEL_X
    RIGHT_RAIL_X = _i("right_rail_x", RIGHT_RAIL_X) or RIGHT_RAIL_X
    MUTE_X = _i("mute_x", MUTE_X) or MUTE_X
    FOOTER_Y = _i("footer_y", FOOTER_Y) or FOOTER_Y
    if isinstance(src.get("row_ys"), list) and src["row_ys"]:
        ROW_YS = [int(y) for y in src["row_ys"]]
    elif isinstance(p0.get("row_label_ys"), list) and p0["row_label_ys"]:
        ROW_YS = [int(y) for y in p0["row_label_ys"]]
    CTRL_DY = _i("ctrl_dy", CTRL_DY) or CTRL_DY
    RAIL_DY = _i("rail_dy", RAIL_DY) or RAIL_DY
    WIDE_CHIP_W = _i("wide_chip_w", WIDE_CHIP_W) or WIDE_CHIP_W
    WIDE_CHIP_H = _i("wide_chip_h", WIDE_CHIP_H) or WIDE_CHIP_H
    wc = p0.get("wide_chip") or {}
    if isinstance(wc.get("w"), (int, float)):
        WIDE_CHIP_W = int(wc["w"])
    if isinstance(wc.get("h"), (int, float)):
        WIDE_CHIP_H = int(wc["h"])
    if isinstance(wc.get("dy"), (int, float)):
        CTRL_DY = int(wc["dy"])
    rail = p0.get("rail") or {}
    if isinstance(rail.get("w"), (int, float)):
        RAIL_W = int(rail["w"])
    if isinstance(rail.get("h"), (int, float)):
        RAIL_H = int(rail["h"])
    if isinstance(rail.get("dy"), (int, float)):
        RAIL_DY = int(rail["dy"])
    # 底栏 x：官方抓图 footer_xs
    fxs = p0.get("footer_xs")
    if isinstance(fxs, list) and len(fxs) >= 3:
        FOOTER_BTNS = [
            ("init", "恢复默认设置", int(fxs[0])),
            ("title", "标题画面", int(fxs[1])),
            ("back", "游戏画面", int(fxs[2])),
        ]


def load_page_placements() -> dict[str, list[tuple[int, int, int]]]:
    """tid -> [(slice_i, x, y), ...] from slice_placements.json."""
    out: dict[str, list[tuple[int, int, int]]] = {}
    if not PLACEMENTS_JSON.exists():
        return {k: list(v) for k, v in PAGE_PACK_PLACEMENTS.items()}
    doc = json.loads(PLACEMENTS_JSON.read_text(encoding="utf-8"))
    for tid, pg in (doc.get("pages") or {}).items():
        placed = []
        for s in pg.get("slices") or []:
            if s.get("ok") and "x" in s and "y" in s:
                # 装饰大图放右栏；过宽片跳过以免盖住控件
                if int(s.get("w") or 0) > 700:
                    continue
                placed.append((int(s["i"]), int(s["x"]), int(s["y"])))
        out[tid] = placed or list(PAGE_PACK_PLACEMENTS.get(tid) or [])
    for tid, fb in PAGE_PACK_PLACEMENTS.items():
        out.setdefault(tid, list(fb))
    return out

LABEL_CN = {
    "fullscreen": "显示模式",
    "sqscr": "画面比例",
    "textspeed": "文本显示速度",
    "autospeed": "自动模式速度",
    "skipall": "快进未读文本",
    "wave": "总音量",
    "bgm": "ＢＧＭ",
    "se": "ＳＥ（游戏音效）",
    "voice": "语音（游戏中）",
    "movie": "视频",
    "noeffect": "画面效果",
    "scanim": "动画效果",
    "esccancel": "ESC键功能",
    "panictype": "老板键功能",
    "stayontop": "保持游戏窗口最前方",
    "showitems": "功能区域开关",
    "talkface": "显示说话人物表情",
    "popup": "显示弹出内容",
    "chapthidetime": "显示章节标题",
    "bgmhidetime": "显示BGM标题",
    "facemode": "立绘模式",
    "qcpopover": "弹出菜单",
    "readskip": "自动跳过已读文本",
    "readjump": "已读文本自动跳过方式",
    "curmove": "鼠标光标自动移动",
    "curmoveyes": "鼠标光标自动移动指向的按钮",
    "curhidestep": "鼠标光标自动隐藏",
    "filedclk": "存档/加载时鼠标操作",
    "hselfix": "Ｈ场景选项固定",
    "hfin": "Ｈ场景选项",
    "allflow": "流程图中显示未读内容",
    "deactive": "非活动窗口时游戏状态",
    "suspend": "待机功能",
    "preview": "任务栏窗口预览",
    "drawspeed": "游戏进行速度",
    "voplspeed": "语音播放速度",
    "skipspeed": "快进速度调整",
    "skipstyle": "快进方式",
    "dramatic": "显示文本窗口（沉浸式体验）",
    "snapshot": "截图保存设置",
    "rclkmvskip": "右键跳过视频",
    "skipmvskip": "快进时跳过视频",
    "atextwait": "每个文字的等待时间",
    "autosty": "自动模式类型",
    "autovwait": "自动模式类型",
    "ctrlskip": "Ctrl快进",
    "afterskip": "选项后快进模式",
    "afterauto": "选项后自动模式",
    "keep_skip": "选项后快进模式",
    "keep_auto": "选项后自动模式",
    "winopac": "对话框透明度",
    "movie": "视频",
    "bgv2": "ＢＧＶ（Ｈ场景）",
    "chvall": "语音单独设定",
    "chv": "角色语音音量",
    "fontselect": "字体选择",
    "hsv_reset": "重置",
    "nohwindow": "Ｈ场景禁用对话框",
    "bgmdown": "ＢＧＭ（角色语音）",
    "voicecut": "语音中断",
    "voeffect": "语音效果",
    "sysse": "ＳＥ（系统音效）",
    "sysvo": "系统语音",
    "bgv": "ＢＧＶ（通常场景）",
    "bgv2": "ＢＧＶ（Ｈ场景）",
    "sysse_en": "系统音效开关",
    "sysvo_en": "系统语音开关",
    "sysvoall": "系统语音总开关",
    "cfall": "全部确认开关",
    "cf_save": "存档时确认",
    "cf_overwrite": "覆盖存档时确认",
    "cf_load": "读档时确认",
    "cf_qsave": "快速存档时确认",
    "cf_qload": "快速读档时确认",
    "cf_title": "返回标题时确认",
    "cf_exit": "退出游戏时确认",
    "cf_init": "恢复默认时确认",
}

OPTS_CN = {
    "fullscreen": ["窗口模式", "全屏模式"],
    "sqscr": ["１６：９", "４：３"],
    "skipall": ["已读内容", "全部内容"],
    "noeffect": ["开启", "关闭"],
    "scanim": ["开启", "关闭"],
    "esccancel": ["鼠标右键", "老板键"],
    "panictype": ["最小化", "图像１", "图像２", "自定义"],
    "stayontop": ["开启", "关闭"],
    "showitems": ["状态图标", "进度条", "窗口菜单", "触控按钮"],
    "talkface": ["开启", "关闭"],
    "popup": ["鼠标经过", "鼠标右键"],
    "readskip": ["开启", "关闭"],
    "readjump": ["快进", "跳转"],
    "curmove": ["开启", "关闭"],
    "curmoveyes": ["是", "否"],
    "curhidestep": ["无", "５秒", "１０秒", "２０秒"],
    "filedclk": ["双击", "单击"],
    "hselfix": ["开启", "关闭"],
    "hfin": ["中出", "外射", "口射", "颜射"],
    "allflow": ["开启", "关闭"],
    "deactive": ["停止", "继续"],
    "suspend": ["开启", "关闭"],
    "preview": ["开启", "关闭"],
    "skipstyle": ["普通", "快速", "纯文字"],
    "dramatic": ["始终显示", "仅在自动时隐藏", "总是隐藏"],
    "snapshot": ["以日期为文件名", "每次设置文件名"],
    "rclkmvskip": ["开启", "关闭"],
    "skipmvskip": ["开启", "关闭"],
    "autosty": ["普通", "语音优先", "快速"],
    "autovwait": ["普通", "语音优先", "快速"],
    "skipall": ["已读内容", "全部内容"],
    "ctrlskip": ["已读内容", "全部内容"],
    "keep_skip": ["继续", "解除"],
    "keep_auto": ["继续", "解除"],
    "afterskip": ["继续", "解除"],
    "afterauto": ["继续", "解除"],
    "voicecut": ["开启", "关闭"],
    "voeffect": ["开启", "关闭"],
    "sysse_en": ["开启", "关闭"],
    "sysvo_en": ["开启", "关闭"],
    "cfall": ["开启", "关闭"],
    "cf_save": ["开启", "关闭"],
    "cf_overwrite": ["开启", "关闭"],
    "cf_load": ["开启", "关闭"],
    "cf_qsave": ["开启", "关闭"],
    "cf_qload": ["开启", "关闭"],
    "cf_title": ["开启", "关闭"],
    "cf_exit": ["开启", "关闭"],
    "cf_init": ["开启", "关闭"],
}

MUTE_KEYS = {"wave", "bgm", "se", "voice", "movie", "sysse", "sysvo", "bgv", "bgv2", "bgmdown", "down"}


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def magenta_to_alpha(im: Image.Image) -> Image.Image:
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


def load_font(size: int) -> ImageFont.ImageFont:
    if FONT_PATH.exists():
        try:
            return ImageFont.truetype(str(FONT_PATH), size=size, index=0)
        except Exception:
            pass
    return ImageFont.load_default()


def _solid_chip_fallback(on: bool) -> Image.Image:
    base = Image.new("RGBA", (380, 50), (0, 0, 0, 0))
    dr = ImageDraw.Draw(base)
    if on:
        dr.rounded_rectangle((0, 0, 379, 49), radius=4, fill=(186, 223, 255, 255), outline=(50, 130, 220, 255), width=2)
    else:
        dr.rounded_rectangle((0, 0, 379, 49), radius=4, fill=(18, 118, 227, 255), outline=(24, 94, 180, 255), width=2)
    return base


def load_slice(pack: str, index: int) -> Image.Image | None:
    d = SLICES / pack
    sj = d / "slices.json"
    if not sj.exists():
        return None
    data = json.loads(sj.read_text(encoding="utf-8"))
    for item in data:
        if int(item["i"]) == index:
            p = d / item["file"]
            if p.exists():
                return magenta_to_alpha(Image.open(p).convert("RGBA"))
    return None


def chrome_value_on() -> Image.Image | None:
    p = VALUE_PARTS / "value_on_571x75.png"
    if p.exists():
        return Image.open(p).convert("RGBA")
    return None


def chrome_value_off() -> Image.Image | None:
    p = VALUE_PARTS / "value_off_571x75.png"
    if p.exists():
        return Image.open(p).convert("RGBA")
    return None


def paste(canvas: Image.Image, spr: Image.Image | None, x: int, y: int) -> None:
    if spr is None:
        return
    x, y = int(x), int(y)
    if x >= canvas.width or y >= canvas.height or x + spr.width <= 0 or y + spr.height <= 0:
        return
    if x < 0 or y < 0:
        cx, cy = max(0, x), max(0, y)
        sx, sy = cx - x, cy - y
        spr = spr.crop((sx, sy, spr.width, spr.height))
        x, y = cx, cy
    if x + spr.width > canvas.width or y + spr.height > canvas.height:
        spr = spr.crop((0, 0, min(spr.width, canvas.width - x), min(spr.height, canvas.height - y)))
    canvas.alpha_composite(spr, (x, y))


def save_official(dst: Path, pack: str, index: int) -> Image.Image | None:
    """复制官方整片切片（禁止二次裁切/手绘）。"""
    spr = load_slice(pack, index)
    if spr is None:
        return None
    ensure(dst.parent)
    spr.save(dst)
    return spr


def paste_page_pack_slices(canvas: Image.Image, pack: str, ox: int, oy: int) -> None:
    """兼容旧调用：无定点表时退回流式。"""
    d = SLICES / pack
    if not d.is_dir():
        return
    files = sorted(d.glob("s*.png"), key=lambda p: p.name)
    x, y = ox, oy
    row_h = 0
    max_right = 1880
    for f in files:
        im = magenta_to_alpha(Image.open(f).convert("RGBA"))
        if x > ox and x + im.width > max_right:
            x = ox
            y += row_h + 10
            row_h = 0
        paste(canvas, im, x, y)
        x += im.width + 10
        row_h = max(row_h, im.height)


def paste_page_pack_placed(
    canvas: Image.Image,
    tid: str,
    placements: dict[str, list[tuple[int, int, int]]] | None = None,
) -> None:
    """仅摆放人工校对过的分页装饰片；禁止 matchTemplate 噪声堆叠。"""
    pack = PAGE_PACKS.get(tid)
    # 硬编码表优先；slice_placements 的 cv 匹配曾把 atlas 堆到画面中央
    places = list(PAGE_PACK_PLACEMENTS.get(tid) or [])
    if not pack or not places:
        return
    for idx, x, y in places:
        spr = load_slice(pack, idx)
        if spr is None:
            continue
        px = min(int(x), 1920 - spr.width - 8)
        py = min(int(y), 1080 - spr.height - 8)
        paste(canvas, spr, px, py)


def paste_rail(canvas: Image.Image, track_src: Image.Image | None, tx: int, ty: int, tw: int, th: int) -> None:
    """官方滑轨片（常为 288×13）按 PBD 槽宽拉伸到目标宽度。"""
    if track_src is None or tw <= 0 or th <= 0:
        return
    spr = track_src
    if spr.size != (tw, max(1, min(th, spr.height) if th < 20 else spr.height)):
        # 横向拉伸到 PBD 宽；高度保持官方片（通常 13）
        nh = spr.height
        if th >= 20:
            # PBD 槽含热区 padding：视觉条垂直居中
            pass
        spr = spr.resize((tw, nh), Image.Resampling.LANCZOS)
        paste(canvas, spr, tx, ty + max(0, (th - nh) // 2))
    else:
        paste(canvas, spr, tx, ty)


def load_pack_atlas(pack: str) -> Image.Image | None:
    """分页 pack 官方整图（仅作备用）。"""
    p = TLG / f"{pack}.png"
    if p.exists():
        return magenta_to_alpha(Image.open(p).convert("RGBA"))
    return None


def parse_uitexts() -> dict[str, str]:
    out: dict[str, str] = {}
    if not LOCALE_CN.exists():
        return out
    for line in LOCALE_CN.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r'^([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$', line.strip())
        if not m:
            m = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def _read_text_auto(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    for enc in ("utf-8", "utf-16", "cp932"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def parse_help() -> dict[str, str]:
    if not HELP_CN.exists():
        return {}
    text = _read_text_auto(HELP_CN)
    out: dict[str, str] = {}
    cur_keys: list[str] = []
    buf: list[str] = []
    for line in text.splitlines():
        raw = line.rstrip()
        if not raw or raw.startswith("#"):
            if cur_keys and buf:
                msg = "\n".join(x.strip() for x in buf if x.strip())
                for k in cur_keys:
                    out[k] = msg
                cur_keys, buf = [], []
            continue
        if re.match(r"^[a-zA-Z_][\w\t ]*$", raw) and not raw.startswith("\t"):
            if cur_keys and buf:
                msg = "\n".join(x.strip() for x in buf if x.strip())
                for k in cur_keys:
                    out[k] = msg
            cur_keys = [k.strip() for k in re.split(r"[\t ]+", raw) if k.strip()]
            buf = []
        else:
            buf.append(raw.lstrip("\t"))
    if cur_keys and buf:
        msg = "\n".join(x.strip() for x in buf if x.strip())
        for k in cur_keys:
            out[k] = msg
    return out


def load_angelic_pages() -> dict[str, dict]:
    """Angelic help_opt / PBD 拓扑 → {tid: {rows:[{key,type}]}}。"""
    out: dict[str, dict] = {}
    for tid, cols in ANGELIC_PAGES.items():
        rows = []
        for key, typ in (cols.get("left") or []) + (cols.get("right") or []):
            rows.append({"key": key, "type": typ, "x": 0 if typ else 0})
        # mark column by reconstructing from lists
        left_keys = {k for k, _ in (cols.get("left") or [])}
        for r in rows:
            r["x"] = 100 if r["key"] in left_keys else 1000
        out[tid] = {"id": tid, "rows": rows}
    return out


def row_label(row: dict) -> str:
    key = row.get("key") or ""
    return LABEL_CN.get(key) or row.get("label") or key


def row_options(row: dict) -> list[str] | None:
    key = row.get("key") or ""
    if key in OPTS_CN:
        return list(OPTS_CN[key])
    opts = row.get("options")
    return list(opts) if opts else None


def _chip_geom(n: int) -> tuple[int, int, int]:
    if n >= 4:
        return QUAD_W, QUAD_H, QUAD_GAP
    if n == 3:
        return TRI_W, TRI_H, TRI_GAP
    return DUAL_W, DUAL_H, DUAL_GAP


def _row_ys_for(n: int) -> list[int]:
    if n <= 0:
        return list(ROW_YS[:1])
    if n <= len(ROW_YS):
        # 均匀取 n 行，优先用画面页 6 行真值
        if n == len(ROW_YS):
            return list(ROW_YS)
        if n == 4:
            return [ROW_YS[0], ROW_YS[1], ROW_YS[2], ROW_YS[3]]
        idxs = [int(round(i * (len(ROW_YS) - 1) / max(1, n - 1))) for i in range(n)]
        return [ROW_YS[j] for j in idxs]
    y0, y1 = ROW_YS[0], min(ROW_YS[-1], FOOTER_Y - 90)
    return [y0 + int(i * (y1 - y0) / max(1, n - 1)) for i in range(n)]


def rematerialize_rows(page: dict, tid: str) -> list[dict]:
    """Angelic keys/types + 原版并排开关几何（非宽值条循环）。"""
    cols = ANGELIC_PAGES.get(tid) or {"left": [], "right": []}
    out: list[dict] = []

    def make_item(key: str, typ: str, icon_x: int, label_x: int, ctrl_x: int, ly: int, opts: list[str] | None) -> dict:
        label = LABEL_CN.get(key) or key
        item = {
            "slot": key,
            "key": key,
            "label": label,
            "type": typ,
            "icon_x": icon_x,
            "x": label_x,
            "y": ly,
            "w": 280,
            "h": 48,
        }
        if typ == "slider":
            rail_x = RIGHT_RAIL_X if ctrl_x >= 1400 else ctrl_x
            if tid != "0" and icon_x >= 900:
                rail_x = max(ctrl_x, 1180)
            ry = min(ly + RAIL_DY, FOOTER_Y - 40)
            item["ctrl"] = {"x": rail_x, "y": ry, "w": RAIL_W, "h": RAIL_H, "slot": key}
            item["track"] = {"x": rail_x, "y": ry, "w": RAIL_W, "h": RAIL_H}
            if key in MUTE_KEYS:
                item["mute"] = True
                item["mute_pos"] = {
                    "x": MUTE_X if rail_x >= 1500 else max(icon_x, rail_x - 100),
                    "y": max(120, ry - (MUTE_H - RAIL_H) // 2),
                    "w": MUTE_W,
                    "h": MUTE_H,
                }
        else:
            opts = opts or ["开启", "关闭"]
            # 简易页：官方为宽值条循环（settings_truth wide_chip），非并排双钮
            if tid == "0" and typ == "toggle":
                cy = ly + CTRL_DY
                item["ctrl"] = {
                    "x": ctrl_x,
                    "y": cy,
                    "w": WIDE_CHIP_W,
                    "h": WIDE_CHIP_H,
                    "slot": key,
                }
                item["chip_w"] = WIDE_CHIP_W
                item["chip_h"] = WIDE_CHIP_H
                item["chip_gap"] = 0
                item["chip_n"] = 1
                item["options"] = opts
                item["chips"] = [
                    {"x": ctrl_x, "y": cy, "w": WIDE_CHIP_W, "h": WIDE_CHIP_H, "i": 0}
                ]
                item["type"] = "wide_value"
                item["w"] = WIDE_CHIP_W
                item["h"] = WIDE_CHIP_H
            else:
                n = max(2, len(opts))
                cw, ch, gap = _chip_geom(n)
                cy = ly + CTRL_DY
                total_w = n * cw + (n - 1) * gap
                item["ctrl"] = {"x": ctrl_x, "y": cy, "w": total_w, "h": ch, "slot": key}
                item["chip_w"] = cw
                item["chip_h"] = ch
                item["chip_gap"] = gap
                item["chip_n"] = n
                item["options"] = opts
                item["chips"] = [
                    {"x": ctrl_x + i * (cw + gap), "y": cy, "w": cw, "h": ch, "i": i} for i in range(n)
                ]
                item["type"] = "choice" if n > 2 else "toggle"
        return item

    left = list(cols.get("left") or [])
    right = list(cols.get("right") or [])
    ys = _row_ys_for(max(len(left), len(right), 1))

    for i, (key, typ) in enumerate(left):
        ly = ys[i] if i < len(ys) else ys[-1]
        opts = list(OPTS_CN[key]) if key in OPTS_CN and typ != "slider" else None
        ctrl_x = LEFT_CTRL_X if typ != "slider" else LEFT_CTRL_X + 110
        out.append(make_item(key, typ, LEFT_ICON_X, LEFT_LABEL_X, ctrl_x, ly, opts))
    for i, (key, typ) in enumerate(right):
        ly = ys[i] if i < len(ys) else ys[-1]
        opts = list(OPTS_CN[key]) if key in OPTS_CN and typ != "slider" else None
        if typ == "slider":
            # 画面页右栏滑条在控件列；简易页音量仍用右轨
            rail = RIGHT_RAIL_X if tid == "0" else max(RIGHT_CTRL_X, 1180)
            icon = RIGHT_ICON_X if tid != "0" else 1515
            lab = RIGHT_LABEL_X if tid != "0" else 1620
            out.append(make_item(key, typ, icon, lab, rail, ly, None))
        else:
            out.append(make_item(key, typ, RIGHT_ICON_X, RIGHT_LABEL_X, RIGHT_CTRL_X, ly, opts))
    _ = page
    return out


def build_native_layout(_pages: dict[str, dict] | None = None) -> dict:
    tabs = []
    for tid, cafe_id, label in PAGE_MAP:
        rows = rematerialize_rows({}, tid)
        tabs.append({"id": tid, "cafe_id": cafe_id, "label": label, "rows": rows})
    doc = {
        "source": "official bare pixels: settings_truth(ig_option) + slice_placements + help_opt topology",
        "chrome": {
            "label_arrow": {"file": "label_arrow_truth.png"},
            "value_on": {"file": "option__pack_s002_parts/value_on_571x75.png", "from": "option__pack/s002 blue profile"},
            "rail": {"w": RAIL_W, "h": RAIL_H, "slice": "option__pack/s014"},
            "chip": {"w": CHIP_OFFICIAL_W, "h": CHIP_OFFICIAL_H, "slice": "option__pack/s005", "note": "small toggles only"},
            "wide_slot": {"w": WIDE_CHIP_W, "h": WIDE_CHIP_H},
            "detail": {"w": DETAIL_W, "h": DETAIL_H, "slice": "option__pack/s011"},
            "mute": {"w": MUTE_W, "h": MUTE_H, "slice": "option__pack/s010"},
            "knob": {"slice": "option__pack/s018"},
            "footer": {"slice": "option_cmds__pack/s000"},
        },
        "grid": {
            "left_icon_x": LEFT_ICON_X,
            "left_label_x": LEFT_LABEL_X,
            "left_ctrl_x": LEFT_CTRL_X,
            "right_icon_x": RIGHT_ICON_X,
            "right_label_x": RIGHT_LABEL_X,
            "right_rail_x": RIGHT_RAIL_X,
            "mute_x": MUTE_X,
            "row_ys": ROW_YS,
            "ctrl_dy": CTRL_DY,
            "rail_dy": RAIL_DY,
        },
        "tabs": tabs,
        "footer": [
            {"id": fid, "label": lab, "x": fx, "y": FOOTER_Y, "w": FOOTER_W, "h": FOOTER_H}
            for fid, lab, fx in FOOTER_BTNS
        ],
        "help_box": HELP_BOX,
        "exclude_pages": ["7", "9"],
    }
    LAYOUT_OUT.parent.mkdir(parents=True, exist_ok=True)
    LAYOUT_OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return doc


def bake_plate(
    tid: str,
    page: dict,
    tab_index: int,
    tab_items: list[dict],
    fonts: dict,
    placements: dict[str, list[tuple[int, int, int]]] | None = None,
) -> tuple[Image.Image, list[dict]]:
    bg = Image.open(TLG / "option__bg0.png").convert("RGBA")
    canvas = bg.copy()
    track_src = load_slice("option__pack", 14)
    hdr_system = load_slice("option__pack", 12)
    hdr_setting = load_slice("option__pack", 13)
    side = load_slice("option__pack", 0)
    sep = load_slice("option__pack", 1)
    arrow = Image.open(ARROW_PNG).convert("RGBA") if ARROW_PNG.exists() else None

    # option__bg0 已含顶栏翼标；禁止再贴 s018 滑块当 logo
    if side:
        paste(canvas, side, 58, 161)
    # 官方 caption @ (87,19) 295×43 ≈ SYSTEM + SETTING 两片并排
    if hdr_system:
        paste(canvas, hdr_system, 87, 22)
    if hdr_setting:
        paste(canvas, hdr_setting, 87 + (hdr_system.width if hdr_system else 138) + 8, 22)
    # 分隔线 sep_a / sep_b
    if sep is not None:
        paste(canvas, sep, 89, 125)
        paste(canvas, sep, 988, 125)

    _ = tab_index
    _ = tab_items

    slots: list[dict] = []
    for row in page.get("rows") or []:
        key = row.get("key") or ""
        typ = row.get("type") or "toggle"
        ly = int(row["y"])
        label = row.get("label") or row_label(row)
        opts = row.get("options") or row_options(row)
        icon_x = int(row.get("icon_x") or LEFT_ICON_X)
        label_x = int(row["x"])

        # 分类箭头胶囊由运行时 detail 热区绘制（label_*_jump），烤板不重复贴
        dr = ImageDraw.Draw(canvas)
        bb = dr.textbbox((0, 0), label, font=fonts["label"])
        th = bb[3] - bb[1]
        ty = ly + max(4, (48 - th) // 2 - 1)
        dr.text((label_x + 1, ty + 1), label, font=fonts["label"], fill=(20, 40, 90, 100))
        dr.text((label_x, ty), label, font=fonts["label"], fill=(20, 50, 120, 255))

        ctrl = row.get("ctrl") or {}
        track = row.get("track") or {}
        item: dict = {
            "key": key,
            "label": label,
            "type": typ,
            "help_key": key,
            "x": int(ctrl.get("x") or LEFT_CTRL_X),
            "y": int(ctrl.get("y") or (ly + CTRL_DY)),
            "w": int(ctrl.get("w") or WIDE_CHIP_W),
            "h": int(ctrl.get("h") or WIDE_CHIP_H),
            "default": 0.55 if typ == "slider" else 0,
        }
        if opts:
            item["options"] = opts

        # HSV 色目标：禁止当成 toggle chips（values[key] 是 list，会 TypeError）
        if key in COLOR_TARGET_KEYS:
            item["type"] = "color_target"
            item["label"] = COLOR_TARGET_LABEL.get(key, label)
            item["options"] = [COLOR_TARGET_LABEL.get(key, label)]
            item.pop("chips", None)
            slots.append(item)
            continue

        if typ == "slider" or track:
            tr = track or {"x": item["x"], "y": item["y"], "w": RAIL_W, "h": RAIL_H}
            tx, ty_r = int(tr["x"]), int(tr["y"])
            tw = int(tr.get("w") or RAIL_W)
            thh = int(tr.get("h") or RAIL_H)
            paste_rail(canvas, track_src, tx, ty_r, tw, thh)
            item["type"] = "slider"
            item["track"] = {"x": tx, "y": ty_r, "w": tw, "h": thh}
            item["num"] = {"x": tx + tw + 10, "y": ty_r - 6, "w": 56, "h": 24}
            item["x"], item["y"], item["w"], item["h"] = tx, ty_r, tw, thh
            if row.get("mute") or key in MUTE_KEYS:
                item["mute"] = True
                item["mute_pos"] = row.get("mute_pos") or {
                    "x": MUTE_X,
                    "y": ty_r - (MUTE_H - thh) // 2,
                    "w": MUTE_W,
                    "h": MUTE_H,
                }
        else:
            opts = opts or item.get("options") or ["开启", "关闭"]
            chips = row.get("chips")
            if not chips:
                n = max(2, len(opts))
                cw, ch, gap = _chip_geom(n)
                chips = [
                    {"x": int(item["x"]) + i * (cw + gap), "y": int(item["y"]), "w": cw, "h": ch, "i": i}
                    for i in range(n)
                ]
            item["options"] = opts
            item["chips"] = chips
            item["chip_n"] = len(chips)
            item["chip_w"] = int(chips[0]["w"])
            item["chip_h"] = int(chips[0]["h"])
            item["w"] = int(chips[-1]["x"] + chips[-1]["w"] - chips[0]["x"])
            item["h"] = int(chips[0]["h"])
            if typ == "wide_value" or (len(chips) == 1 and int(chips[0]["w"]) >= 400):
                item["type"] = "wide_value"
            else:
                item["type"] = "choice" if len(chips) > 2 else "toggle"
            # 不在烤板上叠开关壳——运行时按选中态画实心/角括号，避免「框中框」与白底

        if tid == "0" and typ in ("toggle", "slider", "choice"):
            # 详细按钮：PBD label_*_jump 约在标签行右侧
            item["detail"] = row.get("detail") or {
                "x": int(label_x) + 480 - DETAIL_W,
                "y": ly,
                "w": DETAIL_W,
                "h": DETAIL_H,
            }
        slots.append(item)

    paste_page_pack_placed(canvas, tid, placements)

    footer_spr = load_slice("option_cmds__pack", 0)
    for fid, lab, fx in FOOTER_BTNS:
        if footer_spr is not None:
            paste(canvas, footer_spr, fx, FOOTER_Y)
        dr = ImageDraw.Draw(canvas)
        bb = dr.textbbox((0, 0), lab, font=fonts["label"])
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        fw = footer_spr.width if footer_spr is not None else FOOTER_W
        fh = footer_spr.height if footer_spr is not None else FOOTER_H
        dr.text(
            (fx + (fw - tw) // 2, FOOTER_Y + (fh - th) // 2 - 1),
            lab,
            font=fonts["label"],
            fill=(245, 250, 255, 255),
        )
    return canvas, slots


def export_chrome(chrome: Path, tabs_dir: Path, tab_items: list[dict], fonts: dict) -> None:
    """只导出官方整片别名；禁止 make_chip / 二次裁切 / 硬缩放。"""
    ensure(chrome)
    ensure(tabs_dir)
    official = ensure(chrome / "official")

    # 清掉历史合成残留
    for junk in ("detail_cn.png", "slider_num.png"):
        p = chrome / junk
        if p.exists():
            p.unlink()

    # 全量归档 option__pack 官方切片
    for i in range(19):
        spr = load_slice("option__pack", i)
        if spr:
            spr.save(official / f"option__pack_s{i:03d}.png")

    # checkbox 官方整片
    save_official(chrome / "check_off.png", "option__pack", 6)
    save_official(chrome / "check_on.png", "option__pack", 4)
    save_official(chrome / "check_off_over.png", "option__pack", 8)
    save_official(chrome / "check_on_over.png", "option__pack", 7)
    for a, b in (
        ("check_off.png", "check_off_over.png"),
        ("check_on.png", "check_on_over.png"),
    ):
        if (chrome / a).exists() and not (chrome / b).exists():
            shutil.copy2(chrome / a, chrome / b)

    # 开关壳（原版真值）：
    #   chip_*_on  = 选中 = 浅底 + 角括号
    #   chip_*_off = 未选 = 实心蓝条
    def _copy_chip(src_sel: Path | None, src_idle: Path | None, dst_prefix: str) -> bool:
        ok = False
        if src_sel is not None and src_sel.exists():
            shutil.copy2(src_sel, chrome / f"{dst_prefix}_on.png")
            shutil.copy2(src_sel, chrome / f"{dst_prefix}_over.png")
            ok = True
        if src_idle is not None and src_idle.exists():
            shutil.copy2(src_idle, chrome / f"{dst_prefix}_off.png")
            ok = True
        return ok

    chip_dual_ok = _copy_chip(VALUE_PARTS / "chip_selected_dual.png", VALUE_PARTS / "chip_idle_dual.png", "chip")
    _copy_chip(VALUE_PARTS / "chip_selected_tri.png", VALUE_PARTS / "chip_idle_tri.png", "chip3")
    _copy_chip(VALUE_PARTS / "chip_selected_quad.png", VALUE_PARTS / "chip_idle_quad.png", "chip4")
    if not chip_dual_ok:
        # 回退：旧 dual 文件名 / 近似命名
        chip_dual_ok = _copy_chip(
            VALUE_PARTS / "chip_selected_brackets_175x44.png",
            VALUE_PARTS / "chip_idle_solid_175x44.png",
            "chip",
        )
    if not chip_dual_ok:
        # 最后回退：直接生成结构化临时壳，保证重建链路不中断。
        _solid_chip_fallback(True).save(chrome / "chip_on.png")
        _solid_chip_fallback(True).save(chrome / "chip_over.png")
        _solid_chip_fallback(False).save(chrome / "chip_off.png")
        chip_dual_ok = True

    # 简易页双钮官方命中 380×50：优先由 dual 片拉伸导出；没有 dual 就直接复用临时壳
    for src_name, dst_name in (
        ("chip_idle_dual.png", "chip_off_380.png"),
        ("chip_selected_dual.png", "chip_on_380.png"),
    ):
        src = VALUE_PARTS / src_name
        if src.exists():
            Image.open(src).convert("RGBA").resize((380, 50), Image.Resampling.LANCZOS).save(chrome / dst_name)
    if not (chrome / "chip_off_380.png").exists() and (chrome / "chip_off.png").exists():
        shutil.copy2(chrome / "chip_off.png", chrome / "chip_off_380.png")
    if not (chrome / "chip_on_380.png").exists() and (chrome / "chip_on.png").exists():
        shutil.copy2(chrome / "chip_on.png", chrome / "chip_on_380.png")
    if (chrome / "chip_off_380.png").exists():
        shutil.copy2(chrome / "chip_off_380.png", chrome / "chip_off.png")
        shutil.copy2(chrome / "chip_on_380.png", chrome / "chip_on.png")
        shutil.copy2(chrome / "chip_on_380.png", chrome / "chip_over.png")

    # 宽值条备用
    for src_name, dst_name in (
        ("chip_on_wide_571x75.png", "value_on.png"),
        ("value_on_571x75.png", "value_on.png"),
        ("chip_off_wide_571x75.png", "value_off.png"),
        ("value_off_571x75.png", "value_off.png"),
    ):
        src = VALUE_PARTS / src_name
        if src.exists() and not (chrome / dst_name).exists():
            shutil.copy2(src, chrome / dst_name)
    if (chrome / "value_on.png").exists():
        shutil.copy2(chrome / "value_on.png", chrome / "value_over.png")
    if ARROW_PNG.exists():
        Image.open(ARROW_PNG).convert("RGBA").save(chrome / "label_arrow.png")

    # 滑块旋钮 = 官方翼标整片
    save_official(chrome / "slider_knob.png", "option__pack", 18)
    save_official(chrome / "slider_knob_over.png", "option__pack", 18)

    # 静音 = 官方 s010 整片（不四切）
    mute = load_slice("option__pack", 10)
    if mute is not None:
        mute.save(chrome / "mute_off.png")
        mute.save(chrome / "mute_over.png")
        mute.save(chrome / "mute_on.png")
        mute.save(chrome / "mute_on_over.png")

    # 详细设定 = 官方 s011 整片（不半切）
    detail = load_slice("option__pack", 11)
    if detail is not None:
        detail.save(chrome / "detail_off.png")
        detail.save(chrome / "detail_on.png")
        detail.save(chrome / "detail_over.png")
    save_official(chrome / "voice_mic.png", "option__pack", 3)

    # 底栏钮 = 官方 cmds s000 整片
    btn = load_slice("option_cmds__pack", 0)
    if btn is not None:
        btn.save(chrome / "stdbtn_off.png")
        btn.save(chrome / "stdbtn_over.png")
        btn.save(chrome / "stdbtn_on.png")
    else:
        save_official(chrome / "stdbtn_off.png", "option__pack", 5)
        shutil.copy2(chrome / "stdbtn_off.png", chrome / "stdbtn_over.png")
        shutil.copy2(chrome / "stdbtn_off.png", chrome / "stdbtn_on.png")

    # 页签选中：原版为青色小圆点（非翼标整片当底）
    dot = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
    dr = ImageDraw.Draw(dot)
    dr.ellipse((1, 1, 16, 16), fill=(80, 230, 255, 255))
    dr.ellipse((4, 4, 13, 13), fill=(180, 255, 255, 220))
    dot.save(tabs_dir / "on.png")
    dot.save(tabs_dir / "on_w.png")
    # hover：淡青点
    dov = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
    dr = ImageDraw.Draw(dov)
    dr.ellipse((2, 2, 15, 15), fill=(120, 200, 240, 160))
    dov.save(tabs_dir / "over.png")
    dov.save(tabs_dir / "over_w.png")

    # 页签/底栏中文：locale 字（不是伪造 chrome 壳）
    for i, ti in enumerate(tab_items):
        lab = ti["label"]
        im = Image.new("RGBA", (max(80, ti["w"] - 8), 25), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        bb = dr.textbbox((0, 0), lab, font=fonts["tab"])
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        dr.text(((im.width - tw) // 2, (25 - th) // 2 - 1), lab, font=fonts["tab"], fill=(240, 248, 255, 255))
        fname = f"label_{i}.png"
        im.save(tabs_dir / fname)
        ti["label_file"] = f"angelic/settings/tabs/{fname}"
        ti["label_y"] = ti["y"] + 20

    for fid, lab in (("btn_init_cn", "恢复默认设置"), ("btn_title_cn", "标题画面"), ("btn_back_cn", "游戏画面")):
        im = Image.new("RGBA", (160, 22), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), lab, font=fonts["sm"], fill=(245, 250, 255, 255))
        im.save(chrome / f"{fid}.png")


def build_tab_items() -> list[dict]:
    """页签命中盒：option.pbd / option_0simple.pbd 的 page0..page9。"""
    hs_path = ROOT / "docs/ui-extract/pixel-reverse/pbd2json-layers/option.hotspots.json"
    by_page: dict[str, dict] = {}
    if hs_path.exists():
        doc = json.loads(hs_path.read_text(encoding="utf-8"))
        for h in doc.get("hotspots") or []:
            n = h.get("name") or ""
            if n.startswith("page") and n[4:].isdigit():
                by_page[n] = h
    # PAGE_MAP tid → 原版 pageN（5a/5b 同属 page5 槽，5b 热区略右移半宽）
    tid_to_page = {
        "0": "page0",
        "1": "page1",
        "2": "page2",
        "3": "page3",
        "4": "page4",
        "5a": "page5",
        "5b": "page5",
        "6": "page6",
        "8": "page8",
    }
    items = []
    for i, (tid, _cid, label) in enumerate(PAGE_MAP):
        pn = tid_to_page.get(tid, f"page{i}")
        h = by_page.get(pn) or {}
        x = int(h.get("left", 465 + i * 128))
        y = int(h.get("top", 0))
        w = int(h.get("width", 128))
        hgt = int(h.get("height", 81))
        if tid == "5b":
            x = x + w // 2
            w = max(64, w // 2)
        items.append(
            {
                "id": tid,
                "label": label,
                "x": x,
                "y": y,
                "w": w,
                "h": hgt,
                "label_y": y + 28,
                "label_file": f"angelic/settings/tabs/label_{i}.png",
            }
        )
    return items


def main() -> None:
    if not (TLG / "option__bg0.png").exists():
        raise SystemExit("missing option__bg0.png")

    truth = load_truth()
    # Angelic live-capture truth is the layout authority. PBD template offsets are
    # resource-local and cannot be used as screen-space coordinates for baked plates.
    apply_truth(truth)
    placements = load_page_placements()

    out = ensure(PREV)
    plates = ensure(out / "plates")
    chrome = ensure(out / "chrome")
    tabs_dir = ensure(out / "tabs")

    fonts = {
        "label": load_font(22),
        "sm": load_font(14),
        "hdr": load_font(18),
        "tab": load_font(14),
    }
    layout = build_native_layout()
    # sync footer globals from layout for baking
    global FOOTER_BTNS, FOOTER_Y, LEFT_ICON_X, LEFT_LABEL_X, LEFT_CTRL_X, RIGHT_RAIL_X, MUTE_X, ROW_YS
    if layout.get("footer"):
        FOOTER_BTNS = [
            (f["id"], f["label"], int(f["x"])) for f in layout["footer"]
        ]
        FOOTER_Y = int(layout["footer"][0]["y"])
    g = layout.get("grid") or {}
    if g.get("left_ctrl_x"):
        LEFT_CTRL_X = int(g["left_ctrl_x"])
    if g.get("right_rail_x"):
        RIGHT_RAIL_X = int(g["right_rail_x"])
    if g.get("mute_x"):
        MUTE_X = int(g["mute_x"])
    if g.get("row_ys"):
        ROW_YS = [int(y) for y in g["row_ys"]]
    pages = {t["id"]: t for t in layout["tabs"]}
    tab_items = build_tab_items()
    export_chrome(chrome, tabs_dir, tab_items, fonts)

    meta_tabs = []
    interaction: dict[str, list] = {}
    footer = [
        {
            "id": fid,
            "label": lab,
            "x": fx,
            "y": FOOTER_Y,
            "w": FOOTER_W,
            "h": FOOTER_H,
            "cn": f"angelic/settings/chrome/btn_{fid}_cn.png",
        }
        for fid, lab, fx in FOOTER_BTNS
    ]

    for i, (tid, cafe_id, label) in enumerate(PAGE_MAP):
        page = pages.get(tid) or {"rows": []}
        canvas, slots = bake_plate(tid, page, i, tab_items, fonts, placements)
        fname = f"plates/tab_{tid}.png"
        canvas.save(out / fname)
        canvas.save(plates / f"tab_{tid}.png")
        meta_tabs.append({"id": tid, "label": label, "plate": fname, "page": cafe_id})
        interaction[tid] = slots
        print(f"tab_{tid}: {len(slots)} slots  (topology {cafe_id}, truth geometry)")

    # chassis = 仅底图，禁止再叠 tab_0（否则每页都盖一层基本设置烤板 → 白框/错位）
    shutil.copy2(TLG / "option__bg0.png", out / "chassis.png")
    shutil.copy2(TLG / "option__bg0.png", out / "bg.png")

    help_map = parse_help()
    meta = {
        "family": "settings",
        "frame": {"x": LEFT_CTRL_X - 40, "y": 110, "w": 1700, "h": 860},
        "tabs": meta_tabs,
        "tabs_layout": {"items": tab_items},
        "footer": footer,
        "back": {"x": 1434, "y": FOOTER_Y, "w": FOOTER_W, "h": FOOTER_H, "label": "返回"},
        "help_box": HELP_BOX,
        "help": help_map,
        "layout": str(LAYOUT_OUT.relative_to(ROOT)).replace("\\", "/"),
        "truth": str(TRUTH_JSON.relative_to(ROOT)).replace("\\", "/") if TRUTH_JSON.exists() else None,
        "note": "official bare pixels from settings_truth(ig_option); wide_value on page0; bg-only chassis",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "interaction_slots.json").write_text(
        json.dumps(interaction, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    dst = ensure(RENPY)
    for src in out.rglob("*"):
        if src.is_file():
            rel = src.relative_to(out)
            d = dst / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, d)
    for junk in ("detail_cn.png", "slider_num.png"):
        for root in (out / "chrome", dst / "chrome"):
            p = root / junk
            if p.exists():
                p.unlink()

    hashes = {(plates / f"tab_{t}.png").read_bytes() for t, _, _ in PAGE_MAP}
    print("layout ->", LAYOUT_OUT)
    print("synced ->", dst)
    print("unique plates", len(hashes), "/", len(PAGE_MAP))

    # 官方裸像素：settings_truth + slice_placements（勿再跑 extract_angelic_settings_from_unpack，
    # 它会用启发式坐标覆盖 interaction_slots）
    # official_bare_pixels.json already written by build_settings_from_pbd2json


if __name__ == "__main__":
    main()
