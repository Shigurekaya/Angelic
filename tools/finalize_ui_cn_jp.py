#!/usr/bin/env python3
"""用 HxNames 还原路径，筛出中文/日文界面（排除 en/tw、剧情 scenario、语音）。"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import HXNAMES, STATIC_FORCE, UI_CN_JP

LOG = STATIC_FORCE / "finalize-ui-cn-jp.log"
REPORT = STATIC_FORCE / "finalize-ui-cn-jp-report.json"
FILTERED = UI_CN_JP / "filtered-cn-jp"
RENAMED = UI_CN_JP / "renamed"

# 目录级：保留中日 UI；排除剧情/英繁
KEEP_DIR = re.compile(
    r"(?i)^(uipsd/|locale/jp/|locale/cn/|image/|font/|system/|"
    r"data/ui|ui/|option|title|menu)"
)
DROP_DIR = re.compile(
    r"(?i)(locale/en/|locale/tw/|scenario/|voice/|bgm/|se/|"
    r"fgimage/|evimage/|adult|movie/|video/)"
)
UI_FILE = re.compile(
    r"(?i)("
    r"_cn|_jp|_ja|syslangtext|uitext|help_|option|title|menu|config|dialog|"
    r"backlog|message|button|icon|window|panel|staff|logo|tips|font|"
    r"cursor|gauge|slider|flow_text|locale|lang|uioption|aboutdialog|"
    r"attention|watermark|deactivelogo|multilang|langselect|langfile|"
    r"langrender|menus\.|ui/"
    r")"
)
SKIP_FILE = re.compile(r"(?i)(_en|_tw)(\.|$)")
AUDIO = re.compile(r"(?i)\.(ogg|wav|opus|sli)$")


def log(msg: str) -> None:
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    STATIC_FORCE.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_hx() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in HXNAMES.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        h, name = line.split(":", 1)
        out[h.strip().upper()] = name.strip().replace("\\", "/")
    return out


def resolve_path(p: Path, root: Path, hx: dict[str, str]) -> str | None:
    """hashdir/hashfile -> locale/jp/help_lang.txt style path."""
    rel = p.relative_to(root)
    parts = list(rel.parts)
    if len(parts) < 2:
        return hx.get(p.name.upper())
    dhash, fhash = parts[0].upper(), parts[-1].upper()
    fname = hx.get(fhash)
    dname = hx.get(dhash)
    if fname and dname:
        d = dname.rstrip("/")
        return f"{d}/{fname}"
    if fname:
        return fname
    return None


def keep(resolved: str) -> bool:
    path = resolved.replace("\\", "/")
    name = Path(path).name
    if AUDIO.search(name):
        return False
    if DROP_DIR.search(path):
        return False
    if SKIP_FILE.search(name):
        return False
    # 明确中日 locale
    if re.search(r"(?i)locale/(jp|cn)/", path):
        return True
    if re.search(r"(?i)uipsd/", path) and UI_FILE.search(name):
        return True
    if UI_FILE.search(name) or UI_FILE.search(path):
        return True
    # image 包内 title 底板等
    if re.search(r"(?i)title_", name) or name.startswith("title"):
        return True
    return False


def main() -> None:
    hx = load_hx()
    log(f"hxnames={len(hx)}")
    for d in (FILTERED, RENAMED):
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)

    roots = [p for p in UI_CN_JP.iterdir() if p.is_dir() and p.name not in {"filtered-cn-jp", "renamed"}]
    renamed_n = 0
    kept_n = 0
    unmatched = 0
    inventory = []

    for root in roots:
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() in {".alst", ".json", ".log"}:
                continue
            resolved = resolve_path(p, root, hx)
            if not resolved:
                unmatched += 1
                # image 未命名：按 magic 留 png/tlg 供界面用
                head = p.read_bytes()[:8]
                if root.name == "image" and head.startswith((b"\x89PNG", b"TLG", b"8BPS")):
                    resolved = f"image/_unresolved/{p.name}"
                else:
                    continue
            else:
                renamed_n += 1

            # write full renamed tree
            dest_all = RENAMED / root.name / resolved
            dest_all.parent.mkdir(parents=True, exist_ok=True)
            if not dest_all.exists():
                shutil.copy2(p, dest_all)

            if not keep(resolved):
                continue
            dest = FILTERED / resolved
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.stat().st_size == p.stat().st_size:
                inventory.append({"resolved": resolved, "skip": "dup"})
                continue
            shutil.copy2(p, dest)
            kept_n += 1
            inventory.append({"resolved": resolved, "src_pack": root.name, "bytes": p.stat().st_size})

    # decode text previews（跳过预览目录自身）
    text_dir = FILTERED / "_text_preview"
    if text_dir.exists():
        shutil.rmtree(text_dir, ignore_errors=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    previewed = 0
    for p in FILTERED.rglob("*"):
        if not p.is_file():
            continue
        if "_text_preview" in p.parts:
            continue
        if p.suffix.lower() not in {".txt", ".ini", ".toml", ".tjs", ".ks"}:
            continue
        raw = p.read_bytes()
        text = None
        for enc in ("utf-16-le", "utf-8-sig", "utf-8", "cp932"):
            try:
                if enc == "utf-16-le" and not raw.startswith(b"\xff\xfe"):
                    continue
                text = raw.decode(enc)
                break
            except Exception:
                continue
        if text is None:
            continue
        text = text.lstrip("\ufeff")
        out = text_dir / (p.name + ".utf8.txt")
        out.write_text(text[:8000], encoding="utf-8")
        previewed += 1

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "hx_entries": len(hx),
        "renamed_files": renamed_n,
        "unmatched_skipped": unmatched,
        "filtered_cn_jp": kept_n,
        "text_previews": previewed,
        "filtered_out": str(FILTERED),
        "renamed_out": str(RENAMED),
        "policy": "keep locale/jp + locale/cn + uipsd/title/option UI; drop en/tw/scenario/audio",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (FILTERED / "_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log(f"DONE renamed={renamed_n} kept_cn_jp={kept_n} unmatched={unmatched} previews={previewed}")
    log(f"filtered -> {FILTERED}")


if __name__ == "__main__":
    main()
