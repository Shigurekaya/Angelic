# -*- coding: utf-8 -*-
import json
from pathlib import Path

ROOT = Path(r"D:\gamedev\Angelic\docs\ui-extract\pixel-reverse\_pack_slices")
for name in ("option__pack", "option_cmds__pack", "option_4text__pack", "option_0simple"):
    p = ROOT / name / "slices.json"
    if not p.exists():
        print(name, "MISSING")
        continue
    sj = json.loads(p.read_text(encoding="utf-8"))
    print("===", name, "n=", len(sj))
    for s in sj:
        print(f"  {s['i']:02d} {s['w']:4d}x{s['h']:4d} {s['file']}")
