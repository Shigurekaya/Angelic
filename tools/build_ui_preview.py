# -*- coding: utf-8 -*-
"""
Angelic-only UI preview builder.
Sources: docs/ui-extract (filtered-cn-jp + pixel-reverse) + tools reverse outputs.
Does NOT share layout with CafeStella.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(r"D:\gamedev\Angelic")
SRC = ROOT / "docs" / "ui-extract"
FILT = SRC / "ui-cn-jp-static" / "filtered-cn-jp"
TLG = SRC / "pixel-reverse" / "tlg-png"
PBD = SRC / "pixel-reverse" / "pbd-layers"
OUT = ROOT / "ui-preview"
A = OUT / "assets"


def chroma(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (r, g, b, 0)
    return im


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_uitexts() -> dict:
    candidates = [
        FILT / "locale" / "cn" / "uitexts_cn.toml",
        SRC / "locale" / "cn" / "uitexts_cn.toml",
    ]
    for p in candidates:
        if p.exists():
            raw = p.read_bytes()
            enc = "utf-16-le" if raw[:2] == b"\xff\xfe" else ("utf-16-be" if raw[:2] == b"\xfe\xff" else "utf-8")
            out = {}
            for line in raw.decode(enc, errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"')
            return out
    return {}


def stage_assets():
    if A.exists():
        # keep _mtn outside assets
        for child in list(A.iterdir()):
            if child.name == "ref":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    for sub in ["title", "settings", "load", "flowchart", "cg", "locale", "hotspots", "packs"]:
        ensure(A / sub)

    # title backgrounds
    for i in range(8):
        src = FILT / f"title_bg{i}.png"
        if src.exists():
            shutil.copy2(src, A / "title" / f"bg{i}.png")
    logo = FILT / "locale" / "cn" / "title_logo_cn.png"
    if logo.exists():
        shutil.copy2(logo, A / "title" / "logo_cn.png")

    # packs
    for f in TLG.glob("*.png"):
        shutil.copy2(f, A / "packs" / f.name)

    # locale
    locale_dirs = [FILT / "locale" / "cn", SRC / "locale" / "cn"]
    for locdir in locale_dirs:
        if not locdir.exists():
            continue
        for f in locdir.iterdir():
            if f.is_file():
                shutil.copy2(f, A / "locale" / f.name)

    # hotspots
    for f in PBD.glob("*.hotspots.json"):
        shutil.copy2(f, A / "hotspots" / f.name)

    # settings bg + packs
    Image.open(A / "packs" / "option__bg0.png").convert("RGBA").save(A / "settings" / "bg.png")
    for name in [
        "option__pack.png",
        "option_4text__pack.png",
        "option_5sound1__pack.png",
        "option_5sound2__pack.png",
        "option_6dialog__pack.png",
        "option_7mouse__pack.png",
        "option_8keyboard1__pack.png",
        "option_9gamepad__pack.png",
    ]:
        p = A / "packs" / name
        if p.exists():
            chroma(Image.open(p)).save(A / "settings" / name)

    # load / flowchart / cg
    Image.open(A / "packs" / "file_load__bg0.png").convert("RGBA").save(A / "load" / "bg.png")
    chroma(Image.open(A / "packs" / "file_load__pack.png")).save(A / "load" / "pack.png")

    fc = Image.open(A / "packs" / "scnchart__bg0.png").convert("RGBA")
    fc2 = fc.resize((1920, int(1920 * fc.height / fc.width)), Image.Resampling.LANCZOS)
    top = max(0, (fc2.height - 1080) // 2)
    fc2.crop((0, top, 1920, top + 1080)).save(A / "flowchart" / "bg.png")
    chroma(Image.open(A / "packs" / "scnchart__pack.png")).save(A / "flowchart" / "pack.png")

    Image.open(A / "packs" / "extra__bg0.png").convert("RGBA").save(A / "cg" / "bg.png")
    for name in ["extra__pack.png", "extra_locale_cn__pack.png", "extra_cg__pack.png", "extra_cgview__pack.png"]:
        p = A / "packs" / name
        if p.exists():
            chroma(Image.open(p)).save(A / "cg" / name)

    # default title composite for first paint (bg0 + logo)
    title = Image.open(A / "title" / "bg0.png").convert("RGBA")
    logo_im = Image.open(A / "title" / "logo_cn.png").convert("RGBA")
    lw = min(640, logo_im.width)
    logo_im = logo_im.resize((lw, int(logo_im.height * lw / logo_im.width)), Image.Resampling.LANCZOS)
    title.alpha_composite(logo_im, (36, 36))
    title.save(A / "title" / "composite.png")


def option_rows(stem: str, labels: dict, limit: int = 14) -> list:
    hs = A / "hotspots" / f"{stem}.hotspots.json"
    if not hs.exists():
        return []
    doc = json.loads(hs.read_text(encoding="utf-8"))
    rows = []
    seen = set()
    key_cn = {
        "fullscreen": "画面尺寸",
        "sqscr": "画面比例",
        "textspeed": "文本速度",
        "autospeed": "自动速度",
        "skipall": "未读跳过",
        "wave": "主音量",
        "bgm": "BGM",
        "se": "音效",
        "voice": "语音",
        "movie": "影片",
        "ask_load": labels.get("config_label_ask_load", "读档确认"),
        "ask_exit": labels.get("config_label_ask_exit", "退出确认"),
        "ask_title": labels.get("config_label_ask_title", "回标题确认"),
        "ask_flow": labels.get("config_label_ask_flow", "流程图跳转确认"),
    }
    for b in doc.get("bindings") or []:
        lid = b.get("layer_id") or ""
        if not lid or lid in seen:
            continue
        seen.add(lid)
        low = lid.lower()
        typ = "button"
        if any(x in low for x in ("speed", "volume", "wave", "bgm", "se", "voice", "movie")):
            typ = "slider"
        elif "toggle" in str(b.get("bindings")) or low in key_cn or low.startswith("ask_"):
            typ = "toggle"
        rows.append(
            {
                "key": lid,
                "label": key_cn.get(lid, labels.get(f"config_label_{lid}", lid)),
                "type": typ,
                "bindings": b.get("bindings") or [],
            }
        )
        if len(rows) >= limit:
            break
    return rows


def build_data(labels: dict) -> dict:
    pack_map = {
        "0": None,
        "1": None,
        "2": None,
        "3": None,
        "4": "option_4text__pack.png",
        "5": "option_5sound1__pack.png",
        "6": "option_6dialog__pack.png",
        "7": "option_7mouse__pack.png",
        "8": "option_8keyboard1__pack.png",
        "9": "option_9gamepad__pack.png",
    }
    tabs_meta = [
        ("0", "基本设置", "option_0simple"),
        ("1", "画面设置", "option_1display"),
        ("2", "游戏设置1", "option_2game1"),
        ("3", "游戏设置2", "option_3game2"),
        ("4", "文本设置", "option_4text"),
        ("5", "音频设置", "option_5sound1"),
        ("6", "确认信息", "option_6dialog"),
        ("7", "鼠标", "option_7mouse"),
        ("8", "键盘", "option_8keyboard1"),
        ("9", "游戏手柄", "option_9gamepad"),
    ]
    tabs = []
    for tid, label, stem in tabs_meta:
        pack = pack_map.get(tid)
        tabs.append(
            {
                "id": tid,
                "label": label,
                "rows": option_rows(stem, labels),
                "pack": f"assets/settings/{pack}" if pack and (A / "settings" / pack).exists() else None,
                "hotspots_file": f"assets/hotspots/{stem}.hotspots.json",
            }
        )

    # CG list from csv if present
    cg_items = []
    cglist = FILT / "main" / "cglist.csv"
    if cglist.exists():
        raw = cglist.read_bytes()
        text = raw.decode("utf-16-le" if raw[:2] == b"\xff\xfe" else "utf-8", errors="replace")
        for i, line in enumerate(text.splitlines()):
            if i == 0 or not line.strip():
                continue
            parts = [c.strip() for c in line.split(",")]
            if parts:
                cg_items.append(parts[0] or f"CG {i}")
            if len(cg_items) >= 16:
                break
    if not cg_items:
        cg_items = [labels.get("extra_label_cg", "ＣＧ欣赏") + f" {i:02d}" for i in range(1, 13)]

    return {
        "game": "天使☆嚣嚣 RE-BOOT!",
        "engine": "Angelic",
        "layout": "angelic-bottom-menu",
        "resolution": {"width": 1920, "height": 1080},
        "title": {
            "style": "bottom-bar",
            "bg": "assets/title/bg0.png",
            "logo": "assets/title/logo_cn.png",
            "logo_pos": {"x": 36, "y": 36, "w": 640},
            "backgrounds": [
                {"index": i, "src": f"assets/title/bg{i}.png", "label": f"背景{i+1}"}
                for i in range(8)
                if (A / "title" / f"bg{i}.png").exists()
            ],
            "buttons": [
                {"id": "start", "label": "从头开始", "action": "start"},
                {"id": "continue", "label": "继续游戏", "action": "start"},
                {"id": "load", "label": "载入进度", "action": "load"},
                {"id": "flowchart", "label": labels.get("common_game_flowchart", "流程图"), "action": "flowchart"},
                {"id": "extra", "label": labels.get("config_sysvo_extra", "鉴赏模式"), "action": "cg"},
                {"id": "after", "label": labels.get("config_sysvo_after", "附加剧情"), "action": "toast"},
                {"id": "option", "label": labels.get("config_sysvo_option", "游戏设置"), "action": "settings"},
                {"id": "exit", "label": "退出游戏", "action": "toast"},
            ],
            "sources": ["title.ks", "uipsd/title.pbd", "image/title_bg*.png", "locale/cn/title_logo_cn.png"],
        },
        "settings": {
            "style": "option-shell",
            "bg": "assets/settings/bg.png",
            "chassis": "assets/settings/option__pack.png",
            "tabs": tabs,
            "help": "assets/locale/help_opt_cn.txt",
            "footer": {
                "back_title": labels.get("common_back_title", "标题画面"),
                "back_game": labels.get("common_back_game", "返回游戏"),
            },
            "sources": ["option.ks", "uipsd/option*.pbd", "locale/cn/help_opt_cn.txt", "uitexts_cn.toml"],
        },
        "load": {
            "style": "file-load",
            "bg": "assets/load/bg.png",
            "pack": "assets/load/pack.png",
            "title": labels.get("common_caps_load", "DATA LOAD"),
            "slots": 12,
            "help": "assets/locale/help_file_cn.txt",
            "sources": ["load.ks", "uipsd/file_load.pbd", "main/savelist.csv"],
        },
        "flowchart": {
            "style": "scnchart",
            "bg": "assets/flowchart/bg.png",
            "pack": "assets/flowchart/pack.png",
            "title": labels.get("common_game_flowchart", "流程图"),
            "nodes": ["序章", "第1章", "第2章", "第3章", "第4章", "终章", "After", "返回标题"],
            "help": "assets/locale/help_flow_cn.txt",
            "sources": ["scnchart.ks", "uipsd/scnchart.pbd", "main/scnchartdata.tjs"],
        },
        "cg": {
            "style": "extra-cg",
            "bg": "assets/cg/bg.png",
            "pack": "assets/cg/extra_locale_cn__pack.png"
            if (A / "cg" / "extra_locale_cn__pack.png").exists()
            else "assets/cg/extra__pack.png",
            "title": labels.get("extra_label_cg", "ＣＧ欣赏"),
            "items": cg_items,
            "help": "assets/locale/help_extra_cn.txt",
            "sources": ["uipsd/extra_cg*.pbd", "main/cglist.csv", "locale/cn/help_extra_cn.txt"],
        },
        "manifest": {
            "packs": len(list((A / "packs").glob("*.png"))),
            "hotspots": len(list((A / "hotspots").glob("*.json"))),
            "title_bgs": len(list((A / "title").glob("bg*.png"))),
            "locale": len(list((A / "locale").glob("*"))),
        },
    }


def write_preview_files(data: dict):
    (OUT / "data.js").write_text(
        "window.UI_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    (OUT / "ASSET-MANIFEST.json").write_text(
        json.dumps(data["manifest"], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main():
    ensure(OUT)
    stage_assets()
    labels = read_uitexts()
    data = build_data(labels)
    write_preview_files(data)
    print("ANGELIC preview built", data["manifest"])


if __name__ == "__main__":
    main()
