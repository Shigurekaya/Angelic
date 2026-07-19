# -*- coding: utf-8 -*-
"""Fast title QA: position drift + band diffs. Fail if drift > 8px."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
PREV = ROOT / "ui-preview/assets/title"
ORIG = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture/manual/title_orig_1080.png"
OUT = ROOT / "docs/ui-extract/pixel-reverse/_text_preview/title_qa"
OUT.mkdir(parents=True, exist_ok=True)

# expected from unpack-tile match on original view
EXPECT = {
    "start": (137, 1003),
    "load": (354, 1003),
    "continue": (570, 1003),
    "flowchart": (804, 1001),
    "extra": (1010, 1003),
    "after": (1228, 1003),
    "system": (1449, 1003),
    "exit": (1665, 1001),
    "lang": (1798, 59),
    "reload": (1798, 1005),
}


def mean_diff(a: Image.Image, b: Image.Image) -> float:
    a = a.convert("RGB")
    b = b.convert("RGB").resize(a.size)
    d = ImageChops.difference(a, b)
    hist = d.histogram()
    s = n = 0
    for i, c in enumerate(hist):
        s += (i % 256) * c
        n += c
    return s / max(1, n)


def match_near(orig: Image.Image, tile: Image.Image, cx: int, cy: int, rad: int = 24) -> tuple:
    tw, th = tile.size
    tp = tile.load()
    mask = []
    for yy in range(th):
        for xx in range(tw):
            r, g, b, a = tp[xx, yy]
            if a > 40 and r + g + b > 100:
                mask.append((xx, yy, r, g, b))
    best = None
    x0 = max(0, cx - rad)
    y0 = max(0, cy - rad)
    x1 = min(1920 - tw, cx + rad)
    y1 = min(1080 - th, cy + rad)
    for y in range(y0, y1 + 1, 1):
        for x in range(x0, x1 + 1, 1):
            s = 0
            for xx, yy, r, g, b in mask:
                or_, og, ob, _ = orig.getpixel((x + xx, y + yy))
                s += abs(r - or_) + abs(g - og) + abs(b - ob)
            sc = s / max(1, len(mask))
            if best is None or sc < best[0]:
                best = (sc, x, y)
    return best


def main() -> int:
    hs = json.loads((PREV / "hotspots.json").read_text(encoding="utf-8"))
    issues = []

    # hotspot vs expect
    for b in hs["buttons"]:
        ex = EXPECT[b["id"]]
        dx, dy = b["x"] - ex[0], b["y"] - ex[1]
        if abs(dx) > 2 or abs(dy) > 2:
            issues.append(f"hotspot {b['id']} ({b['x']},{b['y']}) != expect {ex}")
        p = PREV / b["idle"]
        if not p.exists():
            issues.append(f"missing {b['idle']}")

    for key in ("lang", "reload"):
        ic = hs["icons"][key]
        ex = EXPECT[key]
        if abs(ic["x"] - ex[0]) > 2 or abs(ic["y"] - ex[1]) > 2:
            issues.append(f"hotspot {key} ({ic['x']},{ic['y']}) != expect {ex}")

    if not ORIG.exists():
        issues.append("orig ref missing")
        print("issues", issues)
        return 1

    orig = Image.open(ORIG).convert("RGBA")
    comp = Image.open(PREV / "composite.png").convert("RGBA")

    # band diffs
    for name, box in (
        ("bottom", (0, 980, 1920, 1080)),
        ("tr", (1750, 0, 1920, 130)),
        ("br", (1750, 940, 1920, 1080)),
    ):
        md = mean_diff(orig.crop(box), comp.crop(box))
        print(f"band {name} mean_diff={md:.2f}")
        side = Image.new("RGB", (box[2] - box[0], (box[3] - box[1]) * 2))
        side.paste(orig.crop(box).convert("RGB"), (0, 0))
        side.paste(comp.crop(box).convert("RGB"), (0, box[3] - box[1]))
        side.save(OUT / f"qa_{name}.png")

    # rematch each button near expect (small radius = fast)
    print("--- rematch near expect ---")
    for b in hs["buttons"]:
        tile = Image.open(PREV / b["idle"]).convert("RGBA")
        ex = EXPECT[b["id"]]
        best = match_near(orig, tile, ex[0], ex[1], rad=20)
        print(f"  {b['id']:10} expect={ex} best={best[1:]} score={best[0]:.1f}")
        # continue 在原版常半透禁用，字模匹配分数差，不作为漂移依据
        if b["id"] == "continue":
            continue
        if best and best[0] < 200 and (abs(best[1] - b["x"]) > 8 or abs(best[2] - b["y"]) > 6):
            issues.append(
                f"drift {b['id']}: hotspot=({b['x']},{b['y']}) match=({best[1]},{best[2]})"
            )

    # lang layered preview
    plate = Image.open(PREV / hs["icons"]["lang"]["idle"]).convert("RGBA")
    for ov in hs["icons"]["lang"].get("overlays") or []:
        plate.alpha_composite(Image.open(PREV / ov["file"]), (int(ov["x"]), int(ov["y"])))
    plate.save(OUT / "lang_layered.png")
    # match lang plate near expect
    # lang / reload：允许 ±4px
    best = match_near(
        orig,
        Image.open(PREV / hs["icons"]["lang"]["idle"]).convert("RGBA"),
        EXPECT["lang"][0],
        EXPECT["lang"][1],
        rad=30,
    )
    print("lang plate match", best)
    if best and (abs(best[1] - hs["icons"]["lang"]["x"]) > 4 or abs(best[2] - hs["icons"]["lang"]["y"]) > 4):
        issues.append(f"lang drift hotspot=({hs['icons']['lang']['x']},{hs['icons']['lang']['y']}) match=({best[1]},{best[2]})")

    best_r = match_near(
        orig,
        Image.open(PREV / hs["icons"]["reload"]["idle"]).convert("RGBA"),
        EXPECT["reload"][0],
        EXPECT["reload"][1],
        rad=40,
    )
    print("reload match", best_r)
    if best_r and best_r[0] < 150 and (
        abs(best_r[1] - hs["icons"]["reload"]["x"]) > 6 or abs(best_r[2] - hs["icons"]["reload"]["y"]) > 6
    ):
        issues.append(
            f"reload drift hotspot=({hs['icons']['reload']['x']},{hs['icons']['reload']['y']}) match=({best_r[1]},{best_r[2]})"
        )

    # 资源完整性
    for name in ("bg0.png", "logo_cn.png", "composite.png", "hotspots.json"):
        if not (PREV / name).exists():
            issues.append(f"missing {name}")
    for b in hs["buttons"]:
        if not (PREV / b["idle"]).exists() or not (PREV / b["hover"]).exists():
            issues.append(f"missing btn art {b['id']}")
    if not (hs["icons"]["lang"].get("overlays")):
        issues.append("lang overlays empty")
    renpy = ROOT.parent / "renpy-angelic/game/images/angelic/title/hotspots.json"
    if not renpy.exists():
        issues.append("renpy title hotspots missing")
    else:
        rhs = json.loads(renpy.read_text(encoding="utf-8"))
        if rhs.get("buttons") != hs.get("buttons"):
            # compare coords at least
            for a, b in zip(rhs.get("buttons") or [], hs.get("buttons") or []):
                if (a.get("x"), a.get("y"), a.get("id")) != (b.get("x"), b.get("y"), b.get("id")):
                    issues.append("renpy hotspots out of sync")
                    break

    print("--- issues ---")
    for it in issues:
        print("!", it)
    print("issue_count", len(issues))
    (OUT / "issues.json").write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
