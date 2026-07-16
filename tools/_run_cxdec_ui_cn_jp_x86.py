#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""天使☆嚣嚣：仅中文/日文界面静态强解（image + data）。

对照 CafeStella `_run_cxdec_ui_cn_jp_x86.py`：
- CxdecExtractorLoader 加载解包模块
- PostMessage(WM_DROPFILES) 拖入 XP3（SendMessage 对本工具无效）
- 排除 voice / 立绘 CG / adult / upgrade

需 32-bit Python。日志写入 docs/ui-extract/static-force/。
"""

from __future__ import annotations

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
UI_OUT = Path(r"D:\gamedev\Angelic\docs\ui-extract\ui-cn-jp-static")
MDLOG = Path(r"D:\gamedev\Angelic\docs\ui-extract\UI-CN-JP-STATIC-UNPACK-LOG.md")
EXTRACT_OUT = GAME / "Extractor_Output"
MIRROR = OUT_DOC / "Extractor_Output"
LOG = OUT_DOC / "ui-cn-jp-static.log"
REPORT = OUT_DOC / "ui-cn-jp-static-report.json"

# 仅中日界面：image（UI 图）+ data（界面脚本/文案）。无独立 uipsd。
ARCHIVES = ["image.xp3", "data.xp3"]
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


def append_md(section: str) -> None:
    MDLOG.parent.mkdir(parents=True, exist_ok=True)
    if not MDLOG.exists():
        MDLOG.write_text(
            "# 天使☆嚣嚣 中日界面静态解包日志\n\n", encoding="utf-8"
        )
    with MDLOG.open("a", encoding="utf-8") as f:
        f.write(section)
        if not section.endswith("\n"):
            f.write("\n")


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
    return cx, cy


def dismiss_errors():
    for h, t in enum_wins():
        low = t.lower()
        if any(
            k in t or k in low
            for k in (
                "Steam Error",
                "Application load error",
                "错误",
                "失敗",
                "失败",
                "Protect",
            )
        ):
            for c, _ in buttons(h):
                user32.SendMessageW(c, BM_CLICK, 0, 0)
            user32.PostMessageW(h, WM_CLOSE, 0, 0)
            log("dismissed: %s" % t)


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
    """CafeStella 经验：必须用 PostMessage，SendMessage 对本 Cxdec 无效。"""
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
    for exe in (
        GAME_EXE_NAME,
        "CafeStella.exe",
        "CxdecExtractorLoader.exe",
        "SmartSteamLoader.exe",
        "KrkrDumpLoader.exe",
        "KrkrzExtract.exe",
    ):
        subprocess.call(
            ["taskkill", "/IM", exe, "/F"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


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
    log("loader=%s" % loader)
    bs = buttons(loader)
    log("buttons=%s" % [t for _, t in bs])
    target = next((c for c, t in bs if "解包" in t), bs[0][0] if bs else None)
    if not target:
        raise SystemExit("no unpack button")
    cx, cy = mouse_click(target)
    log("clicked unpack module @%s,%s" % (cx, cy))

    exh = None
    for _ in range(120):
        dismiss_errors()
        xs = find_extracts()
        if xs and find_pid(GAME_EXE_NAME):
            exh = xs[0]
            break
        time.sleep(0.5)
    if not exh:
        log("FAIL wins=%s" % [t for _, t in enum_wins()][:30])
        raise SystemExit("no extract window / game not running")
    pid = find_pid(GAME_EXE_NAME)
    log("extract=%s pid=%s boot_wait=%ss" % (exh, pid, boot_wait))
    time.sleep(boot_wait)
    if not find_pid(GAME_EXE_NAME):
        raise SystemExit("game died during boot (DRM/protect?)")
    xs = find_extracts()
    return xs[0] if xs else exh


def wait_done(name, before, timeout=1800, stable=45):
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


def organize_ui():
    UI_OUT.mkdir(parents=True, exist_ok=True)
    if not EXTRACT_OUT.exists():
        log("no Extractor_Output")
        return {"copied": 0}
    if MIRROR.exists():
        shutil.rmtree(MIRROR, ignore_errors=True)
    shutil.copytree(EXTRACT_OUT, MIRROR)
    copied = 0
    summary = {}
    for arch in ARCHIVES:
        stem = arch.replace(".xp3", "")
        src = EXTRACT_OUT / stem
        if not src.exists():
            cands = [
                p
                for p in EXTRACT_OUT.iterdir()
                if p.is_dir() and stem.lower() in p.name.lower()
            ]
            src = cands[0] if cands else None
        if not src or not src.exists():
            log("missing folder for %s" % arch)
            summary[stem] = {"files": 0, "status": "missing"}
            continue
        dest = UI_OUT / stem
        if dest.exists():
            shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(src, dest)
        n = count_files(dest)
        copied += n
        summary[stem] = {"files": n, "status": "ok"}
        log("organized %s -> %s (%s files)" % (stem, dest, n))
    for alst in EXTRACT_OUT.glob("*.alst"):
        shutil.copy2(alst, UI_OUT / alst.name)
    return {"copied": copied, "summary": summary, "out": str(UI_OUT)}


def main():
    OUT_DOC.mkdir(parents=True, exist_ok=True)
    log("==== Angelic UI CN/JP static unpack start ====")
    log("scope=%s (CN/JP UI only)" % ",".join(ARCHIVES))
    log("exclude=voice,fgimage,evimage,adult*,upgrade*")
    append_md(
        "\n### %s — 启动 Cxdec 中日界面解包\n\n"
        "- 脚本：`tools/_run_cxdec_ui_cn_jp_x86.py`\n"
        "- 范围：`%s`\n"
        "- 状态：运行中…\n"
        % (datetime.now().strftime("%Y-%m-%d %H:%M"), ",".join(ARCHIVES))
    )
    kill_all()
    time.sleep(1)
    before = count_files(EXTRACT_OUT)
    exh = boot(50)
    results = []
    for name in ARCHIVES:
        p = GAME / name
        if not p.exists():
            log("missing %s" % name)
            continue
        if not find_pid(GAME_EXE_NAME) or not find_extracts():
            log("session lost; reboot")
            kill_all()
            time.sleep(2)
            exh = boot(50)
        xs = find_extracts()
        start = count_files(EXTRACT_OUT)
        for h in xs:
            drop_post(h, p)
        timeout = 2400 if name == "data.xp3" else 1200
        after = wait_done(name, start, timeout=timeout)
        added = after - start
        results.append({"archive": name, "added": added, "after": after})
        log("%s DONE added=%s" % (name, added))
        if added == 0:
            log("WARNING 0 files from %s" % name)

    org = organize_ui()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "game": "天使☆嚣嚣 RE-BOOT (Hikari Field)",
        "scope": "CN/JP UI only",
        "archives": ARCHIVES,
        "excluded": sorted(
            [
                "voice.xp3",
                "fgimage.xp3",
                "evimage.xp3",
                "adult.xp3",
                "adult2.xp3",
                "adult3.xp3",
                "upgrade.xp3",
                "upgrade2.xp3",
                "upgrade3.xp3",
            ]
        ),
        "method": "CxdecExtractorLoader + PostMessage WM_DROPFILES (CafeStella recipe)",
        "before": before,
        "after": count_files(EXTRACT_OUT),
        "results": results,
        "organized": org,
        "paths": {
            "extractor": str(EXTRACT_OUT),
            "mirror": str(MIRROR),
            "ui_out": str(UI_OUT),
            "log": str(LOG),
        },
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log("report -> %s" % REPORT)
    append_md(
        "\n### %s — Cxdec 结束\n\n```json\n%s\n```\n"
        % (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            json.dumps(report, ensure_ascii=False, indent=2),
        )
    )
    log("DONE %s" % report)
    kill_all()


if __name__ == "__main__":
    if ctypes.sizeof(ctypes.c_void_p) != 4:
        sys.exit("need 32-bit python")
    main()
