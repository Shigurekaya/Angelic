# -*- coding: utf-8 -*-
import json
from pathlib import Path

p = Path(r"D:/gamedev/renpy-angelic/game/images/angelic/_mtn/title_bg.json")
d = json.loads(p.read_text(encoding="utf-8"))
obj = d["object"]
print("object keys", list(obj.keys()))
for section in ("logo", "title_bg"):
    sec = obj.get(section) or {}
    mot = sec.get("motion") or {}
    print("===", section, "motions", len(mot))
    for name, m in list(mot.items())[:30]:
        layers = m.get("layer") or []
        print(" ", name, "last", m.get("lastTime"), "layers", len(layers))
        for L in layers[:5]:
            fl = L.get("frameList") or []
            print("   ", (L.get("label") or "?")[:50], "frames", len(fl))
            if fl:
                c0 = (fl[0].get("content") or {})
                print("      t0", fl[0].get("time"), "opa", c0.get("opa"), "zx", c0.get("zx"), "coord", c0.get("coord"))

resx = Path(r"D:/gamedev/renpy-angelic/game/images/angelic/_mtn/title_bg.resx.json")
print("resx", resx.read_text(encoding="utf-8")[:1200])
