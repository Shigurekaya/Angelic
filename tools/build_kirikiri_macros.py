# -*- coding: utf-8 -*-
"""Extract Kirikiri macro definitions into an auditable registry."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/ui-extract/recovered-scenarios"
OUT = ROOT / "docs/ui-extract/kirikiri-macros.json"
MACRO_START = re.compile(r"^\s*\[macro\s+name=(?P<name>[^\]\s]+|\"[^\"]+\")(?P<args>[^\]]*)\]\s*$", re.I)
MACRO_END = re.compile(r"^\s*\[endmacro\]\s*$", re.I)
COMMAND = re.compile(r"^\s*(?:@(?P<at>[^\s]+)|\[(?P<br>[^\s\]]+))(?:\s+(?P<args>.*?))?\]?\s*$")


def clean_name(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    return raw


def main() -> None:
    macros = []
    current = None
    for path in sorted(SOURCE.rglob("*.ks")):
        text = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(text, 1):
            if current is None:
                m = MACRO_START.match(line)
                if m:
                    current = {
                        "name": clean_name(m.group("name")),
                        "file": path.relative_to(SOURCE).as_posix(),
                        "start_line": i,
                        "body": [],
                    }
                continue
            if MACRO_END.match(line):
                current["end_line"] = i
                macros.append(current)
                current = None
                continue
            if line.strip():
                current["body"].append({"line": i, "text": line.rstrip("\n")})
    registry = {}
    for m in macros:
        body = m["body"]
        registry.setdefault(m["name"], []).append({
            "file": m["file"],
            "start_line": m["start_line"],
            "end_line": m.get("end_line"),
            "body_lines": len(body),
            "preview": [x["text"] for x in body[:8]],
        })
    OUT.write_text(json.dumps({"macro_count": len(macros), "macros": registry}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"macro_count": len(macros), "macro_names": len(registry)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
