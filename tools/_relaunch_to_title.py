# -*- coding: utf-8 -*-
"""Kill game, relaunch, skip splash ONLY, stop on bright title KV (do not Enter into new game)."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_printwindow import EXE, GAME, ensure_running, find_game_hwnd, print_window, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")


def key(hwnd, vk, hold=0.04):
    user32.PostMessageW(hwnd, 0x100, vk, 0)
    time.sleep(hold)
    user32.PostMessageW(hwnd, 0x101, vk, 0)


def mean_l(path: Path) -> int:
    return Image.open(path).convert("L").resize((1, 1)).getpixel((0, 0))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
    time.sleep(1.5)
    subprocess.Popen([str(EXE)], cwd=str(GAME))
    time.sleep(18)
    w = None
    for _ in range(40):
        w = find_game_hwnd()
        if w:
            break
        time.sleep(0.5)
    if not w:
        print("FAIL launch")
        return
    hwnd = w["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    prev_l = -1
    bright_streak = 0
    for i in range(50):
        path = OUT / f"rl_boot_{i:02d}.png"
        print_window(hwnd, path)
        L = mean_l(path)
        print(f"boot {i} L={L}")
        # skip logos (often bright or dark) with space/ret sparingly
        if L < 40:
            key(hwnd, 0x0D)
            key(hwnd, 0x20)
            time.sleep(0.5)
            bright_streak = 0
        elif L > 150:
            bright_streak += 1
            # wait — do NOT keep pressing enter (that starts game)
            time.sleep(0.8)
            if bright_streak >= 3:
                print("settled bright title")
                break
        else:
            key(hwnd, 0x20)
            time.sleep(0.4)
            bright_streak = 0
        prev_l = L

    # final captures
    for name in ("rl_title_a", "rl_title_b"):
        print_window(hwnd, OUT / f"{name}.png")
        im = Image.open(OUT / f"{name}.png").convert("RGBA")
        im.resize((1920, 1080), Image.Resampling.LANCZOS).save(OUT / f"{name}_1080.png")
        print(name, im.size, "L", mean_l(OUT / f"{name}.png"))

    # ONE down to highlight first menu item, capture
    key(hwnd, 0x28)
    time.sleep(0.6)
    print_window(hwnd, OUT / "rl_title_focus1.png")
    Image.open(OUT / "rl_title_focus1.png").resize((1920, 1080), Image.Resampling.LANCZOS).save(
        OUT / "rl_title_focus1_1080.png"
    )
    print("focus1 L", mean_l(OUT / "rl_title_focus1.png"))

    # hover via PostMessage click at right — without confirm
    # move: WM_MOUSEMOVE
    cw = 1706
    ch = 960
    for i, yf in enumerate([0.40, 0.48, 0.55, 0.62, 0.70, 0.78]):
        x = int(cw * 0.86)
        y = int(ch * yf)
        lp = (y << 16) | (x & 0xFFFF)
        user32.PostMessageW(hwnd, 0x0200, 0, lp)  # WM_MOUSEMOVE
        time.sleep(0.4)
        print_window(hwnd, OUT / f"rl_hover_{i}.png")
        Image.open(OUT / f"rl_hover_{i}.png").resize((1920, 1080), Image.Resampling.LANCZOS).save(
            OUT / f"rl_hover_{i}_1080.png"
        )
        print(f"hover_{i} L", mean_l(OUT / f"rl_hover_{i}.png"))

    print("done — game left on title")


if __name__ == "__main__":
    main()
