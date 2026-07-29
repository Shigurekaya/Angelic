# -*- coding: utf-8 -*-
"""Compile Kirikiri IR into a Ren'Py migration scaffold."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IR = ROOT / "docs/ui-extract/kirikiri-ir.json"
OUT = ROOT / "docs/ui-extract/kirikiri-renpy-scaffold.rpy"

RENPY_TEMPLATE = '''# Auto-generated Kirikiri migration scaffold
# This file is intentionally incomplete: it preserves structure, labels, and calls
# so the migration can be filled incrementally.

init python:
    kirikiri_ir = {ir_json}
    kirikiri_label_index = {{}}
    kirikiri_call_graph = {{}}
    kirikiri_storages = {{}}
    for _f in kirikiri_ir.get("files", []):
        _path = _f.get("path")
        for _cmd in _f.get("commands", []):
            if _cmd.get("type") == "label":
                kirikiri_label_index[_cmd["name"]] = _path
                kirikiri_call_graph.setdefault(_cmd["name"], set())
            elif _cmd.get("type") == "command":
                _attrs = _cmd.get("attrs") or {{}}
                _storage = _attrs.get("storage") or _attrs.get("file")
                if _storage:
                    kirikiri_storages.setdefault(_storage, set()).add(_path)
                if _cmd.get("name") in ("jump", "call", "sysjump", "シーン回想開始") and _storage:
                    kirikiri_call_graph.setdefault(_path, set()).add(_storage)

    kirikiri_state = {{
        "current_file": None,
        "current_label": None,
        "history": [],
        "flags": {{}},
        "variables": {{}},
        "visited": set(),
    }}

    def kirikiri_set_flag(name, value=True):
        kirikiri_state["flags"][str(name)] = bool(value)

    def kirikiri_get_flag(name, default=False):
        return bool(kirikiri_state["flags"].get(str(name), default))

    def kirikiri_set_var(name, value):
        kirikiri_state["variables"][str(name)] = value

    def kirikiri_get_var(name, default=None):
        return kirikiri_state["variables"].get(str(name), default)

    def kirikiri_log(step, payload=None):
        kirikiri_state["history"].append({{"step": step, "payload": payload}})

    def kirikiri_mark_visit(label):
        kirikiri_state["visited"].add(str(label))

    def kirikiri_resolve_storage(storage):
        return kirikiri_label_index.get(storage, storage)

label kirikiri_migration_start:
    $ kirikiri_log("migration_start")
    "Kirikiri migration scaffold loaded."
    return

'''


def main() -> None:
    data = json.loads(IR.read_text(encoding="utf-8"))
    OUT.write_text(RENPY_TEMPLATE.format(ir_json=json.dumps(data, ensure_ascii=False, indent=2)), encoding="utf-8")
    print(json.dumps({"labels": sum(len(f.get('labels', [])) for f in data.get('files', [])), "files": len(data.get('files', []))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
