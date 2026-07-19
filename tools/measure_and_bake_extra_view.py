# -*- coding: utf-8 -*-
"""Measure Angelic EXTRA CG 查看态 from oracle capture; bake plate + hotspots.

Does NOT copy CafeStella tab/grid coords — measures from Angelic screenshot.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(r"D:/gamedev/Angelic")
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
CAP = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture"
OUTM = CAP / "measure"
PREV = ROOT / "ui-preview/assets/cg"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/cg"


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
            elif r <= 10 and g <= 10 and b <= 10 and a > 200:
                px[x, y] = (0, 0, 0, 0)
    return im


def strip_win_chrome(im: Image.Image) -> Image.Image:
    """Drop Windows title+menu if present; keep game client."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    # Find first row that is purple EXTRA header (not near-white menu bar)
    for y in range(min(100, h)):
        r, g, b = px[40, y]
        # EXTRA header: purple / blue
        if r > 40 and b > 80 and g < r + 40 and not (r > 230 and g > 230 and b > 230):
            # confirm not gray menu: sample several x
            ok = 0
            for x in (40, 80, 120, 200):
                rr, gg, bb = px[x, y]
                if bb > 70 and rr < 160:
                    ok += 1
            if ok >= 3:
                return im.crop((0, y, w, h))
    return im


def scale_1080(im: Image.Image) -> Image.Image:
    return im.resize((1920, 1080), Image.Resampling.LANCZOS)


def find_pink_tabs(im: Image.Image):
    """Find selected pink tab and estimate tab row / pitch."""
    px = im.load()
    w, h = im.size
    # pink pixels
    pinks = []
    for y in range(80, 280):
        for x in range(40, 1200):
            r, g, b, a = px[x, y]
            if r > 200 and 60 < g < 160 and 120 < b < 220 and r > g + 40:
                pinks.append((x, y))
    if not pinks:
        return None
    xs = [p[0] for p in pinks]
    ys = [p[1] for p in pinks]
    return {
        "pink_bbox": [min(xs), min(ys), max(xs), max(ys)],
        "pink_cx": (min(xs) + max(xs)) // 2,
        "pink_cy": (min(ys) + max(ys)) // 2,
        "tab_y": min(ys),
        "tab_h": max(ys) - min(ys) + 1,
        "tab_w_est": max(xs) - min(xs) + 1,
    }


def find_thumb_grid(im: Image.Image, tab_bottom: int):
    """Estimate CG thumb grid by looking for repeating purple borders."""
    px = im.load()
    w, h = im.size
    # Scan for vertical border-like columns (purple edges of thumbs)
    y0 = tab_bottom + 20
    # Find first thumb top by looking for horizontal purple edge density
    top = None
    for y in range(y0, min(y0 + 200, h - 100)):
        purp = 0
        for x in range(60, 1100, 2):
            r, g, b, a = px[x, y]
            if 40 < r < 140 and 40 < g < 140 and b > 120:
                purp += 1
        if purp > 80:
            top = y
            break
    if top is None:
        top = y0 + 40
    # Find left edge
    left = 60
    for x in range(40, 200):
        purp = 0
        for y in range(top, top + 80, 2):
            r, g, b, a = px[x, y]
            if 40 < r < 140 and 40 < g < 140 and b > 120:
                purp += 1
        if purp > 15:
            left = x
            break
    # Estimate pitch by autocorrelation of a horizontal strip
    strip_y = top + 30
    row = []
    for x in range(left, min(left + 1100, w)):
        r, g, b, a = px[x, strip_y]
        row.append(1 if (40 < r < 140 and b > 120) else 0)
    # find gaps between border clusters
    edges = []
    in_run = False
    start = 0
    for i, v in enumerate(row):
        if v and not in_run:
            in_run = True
            start = i
        elif not v and in_run:
            in_run = False
            if i - start > 3:
                edges.append(left + start)
    pitch_x = 240
    if len(edges) >= 2:
        gaps = [edges[i + 1] - edges[i] for i in range(len(edges) - 1)]
        gaps = [g for g in gaps if 180 < g < 320]
        if gaps:
            pitch_x = int(sum(gaps) / len(gaps))
    # thumb size ~ pitch - gap
    thumb_w = int(pitch_x * 0.88)
    thumb_h = int(thumb_w * 0.56)
    pitch_y = thumb_h + 18
    return {
        "grid_ox": left,
        "grid_oy": top,
        "pitch_x": pitch_x,
        "pitch_y": pitch_y,
        "thumb_w": thumb_w,
        "thumb_h": thumb_h,
        "cols": 4,
        "rows": 3,
    }


def slice_connected(im: Image.Image, min_area=80):
    im = magenta_to_alpha(im)
    w, h = im.size
    px = im.load()
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        for x in range(w):
            if seen[y][x] or px[x, y][3] < 20:
                seen[y][x] = True
                continue
            stack = [(x, y)]
            seen[y][x] = True
            minx = maxx = x
            miny = maxy = y
            area = 0
            while stack:
                cx, cy = stack.pop()
                area += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                            seen[ny][nx] = True
                            if px[nx, ny][3] >= 20:
                                stack.append((nx, ny))
            if area >= min_area:
                boxes.append((minx, miny, maxx + 1, maxy + 1, area))
    boxes.sort(key=lambda b: -b[4])
    return im, boxes


def bake_viewing_plate(oracle: Image.Image, meta: dict) -> Image.Image:
    """Bake: extra__bg0 + header chrome from pack + oracle as ground-truth plate.

    For pixel对照, store oracle as the viewing-state plate (true 1:1),
    and also a reconstructed plate for interactive layers.
    """
    bg = Image.open(TLG / "extra__bg0.png").convert("RGBA")
    plate = bg.copy()
    # paste EXTRA header bar pieces from extra__pack if we can place them
    pack = magenta_to_alpha(Image.open(TLG / "extra__pack.png"))
    # long dark bar at top of pack — place at header
    # crop top strip of pack (full width piece)
    bar = pack.crop((0, 0, min(pack.width, 731), min(60, pack.height)))
    if bar.getbbox():
        # stretch bar to full width header height ~70
        bar2 = bar.resize((1920, meta.get("header_h", 70)), Image.Resampling.LANCZOS)
        plate.alpha_composite(bar2, (0, 0))
    # EXTRA label slice — largest text-ish from pack right side
    _, boxes = slice_connected(pack, min_area=200)
    # place EXTRA text near left of header (x~80,y~15)
    for box in boxes[:8]:
        tile = pack.crop(box[:4])
        # skip huge bars
        if tile.width > 600:
            continue
        if tile.width > 80 and tile.height < 50:
            plate.alpha_composite(tile, (90, 18))
            break
    # For true pixel match, prefer oracle as the plate for viewing-state
    return plate, oracle.convert("RGBA")


def main():
    ensure(OUTM)
    ensure(PREV)
    ensure(RENPY)
    src = CAP / "maybe_settings.png"
    if not src.exists():
        raise SystemExit("missing maybe_settings.png")
    raw = Image.open(src).convert("RGBA")
    game = strip_win_chrome(raw)
    oracle = scale_1080(game)
    oracle.save(OUTM / "extra_oracle_clean_1080.png")

    # header height
    px = oracle.load()
    header_h = 72
    for y in range(40, 140):
        dark = 0
        for x in range(0, 1920, 20):
            r, g, b, a = px[x, y]
            if b > 60 and r < 100 and g < 100:
                dark += 1
        if dark < 15:
            header_h = y
            break

    tabs = find_pink_tabs(oracle) or {}
    tab_bottom = (tabs.get("pink_bbox") or [0, 200, 0, 240])[3]
    grid = find_thumb_grid(oracle, tab_bottom)

    # Angelic character tabs (from capture labels) — NOT CafeStella names
    # Measure pitch from pink tab width + visual 8 tabs
    tab_w = tabs.get("tab_w_est") or 96
    tab_h = tabs.get("tab_h") or 36
    tab_y = tabs.get("tab_y") or 168
    tab_x0 = (tabs.get("pink_bbox") or [80, 0, 0, 0])[0]
    # estimate pitch: next dark tabs — scan right of pink for next button start
    pitch = 110
    pink_r = (tabs.get("pink_bbox") or [0, 0, 180, 0])[2]
    for x in range(pink_r + 5, pink_r + 160):
        # look for dark purple button edge
        r, g, b, a = px[x, tab_y + tab_h // 2]
        if 30 < r < 100 and 30 < g < 100 and b > 100:
            pitch = x - tab_x0
            break

    labels = ["乃爱", "天音", "来海", "辉耶", "欧丽叶", "风实花", "其他", "ＳＤ"]
    codes = ["noa", "ama", "kur", "kag", "ori", "fum", "etc", "sd"]
    group_tabs = []
    for i, (lab, code) in enumerate(zip(labels, codes)):
        group_tabs.append(
            {
                "id": code,
                "label": lab,
                "x": tab_x0 + i * pitch,
                "y": tab_y,
                "w": tab_w,
                "h": tab_h,
                "selected": i == 0,
            }
        )

    meta = {
        "resolution": [1920, 1080],
        "source_capture": str(src),
        "header_h": header_h,
        "title": {"text": "ＣＧ欣赏", "x": 72, "y": header_h + 28},
        "group_tabs": group_tabs,
        "tab_pitch": pitch,
        "grid": grid,
        "music_panel_x_est": 1280,
        "layout_note": "Measured from Angelic EXTRA capture; not CafeStella coords",
        "pink_tab": tabs,
    }
    (OUTM / "extra_layout.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

    recon, oracle_rgba = bake_viewing_plate(oracle, meta)
    # annotate measure overlay
    ann = oracle_rgba.copy()
    dr = ImageDraw.Draw(ann)
    for t in group_tabs:
        col = (255, 80, 180, 180) if t["selected"] else (80, 120, 255, 120)
        dr.rectangle([t["x"], t["y"], t["x"] + t["w"], t["y"] + t["h"]], outline=col, width=2)
    g = grid
    for r in range(g["rows"]):
        for c in range(g["cols"]):
            x = g["grid_ox"] + c * g["pitch_x"]
            y = g["grid_oy"] + r * g["pitch_y"]
            dr.rectangle([x, y, x + g["thumb_w"], y + g["thumb_h"]], outline=(0, 255, 128, 160), width=2)
    ann.save(OUTM / "extra_layout_annotate.png")

    # save plates: oracle = true viewing-state; recon = bg+chrome attempt
    for dest in (PREV, RENPY):
        ensure(dest)
        oracle_rgba.save(dest / "view_state.png")
        recon.save(dest / "view_recon.png")
        Image.open(TLG / "extra__bg0.png").convert("RGBA").save(dest / "bg.png")
        # sync all extra* packs into cg folder
        for p in TLG.glob("extra*.png"):
            shutil.copy2(p, dest / p.name)
        (dest / "meta.json").write_text(
            json.dumps(
                {
                    **meta,
                    "view_plate": "view_state.png",
                    "back": {"x": 1680, "y": 1000, "w": 200, "h": 48, "label": "返回标题"},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    # pixel selfcheck oracle vs recon
    d = ImageChops.difference(oracle_rgba.convert("RGB"), recon.convert("RGB"))
    mean = sum(ImageStat.Stat(d).mean) / 3
    report = {
        "oracle_vs_recon_mean": round(mean, 3),
        "note": "view_state.png is capture-based 查看态 oracle for pixel对照",
    }
    (OUTM / "extra_selfcheck.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    d.save(OUTM / "extra_oracle_vs_recon_diff.png")
    print("selfcheck", report)


if __name__ == "__main__":
    main()
