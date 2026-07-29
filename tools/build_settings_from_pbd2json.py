# -*- coding: utf-8 -*-
"""Build Angelic settings-layout.json from pbd2json layers (Cafe build_settings_plates equivalent).

Cafe: psb_22/psb_30 FreeMote left/top
Angelic: option_*.pbd via pbd2json x/y/width/height
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(r"D:/gamedev/Angelic")
PBD = ROOT / "docs/ui-extract/pixel-reverse/pbd2json-layers"
LAYOUT = ROOT / "docs/ui-extract/pixel-reverse/settings-layout"
PREV = ROOT / "ui-preview/assets/settings"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/settings"

# tid -> pbd stem
PAGE_PBD = {
    "0": "option_0simple",
    "1": "option_1display",
    "2": "option_2game1",
    "3": "option_3game2",
    "4": "option_4text",
    "5a": "option_5sound1",
    "5b": "option_5sound2",
    "6": "option_6dialog",
    "8": "option_8keyboard1",
}
PAGE_LABEL = {
    "0": "基本设置",
    "1": "画面设置",
    "2": "游戏设置1",
    "3": "游戏设置2",
    "4": "文本设置",
    "5a": "音频1",
    "5b": "音频2",
    "6": "确认信息",
    "8": "键盘",
}

# page0 visible keys (Cafe-style simple page; keep skipall/movie as on PBD)
PAGE0_LEFT = ["fullscreen", "sqscr", "textspeed", "autospeed", "skipall"]
PAGE0_RIGHT = ["wave", "bgm", "se", "voice", "movie"]

LABEL_CN = {
    "fullscreen": "显示模式",
    "sqscr": "画面比例",
    "textspeed": "文本显示速度",
    "autospeed": "自动模式速度",
    "skipall": "快进未读文本",
    "wave": "总音量",
    "bgm": "ＢＧＭ",
    "se": "ＳＥ（游戏音效）",
    "voice": "语音（游戏中）",
    "movie": "视频",
}
OPTS = {
    "fullscreen": ["窗口模式", "全屏模式"],
    "sqscr": ["16:9", "4:3"],
    "skipall": ["关", "开"],
}


def load_hs(stem: str) -> dict[str, dict]:
    p = PBD / f"{stem}.hotspots.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    return {h["name"]: h for h in doc.get("hotspots") or []}


def row_from_key(hs: dict[str, dict], key: str) -> dict | None:
    area = hs.get(key)
    if not area:
        return None
    off = hs.get(f"{key}_off")
    on = hs.get(f"{key}_on")
    slider = hs.get(f"{key}_slider")
    mute = hs.get(f"{key}_mute")

    # label row: nearest label_*_jump above/near control
    icon_x = int(area["left"])
    label_x = int(area["left"])
    label_y = int(area["top"])
    label_h = 32
    best = None
    for name, h in hs.items():
        if not (name.startswith("label_") and name.endswith("_jump")):
            continue
        if abs(h["left"] - area["left"]) > 120:
            continue
        dy = area["top"] - h["top"]
        if 20 <= dy <= 80:
            dist = abs(dy - 51) + abs(h["left"] - area["left"])
            if best is None or dist < best[0]:
                best = (dist, h)
    if best:
        h = best[1]
        icon_x = int(h["left"])
        label_x = int(h["left"] + h["width"] + 4)
        label_y = int(h["top"])
        label_h = int(h["height"])
        # 「详细」按钮本身常为 label_*_jump
        item_detail = {
            "x": int(h["left"]),
            "y": int(h["top"]),
            "w": int(h["width"]),
            "h": int(h["height"]),
        }
    else:
        item_detail = None

    item = {
        "slot": key,
        "key": key,
        "label": LABEL_CN.get(key, key),
        "icon_x": icon_x,
        "x": label_x,
        "y": label_y,
        "w": 480,
        "h": label_h,
    }
    if item_detail:
        item["detail"] = item_detail

    if off and on:
        item["type"] = "toggle"
        item["options"] = OPTS.get(key, ["关", "开"])
        item["ctrl"] = {
            "x": off["left"],
            "y": off["top"],
            "w": on["left"] + on["width"] - off["left"],
            "h": off["height"],
            "slot": key,
        }
        item["chips"] = [
            {"x": off["left"], "y": off["top"], "w": off["width"], "h": off["height"], "i": 0},
            {"x": on["left"], "y": on["top"], "w": on["width"], "h": on["height"], "i": 1},
        ]
        item["chip_n"] = 2
        item["chip_w"] = off["width"]
        item["chip_h"] = off["height"]
        item["chip_gap"] = on["left"] - off["left"] - off["width"]
    elif slider:
        item["type"] = "slider"
        rail_x = slider["left"]
        rail_y = slider["top"]
        # prefer rail uistate size if present in area
        item["ctrl"] = {"x": rail_x, "y": rail_y, "w": slider["width"], "h": slider["height"], "slot": key}
        # 视觉轨高约 13；在 PBD 槽内垂直居中，宽度用官方槽宽
        rh = 13
        item["track"] = {
            "x": rail_x,
            "y": rail_y + max(0, (slider["height"] - rh) // 2),
            "w": int(slider["width"]),
            "h": rh,
        }
        if mute:
            item["mute"] = True
            item["mute_pos"] = {"x": mute["left"], "y": mute["top"], "w": mute["width"], "h": mute["height"]}
    else:
        item["type"] = "toggle"
        item["ctrl"] = {
            "x": area["left"],
            "y": area["top"],
            "w": area["width"],
            "h": area["height"],
            "slot": key,
        }
    return item


def build_page0(hs: dict[str, dict]) -> list[dict]:
    rows = []
    for key in PAGE0_LEFT + PAGE0_RIGHT:
        row = row_from_key(hs, key)
        if row:
            rows.append(row)
    return rows


def slots_from_rows(rows: list[dict]) -> list[dict]:
    slots = []
    for r in rows:
        ctrl = r.get("ctrl") or {}
        item = {
            "key": r["key"],
            "label": r["label"],
            "type": r["type"],
            "help_key": r["key"],
            "x": int(ctrl.get("x", r["x"])),
            "y": int(ctrl.get("y", r["y"])),
            "w": int(ctrl.get("w", r["w"])),
            "h": int(ctrl.get("h", r["h"])),
            "default": 0.55 if r["type"] == "slider" else 0,
        }
        if r.get("options"):
            item["options"] = r["options"]
        if r.get("chips"):
            item["chips"] = r["chips"]
            item["chip_n"] = r.get("chip_n", len(r["chips"]))
            item["chip_w"] = r.get("chip_w")
            item["chip_h"] = r.get("chip_h")
        if r.get("track"):
            item["track"] = r["track"]
            item["type"] = "slider"
            item["x"] = r["track"]["x"]
            item["y"] = r["track"]["y"]
            item["w"] = r["track"]["w"]
            item["h"] = r["track"]["h"]
            item["num"] = {"x": item["x"] + item["w"] + 10, "y": item["y"] - 6, "w": 56, "h": 24}
        if r.get("mute"):
            item["mute"] = True
            item["mute_pos"] = r["mute_pos"]
        slots.append(item)
    return slots


def build_tabs_layout(hs0: dict[str, dict]) -> list[dict]:
    items = []
    for i, tid in enumerate(["0", "1", "2", "3", "4", "5a", "6", "8", "5b"]):
        # map to pageN radios on option_0simple
        page_i = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5a": 5, "5b": 5, "6": 6, "8": 8}.get(tid, i)
        h = hs0.get(f"page{page_i}")
        if h:
            items.append(
                {
                    "id": tid,
                    "label": PAGE_LABEL.get(tid, tid),
                    "x": h["left"],
                    "y": h["top"],
                    "w": h["width"],
                    "h": h["height"],
                }
            )
        else:
            items.append({"id": tid, "label": PAGE_LABEL.get(tid, tid), "x": 465 + i * 128, "y": 0, "w": 128, "h": 81})
    return items


def main() -> None:
    hs0 = load_hs("option_0simple")
    rows0 = build_page0(hs0)
    tabs = []
    interaction = {}

    # page0 from official PBD
    tabs.append(
        {
            "id": "0",
            "cafe_id": "0_simple",
            "label": PAGE_LABEL["0"],
            "rows": rows0,
        }
    )
    interaction["0"] = slots_from_rows(rows0)

    # other pages: export all area/button/slider/toggle with x/y as hotspots slots
    for tid, stem in PAGE_PBD.items():
        if tid == "0":
            continue
        hs = load_hs(stem)
        rows = []
        slots = []
        for name, h in sorted(hs.items(), key=lambda kv: (kv[1]["top"], kv[1]["left"])):
            cls = h.get("class")
            if cls not in ("area", "slider", "toggle", "button") and not (
                name.endswith("_slider") or name.endswith("_mute") or name.endswith("_off") or name.endswith("_on")
            ):
                continue
            if name.startswith("page") or name.startswith("label_") or name.startswith("_"):
                continue
            # prefer primary keys without _off/_on/_slider/_mute suffix for rows
            if name.endswith(("_off", "_on", "_slider", "_mute", "_value", "_numbase", "_play", "_test")):
                continue
            key = name
            row = {
                "slot": key,
                "key": key,
                "label": LABEL_CN.get(key, key),
                "type": "slider" if hs.get(f"{key}_slider") else ("toggle" if hs.get(f"{key}_off") else "toggle"),
                "x": h["left"],
                "y": h["top"],
                "w": h["width"],
                "h": h["height"],
                "icon_x": h["left"],
                "ctrl": {"x": h["left"], "y": h["top"], "w": h["width"], "h": h["height"], "slot": key},
            }
            if hs.get(f"{key}_off") and hs.get(f"{key}_on"):
                off, on = hs[f"{key}_off"], hs[f"{key}_on"]
                row["chips"] = [
                    {"x": off["left"], "y": off["top"], "w": off["width"], "h": off["height"], "i": 0},
                    {"x": on["left"], "y": on["top"], "w": on["width"], "h": on["height"], "i": 1},
                ]
                row["chip_n"] = 2
                row["ctrl"] = {
                    "x": off["left"],
                    "y": off["top"],
                    "w": on["left"] + on["width"] - off["left"],
                    "h": off["height"],
                    "slot": key,
                }
                row["options"] = OPTS.get(key, ["关", "开"])
            if hs.get(f"{key}_slider"):
                sl = hs[f"{key}_slider"]
                row["type"] = "slider"
                row["track"] = {"x": sl["left"], "y": sl["top"] + 20, "w": min(610, sl["width"]), "h": 13}
                row["ctrl"] = {"x": sl["left"], "y": sl["top"], "w": sl["width"], "h": sl["height"], "slot": key}
                if hs.get(f"{key}_mute"):
                    m = hs[f"{key}_mute"]
                    row["mute"] = True
                    row["mute_pos"] = {"x": m["left"], "y": m["top"], "w": m["width"], "h": m["height"]}
            rows.append(row)
        tabs.append({"id": tid, "cafe_id": tid, "label": PAGE_LABEL.get(tid, tid), "rows": rows})
        interaction[tid] = slots_from_rows(rows)

    # chassis / footer from page0
    footer = []
    for fid, name in (("init", "reset"), ("title", "title"), ("back", "back")):
        h = hs0.get(name)
        if h:
            footer.append(
                {
                    "id": fid,
                    "label": {"init": "恢复默认设置", "title": "标题画面", "back": "游戏画面"}[fid],
                    "x": h["left"],
                    "y": h["top"],
                    "w": h["width"],
                    "h": h["height"],
                }
            )

    helpbase = hs0.get("helpbase") or {"left": 27, "top": 979, "width": 731, "height": 77}
    layout = {
        "source": "pbd2json option_*.pbd (Cafe-style strict unpack; absolute x/y)",
        "resolution": {"width": 1920, "height": 1080},
        "chassis": {
            "bg": {"x": 0, "y": 0, "w": 1920, "h": 1080, "src": "option__bg0"},
            "sep_a": {k: hs0["sep_a"][k] for k in ("left", "top", "width", "height")} if "sep_a" in hs0 else None,
            "sep_b": {k: hs0["sep_b"][k] for k in ("left", "top", "width", "height")} if "sep_b" in hs0 else None,
            "source": "option_0simple.pbd via pbd2json",
        },
        "grid": {
            "note": "derived from option_0simple.pbd absolute rects",
            "left_ctrl_x": 130,
            "right_rail_x": 1098,
            "mute_x": 1021,
            "row_ys": sorted({r["y"] for r in rows0 if r["key"] in PAGE0_LEFT}),
        },
        "tabs": tabs,
        "footer": footer,
        "help_box": {
            "x": helpbase["left"],
            "y": helpbase["top"],
            "w": helpbase["width"],
            "h": helpbase["height"],
        },
        "tabs_layout": {"items": build_tabs_layout(hs0)},
        "exclude_pages": ["7", "9"],
    }

    LAYOUT.mkdir(parents=True, exist_ok=True)
    out_layout = LAYOUT / "angelic_settings_layout.json"
    out_bare = LAYOUT / "official_bare_pixels.json"
    out_layout.write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
    out_bare.write_text(
        json.dumps(
            {
                **layout,
                "tool": "pbd2json.exe",
                "pbd_layers_dir": "docs/ui-extract/pixel-reverse/pbd2json-layers",
                "note": "Cafe Stella equivalent of FreeMote PSB left/top",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    # sync interaction + meta fragments
    for dest_root in (PREV, RENPY):
        dest_root.mkdir(parents=True, exist_ok=True)
        (dest_root / "interaction_slots.json").write_text(
            json.dumps(interaction, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        meta_path = dest_root / "meta.json"
        meta = {}
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["footer"] = footer
        meta["help_box"] = layout["help_box"]
        meta["tabs_layout"] = layout["tabs_layout"]
        meta["layout"] = "docs/ui-extract/pixel-reverse/settings-layout/angelic_settings_layout.json"
        meta["truth"] = "docs/ui-extract/pixel-reverse/pbd2json-layers/option_0simple.hotspots.json"
        meta["note"] = "official bare pixels from pbd2json (Cafe-style unpack)"
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("wrote", out_layout)
    print("page0 rows", len(rows0))
    for r in rows0:
        print(" ", r["key"], r["type"], "label", r["x"], r["y"], "ctrl", r.get("ctrl"))
    print("footer", footer)


if __name__ == "__main__":
    main()
