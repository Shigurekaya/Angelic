# -*- coding: utf-8 -*-
"""从原版 ig_option_*_1080 截图提取设定页坐标真值 + 标签箭头精灵。

产出：
  docs/ui-extract/pixel-reverse/settings-layout/settings_truth.json
  docs/ui-extract/pixel-reverse/settings-layout/label_arrow_truth.png
  docs/ui-extract/pixel-reverse/settings-layout/slice_placements.json（刷新分页 pack 落点）
"""
from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "docs/ui-extract/pixel-reverse/_orig_capture"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
OUT = ROOT / "docs/ui-extract/pixel-reverse/settings-layout"
KEEP = ["0", "1", "2", "3", "4", "5a", "5b", "6", "8"]


def load_rgba(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGBA"))


def load_bgr_a(path: Path):
    arr = load_rgba(path)
    return cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR), arr[:, :, 3]


def blue_mask(im: np.ndarray) -> np.ndarray:
    b, g, r = im[:, :, 2].astype(int), im[:, :, 1].astype(int), im[:, :, 0].astype(int)
    return ((b > 140) & (b > r + 30) & (b > g + 20)).astype(np.uint8) * 255


def export_arrow(im: np.ndarray) -> dict:
    # 左栏第一枚箭头胶囊（蓝块检测稳定点）
    box = im[237:287, 164:260].copy()
    b, g, r = box[:, :, 2].astype(int), box[:, :, 1].astype(int), box[:, :, 0].astype(int)
    keep = ((b > 140) & (b > r + 25) & (b > g + 15)) | ((r > 200) & (g > 200) & (b > 200))
    box[:, :, 3] = np.where(keep, 255, 0).astype(np.uint8)
    ys, xs = np.where(box[:, :, 3] > 0)
    crop = box[int(ys.min()) : int(ys.max()) + 1, int(xs.min()) : int(xs.max()) + 1]
    dest = OUT / "label_arrow_truth.png"
    Image.fromarray(crop).save(dest)
    return {
        "file": dest.name,
        "w": int(crop.shape[1]),
        "h": int(crop.shape[0]),
        "src_box": [164, 237, 260, 287],
    }


def analyze_page0(im: np.ndarray) -> dict:
    mask = blue_mask(im)
    mask[:120, :] = 0
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    chips, rails, icons_l, icons_r, mutes = [], [], [], [], []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if 480 <= w <= 650 and 55 <= h <= 90:
            chips.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})
        elif 200 <= w <= 500 and 12 <= h <= 28:
            rails.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})
        elif 70 <= w <= 120 and 35 <= h <= 55:
            item = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
            (icons_l if x < 600 else icons_r).append(item)
        elif 45 <= w <= 80 and 30 <= h <= 55 and x > 1400:
            mutes.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h)})

    def sorty(xs):
        return sorted(xs, key=lambda d: (d["y"], d["x"]))

    icons_l, icons_r = sorty(icons_l), sorty(icons_r)
    chips, rails, mutes = sorty(chips), sorty(rails), sorty(mutes)

    # 补 y=313 选中条（色相更亮时蓝块阈值可能漏）
    if not any(abs(c["y"] - 313) < 20 for c in chips):
        chips = [{"x": 195, "y": 313, "w": 571, "h": 75}] + chips
        chips = sorty(chips)

    # 过滤与底栏重叠的误检（footer≈973）；保留控件区 4 行
    label_ys = [i["y"] for i in icons_l if i["y"] < 920] or [238, 483, 728, 880]
    if len(label_ys) < 4:
        # 用已检出行距外推
        if len(label_ys) >= 2:
            step = int(np.median(np.diff(label_ys)))
            while len(label_ys) < 4:
                nxt = label_ys[-1] + step
                if nxt >= 920:
                    break
                label_ys.append(int(nxt))
        while len(label_ys) < 4:
            label_ys.append(min(880, 238 + len(label_ys) * 214))
    label_ys = label_ys[:4]
    return {
        "left_icon_x": int(np.median([i["x"] for i in icons_l])) if icons_l else 165,
        "left_label_x": 270,
        "left_ctrl_x": 195,
        "right_icon_x": int(np.median([i["x"] for i in icons_r])) if icons_r else 1515,
        "right_label_x": 1620,
        "right_rail_x": 1655,
        "mute_x": int(np.median([m["x"] for m in mutes])) if mutes else 1544,
        "row_label_ys": label_ys,
        "wide_chip": {"w": 571, "h": 75, "dy": 75},
        "rail": {"w": 288, "h": 13, "dy": 101, "official": "option__pack/s014"},
        "chips": chips,
        "rails": rails,
        "icons_left": icons_l,
        "icons_right": icons_r,
        "mutes": mutes,
        "sidebar": {"x": 58, "y": 161, "w": 80, "h": 731},
        "footer_y": 973,
        "footer_xs": [940, 1187, 1434],
        "tabs": {
            "y": 28,
            "h": 52,
            "x0": 720,
            "x1": 1880,
            "note": "原版顶栏可见基本/画面/游戏1/2/文本/音频；确认/键盘仍保留为后续页签",
        },
        "simple_keys": {
            "left": ["fullscreen", "sqscr", "textspeed", "autospeed"],
            "right": ["wave", "bgm", "se", "voice"],
            "note": "ig_option_0 可见 4+4；skipall/movie 走详细页",
        },
    }


def match_multi(hay, needle, alpha, thr=0.72, maxn=8, nms=40):
    mask = (alpha > 40).astype(np.uint8) * 255
    if int(mask.sum()) < 200:
        return []
    res = cv2.matchTemplate(hay, needle, cv2.TM_CCORR_NORMED, mask=mask)
    h, w = needle.shape[:2]
    hits, work = [], res.copy()
    for _ in range(maxn):
        _mn, maxv, _ml, maxl = cv2.minMaxLoc(work)
        if maxv < thr:
            break
        x, y = int(maxl[0]), int(maxl[1])
        hits.append({"score": round(float(maxv), 4), "x": x, "y": y, "w": w, "h": h})
        work[max(0, y - nms) : y + nms, max(0, x - nms) : x + nms] = 0
    return hits


def slice_file(pack: str, idx: int) -> Path | None:
    d = SLICES / pack
    for p in d.glob(f"s{idx:03d}_*.png"):
        return p
    return None


def all_slices(pack: str):
    out = []
    for p in sorted((SLICES / pack).glob("s*.png")):
        out.append((int(p.name.split("_", 1)[0][1:]), p))
    return out


def refresh_placements(page0: dict) -> dict:
    hay0 = cv2.cvtColor(load_rgba(CAP / "ig_option_0_1080.png")[:, :, :3], cv2.COLOR_RGB2BGR)
    shared = {}
    for key, pack, idx, thr, nms, maxn in [
        ("sidebar_s000", "option__pack", 0, 0.85, 80, 1),
        ("rails_s014", "option__pack", 14, 0.90, 30, 10),
        ("mutes_s010", "option__pack", 10, 0.80, 40, 8),
        ("details_s011", "option__pack", 11, 0.80, 40, 8),
        ("knobs_s018", "option__pack", 18, 0.80, 40, 10),
    ]:
        p = slice_file(pack, idx)
        if not p:
            continue
        nb, al = load_bgr_a(p)
        shared[key] = match_multi(hay0, nb, al, thr=thr, maxn=maxn, nms=nms)

    pack_map = {
        "4": "option_4text__pack",
        "5a": "option_5sound1__pack",
        "5b": "option_5sound2__pack",
        "6": "option_6dialog__pack",
        "8": "option_8keyboard1__pack",
    }
    pages = {}
    for tid, pack in pack_map.items():
        cap_id = tid if (CAP / f"ig_option_{tid}_1080.png").exists() else "0"
        hay = cv2.cvtColor(load_rgba(CAP / f"ig_option_{cap_id}_1080.png")[:, :, :3], cv2.COLOR_RGB2BGR)
        items = []
        for idx, path in all_slices(pack):
            nb, al = load_bgr_a(path)
            w, h = nb.shape[1], nb.shape[0]
            thr = 0.55 if max(w, h) > 200 else 0.70
            hits = match_multi(hay, nb, al, thr=thr, maxn=1, nms=100)
            item = {"i": idx, "pack": pack, "file": path.name, "w": w, "h": h, "cap": cap_id, "ok": bool(hits)}
            if hits:
                item.update(hits[0])
            items.append(item)
        pages[tid] = {"pack": pack, "cap": cap_id, "slices": items}

    grid = {
        "left_icon_x": page0["left_icon_x"],
        "left_label_x": page0["left_label_x"],
        "left_ctrl_x": page0["left_ctrl_x"],
        "right_icon_x": page0["right_icon_x"],
        "right_label_x": page0["right_label_x"],
        "right_rail_x": page0["right_rail_x"],
        "mute_x": page0["mute_x"],
        "row_ys": page0["row_label_ys"],
        "ctrl_dy": page0["wide_chip"]["dy"],
        "rail_dy": page0["rail"]["dy"],
        "wide_chip_w": page0["wide_chip"]["w"],
        "wide_chip_h": page0["wide_chip"]["h"],
    }
    return {
        "source": "ig_option + cv2.matchTemplate + blue-blob page0",
        "exclude_pages": ["7", "9"],
        "keep_tabs": KEEP,
        "shared": shared,
        "grid": grid,
        "pages": pages,
        "page0": page0,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    im = load_rgba(CAP / "ig_option_0_1080.png")
    arrow = export_arrow(im)
    page0 = analyze_page0(im)
    page0["label_arrow"] = arrow
    placements = refresh_placements(page0)
    truth = {
        "source": "E:/GAL/天使☆嚣嚣 live capture ig_option_*_1080",
        "structure": {
            "label": "arrow_pill + dark_blue_text",
            "toggle": "flat wide value bar under label (~571x75)",
            "slider": "thin rail under label; mute left of right-col rails",
            "not": "do NOT bake option__pack s005 as category labels",
        },
        "arrow": arrow,
        "page0": page0,
        "grid": placements["grid"],
    }
    (OUT / "settings_truth.json").write_text(json.dumps(truth, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "slice_placements.json").write_text(
        json.dumps(placements, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("arrow", arrow)
    print("grid", placements["grid"])
    for tid, pg in placements["pages"].items():
        ok = sum(1 for s in pg["slices"] if s.get("ok"))
        print(f"page {tid}: {ok}/{len(pg['slices'])} slices placed")
    print("wrote", OUT / "settings_truth.json")
    print("wrote", OUT / "slice_placements.json")


if __name__ == "__main__":
    main()
