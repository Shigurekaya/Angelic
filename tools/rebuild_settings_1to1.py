# -*- coding: utf-8 -*-
"""Rebuild Angelic settings plates 1:1 method (Cafe Stella style).

PBD ox/oy for Angelic is too noisy to place atlas tiles. Instead:
  - bg0 chassis
  - chrome slices (label ribbons / slider tracks / checks) stamped into measured slots
  - CN labels from locale/cn/uitexts_cn.toml
  - per-tab interaction_slots.json for Ren'Py overlays

Do NOT dump whole option_*__pack atlases into the frame.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
LOCALE_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/uitexts_cn.toml"
PREV = ROOT / "ui-preview/assets/settings"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/settings"
FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")

OPTION_FRAME = {"x": 109, "y": 120, "w": 1701, "h": 839}

# Top tab strip (measured guess; refine when live capture exists)
TAB_STRIP = {"x0": 200, "x1": 1680, "y": 28, "h": 52}

PAGE_ORDER = [
    ("0", "基本设置"),
    ("1", "画面设置"),
    ("2", "游戏设置1"),
    ("3", "游戏设置2"),
    ("4", "文本设置"),
    ("5a", "音频1"),
    ("5b", "音频2"),
    ("6", "确认信息"),
    ("7", "鼠标"),
    ("8", "键盘"),
    ("9", "手柄"),
]

# Cafe-style rows: (key, label, type, options|None)
PAGE_ROWS: dict[str, list[tuple]] = {
    "0": [
        ("fullscreen", "显示模式", "toggle", ["窗口", "全屏"]),
        ("sqscr", "画面比例", "toggle", ["16:9", "4:3"]),
        ("textspeed", "文本显示速度", "slider", None),
        ("autospeed", "自动模式速度", "slider", None),
        ("skipall", "快进未读文本", "toggle", ["仅已读", "全部"]),
        ("wave", "总音量", "slider", None),
        ("bgm", "ＢＧＭ", "slider", None),
        ("se", "ＳＥ", "slider", None),
        ("voice", "语音", "slider", None),
        ("movie", "视频", "slider", None),
    ],
    "1": [
        ("fullscreen", "显示模式", "toggle", ["窗口", "全屏"]),
        ("sqscr", "画面比例", "toggle", ["16:9", "4:3"]),
        ("noeffect", "画面效果", "toggle", ["关", "开"]),
        ("scanim", "动画效果", "toggle", ["关", "开"]),
        ("esccancel", "ESC键功能", "toggle", ["右键菜单", "老板键"]),
        ("stayontop", "保持窗口最前", "toggle", ["关", "开"]),
        ("showitems", "功能区域开关", "toggle", ["关", "开"]),
        ("talkface", "说话人物表情", "toggle", ["关", "开"]),
        ("popup", "显示弹出内容", "toggle", ["悬停", "右键"]),
    ],
    "2": [
        ("readskip", "自动跳过已读", "toggle", ["关", "开"]),
        ("curmove", "光标自动移动", "toggle", ["关", "开"]),
        ("curhide", "光标自动隐藏", "toggle", ["关", "开"]),
        ("hselfix", "Ｈ场景选项固定", "toggle", ["关", "开"]),
        ("allflow", "流程图显示未读", "toggle", ["关", "开"]),
        ("deactive", "非活动时状态", "toggle", ["停止", "继续"]),
        ("suspend", "待机功能", "toggle", ["关", "开"]),
    ],
    "3": [
        ("drawspeed", "游戏进行速度", "slider", None),
        ("voplspeed", "语音播放速度", "slider", None),
        ("skipspeed", "快进速度", "slider", None),
        ("skipstyle", "快进方式", "choice", ["普通", "快进", "纯文字"]),
        ("dramatic", "沉浸式体验", "toggle", ["关", "开"]),
        ("rclkmvskip", "右键跳过视频", "toggle", ["关", "开"]),
    ],
    "4": [
        ("textspeed", "文本显示速度", "slider", None),
        ("autospeed", "自动模式速度", "slider", None),
        ("atextwait", "每字等待时间", "slider", None),
        ("autosty", "自动模式类型", "choice", ["普通", "语音优先", "快速"]),
        ("skipall", "快进未读文本", "toggle", ["仅已读", "全部"]),
        ("keep_skip", "选项后保持快进", "toggle", ["关", "开"]),
        ("keep_auto", "选项后保持自动", "toggle", ["关", "开"]),
        ("winopac", "对话框透明度", "slider", None),
    ],
    "5a": [
        ("wave", "总音量", "slider", None),
        ("bgm", "ＢＧＭ", "slider", None),
        ("bgmdown", "ＢＧＭ（语音时）", "slider", None),
        ("movie", "视频", "slider", None),
        ("se", "ＳＥ（游戏）", "slider", None),
        ("voice", "语音（游戏）", "slider", None),
        ("voicecut", "语音中断", "toggle", ["关", "开"]),
        ("voeffect", "语音效果", "toggle", ["关", "开"]),
    ],
    "5b": [
        ("sysse", "ＳＥ（系统）", "slider", None),
        ("sysvo", "系统语音", "slider", None),
        ("bgv", "ＢＧＶ（通常）", "slider", None),
        ("bgv2", "ＢＧＶ（Ｈ）", "slider", None),
        ("sysse_en", "系统音效开关", "toggle", ["关", "开"]),
        ("sysvo_en", "系统语音开关", "toggle", ["关", "开"]),
    ],
    "6": [
        ("cf_save", "存档时确认", "dialog_onoff", ["开", "关"]),
        ("cf_overwrite", "覆盖存档时确认", "dialog_onoff", ["开", "关"]),
        ("cf_load", "读档时确认", "dialog_onoff", ["开", "关"]),
        ("cf_qsave", "快速存档时确认", "dialog_onoff", ["开", "关"]),
        ("cf_qload", "快速读档时确认", "dialog_onoff", ["开", "关"]),
        ("cf_title", "返回标题时确认", "dialog_onoff", ["开", "关"]),
        ("cf_exit", "退出游戏时确认", "dialog_onoff", ["开", "关"]),
        ("cf_init", "恢复默认时确认", "dialog_onoff", ["开", "关"]),
    ],
    "7": [
        ("gesture", "鼠标手势", "toggle", ["关", "开"]),
        ("wheel", "滚轮", "toggle", ["关", "开"]),
        ("note", "本页详细绑定需原版手势编辑器", "button", ["说明"]),
    ],
    "8": [
        ("binding", "快捷键绑定", "button", ["查看"]),
        ("note", "本页详细键位需原版按键编辑器", "button", ["说明"]),
    ],
    "9": [
        ("gamepad", "游戏手柄", "toggle", ["关", "开"]),
        ("note", "本页详细分配需原版手柄编辑器", "button", ["说明"]),
    ],
}


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


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
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
    if x >= canvas.width or y >= canvas.height:
        return
    canvas.alpha_composite(spr, (x, y))


def paste_fit(canvas: Image.Image, spr: Image.Image | None, x: int, y: int, w: int, h: int) -> None:
    if spr is None or w <= 0 or h <= 0:
        return
    if spr.size != (w, h):
        spr = spr.resize((w, h), Image.Resampling.LANCZOS)
    paste(canvas, spr, x, y)


def make_chip(w: int, h: int, on: bool) -> Image.Image:
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    if on:
        fill = (210, 230, 255, 230)
        outline = (255, 255, 255, 255)
    else:
        fill = (30, 55, 110, 200)
        outline = (180, 210, 255, 220)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), radius=10, fill=fill, outline=outline, width=2)
    return im


def make_slider_track(w: int, h: int = 18) -> Image.Image:
    base = load_slice("option__pack", 14)
    if base is not None:
        return base.resize((w, h), Image.Resampling.LANCZOS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(40, 80, 160, 200), outline=(200, 230, 255, 255))
    return im


def make_label_bar(w: int, h: int = 46) -> Image.Image:
    base = load_slice("option__pack", 5) or load_slice("option__pack", 9)
    if base is not None:
        return base.resize((w, h), Image.Resampling.LANCZOS)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    dr.rounded_rectangle((0, 0, w - 1, h - 1), radius=8, fill=(25, 55, 130, 210), outline=(220, 235, 255, 255), width=2)
    return im


def layout_rows(tid: str) -> list[dict]:
    """Build absolute rects for rows (2-col for simple / long lists wrap)."""
    rows = PAGE_ROWS.get(tid) or []
    fx, fy = OPTION_FRAME["x"], OPTION_FRAME["y"]
    fw, fh = OPTION_FRAME["w"], OPTION_FRAME["h"]
    pad_x, pad_y = 36, 72
    gap_x, gap_y = 28, 12
    # dialog page: single column denser
    if tid == "6":
        cols = 1
        cell_w = fw - pad_x * 2
        cell_h = 72
    elif tid in ("7", "8", "9"):
        cols = 1
        cell_w = fw - pad_x * 2
        cell_h = 96
    else:
        cols = 2
        cell_w = (fw - pad_x * 2 - gap_x) // 2
        # 基本设置 2×5 必须塞进 frame；其它页可略疏
        cell_h = 112 if tid == "0" else 100

    out = []
    for i, (key, label, typ, opts) in enumerate(rows):
        c = i % cols
        r = i // cols
        x = fx + pad_x + c * (cell_w + gap_x)
        y = fy + pad_y + r * (cell_h + gap_y)
        # 底栏 cmds 占约 56px；内容勿压住
        if y + cell_h > fy + fh - 64:
            break
        label_h = 40
        ctrl_y = y + label_h + 10
        ctrl_h = 46
        item = {
            "key": key,
            "label": label,
            "type": typ,
            "options": opts,
            "x": x,
            "y": y,
            "w": cell_w,
            "h": cell_h,
            "label_rect": {"x": x, "y": y, "w": cell_w, "h": label_h},
        }
        if typ == "slider":
            track_w = min(640, cell_w - 20)
            item["track"] = {"x": x + 10, "y": ctrl_y + 8, "w": track_w, "h": 22}
            item["num"] = {"x": x + 10 + track_w + 10, "y": ctrl_y + 4, "w": 66, "h": 28}
        elif typ in ("toggle", "choice", "dialog_onoff", "button"):
            n = max(1, len(opts or ["关", "开"]))
            bw = min(208, (cell_w - 20) // n - 8) if n > 1 else min(280, cell_w - 40)
            gap = 12
            total = n * bw + (n - 1) * gap
            ox0 = x + max(10, (cell_w - total) // 2)
            chips = []
            for ci in range(n):
                chips.append({"x": ox0 + ci * (bw + gap), "y": ctrl_y, "w": bw, "h": ctrl_h, "i": ci})
            item["chips"] = chips
            if typ == "dialog_onoff" and len(chips) >= 2:
                item["on"] = chips[0]
                item["off"] = chips[1]
        out.append(item)
    return out


def draw_tab_strip(canvas: Image.Image, active: int, font: ImageFont.ImageFont) -> list[dict]:
    n = len(PAGE_ORDER)
    x0, x1 = TAB_STRIP["x0"], TAB_STRIP["x1"]
    y, th = TAB_STRIP["y"], TAB_STRIP["h"]
    tw = (x1 - x0) // n
    items = []
    dr = ImageDraw.Draw(canvas)
    for i, (tid, label) in enumerate(PAGE_ORDER):
        x = x0 + i * tw
        items.append({"id": tid, "label": label, "x": x, "y": y, "w": tw, "h": th})
        # selected underline + brighter text
        if i == active:
            dr.rounded_rectangle((x + 4, y + 4, x + tw - 4, y + th - 4), radius=8, outline=(255, 255, 255, 220), width=2)
            fill = (255, 255, 255, 255)
        else:
            fill = (190, 215, 245, 220)
        bb = dr.textbbox((0, 0), label, font=font)
        twt = bb[2] - bb[0]
        tht = bb[3] - bb[1]
        tx = x + (tw - twt) // 2
        ty = y + (th - tht) // 2 - 2
        dr.text((tx + 1, ty + 1), label, font=font, fill=(10, 25, 60, 160))
        dr.text((tx, ty), label, font=font, fill=fill)
    return items


def draw_header(canvas: Image.Image, font_hdr: ImageFont.ImageFont) -> None:
    # Title chip near top-left of content
    title = "SYSTEM SETTING"
    x, y = OPTION_FRAME["x"] + 24, OPTION_FRAME["y"] + 18
    dr = ImageDraw.Draw(canvas)
    bb = dr.textbbox((0, 0), title, font=font_hdr)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 10
    dr.rounded_rectangle(
        (x - pad, y - 4, x + tw + pad, y + th + 6),
        radius=6,
        fill=(15, 25, 50, 210),
        outline=(230, 240, 255, 255),
        width=2,
    )
    dr.text((x, y), title, font=font_hdr, fill=(255, 255, 255, 255))


def draw_footer(canvas: Image.Image, font: ImageFont.ImageFont) -> list[dict]:
    """Bottom command hotspots: reset / title / back."""
    labels = [("init", "初始化"), ("title", "标题"), ("back", "返回")]
    fx = OPTION_FRAME["x"] + OPTION_FRAME["w"] - 24
    y = OPTION_FRAME["y"] + OPTION_FRAME["h"] - 56
    bw, bh = 140, 40
    gap = 16
    out = []
    dr = ImageDraw.Draw(canvas)
    for i, (fid, lab) in enumerate(reversed(labels)):
        x = fx - (i + 1) * (bw + gap)
        chip = make_chip(bw, bh, on=False)
        paste(canvas, chip, x, y)
        bb = dr.textbbox((0, 0), lab, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        dr.text((x + (bw - tw) // 2, y + (bh - th) // 2 - 1), lab, font=font, fill=(245, 250, 255, 255))
        out.append({"id": fid, "label": lab, "x": x, "y": y, "w": bw, "h": bh})
    return out


def bake_plate(tid: str, tab_index: int, font: ImageFont.ImageFont, font_sm: ImageFont.ImageFont, font_hdr: ImageFont.ImageFont, font_tab: ImageFont.ImageFont) -> tuple[Image.Image, list[dict], list[dict], list[dict]]:
    bg = Image.open(TLG / "option__bg0.png").convert("RGBA")
    canvas = bg.copy()
    tab_items = draw_tab_strip(canvas, tab_index, font_tab)
    draw_header(canvas, font_hdr)
    footer = draw_footer(canvas, font_sm)

    slots = layout_rows(tid)
    label_bar = None
    for item in slots:
        lr = item["label_rect"]
        if label_bar is None or label_bar.size[0] != lr["w"]:
            label_bar = make_label_bar(lr["w"], lr["h"])
        paste(canvas, label_bar, lr["x"], lr["y"])
        dr = ImageDraw.Draw(canvas)
        text = item["label"]
        bb = dr.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        # ribbon 左端有翼饰，文字略偏右并垂直居中
        tx = lr["x"] + 56
        ty = lr["y"] + max(4, (lr["h"] - th) // 2)
        dr.text((tx + 1, ty + 1), text, font=font, fill=(10, 20, 50, 140))
        dr.text((tx, ty), text, font=font, fill=(240, 248, 255, 255))

        if item["type"] == "slider":
            tr = item["track"]
            paste_fit(canvas, make_slider_track(tr["w"], tr["h"]), tr["x"], tr["y"], tr["w"], tr["h"])
        # toggle/choice/dialog：chip 由 Ren'Py 运行时叠，避免与 plate 双重绘制

    return canvas, slots, tab_items, footer


def export_chrome(chrome_dir: Path) -> None:
    ensure(chrome_dir)
    # check icons
    for name, idx, on in (("check_off", 4, False), ("check_on", 6, True)):
        spr = load_slice("option__pack", idx)
        if spr:
            spr.save(chrome_dir / f"{name}.png")
    # synthetic chips / knob for runtime
    for name, on in (("chip_off", False), ("chip_on", True)):
        make_chip(280, 46, on=on).save(chrome_dir / f"{name}.png")
    for name, on in (("chip4_off", False), ("chip4_on", True)):
        make_chip(208, 46, on=on).save(chrome_dir / f"{name}.png")
    make_chip(208, 46, on=False).save(chrome_dir / "chip_over.png")
    make_chip(208, 46, on=False).save(chrome_dir / "chip4_over.png")
    # slider knob
    knob = Image.new("RGBA", (50, 38), (0, 0, 0, 0))
    dr = ImageDraw.Draw(knob)
    dr.ellipse((4, 2, 45, 35), fill=(230, 245, 255, 255), outline=(40, 80, 160, 255), width=2)
    knob.save(chrome_dir / "slider_knob.png")
    knob2 = knob.copy()
    dr2 = ImageDraw.Draw(knob2)
    dr2.ellipse((4, 2, 45, 35), fill=(255, 255, 255, 255), outline=(80, 140, 220, 255), width=2)
    knob2.save(chrome_dir / "slider_knob_over.png")
    num = Image.new("RGBA", (66, 27), (20, 40, 80, 200))
    ImageDraw.Draw(num).rounded_rectangle((0, 0, 65, 26), radius=6, outline=(200, 220, 255, 255))
    num.save(chrome_dir / "slider_num.png")


def main() -> None:
    out = ensure(PREV)
    plates = ensure(out / "plates")
    chrome = ensure(out / "chrome")
    export_chrome(chrome)

    font = load_font(22)
    font_sm = load_font(17)
    font_hdr = load_font(20)
    font_tab = load_font(16)

    meta_tabs = []
    tab_items = []
    interaction: dict[str, list] = {}
    footer_meta = []

    for i, (tid, label) in enumerate(PAGE_ORDER):
        canvas, slots, titems, footer = bake_plate(tid, i, font, font_sm, font_hdr, font_tab)
        if i == 0:
            tab_items = titems
            footer_meta = footer
        fname = f"plates/tab_{tid}.png"
        canvas.save(out / fname)
        canvas.save(plates / f"tab_{tid}.png")
        meta_tabs.append({"id": tid, "label": label, "plate": fname})
        # normalize hotspots for Ren'Py
        hs = []
        for s in slots:
            h = {
                "key": s["key"],
                "label": s["label"],
                "type": s["type"],
                "x": s["x"],
                "y": s["y"],
                "w": s["w"],
                "h": s["h"],
                "default": 1 if s["type"] in ("dialog_onoff",) else (0.55 if s["type"] == "slider" else 0),
            }
            if s.get("options"):
                h["options"] = s["options"]
            if s.get("track"):
                h["track"] = s["track"]
            if s.get("num"):
                h["num"] = s["num"]
            if s.get("chips"):
                h["chips"] = s["chips"]
                h["chip_n"] = len(s["chips"])
            if s.get("on"):
                h["on"] = s["on"]
            if s.get("off"):
                h["off"] = s["off"]
            hs.append(h)
        interaction[tid] = hs
        print(f"tab_{tid}: {len(hs)} slots")

    shutil.copy2(plates / "tab_0.png", out / "chassis.png")
    shutil.copy2(TLG / "option__bg0.png", out / "bg.png")

    meta = {
        "family": "settings",
        "frame": OPTION_FRAME,
        "tabs": meta_tabs,
        "tabs_layout": {"items": tab_items},
        "footer": footer_meta,
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "help_box": {"x": 120, "y": 980, "w": 700, "h": 48},
        "note": "Cafe-style slot bake (no atlas dump); chrome+CN labels",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "interaction_slots.json").write_text(
        json.dumps(interaction, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # sync to renpy
    dst = ensure(RENPY)
    for src in out.rglob("*"):
        if src.is_file():
            rel = src.relative_to(out)
            d = dst / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, d)
    print("synced ->", dst)
    print("unique plates", len({(plates / f"tab_{t}.png").read_bytes() for t, _ in PAGE_ORDER}))


if __name__ == "__main__":
    main()
