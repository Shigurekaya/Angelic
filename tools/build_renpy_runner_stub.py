# -*- coding: utf-8 -*-
"""Build a Ren'Py-side Kirikiri runtime helper stub from the IR and op map."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IR = ROOT / "docs/ui-extract/kirikiri-ir.json"
OPMAP = ROOT / "docs/ui-extract/kirikiri-opmap.json"
OUT = ROOT / "docs/ui-extract/kirikiri-runtime-stub.rpy"

TEMPLATE = '''# Auto-generated Kirikiri runtime helper stub

init python:
    kirikiri_ir = {ir_json}
    kirikiri_opmap = {op_json}

    def kirikiri_dispatch(cmd, ctx=None):
        ctx = ctx or {{}}
        name = cmd.get("name") if isinstance(cmd, dict) else None
        attrs = cmd.get("attrs") if isinstance(cmd, dict) else {{}}
        if name == "jump":
            return {{"action": "jump", "target": attrs.get("storage") or attrs.get("target")}}
        if name == "call":
            return {{"action": "call", "target": attrs.get("storage") or attrs.get("target")}}
        if name == "return":
            return {{"action": "return"}}
        if name in ("wait", "wt"):
            return {{"action": "pause", "time": attrs.get("time") or attrs.get("t") or "0"}}
        if name in ("bgm", "se", "sysse", "voice"):
            return {{"action": "audio", "channel": name, "file": attrs.get("storage") or attrs.get("file") or attrs.get("src")}}
        if name in ("scene", "show"):
            return {{"action": "display", "name": name, "attrs": attrs}}
        if name == "eval":
            return {{"action": "eval", "expr": attrs.get("expr") or attrs.get("value")}}
        if name == "if":
            return {{"action": "if", "expr": attrs.get("expr") or attrs.get("cond")}}
        if name in ("シーン回想開始",):
            return {{"action": "replay", "target": attrs.get("target") or attrs.get("storage")}}
        return {{"action": "noop", "name": name, "attrs": attrs}}

    def kirikiri_iter_commands():
        for f in kirikiri_ir.get("files", []):
            for cmd in f.get("commands", []):
                if cmd.get("type") == "command":
                    yield f.get("path"), cmd

label kirikiri_runtime_probe:
    "Kirikiri runtime stub loaded."
    return
'''


def main() -> None:
    ir = json.loads(IR.read_text(encoding="utf-8"))
    op = json.loads(OPMAP.read_text(encoding="utf-8"))
    OUT.write_text(TEMPLATE.format(ir_json=json.dumps(ir, ensure_ascii=False, indent=2), op_json=json.dumps(op, ensure_ascii=False, indent=2)), encoding="utf-8")
    print(json.dumps({"files": len(ir.get("files", [])), "ops": len(op.get("op_map", {}))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
