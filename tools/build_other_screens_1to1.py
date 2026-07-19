# -*- coding: utf-8 -*-
"""Bake Angelic settings/load/flowchart/cg plates into ui-preview + renpy."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
PBD = ROOT / "docs/ui-extract/pixel-reverse/pbd-layers"
PREV = ROOT / "ui-preview/assets"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic"


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


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_tlg(name: str) -> Image.Image | None:
    p = TLG / name
    if not p.exists():
        return None
    return Image.open(p).convert("RGBA")


def paste_pack(bg: Image.Image, pack: Image.Image | None) -> Image.Image:
    out = bg.copy()
    if pack is None:
        return out
    pack = magenta_to_alpha(pack)
    # center if smaller
    x = max(0, (out.width - pack.width) // 2)
    y = max(0, (out.height - pack.height) // 2)
    if pack.width <= out.width and pack.height <= out.height:
        out.alpha_composite(pack, (x, y))
    else:
        # top-left crop
        out.alpha_composite(pack.crop((0, 0, out.width, out.height)), (0, 0))
    return out


def crop_1080(im: Image.Image) -> Image.Image:
    if im.size == (1920, 1080):
        return im
    w, h = im.size
    if w != 1920:
        nh = int(1920 * h / w)
        im = im.resize((1920, nh), Image.Resampling.LANCZOS)
        w, h = im.size
    top = max(0, (h - 1080) // 2)
    return im.crop((0, top, 1920, top + 1080))


def copy_hotspots(stem: str, dest: Path) -> None:
    src = PBD / f"{stem}.hotspots.json"
    if src.exists():
        shutil.copy2(src, dest / f"{stem}.hotspots.json")


def bake_settings() -> None:
    out = ensure(PREV / "settings")
    plates = ensure(out / "plates")
    bg = load_tlg("option__bg0.png")
    if bg is None:
        raise SystemExit("missing option__bg0.png")
    bg.save(out / "bg.png")
    pack = load_tlg("option__pack.png")
    if pack:
        magenta_to_alpha(pack).save(out / "option__pack.png")
        paste_pack(bg, pack).save(out / "chassis.png")
    else:
        bg.save(out / "chassis.png")

    tab_packs = [
        ("0", "option__pack.png"),
        ("4", "option_4text__pack.png"),
        ("5a", "option_5sound1__pack.png"),
        ("5b", "option_5sound2__pack.png"),
        ("6", "option_6dialog__pack.png"),
        ("7", "option_7mouse__pack.png"),
        ("8", "option_8keyboard1__pack.png"),
        ("9", "option_9gamepad__pack.png"),
    ]
    for tab, name in tab_packs:
        p = load_tlg(name)
        if not p:
            continue
        alpha = magenta_to_alpha(p)
        alpha.save(out / name)
        plate = paste_pack(bg, p)
        plate.save(plates / f"tab_{tab}.png")

    # default plate
    shutil.copy2(out / "chassis.png", plates / "tab_0.png")
    copy_hotspots("option", out)
    copy_hotspots("option_0simple", out)
    meta = {
        "tabs": [
            {"id": "0", "label": "基本设置", "plate": "plates/tab_0.png"},
            {"id": "1", "label": "画面设置", "plate": "plates/tab_0.png"},
            {"id": "2", "label": "游戏设置1", "plate": "plates/tab_0.png"},
            {"id": "3", "label": "游戏设置2", "plate": "plates/tab_0.png"},
            {"id": "4", "label": "文本设置", "plate": "plates/tab_4.png"},
            {"id": "5", "label": "音频设置", "plate": "plates/tab_5a.png"},
            {"id": "6", "label": "确认信息", "plate": "plates/tab_6.png"},
            {"id": "7", "label": "鼠标", "plate": "plates/tab_7.png"},
            {"id": "8", "label": "键盘", "plate": "plates/tab_8.png"},
            {"id": "9", "label": "游戏手柄", "plate": "plates/tab_9.png"},
        ],
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("settings ok")


def bake_load() -> None:
    out = ensure(PREV / "load")
    bg = load_tlg("file_load__bg0.png")
    pack = load_tlg("file_load__pack.png")
    if bg is None:
        raise SystemExit("missing file_load__bg0")
    bg.save(out / "bg.png")
    if pack:
        magenta_to_alpha(pack).save(out / "pack.png")
        paste_pack(bg, pack).save(out / "composite.png")
    else:
        bg.save(out / "composite.png")
    copy_hotspots("file_load", out)
    meta = {"back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"}}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("load ok")


def bake_flowchart() -> None:
    out = ensure(PREV / "flowchart")
    bg = load_tlg("scnchart__bg0.png")
    pack = load_tlg("scnchart__pack.png")
    if bg is None:
        raise SystemExit("missing scnchart__bg0")
    bg1080 = crop_1080(bg)
    bg1080.save(out / "bg.png")
    if pack:
        alpha = magenta_to_alpha(pack)
        alpha.save(out / "pack.png")
        # pack may be full-res overlay; place top-left on cropped bg
        comp = bg1080.copy()
        if alpha.size != bg1080.size:
            # try center-crop pack similarly if tall
            if alpha.height > 1080 and alpha.width == 1920:
                alpha = crop_1080(alpha)
            else:
                # scale width
                if alpha.width != 1920:
                    nh = int(1920 * alpha.height / alpha.width)
                    alpha = alpha.resize((1920, nh), Image.Resampling.LANCZOS)
                    alpha = crop_1080(alpha) if alpha.height != 1080 else alpha
        if alpha.size == comp.size:
            comp.alpha_composite(alpha)
        else:
            comp.alpha_composite(alpha.crop((0, 0, min(comp.width, alpha.width), min(comp.height, alpha.height))))
        comp.save(out / "composite.png")
    else:
        bg1080.save(out / "composite.png")
    copy_hotspots("scnchart", out)
    meta = {"back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"}}
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("flowchart ok")


def bake_cg() -> None:
    out = ensure(PREV / "cg")
    bg = load_tlg("extra__bg0.png")
    if bg is None:
        raise SystemExit("missing extra__bg0")
    bg.save(out / "bg.png")
    comp = bg.copy()
    for name in ["extra__pack.png", "extra_locale_cn__pack.png", "extra_cg__pack.png"]:
        p = load_tlg(name)
        if not p:
            continue
        alpha = magenta_to_alpha(p)
        alpha.save(out / name)
        if alpha.size == comp.size:
            comp.alpha_composite(alpha)
        else:
            x = max(0, (comp.width - alpha.width) // 2)
            y = max(0, (comp.height - alpha.height) // 2)
            if alpha.width <= comp.width and alpha.height <= comp.height:
                comp.alpha_composite(alpha, (x, y))
    comp.save(out / "composite.png")
    copy_hotspots("extra", out)
    copy_hotspots("extra_cg", out)
    meta = {
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "mode": "cg",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("cg ok")


def sync_to_renpy() -> None:
    for name in ("settings", "load", "flowchart", "cg", "packs", "hotspots", "locale"):
        src = PREV / name
        if not src.exists():
            continue
        dst = RENPY / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print("synced", name)


def main() -> None:
    # also refresh packs folder
    packs = ensure(PREV / "packs")
    for p in TLG.glob("*.png"):
        shutil.copy2(p, packs / p.name)
    bake_settings()
    bake_load()
    bake_flowchart()
    bake_cg()
    sync_to_renpy()


if __name__ == "__main__":
    main()
