# -*- coding: utf-8 -*-
"""Manual-drive capture: you click all menus; this saves every distinct client frame.

Usage:
  1. Launch tenshi_sz.exe, leave it foreground (windowed or maximized OK).
  2. Run this script.
  3. Manually open: title / system settings (all tabs) / load-save / CG / flowchart /
     backlog / afterstory / dialogue / etc.
  4. Press Ctrl+C when done.

Saves under:
  docs/ui-extract/pixel-reverse/_orig_capture/manual_session/<stamp>/
    frames/NNNN_tag_hash.png (+ *_1080.png)
    manifest.jsonl
    index.json
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import sys
import time
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _capture_printwindow import find_game_hwnd, user32  # noqa: E402

ROOT = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/_orig_capture")
TLG = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/tlg-png")

# Template stems for rough tagging (bg0 / packs)
TAG_TEMPLATES = {
    "option": "option__bg0.png",
    "title": "title_bg0.png",  # may miss; fallback skip
    "file_load": "file_load__bg0.png",
    "file_save": "file_save__bg0.png",
    "extra": "extra__bg0.png",
    "scnchart": "scnchart__bg0.png",
    "backlog": "backlog__bg0.png",
    "dialog": "dialog__bg0.png",
    "qconf": "qconf__pack.png",
    "window": "window__bg0.png",
}

POLL_S = 0.35
# perceptual hash grid
PHASH_W, PHASH_H = 64, 36
# mean abs pixel diff on small grid to count as "new"
DIFF_NEW = 6.5
# min seconds between two saves even if different (debounce flicker)
MIN_SAVE_GAP = 0.55


def client_rect_screen(hwnd):
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(rect))
    pt = wintypes.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    w, h = rect.right - rect.left, rect.bottom - rect.top
    return pt.x, pt.y, w, h


def grab_client(hwnd) -> Image.Image | None:
    x, y, w, h = client_rect_screen(hwnd)
    if w < 200 or h < 150:
        return None
    im = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    return im.convert("RGBA")


def grid_bytes(im: Image.Image) -> bytes:
    g = im.resize((PHASH_W, PHASH_H), Image.Resampling.BILINEAR).convert("L")
    return g.tobytes()


def mean_abs_diff(a: bytes, b: bytes) -> float:
    if len(a) != len(b) or not a:
        return 999.0
    s = 0
    n = len(a)
    # sample every byte (already tiny)
    for i in range(n):
        s += abs(a[i] - b[i])
    return s / n


def md5_short(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:10]


def load_templates() -> dict[str, bytes]:
    out = {}
    for tag, fname in TAG_TEMPLATES.items():
        p = TLG / fname
        if not p.exists():
            # title_bg may live elsewhere
            alt = Path(r"D:/gamedev/Angelic/docs/ui-extract/ui-cn-jp-static/filtered-cn-jp") / fname
            p = alt if alt.exists() else p
        if p.exists():
            im = Image.open(p).convert("RGBA")
            out[tag] = grid_bytes(im)
    return out


def best_tag(gb: bytes, templates: dict[str, bytes]) -> tuple[str, float]:
    best, score = "unknown", 999.0
    for tag, tb in templates.items():
        d = mean_abs_diff(gb, tb)
        if d < score:
            best, score = tag, d
    # map score to similarity-ish label confidence
    return best, score


def mean_l(im: Image.Image) -> float:
    return float(im.convert("L").resize((1, 1)).getpixel((0, 0)))


def main() -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sess = ROOT / "manual_session" / stamp
    frames = sess / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    templates = load_templates()
    print("templates loaded:", list(templates.keys()))
    print("session:", sess)
    print("Click through ALL menus. Ctrl+C to stop.\n")

    manifest = sess / "manifest.jsonl"
    index: list[dict] = []
    seen_hashes: set[str] = set()
    last_grid: bytes | None = None
    last_save_t = 0.0
    n = 0
    skips = 0

    try:
        while True:
            w = find_game_hwnd()
            if not w:
                print("[wait] no game window…")
                time.sleep(1.0)
                continue
            hwnd = w["hwnd"]
            # do NOT force foreground — user is clicking
            im = grab_client(hwnd)
            if im is None:
                skips += 1
                if skips % 20 == 1:
                    print("[skip] client empty/minimized")
                time.sleep(POLL_S)
                continue
            skips = 0
            gb = grid_bytes(im)
            if last_grid is not None and mean_abs_diff(gb, last_grid) < DIFF_NEW:
                time.sleep(POLL_S)
                continue
            now = time.time()
            if now - last_save_t < MIN_SAVE_GAP:
                time.sleep(POLL_S)
                continue

            h = md5_short(gb)
            if h in seen_hashes:
                last_grid = gb
                time.sleep(POLL_S)
                continue

            tag, dist = best_tag(gb, templates)
            # loose thresholds: smaller dist = closer to template
            if dist > 55:
                tag = "unknown"
            elif dist > 35 and tag != "unknown":
                tag = f"{tag}?"

            n += 1
            name = f"{n:04d}_{tag}_{h}"
            path = frames / f"{name}.png"
            path1080 = frames / f"{name}_1080.png"
            im.save(path)
            im.resize((1920, 1080), Image.Resampling.LANCZOS).save(path1080)
            L = mean_l(im)
            rec = {
                "i": n,
                "file": path.name,
                "file_1080": path1080.name,
                "tag": tag,
                "template_dist": round(dist, 2),
                "hash": h,
                "size": list(im.size),
                "L": round(L, 1),
                "t": datetime.now().isoformat(timespec="seconds"),
            }
            with manifest.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            index.append(rec)
            seen_hashes.add(h)
            last_grid = gb
            last_save_t = now
            print(f"[{n:04d}] {tag:12s} dist={dist:5.1f} L={L:5.1f} {im.size}  {h}")
            time.sleep(POLL_S)
    except KeyboardInterrupt:
        print("\nstopped.")

    (sess / "index.json").write_text(
        json.dumps(
            {
                "session": stamp,
                "count": len(index),
                "frames_dir": str(frames),
                "items": index,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    # also copy latest pointer
    latest = ROOT / "manual_session" / "LATEST.txt"
    latest.write_text(str(sess), encoding="utf-8")
    print(f"saved {len(index)} frames → {sess}")
    print("LATEST →", sess)


if __name__ == "__main__":
    main()
