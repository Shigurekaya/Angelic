import json
import subprocess
from pathlib import Path

PBD2JSON = Path(r"D:/gamedev/CafeStella/tools/vendor/hxv4_unhash_tools/binaries/pbd2json.exe")
UIPSD = Path(r"D:/gamedev/Angelic/docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd")

for pbd in ("option_1display.pbd", "option_2game1.pbd", "option_4text.pbd"):
    raw = subprocess.check_output([str(PBD2JSON), str(UIPSD / pbd)])
    doc = json.loads(raw.decode("utf-8-sig"))
    result = doc.get("result") or {}
    print("====", pbd, "n=", len(result))
    for name, node in sorted(result.items()):
        if not isinstance(node, dict):
            continue
        if not (name.endswith(("_off", "_on")) or name.endswith("_slider")):
            continue
        x, y = node.get("x"), node.get("y")
        w, h = node.get("width"), node.get("height")
        if x is None and w is None:
            continue
        print(f"  {name:28} xywh=({x},{y},{w},{h}) cls={node.get('class')}")
