# -*- coding: utf-8 -*-
"""Complete Cafe-style UI unpack for Angelic.

1) slice all *__pack.png (and other atlases)
2) export pbd2json hotspots -> preview/renpy (Cafe left/top format)
3) rewrite title/file/hud/qconf/extra hotspot json from official PBD
4) screen-atlas.json
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r"D:/gamedev/Angelic")
sys.path.insert(0, str(ROOT / "tools"))

from slice_all_ui_packs import slice_one, OUT as SLICES_OUT, TLG  # noqa: E402

PBD2 = ROOT / "docs/ui-extract/pixel-reverse/pbd2json-layers"
PREV = ROOT / "ui-preview/assets"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic"
PIXEL = ROOT / "docs/ui-extract/pixel-reverse"

# screen -> renpy/preview subdir + which pbd stems feed hotspots
SCREEN_WIRE = {
    "title": {
        "dir": "title",
        "pbds": ["title.pbd", "title_locale_cn.pbd"],
        "primary": "title_locale_cn",
    },
    "settings": {
        "dir": "settings",
        "pbds": ["option.pbd", "option_0simple.pbd"],
        "primary": "option_0simple",
    },
    "file": {
        "dir": "file",
        "pbds": ["file.pbd", "file_load.pbd", "file_save.pbd", "file_quick.pbd"],
        "primary": "file_load",
    },
    "load": {"dir": "load", "pbds": ["file_load.pbd"], "primary": "file_load"},
    "qconf": {
        "dir": "qconf",
        "pbds": ["qconf.pbd", "qconf_load.pbd", "qconf_save.pbd", "qconf_text.pbd", "qconf_volume.pbd"],
        "primary": "qconf",
    },
    "hud": {
        "dir": "hud",
        "pbds": ["quickmenu.pbd", "window.pbd", "window_h.pbd", "voicebar.pbd"],
        "primary": "quickmenu",
    },
    "touch": {
        "dir": "touch",
        "pbds": ["touchuibar.pbd", "touchvolume.pbd"],
        "primary": "touchuibar",
    },
    "cg": {
        "dir": "cg",
        "pbds": ["extra_cg.pbd", "extra_cgview.pbd", "extra_locale_cn.pbd"],
        "primary": "extra_cg",
    },
    "flowchart": {"dir": "flowchart", "pbds": ["scnchart.pbd"], "primary": "scnchart"},
    "phonechat": {"dir": "phonechat", "pbds": ["phonechat.pbd"], "primary": "phonechat"},
    "afterstory": {"dir": "afterstory", "pbds": ["extra.pbd"], "primary": "extra"},
    "langselect": {"dir": "langselect", "pbds": ["title.pbd"], "primary": "title"},
}


def cafe_hotspot(h: dict) -> dict:
    """Normalize to Cafe FreeMote hotspot shape (left/top/width/height/name)."""
    return {
        "name": h.get("name") or h.get("uiname"),
        "left": int(h["left"]),
        "top": int(h["top"]),
        "width": int(h["width"]),
        "height": int(h["height"]),
        "class": h.get("class"),
        "uiname": h.get("uiname") or h.get("name"),
        "layer_id": h.get("name"),
        "x": int(h["left"]),
        "y": int(h["top"]),
        "w": int(h["width"]),
        "h": int(h["height"]),
    }


def load_hotspots(stem: str) -> list[dict]:
    p = PBD2 / f"{stem}.hotspots.json"
    if not p.exists():
        return []
    doc = json.loads(p.read_text(encoding="utf-8"))
    return [cafe_hotspot(h) for h in doc.get("hotspots") or []]


def slice_all_packs() -> dict:
    SLICES_OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for png in sorted(TLG.glob("*.png")):
        if png.name == "manifest.json":
            continue
        info = slice_one(png)
        results.append(info)
        print(f"SLICE {info['stem']}: {info['slices']}", flush=True)
    (SLICES_OUT / "index.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"packs": len(results), "slices": sum(r["slices"] for r in results)}


def export_screen_atlas() -> dict:
    atlas = {"generated_at": datetime.now(timezone.utc).isoformat(), "method": "pbd2json", "screens": {}}
    for screen, cfg in SCREEN_WIRE.items():
        entries = []
        for pbd_name in cfg["pbds"]:
            stem = Path(pbd_name).stem
            hs = load_hotspots(stem)
            entries.append(
                {
                    "pbd": pbd_name,
                    "hotspot_count": len(hs),
                    "hotspots_sample": hs[:12],
                }
            )
        atlas["screens"][screen] = entries
    out = PIXEL / "screen-atlas.json"
    out.write_text(json.dumps(atlas, ensure_ascii=False, indent=2), encoding="utf-8")
    # also to preview ref
    ref = PREV / "ref"
    ref.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out, ref / "screen-atlas.json")
    return atlas


def wire_title_hotspots() -> dict:
    """Merge pbd2json official rects into build_title hotspots (keep idle/hover/icons)."""
    hs = {h["name"]: h for h in load_hotspots("title_locale_cn")}
    title_hs = {h["name"]: h for h in load_hotspots("title")}
    order = ["start", "load", "continue", "flowchart", "extra", "after", "system", "exit"]

    # Prefer existing bake (idle/hover/icons); never wipe asset paths.
    existing: dict = {}
    for cand in (PREV / "title" / "hotspots.json", RENPY / "title" / "hotspots.json"):
        if cand.exists():
            try:
                existing = json.loads(cand.read_text(encoding="utf-8"))
                break
            except Exception:
                pass
    by_id = {str(b.get("id") or ""): dict(b) for b in (existing.get("buttons") or [])}

    buttons = []
    for name in order:
        h = hs.get(name)
        if not h:
            continue
        base = by_id.get(name) or {
            "id": name,
            "key": name,
            "label": name,
            "idle": f"buttons/{name}_idle.png",
            "hover": f"buttons/{name}_hover.png",
            "action": name,
        }
        base.update(
            {
                "id": name,
                "key": name,
                "x": h["left"],
                "y": h["top"],
                "w": h["width"],
                "h": h["height"],
                "left": h["left"],
                "top": h["top"],
                "width": h["width"],
                "height": h["height"],
                "source": "title_locale_cn.pbd via pbd2json",
            }
        )
        if "idle" not in base:
            base["idle"] = f"buttons/{name}_idle.png"
        if "hover" not in base:
            base["hover"] = f"buttons/{name}_hover.png"
        buttons.append(base)

    lang = []
    for name in ("lang_left", "lang_right"):
        h = title_hs.get(name)
        if h:
            lang.append(
                {
                    "id": name,
                    "x": h["left"],
                    "y": h["top"],
                    "w": h["width"],
                    "h": h["height"],
                    "left": h["left"],
                    "top": h["top"],
                    "width": h["width"],
                    "height": h["height"],
                }
            )

    icons = existing.get("icons") or {}
    doc = {
        "source": "pbd2json title_locale_cn.pbd + title.pbd (Cafe-style official coords)",
        "layout": "title_locale_cn_pbd2json",
        "resolution": [1920, 1080],
        "bg_count": int(existing.get("bg_count") or 8),
        "layered": True,
        "buttons": buttons,
        "icons": icons,
        "lang": lang,
        "hotspots": buttons + lang,
    }
    if existing.get("logo"):
        doc["logo"] = existing["logo"]
    for root in (PREV / "title", RENPY / "title", RENPY / "assets" / "title"):
        root.mkdir(parents=True, exist_ok=True)
        (root / "hotspots.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return doc


def wire_screen_hotspots() -> dict:
    stats = {}
    for screen, cfg in SCREEN_WIRE.items():
        dest_dirs = [PREV / cfg["dir"], RENPY / cfg["dir"]]
        # copy each pbd hotspots + primary as meta hotspots
        all_hs = []
        for pbd_name in cfg["pbds"]:
            stem = Path(pbd_name).stem
            hs = load_hotspots(stem)
            all_hs.extend(hs)
            for d in dest_dirs:
                d.mkdir(parents=True, exist_ok=True)
                (d / f"{stem}.hotspots.json").write_text(
                    json.dumps({"source": pbd_name, "tool": "pbd2json", "hotspots": hs}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        primary = load_hotspots(cfg["primary"])
        meta = {
            "source": f"pbd2json {cfg['primary']}.pbd",
            "tool": "pbd2json",
            "hotspots": primary,
            "all_count": len(all_hs),
        }
        for d in dest_dirs:
            (d / "hotspots.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            # Cafe-compatible interaction for file screens
            if screen in ("file", "load"):
                slots = []
                for h in primary:
                    if h.get("class") in ("button", "toggle", "radio", "area", "copy", "slider") or (
                        h["name"] and not h["name"].startswith("page") and h["name"] not in ("base", "caption")
                    ):
                        slots.append(
                            {
                                "key": h["name"],
                                "label": h["name"],
                                "type": h.get("class") or "button",
                                "x": h["left"],
                                "y": h["top"],
                                "w": h["width"],
                                "h": h["height"],
                                "left": h["left"],
                                "top": h["top"],
                            }
                        )
                (d / "interaction_slots.json").write_text(
                    json.dumps({"0": slots, "source": meta["source"]}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
        stats[screen] = len(primary)
        print(f"WIRE {screen}: {len(primary)} primary / {len(all_hs)} total", flush=True)
    return stats


def copy_hotspots_tree() -> int:
    """Mirror all pbd2json hotspots into renpy/hotspots for Cafe-like dump."""
    dest = RENPY / "hotspots"
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in PBD2.glob("*.hotspots.json"):
        shutil.copy2(p, dest / p.name)
        n += 1
    return n


def main() -> None:
    print("=== 1) slice all packs ===", flush=True)
    slice_stats = slice_all_packs()
    print(slice_stats, flush=True)

    print("=== 2) ensure pbd2json (already done if present) ===", flush=True)
    if not (PBD2 / "manifest.json").exists():
        from unpack_pbd2json_ui import main as unpack_pbd

        unpack_pbd()

    print("=== 3) screen atlas ===", flush=True)
    export_screen_atlas()

    print("=== 4) wire screen hotspots ===", flush=True)
    stats = wire_screen_hotspots()
    title_doc = wire_title_hotspots()
    print("title buttons", [(b["id"], b["x"], b["y"]) for b in title_doc["buttons"]], flush=True)

    print("=== 5) settings layout from pbd2json ===", flush=True)
    from build_settings_from_pbd2json import main as build_settings

    build_settings()

    n = copy_hotspots_tree()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "slice": slice_stats,
        "screens_wired": stats,
        "title_buttons": len(title_doc["buttons"]),
        "hotspots_mirrored": n,
        "method": "Cafe-style: pbd2json absolute x/y (= FreeMote left/top)",
    }
    (PIXEL / "FULL-UI-UNPACK-REPORT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE", report, flush=True)


if __name__ == "__main__":
    main()
