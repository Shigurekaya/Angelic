#!/usr/bin/env python3
"""Angelic pixel-level UI reverse: parse uipsd/*.pbd geometry + decode TLG5 packs."""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UIPSD = REPO / "docs" / "ui-extract" / "ui-cn-jp-static" / "filtered-cn-jp" / "uipsd"
OUT = REPO / "docs" / "ui-extract" / "pixel-reverse"
PBD_OUT = OUT / "pbd-layers"
TLG_OUT = OUT / "tlg-png"
LIMELIGHT_TOOLS = Path(r"D:\gamedev\LimeLight\tools\lllj-extract")

SCREEN_GROUPS = {
    "title": ("title.pbd", "title_locale_cn.pbd"),
    "option": tuple(f"option_{x}.pbd" for x in (
        "0simple", "1display", "2game1", "3game2", "4text", "5sound1", "5sound2",
        "6dialog", "7mouse", "8keyboard1", "9gamepad", "9gamepad2_assign",
    )) + ("option.pbd", "option_cmds.pbd", "option_keyinput.pbd"),
    "file": ("file.pbd", "file_load.pbd", "file_save.pbd", "file_quick.pbd"),
    "qconf": (
        "qconf.pbd", "qconf_load.pbd", "qconf_qload.pbd", "qconf_qvsave.pbd",
        "qconf_save.pbd", "qconf_text.pbd", "qconf_volume.pbd", "qlpopup.pbd", "qvpopup.pbd",
    ),
    "window": ("window.pbd", "window_h.pbd", "dialog.pbd", "backlog.pbd", "select.pbd"),
    "extra": (
        "extra.pbd", "extra_cg.pbd", "extra_cgview.pbd", "extra_locale_cn.pbd", "extra_voice.pbd",
        "chapter.pbd", "scnchart.pbd", "bgmtitle.pbd",
    ),
    "hud": (
        "quickmenu.pbd", "touchuibar.pbd", "touchvolume.pbd", "voicebar.pbd",
        "phonechat.pbd", "clickglyph_img.pbd", "autoskipmark_img.pbd", "autoskipmark_pos.pbd",
        "btncustom.pbd", "gesture_help.pbd",
    ),
}


def ensure_parser():
    sys.path.insert(0, str(LIMELIGHT_TOOLS))
    from pbd_ns_parse import geometry_from_layer, parse_bindings_with_geometry, parse_pbd_layers

    return parse_pbd_layers, geometry_from_layer, parse_bindings_with_geometry


def valid_geom(g: dict) -> dict | None:
    if not g:
        return None
    out = {}
    for k, v in g.items():
        if k == "storage":
            out[k] = v
            continue
        if not isinstance(v, int):
            continue
        if k in ("width", "height", "cw", "ch", "w", "h") and not (1 <= v <= 1920):
            continue
        if k in ("left", "top", "x", "y", "cx", "cy", "ox", "oy", "storagex", "storagey") and not (
            -100 <= v <= 2000
        ):
            continue
        if k == "opacity" and not (0 <= v <= 255):
            continue
        out[k] = v
    # keep only if we have some placement or size
    keys = set(out) - {"storage", "opacity"}
    return out if keys else None


def parse_all_pbd() -> dict:
    parse_pbd_layers, geometry_from_layer, parse_bindings_with_geometry = ensure_parser()
    PBD_OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    screens: dict[str, list] = {k: [] for k in SCREEN_GROUPS}
    screens["other"] = []

    for pbd in sorted(UIPSD.glob("*.pbd")):
        data = pbd.read_bytes()
        if not data.startswith(b"TJS/ns"):
            summary.append({"name": pbd.name, "verdict": "BAD_MAGIC"})
            continue
        try:
            layers = parse_pbd_layers(data)
            bindings = parse_bindings_with_geometry(data)
        except Exception as exc:  # noqa: BLE001
            summary.append({"name": pbd.name, "verdict": "ERR", "error": str(exc)})
            continue

        hotspots = []
        for layer in layers:
            g = valid_geom(geometry_from_layer(layer) or {})
            if not g:
                continue
            hotspots.append(
                {
                    "layer_id": layer.get("layer_id"),
                    "sort_index": layer.get("sort_index"),
                    **g,
                }
            )
        bind_geo = []
        for b in bindings:
            g = valid_geom(b.get("properties") or {})
            bind_geo.append(
                {
                    "layer_id": b.get("layer_id"),
                    "bindings": b.get("bindings"),
                    "geometry": g,
                }
            )

        doc = {
            "source": pbd.name,
            "layer_count": len(layers),
            "hotspot_count": len(hotspots),
            "binding_count": len(bind_geo),
            "hotspots": hotspots,
            "bindings": bind_geo,
            "layers": layers,
        }
        dest = PBD_OUT / f"{pbd.stem}.json"
        dest.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
        # compact hotspot-only
        (PBD_OUT / f"{pbd.stem}.hotspots.json").write_text(
            json.dumps(
                {
                    "source": pbd.name,
                    "hotspots": hotspots,
                    "bindings": [
                        x for x in bind_geo if x.get("geometry") or x.get("bindings")
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        entry = {
            "name": pbd.name,
            "verdict": "OK",
            "layers": len(layers),
            "hotspots": len(hotspots),
            "bindings": len(bind_geo),
        }
        summary.append(entry)
        placed = False
        for screen, names in SCREEN_GROUPS.items():
            if pbd.name in names:
                screens[screen].append(entry)
                placed = True
                break
        if not placed:
            screens["other"].append(entry)
        print(f"PBD {pbd.name} layers={len(layers)} hotspots={len(hotspots)}", flush=True)

    (PBD_OUT / "manifest.json").write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "items": summary,
                "screens": screens,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "ok": sum(1 for s in summary if s.get("verdict") == "OK"),
        "total": len(summary),
        "hotspots": sum(s.get("hotspots") or 0 for s in summary),
    }


def decode_tlg() -> dict:
    sys.path.insert(0, str(LIMELIGHT_TOOLS))
    try:
        from tlg5_decode import decode_tlg5_raw
        from PIL import Image
    except Exception as exc:  # noqa: BLE001
        return {"ok": 0, "error": str(exc)}

    TLG_OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for tlg in sorted(UIPSD.glob("*.tlg")):
        data = tlg.read_bytes()
        if not data.startswith(b"TLG5.0"):
            items.append({"name": tlg.name, "verdict": "NOT_TLG5", "bytes": len(data)})
            continue
        try:
            w, h, rgba = decode_tlg5_raw(data)
            dest = TLG_OUT / f"{tlg.stem}.png"
            Image.frombytes("RGBA", (w, h), rgba).save(dest)
            items.append({"name": tlg.name, "verdict": "OK", "w": w, "h": h, "png": dest.name})
            print(f"TLG {tlg.name} {w}x{h}", flush=True)
        except Exception as exc:  # noqa: BLE001
            items.append({"name": tlg.name, "verdict": "ERR", "error": str(exc)})
            print(f"TLG ERR {tlg.name}: {exc}", flush=True)
    (TLG_OUT / "manifest.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"ok": sum(1 for i in items if i["verdict"] == "OK"), "total": len(items)}


def write_report(pbd_stats: dict, tlg_stats: dict) -> None:
    man = json.loads((PBD_OUT / "manifest.json").read_text(encoding="utf-8"))
    lines = [
        "# 天使☆嚣嚣 RE-BOOT — 像素级 UI 反推",
        "",
        f"> 生成：{datetime.now(timezone.utc).isoformat()}",
        "",
        "## 方法",
        "",
        "1. 静态强解已完成：`filtered-cn-jp/uipsd/*.pbd` + `*.tlg`",
        "2. 复用 LimeLight `pbd_ns_parse.py` 提取图层几何 / 绑定",
        "3. TLG5 解码为 PNG 精灵图（按钮烤字 / chrome）",
        "",
        "## 统计",
        "",
        f"- PBD 解析：{pbd_stats}",
        f"- TLG 解码：{tlg_stats}",
        "",
        "## 分界面",
        "",
    ]
    for screen, items in (man.get("screens") or {}).items():
        if not items:
            continue
        lines.append(f"### `{screen}`")
        for it in items:
            lines.append(
                f"- `{it['name']}` — layers={it.get('layers')} hotspots={it.get('hotspots')} bindings={it.get('bindings')}"
            )
        lines.append("")
    lines += [
        "## 坐标可信度",
        "",
        "- PBD 几何为启发式提取（与 LimeLight 相同限制）：部分 `cx/cy/cw/ch` 可能噪声",
        "- **优先**使用 `*.hotspots.json` 中已过滤（宽高 1–1920、坐标 -100–2000）的条目",
        "- 绑定字符串 `Current.cmd(...)` 用于语义映射（设置项 key）",
        "- 精灵图见 `tlg-png/`，可与热区叠图校验",
        "",
        "## 产物",
        "",
        "| 路径 | 说明 |",
        "|---|---|",
        "| `pixel-reverse/pbd-layers/*.hotspots.json` | 每屏热区 |",
        "| `pixel-reverse/pbd-layers/*.json` | 全量图层 |",
        "| `pixel-reverse/tlg-png/` | TLG→PNG |",
        "| `pixel-reverse/PIXEL-REVERSE.md` | 本说明 |",
        "",
    ]
    (OUT / "PIXEL-REVERSE.md").write_text("\n".join(lines), encoding="utf-8")

    # screen atlas compact
    atlas = {"generated_at": datetime.now(timezone.utc).isoformat(), "screens": {}}
    for screen, items in (man.get("screens") or {}).items():
        atlas["screens"][screen] = []
        for it in items:
            hs_path = PBD_OUT / f"{Path(it['name']).stem}.hotspots.json"
            if not hs_path.is_file():
                continue
            doc = json.loads(hs_path.read_text(encoding="utf-8"))
            atlas["screens"][screen].append(
                {
                    "pbd": it["name"],
                    "hotspot_count": len(doc.get("hotspots") or []),
                    "hotspots_sample": (doc.get("hotspots") or [])[:15],
                    "bindings_sample": (doc.get("bindings") or [])[:8],
                }
            )
    (OUT / "screen-atlas.json").write_text(json.dumps(atlas, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # ensure pillow via Angelic uv if needed
    print("=== parse PBD ===", flush=True)
    pbd_stats = parse_all_pbd()
    print(pbd_stats, flush=True)
    print("=== decode TLG ===", flush=True)
    tlg_stats = decode_tlg()
    print(tlg_stats, flush=True)
    write_report(pbd_stats, tlg_stats)
    print("DONE", OUT, flush=True)


if __name__ == "__main__":
    main()
