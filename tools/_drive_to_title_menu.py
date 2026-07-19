# -*- coding: utf-8 -*-
"""Drive original game to stable title menu and capture; also open settings/load if possible."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(r"D:/gamedev/Angelic/tools")))
from _capture_printwindow import ensure_running, find_game_hwnd, print_window, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
VK = {"ret": 0x0D, "esc": 0x1B, "space": 0x20, "down": 0x28, "up": 0x26, "left": 0x25, "right": 0x27}


def key(hwnd, vk, hold=0.05):
    user32.PostMessageW(hwnd, 0x100, vk, 0)
    time.sleep(hold)
    user32.PostMessageW(hwnd, 0x101, vk, 0)


def click_client(hwnd, x, y):
    # client coords
    lparam = (y << 16) | (x & 0xFFFF)
    user32.PostMessageW(hwnd, 0x0201, 0x0001, lparam)  # WM_LBUTTONDOWN
    time.sleep(0.05)
    user32.PostMessageW(hwnd, 0x0202, 0, lparam)  # WM_LBUTTONUP


def save_scaled(hwnd, name: str):
    info = print_window(hwnd, OUT / f"{name}.png")
    im = Image.open(info["path"]).convert("RGBA")
    im.resize((1920, 1080), Image.Resampling.LANCZOS).save(OUT / f"{name}_1080.png")
    return im.size


def glow_count(path: Path, region="right") -> int:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    if region == "right":
        box = (int(w * 0.75), int(h * 0.3), w, int(h * 0.95))
    else:
        box = (int(w * 0.1), int(h * 0.8), int(w * 0.9), h)
    crop = im.crop(box)
    px = crop.load()
    n = 0
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = px[x, y]
            if (r > 200 and g > 170 and b < 140) or (b > 190 and g > 150 and r < 155):
                n += 1
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # kill stale then relaunch fresh
    subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
    time.sleep(1)
    w = ensure_running(boot=20.0)
    if not w:
        print("FAIL launch")
        return
    hwnd = w["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    log = []
    # spam through splash / logos / movies
    for i in range(25):
        key(hwnd, VK["ret"])
        key(hwnd, VK["space"])
        time.sleep(0.4)
        if i % 5 == 4:
            size = save_scaled(hwnd, f"boot_{i}")
            gR = glow_count(OUT / f"boot_{i}_1080.png", "right")
            gB = glow_count(OUT / f"boot_{i}_1080.png", "bottom")
            log.append({"i": i, "size": size, "glow_right": gR, "glow_bottom": gB})
            print(f"boot_{i}: glowR={gR} glowB={gB} size={size}")
            if gR > 2500 or gB > 2500:
                print("likely menu visible")
                break
    # final title capture
    save_scaled(hwnd, "title_stable")
    # try click bottom-center (heart) and right-side menu zones
    rect = type("R", (), {})()
    # approximate client size from last capture
    im = Image.open(OUT / "title_stable.png")
    cw, ch = im.size
    for xy in [(cw // 2, int(ch * 0.92)), (int(cw * 0.85), int(ch * 0.45)), (int(cw * 0.85), int(ch * 0.55)), (int(cw * 0.85), int(ch * 0.65))]:
        click_client(hwnd, xy[0], xy[1])
        time.sleep(0.6)
    save_scaled(hwnd, "title_after_click")
    # try open system via keyboard navigation (down+enter repeatedly)
    for _ in range(8):
        key(hwnd, VK["down"])
        time.sleep(0.15)
    key(hwnd, VK["ret"])
    time.sleep(1.2)
    save_scaled(hwnd, "maybe_settings")
    key(hwnd, VK["esc"])
    time.sleep(0.8)
    save_scaled(hwnd, "back_title")
    (OUT / "drive_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print("done", log[-3:] if log else None)


if __name__ == "__main__":
    main()
