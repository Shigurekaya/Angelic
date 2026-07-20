# -*- coding: utf-8 -*-
"""Capture Angelic settings via ImageGrab client rect (PrintWindow fails on HW accel)."""
from __future__ import annotations

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_printwindow import EXE, GAME, find_game_hwnd, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
LAYOUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture/manual/title_btn_layout.json")
BG0 = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/tlg-png/option__bg0.png")

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


def client_rect_screen(hwnd):
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    pt = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y, rect.right - rect.left, rect.bottom - rect.top


def grab_client(hwnd) -> Image.Image:
    x, y, w, h = client_rect_screen(hwnd)
    if w < 100 or h < 100:
        raise RuntimeError(f"bad client {w}x{h}")
    # slight delay so present finishes
    time.sleep(0.05)
    im = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return im.convert("RGBA")


def mean_l(im: Image.Image) -> float:
    return im.convert("L").resize((1, 1)).getpixel((0, 0))


def save(name: str, im: Image.Image) -> float:
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f"{name}.png")
    im.resize((1920, 1080), Image.Resampling.LANCZOS).save(OUT / f"{name}_1080.png")
    L = mean_l(im)
    print(f"  {name}: {im.size} L={L:.0f}")
    return L


def move_click(sx, sy):
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    ax = int(sx * 65535 / max(1, sw - 1))
    ay = int(sy * 65535 / max(1, sh - 1))
    user32.SetCursorPos(int(sx), int(sy))
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


def to_screen(hwnd, cx, cy):
    pt = wintypes.POINT(int(cx), int(cy))
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y


def layout_center(btn, cw, ch):
    sx, sy = cw / 1920.0, ch / 1080.0
    return int((btn["x"] + btn["w"] / 2) * sx), int((btn["y"] + btn["h"] / 2) * sy)


def corr_to_bg0(im: Image.Image) -> float:
    """Rough similarity to option__bg0 (sky chrome). Higher = closer."""
    if not BG0.exists():
        return 0.0
    a = im.resize((320, 180), Image.Resampling.BILINEAR).convert("RGB")
    b = Image.open(BG0).resize((320, 180), Image.Resampling.BILINEAR).convert("RGB")
    import numpy as np

    aa = np.asarray(a, dtype=np.float32)
    bb = np.asarray(b, dtype=np.float32)
    return float(1.0 - np.mean(np.abs(aa - bb)) / 255.0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    btns = json.loads(LAYOUT.read_text(encoding="utf-8")) if LAYOUT.exists() else {}
    system = btns.get("system") or {"x": 1448, "y": 1002, "w": 117, "h": 38}

    subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
    time.sleep(1.2)
    print("launch", EXE)
    subprocess.Popen([str(EXE)], cwd=str(GAME))

    w = None
    for _ in range(80):
        w = find_game_hwnd()
        if w:
            break
        time.sleep(0.4)
    if not w:
        raise SystemExit("no hwnd")
    hwnd = w["hwnd"]
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)

    # skip splash: wait until NOT near-white, then settle
    for i in range(50):
        user32.SetForegroundWindow(hwnd)
        im = grab_client(hwnd)
        L = mean_l(im)
        save(f"ig_boot_{i:02d}", im)
        print(f"boot {i} L={L:.0f}")
        if L > 230:
            # white splash — click through
            key_vk(0x0D)
            key_vk(0x20)
            time.sleep(0.5)
        elif L > 100:
            # likely title KV — wait to settle
            time.sleep(0.8)
            im2 = grab_client(hwnd)
            if abs(mean_l(im2) - L) < 8 and L < 220:
                save("ig_title", im2)
                print("title settled")
                break
        else:
            key_vk(0x20)
            time.sleep(0.4)

    # esc a few times to ensure title menu
    for _ in range(4):
        key_vk(0x1B)
        time.sleep(0.2)
    time.sleep(0.5)
    user32.SetForegroundWindow(hwnd)
    title = grab_client(hwnd)
    save("ig_title_ready", title)

    x, y, cw, ch = client_rect_screen(hwnd)
    print("client", cw, ch, "screen_origin", x, y)
    cx, cy = layout_center(system, cw, ch)
    sx, sy = to_screen(hwnd, cx, cy)
    print("system click", cx, cy, "->", sx, sy)

    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    user32.SetCursorPos(sx, sy)
    time.sleep(0.4)
    save("ig_hover_system", grab_client(hwnd))
    move_click(sx, sy)
    time.sleep(1.4)
    user32.SetForegroundWindow(hwnd)
    opt0 = grab_client(hwnd)
    L0 = save("ig_option_0", opt0)
    sim0 = corr_to_bg0(opt0)
    print(f"option_0 sim_bg0={sim0:.3f}")

    # If still look like title, try alternate click points near system
    if sim0 < 0.55:
        print("retry system clicks")
        for dx, dy in [(0, 0), (-40, 0), (40, 0), (0, -20), (-80, 0), (80, 0)]:
            sx2, sy2 = to_screen(hwnd, cx + dx, cy + dy)
            user32.SetForegroundWindow(hwnd)
            move_click(sx2, sy2)
            time.sleep(1.0)
            opt0 = grab_client(hwnd)
            sim0 = corr_to_bg0(opt0)
            L0 = save(f"ig_option_0_try_{dx}_{dy}", opt0)
            print(f"  try {dx},{dy} sim={sim0:.3f} L={L0:.0f}")
            if sim0 >= 0.55:
                save("ig_option_0", opt0)
                break

    # tabs
    tabs = ["0", "1", "2", "3", "4", "5a", "5b", "6", "7", "8", "9"]
    x0 = int(220 * cw / 1920)
    x1 = int(1700 * cw / 1920)
    tab_y = int(55 * ch / 1080)
    tw = (x1 - x0) // len(tabs)
    log = [{"tab": "0", "sim": sim0, "L": L0}]
    for i, tid in enumerate(tabs):
        if i == 0:
            continue
        tcx = x0 + i * tw + tw // 2
        tsx, tsy = to_screen(hwnd, tcx, tab_y)
        user32.SetForegroundWindow(hwnd)
        move_click(tsx, tsy)
        time.sleep(0.85)
        im = grab_client(hwnd)
        sim = corr_to_bg0(im)
        L = save(f"ig_option_{tid}", im)
        log.append({"tab": tid, "sim": sim, "L": L, "client": [tcx, tab_y]})
        print(f"tab {tid} sim={sim:.3f}")

    (OUT / "ig_settings_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE")


if __name__ == "__main__":
    main()
