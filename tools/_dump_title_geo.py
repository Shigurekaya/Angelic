# -*- coding: utf-8 -*-
"""Dump title_locale_cn layer geometry for button placement."""
from __future__ import annotations

import json
from pathlib import Path

p = Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/pbd-layers/title_locale_cn.json")
d = json.loads(p.read_text(encoding="utf-8"))
for L in d.get("layers") or []:
    lid = L.get("layer_id")
    if lid in (
        "start", "load", "continue", "flowchart", "extra", "after", "system", "exit",
        "allbtns", "title_cn", "area", "amv_pos0", "amv_pos1",
    ) or lid and "btn" in str(lid).lower():
        keys = {k: L.get(k) for k in L if k in (
            "layer_id", "sort_index", "left", "top", "width", "height",
            "cx", "cy", "cw", "ch", "ox", "oy", "x", "y", "w", "h",
            "storagex", "storagey", "storage", "opacity",
        ) or k in ("properties",)}
        print(json.dumps(keys, ensure_ascii=False))

print("--- bindings ---")
for b in d.get("bindings") or []:
    print(json.dumps(b, ensure_ascii=False)[:200])

print("--- title.pbd interesting ---")
t = json.loads(Path(r"D:/gamedev/Angelic/docs/ui-extract/pixel-reverse/pbd-layers/title.json").read_text(encoding="utf-8"))
for L in t.get("layers") or []:
    lid = str(L.get("layer_id") or "")
    if lid in ("start", "load", "continue", "flowchart", "extra", "after", "system", "exit", "lang_left", "lang_right"):
        print(lid, {k: L.get(k) for k in ("left", "top", "width", "height", "ox", "oy", "storagex", "storagey", "x", "y", "cx", "cy")})
