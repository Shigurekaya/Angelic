# -*- coding: utf-8 -*-
"""Drive Angelic to settled title 查看态 + system screens; client BitBlt capture."""
from __future__ import annotations

import ctypes
import json
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_client_bitblt import client_capture, save  # noqa: E402
from _capture_printwindow import ensure_running, user32  # noqa: E402

OUT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
AUDIT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_text_preview")

# SendInput
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK = {"ret": 0x0D, "esc": 0x1B, "space": 0x20, "down": 0x28, "up": 0x26, "left": 0x25, "right": 0x27, "f": 0x46}


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", INPUT_UNION)]


def send_key(vk, hold=0.05):
    extra = ctypes.pointer(ctypes.c_ulong(0))
    down = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(vk, 0, 0, 0, extra)))
    up = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, extra)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    time.sleep(hold)
    ctypes.windll.user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))


def mouse_abs(x, y):
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    ax = int(x * 65535 / max(1, sw - 1))
    ay = int(y * 65535 / max(1, sh - 1))
    extra = ctypes.pointer(ctypes.c_ulong(0))
    inp = INPUT(
        type=INPUT_MOUSE,
        union=INPUT_UNION(
            mi=MOUSEINPUT(ax, ay, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, 0, extra)
        ),
    )
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def click_screen(x, y):
    mouse_abs(x, y)
    time.sleep(0.05)
    extra = ctypes.pointer(ctypes.c_ulong(0))
    down = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, extra)))
    up = INPUT(type=INPUT_MOUSE, union=INPUT_UNION(mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, extra)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(down), ctypes.sizeof(INPUT))
    time.sleep(0.05)
    ctypes.windll.user32.SendInput(1, ctypes.byref(up), ctypes.sizeof(INPUT))


def client_to_screen(hwnd, cx, cy):
    pt = wintypes.POINT(cx, cy)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return pt.x, pt.y


def client_size(hwnd):
    r = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    return r.right - r.left, r.bottom - r.top


def sad_match(hay: Image.Image, needle: Image.Image, region, step=3):
    """Return (score, x, y) best mean abs diff in region (x0,y0,x1,y1)."""
    hx = hay.convert("RGB")
    nd = needle.convert("RGB")
    nw, nh = nd.size
    x0, y0, x1, y1 = region
    best = (1e18, -1, -1)
    for y in range(y0, max(y0 + 1, y1 - nh), step):
        for x in range(x0, max(x0 + 1, x1 - nw), step):
            patch = hx.crop((x, y, x + nw, y + nh))
            diff = ImageChops.difference(patch, nd)
            s = sum(ImageStat.Stat(diff).mean) / 3.0
            if s < best[0]:
                best = (s, x, y)
    return best


def detect_menu_glyphs(im: Image.Image) -> dict:
    """Match idle white button crops on capture."""
    # prefer idle-looking crops (narrower, less yellow)
    candidates = {
        "flowchart": "title_btn_23.png",
        "start": "title_btn_11.png",
        "load": "title_btn_14.png",
        "system": "title_btn_08.png",
        "extra": "title_btn_17.png",
        "after": "title_btn_18.png",
        "continue": "title_btn_15.png",
        "exit": "title_btn_22.png",
    }
    w, h = im.size
    regions = {
        "right": (int(w * 0.72), int(h * 0.25), w, int(h * 0.95)),
        "bottom": (int(w * 0.05), int(h * 0.72), int(w * 0.95), h),
        "center": (int(w * 0.35), int(h * 0.35), int(w * 0.75), int(h * 0.75)),
    }
    out = {}
    for key, fname in candidates.items():
        tp = AUDIT / fname
        if not tp.exists():
            continue
        nd = Image.open(tp)
        # strip near-magenta
        nd = nd.convert("RGBA")
        px = nd.load()
        for yy in range(nd.height):
            for xx in range(nd.width):
                r, g, b, a = px[xx, yy]
                if r > 240 and b > 240 and g < 60:
                    px[xx, yy] = (0, 0, 0, 0)
        # use RGB with black bg for match
        rgb = Image.new("RGB", nd.size, (0, 0, 0))
        rgb.paste(nd, mask=nd.split()[3])
        best_all = (1e18, None, -1, -1)
        for rname, reg in regions.items():
            sc, x, y = sad_match(im, rgb, reg, step=4)
            if sc < best_all[0]:
                best_all = (sc, rname, x, y)
        out[key] = {"score": round(best_all[0], 2), "region": best_all[1], "x": best_all[2], "y": best_all[3], "crop": fname}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    subprocess.run(["taskkill", "/IM", "tenshi_sz.exe", "/F"], capture_output=True)
    time.sleep(1.2)
    winfo = ensure_running(boot=25.0)
    if not winfo:
        print("FAIL launch")
        return
    hwnd = winfo["hwnd"]
    user32.ShowWindow(hwnd, 3)  # maximize
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    log = []
    # skip splash / logos
    for i in range(40):
        send_key(VK["ret"])
        send_key(VK["space"])
        time.sleep(0.35)
        if i % 8 == 7:
            im = client_capture(hwnd)
            save(f"drv_boot_{i}", im)
            # rough: if bottom heart-like red present
            crop = im.crop((im.width // 2 - 40, im.height - 80, im.width // 2 + 40, im.height))
            px = list(crop.getdata())
            redish = sum(1 for r, g, b, a in px if r > 120 and g < 90 and b < 90)
            log.append({"i": i, "size": im.size, "redish": redish})
            print(f"boot_{i} size={im.size} redish={redish}")
            if redish > 40:
                break

    # wait for settle
    time.sleep(1.5)
    base = client_capture(hwnd)
    save("title_client_base", base)
    matches = detect_menu_glyphs(base)
    (OUT / "title_client_match.json").write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8")
    print("base matches", matches)

    cw, ch = client_size(hwnd)
    # click heart bottom-center
    hx, hy = client_to_screen(hwnd, cw // 2, int(ch * 0.96))
    click_screen(hx, hy)
    time.sleep(0.8)
    after_heart = client_capture(hwnd)
    save("title_after_heart", after_heart)

    # sweep mouse along bottom and right to force hover glow
    for frac_y in [0.55, 0.62, 0.70, 0.78, 0.86, 0.93]:
        sx, sy = client_to_screen(hwnd, int(cw * 0.88), int(ch * frac_y))
        mouse_abs(sx, sy)
        time.sleep(0.25)
    hover_r = client_capture(hwnd)
    save("title_hover_right", hover_r)

    for frac_x in [0.25, 0.35, 0.45, 0.55, 0.65, 0.75]:
        sx, sy = client_to_screen(hwnd, int(cw * frac_x), int(ch * 0.92))
        mouse_abs(sx, sy)
        time.sleep(0.25)
    hover_b = client_capture(hwnd)
    save("title_hover_bottom", hover_b)

    # diff hover vs base to find UI
    for name, im in [("right", hover_r), ("bottom", hover_b), ("heart", after_heart)]:
        d = ImageChops.difference(im.convert("RGB"), base.convert("RGB"))
        d = d.point(lambda v: 255 if v > 28 else 0)
        d = d.filter(ImageFilter.MaxFilter(3))
        d.save(OUT / f"diff_{name}.png")
        # bbox of non-black
        bb = d.getbbox()
        print(f"diff_{name} bbox={bb}")

    matches2 = detect_menu_glyphs(hover_r)
    (OUT / "title_hover_match.json").write_text(json.dumps(matches2, ensure_ascii=False, indent=2), encoding="utf-8")
    print("hover matches", matches2)

    # try open EXTRA via keyboard (we know it worked once)
    for _ in range(6):
        send_key(VK["down"])
        time.sleep(0.12)
    send_key(VK["ret"])
    time.sleep(1.5)
    extra = client_capture(hwnd)
    save("screen_extra", extra)

    send_key(VK["esc"])
    time.sleep(0.8)
    # navigate to system (further down)
    for _ in range(10):
        send_key(VK["up"])
        time.sleep(0.08)
    for _ in range(7):
        send_key(VK["down"])
        time.sleep(0.12)
    send_key(VK["ret"])
    time.sleep(1.5)
    opt = client_capture(hwnd)
    save("screen_option", opt)

    send_key(VK["esc"])
    time.sleep(0.8)
    for _ in range(3):
        send_key(VK["up"])
        time.sleep(0.1)
    # try load (3rd item often)
    for _ in range(2):
        send_key(VK["down"])
        time.sleep(0.12)
    send_key(VK["ret"])
    time.sleep(1.5)
    load = client_capture(hwnd)
    save("screen_load", load)

    send_key(VK["esc"])
    time.sleep(0.8)
    save("title_final", client_capture(hwnd))

    (OUT / "drive_client_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
