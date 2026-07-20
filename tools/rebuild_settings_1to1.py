# -*- coding: utf-8 -*-
"""Rebuild Angelic settings plates from static unpack (Cafe method, Angelic geometry).

Topology: Cafe/YuzuSoft option a–j slot keys (proven in Angelic PBD + help_opt)
Chrome:   option__bg0 + option__pack native sizes (313×57 label, 288×13 rail) — NO Cafe w/h
Labels:   locale/cn uitexts + help_opt
Interact: interaction_slots.json → Ren'Py overlays official chrome whole slices
Policy: 官方整片 only — no make_chip, no sub-crop, no nine_slice
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
LOCALE_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/uitexts_cn.toml"
HELP_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/help_opt_cn.txt"
CAFE_LAYOUT = Path(r"D:/gamedev/CafeStella/ui-preview/assets/settings/settings-layout.json")
LAYOUT_OUT = ROOT / "docs/ui-extract/pixel-reverse/settings-layout/angelic_settings_layout.json"
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
    ("8", "8a_keyboard1", "键盘"),
]

# Native chrome sizes = official option__pack slice sizes (整片使用，禁止二次裁切)
LABEL_W, LABEL_H = 313, 57   # s005 / s009
RAIL_W, RAIL_H = 288, 13      # s014
# 官方开关壳图 = 标签条整片；交互槽几何另计（Ren'Py Transform 缩放官方图）
CHIP_OFFICIAL_W, CHIP_OFFICIAL_H = 313, 57
SLOT_CHIP_W, SLOT_CHIP_H = 144, 37
CHIP_W, CHIP_H = SLOT_CHIP_W, SLOT_CHIP_H
DETAIL_W, DETAIL_H = 124, 32  # s011 整片
MUTE_W, MUTE_H = 76, 54       # s010 整片
MUTE_SZ = MUTE_W
ROW_YS = [160, 300, 440, 580, 720]
LEFT_X, RIGHT_X = 181, 1020
CTRL_DY = 62
FOOTER_Y = 973
HELP_BOX = {"x": 48, "y": 994, "w": 520, "h": 60}
FOOTER_BTNS = [
    ("init", "初始化", 940),
    ("title", "标题", 1187),
    ("back", "返回", 1434),
]
# option_cmds__pack s000 官方底栏钮整片
FOOTER_W, FOOTER_H = 242, 60

# 分页专用官方 pack（整图/整片烤进对应 plate，不裁内部）
PAGE_PACKS = {
    "4": "option_4text__pack",
    "5a": "option_5sound1__pack",
    "5b": "option_5sound2__pack",
    "6": "option_6dialog__pack",
    "8": "option_8keyboard1__pack",
}
# 分页官方切片定点（替代流式）；右栏装饰区，禁堆满控件
PAGE_PACK_PLACEMENTS = {
    "4": [(0, 1080, 200), (1, 1080, 520)],
    "5a": [(3, 1180, 200)],
    "5b": [(0, 1280, 160)],
    "6": [(0, 1680, 220)],
    "8": [(0, 1280, 180)],
}

LABEL_CN = {
    "fullscreen": "显示模式",
    "sqscr": "画面比例",
    "textspeed": "文本显示速度",
    "autospeed": "自动模式速度",
    "skipall": "快进未读文本",
    "wave": "总音量",
    "bgm": "ＢＧＭ",
    "se": "ＳＥ",
    "voice": "语音",
    "movie": "视频",
    "noeffect": "画面效果",
    "scanim": "动画效果",
    "esccancel": "ESC键功能",
    "panictype": "老板键功能",
    "stayontop": "保持窗口最前",
    "showitems": "功能区域开关",
    "talkface": "说话人物表情",
    "popup": "显示弹出内容",
    "chapthidetime": "章节标题显示",
    "bgmhidetime": "BGM标题显示",
    "facemode": "立绘模式",
    "qcpopover": "弹出菜单",
    "readskip": "自动跳过已读",
    "readjump": "已读跳过方式",
    "curmove": "光标自动移动",
    "curmoveyes": "光标移向",
    "curhidestep": "光标自动隐藏",
    "hselfix": "Ｈ场景选项固定",
    "allflow": "流程图显示未读",
    "deactive": "非活动时状态",
    "suspend": "待机功能",
    "preview": "任务栏预览",
    "drawspeed": "游戏进行速度",
    "voplspeed": "语音播放速度",
    "skipspeed": "快进速度",
    "skipstyle": "快进方式",
    "dramatic": "沉浸式体验",
    "rclkmvskip": "右键跳过视频",
    "skipmvskip": "快进时跳过视频",
    "atextwait": "每字等待时间",
    "autosty": "自动模式类型",
    "keep_skip": "选项后保持快进",
    "keep_auto": "选项后保持自动",
    "winopac": "对话框透明度",
    "bgmdown": "ＢＧＭ（语音时）",
    "voicecut": "语音中断",
    "voeffect": "语音效果",
    "sysse": "ＳＥ（系统）",
    "sysvo": "系统语音",
    "bgv": "ＢＧＶ（通常）",
    "bgv2": "ＢＧＶ（Ｈ）",
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
    "gesture": "鼠标手势",
    "wheel": "滚轮",
    "gsenable": "手势功能",
    "keybind": "快捷键绑定",
    "kbhelp": "键盘说明",
    "pad": "游戏手柄",
    "gamepad": "游戏手柄",
}

OPTS_CN = {
    "fullscreen": ["窗口", "全屏"],
    "sqscr": ["16:9", "4:3"],
    "skipall": ["仅已读", "全部"],
    "noeffect": ["关", "开"],
    "scanim": ["关", "开"],
    "esccancel": ["右键菜单", "老板键"],
    "stayontop": ["关", "开"],
    "showitems": ["关", "开"],
    "talkface": ["关", "开"],
    "popup": ["悬停", "右键"],
    "readskip": ["关", "开"],
    "curmove": ["关", "开"],
    "curhide": ["关", "开"],
    "hselfix": ["关", "开"],
    "allflow": ["关", "开"],
    "deactive": ["停止", "继续"],
    "suspend": ["关", "开"],
    "skipstyle": ["普通", "快进", "纯文字"],
    "dramatic": ["关", "开"],
    "rclkmvskip": ["关", "开"],
    "autosty": ["普通", "语音优先", "快速"],
    "keep_skip": ["关", "开"],
    "keep_auto": ["关", "开"],
    "voicecut": ["关", "开"],
    "voeffect": ["关", "开"],
    "sysse_en": ["关", "开"],
    "sysvo_en": ["关", "开"],
    "gesture": ["关", "开"],
    "wheel": ["关", "开"],
    "gamepad": ["关", "开"],
    "gsenable": ["关", "开"],
    "pad": ["关", "开"],
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


def paste_page_pack_placed(canvas: Image.Image, tid: str) -> None:
    """按 PAGE_PACK_PLACEMENTS 整片定点摆放。"""
    pack = PAGE_PACKS.get(tid)
    places = PAGE_PACK_PLACEMENTS.get(tid) or []
    if not pack or not places:
        return
    for idx, x, y in places:
        spr = load_slice(pack, idx)
        if spr is None:
            continue
        px = min(int(x), 1920 - spr.width - 8)
        py = min(int(y), 1080 - spr.height - 8)
        paste(canvas, spr, px, py)


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


def load_cafe_pages() -> dict[str, dict]:
    raw = json.loads(CAFE_LAYOUT.read_text(encoding="utf-8"))
    return {t["id"]: t for t in raw.get("tabs") or []}


def row_label(row: dict) -> str:
    key = row.get("key") or ""
    return LABEL_CN.get(key) or row.get("label") or key


def row_options(row: dict) -> list[str] | None:
    key = row.get("key") or ""
    if key in OPTS_CN:
        return list(OPTS_CN[key])
    opts = row.get("options")
    return list(opts) if opts else None


def rematerialize_rows(cafe_page: dict, single_col: bool = False) -> list[dict]:
    """Keep Cafe keys/types; place with Angelic native chrome sizes."""
    src = list(cafe_page.get("rows") or [])
    if not src:
        return []

    left = sorted([r for r in src if int(r.get("x") or 0) < 700], key=lambda r: int(r.get("y") or 0))
    right = sorted([r for r in src if int(r.get("x") or 0) >= 700], key=lambda r: int(r.get("y") or 0))
    third: list[dict] = []
    if single_col:
        all_rows = left + right
        left = all_rows[: len(ROW_YS)]
        right = []
        third = all_rows[len(ROW_YS) : 2 * len(ROW_YS)]
    else:
        if not right and len(left) > len(ROW_YS):
            mid = (len(left) + 1) // 2
            right = left[mid:]
            left = left[:mid]
        elif len(left) > len(ROW_YS):
            overflow = left[len(ROW_YS) :]
            left = left[: len(ROW_YS)]
            right = overflow + right
        if len(right) > len(ROW_YS):
            third = right[len(ROW_YS) :]
            right = right[: len(ROW_YS)]
        if len(left) > len(ROW_YS):
            third = left[len(ROW_YS) :] + third
            left = left[: len(ROW_YS)]

    out: list[dict] = []

    def place(group: list[dict], col_x: int) -> None:
        for i, row in enumerate(group):
            if i >= len(ROW_YS):
                break
            ly = ROW_YS[i]
            key = row.get("key") or ""
            typ = row.get("type") or "toggle"
            if typ == "choice":
                typ = "toggle"
            opts = row_options(row)
            n = len(opts) if opts else (2 if typ != "slider" else 0)
            lx, ly_i = col_x, ly
            cy = ly_i + CTRL_DY
            item = {
                "slot": row.get("slot") or key,
                "key": key,
                "label": row_label(row),
                "type": "slider" if typ == "slider" else "toggle",
                "x": lx,
                "y": ly_i,
                "w": LABEL_W,
                "h": LABEL_H,
            }
            if typ == "slider":
                item["ctrl"] = {"x": lx + 12, "y": cy + 8, "w": RAIL_W, "h": RAIL_H, "slot": item["slot"]}
                item["track"] = {"x": lx + 12, "y": cy + 8, "w": RAIL_W, "h": RAIL_H}
            else:
                n = max(1, min(n or 2, 4))
                if n == 3:
                    cw = 100
                    total_w = n * cw + 8
                elif n == 4:
                    cw = 74
                    total_w = n * cw + 12
                else:
                    cw = CHIP_W
                    total_w = n * CHIP_W + max(0, n - 1) * 4
                item["ctrl"] = {"x": lx + 12, "y": cy, "w": total_w, "h": CHIP_H, "slot": item["slot"]}
                item["chip_w"] = cw
                item["chip_n"] = n
            if opts:
                item["options"] = opts
            out.append(item)

    place(left, LEFT_X)
    place(right, RIGHT_X)
    if third:
        place(third[: len(ROW_YS)], 610)
    return out


def build_native_layout(cafe_pages: dict[str, dict]) -> dict:
    tabs = []
    for tid, cafe_id, label in PAGE_MAP:
        cafe = cafe_pages.get(cafe_id) or {"rows": []}
        rows = rematerialize_rows(cafe, single_col=(tid in PAGE_PACK_PLACEMENTS))
        tabs.append({"id": tid, "cafe_id": cafe_id, "label": label, "rows": rows})
    doc = {
        "source": "Angelic static: option__bg0 + option__pack native + Cafe slot topology (keys only); no mouse/gamepad",
        "chrome": {
            "label": {"w": LABEL_W, "h": LABEL_H, "slice": "option__pack/s005"},
            "rail": {"w": RAIL_W, "h": RAIL_H, "slice": "option__pack/s014"},
            "chip": {"w": CHIP_OFFICIAL_W, "h": CHIP_OFFICIAL_H, "slice": "option__pack/s005"},
            "chip_on": {"slice": "option__pack/s009"},
            "detail": {"w": DETAIL_W, "h": DETAIL_H, "slice": "option__pack/s011"},
            "mute": {"w": MUTE_W, "h": MUTE_H, "slice": "option__pack/s010"},
            "knob": {"slice": "option__pack/s018"},
            "footer": {"slice": "option_cmds__pack/s000"},
        },
        "grid": {"left_x": LEFT_X, "right_x": RIGHT_X, "row_ys": ROW_YS, "ctrl_dy": CTRL_DY},
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
) -> tuple[Image.Image, list[dict]]:
    bg = Image.open(TLG / "option__bg0.png").convert("RGBA")
    canvas = bg.copy()
    label_src = load_slice("option__pack", 5)  # 官方蓝标签条整片
    label_hi = load_slice("option__pack", 9)   # 官方亮标签条整片
    track_src = load_slice("option__pack", 14) # 官方滑轨整片
    hdr_system = load_slice("option__pack", 12)  # SYSTEM 字图整片
    hdr_setting = load_slice("option__pack", 13)  # SETTING 字图整片
    side = load_slice("option__pack", 0)  # 左侧装饰整片
    wing = load_slice("option__pack", 18)  # 翼标整片

    if side:
        paste(canvas, side, 58, 161)
    if wing:
        paste(canvas, wing, 40, 28)
    if hdr_system:
        paste(canvas, hdr_system, LEFT_X, 118)
    if hdr_setting:
        paste(canvas, hdr_setting, LEFT_X + 150, 118)

    # 页签字不烤进 plate（运行时 tabs/label_* 叠层）
    _ = tab_index
    _ = label_hi

    slots: list[dict] = []
    for row in page.get("rows") or []:
        key = row.get("key") or ""
        typ = row.get("type") or "toggle"
        lx, ly = int(row["x"]), int(row["y"])
        lw, lh = int(row["w"]), int(row["h"])
        label = row.get("label") or row_label(row)
        opts = row.get("options") or row_options(row)

        if label_src is not None:
            # 官方整片原尺寸粘贴，禁止九切片
            paste(canvas, label_src, lx, ly)
            lw, lh = label_src.size

        dr = ImageDraw.Draw(canvas)
        bb = dr.textbbox((0, 0), label, font=fonts["label"])
        th = bb[3] - bb[1]
        tx = lx + 40
        ty = ly + max(4, (lh - th) // 2 - 1)
        dr.text((tx + 1, ty + 1), label, font=fonts["label"], fill=(10, 20, 50, 150))
        dr.text((tx, ty), label, font=fonts["label"], fill=(240, 248, 255, 255))

        ctrl = row.get("ctrl") or {}
        track = row.get("track") or {}
        item: dict = {
            "key": key,
            "label": label,
            "type": typ,
            "help_key": key,
            "x": int(ctrl.get("x") or lx + 12),
            "y": int(ctrl.get("y") or (ly + CTRL_DY)),
            "w": int(ctrl.get("w") or RAIL_W),
            "h": int(ctrl.get("h") or CHIP_H),
            "default": 0.55 if typ == "slider" else 0,
        }
        if opts:
            item["options"] = opts
            item["chip_n"] = int(row.get("chip_n") or len(opts))

        if typ == "slider" or track:
            tr = track or {"x": item["x"], "y": item["y"], "w": RAIL_W, "h": RAIL_H}
            if track_src is not None:
                paste(canvas, track_src, int(tr["x"]), int(tr["y"]))
                tw, thh = track_src.size
            else:
                tw, thh = int(tr["w"]), max(RAIL_H, int(tr.get("h") or RAIL_H))
            item["type"] = "slider"
            item["track"] = {"x": int(tr["x"]), "y": int(tr["y"]), "w": tw, "h": thh}
            item["num"] = {"x": int(tr["x"]) + tw + 10, "y": int(tr["y"]) - 6, "w": 56, "h": 24}
            item["x"], item["y"], item["w"], item["h"] = item["track"]["x"], item["track"]["y"], tw, thh
            if key in MUTE_KEYS:
                item["mute"] = True
                item["mute_pos"] = {
                    "x": int(tr["x"]) - MUTE_W - 8,
                    "y": int(tr["y"]) - (MUTE_H - thh) // 2,
                    "w": MUTE_W,
                    "h": MUTE_H,
                }
        else:
            n = int(item.get("chip_n") or 2)
            cw = max(80, int(RAIL_W // max(1, n)) - 4)
            if n == 3:
                cw = min(cw, 100)
            elif n == 4:
                cw = min(cw, 74)
            gap = 4
            chips = []
            for ci in range(n):
                chips.append(
                    {
                        "x": int(item["x"]) + ci * (cw + gap),
                        "y": int(item["y"]),
                        "w": cw,
                        "h": CHIP_H,
                        "i": ci,
                    }
                )
            item["chips"] = chips
            item["w"] = chips[-1]["x"] + chips[-1]["w"] - chips[0]["x"] if chips else item["w"]
            item["h"] = CHIP_H

        if tid == "0" and typ in ("toggle", "slider"):
            item["detail"] = {
                "x": lx + lw - DETAIL_W - 4,
                "y": ly + (lh - DETAIL_H) // 2,
                "w": DETAIL_W,
                "h": DETAIL_H,
            }

        slots.append(item)

    # 分页官方 pack：定点整片（禁流式堆叠）
    paste_page_pack_placed(canvas, tid)

    # 底栏：官方 cmds 钮整片
    footer_spr = load_slice("option_cmds__pack", 0) or load_slice("option__pack", 5)
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

    hb = HELP_BOX
    # 帮助区：不手绘壳、不硬缩放官方复合板；仅留透明热区由运行时叠字
    _ = hb

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

    # 开关壳 = 官方标签条整片（off=s005 / on·over=s009）
    save_official(chrome / "chip_off.png", "option__pack", 5)
    save_official(chrome / "chip_on.png", "option__pack", 9)
    save_official(chrome / "chip_over.png", "option__pack", 9)
    for prefix in ("chip3", "chip4"):
        shutil.copy2(chrome / "chip_off.png", chrome / f"{prefix}_off.png")
        shutil.copy2(chrome / "chip_on.png", chrome / f"{prefix}_on.png")
        shutil.copy2(chrome / "chip_over.png", chrome / f"{prefix}_over.png")

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

    # 页签选中/悬停：官方翼标 / 箭头整片
    tab_on = load_slice("option__pack", 18)
    tab_ov = load_slice("option__pack", 16) or load_slice("option__pack", 17)
    if tab_on is not None:
        tab_on.save(tabs_dir / "on.png")
        tab_on.save(tabs_dir / "on_w.png")
    if tab_ov is not None:
        tab_ov.save(tabs_dir / "over.png")
        tab_ov.save(tabs_dir / "over_w.png")
    elif tab_on is not None:
        shutil.copy2(tabs_dir / "on.png", tabs_dir / "over.png")
        shutil.copy2(tabs_dir / "on.png", tabs_dir / "over_w.png")

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
        ti["label_y"] = ti["y"] + 14

    for fid, lab in (("btn_init_cn", "初始化"), ("btn_title_cn", "标题"), ("btn_back_cn", "返回")):
        im = Image.new("RGBA", (120, 20), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), lab, font=fonts["sm"], fill=(245, 250, 255, 255))
        im.save(chrome / f"{fid}.png")


def build_tab_items() -> list[dict]:
    n = len(PAGE_MAP)
    x0, x1, y, th = 160, 1760, 28, 52
    tw = (x1 - x0) // n
    return [
        {"id": tid, "label": label, "x": x0 + i * tw, "y": y, "w": tw, "h": th}
        for i, (tid, _cid, label) in enumerate(PAGE_MAP)
    ]


def main() -> None:
    if not CAFE_LAYOUT.exists():
        raise SystemExit(f"missing Cafe topology: {CAFE_LAYOUT}")
    if not (TLG / "option__bg0.png").exists():
        raise SystemExit("missing option__bg0.png")

    out = ensure(PREV)
    plates = ensure(out / "plates")
    chrome = ensure(out / "chrome")
    tabs_dir = ensure(out / "tabs")

    fonts = {
        "label": load_font(20),
        "sm": load_font(14),
        "hdr": load_font(18),
        "tab": load_font(14),
    }
    cafe_pages = load_cafe_pages()
    layout = build_native_layout(cafe_pages)
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
        canvas, slots = bake_plate(tid, page, i, tab_items, fonts)
        fname = f"plates/tab_{tid}.png"
        canvas.save(out / fname)
        canvas.save(plates / f"tab_{tid}.png")
        meta_tabs.append({"id": tid, "label": label, "plate": fname, "page": cafe_id})
        interaction[tid] = slots
        print(f"tab_{tid}: {len(slots)} slots  (topology {cafe_id}, native chrome)")

    shutil.copy2(plates / "tab_0.png", out / "chassis.png")
    shutil.copy2(TLG / "option__bg0.png", out / "bg.png")

    help_map = parse_help()
    meta = {
        "family": "settings",
        "frame": {"x": LEFT_X - 20, "y": 110, "w": 1560, "h": 860},
        "tabs": meta_tabs,
        "tabs_layout": {"items": tab_items},
        "footer": footer,
        "back": {"x": 1520, "y": FOOTER_Y, "w": FOOTER_W, "h": FOOTER_H, "label": "返回"},
        "help_box": HELP_BOX,
        "help": help_map,
        "layout": str(LAYOUT_OUT.relative_to(ROOT)).replace("\\", "/"),
        "note": "official-only chrome: option__pack / option_cmds / page packs whole slices; no make_chip / no sub-crop",
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
    # 同步后清掉目标侧历史合成残留
    for junk in ("detail_cn.png", "slider_num.png"):
        for root in (out / "chrome", dst / "chrome"):
            p = root / junk
            if p.exists():
                p.unlink()

    hashes = {(plates / f"tab_{t}.png").read_bytes() for t, _, _ in PAGE_MAP}
    print("layout ->", LAYOUT_OUT)
    print("synced ->", dst)
    print("unique plates", len(hashes), "/", len(PAGE_MAP))


if __name__ == "__main__":
    main()
