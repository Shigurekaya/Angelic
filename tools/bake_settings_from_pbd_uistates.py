# -*- coding: utf-8 -*-
"""Bake Angelic settings 1:1 from pbd2json uistates (Cafe stamp equivalent).

Uses option.pbd templates: btn2, _jump, _sysbtn, slider_l rail/knob.
Labels/pages: uitexts (no option_locale file in archives).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:/gamedev/Angelic")
UIPSD = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd"
TLG = ROOT / "docs/ui-extract/pixel-reverse/tlg-png"
OUT = ROOT / "ui-preview/assets/settings"
RENPY = ROOT.parent / "renpy-angelic/game/images/angelic/settings"
PBD2JSON = Path(r"D:/gamedev/CafeStella/tools/vendor/hxv4_unhash_tools/binaries/pbd2json.exe")
LOCALE = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/uitexts_cn.toml"
HELP_CN = ROOT / "docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/locale/cn/help_opt_cn.txt"
FONT = Path(r"C:/Windows/Fonts/msyh.ttc")

# Keep-set: no mouse(7) / gamepad(9). 5a/5b split audio; keyboard=8.
PAGE_PBDS = {
    "0": "option_0simple.pbd",
    "1": "option_1display.pbd",
    "2": "option_2game1.pbd",
    "3": "option_3game2.pbd",
    "4": "option_4text.pbd",
    "5a": "option_5sound1.pbd",
    "5b": "option_5sound2.pbd",
    "6": "option_6dialog.pbd",
    "8": "option_8keyboard1.pbd",
}

LABEL_CN = {
    "label_a": "显示模式",
    "label_b": "画面比例",
    "label_c": "文本显示速度",
    "label_d": "自动模式速度",
    "label_e": "快进未读文本",
    "label_f": "总音量",
    "label_g": "ＢＧＭ",
    "label_h": "ＳＥ（游戏音效）",
    "label_i": "语音（游戏中）",
    "label_j": "视频",
    "fullscreen_off": "窗口模式",
    "fullscreen_on": "全屏模式",
    "sqscr_off": "16:9",
    "sqscr_on": "4:3",
    "skipall_off": "关",
    "skipall_on": "开",
    "reset": "恢复默认设置",
    "title": "标题画面",
    "back": "游戏画面",
    "page0": "基本",
    "page1": "画面",
    "page2": "游戏1",
    "page3": "游戏2",
    "page4": "文本",
    "page5": "音频",
    "page6": "确认",
    "page7": "鼠标",
    "page8": "键盘",
    "page9": "手柄",
    "color_win": "普通对话框",
    "color_owin": "选项框",
    "color_hwin": "历史对话框",
    "color_text": "未读文字",
    "color_read": "已读文字",
}

COLOR_KEYS = {"color_win", "color_owin", "color_hwin", "color_text", "color_read"}
PAGE_LABELS = {
    "0": "基本",
    "1": "画面",
    "2": "游戏1",
    "3": "游戏2",
    "4": "文本",
    "5a": "音频1",
    "5b": "音频2",
    "6": "确认",
    "8": "键盘",
}
# tid → original pageN radio id for active-dot highlight
ACTIVE_PAGE = {
    "0": "page0",
    "1": "page1",
    "2": "page2",
    "3": "page3",
    "4": "page4",
    "5a": "page5",
    "5b": "page5",
    "6": "page6",
    "8": "page8",
}
# meta tabs_layout: (tid, pbd page id used for hotspot geometry)
TAB_LAYOUT_MAP = [
    ("0", "0"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5a", "5"),
    ("5b", "5"),
    ("6", "6"),
    ("8", "8"),
]

_ATLAS: dict[str, Image.Image] = {}
_TEMPLATES: dict[str, dict] | None = None


def run_pbd(pbd: Path) -> dict:
    raw = subprocess.check_output([str(PBD2JSON), str(pbd)])
    for enc in ("utf-8-sig", "utf-8", "gbk", "cp932"):
        try:
            return json.loads(raw.decode(enc))
        except Exception:
            continue
    return json.loads(raw.decode("utf-8", errors="ignore"))


def atlas(storage: str) -> Image.Image | None:
    if not storage:
        return None
    if storage in _ATLAS:
        return _ATLAS[storage]
    p = TLG / f"{storage}.png"
    if not p.exists():
        return None
    im = Image.open(p).convert("RGBA")
    _ATLAS[storage] = im
    return im


def crop_state(st: dict) -> Image.Image | None:
    storage = st.get("storage") or ""
    im = atlas(storage)
    if im is None:
        return None
    cx, cy = int(st.get("cx") or 0), int(st.get("cy") or 0)
    w = int(st.get("w") or st.get("cw") or 0)
    h = int(st.get("h") or st.get("ch") or 0)
    if w <= 0 or h <= 0 or cx + w > im.width or cy + h > im.height:
        return None
    return im.crop((cx, cy, cx + w, cy + h))


def load_templates() -> dict[str, dict]:
    global _TEMPLATES
    if _TEMPLATES is not None:
        return _TEMPLATES
    doc = run_pbd(UIPSD / "option.pbd")
    _TEMPLATES = doc.get("result") or {}
    return _TEMPLATES


def tmpl_crop(name: str, state: str = "off") -> Image.Image | None:
    node = load_templates().get(name) or {}
    us = node.get("uistates") or {}
    st = us.get(state) or us.get("(~null~)") or us.get("normal") or us.get("rail")
    if not st and us:
        st = next(iter(us.values()))
    return crop_state(st) if st else None


def layer_list(doc: dict) -> list[dict]:
    result = doc.get("result")
    if not isinstance(result, dict):
        return list(result or [])
    order_names: list[str] = []
    for item in doc.get("order") or []:
        if isinstance(item, dict) and item.get("name"):
            order_names.append(str(item["name"]))
        elif isinstance(item, str):
            order_names.append(item)
    for name in result:
        if name not in order_names:
            order_names.append(name)
    out = []
    for name in order_names:
        node = result.get(name)
        if not isinstance(node, dict):
            continue
        out.append(
            {
                "name": name,
                "x": int(node.get("x") or 0),
                "y": int(node.get("y") or 0),
                "width": int(node.get("width") or node.get("w") or 0),
                "height": int(node.get("height") or node.get("h") or 0),
                "class": node.get("class") or "",
                "uistates": node.get("uistates") or {},
                "groupName": node.get("groupName") or "",
            }
        )
    return out


def pick_state(uistates: dict, prefer_on: bool = False) -> tuple[str, dict] | None:
    if not uistates:
        return None
    order = ("on", "off", "(~null~)", "normal", "rail", "nosave") if prefer_on else (
        "off",
        "on",
        "(~null~)",
        "normal",
        "rail",
        "nosave",
    )
    for k in order:
        if k in uistates and (uistates[k].get("storage") or uistates[k].get("w")):
            return k, uistates[k]
    for k, st in uistates.items():
        if st.get("storage"):
            return k, st
    return None


def paste(canvas: Image.Image, spr: Image.Image | None, x: int, y: int) -> None:
    if spr is None:
        return
    x, y = int(x), int(y)
    if x >= canvas.width or y >= canvas.height:
        return
    canvas.alpha_composite(spr, (max(0, x), max(0, y)))


def font(size: int):
    try:
        return ImageFont.truetype(str(FONT), size)
    except Exception:
        return ImageFont.load_default()


def draw_text_center(canvas, text, x, y, w, h, fill=(255, 255, 255, 255), size=18):
    if not text:
        return
    dr = ImageDraw.Draw(canvas)
    f = font(size)
    bb = dr.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tx = x + max(0, (w - tw) // 2)
    ty = y + max(0, (h - th) // 2) - 1
    dr.text((tx + 1, ty + 1), text, font=f, fill=(10, 30, 60, 90))
    dr.text((tx, ty), text, font=f, fill=fill)


def draw_label(canvas, text, x, y, h=32):
    if not text:
        return
    dr = ImageDraw.Draw(canvas)
    f = font(20)
    bb = dr.textbbox((0, 0), text, font=f)
    th = bb[3] - bb[1]
    ty = y + max(0, (h - th) // 2) - 1
    dr.text((x + 1, ty + 1), text, font=f, fill=(20, 40, 90, 90))
    dr.text((x, ty), text, font=f, fill=(20, 50, 120, 255))


def load_uitexts() -> dict[str, str]:
    out: dict[str, str] = {}
    if not LOCALE.exists():
        return out
    for line in LOCALE.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r'^([A-Za-z0-9_]+)\s*=\s*"(.*)"\s*$', line.strip())
        if not m:
            m = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$", line.strip())
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def parse_help() -> dict[str, str]:
    """Parse help_opt_cn.txt → {key: help text}（文件多为 UTF-16）。"""
    if not HELP_CN.exists():
        return {}
    raw_b = HELP_CN.read_bytes()
    if raw_b.startswith(b"\xff\xfe") or raw_b.startswith(b"\xfe\xff"):
        text = raw_b.decode("utf-16")
    elif raw_b.startswith(b"\xef\xbb\xbf"):
        text = raw_b.decode("utf-8-sig")
    else:
        text = None
        for enc in ("utf-8", "utf-16", "cp932"):
            try:
                text = raw_b.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            text = raw_b.decode("utf-8", errors="ignore")
    out: dict[str, str] = {}
    cur_keys: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        nonlocal cur_keys, buf
        if cur_keys and buf:
            msg = "\n".join(x.strip() for x in buf if x.strip())
            for k in cur_keys:
                out[k] = msg
        cur_keys, buf = [], []

    for line in text.splitlines():
        raw = line.rstrip()
        if not raw or raw.startswith("#"):
            flush()
            continue
        if re.match(r"^[a-zA-Z_][\w\t ]*$", raw) and not raw.startswith("\t"):
            flush()
            cur_keys = [k.strip() for k in re.split(r"[\t ]+", raw) if k.strip()]
            buf = []
        else:
            buf.append(raw.lstrip("\t"))
    flush()
    return out



def export_chrome(chrome: Path) -> None:
    chrome.mkdir(parents=True, exist_ok=True)
    im = atlas("option__pack")
    if im is None:
        raise SystemExit("missing option__pack.png")

    # Official: off=brackets cy0, on=solid cy50 (selected)
    brackets = im.crop((106, 0, 486, 50))
    solid = im.crop((106, 50, 486, 100))
    over = im.crop((106, 100, 486, 150))
    brackets.save(chrome / "chip_off.png")  # unselected
    solid.save(chrome / "chip_on.png")  # selected
    over.save(chrome / "chip_over.png")
    brackets.save(chrome / "chip_off_380.png")
    solid.save(chrome / "chip_on_380.png")

    # smaller btn3/btn4
    for pref, cx, cy_off, w, h in (
        ("chip3", 106, 560, 246, 50),
        ("chip4", 106, 710, 185, 50),
    ):
        off = im.crop((cx, cy_off, cx + w, cy_off + h))
        on = im.crop((cx, cy_off + 50, cx + w, cy_off + 50 + h))
        off.save(chrome / f"{pref}_off.png")
        on.save(chrome / f"{pref}_on.png")
        on.save(chrome / f"{pref}_over.png")

    # jump arrow → also detail_* aliases (runtime / selfcheck)
    for st, name in (("off", "label_arrow.png"), ("over", "label_arrow_over.png"), ("on", "label_arrow_on.png")):
        spr = tmpl_crop("_jump", st)
        if spr:
            spr.save(chrome / name)
    for src, dst in (
        ("label_arrow.png", "detail_off.png"),
        ("label_arrow_over.png", "detail_over.png"),
        ("label_arrow_on.png", "detail_on.png"),
    ):
        p = chrome / src
        if p.exists():
            shutil.copy2(p, chrome / dst)

    # sysbtn / footer chrome → stdbtn aliases
    for st, name in (("off", "sysbtn_off.png"), ("on", "sysbtn_on.png"), ("over", "sysbtn_over.png")):
        spr = tmpl_crop("_sysbtn", st)
        if spr:
            spr.save(chrome / name)
    for src, dst in (
        ("sysbtn_off.png", "stdbtn_off.png"),
        ("sysbtn_over.png", "stdbtn_over.png"),
        ("sysbtn_on.png", "stdbtn_on.png"),
    ):
        p = chrome / src
        if p.exists():
            shutil.copy2(p, chrome / dst)

    # long rail + knob from slider_l template
    node = load_templates().get("slider_l_slider") or {}
    us = node.get("uistates") or {}
    if "rail" in us:
        rail = crop_state(us["rail"])
        if rail:
            rail.save(chrome / "slider_rail.png")
            rail.save(chrome / "slider_rail_l.png")
    if "normal" in us:
        knob = crop_state(us["normal"])
        if knob:
            knob.save(chrome / "slider_knob.png")
            knob.save(chrome / "slider_knob_over.png")

    # mute
    mute_node = load_templates().get("mute_mute") or {}
    mus = mute_node.get("uistates") or {}
    for key, fname in (
        ("on", "mute_on.png"),
        ("over_off", "mute_over.png"),
        ("over_on", "mute_on_over.png"),
        ("normal_on", "mute_off.png"),  # fallback naming
    ):
        if key in mus:
            spr = crop_state(mus[key])
            if spr:
                spr.save(chrome / fname)
    # ensure mute_off
    if "on" in mus:
        # 'on' = muted icon; need unmuted — try normal_on / over_off
        pass
    if not (chrome / "mute_off.png").exists() and "over_off" in mus:
        crop_state(mus["over_off"]).save(chrome / "mute_off.png")

    # caption
    cap = tmpl_crop("caption", "(~null~)")
    if cap:
        cap.save(chrome / "caption_system_setting.png")

    # pgdot
    for st, name in (("dot_on", "tab_dot_on.png"), ("dot_ov", "tab_dot_over.png")):
        spr = tmpl_crop("pgdot", st)
        if spr:
            spr.save(chrome / name)

    print("chrome exported →", chrome)


def build_slots(layers: list[dict], tid: str) -> list[dict]:
    by = {L["name"]: L for L in layers}
    slots: list[dict] = []
    seen = set()

    # color targets
    for key in COLOR_KEYS:
        L = by.get(key)
        if not L:
            continue
        slots.append(
            {
                "key": key,
                "label": LABEL_CN.get(key, key),
                "type": "color_target",
                "options": [LABEL_CN.get(key, key)],
                "help_key": key,
                "x": L["x"],
                "y": L["y"],
                "w": L["width"],
                "h": L["height"],
            }
        )
        seen.add(key)

    # Sliders FIRST — volume rows have empty *_off/*_on stubs that must not steal keys.
    for name, L in by.items():
        if not name.endswith("_slider"):
            continue
        key = name[: -len("_slider")]
        if key in seen:
            continue
        if int(L.get("width") or 0) <= 0 or int(L.get("height") or 0) <= 0:
            continue
        mute = by.get(f"{key}_mute")
        us = L.get("uistates") or {}
        rail = us.get("rail")
        track = {
            "x": L["x"],
            "y": L["y"] + max(0, (L["height"] - 13) // 2),
            "w": L["width"],
            "h": 13,
        }
        if rail:
            track["w"] = int(rail.get("w") or L["width"])
        item = {
            "key": key,
            "label": LABEL_CN.get(
                {
                    "textspeed": "label_c",
                    "autospeed": "label_d",
                    "wave": "label_f",
                    "bgm": "label_g",
                    "se": "label_h",
                    "voice": "label_i",
                    "movie": "label_j",
                }.get(key, ""),
                key,
            ),
            "type": "slider",
            "help_key": key,
            "x": L["x"],
            "y": L["y"],
            "w": L["width"],
            "h": L["height"],
            "default": 0.55,
            "track": track,
        }
        if mute and int(mute.get("width") or 0) > 0 and int(mute.get("height") or 0) > 0:
            item["mute"] = True
            item["mute_pos"] = {
                "x": mute["x"],
                "y": mute["y"],
                "w": mute["width"],
                "h": mute["height"],
            }
        jump_alias = {
            "textspeed": "label_c_jump",
            "autospeed": "label_d_jump",
            "wave": "label_f_jump",
            "bgm": "label_g_jump",
            "se": "label_h_jump",
            "voice": "label_i_jump",
            "movie": "label_j_jump",
        }
        jn = jump_alias.get(key)
        if jn and jn in by:
            j = by[jn]
            item["detail"] = {"x": j["x"], "y": j["y"], "w": j["width"], "h": j["height"]}
        slots.append(item)
        seen.add(key)

    # paired off/on buttons (require real geometry + uistates)
    for name, L in list(by.items()):
        if not name.endswith("_off"):
            continue
        key = name[: -len("_off")]
        if key in seen or key in COLOR_KEYS:
            continue
        on = by.get(key + "_on")
        if not on:
            continue
        if int(L.get("width") or 0) <= 0 or int(L.get("height") or 0) <= 0:
            continue
        if int(on.get("width") or 0) <= 0 or int(on.get("height") or 0) <= 0:
            continue
        # Empty *_off/*_on stubs (volume rows) have w/h 0 and are skipped above.
        # Dialog cf_* copies may have empty uistates but valid boxes — keep them.
        opts = [LABEL_CN.get(name, "关"), LABEL_CN.get(key + "_on", "开")]
        item = {
            "key": key,
            "label": LABEL_CN.get(f"label_{key}", key),
            "type": "toggle",
            "help_key": key,
            "x": L["x"],
            "y": L["y"],
            "w": on["x"] + on["width"] - L["x"],
            "h": L["height"],
            "default": 0,
            "options": opts,
            "chips": [
                {"x": L["x"], "y": L["y"], "w": L["width"], "h": L["height"], "i": 0},
                {"x": on["x"], "y": on["y"], "w": on["width"], "h": on["height"], "i": 1},
            ],
            "chip_n": 2,
            "chip_w": L["width"],
            "chip_h": L["height"],
        }
        jump_alias = {
            "fullscreen": "label_a_jump",
            "sqscr": "label_b_jump",
            "textspeed": "label_c_jump",
            "autospeed": "label_d_jump",
            "skipall": "label_e_jump",
            "wave": "label_f_jump",
            "bgm": "label_g_jump",
            "se": "label_h_jump",
            "voice": "label_i_jump",
            "movie": "label_j_jump",
        }
        jn = jump_alias.get(key)
        if jn and jn in by:
            j = by[jn]
            item["detail"] = {"x": j["x"], "y": j["y"], "w": j["width"], "h": j["height"]}
        slots.append(item)
        seen.add(key)

    # (sliders already collected above)
    # keyboard / keybind areas (option_8keyboard1): transparent hit boxes
    for name, L in by.items():
        if not name.startswith("key_"):
            continue
        if name in seen:
            continue
        if L["width"] <= 0 or L["height"] <= 0:
            continue
        slots.append(
            {
                "key": name,
                "label": name.replace("key_", ""),
                "type": "button",
                "help_key": name,
                "x": L["x"],
                "y": L["y"],
                "w": L["width"],
                "h": L["height"],
                "default": 0,
                "options": [name.replace("key_", "")],
                "chip_n": 1,
            }
        )
        seen.add(name)

    # checkboxes / character-voice toggles (audio2 etc.)
    for name, L in by.items():
        if name in seen:
            continue
        if int(L.get("width") or 0) <= 0 or int(L.get("height") or 0) <= 0:
            continue
        cls = str(L.get("class") or "")
        is_chk = name.endswith("_chk") or name.endswith("_check")
        if not (is_chk or (cls == "toggle" and name.endswith("_mute") is False and f"{name}_slider" not in by and f"{name}_off" not in by)):
            if not is_chk:
                continue
        if name.endswith("_mute"):
            continue
        key = name[:-4] if name.endswith("_chk") else name
        if key in seen or name in seen:
            continue
        slots.append(
            {
                "key": key if is_chk else name,
                "label": key if is_chk else name,
                "type": "check",
                "help_key": key if is_chk else name,
                "x": L["x"],
                "y": L["y"],
                "w": L["width"],
                "h": L["height"],
                "default": 0,
            }
        )
        seen.add(key if is_chk else name)

    return slots


def bake_page(tid: str, pbd_name: str, uitexts: dict[str, str]) -> tuple[Image.Image, list[dict], dict]:
    doc = run_pbd(UIPSD / pbd_name)
    layers = layer_list(doc)
    by = {L["name"]: L for L in layers}

    canvas = Image.open(TLG / "option__bg0.png").convert("RGBA")

    # which page radio is active for this plate
    active_page = ACTIVE_PAGE.get(tid, "page0")

    # default selected chip layer names (index 0 → *_off gets solid / uistate on)
    selected = {"fullscreen_off", "sqscr_off", "skipall_off"}

    jump_spr_off = tmpl_crop("_jump", "off")
    sysbtn_off = tmpl_crop("_sysbtn", "off")
    pgdot_on = tmpl_crop("pgdot", "dot_on")

    for L in layers:
        name = L["name"]
        if name == "base":
            continue
        x, y, w, h = L["x"], L["y"], L["width"], L["height"]
        us = L["uistates"]
        cls = L["class"]

        # labels (engine text)
        if name.startswith("label_") and not name.endswith("_jump"):
            text = LABEL_CN.get(name) or ""
            draw_label(canvas, text, x, y, h or 32)
            continue

        # jumps — use template if layer has no storage
        if name.endswith("_jump") or name == "_jump":
            picked = pick_state(us, prefer_on=False)
            spr = crop_state(picked[1]) if picked else jump_spr_off
            if spr is None:
                spr = jump_spr_off
            if spr:
                ox = oy = 0
                if picked:
                    ox = int(picked[1].get("ox") or 0)
                    oy = int(picked[1].get("oy") or 0)
                paste(canvas, spr, x + ox, y + oy)
            continue

        # page radios — only keep-set pages (no mouse/gamepad)
        if name.startswith("page") and name[4:].isdigit():
            pid = int(name[4:])
            if pid in (7, 9):
                continue
            text = LABEL_CN.get(name, name)
            # 5a/5b share page5 label on plate; meta tabs_layout handles split hotspots
            draw_text_center(canvas, text, x, y + 22, w or 128, 36, fill=(255, 255, 255, 230), size=15)
            if name == active_page and pgdot_on is not None:
                paste(canvas, pgdot_on, x + max(0, (w - pgdot_on.width) // 2), y + 58)
            continue

        # footer copies
        if name in ("reset", "title"):
            draw_text_center(canvas, LABEL_CN.get(name, name), x, y, w or 315, h or 58, fill=(245, 250, 255, 255), size=18)
            continue
        if name in ("back", "_sysbtn"):
            spr = None
            picked = pick_state(us, prefer_on=False)
            if picked:
                spr = crop_state(picked[1])
            if spr is None:
                spr = sysbtn_off
            if spr:
                paste(canvas, spr, x, y)
            # CN on top of sysbtn
            draw_text_center(canvas, LABEL_CN.get("back", "游戏画面"), x, y, w or 315, h or 58, fill=(255, 255, 255, 255), size=18)
            continue

        # skip pure areas without art
        if cls in ("area",) and not us:
            continue

        # mute / check marks: runtime only
        if name.endswith("_mute") or name.endswith("_chk") or name.endswith("_check"):
            continue

        # Interactive chips / toggles: do NOT bake default on/off art.
        # Plate keeps labels/rails/arrows; runtime draws chip state so clicks never fight baked pixels.
        if name.endswith("_off") or name.endswith("_on"):
            continue

        picked = pick_state(us, prefer_on=False)
        if not picked:
            if name.endswith("_slider") and ("rail" in us or "normal" in us):
                rail = crop_state(us["rail"]) if "rail" in us else None
                knob = crop_state(us.get("normal") or {}) if us.get("normal") else None
                if rail is not None:
                    ry = y + max(0, (h - rail.height) // 2)
                    paste(canvas, rail, x, ry)
                if knob is not None:
                    kx = x + int(max(0, (w - knob.width) * 0.55))
                    ky = y + max(0, (h - knob.height) // 2)
                    paste(canvas, knob, kx, ky)
            continue

        st = picked[1]
        spr = crop_state(st)
        if spr is None:
            continue
        ox, oy = int(st.get("ox") or 0), int(st.get("oy") or 0)
        paste(canvas, spr, x + ox, y + oy)
    # Keyboard page: stamp official pack atlas (geometry from PBD labels/areas)
    if tid == "8":
        pack = atlas("option_8keyboard1__pack")
        if pack is not None:
            # pack is decoration sheet — place at origin of content area if smaller than canvas
            # Prefer paste at (0,0) only when full-bleed; else leave labels and rely on bg
            if pack.width >= 400:
                # Center-ish placement used by prior rebuilds: left panel around x=80 y=120
                paste(canvas, pack, 80, 120)

    slots = build_slots(layers, tid)

    # meta extras
    extra: dict = {}
    tabs = []
    for i in range(10):
        pn = f"page{i}"
        if pn in by:
            h = by[pn]
            tabs.append(
                {
                    "id": str(i),
                    "label": LABEL_CN.get(pn, pn),
                    "x": h["x"],
                    "y": h["y"],
                    "w": h["width"],
                    "h": h["height"],
                    "label_y": h["y"] + 28,
                }
            )
    extra["tabs_layout"] = {"items": tabs}
    footer = []
    for fid, nm in (("init", "reset"), ("title", "title"), ("back", "back")):
        if nm in by:
            h = by[nm]
            footer.append({"id": fid, "label": LABEL_CN.get(nm, nm), "x": h["x"], "y": h["y"], "w": h["width"], "h": h["height"]})
    extra["footer"] = footer
    if "hsv" in by:
        h = by["hsv"]
        extra["colorpicker"] = {"x": h["x"], "y": h["y"], "w": h["width"], "h": h["height"]}
    if "winsample" in by:
        h = by["winsample"]
        extra["winsample"] = {
            "x": h["x"],
            "y": h["y"],
            "w": h["width"],
            "h": h["height"],
            "text": "天使☆嚣嚣 RE-BOOT!",
        }
    return canvas, slots, extra


def main() -> int:
    load_templates()
    uitexts = load_uitexts()
    OUT.mkdir(parents=True, exist_ok=True)
    plates = OUT / "plates"
    chrome = OUT / "chrome"
    tabs_dir = OUT / "tabs"
    plates.mkdir(exist_ok=True)
    tabs_dir.mkdir(exist_ok=True)

    export_chrome(chrome)

    interaction: dict[str, list] = {}
    meta_tabs = []
    meta_footer = None
    meta_tabs_layout = None
    colorpicker = None
    winsample = None

    for tid, pbd in PAGE_PBDS.items():
        print("bake", tid, pbd, flush=True)
        canvas, slots, extra = bake_page(tid, pbd, uitexts)
        for s in slots:
            if s.get("detail") is None:
                s.pop("detail", None)
        fname = f"tab_{tid}.png"
        canvas.save(plates / fname)
        canvas.save(OUT / fname)
        interaction[tid] = slots
        meta_tabs.append({"id": tid, "label": PAGE_LABELS.get(tid, tid), "plate": f"plates/{fname}"})
        if tid == "0":
            meta_footer = extra.get("footer")
            meta_tabs_layout = extra.get("tabs_layout")
        if tid == "4":
            colorpicker = extra.get("colorpicker")
            winsample = extra.get("winsample")
        print(f"  slots={len(slots)}", flush=True)

    shutil.copy2(TLG / "option__bg0.png", OUT / "bg.png")
    shutil.copy2(TLG / "option__bg0.png", OUT / "chassis.png")

    # Remove stale mouse/gamepad plates from previous bakes
    for stale in ("tab_5.png", "tab_7.png", "tab_9.png"):
        for base in (plates, OUT, RENPY / "plates", RENPY):
            p = base / stale if base.name != "plates" or stale.startswith("tab_") else base / stale
            # plates dir and OUT root both may hold tab_*.png
            for cand in (plates / stale, OUT / stale, RENPY / "plates" / stale, RENPY / stale):
                if cand.exists():
                    cand.unlink()

    # tabs_layout for keep-set (5a/5b share page5 geometry; 5b shifted half-width)
    items = []
    raw_by = {it["id"]: it for it in ((meta_tabs_layout or {}).get("items") or [])}
    for i, (tid, pid) in enumerate(TAB_LAYOUT_MAP):
        src = raw_by.get(pid) or {}
        w = int(src.get("w", 128))
        x = int(src.get("x", 465 + i * 128))
        if tid == "5b":
            x = x + max(8, w // 2)
        it = {
            "id": tid,
            "label": PAGE_LABELS.get(tid, tid),
            "x": x,
            "y": int(src.get("y", 0)),
            "w": w if tid not in ("5a", "5b") else max(64, w // 2),
            "h": int(src.get("h", 81)),
            "label_y": int(src.get("label_y", 28)),
            "label_file": f"angelic/settings/tabs/label_{tid}.png",
        }
        items.append(it)
        lab = Image.new("RGBA", (max(8, it["w"]), 28), (0, 0, 0, 0))
        draw_text_center(
            lab,
            PAGE_LABELS.get(tid, tid)[:4],
            0,
            0,
            lab.width,
            lab.height,
            fill=(255, 255, 255, 230),
            size=14,
        )
        lab.save(tabs_dir / f"label_{tid}.png")

    help_map = parse_help()
    meta = {
        "family": "settings",
        "source": "pbd2json uistates cx/cy + option.pbd templates",
        "note": "option_locale not in archives; labels from uitexts_cn.toml; help from help_opt_cn.txt",
        "tabs": meta_tabs,
        "tabs_layout": {"items": items},
        "footer": meta_footer
        or [
            {"id": "init", "label": "恢复默认设置", "x": 923, "y": 989, "w": 315, "h": 58},
            {"id": "title", "label": "标题画面", "x": 1252, "y": 989, "w": 315, "h": 58},
            {"id": "back", "label": "游戏画面", "x": 1581, "y": 989, "w": 315, "h": 58},
        ],
        "back": {"x": 1581, "y": 989, "w": 315, "h": 58, "label": "返回"},
        "help_box": {"x": 27, "y": 979, "w": 731, "h": 77},
        "help": help_map,
        "colorpicker": colorpicker or {"x": 1492, "y": 187, "w": 306, "h": 322},
        "winsample": winsample
        or {"x": 1030, "y": 685, "w": 800, "h": 156, "text": "天使☆嚣嚣 RE-BOOT!"},
    }
    (OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "interaction_slots.json").write_text(
        json.dumps(interaction, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for dest in (RENPY, RENPY.parent / "assets" / "settings"):
        dest.mkdir(parents=True, exist_ok=True)
        for src in OUT.rglob("*"):
            if src.is_file():
                dst = dest / src.relative_to(OUT)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    qa = ROOT / "tools" / "_qa_tab0_official.png"
    shutil.copy2(plates / "tab_0.png", qa)
    print("QA", qa)
    print("slots", {k: len(v) for k, v in interaction.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
