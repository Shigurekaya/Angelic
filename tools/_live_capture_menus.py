# -*- coding: utf-8 -*-
"""Live capture Angelic menus via SetCursorPos + mouse_event + PrintWindow."""
from __future__ import annotations

import ctypes
import json
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_printwindow import find_game_hwnd, print_window, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


def client_size(hwnd):
    r = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def to_screen(hwnd, cx, cy):
    pt = wintypes.POINT(int(cx), int(cy))
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y


def move_click(sx, sy):
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    ax = int(sx * 65535 / max(1, sw - 1))
    ay = int(sy * 65535 / max(1, sh - 1))
    user32.SetCursorPos(sx, sy)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, ax, ay, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.06)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def key_vk(vk):
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, 2, 0)


def save_pw(hwnd, name):
    path = OUT / f"{name}.png"
    info = print_window(hwnd, path)
    im = Image.open(path).convert("RGBA").copy()
    im.resize((1920, 1080), Image.Resampling.LANCZOS).save(OUT / f"{name}_1080.png")
    # mean luminance
    g = im.convert("L").resize((1, 1)).getpixel((0, 0))
    print(name, im.size, "L", g)
    return im, g


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    w = find_game_hwnd()
    if not w:
        print("no game — launch first")
        return
    hwnd = w["hwnd"]
    user32.ShowWindow(hwnd, 9)  # restore
    user32.ShowWindow(hwnd, 3)  # maximize
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)

    cw, ch = client_size(hwnd)
    print("client", cw, ch)

    # Escape a few times to title
    for _ in range(6):
        key_vk(0x1B)
        time.sleep(0.25)
    time.sleep(0.8)
    base, _ = save_pw(hwnd, "live_title0")

    # Click right-side menu candidates (scaled from 1920 layout)
    # BTN_X=1560 BTN_Y0=380 DY=58 → client scale
    sx = cw / 1920
    sy = ch / 1080
    points = []
    for i, name in enumerate(
        ["start", "continue", "load", "flowchart", "extra", "after", "system", "exit"]
    ):
        cx = int(1560 * sx + 40)
        cy = int((380 + i * 58) * sy + 20)
        points.append((name, cx, cy))

    # also bottom logo / heart
    points.append(("heart", cw // 2, int(ch * 0.95)))
    # top-right language
    points.append(("lang", int(cw * 0.92), int(ch * 0.06)))

    log = []
    for name, cx, cy in points:
        user32.SetForegroundWindow(hwnd)
        sx_, sy_ = to_screen(hwnd, cx, cy)
        # hover first
        user32.SetCursorPos(sx_, sy_)
        time.sleep(0.35)
        hover, lh = save_pw(hwnd, f"live_hover_{name}")
        move_click(sx_, sy_)
        time.sleep(0.9)
        after, la = save_pw(hwnd, f"live_click_{name}")
        log.append({"name": name, "client": [cx, cy], "hover_L": lh, "click_L": la})
        print("clicked", name, "L", la)
        # if left title (darker or different), esc back
        if la < 80 or abs(la - 203) > 40:
            # might have opened a menu — keep if looks like EXTRA/option
            if la > 80:
                print("kept screen after", name)
                # if not title-like, esc later
            key_vk(0x1B)
            time.sleep(0.7)
            save_pw(hwnd, f"live_back_{name}")

    # keyboard navigate to open screens
    for _ in range(8):
        key_vk(0x1B)
        time.sleep(0.15)
    time.sleep(0.5)
    for i in range(8):
        key_vk(0x28)  # down
        time.sleep(0.2)
        save_pw(hwnd, f"live_kbd_focus_{i}")
    key_vk(0x0D)
    time.sleep(1.2)
    save_pw(hwnd, "live_kbd_enter")

    (OUT / "live_capture_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print("done", log)


if __name__ == "__main__":
    main()
