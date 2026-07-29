# -*- coding: utf-8 -*-
"""Build a macro expansion registry from recovered Kirikiri scripts."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/ui-extract/recovered-scenarios"
OUT = ROOT / "docs/ui-extract/kirikiri-macro-expansion.json"
MACRO_START = re.compile(r"^\s*\[macro\s+name=(?P<name>[^\]\s]+|\"[^\"]+\")(?P<args>[^\]]*)\]\s*$", re.I)
MACRO_END = re.compile(r"^\s*\[endmacro\]\s*$", re.I)
LABEL = re.compile(r"^\s*\*(?P<name>[^|\s]+)(?:\|(?P<title>.*))?$")
CMD = re.compile(r"^\s*(?:@(?P<at>[^\s]+)|\[(?P<br>[^\s\]]+))(?:\s+(?P<args>.*?))?\]?\s*$")


def clean_name(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    return raw


def parse_body(lines):
    out = []
    for line_no, line in lines:
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        if LABEL.match(line):
            out.append({"kind": "label", "raw": line.rstrip(), "line": line_no})
            continue
        m = CMD.match(line)
        if m:
            name = m.group("at") or m.group("br")
            raw_args = (m.group("args") or "").strip()
            out.append({"kind": "command", "name": name, "args": raw_args, "line": line_no})
            continue
        out.append({"kind": "text", "raw": line.rstrip(), "line": line_no})
    return out


def main() -> None:
    registry = {}
    current = None
    for path in sorted(SOURCE.rglob("*.ks")):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines, 1):
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
                registry.setdefault(current["name"], []).append({
                    "file": current["file"],
                    "start_line": current["start_line"],
                    "end_line": current["end_line"],
                    "body": parse_body(current["body"]),
                })
                current = None
                continue
            current["body"].append((i, line))
    # summarize replacements for overlapping macro names
    summary = {}
    for name, defs in registry.items():
        summary[name] = {
            "count": len(defs),
            "files": [d["file"] for d in defs],
            "first_body": defs[0]["body"][:10] if defs else [],
        }
    OUT.write_text(json.dumps({"summary": summary, "definitions": registry}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"macro_names": len(summary), "definitions": sum(v["count"] for v in summary.values())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
