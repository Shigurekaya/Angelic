# -*- coding: utf-8 -*-
"""Capture Angelic original window screenshots for viewing-state reference.

Launches tenshi_sz.exe if needed, waits for main window, grabs client area.
Manual: switch to each menu before pressing Enter in console mode,
or use --auto with timed captures after boot.
"""
from __future__ import annotations

import argparse
import ctypes
import subprocess
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageGrab

GAME = Path(r"E:\GAL\天使☆嚣嚣")
EXE = GAME / "tenshi_sz.exe"
OUT = Path(r"D:\gamedev\Angelic\docs\ui-extract\pixel-reverse\_orig_capture")

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)


def enum_windows():
    wins = []

    def cb(hwnd, _lp):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            title = buf.value
            if title and ("天使" in title or "RE-BOOT" in title or "tenshi" in title.lower() or "嚣嚣" in title):
                wins.append((hwnd, title))
            # also catch generic
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls, 256)
            if "Kirikiri" in cls.value or "TVP" in cls.value or "tjs" in cls.value.lower():
                wins.append((hwnd, title or cls.value))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return wins


def client_rect_screen(hwnd):
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    pt = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y, rect.right - rect.left, rect.bottom - rect.top


def capture_hwnd(hwnd, path: Path) -> dict:
    x, y, w, h = client_rect_screen(hwnd)
    if w < 100 or h < 100:
        # fallback PrintWindow full window
        wr = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(wr))
        x, y = wr.left, wr.top
        w, h = wr.right - wr.left, wr.bottom - wr.top
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return {"x": x, "y": y, "w": w, "h": h, "path": str(path), "size": img.size}


def ensure_game(boot_wait: float) -> None:
    wins = enum_windows()
    if wins:
        print("already running", wins)
        return
    if not EXE.exists():
        raise SystemExit(f"missing {EXE}")
    print("launching", EXE)
    subprocess.Popen([str(EXE)], cwd=str(GAME))
    time.sleep(boot_wait)
    for i in range(30):
        wins = enum_windows()
        if wins:
            print("found", wins)
            return
        time.sleep(1)
    # list all visible for debug
    allw = []

    def cb(hwnd, _lp):
        if user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if buf.value:
                allw.append(buf.value)
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    print("no game window; visible titles sample:", allw[:30])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=float, default=12.0)
    ap.add_argument("--name", default="boot")
    ap.add_argument("--launch", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.launch:
        ensure_game(args.boot)
    wins = enum_windows()
    if not wins:
        # try any large window containing 天使 or RE-BOOT in process list via ImageGrab full primary
        print("NO matching window — capturing primary monitor as fallback")
        img = ImageGrab.grab()
        path = OUT / f"{args.name}_primary.png"
        img.save(path)
        print("saved", path, img.size)
        return
    hwnd, title = wins[0]
    path = OUT / f"{args.name}.png"
    info = capture_hwnd(hwnd, path)
    print(json_dumps := __import__("json").dumps({"title": title, **info}, ensure_ascii=False))


if __name__ == "__main__":
    main()
