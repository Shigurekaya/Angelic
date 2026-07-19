# -*- coding: utf-8 -*-
"""Capture tenshi_sz window via PrintWindow (works even if occluded)."""
from __future__ import annotations

import ctypes
import json
import subprocess
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image

OUT = Path(r"D:\gamedev\Angelic\docs\ui-extract\pixel-reverse\_orig_capture")
GAME = Path(r"E:\GAL\天使☆嚣嚣")
EXE = GAME / "tenshi_sz.exe"

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


def list_windows():
    wins = []

    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        title = ""
        if length:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        wins.append({"hwnd": int(hwnd), "title": title, "cls": cls.value, "pid": int(pid.value)})
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return wins


def find_game_hwnd():
    # match by process name
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq tenshi_sz.exe", "/FO", "CSV", "/NH"],
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        out = ""
    pids = set()
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) >= 2 and parts[0].lower() == "tenshi_sz.exe":
            pids.add(int(parts[1]))
    wins = list_windows()
    for w in wins:
        if w["pid"] in pids and w["title"]:
            return w
    # fallback title
    for w in wins:
        t = w["title"]
        if "RE-BOOT" in t or "嚣嚣" in t or "天使" in t:
            return w
    return None


def print_window(hwnd: int, path: Path) -> dict:
    # get client size
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
    if w < 64 or h < 64:
        wr = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(wr))
        w = wr.right - wr.left
        h = wr.bottom - wr.top

    hwndDC = user32.GetDC(hwnd)
    memDC = gdi32.CreateCompatibleDC(hwndDC)
    bmp = gdi32.CreateCompatibleBitmap(hwndDC, w, h)
    gdi32.SelectObject(memDC, bmp)
    # PW_RENDERFULLCONTENT = 2
    ok = user32.PrintWindow(hwnd, memDC, 2)
    if not ok:
        ok = user32.PrintWindow(hwnd, memDC, 0)

    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = w
    bmi.biHeight = -h  # top-down
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = 0
    buf_len = w * h * 4
    buf = (ctypes.c_ubyte * buf_len)()
    gdi32.GetDIBits(memDC, bmp, 0, h, buf, ctypes.byref(bmi), 0)

    img = Image.frombuffer("RGBA", (w, h), bytes(buf), "raw", "BGRA", 0, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)

    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(memDC)
    user32.ReleaseDC(hwnd, hwndDC)
    return {"ok": bool(ok), "w": w, "h": h, "path": str(path)}


def ensure_running(boot=12.0):
    w = find_game_hwnd()
    if w:
        return w
    subprocess.Popen([str(EXE)], cwd=str(GAME))
    time.sleep(boot)
    for _ in range(40):
        w = find_game_hwnd()
        if w:
            return w
        time.sleep(0.5)
    return None


def main():
    import sys

    name = sys.argv[1] if len(sys.argv) > 1 else "capture"
    w = ensure_running()
    if not w:
        print("GAME NOT FOUND")
        # dump titles for debug
        for x in list_windows():
            if x["title"]:
                print(x["pid"], x["cls"], x["title"][:80])
        return
    print("game", json.dumps(w, ensure_ascii=False))
    user32.ShowWindow(w["hwnd"], 9)  # SW_RESTORE
    user32.SetForegroundWindow(w["hwnd"])
    time.sleep(0.4)
    OUT.mkdir(parents=True, exist_ok=True)
    info = print_window(w["hwnd"], OUT / f"{name}.png")
    # also upscale note
    img = Image.open(info["path"])
    if img.size != (1920, 1080):
        img.resize((1920, 1080), Image.Resampling.LANCZOS).save(OUT / f"{name}_1080.png")
        info["scaled"] = str(OUT / f"{name}_1080.png")
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
