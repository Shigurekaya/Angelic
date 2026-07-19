# -*- coding: utf-8 -*-
"""Re-bake Angelic settings / flowchart plates correctly (not centered atlas dumps).

Rules (cafe method):
- Base = full-screen __bg0 from unpack TLG
- Overlay = pack slices / whole pack placed inside option frame — never center-dump atlas
- Do NOT stamp from live screenshots as art
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
PREV = ROOT / "ui-preview/assets"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic"
MEASURE = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture/measure/extra_layout.json"

# YuzuSoft-style option frame (from patch_pixel_settings / help chrome)
OPTION_FRAME = {"x": 109, "y": 120, "w": 1701, "h": 839}


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


def paste_in_frame(bg: Image.Image, pack: Image.Image, frame: dict) -> Image.Image:
    """Place pack top-left inside frame (clip if oversized)."""
    out = bg.copy()
    pack = magenta_to_alpha(pack)
    fx, fy = int(frame["x"]), int(frame["y"])
    fw, fh = int(frame["w"]), int(frame["h"])
    # prefer top-left of frame; if pack smaller, keep top-left (not center-atlas)
    x, y = fx, fy
    # clip pack to frame
    pw, ph = pack.size
    if pw > fw or ph > fh:
        pack = pack.crop((0, 0, min(pw, fw), min(ph, fh)))
    out.alpha_composite(pack, (x, y))
    return out


def paste_slices_row(bg: Image.Image, slice_dir: Path, indices: list[int], x0: int, y0: int, gap: int = 8) -> Image.Image:
    """Paste numbered slices horizontally (for tab chrome etc.)."""
    out = bg.copy()
    x = x0
    sj = slice_dir / "slices.json"
    files = {}
    if sj.exists():
        data = json.loads(sj.read_text(encoding="utf-8"))
        for item in data:
            files[int(item["i"])] = item["file"]
    for i in indices:
        fn = files.get(i, f"s{i:03d}_*.png")
        path = None
        if i in files:
            path = slice_dir / files[i]
        else:
            hits = list(slice_dir.glob(f"s{i:03d}_*.png"))
            path = hits[0] if hits else None
        if path is None or not path.exists():
            continue
        tile = magenta_to_alpha(Image.open(path).convert("RGBA"))
        out.alpha_composite(tile, (x, y0))
        x += tile.width + gap
    return out


def bake_settings() -> dict:
    out = ensure(PREV / "settings")
    plates = ensure(out / "plates")
    bg = load_tlg("option__bg0.png")
    if bg is None:
        raise SystemExit("missing option__bg0")

    bg.save(out / "bg.png")

    # Tab page packs: base chrome + page-specific overlay
    tabs = [
        ("0", "option__pack.png", None),
        ("1", "option__pack.png", None),  # same chassis until dedicated packs exist
        ("2", "option__pack.png", None),
        ("3", "option__pack.png", None),
        ("4", "option__pack.png", "option_4text__pack.png"),
        ("5a", "option__pack.png", "option_5sound1__pack.png"),
        ("5b", "option__pack.png", "option_5sound2__pack.png"),
        ("6", "option__pack.png", "option_6dialog__pack.png"),
        ("7", "option__pack.png", "option_7mouse__pack.png"),
        ("8", "option__pack.png", "option_8keyboard1__pack.png"),
        ("9", "option__pack.png", "option_9gamepad__pack.png"),
    ]

    meta_tabs = []
    for tid, base_pack, overlay in tabs:
        canvas = bg.copy()
        bp = load_tlg(base_pack)
        if bp:
            canvas = paste_in_frame(canvas, bp, OPTION_FRAME)
        if overlay:
            op = load_tlg(overlay)
            if op:
                # page content slightly inset
                frame2 = {
                    "x": OPTION_FRAME["x"] + 40,
                    "y": OPTION_FRAME["y"] + 80,
                    "w": OPTION_FRAME["w"] - 80,
                    "h": OPTION_FRAME["h"] - 100,
                }
                canvas = paste_in_frame(canvas, op, frame2)
        # footer cmds (reset / title / back-ish) if present — bottom of frame
        cmds = load_tlg("option_cmds__pack.png")
        if cmds:
            cmds = magenta_to_alpha(cmds)
            # place near bottom-right of frame
            cx = OPTION_FRAME["x"] + OPTION_FRAME["w"] - cmds.width - 24
            cy = OPTION_FRAME["y"] + OPTION_FRAME["h"] - cmds.height - 12
            if cx > 0 and cy > 0:
                canvas.alpha_composite(cmds, (cx, cy))

        fname = f"plates/tab_{tid}.png"
        canvas.save(out / fname)
        canvas.save(plates / f"tab_{tid}.png")
        labels = {
            "0": "基本设置",
            "1": "画面设置",
            "2": "游戏设置1",
            "3": "游戏设置2",
            "4": "文本设置",
            "5a": "音频1",
            "5b": "音频2",
            "6": "确认信息",
            "7": "鼠标",
            "8": "键盘",
            "9": "手柄",
        }
        meta_tabs.append({"id": tid, "label": labels.get(tid, tid), "plate": fname})

    # chassis = tab_0
    shutil.copy2(plates / "tab_0.png", out / "chassis.png")

    # copy packs for runtime
    for name in [
        "option__pack.png",
        "option_4text__pack.png",
        "option_5sound1__pack.png",
        "option_5sound2__pack.png",
        "option_6dialog__pack.png",
        "option_7mouse__pack.png",
        "option_8keyboard1__pack.png",
        "option_9gamepad__pack.png",
        "option_cmds__pack.png",
        "option_keyinput__pack.png",
    ]:
        src = TLG / name
        if src.exists():
            shutil.copy2(src, out / name)

    # tab hotspots: top strip inside header (10 pages)
    n = len(meta_tabs)
    tab_x0, tab_y, tab_h = 200, 28, 52
    tab_x1 = 1600
    tw = (tab_x1 - tab_x0) // max(1, n)
    tab_items = []
    for i, t in enumerate(meta_tabs):
        tab_items.append(
            {
                "id": t["id"],
                "label": t["label"],
                "x": tab_x0 + i * tw,
                "y": tab_y,
                "w": tw,
                "h": tab_h,
            }
        )

    meta = {
        "family": "settings",
        "frame": OPTION_FRAME,
        "tabs": meta_tabs,
        "tabs_layout": {"items": tab_items},
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "note": "bg0 + packs in frame (not centered atlas)",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # sync to renpy
    dst = ensure(RENPY / "settings")
    for src in out.rglob("*"):
        if src.is_file():
            rel = src.relative_to(out)
            d = dst / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, d)
    return {"tabs": len(meta_tabs), "dst": str(dst)}


def bake_flowchart() -> dict:
    out = ensure(PREV / "flowchart")
    bg = load_tlg("scnchart__bg0.png")
    if bg is None:
        raise SystemExit("missing scnchart__bg0")
    # crop 1920x1440 → 1920x1080 (top content)
    if bg.size != (1920, 1080):
        w, h = bg.size
        if w == 1920 and h >= 1080:
            bg = bg.crop((0, 0, 1920, 1080))
        else:
            bg = bg.resize((1920, 1080), Image.Resampling.LANCZOS)
    bg.save(out / "bg.png")

    canvas = bg.copy()
    pack = load_tlg("scnchart__pack.png")
    if pack:
        pack = magenta_to_alpha(pack)
        # place pack in upper content (leave bottom bar)
        x = max(0, (1920 - pack.width) // 2)
        y = 80
        canvas.alpha_composite(pack, (x, y))
    canvas.save(out / "composite.png")
    if pack:
        magenta_to_alpha(pack).save(out / "pack.png")

    meta = {
        "family": "flowchart",
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "exclude_story": True,
        "note": "scnchart__bg0 crop + pack overlay",
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    dst = ensure(RENPY / "flowchart")
    for src in out.rglob("*"):
        if src.is_file():
            shutil.copy2(src, dst / src.name)
    return {"composite": str(out / "composite.png")}


def patch_cg_group_tabs() -> dict:
    """Merge measured EXTRA group_tabs into cg_hotspots.json."""
    hs_path = RENPY / "cg" / "cg_hotspots.json"
    if not hs_path.exists():
        return {"ok": False, "reason": "missing cg_hotspots"}
    data = json.loads(hs_path.read_text(encoding="utf-8"))
    if MEASURE.exists():
        m = json.loads(MEASURE.read_text(encoding="utf-8"))
        data["group_tabs"] = m.get("group_tabs") or []
        # keep existing cells/grid if already matching view_state; only add tabs
        data["layout_note"] = m.get("layout_note")
    else:
        # fallback: 8 tabs horizontal
        groups = data.get("groups") or []
        tabs = []
        x0, pitch = 80, 110
        for i, g in enumerate(groups):
            tabs.append(
                {
                    "id": g.get("id"),
                    "label": g.get("label"),
                    "x": x0 + i * pitch,
                    "y": 168,
                    "w": 96,
                    "h": 36,
                }
            )
        data["group_tabs"] = tabs
    data["back"] = data.get("back") or {"x": 1680, "y": 1000, "w": 200, "h": 48}
    hs_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    # also preview + game root
    prev = ensure(PREV / "cg")
    shutil.copy2(hs_path, prev / "cg_hotspots.json")
    game = RENPY.parent.parent
    shutil.copy2(hs_path, game / "cg_hotspots.json")
    return {"group_tabs": len(data.get("group_tabs") or [])}


def main() -> int:
    s = bake_settings()
    f = bake_flowchart()
    c = patch_cg_group_tabs()
    print(json.dumps({"settings": s, "flowchart": f, "cg": c}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
