# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ui-preview"
DST = ROOT.parent / "renpy-angelic" / "game" / "images" / "angelic"


def ensure(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def copy_file(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    ensure(dst.parent)
    shutil.copy2(src, dst)
    return True


def sync_tree(src_root: Path, dst_root: Path, exts=None):
    exts = None if exts is None else {e.lower() for e in exts}
    count = 0
    for src in src_root.rglob("*"):
        if not src.is_file():
            continue
        if exts is not None and src.suffix.lower() not in exts:
            continue
        rel = src.relative_to(src_root)
        dst = dst_root / rel
        ensure(dst.parent)
        shutil.copy2(src, dst)
        count += 1
    return count


def collect_source_manifest() -> dict:
    data_js = SRC / "data.js"
    if data_js.exists():
        text = data_js.read_text(encoding="utf-8", errors="replace")
        return {"has_data_js": True, "size": len(text)}
    return {"has_data_js": False, "size": 0}


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync Angelic UI preview assets into renpy-angelic")
    ap.add_argument("--clean", action="store_true", help="remove destination tree before copying")
    args = ap.parse_args()

    if args.clean and DST.exists():
        shutil.rmtree(DST)
    ensure(DST)

    copied = 0
    if SRC.exists():
        # skip ref/ (JP locale stamps with non-ASCII names; not needed at runtime)
        for child in (SRC / "assets").iterdir() if (SRC / "assets").exists() else []:
            if child.name == "ref":
                continue
            if child.is_dir():
                copied += sync_tree(child, DST / child.name, exts={".png", ".jpg", ".jpeg", ".webp", ".gif", ".json", ".txt", ".toml", ".ini", ".csv"})
            elif child.is_file() and child.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".json"}:
                if copy_file(child, DST / child.name):
                    copied += 1
        copied += sync_tree(SRC, DST, exts={".json"})
        copied += copy_file(SRC / "data.js", DST.parent.parent / "angelic_preview_data.js")
        copied += copy_file(SRC / "ASSET-MANIFEST.json", DST.parent.parent / "ASSET-MANIFEST.json")

    manifest = {
        "source": str(SRC),
        "destination": str(DST),
        "copied": copied,
        "preview": collect_source_manifest(),
    }
    (DST.parent.parent / "sync-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
