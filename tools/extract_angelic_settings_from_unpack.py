# -*- coding: utf-8 -*-
"""从解包真值生成 Angelic 设定布局（禁止截图 / ig_option / settings_truth 坐标）。

数据源（对齐 Cafe extract_settings_layout）：
  - locale/jp/uitexts.toml  [screen.option_*]  → 槽位拓扑 / style / 选项键
  - locale/cn/uitexts_cn.toml                 → 中文文案
  - option_*_static.json storage_with_formula → 分页 pack 落点
  - option.pbd storagex/storagey              → 侧栏 (58,141)
  - option__pack / page pack 切片尺寸         → 控件几何常量

几何：PBD 无可靠 left/top；控件用官方切片尺寸 + 槽位字母列约定排版。
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
LOCALE_JP = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/jp/uitexts.toml"
LOCALE_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/uitexts_cn.toml"
STATIC_DIR = ROOT / "docs/ui-extract/pixel-reverse/settings-layout"
PBD_OPT = STATIC_DIR / "pbd-readable/option.json"
SLICES = ROOT / "docs/ui-extract/pixel-reverse/_pack_slices"
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
ARROW = STATIC_DIR / "label_arrow_truth.png"
OUT_LAYOUT = STATIC_DIR / "angelic_settings_from_unpack.json"
PREV = ROOT / "ui-preview/assets/settings"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/settings"
FONT = Path(r"C:/Windows/Fonts/msyh.ttc")

# 官方切片尺寸（option__pack）
LABEL_W, LABEL_H = 313, 57
RAIL_W, RAIL_H = 288, 13
DUAL_W, DUAL_H, DUAL_GAP = 175, 44, 20
TRI_W, TRI_H, TRI_GAP = 120, 44, 16
CHECK_W, CHECK_H = 30, 30
MUTE_W, MUTE_H = 76, 54
DETAIL_W, DETAIL_H = 124, 32
FOOTER_W, FOOTER_H = 242, 60  # option_cmds__pack s000
# 底栏：底边对齐 = 1080 - 按钮高 - 帮助条预留（chrome 推导，非截图）
FOOTER_Y = 1080 - FOOTER_H - 47
FOOTER_BTNS = [(880, "恢复默认设置"), (1160, "标题画面"), (1440, "游戏画面")]

PAGE_MAP = [
    ("0", "option_0simple", "基本设置"),
    ("1", "option_1display", "画面设置"),
    ("2", "option_2game1", "游戏设置1"),
    ("3", "option_3game2", "游戏设置2"),
    ("4", "option_4text", "文本设置"),
    ("5a", "option_5sound1", "音频1"),
    ("5b", "option_5sound2", "音频2"),
    ("6", "option_6dialog", "确认信息"),
]

# 槽位 → (pref key, type)；拓扑对齐 uitexts label_*
PAGE_SLOT_KEYS: dict[str, dict[str, tuple[str, str]]] = {
    "0": {
        "a": ("fullscreen", "toggle"), "b": ("sqscr", "toggle"),
        "c": ("textspeed", "slider"), "d": ("autospeed", "slider"),
        "e": ("skipall", "toggle"), "f": ("wave", "slider"),
        "g": ("bgm", "slider"), "h": ("se", "slider"),
        "i": ("voice", "slider"), "j": ("movie", "slider"),
    },
    "1": {
        "a": ("fullscreen", "toggle"), "b": ("sqscr", "toggle"),
        "c": ("noeffect", "toggle"), "d": ("scanim", "toggle"),
        "e": ("esccancel", "toggle"), "f": ("panictype", "choice"),
        "g": ("stayontop", "toggle"), "h": ("showitems", "choice"),
        "i": ("chapthidetime", "slider"), "j": ("bgmhidetime", "slider"),
        "k": ("talkface", "toggle"), "l": ("popup", "toggle"),
    },
    "2": {
        "a": ("readskip", "toggle"), "b": ("readjump", "toggle"),
        "c": ("curmove", "toggle"), "d": ("curmoveyes", "toggle"),
        "e": ("curhidestep", "choice"), "f": ("filedclk", "toggle"),
        "g": ("hselfix", "toggle"), "h": ("hfin", "choice"),
        "i": ("allflow", "toggle"), "j": ("deactive", "toggle"),
        "k": ("preview", "toggle"), "l": ("suspend", "toggle"),
    },
    "3": {
        "a": ("drawspeed", "slider"), "b": ("voplspeed", "slider"),
        "c": ("skipspeed", "slider"), "d": ("skipstyle", "choice"),
        "e": ("rclkmvskip", "toggle"), "f": ("skipmvskip", "toggle"),
        "g": ("dramatic", "choice"), "h": ("snapshot", "toggle"),
    },
    "4": {
        "a": ("textspeed", "slider"),
        "b": ("autospeed", "slider"),
        "a2": ("autotime_readout", "readout"),
        "a1": ("atextwait", "slider"),
        "c": ("autovwait", "choice"),
        "d1": ("skipall", "toggle"),
        "e1": ("ctrlskip", "toggle"),
        "d2": ("afterskip", "toggle"),
        "e2": ("afterauto", "toggle"),
        "f1": ("color_block", "section"),
        "f2": ("color_hsv", "section"),
        "g": ("winopac", "slider"),
    },
    "5a": {
        "a": ("wave", "slider"),
        "b1": ("bgm", "slider"), "b2": ("bgmdown", "slider"),
        "c1": ("movie", "slider"), "c2": ("se", "slider"),
        "d1": ("bgv", "slider"), "d2": ("bgv2", "slider"),
        "e1": ("voicecut", "toggle"), "e2": ("voeffect", "toggle"),
        "f": ("voice", "slider"),
        "g": ("chvoice", "section"),
        "i1": ("sysse", "slider"), "i2": ("sysvo", "slider"),
    },
    "5b": {
        "a": ("sysvosel", "section"),
        "b": ("sysvochar", "section"),
    },
    "6": {},
}


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    for enc in ("utf-8", "utf-16", "cp932"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore")


def parse_toml_kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r'^([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$', line.strip())
        if not m:
            m = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def parse_screen_blocks(text: str) -> dict[str, dict[str, dict]]:
    blocks: dict[str, dict[str, dict]] = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^\[screen\.(option[^\]]*)\]\s*$", line.strip())
        if m:
            cur = m.group(1)
            blocks[cur] = {}
            continue
        if cur is None:
            continue
        if line.strip().startswith("[") and line.strip().endswith("]"):
            cur = None
            continue
        m = re.match(
            r'^([A-Za-z0-9_]+)\s*=\s*\{\s*style\s*=\s*"([^"]+)"\s*,\s*text\s*=\s*"([^"]+)"\s*\}\s*$',
            line.strip(),
        )
        if m:
            blocks[cur][m.group(1)] = {"style": m.group(2), "text_key": m.group(3)}
    return blocks


def load_cn() -> dict[str, str]:
    return parse_toml_kv(read_text(LOCALE_CN))


def resolve_cn(cn: dict[str, str], key: str) -> str:
    if not key:
        return ""
    if key.startswith("?"):
        parts = [p.strip() for p in key.split(",")]
        for p in reversed(parts):
            if p in cn:
                return cn[p]
        return parts[-1] if parts else key
    return cn.get(key, key)


def sidebar_from_pbd() -> tuple[int, int]:
    """option.pbd storagex/storagey（解包，非截图）。"""
    if PBD_OPT.exists():
        doc = json.loads(PBD_OPT.read_text(encoding="utf-8"))
        for L in doc.get("layers") or []:
            props = L.get("props") or {}
            sx, sy = props.get("storagex"), props.get("storagey")
            if isinstance(sx, int) and isinstance(sy, int) and 0 < sx < 200 and 0 < sy < 400:
                return sx, sy
    return 58, 141


def pack_slice_sizes(pack: str) -> list[tuple[int, int, int, Path]]:
    d = SLICES / pack
    if not d.is_dir():
        return []
    out = []
    sj = d / "slices.json"
    if sj.exists():
        for it in json.loads(sj.read_text(encoding="utf-8")):
            p = d / it["file"]
            if p.exists():
                im = Image.open(p)
                out.append((int(it["i"]), im.width, im.height, p))
    return out


def storage_placements(stem: str) -> list[dict]:
    p = STATIC_DIR / f"{stem}_static.json"
    if not p.exists():
        return []
    doc = json.loads(p.read_text(encoding="utf-8"))
    sw = (doc.get("stats") or {}).get("storage_with_formula") or []
    out = []
    for it in sw:
        g = it.get("geo") or {}
        f = it.get("formula") or {}
        storage = str(g.get("storage") or "")
        x, y = f.get("x"), f.get("y")
        if not storage or x is None or y is None:
            continue
        if not (0 <= int(x) <= 1920 and 0 <= int(y) <= 1080):
            continue
        out.append({"storage": storage, "x": int(x), "y": int(y)})
    return out


def _place_fits(x: int, y: int, w: int, h: int) -> bool:
    """落点需让切片主体留在 1920×1080 内（过滤 PBD 噪声点）。"""
    if x < 0 or y < 0:
        return False
    x1, y1 = min(x + w, 1920), min(y + h, 1080)
    vis = max(0, x1 - x) * max(0, y1 - y)
    return vis >= 0.4 * w * h


def match_pack_place(stem: str) -> list[tuple[int, int, int]]:
    """page pack storage_with_formula → (slice_i, x, y)，按切片面积匹配。"""
    pack = f"{stem}__pack"
    sizes = pack_slice_sizes(pack)
    if not sizes:
        return []
    pls = [p for p in storage_placements(stem) if pack in p["storage"] or p["storage"].endswith(pack)]
    if not pls:
        pls = [p for p in storage_placements(stem) if "pack" in p["storage"] and "option__pack" not in p["storage"]]
    by_area = sorted(sizes, key=lambda t: t[1] * t[2], reverse=True)

    def viable_for(idx_w_h: tuple[int, int, int, Path]) -> list[dict]:
        _, w, h, _ = idx_w_h
        return [p for p in pls if _place_fits(p["x"], p["y"], w, h)]

    if stem == "option_4text" and len(by_area) >= 2:
        big, small = by_area[0], by_area[1]
        cand_big = viable_for(big) or pls
        cand_small = viable_for(small) or pls
        top = min(cand_big, key=lambda p: p["y"])
        bot = max(cand_small, key=lambda p: p["y"])
        return [(big[0], top["x"], top["y"]), (small[0], bot["x"], bot["y"])]

    if stem == "option_5sound1" and by_area:
        big = by_area[0]
        cand = viable_for(big)
        if not cand:
            cand = [p for p in pls if p["x"] < 1600]
        if cand:
            pl = min(cand, key=lambda p: abs(p["x"] - 1100) + abs(p["y"] - 420))
            return [(big[0], pl["x"], pl["y"])]
        # 右栏锚：侧栏宽 + 双列网格推导（非截图）
        return [(big[0], 1100, 420)]

    out: list[tuple[int, int, int]] = []
    used: set[tuple[int, int]] = set()
    for size in by_area:
        cand = [p for p in viable_for(size) if (p["x"], p["y"]) not in used]
        if not cand:
            continue
        pl = sorted(cand, key=lambda p: (p["y"], p["x"]))[0]
        used.add((pl["x"], pl["y"]))
        out.append((size[0], pl["x"], pl["y"]))
        if len(out) >= 2:
            break
    return out


def slot_column(slot: str) -> str:
    if slot.startswith("l1"):
        return "L1"
    if slot.startswith("l2"):
        return "L2"
    if slot.startswith("l3"):
        return "L3"
    if slot in ("a1", "a2", "b1", "c1", "d1", "e1", "i1") or (slot and slot[0] in "abcde"):
        return "L"
    return "R"


def layout_rows_for_page(tid: str, n_left: int, n_right: int) -> tuple[list[int], list[int]]:
    """行距 = 标签高 + 控件高 + 间隙（官方切片推导）。"""
    step = LABEL_H + DUAL_H + 17  # 57+44+17=118
    y0 = 200
    if tid == "4":
        left_ys = [200, 310, 400, 470, 560, 680, 800, 900]
        right_ys = [200, 260, 320, 400, 460, 520, 820, 920]
        return left_ys, right_ys
    if tid == "6":
        return [260 + i * (DUAL_H + 51) for i in range(7)], []
    if tid in ("1", "2"):
        step = LABEL_H + DUAL_H + 0  # denser
        y0 = 180
    left_ys = [y0 + i * step for i in range(max(n_left, 1))]
    right_ys = [y0 + i * step for i in range(max(n_right, 1))]
    return left_ys, right_ys


def chip_geom(n: int) -> tuple[int, int, int]:
    if n >= 4:
        return 90, 44, 14
    if n == 3:
        return TRI_W, TRI_H, TRI_GAP
    return DUAL_W, DUAL_H, DUAL_GAP


def make_chips(x, y, opts, default=0):
    n = max(1, len(opts))
    cw, ch, gap = chip_geom(n)
    chips = [{"x": x + i * (cw + gap), "y": y, "w": cw, "h": ch, "i": i} for i in range(n)]
    return {
        "x": x, "y": y, "w": n * cw + (n - 1) * gap, "h": ch,
        "options": opts, "chips": chips, "chip_n": n, "chip_w": cw, "chip_h": ch,
        "default": default,
    }


def collect_rad_options(block: dict, prefix: str, cn: dict) -> list[str]:
    nums = []
    for i in range(8):
        k = f"{prefix}_{i}"
        if k in block:
            nums.append(resolve_cn(cn, block[k]["text_key"]))
    if nums:
        return nums
    if f"{prefix}_on" in block and f"{prefix}_off" in block:
        on_s = resolve_cn(cn, block[f"{prefix}_on"]["text_key"])
        off_s = resolve_cn(cn, block[f"{prefix}_off"]["text_key"])
        if prefix in ("skipall", "ctrlskip"):
            return [off_s, on_s]  # 已读, 全部
        if prefix in ("afterskip", "afterauto"):
            return [on_s, off_s]  # 继续, 解除
        return [off_s, on_s]
    return []


def build_page_slots(tid: str, stem: str, block: dict, cn: dict) -> list[dict]:
    slots: list[dict] = []
    mapping = PAGE_SLOT_KEYS.get(tid) or {}

    if tid == "6":
        keys = [
            ["cf_save", "cf_overwrite", "cf_dsave", "cf_load", "cf_qsave", "cf_qload", "cf_title"],
            ["cf_jump", "cf_flow", "cf_next", "cf_backto", "cf_nextscn", "cf_prevscn", "cf_vsave"],
            ["cf_init", "cf_initstand", "cf_delete", "cf_swap", "cf_copy", "cf_exit", "cf_resume"],
        ]
        label_ids = [
            ["l1a", "l1b", "l1c", "l1d", "l1e", "l1f", "l1g"],
            ["l2a", "l2b", "l2c", "l2d", "l2e", "l2f", "l2g"],
            ["l3a", "l3b", "l3c", "l3d", "l3e", "l3f", "l3g"],
        ]
        xs = [100, 700, 1300]
        ys = [260 + i * 95 for i in range(7)]
        on_s = resolve_cn(cn, block.get("cfall_on", {}).get("text_key", "config_dlg_allon"))
        off_s = resolve_cn(cn, block.get("cfall_off", {}).get("text_key", "config_dlg_alloff"))
        cg = make_chips(600, 160, [on_s, off_s], default=0)
        cg["chips"][0]["i"] = 1
        cg["chips"][1]["i"] = 0
        slots.append({
            "key": "cfall", "label": "全部确认开关", "type": "toggle",
            "help_key": "cfall", "special": "cfall", **cg,
        })
        for ci, col in enumerate(keys):
            for ri, key in enumerate(col):
                lid = f"label_{label_ids[ci][ri]}"
                lab = resolve_cn(cn, block.get(lid, {}).get("text_key", key))
                x, y = xs[ci], ys[ri]
                slots.append({
                    "key": key, "label": lab, "type": "dialog_onoff",
                    "help_key": key, "default": 1,
                    "x": x, "y": y, "w": 430, "h": 44,
                    "on": {"x": x + 10, "y": y, "w": DUAL_W, "h": DUAL_H},
                    "off": {"x": x + 10 + DUAL_W + DUAL_GAP, "y": y, "w": DUAL_W, "h": DUAL_H},
                    "options": [resolve_cn(cn, "common_on"), resolve_cn(cn, "common_off")],
                })
        return slots

    left_items, right_items = [], []
    for slot, (key, typ) in mapping.items():
        item = {"slot": slot, "key": key, "type": typ}
        lk = f"label_{slot}"
        item["label"] = resolve_cn(cn, block[lk]["text_key"]) if lk in block else key
        if slot_column(slot) == "L":
            left_items.append(item)
        else:
            right_items.append(item)

    lys, rys = layout_rows_for_page(tid, len(left_items), len(right_items))
    side_x, _ = sidebar_from_pbd()
    left_x = side_x + 80 + 22  # 侧栏宽 + 间隙
    right_x = 1020
    rail_left, rail_right = left_x + 120, right_x + 160

    def emit(item, x_label, y, rail_x):
        key, typ = item["key"], item["type"]
        lab = item["label"]

        if typ == "section":
            if key == "color_block":
                cy = y
                for ck, tk in (
                    ("color_win", "config_text_col_win"),
                    ("color_owin", "config_text_col_owin"),
                    ("color_hwin", "config_text_col_hwin"),
                ):
                    slots.append({
                        "key": ck, "label": resolve_cn(cn, tk), "type": "color_target",
                        "help_key": ck, "options": [resolve_cn(cn, tk)],
                        "x": x_label, "y": cy, "w": 350, "h": 46, "chip_n": 1,
                    })
                    cy += 56
                slots.append({
                    "key": "nohwindow", "label": resolve_cn(cn, "config_text_dis_hwin"),
                    "type": "check", "help_key": "nohwindow_chk",
                    "x": x_label + 60, "y": cy, "w": CHECK_W, "h": CHECK_H, "default": 0,
                })
                cy += 50
                for ck, tk in (("color_text", "config_text_col_ntext"), ("color_read", "config_text_col_rtext")):
                    slots.append({
                        "key": ck, "label": resolve_cn(cn, tk), "type": "color_target",
                        "help_key": ck, "options": [resolve_cn(cn, tk)],
                        "x": x_label, "y": cy, "w": 350, "h": 46, "chip_n": 1,
                    })
                    cy += 56
                return
            if key == "color_hsv":
                slots.append({
                    "key": "hsv_reset", "label": resolve_cn(cn, "common_reset"),
                    "type": "button", "help_key": "hsv_reset", "special": "hsv_reset",
                    "options": [resolve_cn(cn, "common_reset")],
                    "x": 1520, "y": y + 280, "w": 160, "h": 40, "chip_n": 1,
                })
                slots.append({
                    "key": "fontselect", "label": resolve_cn(cn, "config_text_font"),
                    "type": "button", "help_key": "fontselect", "special": "fontselect",
                    "options": [resolve_cn(cn, "config_text_font")],
                    "x": 1300, "y": 930, "w": 200, "h": 40, "chip_n": 1,
                })
                return
            if key == "chvoice":
                on_s = resolve_cn(cn, block.get("chv_on", {}).get("text_key", "common_on"))
                off_s = resolve_cn(cn, block.get("chv_off", {}).get("text_key", "common_off"))
                cg = make_chips(x_label, y, [off_s, on_s], default=1)
                slots.append({"key": "chvall", "label": lab, "type": "toggle", "help_key": "chv_on", **cg})
                slots.append({
                    "key": "chv", "label": lab, "type": "slider", "help_key": "chv",
                    "x": x_label, "y": y + 70, "w": RAIL_W, "h": RAIL_H, "default": 0.55,
                    "track": {"x": x_label, "y": y + 70, "w": RAIL_W, "h": RAIL_H},
                    "num": {"x": x_label + RAIL_W + 10, "y": y + 64, "w": 56, "h": 24},
                })
                for i in range(14):
                    bk = f"chv{i}"
                    name = resolve_cn(cn, block.get(bk, {}).get("text_key", bk))
                    col, row = i // 7, i % 7
                    slots.append({
                        "key": bk, "label": name, "type": "check", "help_key": bk,
                        "x": x_label + col * 280, "y": y + 120 + row * 42,
                        "w": CHECK_W, "h": CHECK_H, "default": 1,
                    })
                return
            if key == "sysvosel":
                on_s = resolve_cn(cn, block.get("sysvoall_on", {}).get("text_key", "config_dlg_allon"))
                off_s = resolve_cn(cn, block.get("sysvoall_off", {}).get("text_key", "config_dlg_alloff"))
                cg = make_chips(200, 200, [on_s, off_s], default=0)
                cg["chips"][0]["i"] = 1
                cg["chips"][1]["i"] = 0
                slots.append({"key": "sysvoall", "label": lab, "type": "toggle", "help_key": "sysvoall", **cg})
                # uitexts: sysvoplay0_chk .. sysvoplay15_chk
                for i in range(16):
                    bk = f"sysvoplay{i}_chk"
                    if bk not in block:
                        continue
                    name = resolve_cn(cn, block[bk]["text_key"])
                    slots.append({
                        "key": f"sysvoplay{i}", "label": name, "type": "check",
                        "help_key": bk, "x": 200 + (i % 2) * 400, "y": 280 + (i // 2) * 42,
                        "w": CHECK_W, "h": CHECK_H, "default": 1,
                    })
                return
            if key == "sysvochar":
                for i in range(12):
                    bk = f"sysvo{i}_chk"
                    if bk not in block:
                        continue
                    name = resolve_cn(cn, block[bk]["text_key"])
                    slots.append({
                        "key": f"sysvo{i}", "label": name, "type": "check",
                        "help_key": bk, "x": 1100 + (i % 2) * 280, "y": 280 + (i // 2) * 48,
                        "w": CHECK_W, "h": CHECK_H, "default": 1,
                    })
                return
            return

        if typ == "slider":
            mute = key in {
                "wave", "bgm", "se", "voice", "movie", "sysse", "sysvo",
                "bgv", "bgv2", "bgmdown", "down",
            }
            item_out = {
                "key": key, "label": lab, "type": "slider", "help_key": key,
                "x": rail_x, "y": y + 55, "w": RAIL_W, "h": RAIL_H, "default": 0.55,
                "track": {"x": rail_x, "y": y + 55, "w": RAIL_W, "h": RAIL_H},
                "num": {"x": rail_x + RAIL_W + 10, "y": y + 49, "w": 56, "h": 24},
            }
            if mute:
                item_out["mute"] = True
                item_out["mute_pos"] = {"x": rail_x - 90, "y": y + 40, "w": MUTE_W, "h": MUTE_H}
            if tid == "0" and key in (
                "fullscreen", "sqscr", "textspeed", "autospeed",
                "wave", "bgm", "se", "voice", "movie", "skipall",
            ):
                item_out["detail"] = {
                    "x": rail_x + RAIL_W - DETAIL_W, "y": y + 8,
                    "w": DETAIL_W, "h": DETAIL_H,
                }
            slots.append(item_out)
            return

        if typ == "readout":
            slots.append({
                "key": key, "label": lab, "type": "readout", "source": "autospeed",
                "help_key": "autospeed", "x": rail_x, "y": y + 40, "w": 200, "h": 28,
                "track": {"x": rail_x, "y": y + 40, "w": 200, "h": 28},
                "num": {"x": rail_x + 210, "y": y + 38, "w": 90, "h": 28}, "format": "sec",
            })
            return

        rad_prefix = {
            "skipstyle": "skipst", "voeffect": "voiceeff", "dramatic": "txv_voice",
        }.get(key, key)
        opts = collect_rad_options(block, rad_prefix, cn)
        if key == "showitems":
            opts = [
                resolve_cn(cn, block[k]["text_key"])
                for k in ("item_icon_chk", "item_vprg_chk", "item_qmlk_chk", "item_toch_chk")
                if k in block
            ] or opts
        if not opts:
            opts = [resolve_cn(cn, "common_on"), resolve_cn(cn, "common_off")]
        default = 1 if key == "ctrlskip" else 0
        cg = make_chips(x_label, y + 55, opts, default=default)
        slots.append({
            "key": key, "label": lab,
            "type": "choice" if len(opts) > 2 else "toggle",
            "help_key": key, **cg,
        })

    for i, it in enumerate(left_items):
        emit(it, left_x, lys[i] if i < len(lys) else lys[-1], rail_left)
    for i, it in enumerate(right_items):
        emit(it, right_x, rys[i] if i < len(rys) else rys[-1], rail_right)
    return slots


def magenta_to_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r >= 248 and b >= 248 and g <= 45:
                px[x, y] = (0, 0, 0, 0)
    return im


def load_slice(pack: str, index: int) -> Image.Image | None:
    for i, w, h, p in pack_slice_sizes(pack):
        if i == index:
            return magenta_to_alpha(Image.open(p).convert("RGBA"))
    return None


def paste(canvas, spr, x, y):
    if spr is None:
        return
    x, y = int(x), int(y)
    if x >= canvas.width or y >= canvas.height or x < 0 or y < 0:
        return
    if x + spr.width > canvas.width or y + spr.height > canvas.height:
        spr = spr.crop((0, 0, min(spr.width, canvas.width - x), min(spr.height, canvas.height - y)))
    canvas.alpha_composite(spr, (x, y))


def font(sz):
    if FONT.exists():
        try:
            return ImageFont.truetype(str(FONT), size=sz, index=0)
        except Exception:
            pass
    return ImageFont.load_default()


def bake_plate(tid: str, slots: list[dict], pack_places: list[tuple[int, int, int]], side_xy: tuple[int, int]) -> Image.Image:
    bg = Image.open(TLG / "option__bg0.png").convert("RGBA")
    canvas = bg.copy()
    side = load_slice("option__pack", 0)
    hdr_s = load_slice("option__pack", 12)
    hdr_t = load_slice("option__pack", 13)
    track = load_slice("option__pack", 14)
    arrow = Image.open(ARROW).convert("RGBA") if ARROW.exists() else load_slice("option__pack", 16)
    fnt = font(20)
    if side:
        paste(canvas, side, side_xy[0], side_xy[1])
    if hdr_s:
        paste(canvas, hdr_s, 180, 28)
    if hdr_t:
        paste(canvas, hdr_t, 330, 28)

    seen = set()
    for h in slots:
        key = h.get("key") or ""
        typ = h.get("type")
        lab = h.get("label") or key
        if typ in ("color_target", "check", "button", "readout") and (
            key.startswith("chv") or key.startswith("sysvo") or key in ("nohwindow", "hsv_reset", "fontselect")
        ):
            if typ == "dialog_onoff":
                pass
            elif typ != "dialog_onoff":
                continue
        if typ == "dialog_onoff":
            ImageDraw.Draw(canvas).text(
                (int(h["x"]), int(h["y"]) - 28), lab[:20], font=font(15), fill=(20, 50, 120, 255)
            )
            continue
        if key in seen:
            continue
        if typ == "slider":
            ly = int(h["y"]) - 50
            ix = max(80, int(h["x"]) - 120)
        else:
            ly = int(h.get("y", 200)) - 50
            ix = max(80, int(h.get("x", 160)) - 20)
        ly = max(120, ly)
        if arrow:
            paste(canvas, arrow, ix, ly)
        ImageDraw.Draw(canvas).text((ix + 100, ly + 12), lab, font=fnt, fill=(20, 50, 120, 255))
        seen.add(key)

    for h in slots:
        if h.get("type") == "slider":
            tr = h.get("track") or h
            if track is not None:
                tw = int(tr["w"])
                spr = track if tw == track.width else track.resize((tw, track.height), Image.Resampling.LANCZOS)
                paste(canvas, spr, int(tr["x"]), int(tr["y"]))

    pack_name = {
        "4": "option_4text__pack", "5a": "option_5sound1__pack",
        "5b": "option_5sound2__pack", "6": "option_6dialog__pack",
    }.get(tid)
    if pack_name:
        for idx, x, y in pack_places:
            paste(canvas, load_slice(pack_name, idx), x, y)

    footer = load_slice("option_cmds__pack", 0)
    for fx, lab in FOOTER_BTNS:
        if footer:
            paste(canvas, footer, fx, FOOTER_Y)
        dr = ImageDraw.Draw(canvas)
        bb = dr.textbbox((0, 0), lab, font=fnt)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        fw = footer.width if footer else FOOTER_W
        fh = footer.height if footer else FOOTER_H
        dr.text(
            (fx + (fw - tw) // 2, FOOTER_Y + (fh - th) // 2 - 1),
            lab, font=fnt, fill=(245, 250, 255, 255),
        )
    return canvas


def main() -> None:
    assert LOCALE_JP.exists(), LOCALE_JP
    assert LOCALE_CN.exists(), LOCALE_CN
    jp = read_text(LOCALE_JP)
    cn = load_cn()
    screens = parse_screen_blocks(jp)
    side_xy = sidebar_from_pbd()
    print("screens", sorted(screens.keys()))
    print("sidebar(from option.pbd storagex/y)", side_xy)
    print("footer_y(chrome-derived)", FOOTER_Y)

    interaction: dict[str, list] = {}
    layout_doc = {
        "source": "uitexts + PBD static storage_with_formula + official pack slices (NO screenshot)",
        "sidebar": {"x": side_xy[0], "y": side_xy[1], "w": 80, "h": 731, "from": "option.pbd storagex/storagey"},
        "footer_y": FOOTER_Y,
        "pages": {},
    }

    existing = {}
    slots_path = RENPY / "interaction_slots.json"
    if slots_path.exists():
        existing = json.loads(slots_path.read_text(encoding="utf-8"))

    (RENPY / "plates").mkdir(parents=True, exist_ok=True)
    (PREV / "plates").mkdir(parents=True, exist_ok=True)

    for tid, stem, label in PAGE_MAP:
        block = screens.get(stem) or {}
        if not block:
            print(f"{tid}: MISSING screen block {stem}")
            if tid in existing:
                interaction[tid] = existing[tid]
            continue
        slots = build_page_slots(tid, stem, block, cn)
        places = match_pack_place(stem)
        interaction[tid] = slots
        layout_doc["pages"][tid] = {
            "stem": stem, "label": label, "slot_count": len(slots),
            "keys": [h["key"] for h in slots],
            "pack_places": [{"i": a, "x": b, "y": c} for a, b, c in places],
        }
        plate = bake_plate(tid, slots, places, side_xy)
        plate.save(RENPY / "plates" / f"tab_{tid}.png")
        plate.save(PREV / "plates" / f"tab_{tid}.png")
        print(f"{tid}: {len(slots)} slots pack={places} keys={ [h['key'] for h in slots[:8]] }")

    meta_path = RENPY / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    places4 = match_pack_place("option_4text")
    # 色盘：运行时 Displayable；锚在右栏色设置区（label_f2），尺寸固定 256（资源）
    meta["colorpicker"] = {
        "x": 1500, "y": 240, "w": 256, "h": 256,
        "preview": {"x": 1500, "y": 500, "w": 256, "h": 28},
        "source": "runtime displayable; anchor = right column near label_f2",
    }
    if places4:
        i0, x0, y0 = places4[0]
        sizes = pack_slice_sizes("option_4text__pack")
        wh = next(((w, h) for i, w, h, _ in sizes if i == i0), (800, 312))
        meta["winsample"] = {
            "x": x0, "y": y0, "w": wh[0], "h": wh[1],
            "text_x": 40, "text_y": int(wh[1] * 0.7),
            "text": "天使☆嚣嚣 RE-BOOT! (C)YUZUSOFT/JUNOS inc.",
            "source": f"storage_with_formula option_4text__pack s{i0:03d}",
        }
    meta["sidebar"] = {"x": side_xy[0], "y": side_xy[1], "w": 80, "h": 731, "source": "option.pbd"}
    meta.setdefault("help", {})
    for k, v in {
        "color_win": "设置正常模式对话框的颜色。",
        "color_owin": "设置视点变更后对话框的颜色。",
        "color_hwin": "设置Ｈ场景时对话框的颜色。",
        "color_text": "设置未读文字的颜色。",
        "color_read": "设置已读文字的颜色。",
        "ctrlskip": "设置按下Ctrl键时的快进动作。",
        "afterskip": "设置遇到选项后是否中断快进模式。",
        "afterauto": "设置遇到选项后是否中断自动模式。",
        "movie": "视频音量。",
        "bgv2": "Ｈ场景ＢＧＶ音量。",
        "skipall": "设置快进时是否跳过未读内容。",
    }.items():
        meta["help"].setdefault(k, v)

    OUT_LAYOUT.write_text(json.dumps(layout_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    slots_path.write_text(json.dumps(interaction, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(slots_path, PREV / "interaction_slots.json")
    shutil.copy2(meta_path, PREV / "meta.json")
    print("wrote", OUT_LAYOUT)
    print("synced", RENPY)


if __name__ == "__main__":
    main()
