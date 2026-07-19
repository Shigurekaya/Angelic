# -*- coding: utf-8 -*-
import json
from pathlib import Path

mtn = json.loads(
    Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json").read_text(
        encoding="utf-8"
    )
)
out = []
out.append("=== object motions ===")
for sec, obj in mtn["object"].items():
    for name, m in (obj.get("motion") or {}).items():
        out.append(f"{sec}/{name} last={m.get('lastTime')} layers={len(m.get('layer') or [])}")


def dump(L, depth=0):
    lab = L.get("label") or ""
    fl = L.get("frameList") or []
    lines = [f"{'  ' * depth}{lab} type={L.get('type')} vis={L.get('visible')}"]
    for fr in fl:
        c = fr.get("content") or {}
        if not c and fr.get("type") == 0:
            lines.append(f"{'  ' * depth}  t={fr.get('time')} END")
            continue
        keep = {k: c[k] for k in ("coord", "opa", "zx", "zy", "ox", "oy", "src") if k in c}
        if keep:
            lines.append(f"{'  ' * depth}  t={fr.get('time')} {json.dumps(keep, ensure_ascii=False)}")
    for ch in L.get("children") or []:
        lines.extend(dump(ch, depth + 1))
    return lines


out.append("\n=== char_move tree ===")
for L in mtn["object"]["title_bg"]["motion"]["char_move"]["layer"]:
    out.extend(dump(L))

out.append("\n=== logo motions ===")
for name, m in mtn["object"]["logo"]["motion"].items():
    out.append(f"-- {name} last={m.get('lastTime')}")
    for L in m.get("layer") or []:
        out.extend(dump(L))

path = Path(r"D:\gamedev\Angelic\tools\_title_fm_compose\mtn_full_utf8.txt")
path.write_text("\n".join(out), encoding="utf-8")
print("wrote", path)
