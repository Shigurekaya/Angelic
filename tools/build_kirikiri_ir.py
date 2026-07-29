# -*- coding: utf-8 -*-
"""Parse recovered KAG/Kirikiri scripts into an auditable migration IR."""
from __future__ import annotations

import json
import re
import shlex
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/ui-extract/recovered-scenarios"
OUTPUT = ROOT / "docs/ui-extract/kirikiri-ir.json"
TAG = re.compile(r"^\s*(?:@(?P<at>[^\s]+)(?:\s+(?P<args>.*))?|\[(?P<br>[^\s\]]+)(?:\s+(?P<bargs>.*?))?\])\s*$")
LABEL = re.compile(r"^\s*\*(?P<name>[^|\s]+)(?:\|(?P<title>.*))?$")
ATTR = re.compile(r"([\w\u3000-\u9fff]+)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\]]+))")
STORAGE = re.compile(r"(?:storage|file)\s*=\s*[\"']?([^\"'\s\]]+)", re.I)


def attrs(raw: str) -> dict[str, str]:
    return {m.group(1): next(v for v in m.groups()[1:] if v is not None) for m in ATTR.finditer(raw or "")}


def parse_file(path: Path) -> dict:
    commands = []
    labels = []
    references = []
    text_lines = 0
    for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith(";"):
            continue
        lm = LABEL.match(raw)
        if lm:
            item = {"type": "label", "name": lm.group("name"), "title": (lm.group("title") or "").strip(), "line": number}
            labels.append(item)
            commands.append(item)
            continue
        tm = TAG.match(raw)
        if tm:
            name = tm.group("at") or tm.group("br")
            raw_args = tm.group("args") or tm.group("bargs") or ""
            item = {"type": "command", "name": name, "attrs": attrs(raw_args), "raw": raw_args, "line": number}
            commands.append(item)
            for match in STORAGE.finditer(raw_args):
                references.append({"storage": match.group(1), "command": name, "line": number})
            continue
        text_lines += 1
        commands.append({"type": "text", "text": stripped, "line": number})
    return {
        "path": path.relative_to(SOURCE).as_posix(),
        "labels": labels,
        "references": references,
        "commands": commands,
        "stats": {"commands": len(commands), "labels": len(labels), "references": len(references), "text_lines": text_lines},
    }


def main() -> None:
    files = []
    command_counts = Counter()
    references = defaultdict(list)
    for path in sorted(SOURCE.rglob("*.ks")):
        doc = parse_file(path)
        files.append(doc)
        for command in doc["commands"]:
            if command["type"] == "command":
                command_counts[command["name"]] += 1
        for ref in doc["references"]:
            references[ref["storage"]].append({"from": doc["path"], "line": ref["line"], "command": ref["command"]})
    payload = {
        "source": str(SOURCE),
        "file_count": len(files),
        "command_counts": dict(command_counts.most_common()),
        "storage_references": dict(sorted(references.items())),
        "files": files,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"files": len(files), "commands": sum(command_counts.values()), "command_types": len(command_counts), "storages": len(references)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
