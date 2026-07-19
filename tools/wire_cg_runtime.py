# -*- coding: utf-8 -*-
"""Wire Angelic EXTRA CG thumbs from full-static/upgrade + cglist.csv → renpy."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HX = ROOT / "tools/vendor/ten_sz_hxnames/HxNames-Tenshi.lst"
CGLIST = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/main/cglist.csv"
FULL = ROOT / "docs/ui-extract/full-static"
PREV = ROOT / "ui-preview/assets/cg"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/cg"

# group code in cglist → UI id / CN label (天使☆嚣嚣)
GROUP_META = [
    ("noa", "乃爱"),
    ("ama", "天音"),
    ("kur", "久远"),
    ("kag", "神乐耶"),
    ("ori", "绪理"),
    ("fum", "文"),
    ("etc", "其他"),
    ("sd", "SD"),
]


def load_hx() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in HX.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        h, name = line.split(":", 1)
        out[h.strip().upper()] = name.strip().replace("\\", "/")
    return out


def build_hash_index() -> dict[str, Path]:
    """filename lower -> path under full-static (prefer png over psb)."""
    hx = load_hx()
    # reverse: basename -> hash
    name_to_hash: dict[str, str] = {}
    for h, name in hx.items():
        base = Path(name).name.lower()
        name_to_hash[base] = h
        name_to_hash[name.lower()] = h

    # file hash -> path
    hash_to_path: dict[str, Path] = {}
    for p in FULL.rglob("*"):
        if p.is_file() and len(p.name) >= 32:
            hash_to_path[p.name.upper()] = p

    resolved: dict[str, Path] = {}
    for base, h in name_to_hash.items():
        if not base.startswith("thum_"):
            continue
        path = hash_to_path.get(h)
        if path is None:
            continue
        # prefer .png names
        if base.endswith(".png") or base.endswith(".jpg"):
            key = Path(base).stem.lower()
            # png preferred over psb sibling
            if key not in resolved or path.suffix.lower() != ".psb":
                resolved[key] = path
        elif base.endswith(".psb"):
            key = Path(base).stem.lower()
            if key not in resolved:
                resolved[key] = path
    return resolved


def parse_cglist(text: str) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(":,") or line.startswith("："):
            cur = line.split(",", 1)[1].strip().lower()
            groups[cur] = []
            continue
        if cur is None:
            continue
        parts = [p.strip() for p in line.split(",")]
        if not parts or not parts[0]:
            continue
        thumb = parts[0]
        frames = [p for p in parts[1:] if p]
        groups[cur].append({"thumb": thumb, "frames": frames})
    return groups


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def main() -> None:
    raw = CGLIST.read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif raw[:3] == b"\xef\xbb\xbf":
        text = raw.decode("utf-8-sig")
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("cp932", errors="replace")

    groups = parse_cglist(text)
    print("cglist groups", {k: len(v) for k, v in groups.items()})

    index = build_hash_index()
    print("thum index", len(index))

    thumbs_dir = ensure(PREV / "thumbs")
    ensure(RENPY / "thumbs")

    group_thumbs: dict[str, list[str]] = {}
    cg_entries: dict[str, list[dict]] = {}
    copied = 0
    missing = []

    for code, label in GROUP_META:
        entries = groups.get(code) or []
        stems = []
        rich = []
        for e in entries:
            stem = e["thumb"]
            if stem.lower().endswith((".png", ".jpg")):
                stem = Path(stem).stem
            stems.append(stem)
            rich.append(e)
            src = index.get(stem.lower())
            if src is None:
                missing.append(stem)
                continue
            # detect image
            data = src.read_bytes()[:16]
            ext = ".png"
            if data.startswith(b"\xff\xd8"):
                ext = ".jpg"
            elif data.startswith(b"PSB") or data.startswith(b"psb"):
                # skip FreeMote for now
                missing.append(stem + "(psb)")
                continue
            dst = thumbs_dir / f"{stem}{ext}"
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
                copied += 1
        group_thumbs[code] = stems
        cg_entries[code] = rich

    meta = {
        "groups": [{"id": c, "label": lab} for c, lab in GROUP_META],
        "group_thumbs": group_thumbs,
        "cg_entries": cg_entries,
        "page_size": 16,
        "cells": [],  # filled at runtime as 4x4 grid
        "grid": {"x0": 88, "y0": 180, "cw": 260, "ch": 146, "cols": 4, "rows": 4, "gap_x": 24, "gap_y": 20},
        "copied": copied,
        "missing_count": len(missing),
        "missing_sample": missing[:20],
    }
    # precompute cell rects
    g = meta["grid"]
    cells = []
    for r in range(g["rows"]):
        for c in range(g["cols"]):
            cells.append(
                {
                    "x": g["x0"] + c * (g["cw"] + g["gap_x"]),
                    "y": g["y0"] + r * (g["ch"] + g["gap_y"]),
                    "w": g["cw"],
                    "h": g["ch"],
                }
            )
    meta["cells"] = cells

    (PREV / "cg_hotspots.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    # sync thumbs + meta to renpy
    if (RENPY / "thumbs").exists():
        shutil.rmtree(RENPY / "thumbs")
    shutil.copytree(thumbs_dir, RENPY / "thumbs")
    shutil.copy2(PREV / "cg_hotspots.json", RENPY / "cg_hotspots.json")
    # also game root convenience
    game = RENPY.parent.parent
    shutil.copy2(PREV / "cg_hotspots.json", game / "cg_hotspots.json")

    print(json.dumps({
        "copied": copied,
        "missing": len(missing),
        "missing_sample": missing[:15],
        "thumbs_on_disk": len(list(thumbs_dir.glob("*"))),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
