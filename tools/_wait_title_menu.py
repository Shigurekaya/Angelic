# -*- coding: utf-8 -*-
"""Wait for title menu, capture, analyze bottom+right for button glow."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(r"D:/gamedev/Angelic/tools")))
from _capture_printwindow import find_game_hwnd, print_window, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")


def glow_mask(im: Image.Image, region: str) -> Image.Image:
    """Highlight yellow/cyan/white-glow UI text pixels."""
    w, h = im.size
    if region == "right":
        box = (int(w * 0.72), int(h * 0.25), w, int(h * 0.95))
    elif region == "bottom":
        box = (0, int(h * 0.75), w, h)
    else:
        box = (0, 0, w, h)
    crop = im.crop(box).convert("RGBA")
    px = crop.load()
    out = Image.new("RGBA", crop.size, (0, 0, 0, 255))
    op = out.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = px[x, y]
            if (r > 200 and g > 170 and b < 140) or (b > 190 and g > 150 and r < 150):
                op[x, y] = (255, 220, 0, 255)
            elif r > 240 and g > 240 and b > 240:
                op[x, y] = (0, 255, 255, 255)
            else:
                op[x, y] = (r // 3, g // 3, b // 3, 255)
    return out


def row_profile(im: Image.Image, x0_frac=0.0, x1_frac=1.0) -> list[tuple[int, int]]:
    w, h = im.size
    px = im.load()
    x0, x1 = int(w * x0_frac), int(w * x1_frac)
    prof = []
    for y in range(h):
        hits = 0
        for x in range(x0, x1):
            r, g, b, a = px[x, y]
            if (r > 200 and g > 170 and b < 140) or (b > 190 and g > 150 and r < 150) or (
                r > 245 and g > 245 and b > 245
            ):
                hits += 1
        prof.append((y, hits))
    return prof


def cluster(prof, min_hits=15, gap=6, min_h=10):
    bands = []
    cur = None
    for y, hits in prof:
        if hits < min_hits:
            continue
        if cur is None or y - cur["y1"] > gap:
            if cur and (cur["y1"] - cur["y0"] + 1) >= min_h:
                bands.append(cur)
            cur = {"y0": y, "y1": y, "hits": hits}
        else:
            cur["y1"] = y
            cur["hits"] += hits
    if cur and (cur["y1"] - cur["y0"] + 1) >= min_h:
        bands.append(cur)
    return bands


def main():
    winfo = find_game_hwnd()
    if not winfo:
        print("NO GAME")
        return
    hwnd = winfo["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    # wait for title menu settle
    for i in range(8):
        time.sleep(1.0)
        path = OUT / f"title_wait_{i}.png"
        print_window(hwnd, path)
        im = Image.open(path).convert("RGBA")
        # scale to 1080 for analysis
        if im.size != (1920, 1080):
            # letterbox-aware: stretch client
            im1080 = im.resize((1920, 1080), Image.Resampling.LANCZOS)
        else:
            im1080 = im
        im1080.save(OUT / f"title_wait_{i}_1080.png")
        right = cluster(row_profile(im1080, 0.75, 1.0), min_hits=20, gap=5, min_h=12)
        bottom = cluster(row_profile(im1080, 0.05, 0.95), min_hits=40, gap=5, min_h=12)
        # bottom-only region profile
        bot_im = im1080.crop((0, int(1080 * 0.78), 1920, 1080))
        bottom2 = cluster(row_profile(bot_im, 0.0, 1.0), min_hits=25, gap=4, min_h=10)
        print(f"t={i} size={im.size} right_bands={len(right)} bottom_bands={len(bottom2)}")
        for b in right[:10]:
            print("  R", b)
        for b in bottom2[:10]:
            print("  B", {**b, "y0": b["y0"] + int(1080 * 0.78), "y1": b["y1"] + int(1080 * 0.78)})
        glow_mask(im1080, "right").save(OUT / f"title_wait_{i}_glow_right.png")
        glow_mask(im1080, "bottom").save(OUT / f"title_wait_{i}_glow_bottom.png")
        # send enter periodically to skip anim
        user32.PostMessageW(hwnd, 0x100, 0x0D, 0)
        user32.PostMessageW(hwnd, 0x101, 0x0D, 0)

    # final capture
    print_window(hwnd, OUT / "title_final.png")
    print("done")


if __name__ == "__main__":
    main()
