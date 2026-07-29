# -*- coding: utf-8 -*-
"""Compile common Kirikiri commands into Ren'Py runtime helpers."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IR = ROOT / "docs/ui-extract/kirikiri-ir.json"
OUT = ROOT / "docs/ui-extract/kirikiri-opmap.json"

OP_MAP = {
    "jump": "renpy.jump",
    "call": "renpy.call",
    "return": "renpy.return_statement",
    "if": "runtime conditional",
    "else": "runtime conditional",
    "endif": "runtime conditional",
    "eval": "python assignment / state mutation",
    "wait": "renpy.pause",
    "wt": "renpy.pause",
    "bgm": "renpy.music.play",
    "se": "renpy.sound.play",
    "sysse": "renpy.sound.play",
    "voice": "renpy.sound.play",
    "show": "show image / displayable",
    "scene": "scene / hide all",
    "dialog": "say / dialogue",
    "loadcell": "asset selection / layered image",
    "copy": "layer placement / crop blit",
    "clip": "layer crop",
    "systrans": "transition",
    "begintrans": "transition start",
    "endtrans": "transition end",
    "stoptrans": "transition cancel",
    "sysjump": "stateful menu jump",
    "シーン回想開始": "replay label",
    "sysrestore": "restore scene/menu state",
    "sysrestore_backtogame": "restore scene/menu state",
    "syspage": "stateful page switch",
    "stage": "layer composition stage",
    "backlay": "background layer restore",
    "clearlayers": "clear layered displayables",
    "locklink": "route lock",
    "unlocklink": "route unlock",
    "clickskip": "dismiss / clickskip",
    "beginskip": "skip mode begin",
    "endskip": "skip mode end",
    "syslay": "system layer control",
    "sysvoice": "voice channel control",
    "sysmovie": "movie channel control",
    "syscover": "cover / overlay",
    "history": "history mode",
    "historyopt": "history options",
    "msgoff": "message window hide",
    "allimage": "image layer sync",
    "endlink": "route end",
    "addSysScript": "register system script",
    "addSysHook": "register hook",
    "sysinit": "system init",
    "clearvar": "state clear",
    "freesnapshot": "save snapshot cleanup",
    "locksnapshot": "save snapshot lock",
    "envstop": "environment stop",
    "cancelskip": "cancel skip mode",
    "quit": "quit / exit",
}


def main() -> None:
    data = json.loads(IR.read_text(encoding="utf-8"))
    counts = Counter()
    for file in data.get("files", []):
        for cmd in file.get("commands", []):
            if cmd.get("type") == "command":
                counts[cmd.get("name") or ""] += 1
    payload = {
        "op_map": OP_MAP,
        "command_counts": dict(counts.most_common()),
        "high_frequency_commands": [name for name, n in counts.most_common() if n >= 10],
        "migration_priority": [
            "jump",
            "call",
            "return",
            "if",
            "eval",
            "wait",
            "bgm",
            "se",
            "voice",
            "show",
            "scene",
            "dialog",
            "loadcell",
            "copy",
            "clip",
            "systrans",
            "sysjump",
            "シーン回想開始",
            "sysrestore",
            "stage",
            "clearlayers",
            "locklink",
            "unlocklink",
            "history",
            "syslay",
        ],
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"mapped": len(OP_MAP), "high_frequency": len(payload["high_frequency_commands"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
