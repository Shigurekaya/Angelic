#!/usr/bin/env python3
"""对 static-offline 做全量 HxNames 路径还原 → static-offline-named/ + unmatched/。"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import HXNAMES, UI_EXTRACT

SRC = UI_EXTRACT / "static-offline"
DST = UI_EXTRACT / "static-offline-named"
UNMATCHED = UI_EXTRACT / "static-offline-unmatched"
REPORT = UI_EXTRACT / "static-force" / "rename-static-offline-report.json"


def load_hx() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in HXNAMES.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        h, name = line.split(":", 1)
        out[h.strip().upper()] = name.strip().replace("\\", "/")
    return out


def resolve(p: Path, pack_root: Path, hx: dict[str, str]) -> str | None:
    rel = p.relative_to(pack_root)
    parts = list(rel.parts)
    if len(parts) < 2:
        return hx.get(p.name.upper())
    dhash, fhash = parts[0].upper(), parts[-1].upper()
    fname = hx.get(fhash)
    dname = hx.get(dhash)
    if fname and dname:
        return f"{dname.rstrip('/')}/{fname}"
    if fname:
        return fname
    return None


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}")
    hx = load_hx()
    for d in (DST, UNMATCHED):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)

    named = unmatched = 0
    per_pack = {}
    for pack_dir in sorted(p for p in SRC.iterdir() if p.is_dir()):
        n_ok = n_bad = 0
        for p in pack_dir.rglob("*"):
            if not p.is_file():
                continue
            resolved = resolve(p, pack_dir, hx)
            if resolved:
                dest = DST / pack_dir.name / resolved
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(p, dest)
                named += 1
                n_ok += 1
            else:
                dest = UNMATCHED / pack_dir.name / p.relative_to(pack_dir)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    shutil.copy2(p, dest)
                unmatched += 1
                n_bad += 1
        per_pack[pack_dir.name] = {"named": n_ok, "unmatched": n_bad}
        print(f"{pack_dir.name}: named={n_ok} unmatched={n_bad}", flush=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "src": str(SRC),
        "dst": str(DST),
        "unmatched_dir": str(UNMATCHED),
        "hx_entries": len(hx),
        "named": named,
        "unmatched": unmatched,
        "per_pack": per_pack,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("report", REPORT)


if __name__ == "__main__":
    main()
