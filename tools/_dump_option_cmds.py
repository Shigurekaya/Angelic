# -*- coding: utf-8 -*-
import json
import subprocess
from pathlib import Path

exe = Path(r"D:\gamedev\CafeStella\tools\vendor\hxv4_unhash_tools\binaries\pbd2json.exe")
uipsd = Path(r"D:\gamedev\Angelic\docs\ui-extract\ui-cn-jp-static\filtered-cn-jp\uipsd")
for stem in ("option_cmds", "option"):
    p = uipsd / f"{stem}.pbd"
    doc = json.loads(subprocess.check_output([str(exe), str(p)]).decode("utf-8-sig"))
    print("====", stem, "names", len(doc.get("names") or []))
    for name, node in sorted(doc["result"].items()):
        us = node.get("uistates") or {}
        stor = [
            (k, st.get("storage"), st.get("cx"), st.get("cy"), st.get("w"), st.get("h"))
            for k, st in us.items()
            if st.get("storage")
        ]
        print(
            f"  {name:20} {str(node.get('class')):8} "
            f"{node.get('x'):4},{node.get('y'):4} "
            f"{node.get('width')}x{node.get('height')} stor={stor[:4]}"
        )
