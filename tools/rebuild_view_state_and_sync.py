# -*- coding: utf-8 -*-
"""Measure EXTRA viewing-state from original capture; rebuild title logo overlay; sync all packs."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

ROOT = Path(r"D:/gamedev/Angelic")
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
CAP = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture"
OUT = CAP / "measure"
PREV = ROOT / "ui-preview/assets"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic"
PACKS_DST = RENPY / "packs"


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def find_content_top(im: Image.Image) -> int:
    """Skip Windows title/menu bars: find first row that looks like game (not gray UI)."""
    px = im.convert("RGB").load()
    w, h = im.size
    for y in range(min(120, h)):
        # sample mid
        r, g, b = px[w // 2, y]
        # windows menu is near-white gray; game EXTRA header is purple/blue
        if not (r > 220 and g > 220 and b > 220) and not (180 < r < 240 and 180 < g < 240 and 180 < b < 240 and abs(r - g) < 15):
            # also skip pure titlebar blue-ish? 
            if y > 20 and (b > r + 20 or r < 200):
                return y
    return 50


def crop_client_game(im: Image.Image) -> Image.Image:
    """Heuristic: drop top chrome; keep full width client game."""
    top = find_content_top(im)
    # also check if PrintWindow already client-only: if top bar is purple EXTRA, top~0
    sample = im.crop((0, 0, im.width, min(80, im.height))).convert("RGB")
    # average of left 200px top 60
    left = sample.crop((0, 0, min(200, sample.width), min(60, sample.height)))
    mean = ImageStat.Stat(left).mean
    # purple-ish header => already game content
    if mean[2] > mean[1] and mean[0] > 40 and mean[0] < 180:
        top = 0
    return im.crop((0, top, im.width, im.height))


def measure_extra():
    ensure(OUT)
    src = CAP / "maybe_settings.png"
    if not src.exists():
        print("no maybe_settings")
        return None
    raw = Image.open(src).convert("RGBA")
    game = crop_client_game(raw)
    game1080 = game.resize((1920, 1080), Image.Resampling.LANCZOS)
    game1080.save(OUT / "extra_view_1080.png")
    # header height: find where purple bar ends (row mean drops blue/purple)
    px = game1080.load()
    header_h = 70
    for y in range(40, 140):
        # sample across
        blues = 0
        for x in range(0, 1920, 16):
            r, g, b, a = px[x, y]
            if b > 80 and r < 120 and g < 120:
                blues += 1
        if blues < 20:
            header_h = y
            break
    # tabs row: pink selected tip
    tab_y = None
    for y in range(header_h + 20, header_h + 160):
        pink = 0
        for x in range(80, 900, 2):
            r, g, b, a = px[x, y]
            if r > 180 and g < 140 and b > 140:
                pink += 1
        if pink > 40:
            tab_y = y
            break
    # thumb grid: look for bordered rects — sample edge density
    meta = {
        "source": str(src),
        "raw_size": list(raw.size),
        "game_size_before_scale": list(game.size),
        "header_h_est": header_h,
        "tab_row_y_est": tab_y,
        "notes": "from maybe_settings PrintWindow; chrome top stripped heuristically",
    }
    (OUT / "extra_view_measure.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print("extra measure", meta)
    return game1080, meta


def rebuild_title():
    """Title viewing-state: title_bg + full-bleed logo_cn (frame+logo) + right idle buttons."""
    title_prev = ensure(PREV / "title")
    title_renpy = ensure(RENPY / "title")
    btns_dir = ensure(title_prev / "buttons")
    ensure(title_renpy / "buttons")

    logo = Image.open(FILT / "locale/cn/title_logo_cn.png").convert("RGBA")
    logo.save(title_prev / "logo_cn.png")
    logo.save(title_renpy / "logo_cn.png")

    for i in range(8):
        bg = Image.open(FILT / f"title_bg{i}.png").convert("RGBA")
        bg.save(title_prev / f"bg{i}.png")
        bg.save(title_renpy / f"bg{i}.png")
        # viewing-state plate = bg + logo overlay
        plate = bg.copy()
        plate.alpha_composite(logo, (0, 0))
        plate.save(title_prev / f"view_bg{i}.png")
        plate.save(title_renpy / f"view_bg{i}.png")

    # reuse existing button crops if present
    audit = ROOT / "docs/ui-extract/pixel-reverse/_text_preview"
    # map from build_title_1to1
    from build_title_1to1 import BUTTON_ORDER, CROP_MAP, BTN_X, BTN_Y0, BTN_DY, BTN_W, BTN_H, ACTIONS  # type: ignore

    # ensure buttons exist
    idle_hover = {}
    for idx, (key, state) in CROP_MAP.items():
        src = audit / f"title_btn_{idx:02d}.png"
        if not src.exists():
            continue
        im = Image.open(src).convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if r >= 248 and b >= 248 and g <= 45:
                    px[x, y] = (0, 0, 0, 0)
                elif r <= 12 and g <= 12 and b <= 12:
                    px[x, y] = (0, 0, 0, 0)
        dst_name = f"{key}_{state}.png"
        im.save(btns_dir / dst_name)
        im.save(title_renpy / "buttons" / dst_name)
        idle_hover.setdefault(key, {})[state] = f"buttons/{dst_name}"

    # Logo is full-bleed at 0,0. Buttons on RIGHT (logo leaves right empty).
    # Vertical stack tuned to 1080; not CafeStella coords under top logo.
    buttons = []
    for i, (key, label) in enumerate(BUTTON_ORDER):
        states = idle_hover.get(key) or {}
        idle = states.get("idle") or states.get("selected") or states.get("hover")
        hover = states.get("hover") or states.get("selected") or idle
        if not idle:
            continue
        buttons.append(
            {
                "id": key,
                "label": label,
                "action": ACTIONS.get(key, "toast"),
                "x": BTN_X,
                "y": BTN_Y0 + i * BTN_DY,
                "w": BTN_W,
                "h": BTN_H,
                "idle": idle,
                "hover": hover,
            }
        )

    # also bake one reference composite with buttons for pixel QA
    ref = Image.open(title_renpy / "view_bg2.png").convert("RGBA")
    for b in buttons:
        p = title_renpy / b["idle"]
        if p.exists():
            tile = Image.open(p).convert("RGBA")
            ref.alpha_composite(tile, (b["x"], b["y"]))
    ref.save(title_prev / "view_state_ref.png")
    ref.save(title_renpy / "view_state_ref.png")

    hs = {
        "resolution": [1920, 1080],
        "logo": {"x": 0, "y": 0, "w": 1920, "h": 1080, "file": "logo_cn.png", "full_bleed": True},
        "use_view_plate": True,
        "bg_count": 8,
        "buttons": buttons,
        "layout_note": "Angelic: logo_cn is full-bleed frame+logo (bottom-left). Buttons right column. Not CafeStella under-logo layout.",
    }
    (title_prev / "hotspots.json").write_text(json.dumps(hs, ensure_ascii=False, indent=2), encoding="utf-8")
    (title_renpy / "hotspots.json").write_text(json.dumps(hs, ensure_ascii=False, indent=2), encoding="utf-8")
    print("title rebuilt", len(buttons), "buttons")
    return hs


def bake_extra_plate(extra_view: Image.Image | None):
    """Compose EXTRA viewing plate from bg0 + locale bits; keep capture as oracle."""
    out = ensure(PREV / "cg")
    ren = ensure(RENPY / "cg")
    bg = Image.open(TLG / "extra__bg0.png").convert("RGBA")
    bg.save(out / "bg.png")
    bg.save(ren / "bg.png")
    pack = TLG / "extra_cg__pack.png"
    if pack.exists():
        im = Image.open(pack).convert("RGBA")
        px = im.load()
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if r >= 248 and b >= 248 and g <= 45:
                    px[x, y] = (0, 0, 0, 0)
        im.save(out / "extra_cg__pack.png")
        im.save(ren / "extra_cg__pack.png")
    if extra_view is not None:
        # store oracle capture for self-check
        extra_view.save(out / "oracle_view_1080.png")
        extra_view.save(ren / "oracle_view_1080.png")
        # diff vs bg0
        d = ImageChops.difference(extra_view.convert("RGB"), bg.convert("RGB"))
        mean = sum(ImageStat.Stat(d).mean) / 3
        (out / "oracle_vs_bg0.json").write_text(
            json.dumps({"mean_abs_diff": round(mean, 3)}, indent=2), encoding="utf-8"
        )
        print("extra oracle vs bg0 mean", round(mean, 3))
    # copy other extra packs
    for name in sorted(TLG.glob("extra*.png")):
        shutil.copy2(name, ren / name.name)
        shutil.copy2(name, out / name.name)
    meta = {
        "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
        "has_oracle": extra_view is not None,
    }
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (ren / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def sync_all_packs():
    dst = ensure(PACKS_DST)
    n = 0
    for p in sorted(TLG.glob("*.png")):
        shutil.copy2(p, dst / p.name)
        n += 1
    # also copy slices index if present
    slices = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
    if slices.exists():
        idx = slices / "index.json"
        if idx.exists():
            shutil.copy2(idx, dst / "slices_index.json")
    manifest = {"packs_copied": n, "dest": str(dst)}
    (RENPY / "packs_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("packs synced", n)
    return n


def selfcheck_title():
    """Compare view_state_ref right strip presence of button glyphs vs capture (weak)."""
    ref = RENPY / "title" / "view_state_ref.png"
    cap = CAP / "pm_title_base_1080.png"
    if not cap.exists():
        cap = CAP / "title_menu_idle_1080.png"
    report = {"ref": str(ref), "cap": str(cap), "exists": ref.exists() and cap.exists()}
    if ref.exists() and cap.exists():
        a = Image.open(ref).convert("RGB")
        b = Image.open(cap).convert("RGB").resize(a.size, Image.Resampling.LANCZOS)
        d = ImageChops.difference(a, b)
        report["mean_abs_diff_full"] = round(sum(ImageStat.Stat(d).mean) / 3, 3)
        # right column only
        rc = d.crop((1500, 350, 1900, 900))
        report["mean_abs_diff_right_menu"] = round(sum(ImageStat.Stat(rc).mean) / 3, 3)
        d.save(OUT / "selfcheck_title_diff.png")
    (OUT / "selfcheck_title.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("selfcheck", report)
    return report


def main():
    ensure(OUT)
    extra = measure_extra()
    rebuild_title()
    bake_extra_plate(extra[0] if extra else None)
    sync_all_packs()
    selfcheck_title()
    # re-bake other screens packs into renpy
    import build_other_screens_1to1 as other

    other.main()
    print("done")


if __name__ == "__main__":
    main()
