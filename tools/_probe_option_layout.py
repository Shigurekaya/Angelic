# -*- coding: utf-8 -*-
"""Probe Angelic option layout sources for 1:1 settings rebuild."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REV = ROOT / "docs/ui-extract/pixel-reverse"
PBD = REV / "pbd-layers"
SLICES = REV / "_pack_slices"
TLG = REV / "tlg-png"
CAP = REV / "_orig_capture"


def main() -> None:
    # 1) option pack slices
    d = SLICES / "option__pack"
    sj = d / "slices.json"
    data = json.loads(sj.read_text(encoding="utf-8"))
    print("option__pack slices", len(data))
    for item in data:
        p = d / item["file"]
        if p.exists():
            im = Image.open(p)
            print(f"  i={item['i']:03d} {im.size} file={item['file']}")

    # 2) option_0simple hotspots richer?
    for name in ("option_0simple", "option", "option_4text", "option_cmds"):
        hp = PBD / f"{name}.hotspots.json"
        d2 = json.loads(hp.read_text(encoding="utf-8"))
        hs = d2.get("hotspots") or []
        keys = set()
        for h in hs:
            keys |= set(h.keys())
        print(f"\n{name} hotspots={len(hs)} keys={sorted(keys)}")
        # find any with left/top/x/y
        geo = [h for h in hs if any(k in h for k in ("left", "top", "x", "y", "ox", "oy", "width", "w"))]
        print(f"  with geo-ish: {len(geo)}")
        if geo:
            print("  sample", geo[0])
        # bindings
        binds = d2.get("bindings") or []
        print(f"  bindings={len(binds)}")
        if binds:
            print("  bind0", binds[0])

    # 3) pm_option capture
    for n in ("pm_option_1080.png", "pm_option.png", "live_click_system_1080.png"):
        p = CAP / n
        if p.exists():
            im = Image.open(p)
            print(n, im.size, "mode", im.mode)

    # 4) search ui-defs / help for option
    for pat in ("**/option*", "**/help_opt*", "**/uitexts*"):
        hits = list(ROOT.glob(f"docs/ui-extract/**/{pat.split('/')[-1]}"))
        print(pat, "hits", len(hits), [str(h.relative_to(ROOT))[:80] for h in hits[:8]])


if __name__ == "__main__":
    main()
