# -*- coding: utf-8 -*-
"""Bake Angelic 全部 UI（除去剧情）→ ui-preview → renpy-angelic。

仿 CafeStella→renpy-cafe 流水线，但只用 Angelic 素材/几何，不抄 Cafe 坐标。
排除：scenario 剧本、剧情配音资源；保留 UI chrome（含 voicebar / 鉴赏入口）。
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
PBD = ROOT / "docs/ui-extract/pixel-reverse/pbd-layers"
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
PREV = ROOT / "ui-preview/assets"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic"
MANIFEST = ROOT / "docs/ui-extract/pixel-reverse/_ui_all_manifest.json"

# screen family → asset stems (bg0 / pack). No scenario.
FAMILIES = {
    "settings": {
        "bg": "option__bg0",
        "packs": [
            "option__pack",
            "option_4text__pack",
            "option_5sound1__pack",
            "option_5sound2__pack",
            "option_6dialog__pack",
            "option_7mouse__pack",
            "option_8keyboard1__pack",
            "option_9gamepad__pack",
            "option_9gamepad2_assign__pack",
            "option_cmds__pack",
            "option_keyinput__pack",
        ],
    },
    "file": {
        "modes": {
            "load": ("file_load__bg0", "file_load__pack"),
            "save": ("file_save__bg0", "file_save__pack"),
            "quick": ("file_quick__bg0", "file_quick__pack"),
        },
        "shared_packs": ["file__pack"],
    },
    "flowchart": {"bg": "scnchart__bg0", "packs": ["scnchart__pack"]},
    "cg": {
        "bg": "extra__bg0",
        "packs": [
            "extra__pack",
            "extra_locale_cn__pack",
            "extra_cg__pack",
            "extra_cgscene__pack",
            "extra_cgview__pack",
            "extra_scene__pack",
            "extra_stand__bg0",
            "extra_stand__pack",
            "extra_stand_dialog__bg0",
            "extra_stand_dialog__pack",
            "extra_voice__pack",
        ],
    },
    "qconf": {
        "packs": [
            "qconf__pack",
            "qconf_load__bg0",
            "qconf_qload__bg0",
            "qconf_qvsave__bg0",
            "qconf_save__bg0",
            "qconf_text__bg0",
            "qconf_volume__bg0",
        ],
    },
    "hud": {
        "packs": [
            "window__pack",
            "window_h__pack",
            "window__bg0",
            "window_h__bg0",
            "quickmenu__bg0",
            "quickmenu__pack",
            "qlpopup__bg0",
            "qlpopup__pack",
            "qvpopup__pack",
            "backlog__bg0",
            "backlog__pack",
            "select__pack",
            "dialog__bg0",
            "dialog__pack",
            "clickglyph_img__pack",
            "autoskipmark_img__pack",
            "voicebar__pack",
            "btncustom__pack",
            "chapter__bg0",
            "bgmtitle__bg0",
        ],
    },
    "touch": {
        "packs": [
            "touchuibar__bg0",
            "touchuibar__pack",
            "touchvolume__bg0",
            "touchvolume__pack",
        ],
    },
    "phonechat": {"bg": "phonechat__bg0", "packs": ["phonechat__pack"]},
    "afterstory": {"bg": "afterstory__bg0", "packs": ["afterstory__pack"]},
    "langselect": {"packs": ["langselect__pack"]},
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
            elif r <= 12 and g <= 12 and b <= 12 and a > 200:
                px[x, y] = (0, 0, 0, 0)
    return im


def load_stem(stem: str) -> Image.Image | None:
    p = TLG / f"{stem}.png"
    if not p.exists():
        return None
    return Image.open(p).convert("RGBA")


def crop_1080(im: Image.Image) -> Image.Image:
    if im.size == (1920, 1080):
        return im
    w, h = im.size
    if w != 1920:
        nh = int(1920 * h / w)
        im = im.resize((1920, nh), Image.Resampling.LANCZOS)
        w, h = im.size
    if h == 1080:
        return im
    top = max(0, (h - 1080) // 2)
    return im.crop((0, top, 1920, min(h, top + 1080)))


def paste_pack(bg: Image.Image, pack: Image.Image) -> Image.Image:
    out = bg.copy()
    pack = magenta_to_alpha(pack)
    if pack.size == out.size:
        out.alpha_composite(pack)
        return out
    if pack.width <= out.width and pack.height <= out.height:
        x = max(0, (out.width - pack.width) // 2)
        y = max(0, (out.height - pack.height) // 2)
        out.alpha_composite(pack, (x, y))
        return out
    # oversized: top-left crop after optional width match
    if pack.width == 1920 and pack.height > 1080:
        pack = crop_1080(pack)
        if pack.size == out.size:
            out.alpha_composite(pack)
            return out
    out.alpha_composite(pack.crop((0, 0, min(out.width, pack.width), min(out.height, pack.height))))
    return out


def copy_hotspots(stem: str, dest: Path) -> None:
    for suffix in (".hotspots.json", ".json"):
        src = PBD / f"{stem}{suffix}" if suffix == ".json" else PBD / f"{stem}.hotspots.json"
        if src.exists() and "hotspots" in src.name or (suffix == ".hotspots.json" and src.exists()):
            if src.exists():
                shutil.copy2(src, dest / src.name)
                return
    hs = PBD / f"{stem}.hotspots.json"
    if hs.exists():
        shutil.copy2(hs, dest / hs.name)


def save_rgba(im: Image.Image, path: Path) -> None:
    ensure(path.parent)
    im.convert("RGBA").save(path)


def bake_family_simple(name: str, spec: dict) -> dict:
    out = ensure(PREV / name)
    used = []
    bg_stem = spec.get("bg")
    packs = list(spec.get("packs") or [])
    bg = load_stem(bg_stem) if bg_stem else None
    if bg is not None:
        bg = crop_1080(bg) if bg.size != (1920, 1080) and bg.width == 1920 else bg
        if bg.width == 1920 and bg.height != 1080:
            bg = crop_1080(bg)
        save_rgba(bg, out / "bg.png")
        used.append(bg_stem)
        comp = bg.copy()
    else:
        comp = Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))

    pack_dir = ensure(out / "packs")
    for stem in packs:
        im = load_stem(stem)
        if im is None:
            continue
        alpha = magenta_to_alpha(im)
        save_rgba(alpha, pack_dir / f"{stem}.png")
        used.append(stem)
        if bg is not None and (alpha.width <= 1920 and alpha.height <= 1080 or alpha.size == comp.size):
            # only auto-composite full-frame or smaller chrome onto bg
            if alpha.size == (1920, 1080) or (alpha.width == 1920 and alpha.height >= 1080):
                a2 = crop_1080(alpha) if alpha.height != 1080 else alpha
                if a2.size == comp.size:
                    comp.alpha_composite(a2)
            elif stem.endswith("__pack") and alpha.width < 1920:
                # keep as loose pack; chassis uses first main pack
                pass
        copy_hotspots(stem.replace("__pack", "").replace("__bg0", ""), out)

    # primary composite: bg + first pack if fits
    if bg is not None and packs:
        first = load_stem(packs[0])
        if first is not None:
            save_rgba(paste_pack(bg if bg.size == (1920, 1080) else crop_1080(bg), first), out / "composite.png")
        else:
            save_rgba(comp if comp.size == (1920, 1080) else crop_1080(comp), out / "composite.png")
    else:
        save_rgba(comp if comp.size[0] else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255)), out / "view.png")

    meta = {
        "family": name,
        "used": used,
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "exclude_story": True,
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta


def bake_settings() -> dict:
    out = ensure(PREV / "settings")
    plates = ensure(out / "plates")
    bg = load_stem("option__bg0")
    assert bg is not None
    save_rgba(bg, out / "bg.png")
    used = ["option__bg0"]
    tab_map = [
        ("0", "option__pack", "基本设置"),
        ("4", "option_4text__pack", "文本设置"),
        ("5a", "option_5sound1__pack", "音频1"),
        ("5b", "option_5sound2__pack", "音频2"),
        ("6", "option_6dialog__pack", "确认信息"),
        ("7", "option_7mouse__pack", "鼠标"),
        ("8", "option_8keyboard1__pack", "键盘"),
        ("9", "option_9gamepad__pack", "手柄"),
    ]
    tabs = []
    for tid, stem, label in tab_map:
        p = load_stem(stem)
        if not p:
            continue
        alpha = magenta_to_alpha(p)
        save_rgba(alpha, out / f"{stem}.png")
        plate = paste_pack(bg, p)
        save_rgba(plate, plates / f"tab_{tid}.png")
        used.append(stem)
        tabs.append({"id": tid, "label": label, "plate": f"plates/tab_{tid}.png"})
    # chassis = first plate
    if tabs:
        shutil.copy2(plates / f"tab_{tabs[0]['id']}.png", out / "chassis.png")
    for extra in ("option_cmds__pack", "option_keyinput__pack", "option_9gamepad2_assign__pack"):
        p = load_stem(extra)
        if p:
            save_rgba(magenta_to_alpha(p), out / f"{extra}.png")
            used.append(extra)
    copy_hotspots("option", out)
    meta = {
        "family": "settings",
        "tabs": tabs
        + [
            {"id": "1", "label": "画面设置", "plate": "plates/tab_0.png"},
            {"id": "2", "label": "游戏设置1", "plate": "plates/tab_0.png"},
            {"id": "3", "label": "游戏设置2", "plate": "plates/tab_0.png"},
        ],
        "used": used,
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
    }
    # stable order: put numeric-ish first
    meta["tabs"] = sorted(meta["tabs"], key=lambda t: str(t["id"]))
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("settings", len(tabs), "plates")
    return meta


def bake_file() -> dict:
    out = ensure(PREV / "file")
    modes_meta = []
    used = ["file__pack"]
    shared = load_stem("file__pack")
    if shared:
        save_rgba(magenta_to_alpha(shared), out / "file__pack.png")
    for mode, (bg_s, pack_s) in FAMILIES["file"]["modes"].items():
        bg = load_stem(bg_s)
        pack = load_stem(pack_s)
        if bg is None:
            continue
        save_rgba(bg, out / f"bg_{mode}.png")
        used.append(bg_s)
        if pack:
            save_rgba(magenta_to_alpha(pack), out / f"pack_{mode}.png")
            save_rgba(paste_pack(bg, pack), out / f"composite_{mode}.png")
            used.append(pack_s)
        else:
            save_rgba(bg, out / f"composite_{mode}.png")
        copy_hotspots(f"file_{mode}", out)
        # Angelic-ish slot grid (not Cafe coords): 4x3 starting mid-left
        slots = []
        for i in range(12):
            col, row = i % 4, i // 4
            slots.append(
                {
                    "index": i,
                    "x": 120 + col * 300,
                    "y": 180 + row * 220,
                    "w": 280,
                    "h": 200,
                }
            )
        modes_meta.append(
            {
                "id": mode,
                "label": {"load": "读档", "save": "存档", "quick": "快速"}.get(mode, mode),
                "composite": f"composite_{mode}.png",
                "bg": f"bg_{mode}.png",
            }
        )
    # mode tabs along top (Angelic header style estimate)
    mode_tabs = [
        {"id": "save", "x": 80, "y": 40, "w": 160, "h": 48},
        {"id": "load", "x": 260, "y": 40, "w": 160, "h": 48},
        {"id": "quick", "x": 440, "y": 40, "w": 160, "h": 48},
    ]
    meta = {
        "family": "file",
        "modes": modes_meta,
        "mode_tabs": mode_tabs,
        "slots": slots if modes_meta else [],
        "page_size": 12,
        "used": used,
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "layout_note": "Slot grid estimated for Angelic; refine from PBD/runtime dump later",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    # also mirror load composite for legacy path
    load_out = ensure(PREV / "load")
    if (out / "composite_load.png").exists():
        shutil.copy2(out / "composite_load.png", load_out / "composite.png")
        shutil.copy2(out / "bg_load.png", load_out / "bg.png")
        shutil.copy2(out / "meta.json", load_out / "meta.json")
    print("file modes", [m["id"] for m in modes_meta])
    return meta


def bake_qconf() -> dict:
    out = ensure(PREV / "qconf")
    used = []
    for stem in FAMILIES["qconf"]["packs"]:
        im = load_stem(stem)
        if not im:
            continue
        save_rgba(magenta_to_alpha(im) if "pack" in stem else im, out / f"{stem}.png")
        used.append(stem)
        copy_hotspots(stem.replace("__bg0", "").replace("__pack", ""), out)
    meta = {
        "family": "qconf",
        "dialogs": [
            {"id": "save", "image": "qconf_save__bg0.png"},
            {"id": "load", "image": "qconf_load__bg0.png"},
            {"id": "qload", "image": "qconf_qload__bg0.png"},
            {"id": "qvsave", "image": "qconf_qvsave__bg0.png"},
            {"id": "text", "image": "qconf_text__bg0.png"},
            {"id": "volume", "image": "qconf_volume__bg0.png"},
            {"id": "pack", "image": "qconf__pack.png"},
        ],
        "used": used,
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("qconf", len(used))
    return meta


def bake_title_extras() -> None:
    """Ensure title packs staged; full title bake is build_title_1to1.py."""
    out = ensure(PREV / "title")
    for stem in ("title__pack", "title_locale_cn__pack", "langselect__pack"):
        im = load_stem(stem)
        if im:
            save_rgba(magenta_to_alpha(im), out / f"{stem}.png")


def sync_all() -> list[str]:
    synced = []
    names = [
        "settings",
        "file",
        "load",
        "flowchart",
        "cg",
        "qconf",
        "hud",
        "touch",
        "phonechat",
        "afterstory",
        "langselect",
        "title",
        "packs",
        "hotspots",
        "locale",
    ]
    # packs dump
    packs = ensure(PREV / "packs")
    for p in TLG.glob("*.png"):
        shutil.copy2(p, packs / p.name)
    for name in names:
        src = PREV / name
        if not src.exists():
            continue
        dst = RENPY / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        synced.append(name)
        print("synced", name)
    return synced


def main() -> None:
    ensure(PREV)
    ensure(RENPY)
    report = {"exclude": ["scenario", "story_voice_assets"], "families": {}}

    bake_title_extras()
    report["families"]["settings"] = bake_settings()
    report["families"]["file"] = bake_file()
    report["families"]["flowchart"] = bake_family_simple("flowchart", FAMILIES["flowchart"])
    report["families"]["cg"] = bake_family_simple("cg", FAMILIES["cg"])
    # prefer oracle view_state if present
    oracle = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture/measure/extra_oracle_clean_1080.png"
    if oracle.exists():
        shutil.copy2(oracle, PREV / "cg" / "view_state.png")
    report["families"]["qconf"] = bake_qconf()
    for name in ("hud", "touch", "phonechat", "afterstory", "langselect"):
        report["families"][name] = bake_family_simple(name, FAMILIES[name])

    # fonts / locale from filtered (UI only)
    for sub in ("font", "locale"):
        src = FILT / sub
        if src.exists():
            dst = ensure(PREV / sub)
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)

    synced = sync_all()
    report["synced"] = synced
    report["tlg_pack_count"] = len(list(TLG.glob("*.png")))
    MANIFEST.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE packs", report["tlg_pack_count"], "synced", synced)


if __name__ == "__main__":
    main()
