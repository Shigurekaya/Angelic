# -*- coding: utf-8 -*-
"""Port cafe prefs/color_picker → angelic, then enrich settings slots/plates."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:/gamedev")
CAFE = ROOT / "renpy-cafe/game"
ANG = ROOT / "renpy-angelic/game"
ANGELIC = ROOT / "Angelic"
TLG = ANGELIC / "docs/ui-extract/pixel-reverse/tlg-png"
SLICES = ANGELIC / "docs/ui-extract/pixel-reverse/_pack_slices"
ARROW = ANGELIC / "docs/ui-extract/pixel-reverse/settings-layout/label_arrow_truth.png"
PREV = ANGELIC / "ui-preview/assets/settings"
RENPY_SET = ANG / "images/angelic/settings"
FONT = Path(r"C:/Windows/Fonts/msyh.ttc")

ANG_CF_KEYS = [
    "cf_save", "cf_overwrite", "cf_dsave", "cf_load", "cf_qsave", "cf_qload", "cf_title",
    "cf_jump", "cf_flow", "cf_next", "cf_backto", "cf_nextscn", "cf_prevscn", "cf_vsave",
    "cf_init", "cf_initstand", "cf_delete", "cf_swap", "cf_copy", "cf_exit", "cf_resume",
]
CF_LABELS = {
    "cf_save": "存档时确认",
    "cf_overwrite": "覆盖存档时确认",
    "cf_dsave": "直接存档时确认",
    "cf_load": "读档时确认",
    "cf_qsave": "快速存档时确认",
    "cf_qload": "快速读档时确认",
    "cf_title": "返回标题界面、中断回想时确认",
    "cf_jump": "历史记录跳转、语音回想时确认",
    "cf_flow": "流程图跳转时确认",
    "cf_next": "跳转下一个选项时确认",
    "cf_backto": "返回上一个选项时确认",
    "cf_nextscn": "跳转下一个场景时确认",
    "cf_prevscn": "返回上一个场景时确认",
    "cf_vsave": "语音收藏时确认",
    "cf_init": "恢复默认设置时确认",
    "cf_initstand": "重置立绘鉴赏模式时确认",
    "cf_delete": "删除存档时确认",
    "cf_swap": "移动存档时确认",
    "cf_copy": "复制存档时确认",
    "cf_exit": "退出游戏时确认",
    "cf_resume": "从待机模式中恢复时确认",
}


def port_rpy() -> None:
    # color picker
    cp = (CAFE / "cafe_color_picker.rpy").read_text(encoding="utf-8")
    pairs = [
        ("CafeColorWheel", "AngelicColorWheel"),
        ("CafeColorPreview", "AngelicColorPreview"),
        ("CAF_CP_GEOM_DEFAULT", "ANG_CP_GEOM_DEFAULT"),
        ("CAF_CP_GEOM", "ANG_CP_GEOM"),
        ("cafe_cp_load_geom", "angelic_cp_load_geom"),
        ("cafe_cp_dragging", "angelic_cp_dragging"),
        ("cafe_cp_set_drag", "angelic_cp_set_drag"),
        ("cafe_cp_redraw_preview", "angelic_cp_redraw_preview"),
        ("cafe_cp_bary", "angelic_cp_bary"),
        ("cafe_cp_closest_on_seg", "angelic_cp_closest_on_seg"),
        ("cafe_cp_clamp_to_tri", "angelic_cp_clamp_to_tri"),
        ("cafe_cp_sv_pos", "angelic_cp_sv_pos"),
        ("cafe_cp_sv_from_pos", "angelic_cp_sv_from_pos"),
        ("cafe_color_ring_path", "angelic_color_ring_path"),
        ("cafe_color_tri_path", "angelic_color_tri_path"),
        ("cafe_color_cursor_path", "angelic_color_cursor_path"),
        ("cafe_hsv_to_hex", "angelic_hsv_to_hex"),
        ("cafe_commit_color_picker", "angelic_commit_color_picker"),
        ("cafe_ensure_color_defaults", "angelic_ensure_color_defaults"),
        ("cafe_set_help", "angelic_set_help"),
        ("cafe/settings/chrome/colorpicker", "angelic/settings/chrome/colorpicker"),
        ("Cafe Stella", "Angelic"),
    ]
    for a, b in pairs:
        cp = cp.replace(a, b)
    cp = re.sub(r"\bcafe\b", "angelic", cp)
    (ANG / "angelic_color_picker.rpy").write_text(cp, encoding="utf-8")

    pf = (CAFE / "cafe_prefs.rpy").read_text(encoding="utf-8")
    pairs = [
        ("CAF_COLOR_DEFAULTS", "ANG_COLOR_DEFAULTS"),
        ("CAF_CF_KEYS", "ANG_CF_KEYS"),
        ("CAF_CHV_NAMES", "ANG_CHV_NAMES"),
        ("CAF_CHV_META", "ANG_CHV_META"),
        ("cafe_chv_meta", "angelic_chv_meta"),
        ("cafe_chv_target", "angelic_chv_target"),
        ("cafe_chv_sync_from_target", "angelic_chv_sync_from_target"),
        ("cafe_chv_ensure", "angelic_chv_ensure"),
        ("cafe_chv_click", "angelic_chv_click"),
        ("cafe_chv_portrait", "angelic_chv_portrait"),
        ("cafe_preview_fg", "angelic_preview_fg"),
        ("cafe_hsv_to_hex", "angelic_hsv_to_hex"),
        ("cafe_color_hex", "angelic_color_hex"),
        ("cafe_msg_text_color", "angelic_msg_text_color"),
        ("cafe_msg_win_alpha", "angelic_msg_win_alpha"),
        ("cafe_ensure_color_defaults", "angelic_ensure_color_defaults"),
        ("cafe_sync_color_from_target", "angelic_sync_color_from_target"),
        ("cafe_commit_color_picker", "angelic_commit_color_picker"),
        ("cafe_reset_colors", "angelic_reset_colors"),
        ("cafe_set_color_target", "angelic_set_color_target"),
        ("cafe_cp_redraw_preview", "angelic_cp_redraw_preview"),
        ("cafe_normalize_help_key", "angelic_normalize_help_key"),
        ("cafe_help_text", "angelic_prefs_help_text"),
        ("cafe_sanitize_help", "angelic_sanitize_help"),
        ("cafe_set_help", "angelic_set_help"),
        ("cafe_effective_volume", "angelic_effective_volume"),
        ("cafe_apply_volumes", "angelic_apply_volumes"),
        ("cafe_apply_pref", "angelic_apply_pref"),
        ("cafe_pick_toggle", "angelic_pick_toggle"),
        ("cafe_dialog_set", "angelic_dialog_set"),
        ("cafe_needs_confirm", "angelic_needs_confirm"),
        ("cafe_settings_defaults", "angelic_settings_defaults"),
        ("cafe_settings_init", "angelic_settings_init"),
        ("cafe_settings_page_keys", "angelic_settings_page_keys"),
        ("cafe_set_sound_page", "angelic_set_sound_page"),
        ("cafe/settings", "angelic/settings"),
        ("# Cafe Stella", "# Angelic"),
    ]
    for a, b in pairs:
        pf = pf.replace(a, b)
    pf = re.sub(r"\bcafe\b", "angelic", pf)
    # Angelic cast (14 slots for chv0-13)
    pf = re.sub(
        r"ANG_CHV_NAMES = \[[^\]]*\]",
        "ANG_CHV_NAMES = [\n"
        '        "白雪 乃爱", "谷风 天音", "小云雀 来海", "星河 辉耶",\n'
        '        "高屋敷 欧丽叶", "百里 风实花", "木下 枫", "白石 千花",\n'
        '        "三国 彩里", "谷风 柚月", "其他（女性）", "其他（男性）",\n'
        '        "其他A", "其他B",\n'
        "    ]",
        pf,
        count=1,
        flags=re.S,
    )
    pf = pf.replace('min(9, int(angelic.values.get("voice_target"', 'min(13, int(angelic.values.get("voice_target"')
    pf = pf.replace("for i in range(10):", "for i in range(14):")
    pf = pf.replace("min(9, int(n))", "min(13, int(n))")
    (ANG / "angelic_prefs.rpy").write_text(pf, encoding="utf-8")
    print("ported prefs/color_picker; cafe leftovers", len(re.findall(r"cafe", pf, re.I)), len(re.findall(r"cafe", cp, re.I)))


def magenta_to_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)
    return im


def load_slice(pack: str, index: int) -> Image.Image | None:
    d = SLICES / pack
    sj = d / "slices.json"
    if not sj.exists():
        return None
    for item in json.loads(sj.read_text(encoding="utf-8")):
        if int(item["i"]) == index:
            p = d / item["file"]
            if p.exists():
                return magenta_to_alpha(Image.open(p).convert("RGBA"))
    return None


def paste(canvas, spr, x, y):
    if spr is None:
        return
    x, y = int(x), int(y)
    if x < 0 or y < 0 or x >= canvas.width or y >= canvas.height:
        return
    if x + spr.width > canvas.width or y + spr.height > canvas.height:
        spr = spr.crop((0, 0, min(spr.width, canvas.width - x), min(spr.height, canvas.height - y)))
    canvas.alpha_composite(spr, (x, y))


def font(size: int):
    if FONT.exists():
        try:
            return ImageFont.truetype(str(FONT), size=size, index=0)
        except Exception:
            pass
    return ImageFont.load_default()


def chip_row(key, label, typ, opts, x, y, cw=175, ch=44, gap=20, help_key=None, default=0):
    n = max(1, len(opts or ["开启", "关闭"]))
    chips = [{"x": x + i * (cw + gap), "y": y, "w": cw, "h": ch, "i": i} for i in range(n)]
    return {
        "key": key,
        "label": label,
        "type": typ,
        "help_key": help_key or key,
        "x": x,
        "y": y,
        "w": n * cw + (n - 1) * gap,
        "h": ch,
        "default": default,
        "options": list(opts),
        "chips": chips,
        "chip_n": n,
        "chip_w": cw,
        "chip_h": ch,
    }


def slider_row(key, label, x, y, w=480, h=20, default=0.5, mute=False, help_key=None):
    item = {
        "key": key,
        "label": label,
        "type": "slider",
        "help_key": help_key or key,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "default": default,
        "track": {"x": x, "y": y, "w": w, "h": h},
        "num": {"x": x + w + 12, "y": y - 4, "w": 56, "h": 24},
    }
    if mute:
        item["mute"] = True
        item["mute_pos"] = {"x": x - 84, "y": y - 18, "w": 76, "h": 54}
    return item


def build_tab4_slots() -> list[dict]:
    """Text settings — measured from original screenshot topology."""
    slots = []
    # Left column
    slots.append(slider_row("textspeed", "文本显示速度", 280, 250, 500, 18, 0.50))
    slots.append(slider_row("autospeed", "自动模式速度", 280, 360, 500, 18, 0.50))
    slots.append({
        "key": "autotime_readout",
        "label": "基本等待时间",
        "type": "readout",
        "source": "autospeed",
        "help_key": "autospeed",
        "x": 280,
        "y": 430,
        "w": 220,
        "h": 28,
        "track": {"x": 280, "y": 430, "w": 220, "h": 28},
        "num": {"x": 510, "y": 428, "w": 90, "h": 28},
        "format": "sec",
    })
    slots.append(slider_row("atextwait", "每个文字的等待时间", 520, 500, 280, 18, 0.25))
    slots.append(chip_row("autovwait", "自动模式类型", "choice",
                          ["普通", "语音优先", "快速"], 160, 620, cw=160, gap=16, default=0))
    slots.append(chip_row("skipall", "快进未读文本", "toggle",
                          ["全部内容", "已读内容"], 160, 720, cw=200, gap=16, default=0))
    # skipall: original default is 已读=0 if options are [全部,已读]? 
    # Original screenshot: 已读 selected for skipall, 全部 for ctrlskip
    # Our options [全部内容, 已读内容] → skipall default 1 (已读), ctrlskip default 0 (全部)
    slots[-1]["default"] = 1
    slots.append(chip_row("ctrlskip", "Ctrl快进", "toggle",
                          ["全部内容", "已读内容"], 160, 800, cw=200, gap=16, default=0))
    slots.append(chip_row("afterskip", "选项后快进模式", "toggle",
                          ["继续", "解除"], 160, 880, cw=160, gap=16, default=0))
    slots.append(chip_row("afterauto", "选项后自动模式", "toggle",
                          ["继续", "解除"], 500, 880, cw=160, gap=16, default=0))

    # Right: color targets
    cy = 210
    for key, lab in (
        ("color_win", "正常模式对话框"),
        ("color_owin", "视点变更后对话框"),
        ("color_hwin", "Ｈ场景时对话框"),
    ):
        slots.append({
            "key": key,
            "label": lab,
            "type": "color_target",
            "help_key": key,
            "options": [lab],
            "x": 1024,
            "y": cy,
            "w": 350,
            "h": 46,
            "chip_n": 1,
            "default": 0,
        })
        cy += 58
    slots.append({
        "key": "nohwindow",
        "label": "Ｈ场景禁用对话框",
        "type": "check",
        "help_key": "nohwindow_chk",
        "x": 1088,
        "y": 390,
        "w": 33,
        "h": 33,
        "default": 0,
    })
    for key, lab in (("color_text", "未读文字"), ("color_read", "已读文字")):
        slots.append({
            "key": key,
            "label": lab,
            "type": "color_target",
            "help_key": key,
            "options": [lab],
            "x": 1024,
            "y": cy + 20,
            "w": 350,
            "h": 46,
            "chip_n": 1,
        })
        cy += 58
    slots.append({
        "key": "hsv_reset",
        "label": "重置",
        "type": "button",
        "help_key": "hsv_reset",
        "options": ["重置"],
        "x": 1523,
        "y": 500,
        "w": 160,
        "h": 40,
        "chip_n": 1,
        "special": "hsv_reset",
    })
    slots.append(slider_row("winopac", "对话框透明度", 1100, 880, 500, 18, 0.75))
    slots.append({
        "key": "fontselect",
        "label": "字体选择",
        "type": "button",
        "help_key": "fontselect",
        "options": ["字体选择"],
        "x": 1300,
        "y": 930,
        "w": 200,
        "h": 40,
        "chip_n": 1,
        "special": "fontselect",
    })
    return slots


def build_tab6_slots() -> list[dict]:
    """Confirm page — cfall + 21 cf_* as dialog_onoff in 3 columns."""
    slots = [{
        "key": "cfall",
        "label": "全部确认开关",
        "type": "toggle",
        "help_key": "cfall",
        "special": "cfall",
        "x": 600,
        "y": 156,
        "w": 520,
        "h": 46,
        "default": 1,
        "options": ["全部开启", "全部关闭"],
        "chips": [
            {"x": 600, "y": 156, "w": 240, "h": 46, "i": 1},
            {"x": 860, "y": 156, "w": 240, "h": 46, "i": 0},
        ],
        "chip_n": 2,
        "chip_w": 240,
        "chip_h": 46,
    }]
    # 3 columns × 7 rows
    cols = [
        ANG_CF_KEYS[0:7],
        ANG_CF_KEYS[7:14],
        ANG_CF_KEYS[14:21],
    ]
    xs = [120, 720, 1320]
    ys = [260, 360, 460, 560, 660, 760, 860]
    for ci, col in enumerate(cols):
        for ri, key in enumerate(col):
            y = ys[ri]
            x = xs[ci]
            slots.append({
                "key": key,
                "label": CF_LABELS.get(key, key),
                "type": "dialog_onoff",
                "help_key": key,
                "default": 1,
                "x": x,
                "y": y,
                "w": 430,
                "h": 44,
                "on": {"x": x + 10, "y": y, "w": 175, "h": 44},
                "off": {"x": x + 205, "y": y, "w": 175, "h": 44},
                "options": ["开启", "关闭"],
            })
    return slots


def build_tab5a_slots() -> list[dict]:
    """Audio1 — volumes + chv panel."""
    slots = []
    left = [
        ("wave", "总音量", 280, 220),
        ("bgm", "ＢＧＭ", 280, 340),
        ("movie", "视频", 280, 460),
        ("bgv", "ＢＧＶ（通常场景）", 280, 580),
        ("bgv2", "ＢＧＶ（Ｈ场景）", 280, 700),
    ]
    mid = [
        ("bgmdown", "ＢＧＭ（角色语音）", 700, 340),
        ("se", "ＳＥ（游戏音效）", 700, 460),
        ("sysse", "ＳＥ（系统音效）", 700, 580),
    ]
    for key, lab, x, y in left + mid:
        slots.append(slider_row(key, lab, x, y, 360, 18, 0.55, mute=True))
    slots.append(slider_row("voice", "语音（游戏中）", 1180, 220, 360, 18, 0.7, mute=True))
    slots.append(chip_row("voicecut", "语音中断", "toggle", ["开启", "关闭"], 1180, 300, cw=160, default=1))
    slots.append(chip_row("voeffect", "语音效果", "toggle", ["开启", "关闭"], 1180, 360, cw=160, default=1))
    # CHV panel
    slots.append(chip_row("chvall", "语音单独设定", "toggle", ["关", "开"], 1180, 430, cw=160, default=1,
                          help_key="chv_on"))
    slots.append(slider_row("chv", "角色语音音量", 1180, 500, 360, 18, 0.55, help_key="chv"))
    # 14 paw prints in 2 cols × 7
    names = [
        "白雪 乃爱", "谷风 天音", "小云雀 来海", "星河 辉耶",
        "高屋敷 欧丽叶", "百里 风实花", "木下 枫", "白石 千花",
        "三国 彩里", "谷风 柚月", "其他（女）", "其他（男）", "其他A", "其他B",
    ]
    for i in range(14):
        col = i // 7
        row = i % 7
        slots.append({
            "key": "chv%d" % i,
            "label": names[i] if i < len(names) else ("角色%d" % i),
            "type": "check",
            "help_key": "chv%d" % i,
            "x": 1180 + col * 280,
            "y": 560 + row * 42,
            "w": 33,
            "h": 33,
            "default": 1,
        })
    return slots


def build_tab5b_slots() -> list[dict]:
    return [
        slider_row("sysvo", "系统语音", 280, 260, 480, 18, 0.6, mute=True),
        slider_row("bgv", "ＢＧＶ（通常场景）", 280, 400, 480, 18, 0.5, mute=True),
        chip_row("sysse_en", "系统音效开关", "toggle", ["开启", "关闭"], 280, 540, default=1),
        chip_row("sysvo_en", "系统语音开关", "toggle", ["开启", "关闭"], 280, 640, default=1),
    ]


def draw_label(canvas, text, icon_x, label_x, y, fnt, arrow):
    if arrow is not None:
        paste(canvas, arrow, icon_x, y)
    dr = ImageDraw.Draw(canvas)
    bb = dr.textbbox((0, 0), text, font=fnt)
    th = bb[3] - bb[1]
    ty = y + max(4, (48 - th) // 2 - 1)
    dr.text((label_x + 1, ty + 1), text, font=fnt, fill=(20, 40, 90, 100))
    dr.text((label_x, ty), text, font=fnt, fill=(20, 50, 120, 255))


def bake_rich_plate(tid: str, slots: list[dict], pack_places: list[tuple[int, int, int]] | None = None) -> Image.Image:
    bg = Image.open(TLG / "option__bg0.png").convert("RGBA")
    canvas = bg.copy()
    side = load_slice("option__pack", 0)
    wing = load_slice("option__pack", 18)
    hdr_s = load_slice("option__pack", 12)
    hdr_t = load_slice("option__pack", 13)
    track = load_slice("option__pack", 14)
    arrow = Image.open(ARROW).convert("RGBA") if ARROW.exists() else None
    fnt = font(22)
    if side:
        paste(canvas, side, 58, 161)
    if wing:
        paste(canvas, wing, 40, 28)
    if hdr_s:
        paste(canvas, hdr_s, 180, 28)
    if hdr_t:
        paste(canvas, hdr_t, 330, 28)

    # labels for non-color_target / non-check rows
    seen_labels = set()
    for h in slots:
        key = h.get("key") or ""
        lab = h.get("label") or key
        typ = h.get("type")
        if typ in ("color_target", "check", "readout") and key.startswith("chv") and key[3:].isdigit():
            continue
        if typ == "color_target" or (typ == "check" and key == "nohwindow"):
            # section label once
            if "wintxcol" not in seen_labels and typ == "color_target":
                draw_label(canvas, "对话框・文字设置", 980, 1080, 160, fnt, arrow)
                seen_labels.add("wintxcol")
            continue
        if typ == "check" and key.startswith("chv") and key[3:].isdigit():
            continue
        if key in seen_labels:
            continue
        # place label above control
        if typ == "slider":
            ly = int(h["y"]) - 55
            ix = 160 if int(h["x"]) < 900 else (int(h["x"]) - 120)
            lx = ix + 100
        elif typ == "dialog_onoff":
            ly = int(h["y"]) - 36
            ix = max(40, int(h["x"]) - 40)
            lx = ix + 90
            # long labels: draw text only without arrow crowding
            dr = ImageDraw.Draw(canvas)
            dr.text((int(h["x"]), ly), lab[:18], font=font(16), fill=(20, 50, 120, 255))
            seen_labels.add(key)
            continue
        else:
            ly = int(h["y"]) - 50
            ix = max(80, int(h["x"]) - 80)
            lx = ix + 100
        if ly < 120:
            ly = 120
        draw_label(canvas, lab, ix, lx, ly, fnt, arrow)
        seen_labels.add(key)

    # rails
    for h in slots:
        if h.get("type") == "slider":
            tr = h.get("track") or h
            if track is not None:
                paste(canvas, track.resize((int(tr["w"]), track.height), Image.Resampling.LANCZOS)
                      if int(tr["w"]) != track.width else track,
                      int(tr["x"]), int(tr["y"]))
            else:
                ImageDraw.Draw(canvas).rectangle(
                    [int(tr["x"]), int(tr["y"]), int(tr["x"]) + int(tr["w"]), int(tr["y"]) + 12],
                    fill=(60, 140, 220, 220),
                )

    # page packs
    pack = {"4": "option_4text__pack", "5a": "option_5sound1__pack", "5b": "option_5sound2__pack", "6": "option_6dialog__pack"}.get(tid)
    places = pack_places or []
    if pack:
        for idx, x, y in places:
            spr = load_slice(pack, idx)
            paste(canvas, spr, x, y)

    # color section title / color label
    if tid == "4":
        draw_label(canvas, "颜色设置", 1480, 1580, 180, fnt, arrow)
        draw_label(canvas, "对话框透明度", 1020, 1120, 820, fnt, arrow)

    if tid == "5a":
        draw_label(canvas, "语音单独设定", 1100, 1200, 400, fnt, arrow)

    # footer
    footer = load_slice("option_cmds__pack", 0)
    for fx, lab in ((880, "恢复默认设置"), (1160, "标题画面"), (1440, "游戏画面")):
        if footer:
            paste(canvas, footer, fx, 973)
        dr = ImageDraw.Draw(canvas)
        bb = dr.textbbox((0, 0), lab, font=fnt)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        fw = footer.width if footer else 260
        fh = footer.height if footer else 60
        dr.text((fx + (fw - tw) // 2, 973 + (fh - th) // 2 - 1), lab, font=fnt, fill=(245, 250, 255, 255))
    return canvas


def enrich() -> None:
    """富页布局改由解包提取器生成（禁止截图坐标）。"""
    port_rpy()
    from extract_angelic_settings_from_unpack import main as unpack_main

    unpack_main()
    print("enriched OK (from unpack)")


if __name__ == "__main__":
    enrich()
