# -*- coding: utf-8 -*-
"""Cafe-style UI unpack for Angelic: pbd2json → absolute x/y/w/h layers.

Mirrors Cafe Stella:
  FreeMote PSB left/top  →  Angelic pbd2json result.*.x/y/width/height

Outputs under docs/ui-extract/pixel-reverse/pbd2json-layers/
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:/gamedev/Angelic")
UIPSD = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd"
OUT = ROOT / "docs/ui-extract/pixel-reverse/pbd2json-layers"
PBD2JSON = Path(r"D:/gamedev/CafeStella/tools/vendor/hxv4_unhash_tools/binaries/pbd2json.exe")

SCREEN_MAP = {
    "title": ("title.pbd", "title_locale_cn.pbd"),
    "option": tuple(
        ["option.pbd", "option_cmds.pbd", "option_keyinput.pbd"]
        + [
            f"option_{x}.pbd"
            for x in (
                "0simple",
                "1display",
                "2game1",
                "3game2",
                "4text",
                "5sound1",
                "5sound2",
                "6dialog",
                "7mouse",
                "8keyboard1",
                "9gamepad",
                "9gamepad2_assign",
            )
        ]
    ),
    "file": ("file.pbd", "file_load.pbd", "file_save.pbd", "file_quick.pbd"),
    "qconf": (
        "qconf.pbd",
        "qconf_load.pbd",
        "qconf_qload.pbd",
        "qconf_qvsave.pbd",
        "qconf_save.pbd",
        "qconf_text.pbd",
        "qconf_volume.pbd",
    ),
    "extra": ("extra.pbd", "extra_cg.pbd", "extra_cgview.pbd", "extra_locale_cn.pbd", "extra_voice.pbd", "scnchart.pbd"),
    "window": ("window.pbd", "window_h.pbd", "dialog.pbd", "backlog.pbd", "select.pbd"),
    "hud": ("quickmenu.pbd", "touchuibar.pbd", "touchvolume.pbd", "voicebar.pbd", "phonechat.pbd"),
}


def run_pbd2json(pbd: Path) -> dict:
    proc = subprocess.run(
        [str(PBD2JSON), str(pbd)],
        capture_output=True,
        check=False,
    )
    raw = proc.stdout
    if not raw:
        raise RuntimeError(f"pbd2json empty: {pbd.name} stderr={proc.stderr[:200]!r}")
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp932"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="ignore"))


def layer_rect(name: str, node: dict) -> dict | None:
    if not isinstance(node, dict):
        return None
    x, y = node.get("x"), node.get("y")
    w = node.get("width", node.get("w"))
    h = node.get("height", node.get("h"))
    if not all(isinstance(v, (int, float)) for v in (x, y, w, h)):
        return None
    if not (0 <= int(w) <= 4096 and 0 <= int(h) <= 4096):
        return None
    if not (-200 <= int(x) <= 4000 and -200 <= int(y) <= 4000):
        return None
    out = {
        "name": name,
        "left": int(x),
        "top": int(y),
        "width": int(w),
        "height": int(h),
        "class": node.get("class"),
        "uiname": node.get("uiname") or name,
    }
    states = node.get("uistates") or {}
    if isinstance(states, dict) and states:
        out["uistates"] = {
            sk: {
                k: sv[k]
                for k in ("ox", "oy", "cx", "cy", "w", "h", "storage", "storagex", "storagey", "opacity")
                if isinstance(sv, dict) and k in sv
            }
            for sk, sv in states.items()
            if isinstance(sv, dict)
        }
    return out


def extract_hotspots(doc: dict) -> list[dict]:
    res = doc.get("result") or {}
    hotspots = []
    for name, node in res.items():
        rec = layer_rect(name, node)
        if rec:
            hotspots.append(rec)
    hotspots.sort(key=lambda h: (h["top"], h["left"], h["name"]))
    return hotspots


def main() -> None:
    if not PBD2JSON.is_file():
        raise SystemExit(f"missing {PBD2JSON}")
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    screens: dict[str, list] = {k: [] for k in SCREEN_MAP}
    screens["other"] = []

    for pbd in sorted(UIPSD.glob("*.pbd")):
        try:
            doc = run_pbd2json(pbd)
        except Exception as exc:  # noqa: BLE001
            summary.append({"name": pbd.name, "verdict": "ERR", "error": str(exc)})
            print("ERR", pbd.name, exc)
            continue
        hotspots = extract_hotspots(doc)
        dest = OUT / f"{pbd.stem}.json"
        dest.write_text(
            json.dumps(
                {
                    "source": pbd.name,
                    "tool": "pbd2json.exe (Cafe Stella vendor)",
                    "names": doc.get("names") or [],
                    "layer_count": len(doc.get("result") or {}),
                    "hotspot_count": len(hotspots),
                    "hotspots": hotspots,
                    "raw_result_keys": sorted((doc.get("result") or {}).keys()),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (OUT / f"{pbd.stem}.hotspots.json").write_text(
            json.dumps({"source": pbd.name, "hotspots": hotspots}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        entry = {"name": pbd.name, "verdict": "OK", "hotspots": len(hotspots), "layers": len(doc.get("result") or {})}
        summary.append(entry)
        placed = False
        for screen, names in SCREEN_MAP.items():
            if pbd.name in names:
                screens[screen].append(entry)
                placed = True
                break
        if not placed:
            screens["other"].append(entry)
        print(f"OK {pbd.name} hotspots={len(hotspots)}")

    (OUT / "manifest.json").write_text(
        json.dumps({"items": summary, "screens": screens}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ok = sum(1 for s in summary if s.get("verdict") == "OK")
    print(f"DONE {ok}/{len(summary)} -> {OUT}")


if __name__ == "__main__":
    main()
