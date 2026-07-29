# -*- coding: utf-8 -*-
"""Re-capture settings with correct click mapping (PrintWindow = full window)."""
from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_printwindow import find_game_hwnd, print_window, user32  # noqa: E402
from _capture_settings_pages import move_click  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
VIEW = Path(r"D:/gamedev/_tmp_settings_view")
VIEW.mkdir(exist_ok=True)


def window_rect(hwnd):
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def client_origin_screen(hwnd):
    pt = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y


def cap(hwnd, name: str) -> Image.Image:
    p = OUT / f"{name}.png"
    print_window(hwnd, p)
    im = Image.open(p).convert("RGBA")
    # Crop to client area inside the full-window capture
    wl, wt, ww, wh = window_rect(hwnd)
    cx, cy = client_origin_screen(hwnd)
    cr = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(cr))
    cw, ch = cr.right - cr.left, cr.bottom - cr.top
    ox, oy = cx - wl, cy - wt
    client = im.crop((ox, oy, ox + cw, oy + ch))
    im1080 = client.resize((1920, 1080), Image.Resampling.LANCZOS)
    im1080.save(OUT / f"{name}_1080.png")
    im1080.convert("RGB").save(VIEW / f"{name}_1080.png", quality=88)
    print(f"{name}: win={im.size} client=({cw},{ch}) oxoy=({ox},{oy}) ->1080")
    return im1080


def click_client(hwnd, cw, ch, x1080, y1080):
    """Click using 1920x1080 client-space coords."""
    cx = int(x1080 * cw / 1920)
    cy = int(y1080 * ch / 1080)
    ox, oy = client_origin_screen(hwnd)
    sx, sy = ox + cx, oy + cy
    user32.SetForegroundWindow(hwnd)
    move_click(sx, sy)
    time.sleep(0.85)


def main() -> None:
    w = find_game_hwnd()
    if not w:
        raise SystemExit("no game")
    hwnd = w["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    cr = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(cr))
    cw, ch = cr.right - cr.left, cr.bottom - cr.top
    print("client", cw, ch, "origin", client_origin_screen(hwnd), "win", window_rect(hwnd))

    # First capture whatever is showing
    cur = cap(hwnd, "recap_cur")

    # Tab centers from original Chinese strip (client 1080 space).
    # Measured from user truth / good live text page: tabs ~ y=40, roughly:
    # 基本~760 画面~900 游戏1~1040 游戏2~1180 文本~1320 音频~1460
    # Confirm may require scrolling tab strip — try further right after audio.
    tabs = [
        ("0", 760),
        ("1", 900),
        ("2", 1040),
        ("3", 1180),
        ("4", 1320),
        ("5a", 1460),
        ("6", 1600),
        ("5b", 1720),
    ]
    for tid, x in tabs:
        click_client(hwnd, cw, ch, x, 42)
        im = cap(hwnd, f"ig_option_{tid}")
        im.save(OUT / f"ig_option_{tid}_1080.png")

    print("done")


if __name__ == "__main__":
    main()
