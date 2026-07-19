# -*- coding: utf-8 -*-
"""Probe PBD geo clusters + LimeLight parser for Angelic option/title."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"D:/gamedev/Angelic")
UIPSD = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(r"D:/gamedev/LimeLight/tools/lllj-extract")))

from compose_view_state_1to1 import extract_geo_clusters  # noqa: E402
from pbd_ns_parse import parse_pbd_layers, geometry_from_layer, parse_bindings_with_geometry  # noqa: E402


def probe(name: str) -> None:
    pbd = UIPSD / name
    data = pbd.read_bytes()
    print(f"\n=== {name} size={len(data)} ===")
    clusters = extract_geo_clusters(data)
    with_storage = [c for c in clusters if c.get("storage")]
    with_xy = [c for c in clusters if any(k in c for k in ("ox", "oy", "x", "y", "left", "top"))]
    with_sx = [c for c in clusters if "storagex" in c or "storagey" in c]
    print(f"clusters={len(clusters)} storage={len(with_storage)} screen_xy={len(with_xy)} storage_xy={len(with_sx)}")
    for c in with_storage[:12]:
        print(" ", {k: c[k] for k in c if not k.startswith("_")})

    layers = parse_pbd_layers(data)
    print(f"lllj layers={len(layers)}")
    good = 0
    samples = []
    for L in layers:
        g = geometry_from_layer(L) or {}
        if g.get("storage") and (
            ("storagex" in g and "storagey" in g)
            or ("ox" in g and "oy" in g)
            or ("left" in g and "top" in g)
        ):
            good += 1
            if len(samples) < 8:
                samples.append(
                    {
                        "id": L.get("layer_id"),
                        **{
                            k: g[k]
                            for k in g
                            if k
                            in (
                                "storage",
                                "storagex",
                                "storagey",
                                "ox",
                                "oy",
                                "left",
                                "top",
                                "x",
                                "y",
                                "width",
                                "height",
                                "cw",
                                "ch",
                                "visible",
                                "opacity",
                            )
                        },
                    }
                )
    print(f"lllj layers_with_placeable_geo={good}")
    for s in samples:
        print("  L", s)

    keys_hit = {}
    for L in layers:
        g = geometry_from_layer(L) or {}
        for k, v in g.items():
            if isinstance(v, int) or k == "storage":
                keys_hit[k] = keys_hit.get(k, 0) + 1
    print("geo key freq", keys_hit)

    binds = parse_bindings_with_geometry(data)
    print(f"bindings={len(binds)}")
    for b in binds[:5]:
        print("  B", b.get("layer_id"), b.get("bindings"), b.get("properties"))


def main():
    for n in [
        "option.pbd",
        "option_0simple.pbd",
        "title.pbd",
        "title_locale_cn.pbd",
        "file_load.pbd",
        "extra_cg.pbd",
    ]:
        if (UIPSD / n).exists():
            probe(n)


if __name__ == "__main__":
    main()
