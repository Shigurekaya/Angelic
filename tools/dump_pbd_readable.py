# -*- coding: utf-8 -*-
"""Dump TJS/ns PBD to readable JSON (Angelic/YuzuSoft UI layout source).

PBD is the layout source (Cafe Stella's FreeMote PSB equivalent).
Encoding: length-prefixed UTF-16 keys + 0x04 int32 / 0x02 string values.
"""
from __future__ import annotations

import json
import re
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UIPSD = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd"
OUT = ROOT / "docs/ui-extract/pixel-reverse/settings-layout/pbd-readable"

GEO_KEYS = {
    "left", "top", "width", "height", "x", "y", "w", "h",
    "cx", "cy", "cw", "ch", "ox", "oy", "storagex", "storagey",
    "opacity", "visible", "order", "index", "hotspot", "area",
}
LAYER_RE = re.compile(
    r"^(?:label_[a-z0-9_]+|page\d+|config_[a-z0-9_]+|"
    r"[a-z][a-z0-9_]*(?:_(?:on|off|chk|sel|rev|slider|value|numbase|mute|test|play|jump))?)$"
)


def read_key(data: bytes, pos: int) -> tuple[str, int] | None:
    if pos + 4 > len(data):
        return None
    n = struct.unpack_from("<I", data, pos)[0]
    if not (1 <= n <= 96):
        return None
    start, end = pos + 4, pos + 4 + n * 2
    if end > len(data):
        return None
    raw = data[start:end]
    try:
        s = raw.decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    if "\x00" in s or not all(32 <= ord(c) <= 126 for c in s):
        return None
    return s, end


def read_str_val(data: bytes, pos: int) -> tuple[str, int] | None:
    if pos + 5 > len(data) or data[pos] != 0x02:
        return None
    n = struct.unpack_from("<I", data, pos + 1)[0]
    if not (1 <= n <= 200):
        return None
    start, end = pos + 5, pos + 5 + n * 2
    if end > len(data):
        return None
    try:
        s = data[start:end].decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    if "\x00" in s:
        return None
    return s, end


def scan_entries(data: bytes) -> list[tuple[int, str, Any]]:
    if not data.startswith(b"TJS/ns"):
        raise ValueError("not TJS/ns PBD")
    entries: list[tuple[int, str, Any]] = []
    pos = 16  # skip TJS/ns0\\0 + TJS\\0\\0\\0\\0\\0
    while pos + 8 < len(data):
        got = read_key(data, pos)
        if not got:
            pos += 1
            continue
        key, after = got
        if after < len(data) and data[after] == 0x04 and after + 5 <= len(data):
            val = struct.unpack_from("<i", data, after + 1)[0]
            entries.append((pos, key, val))
            pos = after + 5
            continue
        sres = read_str_val(data, after)
        if sres:
            entries.append((pos, key, sres[0]))
            pos = sres[1]
            continue
        # bare following length-string (storage / call targets)
        got2 = read_key(data, after)
        if got2 and (got2[0].startswith(".") or "pack" in got2[0] or got2[0].startswith("option")):
            entries.append((pos, key, got2[0]))
            pos = got2[1]
            continue
        pos = after
    return entries


def cluster_layers(entries: list[tuple[int, str, Any]]) -> list[dict[str, Any]]:
    """Group nearby entries; attach layer_id when a name-like key appears."""
    layers: list[dict[str, Any]] = []
    cur: dict[str, Any] | None = None
    last_pos = -10_000

    def flush() -> None:
        nonlocal cur
        if cur and (cur.get("props") or cur.get("layer_id")):
            layers.append(cur)
        cur = None

    for pos, key, val in entries:
        if pos - last_pos > 64:
            flush()
            cur = {"_pos": pos, "props": {}}
        if cur is None:
            cur = {"_pos": pos, "props": {}}
        last_pos = pos

        if isinstance(val, str) and key in {"name", "uiname", "sename"}:
            cur["layer_id"] = val
        elif key in GEO_KEYS and isinstance(val, int):
            # keep first sensible, else last
            if key not in cur["props"] or abs(val) < abs(cur["props"][key]):
                if abs(val) < 100_000:
                    cur["props"][key] = val
        elif key == "storage" and isinstance(val, str):
            cur["props"]["storage"] = val
        elif isinstance(val, str) and LAYER_RE.match(val) and key in {"name", "uiname"}:
            cur["layer_id"] = val
        elif isinstance(val, (int, str)) and key not in {"exp", "call", "evals"}:
            cur["props"].setdefault(key, val)

        # layer id often appears as a bare string key with no useful value —
        # also detect when KEY itself is a layer id (dictionary key = layer name)
        if LAYER_RE.match(key) and key not in GEO_KEYS and key not in {
            "storage", "name", "uiname", "sename", "class", "button", "layer",
            "visible", "opacity", "order", "index", "result", "base", "page",
        }:
            if "layer_id" not in cur:
                cur["layer_id"] = key

    flush()
    return layers


def abs_formula(props: dict[str, Any]) -> dict[str, int | None]:
    """YuzuSoft title formula: screen = center + c - o."""
    cx, cy = props.get("cx"), props.get("cy")
    ox, oy = props.get("ox"), props.get("oy")
    out: dict[str, int | None] = {"x": None, "y": None}
    if isinstance(cx, int) and isinstance(ox, int) and abs(cx) < 5000 and abs(ox) < 5000:
        out["x"] = 960 + cx - ox
    if isinstance(cy, int) and isinstance(oy, int) and abs(cy) < 5000 and abs(oy) < 5000:
        out["y"] = 540 + cy - oy
    # fallback: plain x/y or left/top
    if out["x"] is None:
        for k in ("left", "x"):
            if isinstance(props.get(k), int) and 0 <= props[k] <= 1920:
                out["x"] = props[k]
                break
    if out["y"] is None:
        for k in ("top", "y"):
            if isinstance(props.get(k), int) and 0 <= props[k] <= 1080:
                out["y"] = props[k]
                break
    return out


def dump_one(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    entries = scan_entries(data)
    layers = cluster_layers(entries)
    usable = []
    for L in layers:
        props = L.get("props") or {}
        formula = abs_formula(props)
        item = {
            "layer_id": L.get("layer_id"),
            "props": props,
            "abs": formula,
        }
        if L.get("layer_id") or any(k in props for k in GEO_KEYS):
            usable.append(item)
    return {
        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        "bytes": len(data),
        "entries": len(entries),
        "layers": usable,
        "note": "TJS/ns PBD readable dump; abs uses 960+cx-ox / 540+cy-oy when cx/cy sensible",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(UIPSD.glob("option*.pbd"))
    index = []
    for p in files:
        doc = dump_one(p)
        out = OUT / f"{p.stem}.json"
        out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        # also compact layers with abs
        placed = [L for L in doc["layers"] if L["abs"]["x"] is not None or L["abs"]["y"] is not None]
        geoish = [
            L for L in doc["layers"]
            if any(k in (L.get("props") or {}) for k in ("ox", "oy", "storagex", "storagey", "left", "top"))
        ]
        index.append({
            "stem": p.stem,
            "layers": len(doc["layers"]),
            "with_abs": len(placed),
            "with_geo_props": len(geoish),
            "file": out.name,
        })
        print(f"{p.stem}: layers={len(doc['layers'])} abs={len(placed)} geo={len(geoish)}")
    (OUT / "_index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
