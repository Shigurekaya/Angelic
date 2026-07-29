import json
from pathlib import Path

slots = json.loads(
    Path(r"D:/gamedev/Angelic/ui-preview/assets/settings/interaction_slots.json").read_text(
        encoding="utf-8"
    )
)
meta = json.loads(
    Path(r"D:/gamedev/Angelic/ui-preview/assets/settings/meta.json").read_text(encoding="utf-8")
)
print("meta keys", list(meta.keys()))
print("tabs", meta.get("tabs"))
print("source", meta.get("source"))
for tid in ["0", "1", "2", "4"]:
    items = slots[tid]
    print(f"=== tab {tid} n={len(items)} ===")
    for it in items:
        chips = it.get("chips")
        bad = ""
        if chips:
            for c in chips:
                if int(c.get("w") or 0) <= 0:
                    bad = " BADCHIP"
        print(
            f"  {it.get('type'):12} {it.get('key'):20} "
            f"xywh={it.get('x'), it.get('y'), it.get('w'), it.get('h')}{bad}"
        )
        if chips and bad:
            print("    chips", chips)
        if it.get("detail") and tid == "0":
            print("    detail", it["detail"])
