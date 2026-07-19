# -*- coding: utf-8 -*-
"""Bake Angelic title — 只用解包原片，禁止自制/缩放叠字。

对照 renpy-cafe：
  - 背景 / logo / pack 切片原样拷贝（仅洋红键）
  - 文字钮：title_locale_cn__pack 原片
  - 切背景：title__pack s001/s002/s003 原片
  - 语言：langselect 色板原片 + 解包「文」「A」原片分文件
    （运行时分层叠放，不在烘焙时自制合成图）
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FILT = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
PREV = ROOT / "ui-preview/assets/title"
RENPY_IMG = ROOT.parent / "renpy-angelic/game/images/angelic/title"
RENPY_GAME = ROOT.parent / "renpy-angelic/game"

# 解包切片索引（字模目视核对）：青=idle，黄=hover
SLICE_MAP = {
    "start": {"idle": 11, "hover": 20},
    "load": {"idle": 14, "hover": 16, "selected": 19},
    "continue": {"idle": 15, "hover": 12, "selected": 13},
    "flowchart": {"idle": 0, "hover": 3, "selected": 23},
    "extra": {"idle": 17, "hover": 4, "selected": 5},
    "after": {"idle": 18, "hover": 6, "selected": 9},
    "system": {"idle": 8, "hover": 10},
    "exit": {"idle": 2, "hover": 1, "selected": 22},
}

BUTTON_ORDER = [
    ("start", "从头开始", "start"),
    ("load", "载入进度", "load"),
    ("continue", "继续游戏", "continue"),
    ("flowchart", "流程图", "flowchart"),
    ("extra", "鉴赏模式", "cg"),
    ("after", "追加剧情", "afterstory"),
    ("system", "系统设定", "settings"),
    ("exit", "退出游戏", "quit"),
]

# 底栏坐标：解包字模在原版查看态上的模板匹配结果（非均分猜测）
BTN_XY = {
    "start": (137, 1003),
    "load": (354, 1003),
    "continue": (570, 1003),  # 原版常半透禁用，字模匹配不可靠，按间距内插
    "flowchart": (804, 1001),
    "extra": (1010, 1003),
    "after": (1228, 1003),
    "system": (1449, 1003),
    "exit": (1665, 1001),
}

# 右上语言 / 右下切背景：原版查看态匹配
LAYOUT = {
    "lang_xy": (1798, 59),
    "reload_xy": (1798, 1005),
}


def magenta_key(im: Image.Image) -> Image.Image:
    """仅去洋红色键（解包 TLG 常用），不改其它像素。"""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)
            elif r >= 200 and b >= 200 and g <= 90 and abs(r - b) < 40:
                px[x, y] = (0, 0, 0, 0)
    return im


def key_black(im: Image.Image) -> Image.Image:
    """字模黑底转透明（原片仍是黑底字模，不是自制）。"""
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r <= 18 and g <= 18 and b <= 18:
                px[x, y] = (0, 0, 0, 0)
    return im


def ensure(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def slice_file(pack: str, idx: int) -> Path:
    d = SLICES / pack
    matches = sorted(d.glob(f"s{idx:03d}_*.png"))
    if not matches:
        raise FileNotFoundError(f"{pack} s{idx:03d}")
    return matches[0]


def load_text_slice(pack: str, idx: int) -> Image.Image:
    return key_black(magenta_key(Image.open(slice_file(pack, idx))))


def load_chrome_slice(pack: str, idx: int) -> Image.Image:
    """色板/图标：只去洋红，保留黑边（原版样式）。"""
    return magenta_key(Image.open(slice_file(pack, idx)))


def extract_white_glyphs(atlas: Image.Image) -> list[tuple[Image.Image, int, int, int, int]]:
    """Return list of (crop, x0,y0,x1,y1) for small white glyphs in atlas."""
    px = atlas.load()
    w, h = atlas.size
    seen = [[False] * w for _ in range(h)]
    out: list[tuple[Image.Image, int, int, int, int]] = []
    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                continue
            r, g, b, a = px[x, y]
            if a < 40 or not (r > 200 and g > 200 and b > 200):
                seen[y][x] = True
                continue
            stack = [(x, y)]
            seen[y][x] = True
            minx = maxx = x
            miny = maxy = y
            area = 0
            while stack:
                cx, cy = stack.pop()
                area += 1
                minx = min(minx, cx)
                maxx = max(maxx, cx)
                miny = min(miny, cy)
                maxy = max(maxy, cy)
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                            seen[ny][nx] = True
                            rr, gg, bb, aa = px[nx, ny]
                            if aa > 40 and rr > 200 and gg > 200 and bb > 200:
                                stack.append((nx, ny))
            bw, bh = maxx - minx + 1, maxy - miny + 1
            if 40 <= area <= 800 and bw <= 40 and bh <= 40:
                crop = key_black(atlas.crop((minx, miny, maxx + 1, maxy + 1)))
                out.append((crop, minx, miny, maxx + 1, maxy + 1))
    out.sort(key=lambda t: -(t[0].width * t[0].height))
    return out


def bake_lang(out_dir: Path) -> dict:
    """语言：原版色板 + atlas 内原版「文/A/箭头」按原相对位置叠放，不缩放、不手绘。"""
    off = load_chrome_slice("langselect__pack", 2)
    over = load_chrome_slice("langselect__pack", 6)
    on = load_chrome_slice("langselect__pack", 3)
    off.save(out_dir / "icon_lang.png")
    over.save(out_dir / "icon_lang_hover.png")
    on.save(out_dir / "icon_lang_on.png")

    atlas = magenta_key(Image.open(TLG / "langselect__pack.png"))
    glyphs = extract_white_glyphs(atlas)
    # 在 atlas 上这组字模是成套的，取包围盒左上角为原点，再平移到色板内
    if not glyphs:
        x, y = LAYOUT["lang_xy"]
        return {
            "lang": {
                "x": x,
                "y": y,
                "w": off.width,
                "h": off.height,
                "idle": "icon_lang.png",
                "hover": "icon_lang_hover.png",
                "overlays": [],
                "action": "lang",
            }
        }

    minx = min(g[1] for g in glyphs)
    miny = min(g[2] for g in glyphs)
    maxx = max(g[3] for g in glyphs)
    maxy = max(g[4] for g in glyphs)
    cluster_w, cluster_h = maxx - minx, maxy - miny
    # 色板内居中放置整组原片（相对偏移保持 atlas 原样）
    ox = max(0, (off.width - cluster_w) // 2)
    oy = max(0, (off.height - cluster_h) // 2)

    overlays = []
    for i, (crop, x0, y0, _x1, _y1) in enumerate(glyphs):
        name = f"icon_lang_glyph_{i}.png"
        crop.save(out_dir / name)
        overlays.append(
            {
                "file": name,
                "x": ox + (x0 - minx),
                "y": oy + (y0 - miny),
                "w": crop.width,
                "h": crop.height,
            }
        )

    x, y = LAYOUT["lang_xy"]
    return {
        "lang": {
            "x": x,
            "y": y,
            "w": off.width,
            "h": off.height,
            "idle": "icon_lang.png",
            "hover": "icon_lang_hover.png",
            "overlays": overlays,
            "action": "lang",
        }
    }


def bake_reload(out_dir: Path) -> dict:
    idle = load_chrome_slice("title__pack", 1)
    hover = load_chrome_slice("title__pack", 2)
    on = load_chrome_slice("title__pack", 3)
    idle.save(out_dir / "icon_reload.png")
    hover.save(out_dir / "icon_reload_hover.png")
    on.save(out_dir / "icon_reload_on.png")
    x, y = LAYOUT["reload_xy"]
    return {
        "reload": {
            "x": x,
            "y": y,
            "w": idle.width,
            "h": idle.height,
            "idle": "icon_reload.png",
            "hover": "icon_reload_hover.png",
            "action": "cycle_bg",
        }
    }


def place_buttons(raw_btns: list[dict]) -> list[dict]:
    """按实测坐标落点，保留解包字模原生宽高。"""
    out = []
    for b in raw_btns:
        x, y = BTN_XY[b["id"]]
        nb = dict(b)
        nb["x"] = int(x)
        nb["y"] = int(y)
        out.append(nb)
    return out


def main() -> None:
    ensure(PREV)
    btn_dir = ensure(PREV / "buttons")

    # 清掉旧的自制合成残留
    for stale in (
        "view_bg0.png",
        "view_bg1.png",
        "view_bg2.png",
        "view_bg3.png",
        "view_bg4.png",
        "view_bg5.png",
        "view_bg6.png",
        "view_bg7.png",
        "view_state.png",
        "view_state_ref.png",
    ):
        p = PREV / stale
        if p.exists():
            p.unlink()

    for i in range(8):
        src = FILT / f"title_bg{i}.png"
        if src.exists():
            shutil.copy2(src, PREV / f"bg{i}.png")
    logo_src = FILT / "locale/cn/title_logo_cn.png"
    if not logo_src.exists():
        logo_src = FILT / "title_logo_cn.png"
    if logo_src.exists():
        shutil.copy2(logo_src, PREV / "logo_cn.png")

    raw_btns = []
    for key, label, action in BUTTON_ORDER:
        sm = SLICE_MAP[key]
        idle = load_text_slice("title_locale_cn__pack", sm["idle"])
        hover = load_text_slice("title_locale_cn__pack", sm["hover"])
        # 原版查看态「继续游戏」无进度时半透；用原片降 alpha，不换素材
        if key == "continue":
            dim = idle.copy()
            a = dim.split()[-1].point(lambda v: int(v * 0.42))
            dim.putalpha(a)
            dim.save(btn_dir / f"{key}_idle.png")
            idle.save(btn_dir / f"{key}_idle_full.png")
        else:
            idle.save(btn_dir / f"{key}_idle.png")
        hover.save(btn_dir / f"{key}_hover.png")
        if "selected" in sm:
            load_text_slice("title_locale_cn__pack", sm["selected"]).save(
                btn_dir / f"{key}_selected.png"
            )
        raw_btns.append(
            {
                "id": key,
                "label": label,
                "action": action,
                "w": idle.width,
                "h": idle.height,
                "idle": f"buttons/{key}_idle.png",
                "hover": f"buttons/{key}_hover.png",
            }
        )
    buttons = place_buttons(raw_btns)

    icons = {}
    icons.update(bake_lang(PREV))
    icons.update(bake_reload(PREV))

    # QA 预览：只用原片叠放（字模原尺寸，不缩放）
    canvas = Image.open(PREV / "bg0.png").convert("RGBA")
    if (PREV / "logo_cn.png").exists():
        canvas.alpha_composite(Image.open(PREV / "logo_cn.png").convert("RGBA"), (0, 0))
    for b in buttons:
        canvas.alpha_composite(Image.open(PREV / b["idle"]), (b["x"], b["y"]))
    lang = icons["lang"]
    canvas.alpha_composite(Image.open(PREV / lang["idle"]), (lang["x"], lang["y"]))
    for ov in lang.get("overlays") or []:
        canvas.alpha_composite(
            Image.open(PREV / ov["file"]),
            (lang["x"] + int(ov["x"]), lang["y"] + int(ov["y"])),
        )
    rel = icons["reload"]
    canvas.alpha_composite(Image.open(PREV / rel["idle"]), (rel["x"], rel["y"]))
    canvas.save(PREV / "composite.png")
    canvas.save(PREV / "title_1to1_cn.png")

    hotspots = {
        "resolution": [1920, 1080],
        "layout": "bottom_hbar_unpack",
        "source": "title_bg* + title_logo_cn + title_locale_cn__pack + title__pack + langselect__pack",
        "note": "Original unpack tiles only. Lang glyphs layered at runtime, not homemade bake.",
        "logo": {"x": 0, "y": 0, "file": "logo_cn.png", "full_bleed": True},
        "layered": True,
        "bg_count": 8,
        "icons": icons,
        "buttons": buttons,
    }
    (PREV / "hotspots.json").write_text(
        json.dumps(hotspots, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    layout = {
        "source": hotspots["source"],
        "locale": "cn",
        "logo": {"x": 0, "y": 0},
        "btn_xy": BTN_XY,
        "language": {"x": lang["x"], "y": lang["y"]},
        "reload_title": {"x": rel["x"], "y": rel["y"]},
        "buttons": buttons,
        "layered": True,
    }
    (PREV / "title_1to1_layout.json").write_text(
        json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if RENPY_GAME.exists():
        shutil.copy2(PREV / "title_1to1_layout.json", RENPY_GAME / "title_1to1_layout.json")

    if RENPY_IMG.exists():
        shutil.rmtree(RENPY_IMG)
    shutil.copytree(PREV, RENPY_IMG)
    print("wrote", PREV)
    print(
        json.dumps(
            {
                "buttons": [b["id"] for b in buttons],
                "lang_overlays": [o["file"] for o in lang.get("overlays") or []],
                "reload": rel["idle"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
