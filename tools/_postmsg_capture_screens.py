# -*- coding: utf-8 -*-
"""Use PostMessage (known working) to navigate title focus and capture screens."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_client_bitblt import client_capture, save  # noqa: E402
from _capture_printwindow import ensure_running, find_game_hwnd, print_window, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
VK = {"ret": 0x0D, "esc": 0x1B, "space": 0x20, "down": 0x28, "up": 0x26}


def key(hwnd, vk, hold=0.05):
    user32.PostMessageW(hwnd, 0x100, vk, 0)
    time.sleep(hold)
    user32.PostMessageW(hwnd, 0x101, vk, 0)


def yellow_right(im: Image.Image) -> int:
    w, h = im.size
    c = im.crop((int(w * 0.72), int(h * 0.25), w, int(h * 0.95)))
    px = c.load()
    n = 0
    for y in range(0, c.height, 2):
        for x in range(0, c.width, 2):
            r, g, b, a = px[x, y]
            if r > 200 and g > 170 and b < 130:
                n += 1
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # fresh launch
    subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
    time.sleep(1.2)
    w = ensure_running(boot=22.0)
    if not w:
        print("FAIL")
        return
    hwnd = w["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # skip splash with PostMessage
    for i in range(30):
        key(hwnd, VK["ret"])
        key(hwnd, VK["space"])
        time.sleep(0.35)
    time.sleep(2.0)

    base = client_capture(hwnd)
    save("pm_title_base", base)
    print("base yellow", yellow_right(base))

    # cycle focus with DOWN — capture each step (look for hover glow)
    log = []
    for i in range(12):
        key(hwnd, VK["down"])
        time.sleep(0.45)
        im = client_capture(hwnd)
        save(f"pm_focus_{i:02d}", im)
        y = yellow_right(im)
        # mean diff vs base
        d = ImageChops.difference(im.convert("RGB"), base.convert("RGB"))
        mean = sum(ImageStat.Stat(d).mean) / 3
        log.append({"i": i, "yellow": y, "diff_mean": round(mean, 3)})
        print(f"focus_{i}: yellow={y} diff_mean={mean:.3f}")
        d.point(lambda v: 255 if v > 20 else 0).save(OUT / f"pm_focus_{i:02d}_mask.png")

    (OUT / "pm_focus_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")

    # enter on current focus
    key(hwnd, VK["ret"])
    time.sleep(1.5)
    entered = client_capture(hwnd)
    save("pm_entered", entered)
    print_window(hwnd, OUT / "pm_entered_pw.png")

    # if not useful, esc and try open extra by counting downs from top
    key(hwnd, VK["esc"])
    time.sleep(0.8)
    for _ in range(20):
        key(hwnd, VK["up"])
        time.sleep(0.08)
    # start at top: down 4 times often hits extra (0 start 1 cont 2 load 3 flow 4 extra)
    for n in range(5):
        key(hwnd, VK["down"])
        time.sleep(0.2)
    key(hwnd, VK["ret"])
    time.sleep(1.5)
    save("pm_extra", client_capture(hwnd))
    print_window(hwnd, OUT / "pm_extra_pw.png")

    key(hwnd, VK["esc"])
    time.sleep(0.8)
    # system ~ index 6
    for _ in range(20):
        key(hwnd, VK["up"])
        time.sleep(0.05)
    for _ in range(7):
        key(hwnd, VK["down"])
        time.sleep(0.15)
    key(hwnd, VK["ret"])
    time.sleep(1.5)
    save("pm_option", client_capture(hwnd))
    print_window(hwnd, OUT / "pm_option_pw.png")

    key(hwnd, VK["esc"])
    time.sleep(0.8)
    for _ in range(20):
        key(hwnd, VK["up"])
        time.sleep(0.05)
    for _ in range(2):
        key(hwnd, VK["down"])
        time.sleep(0.15)
    key(hwnd, VK["ret"])
    time.sleep(1.5)
    save("pm_load", client_capture(hwnd))
    print_window(hwnd, OUT / "pm_load_pw.png")

    print("done", log)


if __name__ == "__main__":
    main()
