# -*- coding: utf-8 -*-
"""Open Angelic title MENU (查看态) and capture client area.

Hypothesis (Yuzusoft / HF docs): title KV settles first; confirm reveals menu.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_client_bitblt import client_capture, save  # noqa: E402
from _capture_printwindow import ensure_running, find_game_hwnd, user32  # noqa: E402
from _drive_title_client import (  # noqa: E402
    VK,
    client_size,
    client_to_screen,
    click_screen,
    detect_menu_glyphs,
    mouse_abs,
    send_key,
)

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")


def frame_score(im: Image.Image) -> float:
    """Score presence of white double-frame near top-left corner."""
    c = im.crop((20, 20, 180, 120)).convert("L")
    # bright edge pixels
    px = c.load()
    n = 0
    for y in range(c.height):
        for x in range(c.width):
            if px[x, y] > 220:
                n += 1
    return n / (c.width * c.height)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hwnd_info = find_game_hwnd()
    if not hwnd_info:
        subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
        time.sleep(1)
        hwnd_info = ensure_running(boot=25.0)
    if not hwnd_info:
        print("FAIL no game")
        return
    hwnd = hwnd_info["hwnd"] if isinstance(hwnd_info, dict) else hwnd_info
    if isinstance(hwnd_info, dict):
        hwnd = hwnd_info["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)

    # skip logos gently; stop when frame appears
    settled = None
    for i in range(35):
        send_key(VK["ret"], hold=0.03)
        time.sleep(0.45)
        im = client_capture(hwnd)
        fs = frame_score(im)
        print(f"skip {i}: size={im.size} frame={fs:.4f}")
        if fs > 0.02 and i > 4:
            settled = im
            # wait more without keyspam — let AMV/menu settle
            time.sleep(2.0)
            settled = client_capture(hwnd)
            break
    if settled is None:
        settled = client_capture(hwnd)
    save("title_kv_only", settled)
    print("kv frame", frame_score(settled))

    # ONE confirm to open menu (do not spam)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    send_key(VK["ret"], hold=0.08)
    time.sleep(1.2)
    menu1 = client_capture(hwnd)
    save("title_menu_open1", menu1)
    d1 = ImageChops.difference(menu1.convert("RGB"), settled.convert("RGB"))
    d1.save(OUT / "diff_menu_open1.png")
    bb1 = d1.point(lambda v: 255 if v > 18 else 0).getbbox()
    print("diff after enter1", bb1, "mean", ImageStat.Stat(d1).mean)

    # if little change, try space / click center-bottom logo
    if not bb1 or (bb1[2] - bb1[0]) * (bb1[3] - bb1[1]) < 5000:
        send_key(VK["space"], hold=0.08)
        time.sleep(1.0)
        menu2 = client_capture(hwnd)
        save("title_menu_open2", menu2)
        cw, ch = client_size(hwnd)
        sx, sy = client_to_screen(hwnd, cw // 2, int(ch * 0.9))
        click_screen(sx, sy)
        time.sleep(1.0)
        menu3 = client_capture(hwnd)
        save("title_menu_open3", menu3)
        menu = menu3
    else:
        menu = menu1

    matches = detect_menu_glyphs(menu)
    (OUT / "title_menu_open_match.json").write_text(
        json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("matches", json.dumps(matches, ensure_ascii=False, indent=2))

    # hover right column to force yellow glow for detection
    cw, ch = client_size(hwnd)
    for fy in [0.40, 0.48, 0.56, 0.64, 0.72, 0.80, 0.88]:
        sx, sy = client_to_screen(hwnd, int(cw * 0.86), int(ch * fy))
        mouse_abs(sx, sy)
        time.sleep(0.35)
        snap = client_capture(hwnd)
        save(f"title_hover_y{int(fy*100):02d}", snap)
        # yellow glow count on right
        r = snap.crop((int(cw * 0.75), int(ch * 0.3), cw, int(ch * 0.95)))
        px = r.load()
        yg = 0
        for y in range(0, r.height, 2):
            for x in range(0, r.width, 2):
                rr, g, b, a = px[x, y]
                if rr > 200 and g > 170 and b < 120:
                    yg += 1
        print(f"hover y={fy:.2f} yellow={yg}")
        if yg > 80:
            save("title_menu_hover_hit", snap)
            break

    # final idle: move mouse away then capture
    sx, sy = client_to_screen(hwnd, 40, 40)
    mouse_abs(sx, sy)
    time.sleep(0.6)
    idle = client_capture(hwnd)
    save("title_menu_idle", idle)
    matches_idle = detect_menu_glyphs(idle)
    (OUT / "title_menu_idle_match.json").write_text(
        json.dumps(matches_idle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("idle matches", matches_idle)
    print("done")


if __name__ == "__main__":
    main()
