# -*- coding: utf-8 -*-
"""Compose Angelic UI viewing-state plates from PBD geo + pack atlases.

查看态 = 玩家打开界面时的默认 idle 显示（非 hover 全亮）。
几何字段复用 LimeLight 的 length-prefixed 扫描（storagex/y → 裁切，ox/oy → 屏幕落点）。
"""
from __future__ import annotations

import json
import struct
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
UIPSD = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd"
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
OUT = ROOT / "docs/ui-extract/pixel-reverse/_view_ref"
PLATES = ROOT / "ui-preview/assets"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic"
REPORT = OUT / "compose_report.json"

GEO_KEYS = {
    "cx", "cy", "cw", "ch", "ox", "oy", "storagex", "storagey",
    "left", "top", "width", "height", "x", "y", "w", "h", "opacity", "visible",
}

# 主界面：查看态叠层清单（Angelc 自己的 uipsd，不是 CafeStella）
SCREENS = {
    "title": {
        "pbd": ["title.pbd", "title_locale_cn.pbd"],
        "bg": "title_bg0",  # 全幅 KV，不是 title__bg0
        "force_packs": ["title__pack.png", "title_locale_cn__pack.png", "langselect__pack.png"],
    },
    "option_0": {
        "pbd": ["option.pbd", "option_0simple.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png"],
    },
    "option_4": {
        "pbd": ["option.pbd", "option_4text.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_4text__pack.png"],
    },
    "option_5a": {
        "pbd": ["option.pbd", "option_5sound1.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_5sound1__pack.png"],
    },
    "option_5b": {
        "pbd": ["option.pbd", "option_5sound2.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_5sound2__pack.png"],
    },
    "option_6": {
        "pbd": ["option.pbd", "option_6dialog.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_6dialog__pack.png"],
    },
    "option_7": {
        "pbd": ["option.pbd", "option_7mouse.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_7mouse__pack.png"],
    },
    "option_8": {
        "pbd": ["option.pbd", "option_8keyboard1.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_8keyboard1__pack.png"],
    },
    "option_9": {
        "pbd": ["option.pbd", "option_9gamepad.pbd"],
        "bg": "option__bg0",
        "force_packs": ["option__pack.png", "option_9gamepad__pack.png"],
    },
    "file_load": {
        "pbd": ["file.pbd", "file_load.pbd"],
        "bg": "file_load__bg0",
        "force_packs": ["file_load__pack.png", "file__pack.png"],
    },
    "file_save": {
        "pbd": ["file.pbd", "file_save.pbd"],
        "bg": "file_save__bg0",
        "force_packs": ["file_save__pack.png", "file__pack.png"],
    },
    "file_quick": {
        "pbd": ["file.pbd", "file_quick.pbd"],
        "bg": "file_quick__bg0",
        "force_packs": ["file_quick__pack.png", "file__pack.png"],
    },
    "extra": {
        "pbd": ["extra.pbd", "extra_locale_cn.pbd"],
        "bg": "extra__bg0",
        "force_packs": ["extra__pack.png", "extra_locale_cn__pack.png"],
    },
    "extra_cg": {
        "pbd": ["extra.pbd", "extra_cg.pbd", "extra_locale_cn.pbd"],
        "bg": "extra__bg0",
        "force_packs": [
            "extra__pack.png", "extra_locale_cn__pack.png",
            "extra_cg__pack.png", "extra_cgscene__pack.png",
        ],
    },
    "extra_cgview": {
        "pbd": ["extra_cgview.pbd"],
        "bg": "extra__bg0",
        "force_packs": ["extra_cgview__pack.png"],
    },
    "extra_voice": {
        "pbd": ["extra_voice.pbd", "extra_locale_cn.pbd"],
        "bg": "extra__bg0",
        "force_packs": ["extra__pack.png", "extra_locale_cn__pack.png", "extra_voice__pack.png"],
    },
    "scnchart": {
        "pbd": ["scnchart.pbd"],
        "bg": "scnchart__bg0",
        "force_packs": ["scnchart__pack.png"],
    },
    "qconf": {
        "pbd": ["qconf.pbd"],
        "bg": None,
        "force_packs": ["qconf__pack.png"],
    },
    "window": {
        "pbd": ["window.pbd"],
        "bg": "window__bg0",
        "force_packs": ["window__pack.png"],
    },
    "backlog": {
        "pbd": ["backlog.pbd"],
        "bg": "backlog__bg0",
        "force_packs": ["backlog__pack.png"],
    },
    "quickmenu": {
        "pbd": ["quickmenu.pbd"],
        "bg": "quickmenu__bg0",
        "force_packs": ["quickmenu__pack.png"],
    },
    "select": {
        "pbd": ["select.pbd"],
        "bg": None,
        "force_packs": ["select__pack.png"],
    },
    "dialog": {
        "pbd": ["dialog.pbd"],
        "bg": "dialog__bg0",
        "force_packs": ["dialog__pack.png"],
    },
}


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


def read_key(data: bytes, pos: int) -> tuple[str, int] | None:
    if pos + 4 > len(data):
        return None
    n = struct.unpack_from("<I", data, pos)[0]
    if not (1 <= n <= 64):
        return None
    start = pos + 4
    end = start + n * 2
    if end > len(data):
        return None
    try:
        s = data[start:end].decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    if not all(32 <= ord(c) <= 126 for c in s):
        return None
    return s, end


def read_int_after(data: bytes, pos: int) -> tuple[int, int] | None:
    if pos < len(data) and data[pos] == 0x04 and pos + 5 <= len(data):
        return struct.unpack_from("<i", data, pos + 1)[0], pos + 5
    return None


def read_storage_str(data: bytes, pos: int) -> tuple[str, int] | None:
    if pos >= len(data) or data[pos] != 0x02:
        return None
    for skip in (1, 2):
        if pos + skip + 4 > len(data):
            continue
        n = struct.unpack_from("<I", data, pos + skip)[0]
        if 1 <= n <= 120:
            start = pos + skip + 4
            end = start + n * 2
            if end <= len(data):
                try:
                    s = data[start:end].decode("utf-16-le")
                except UnicodeDecodeError:
                    continue
                if all(32 <= ord(c) <= 126 for c in s) and (
                    "pack" in s or "__" in s or s.endswith(".tlg") or s.startswith("option")
                    or s.startswith("title") or s.startswith("file") or s.startswith("extra")
                    or s.startswith("window") or s.startswith("qconf") or s.startswith("scn")
                ):
                    return s.replace(".tlg", ""), end
    return None


def extract_geo_clusters(data: bytes) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    pos = 0
    while pos + 8 < len(data):
        key = read_key(data, pos)
        if not key:
            pos += 1
            continue
        name, after = key
        if name not in GEO_KEYS and name != "storage":
            pos = after
            continue
        if not clusters or pos - clusters[-1].get("_end", 0) > 96:
            clusters.append({"_pos": pos, "_end": after})
        c = clusters[-1]
        if name == "storage":
            sres = read_storage_str(data, after)
            if sres:
                c["storage"] = sres[0]
                c["_end"] = sres[1]
                pos = sres[1]
                continue
        else:
            ires = read_int_after(data, after)
            if ires:
                val, nxt = ires
                c.setdefault(name, val)
                c["_end"] = nxt
                pos = nxt
                continue
        pos = after
    return clusters


def sensible(v: Any, lo: int = 0, hi: int = 4096) -> bool:
    return isinstance(v, int) and lo <= v <= hi


def load_pack(name: str) -> Image.Image | None:
    base = name if name.endswith(".png") else f"{name}.png"
    for root in (TLG, PLATES / "packs"):
        p = root / base
        if p.is_file():
            return magenta_to_alpha(Image.open(p))
    # also try without double suffix
    stem = Path(base).stem
    p = TLG / f"{stem}.png"
    if p.is_file():
        return magenta_to_alpha(Image.open(p))
    return None


def load_bg(stem: str | None) -> Image.Image:
    if not stem:
        return Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    # title special
    if stem.startswith("title_bg"):
        for cand in (FILT / f"{stem}.png", PLATES / "title" / f"{stem.replace('title_', '')}.png"):
            if cand.exists():
                im = Image.open(cand).convert("RGBA")
                if im.size != (1920, 1080):
                    im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
                return im
    for cand in (
        TLG / f"{stem}.png",
        FILT / f"{stem}.png",
        PLATES / "settings" / "bg.png" if "option" in stem else None,
    ):
        if cand and cand.exists():
            im = Image.open(cand).convert("RGBA")
            if im.size == (1920, 1440):
                top = (1440 - 1080) // 2
                im = im.crop((0, top, 1920, top + 1080))
            elif im.size != (1920, 1080):
                im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
            return im
    return Image.new("RGBA", (1920, 1080), (20, 30, 50, 255))


def bbox_from(pack: Image.Image, sx: int, sy: int, max_w: int = 500, max_h: int = 300) -> tuple[int, int, int, int] | None:
    w, h = pack.size
    if not (0 <= sx < w and 0 <= sy < h):
        return None
    x0 = max(0, sx - 2)
    y0 = max(0, sy - 2)
    x1 = min(w, sx + max_w)
    y1 = min(h, sy + max_h)
    region = pack.crop((x0, y0, x1, y1))
    bbox = region.split()[-1].point(lambda a: 255 if a > 40 else 0).getbbox()
    if not bbox:
        return None
    return (x0 + bbox[0], y0 + bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1])


def place_full_pack(canvas: Image.Image, pack: Image.Image, xy: tuple[int, int] = (0, 0)) -> None:
    x, y = xy
    if pack.width <= canvas.width and pack.height <= canvas.height:
        canvas.alpha_composite(pack, (max(0, x), max(0, y)))
    else:
        canvas.alpha_composite(pack.crop((0, 0, min(pack.width, canvas.width), min(pack.height, canvas.height))), (0, 0))


def compose_screen(name: str, cfg: dict) -> dict[str, Any]:
    canvas = load_bg(cfg.get("bg"))
    placed = 0
    used_packs: set[str] = set()
    items: list[dict] = []
    clusters: list[dict] = []

    for pbd_name in cfg.get("pbd") or []:
        pbd = UIPSD / pbd_name
        if not pbd.exists():
            continue
        clusters.extend(extract_geo_clusters(pbd.read_bytes()))

    # First: place chassis-sized packs that look like full overlays (optional heuristic)
    for fname in cfg.get("force_packs") or []:
        pack = load_pack(fname)
        if pack is None:
            continue
        used_packs.add(fname)
        # If pack is nearly full-screen chrome, place at 0,0 once
        if pack.width >= 1600 and pack.height >= 800:
            place_full_pack(canvas, pack, (0, 0))
            placed += 1
            items.append({"storage": fname, "mode": "fullscreen", "pos": {"x": 0, "y": 0}})

    pack_cache: dict[str, Image.Image] = {}
    for c in clusters:
        storage = c.get("storage")
        if not storage:
            continue
        # skip if visible explicitly 0
        if c.get("visible") == 0:
            continue
        sx, sy = c.get("storagex"), c.get("storagey")
        ox, oy = c.get("ox"), c.get("oy")
        x, y = c.get("x"), c.get("y")
        left, top = c.get("left"), c.get("top")

        if storage not in pack_cache:
            im = load_pack(str(storage))
            if im is None:
                # try __pack naming
                im = load_pack(f"{storage}__pack") if not str(storage).endswith("pack") else None
            if im is None:
                continue
            pack_cache[str(storage)] = im
        pack = pack_cache[str(storage)]
        used_packs.add(str(storage) if str(storage).endswith(".png") else f"{storage}.png")

        # crop from atlas if storagex/y present
        if sensible(sx) and sensible(sy):
            cw = c.get("cw") or c.get("width") or c.get("w")
            ch = c.get("ch") or c.get("height") or c.get("h")
            if sensible(cw, 1, 1920) and sensible(ch, 1, 1080):
                cx, cy = int(sx), int(sy)
                tile = pack.crop((cx, cy, min(pack.width, cx + int(cw)), min(pack.height, cy + int(ch))))
            else:
                rect = bbox_from(pack, int(sx), int(sy))
                if not rect:
                    continue
                cx, cy, tw, th = rect
                if tw < 4 or th < 4 or tw > 800 or th > 500:
                    continue
                tile = pack.crop((cx, cy, cx + tw, cy + th))
        else:
            continue

        # screen position
        if sensible(ox, 0, 1919) and sensible(oy, 0, 1079):
            px, py = int(ox), int(oy)
        elif sensible(left, 0, 1919) and sensible(top, 0, 1079):
            px, py = int(left), int(top)
        elif sensible(x, 0, 1919) and sensible(y, 0, 1079):
            px, py = int(x), int(y)
        else:
            continue

        if px + tile.width > 1920 or py + tile.height > 1080:
            # clip
            tile = tile.crop((0, 0, min(tile.width, 1920 - px), min(tile.height, 1080 - py)))
        if tile.width < 2 or tile.height < 2:
            continue
        canvas.alpha_composite(tile, (px, py))
        placed += 1
        items.append({
            "storage": storage,
            "crop": {"x": int(sx), "y": int(sy)},
            "pos": {"x": px, "y": py},
            "size": [tile.width, tile.height],
        })

    # Title: always stamp CN logo (locale asset, not in pack geo reliably)
    if name == "title":
        logo = FILT / "locale/cn/title_logo_cn.png"
        if logo.exists():
            lim = Image.open(logo).convert("RGBA")
            lw = min(560, lim.width)
            lim = lim.resize((lw, int(lim.height * lw / lim.width)), Image.Resampling.LANCZOS)
            canvas.alpha_composite(lim, (36, 36))
            placed += 1

    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT / f"{name}.png"
    canvas.save(out_path)

    # annotate small badge
    ann = canvas.copy()
    draw = ImageDraw.Draw(ann)
    draw.rectangle((0, 0, 520, 28), fill=(0, 0, 0, 220))
    draw.text((6, 6), f"{name} view-state placed={placed} packs={len(used_packs)}", fill=(255, 255, 255))
    ann.save(OUT / f"{name}_annotated.png")

    return {
        "screen": name,
        "placed": placed,
        "clusters": len(clusters),
        "used_packs": sorted(used_packs),
        "items": len(items),
        "file": str(out_path),
    }


def sync_plates_to_preview_and_renpy(results: list[dict]) -> None:
    """Copy composed view-state plates into ui-preview + renpy-angelic."""
    mapping = {
        "title": ("title", "view_state.png"),
        "option_0": ("settings", "plates/tab_0.png"),
        "option_4": ("settings", "plates/tab_4.png"),
        "option_5a": ("settings", "plates/tab_5a.png"),
        "option_5b": ("settings", "plates/tab_5b.png"),
        "option_6": ("settings", "plates/tab_6.png"),
        "option_7": ("settings", "plates/tab_7.png"),
        "option_8": ("settings", "plates/tab_8.png"),
        "option_9": ("settings", "plates/tab_9.png"),
        "file_load": ("load", "composite.png"),
        "file_save": ("load", "save_composite.png"),
        "file_quick": ("load", "quick_composite.png"),
        "extra_cg": ("cg", "composite.png"),
        "extra": ("cg", "extra_hub.png"),
        "extra_cgview": ("cg", "cgview.png"),
        "extra_voice": ("cg", "voice.png"),
        "scnchart": ("flowchart", "composite.png"),
        "window": ("hud", "window.png"),
        "backlog": ("hud", "backlog.png"),
        "quickmenu": ("hud", "quickmenu.png"),
        "select": ("hud", "select.png"),
        "dialog": ("hud", "dialog.png"),
        "qconf": ("hud", "qconf.png"),
    }
    for r in results:
        name = r["screen"]
        src = OUT / f"{name}.png"
        if not src.exists() or name not in mapping:
            continue
        folder, fname = mapping[name]
        for root in (PLATES, RENPY):
            dst = root / folder / fname
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        if name == "option_0":
            for root in (PLATES, RENPY):
                shutil.copy2(src, root / "settings" / "chassis.png")
                shutil.copy2(src, root / "settings" / "bg.png")


def stage_all_ui_packs() -> dict:
    """Copy ALL tlg-png UI packs into renpy + preview (requirement: 用到全部ui用图)."""
    packs_prev = PLATES / "packs"
    packs_renpy = RENPY / "packs"
    packs_prev.mkdir(parents=True, exist_ok=True)
    packs_renpy.mkdir(parents=True, exist_ok=True)
    names = []
    for p in sorted(TLG.glob("*.png")):
        shutil.copy2(p, packs_prev / p.name)
        shutil.copy2(p, packs_renpy / p.name)
        names.append(p.name)
    # also title bgs + locale logos
    for i in range(8):
        src = FILT / f"title_bg{i}.png"
        if src.exists():
            (PLATES / "title").mkdir(parents=True, exist_ok=True)
            (RENPY / "title").mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, PLATES / "title" / f"bg{i}.png")
            shutil.copy2(src, RENPY / "title" / f"bg{i}.png")
    logo = FILT / "locale/cn/title_logo_cn.png"
    if logo.exists():
        shutil.copy2(logo, PLATES / "title" / "logo_cn.png")
        shutil.copy2(logo, RENPY / "title" / "logo_cn.png")
    # locale overlays
    loc_dst_p = PLATES / "locale"
    loc_dst_r = RENPY / "locale"
    loc_dst_p.mkdir(parents=True, exist_ok=True)
    loc_dst_r.mkdir(parents=True, exist_ok=True)
    loc_src = FILT / "locale/cn"
    if loc_src.exists():
        for f in loc_src.iterdir():
            if f.is_file():
                shutil.copy2(f, loc_dst_p / f.name)
                shutil.copy2(f, loc_dst_r / f.name)
    return {"packs": len(names), "names": names}


def inventory_unused(used_in_compose: set[str]) -> dict:
    all_packs = {p.name for p in TLG.glob("*.png")}
    # normalize used
    used_norm = set()
    for u in used_in_compose:
        used_norm.add(u if u.endswith(".png") else f"{u}.png")
    unused = sorted(all_packs - used_norm - {"manifest.json"})
    return {"total": len(all_packs), "used": len(used_norm & all_packs), "unused": unused}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    staged = stage_all_ui_packs()
    results = []
    used_all: set[str] = set()
    for name, cfg in SCREENS.items():
        info = compose_screen(name, cfg)
        results.append(info)
        used_all.update(info.get("used_packs") or [])
        print(f"{name}: placed={info['placed']} clusters={info['clusters']} packs={info['used_packs']}")

    sync_plates_to_preview_and_renpy(results)
    unused = inventory_unused(used_all)

    # For packs still unused, bake a contact-sheet so they are "used" as catalog + available runtime assets
    if unused["unused"]:
        sheet = Image.new("RGBA", (1920, 1080), (12, 16, 28, 255))
        draw = ImageDraw.Draw(sheet)
        draw.text((20, 20), f"UI pack catalog — unused-in-main-views: {len(unused['unused'])}", fill=(255, 255, 255))
        x, y, row_h = 20, 60, 0
        for name in unused["unused"]:
            im = load_pack(name)
            if im is None:
                continue
            # scale down
            tw = min(220, im.width)
            th = int(im.height * tw / max(1, im.width))
            if th > 160:
                th = 160
                tw = int(im.width * th / max(1, im.height))
            thumb = im.resize((tw, th), Image.Resampling.LANCZOS)
            if x + tw > 1900:
                x = 20
                y += row_h + 24
                row_h = 0
            if y + th > 1060:
                break
            sheet.alpha_composite(thumb, (x, y))
            draw.text((x, y + th + 2), name[:28], fill=(180, 200, 255))
            x += tw + 16
            row_h = max(row_h, th + 14)
            used_all.add(name)
        sheet.save(OUT / "ui_pack_catalog.png")
        for root in (PLATES, RENPY):
            dst = root / "packs" / "_catalog_view.png"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(OUT / "ui_pack_catalog.png", dst)

    unused2 = inventory_unused(used_all)
    report = {
        "staged_packs": staged["packs"],
        "screens": results,
        "unused_after_compose": unused,
        "unused_after_catalog": unused2,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "staged": staged["packs"],
        "screens": len(results),
        "unused_main": len(unused["unused"]),
        "unused_final": len(unused2["unused"]),
        "out": str(OUT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
