# -*- coding: utf-8 -*-
import json
from pathlib import Path
from PIL import Image

mtn = json.loads(
    Path(r"D:\gamedev\renpy-angelic\game\images\angelic\_mtn\title_bg.json").read_text(
        encoding="utf-8"
    )
)
out = Path(r"D:\gamedev\Angelic\tools\_title_fm_compose\names_utf8.txt")
lines = ["ICONS:"]
for name, ic in mtn["source"]["normal"]["icon"].items():
    lines.append(f"{ic['width']}x{ic['height']}  {name}")

lines.append("")
lines.append("SLOTS:")
cm = mtn["object"]["title_bg"]["motion"]["char_move"]


def walk(L):
    lab = L.get("label") or ""
    fl = L.get("frameList") or []
    src = None
    for fr in fl:
        c = fr.get("content") or {}
        if c.get("src"):
            src = c["src"]
    if src and "結合" in lab:
        key = src.replace("src/normal/", "")
        ic = mtn["source"]["normal"]["icon"][key]
        t90 = None
        for fr in fl:
            c = fr.get("content") or {}
            if c.get("coord") is not None and fr.get("time") in (90, 90.0):
                t90 = c["coord"]
        lines.append(f"label={lab}")
        lines.append(f"  key={key}")
        lines.append(f"  size={ic['width']}x{ic['height']} origin=({ic['originX']},{ic['originY']})")
        lines.append(f"  t90={t90}")
    for ch in L.get("children") or []:
        walk(ch)


for L in cm["layer"]:
    walk(L)

lines.append("")
lines.append("FILES:")
SRC = Path(r"D:\gamedev\Angelic\ui-preview\_mtn\title_bg")
for p in sorted(SRC.glob("*.png")):
    im = Image.open(p)
    if im.size in ((400, 497), (1642, 725), (1332, 1208), (1290, 1120)):
        lines.append(f"{im.size[0]}x{im.size[1]}  {p.name}")

out.write_text("\n".join(lines), encoding="utf-8")
print("wrote", out)
