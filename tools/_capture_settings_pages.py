# -*- coding: utf-8 -*-
"""Capture Angelic original settings pages (pixel ground truth).

Flow: relaunch → settle title → click 系统设定 → capture tab0 → click tabs → capture each.
"""
from __future__ import annotations

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_printwindow import EXE, GAME, find_game_hwnd, print_window, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
LAYOUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture/manual/title_btn_layout.json")

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


def mean_l(path: Path) -> int:
    return Image.open(path).convert("L").resize((1, 1)).getpixel((0, 0))


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


def save_cap(hwnd, name: str) -> tuple[Image.Image, int]:
    path = OUT / f"{name}.png"
    print_window(hwnd, path)
    im = Image.open(path).convert("RGBA")
    im1080 = im.resize((1920, 1080), Image.Resampling.LANCZOS)
    im1080.save(OUT / f"{name}_1080.png")
    L = mean_l(path)
    print(f"  {name}: {im.size} L={L}")
    return im1080, L


def layout_to_client(btn: dict, cw: int, ch: int) -> tuple[int, int]:
    """Map 1920x1080 layout rect center → client coords."""
    sx = cw / 1920.0
    sy = ch / 1080.0
    cx = int((btn["x"] + btn["w"] / 2) * sx)
    cy = int((btn["y"] + btn["h"] / 2) * sy)
    return cx, cy


def settle_title(hwnd) -> None:
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)
    for _ in range(8):
        key_vk(0x1B)
        time.sleep(0.2)
    time.sleep(0.6)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    btns = json.loads(LAYOUT.read_text(encoding="utf-8")) if LAYOUT.exists() else {}
    system = btns.get("system") or {"x": 1448, "y": 1002, "w": 117, "h": 38}

    # relaunch clean
    subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
    time.sleep(1.2)
    if not EXE.exists():
        raise SystemExit(f"missing {EXE}")
    print("launch", EXE)
    subprocess.Popen([str(EXE)], cwd=str(GAME))

    w = None
    for i in range(60):
        w = find_game_hwnd()
        if w:
            break
        time.sleep(0.5)
    if not w:
        raise SystemExit("game window not found")
    hwnd = w["hwnd"]
    print("hwnd", hwnd, w.get("title"))

    # skip splash → title (bright KV)
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    bright = 0
    for i in range(40):
        path = OUT / f"setcap_boot_{i:02d}.png"
        print_window(hwnd, path)
        L = mean_l(path)
        print(f"boot {i} L={L}")
        if L < 45:
            key_vk(0x0D)
            key_vk(0x20)
            time.sleep(0.45)
            bright = 0
        elif L > 140:
            bright += 1
            time.sleep(0.7)
            if bright >= 3:
                print("title settled")
                break
        else:
            key_vk(0x20)
            time.sleep(0.35)
            bright = 0

    settle_title(hwnd)
    save_cap(hwnd, "setcap_title")

    cw, ch = client_size(hwnd)
    print("client", cw, ch)
    cx, cy = layout_to_client(system, cw, ch)
    sx, sy = to_screen(hwnd, cx, cy)
    print("click system client", cx, cy, "screen", sx, sy)

    user32.SetForegroundWindow(hwnd)
    time.sleep(0.2)
    user32.SetCursorPos(sx, sy)
    time.sleep(0.35)
    save_cap(hwnd, "setcap_hover_system")
    move_click(sx, sy)
    time.sleep(1.2)
    im, L = save_cap(hwnd, "setcap_option_0")
    if L < 40:
        print("WARN: option capture still dark — retry click")
        move_click(sx, sy)
        time.sleep(1.2)
        im, L = save_cap(hwnd, "setcap_option_0")

    # Tab strip guess (Angelic rebuild used y≈28–80, x 200–1720). Click each.
    # Prefer measured strip on capture if bright enough.
    tab_y = int(50 * ch / 1080)
    tabs = [
        ("0", "基本"),
        ("1", "画面"),
        ("2", "游戏1"),
        ("3", "游戏2"),
        ("4", "文本"),
        ("5a", "音频1"),
        ("5b", "音频2"),
        ("6", "确认"),
        ("7", "鼠标"),
        ("8", "键盘"),
        ("9", "手柄"),
    ]
    x0 = int(220 * cw / 1920)
    x1 = int(1700 * cw / 1920)
    n = len(tabs)
    tw = (x1 - x0) // n
    log = [{"tab": "0", "L": L, "file": "setcap_option_0_1080.png"}]

    for i, (tid, _lab) in enumerate(tabs):
        if i == 0:
            continue
        tcx = x0 + i * tw + tw // 2
        tcy = tab_y
        tsx, tsy = to_screen(hwnd, tcx, tcy)
        user32.SetForegroundWindow(hwnd)
        move_click(tsx, tsy)
        time.sleep(0.7)
        _, Lt = save_cap(hwnd, f"setcap_option_{tid}")
        log.append({"tab": tid, "L": Lt, "client": [tcx, tcy]})

    (OUT / "setcap_settings_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print("done", log)


if __name__ == "__main__":
    main()
