# -*- coding: utf-8 -*-
"""天使☆嚣嚣：全部 XP3 静态强解（Cxdec 运行时解密）。

已解包则跳过。强制重解用 --force。
需 32-bit Python（与 CafeStella / _run_cxdec_*_x86 相同）。
"""
from __future__ import annotations

import argparse
import ctypes
import json
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

GAME = Path(r"E:\GAL\天使☆嚣嚣")
OUT_DOC = Path(r"D:\gamedev\Angelic\docs\ui-extract\static-force")
FULL_OUT = Path(r"D:\gamedev\Angelic\docs\ui-extract\full-static")
MDLOG = Path(r"D:\gamedev\Angelic\docs\ui-extract\FULL-STATIC-UNPACK-LOG.md")
EXTRACT_OUT = GAME / "Extractor_Output"
LOG = OUT_DOC / "full-static-all.log"
REPORT = OUT_DOC / "full-static-all-report.json"
GAME_EXE_NAME = "tenshi_sz.exe"

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
kernel32 = ctypes.windll.kernel32
BM_CLICK = 0x00F5
WM_DROPFILES = 0x0233
WM_CLOSE = 0x0010
GMEM_MOVEABLE = 0x0002
GMEM_ZEROINIT = 0x0040
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class DROPFILES(ctypes.Structure):
    _fields_ = [
        ("pFiles", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("fNC", wintypes.BOOL),
        ("fWide", wintypes.BOOL),
    ]


def log(msg: str) -> None:
    line = "[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg)
    try:
        print(line)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((line + "\n").encode("utf-8", "replace"))
    sys.stdout.flush()
    OUT_DOC.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def enum_wins(visible_only=True):
    hits = []

    def cb(hwnd, _):
        if (not visible_only) or user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            if buf.value:
                hits.append((hwnd, buf.value))
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return hits


def buttons(hwnd):
    out = []
    child = 0
    while True:
        child = user32.FindWindowExW(hwnd, child, "Button", None)
        if not child:
            return out
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(child, buf, 256)
        out.append((child, buf.value))


def mouse_click(hwnd):
    parent = user32.GetAncestor(hwnd, 2) or hwnd
    user32.SetForegroundWindow(parent)
    time.sleep(0.25)
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2
    user32.SetCursorPos(cx, cy)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    user32.SendMessageW(hwnd, BM_CLICK, 0, 0)


def dismiss_errors():
    for h, t in enum_wins():
        low = t.lower()
        if any(
            k in t or k in low
            for k in ("Steam Error", "Application load error", "错误", "失敗", "失败", "Protect")
        ):
            for c, _ in buttons(h):
                user32.SendMessageW(c, BM_CLICK, 0, 0)
            user32.PostMessageW(h, WM_CLOSE, 0, 0)


def find_loader():
    for h, t in enum_wins():
        if "CxdecExtractorLoader" in t:
            return h
    return None


def find_extracts():
    return [h for h, t in enum_wins() if t.strip() == "CxdecExtractor"]


def find_pid(name):
    out = subprocess.check_output(
        ["tasklist", "/FI", "IMAGENAME eq %s" % name, "/FO", "CSV", "/NH"],
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) >= 2 and parts[0].lower() == name.lower():
            return int(parts[1])
    return None


def count_files(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for p in root.rglob("*") if p.is_file())


def drop_post(hwnd, path):
    path = str(Path(path).resolve())
    payload = (path + "\0\0").encode("utf-16-le")
    size = ctypes.sizeof(DROPFILES) + len(payload)
    hglob = kernel32.GlobalAlloc(GMEM_MOVEABLE | GMEM_ZEROINIT, size)
    ptr = kernel32.GlobalLock(hglob)
    df = DROPFILES.from_address(ptr)
    df.pFiles = ctypes.sizeof(DROPFILES)
    df.fNC = False
    df.fWide = True
    ctypes.memmove(ptr + ctypes.sizeof(DROPFILES), payload, len(payload))
    kernel32.GlobalUnlock(hglob)
    shell32.DragAcceptFiles(hwnd, True)
    ok = user32.PostMessageW(hwnd, WM_DROPFILES, hglob, 0)
    log("PostMessage drop %s hwnd=%s ok=%s" % (Path(path).name, hwnd, ok))
    return ok


def kill_all():
    for exe in (GAME_EXE_NAME, "CxdecExtractorLoader.exe", "SmartSteamLoader.exe", "KrkrDumpLoader.exe"):
        subprocess.call(["taskkill", "/IM", exe, "/F"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def boot(boot_wait=50):
    dismiss_errors()
    loader = find_loader()
    if not loader:
        log("launch CxdecExtractorLoader + tenshi_sz.exe")
        subprocess.Popen(
            [str(GAME / "CxdecExtractorLoader.exe"), str(GAME / GAME_EXE_NAME)],
            cwd=str(GAME),
        )
        for _ in range(90):
            dismiss_errors()
            loader = find_loader()
            if loader:
                break
            time.sleep(0.4)
    if not loader:
        raise SystemExit("no loader window")
    bs = buttons(loader)
    target = next((c for c, t in bs if "解包" in t), bs[0][0] if bs else None)
    if not target:
        raise SystemExit("no unpack button")
    mouse_click(target)
    log("clicked unpack module")
    for _ in range(120):
        dismiss_errors()
        if find_extracts() and find_pid(GAME_EXE_NAME):
            break
        time.sleep(0.5)
    if not find_extracts() or not find_pid(GAME_EXE_NAME):
        raise SystemExit("boot failed")
    log("pid=%s boot_wait=%ss" % (find_pid(GAME_EXE_NAME), boot_wait))
    time.sleep(boot_wait)
    if not find_pid(GAME_EXE_NAME):
        raise SystemExit("game died during boot")
    return find_extracts()


def wait_done(name, before, timeout, stable=50):
    end = time.time() + timeout
    last = before
    stable_at = time.time()
    while time.time() < end:
        dismiss_errors()
        if not find_pid(GAME_EXE_NAME):
            log("game died during %s" % name)
            return count_files(EXTRACT_OUT)
        now = count_files(EXTRACT_OUT)
        if now != last:
            log("%s files=%s (+%s)" % (name, now, now - before))
            last = now
            stable_at = time.time()
        elif now > before and time.time() - stable_at > stable:
            break
        time.sleep(3)
    return count_files(EXTRACT_OUT)


def timeout_for(path: Path) -> int:
    mb = path.stat().st_size / (1024 * 1024)
    return int(max(900, mb * 12))


def organize():
    FULL_OUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    for src in sorted(EXTRACT_OUT.iterdir()) if EXTRACT_OUT.exists() else []:
        if not src.is_dir():
            continue
        dest = FULL_OUT / src.name
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
        n = count_files(dest)
        summary[src.name] = {"files": n, "status": "ok"}
        log("organized %s files=%s" % (src.name, n))
    for alst in EXTRACT_OUT.glob("*.alst") if EXTRACT_OUT.exists() else []:
        shutil.copy2(alst, FULL_OUT / alst.name)
    return summary


def inventory_only():
    archives = sorted(GAME.glob("*.xp3"))
    rows = []
    for p in archives:
        stem = p.stem
        dest = FULL_OUT / stem
        n = count_files(dest)
        rows.append({"archive": p.name, "size_mb": round(p.stat().st_size / 1e6, 1), "files": n, "done": n > 0})
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "inventory",
        "full_out": str(FULL_OUT),
        "total_files": count_files(FULL_OUT),
        "archives": rows,
        "all_done": all(r["done"] for r in rows),
    }
    OUT_DOC.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main():
    if ctypes.sizeof(ctypes.c_void_p) != 4:
        # still allow --inventory on 64-bit
        ap = argparse.ArgumentParser()
        ap.add_argument("--inventory", action="store_true")
        ap.add_argument("--force", action="store_true")
        args, _ = ap.parse_known_args()
        if args.inventory:
            inventory_only()
            return
        sys.exit("need 32-bit python to run Cxdec unpack (use --inventory on 64-bit)")

    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="re-extract even if folder exists")
    ap.add_argument("--inventory", action="store_true")
    args = ap.parse_args()
    if args.inventory:
        inventory_only()
        return

    archives = sorted(GAME.glob("*.xp3"))
    log("==== FULL static unpack all XP3 ====")
    log("archives=%s" % [p.name for p in archives])
    kill_all()
    time.sleep(1)
    boot(50)
    results = []
    for p in archives:
        stem = p.stem
        done_dir = EXTRACT_OUT / stem
        if not args.force and done_dir.exists() and count_files(done_dir) > 0:
            n = count_files(done_dir)
            log("skip already-done %s files=%s" % (p.name, n))
            results.append({"archive": p.name, "skipped": True, "files": n})
            continue
        if not find_pid(GAME_EXE_NAME) or not find_extracts():
            kill_all()
            time.sleep(2)
            boot(50)
        start = count_files(EXTRACT_OUT)
        for h in find_extracts():
            drop_post(h, p)
        to = timeout_for(p)
        log("%s timeout=%ss" % (p.name, to))
        after = wait_done(p.name, start, timeout=to)
        results.append({"archive": p.name, "added": after - start, "after": after})
        log("%s DONE added=%s" % (p.name, after - start))

    summary = organize()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "CxdecExtractorLoader + PostMessage WM_DROPFILES",
        "results": results,
        "organized": summary,
        "total_files": count_files(FULL_OUT),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log("DONE total=%s report=%s" % (report["total_files"], REPORT))
    kill_all()


if __name__ == "__main__":
    main()
