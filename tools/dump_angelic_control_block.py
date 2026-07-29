#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性从 tenshi_sz 进程内存抓取 Cx control block（之后全程离线）。

必须用 32-bit Python：
  D:\\gamedev\\CafeStella\\tools\\vendor\\python311-x86\\python.exe tools\\dump_angelic_control_block.py
"""
from __future__ import annotations

import json
import struct
import subprocess
import sys
import time
from ctypes import Structure, byref, c_size_t, create_string_buffer, sizeof, windll, wintypes
from datetime import datetime, timezone
from pathlib import Path

GAME = Path(r"E:\GAL\天使☆嚣嚣")
EXE = GAME / "tenshi_sz.exe"
OUT = Path(r"D:\gamedev\Angelic\docs\ui-extract\static-force\keys")
REPORT = OUT / "control-block-report.json"

PROCESS_ALL_ACCESS = 0x1F0FFF
MEM_COMMIT = 0x1000
READABLE = {0x02, 0x04, 0x08, 0x20, 0x40, 0x80}
kernel32 = windll.kernel32
CB_SIG = b" Encryption control block"
CB_SIG_INV = bytes((~b) & 0xFF for b in CB_SIG)


class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [
        ("BaseAddress", wintypes.LPVOID),
        ("AllocationBase", wintypes.LPVOID),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def kill_game() -> None:
    for name in ("tenshi_sz.exe", "CxdecExtractorLoader.exe", "CxdecExtractor.exe"):
        subprocess.run(["taskkill", "/IM", name, "/F"], capture_output=True)


def find_pid(name: str) -> int | None:
    out = subprocess.check_output(
        ["tasklist", "/FI", f"IMAGENAME eq {name}", "/FO", "CSV", "/NH"],
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    for line in out.splitlines():
        parts = [p.strip().strip('"') for p in line.split(",")]
        if len(parts) >= 2 and parts[0].lower() == name.lower():
            return int(parts[1])
    return None


def iter_regions(hproc):
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    while address < 0x7FFF0000:
        if not kernel32.VirtualQueryEx(hproc, address, byref(mbi), sizeof(mbi)):
            break
        base = mbi.BaseAddress or 0
        size = mbi.RegionSize or 0
        if mbi.State == MEM_COMMIT and (mbi.Protect & 0xFF) in READABLE and size:
            yield base, size
        nxt = base + size if size else address + 0x1000
        if nxt <= address:
            break
        address = nxt


def read_mem(hproc, addr: int, size: int) -> bytes | None:
    buf = create_string_buffer(size)
    n = c_size_t(0)
    if not kernel32.ReadProcessMemory(hproc, addr, buf, size, byref(n)) or not n.value:
        return None
    return buf.raw[: n.value]


def dump_control_blocks(pid: int) -> list[dict]:
    hproc = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not hproc:
        raise OSError(f"OpenProcess failed err={kernel32.GetLastError()}")
    OUT.mkdir(parents=True, exist_ok=True)
    found = []
    for base, size in iter_regions(hproc):
        off = 0
        while off < size:
            chunk = min(size - off, 4 * 1024 * 1024)
            data = read_mem(hproc, base + off, chunk)
            if not data:
                off += chunk
                continue
            for label, sig in (("raw", CB_SIG), ("inv", CB_SIG_INV)):
                start = 0
                while True:
                    idx = data.find(sig, start)
                    if idx < 0:
                        break
                    abs_addr = base + off + idx
                    # Signature often sits at start of 0x1000 block of inverted u32s
                    for delta in (0, -0x1000, 0x18, 0x20):
                        addr = abs_addr + delta
                        if addr < 0:
                            continue
                        block = read_mem(hproc, addr, 0x1000)
                        if not block or len(block) != 0x1000:
                            continue
                        raw_path = OUT / f"control_block_{label}_{addr:08x}.bin"
                        raw_path.write_bytes(block)
                        u32 = list(struct.unpack("<1024I", block))
                        inv = struct.pack("<1024I", *[((~x) & 0xFFFFFFFF) for x in u32])
                        inv_path = OUT / f"control_block_{label}_{addr:08x}.inv.bin"
                        inv_path.write_bytes(inv)
                        # also dump "already inverted" interpretation (no ~)
                        asis_path = OUT / f"control_block_{label}_{addr:08x}.asis.bin"
                        asis_path.write_bytes(block)
                        found.append(
                            {
                                "label": label,
                                "sig_addr": hex(abs_addr),
                                "dump_addr": hex(addr),
                                "delta": delta,
                                "raw": str(raw_path),
                                "inv": str(inv_path),
                                "asis": str(asis_path),
                            }
                        )
                        log(f"CB {label} sig@{hex(abs_addr)} dump@{hex(addr)} delta={delta}")
                    start = idx + 4
            off += chunk
    kernel32.CloseHandle(hproc)
    return found


def main() -> None:
    if struct.calcsize("P") * 8 != 32:
        raise SystemExit("need 32-bit python (python311-x86)")
    OUT.mkdir(parents=True, exist_ok=True)
    kill_game()
    time.sleep(1)
    log(f"launch {EXE}")
    subprocess.Popen([str(EXE)], cwd=str(GAME))
    pid = None
    for _ in range(120):
        pid = find_pid("tenshi_sz.exe")
        if pid:
            break
        time.sleep(0.5)
    if not pid:
        raise SystemExit("tenshi_sz.exe not started")
    log(f"pid={pid} waiting for cxdec init...")
    time.sleep(25)
    log("scan memory for control block signature...")
    found = dump_control_blocks(pid)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pid": pid,
        "control_blocks": found,
        "count": len(found),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"found {len(found)} candidate dump(s) -> {REPORT}")
    kill_game()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
