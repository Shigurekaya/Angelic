# -*- coding: utf-8 -*-
"""Audit Angelic view-state UI coverage and synthesize reference composites.

Focuses on the player's normal idle/default menu state, not hover-only states.
Uses the extracted filtered-cn-jp assets plus reverse-layer metadata where available.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:/gamedev/Angelic")
SRC = ROOT / "docs" / "ui-extract"
FILT = SRC / "ui-cn-jp-static" / "filtered-cn-jp"
PBD = SRC / "pixel-reverse" / "pbd-layers"
TLG = SRC / "pixel-reverse" / "tlg-png"
PREV = ROOT / "ui-preview" / "assets"
OUT = SRC / "pixel-reverse" / "_view_ref"
REPORT = ROOT / "docs" / "ui-extract" / "pixel-reverse" / "view_state_audit.json"

TARGETS = {
    "title": ["title__bg0.png", "title__pack.png", "title_locale_cn__pack.png"],
    "option": [
        "option__bg0.png", "option__pack.png", "option_4text__pack.png", "option_5sound1__pack.png",
        "option_5sound2__pack.png", "option_6dialog__pack.png", "option_7mouse__pack.png",
        "option_8keyboard1__pack.png", "option_9gamepad__pack.png",
    ],
    "file_load": ["file_load__bg0.png", "file_load__pack.png"],
    "extra_cg": ["extra__bg0.png", "extra__pack.png", "extra_locale_cn__pack.png", "extra_cg__pack.png", "extra_cgview__pack.png"],
    "scnchart": ["scnchart__bg0.png", "scnchart__pack.png"],
}

SCREEN_STEMS = {
    "title": ["title", "title_locale_cn"],
    "option": ["option", "option_0simple", "option_1display", "option_2game1", "option_3game2", "option_4text", "option_5sound1", "option_6dialog", "option_7mouse", "option_8keyboard1", "option_9gamepad"],
    "file_load": ["file_load"],
    "extra_cg": ["extra", "extra_cg"],
    "scnchart": ["scnchart"],
}


def load_img(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    return Image.open(path).convert("RGBA")


def save_if(img: Image.Image | None, path: Path) -> bool:
    if img is None:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    return True


def list_files(d: Path, exts: Iterable[str]) -> list[str]:
    if not d.exists():
        return []
    out = []
    for p in sorted(d.iterdir()):
        if p.is_file() and p.suffix.lower() in exts:
            out.append(p.name)
    return out


def parse_json(p: Path) -> dict:
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def pack_lookup() -> set[str]:
    names = set()
    for d in [TLG, PREV / "packs"]:
        for n in list_files(d, {".png", ".jpg", ".jpeg", ".webp"}):
            names.add(n)
    return names


def screen_hotspot_summary(stem: str) -> dict:
    p = PBD / f"{stem}.hotspots.json"
    d = parse_json(p)
    hs = d.get("hotspots") or []
    bd = d.get("bindings") or []
    return {
        "file": p.as_posix(),
        "exists": p.exists(),
        "hotspots": len(hs),
        "bindings": len(bd),
        "layers": [h.get("layer_id") for h in hs if h.get("layer_id")][:80],
        "binding_layers": [b.get("layer_id") for b in bd if b.get("layer_id")][:80],
    }


def gather_unused_pack_names() -> dict:
    existing = pack_lookup()
    used = set()
    refs = []
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix.lower() in {".py", ".rpy", ".json", ".txt", ".ini", ".toml"}:
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for name in existing:
                if name in text:
                    used.add(name)
                    refs.append((f.as_posix(), name))
    unused = sorted(existing - used)
    return {"existing": sorted(existing), "used": sorted(used), "unused": unused, "refs": refs}


def composite_from_packs(kind: str) -> Image.Image | None:
    if kind == "title":
        bg = load_img(PREV / "title" / "bg0.png") or load_img(FILT / "title_bg0.png")
        if bg is None:
            return None
        canvas = bg.copy().resize((1920, 1080), Image.Resampling.LANCZOS) if bg.size != (1920, 1080) else bg.copy()
        logo = load_img(PREV / "title" / "logo_cn.png") or load_img(FILT / "locale" / "cn" / "title_logo_cn.png")
        if logo:
            w = min(640, logo.width)
            logo = logo.resize((w, int(logo.height * w / logo.width)), Image.Resampling.LANCZOS)
            canvas.alpha_composite(logo, (36, 36))
        return canvas
    if kind == "option":
        bg = load_img(PREV / "settings" / "bg.png")
        pack = load_img(PREV / "settings" / "option__pack.png") or load_img(PREV / "packs" / "option__pack.png")
        if bg is None and pack is None:
            return None
        canvas = bg.copy() if bg else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
        if pack:
            canvas.alpha_composite(pack, (0, 0))
        return canvas
    if kind == "file_load":
        bg = load_img(PREV / "load" / "bg.png")
        pack = load_img(PREV / "load" / "pack.png")
        if bg is None and pack is None:
            return None
        canvas = bg.copy() if bg else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
        if pack:
            canvas.alpha_composite(pack, (0, 0))
        return canvas
    if kind == "extra_cg":
        bg = load_img(PREV / "cg" / "bg.png")
        pack = load_img(PREV / "cg" / "extra_locale_cn__pack.png") or load_img(PREV / "cg" / "extra__pack.png")
        if bg is None and pack is None:
            return None
        canvas = bg.copy() if bg else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
        if pack:
            canvas.alpha_composite(pack, (0, 0))
        return canvas
    if kind == "scnchart":
        bg = load_img(PREV / "flowchart" / "bg.png")
        pack = load_img(PREV / "flowchart" / "pack.png")
        if bg is None and pack is None:
            return None
        canvas = bg.copy() if bg else Image.new("RGBA", (1920, 1080), (0, 0, 0, 255))
        if pack:
            canvas.alpha_composite(pack, (0, 0))
        return canvas
    return None


def draw_missing_overlay(img: Image.Image, title: str, missing: list[str]) -> Image.Image:
    out = img.copy()
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype(str(ROOT / "ui-preview" / "assets" / "ref" / "font" / "SourceHanSansSC-Regular.otf"), 24)
    except Exception:
        font = ImageFont.load_default()
    d.rectangle((16, 16, 840, 110 + 30 * max(1, len(missing))), fill=(0, 0, 0, 160))
    d.text((28, 24), title, fill=(255, 255, 255, 255), font=font)
    for i, s in enumerate(missing[:20]):
        d.text((28, 58 + i * 28), s, fill=(255, 240, 140, 255), font=font)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {
        "title": screen_hotspot_summary("title"),
        "title_locale_cn": screen_hotspot_summary("title_locale_cn"),
        "option": screen_hotspot_summary("option"),
        "option_0simple": screen_hotspot_summary("option_0simple"),
        "option_1display": screen_hotspot_summary("option_1display"),
        "option_2game1": screen_hotspot_summary("option_2game1"),
        "option_3game2": screen_hotspot_summary("option_3game2"),
        "option_4text": screen_hotspot_summary("option_4text"),
        "option_5sound1": screen_hotspot_summary("option_5sound1"),
        "option_6dialog": screen_hotspot_summary("option_6dialog"),
        "option_7mouse": screen_hotspot_summary("option_7mouse"),
        "option_8keyboard1": screen_hotspot_summary("option_8keyboard1"),
        "option_9gamepad": screen_hotspot_summary("option_9gamepad"),
        "file_load": screen_hotspot_summary("file_load"),
        "extra": screen_hotspot_summary("extra"),
        "extra_cg": screen_hotspot_summary("extra_cg"),
        "scnchart": screen_hotspot_summary("scnchart"),
        "packs": {},
        "unused": gather_unused_pack_names(),
    }
    for kind, names in TARGETS.items():
        missing = [n for n in names if not ((TLG / n).exists() or (PREV / "packs" / n).exists() or (PREV / kind / n).exists())]
        summary["packs"][kind] = {"required": names, "missing": missing}
        comp = composite_from_packs(kind)
        if comp is not None:
            save_if(draw_missing_overlay(comp, f"{kind} view-state ref / missing {len(missing)}", missing), OUT / f"{kind}.png")
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "report": REPORT.as_posix(),
        "ref_dir": OUT.as_posix(),
        "missing_counts": {k: len(v["missing"]) for k, v in summary["packs"].items()},
        "unused_count": len(summary["unused"]["unused"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
