#!/usr/bin/env python3
"""静态索引 Angelic XP3（哈希文件名），不启动游戏。"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import GAME, INDEXES, UI_ARCHIVES, EXCLUDE_ARCHIVES, HXNAMES


def load_hxnames(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        h, name = line.split(":", 1)
        out[h.strip().upper()] = name.strip()
    return out


def index_one(xp3: Path, hx: dict[str, str]) -> dict:
    from tamago.formats.xp3 import XP3File

    entries = []
    encrypted = 0
    xp = XP3File(xp3)
    try:
        for i, f in enumerate(xp.files):
            if f.encrypted:
                encrypted += 1
            name = str(f.file_name)
            # hashed names are opaque chars; also try hex of name bytes
            resolved = hx.get(name.upper())
            if not resolved:
                try:
                    resolved = hx.get(name.encode("utf-16-le").hex().upper())
                except Exception:
                    resolved = None
            entries.append(
                {
                    "index": i,
                    "name": name,
                    "name_ord": [ord(c) for c in name[:32]],
                    "resolved": resolved,
                    "original_size": int(f.original_size or 0),
                    "compressed_size": int(f.compressed_size or 0),
                    "encrypted": bool(f.encrypted),
                    "key": int(f.key) if f.key is not None else None,
                }
            )
    finally:
        xp.close()
    resolved_n = sum(1 for e in entries if e["resolved"])
    return {
        "archive": xp3.name,
        "path": str(xp3),
        "bytes": xp3.stat().st_size,
        "files": len(entries),
        "encrypted": encrypted,
        "hx_resolved": resolved_n,
        "entries": entries,
    }


def main() -> None:
    INDEXES.mkdir(parents=True, exist_ok=True)
    hx = load_hxnames(HXNAMES)
    targets = []
    for n in UI_ARCHIVES:
        p = GAME / n
        if p.exists():
            targets.append(p)
    # also index all non-excluded for inventory
    for p in sorted(GAME.glob("*.xp3")):
        if p.name.lower() in {x.lower() for x in EXCLUDE_ARCHIVES}:
            continue
        if p not in targets:
            targets.append(p)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hxnames": str(HXNAMES),
        "hx_entries": len(hx),
        "archives": [],
    }
    for xp3 in targets:
        print(f"index {xp3.name} ...", flush=True)
        try:
            info = index_one(xp3, hx)
        except Exception as e:
            info = {"archive": xp3.name, "error": repr(e)}
        report["archives"].append({k: v for k, v in info.items() if k != "entries"})
        out = INDEXES / f"{xp3.stem}.json"
        out.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {out} files={info.get('files')} hx={info.get('hx_resolved')}", flush=True)

    summary = INDEXES / "summary.json"
    summary.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"summary -> {summary}", flush=True)


if __name__ == "__main__":
    main()
