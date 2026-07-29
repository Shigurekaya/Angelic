import json
import subprocess
from pathlib import Path

PBD2JSON = Path(r"D:/gamedev/CafeStella/tools/vendor/hxv4_unhash_tools/binaries/pbd2json.exe")
UIPSD = Path(r"D:/gamedev/Angelic/docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd")

raw = subprocess.check_output([str(PBD2JSON), str(UIPSD / "option_0simple.pbd")])
doc = json.loads(raw.decode("utf-8-sig"))
result = doc.get("result") or {}
print("result keys sample", list(result.keys())[:40], "n=", len(result))
for name, node in sorted(result.items()):
    if not isinstance(node, dict):
        continue
    x, y = node.get("x"), node.get("y")
    w, h = node.get("width"), node.get("height")
    cls = node.get("class")
    us = node.get("uistates") or {}
    stor = any(
        isinstance(st, dict) and (st.get("storage") or st.get("w"))
        for st in us.values()
    )
    if name.endswith(("_off", "_on", "_slider", "_mute", "_jump")) or name.startswith("label_"):
        print(f"{name:28} cls={cls} xywh=({x},{y},{w},{h}) stor={stor} states={list(us.keys())[:6]}")
