# -*- coding: utf-8 -*-
"""Recover readable Kirikiri scenario files from GARbro hash extraction output."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path(r"E:\GAL\天使☆嚣嚣\Extractor_Output")
DEFAULT_OUTPUT = ROOT / "docs/ui-extract/recovered-scenarios"
TEXT_EXTENSIONS = {".ks", ".tjs", ".txt", ".csv", ".asd", ".stand"}
KAG_TAG = re.compile(r"(?m)^\s*(?:\[[A-Za-z_][^\]\r\n]*\]|@[A-Za-z_][^\r\n]*)")
LABEL = re.compile(r"(?m)^\s*\*[A-Za-z0-9_\-\u3000-\u9fff]+")


def decode_text(data: bytes) -> tuple[str | None, str | None]:
    if data.startswith(b"\xef\xbb\xbf"):
        candidates = ("utf-8-sig",)
    elif data.startswith((b"\xff\xfe", b"\xfe\xff")):
        candidates = ("utf-16",)
    else:
        candidates = ("cp932", "utf-8", "utf-16le")
    for encoding in candidates:
        try:
            text = data.decode(encoding)
        except UnicodeDecodeError:
            continue
        if "\x00" in text[:100] and encoding != "utf-16le":
            continue
        return text, encoding
    return None, None


def classify(text: str) -> tuple[str | None, int]:
    tags = len(KAG_TAG.findall(text))
    labels = len(LABEL.findall(text))
    dialogue = sum(1 for line in text.splitlines() if line.strip() and not line.lstrip().startswith((";", "#", "[", "@", "*")))
    score = tags * 4 + labels * 3 + min(dialogue, 30)
    if tags >= 2 or (tags and labels) or (labels >= 2 and dialogue >= 3):
        return ".ks", score
    return None, score


def load_names(path: Path | None) -> dict[str, str]:
    names: dict[str, str] = {}
    if not path or not path.exists():
        return names
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        digest, name = line.split(":", 1)
        names[digest.strip().upper()] = name.strip().replace("\\", "/")
    return names


def iter_payloads(source: Path):
    for archive in ("data", "adult", "adult2", "adult3", "upgrade", "upgrade2", "upgrade3"):
        root = source / archive
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                yield archive, path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--names", type=Path, default=ROOT / "tools/vendor/ten_sz_hxnames/HxNames-Tenshi.lst")
    parser.add_argument("--min-score", type=int, default=8)
    args = parser.parse_args()

    names = load_names(args.names)
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = []
    counts = Counter()

    for archive, source_path in iter_payloads(args.source):
        counts["scanned"] += 1
        data = source_path.read_bytes()
        if len(data) < 8 or len(data) > 8_000_000:
            continue
        text, encoding = decode_text(data)
        if text is None:
            continue
        extension, score = classify(text)
        digest = source_path.name.upper()
        known_name = names.get(digest)
        if known_name and Path(known_name).suffix.lower() in TEXT_EXTENSIONS:
            relative = Path(archive) / "named" / Path(known_name)
            extension = Path(known_name).suffix.lower()
        elif extension and score >= args.min_score:
            relative = Path(archive) / "detected" / f"{digest}{extension}"
        else:
            continue
        destination = args.output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
        counts[extension] += 1
        manifest.append({
            "archive": archive,
            "source": str(source_path),
            "output": relative.as_posix(),
            "name": known_name,
            "encoding": encoding,
            "score": score,
            "bytes": len(data),
        })

    manifest.sort(key=lambda row: (row["archive"], row["output"]))
    (args.output / "manifest.json").write_text(json.dumps({
        "counts": dict(counts),
        "files": manifest,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(dict(counts), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
