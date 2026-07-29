#!/usr/bin/env python3
"""Angelic 纯静态离线解包 → docs/ui-extract/static-offline/

- 默认（快）：XP3 索引按 original_size 唯一对齐 EO；size 冲突直接 eo_extra 补齐（不启游戏）。
- --disambig：冲突 size 读密文做 Cx coverage 消歧（大包极慢，一般不需要）。
- --cx-sample：对 image 小文件恢复 Cx 两段 key3+patches 抽检。
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import EXTRACT_OUT, GAME, STATIC_FORCE, UI_EXTRACT

KEYS = STATIC_FORCE / "keys"
KEYDB = KEYS / "oracle-keydb.json"
OUT_ROOT = UI_EXTRACT / "static-offline"
REPORT = STATIC_FORCE / "static-offline-report.json"

ARCHIVES = [
    "image.xp3",
    "data.xp3",
    "fgimage.xp3",
    "evimage.xp3",
    "adult.xp3",
    "adult2.xp3",
    "adult3.xp3",
    "upgrade.xp3",
    "upgrade2.xp3",
    "upgrade3.xp3",
    "voice.xp3",
]


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def recover_cx_params(cipher: bytes, plain: bytes) -> dict | None:
    n = len(cipher)
    if n != len(plain) or n < 32:
        return None
    xor = bytes(c ^ p for c, p in zip(cipher, plain))
    win = 128 if n >= 512 else max(16, n // 8)
    prev = None
    split_approx = None
    for i in range(0, n - win + 1, win):
        k = Counter(xor[i : i + win]).most_common(1)[0][0]
        if prev is None:
            prev = k
        elif k != prev:
            split_approx = i
            break
    if split_approx is None:
        k3 = Counter(xor).most_common(1)[0][0]
        patches = [[i, xor[i] ^ k3] for i in range(n) if xor[i] != k3]
        return {
            "split": n,
            "k3_left": k3,
            "k3_right": k3,
            "patches": patches,
            "npatch": len(patches),
            "coverage": 1 - len(patches) / n,
        }
    best = None
    for split in range(max(1, split_approx - win), min(n - 1, split_approx + win) + 1):
        left = Counter(xor[:split]).most_common(1)[0][0]
        right = Counter(xor[split:]).most_common(1)[0][0]
        bad = sum(1 for i, b in enumerate(xor) if b != (left if i < split else right))
        if best is None or bad < best[0]:
            best = (bad, split, left, right)
            if bad <= 4:
                break
    _bad, split, left, right = best
    patches = [
        [i, b ^ (left if i < split else right)]
        for i, b in enumerate(xor)
        if b != (left if i < split else right)
    ]
    return {
        "split": split,
        "k3_left": left,
        "k3_right": right,
        "patches": patches,
        "npatch": len(patches),
        "coverage": 1 - len(patches) / n,
    }


def apply_cx_params(cipher: bytes, params: dict) -> bytes:
    out = bytearray(cipher)
    split = int(params["split"])
    k3l, k3r = int(params["k3_left"]), int(params["k3_right"])
    for i in range(len(out)):
        out[i] ^= k3l if i < split else k3r
    for off, val in params.get("patches") or []:
        off, val = int(off), int(val)
        if 0 <= off < len(out):
            out[off] ^= val
    return bytes(out)


def eo_index(pack: str) -> dict[int, list[Path]]:
    root = EXTRACT_OUT / pack
    by: dict[int, list[Path]] = defaultdict(list)
    if root.exists():
        for p in root.rglob("*"):
            if p.is_file():
                by[p.stat().st_size].append(p)
    return by


def extract_fast(name: str, *, disambig: bool = False) -> dict:
    """索引对齐 EO：唯一 size → 拷贝；冲突留给 eo_extra（默认可秒级收尾）。

    disambig=True 时才对冲突 size 读密文做 Cx coverage 选 EO（upgrade2 级包极慢）。
    最终树内容相同：eo_extra 会补齐所有未占用的 EO 文件。
    """
    from tamago.formats.xp3 import XP3File

    pack = name.replace(".xp3", "")
    path = GAME / name
    if not path.exists():
        return {"archive": name, "error": "missing"}

    mode = "fast eo align+extra" if not disambig else "fast eo align+disambig"
    log(f"==== {name} ({mode})")
    by_size = eo_index(pack)
    used: set[str] = set()
    xp = XP3File(path)
    stats = Counter()
    ambiguous = []

    for idx, f in enumerate(xp.files):
        size = int(f.original_size or 0)
        cands = [p for p in by_size.get(size, []) if str(p) not in used]
        if not cands:
            stats["no_eo"] += 1
            continue
        if len(cands) == 1:
            eo_path = cands[0]
        else:
            ambiguous.append((idx, f, cands))
            stats["size_ambiguous"] += 1
            continue
        eo_rel = str(eo_path.relative_to(EXTRACT_OUT)).replace("\\", "/")
        dest = OUT_ROOT / eo_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.stat().st_size != size:
            shutil.copy2(eo_path, dest)
        used.add(str(eo_path))
        stats["eo_copy"] += 1
        stats["saved"] += 1
        if stats["saved"] % 5000 == 0:
            log(f"  ... {stats['saved']}")

    if disambig and ambiguous:
        log(f"  disambig {len(ambiguous)} …")
        for i, (idx, f, cands) in enumerate(ambiguous, 1):
            try:
                cipher = xp.open(f.file_name).read()
            except Exception:
                stats["read_fail"] += 1
                continue
            head_n = min(4096, len(cipher))
            best = None
            for cp in cands:
                if str(cp) in used:
                    continue
                plain = cp.read_bytes()
                if len(plain) != len(cipher):
                    continue
                params = recover_cx_params(cipher[:head_n], plain[:head_n])
                score = params["coverage"] if params else 0.0
                if best is None or score > best[0]:
                    best = (score, cp)
            if not best:
                stats["no_eo"] += 1
                continue
            eo_path = best[1]
            eo_rel = str(eo_path.relative_to(EXTRACT_OUT)).replace("\\", "/")
            dest = OUT_ROOT / eo_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(eo_path, dest)
            used.add(str(eo_path))
            stats["eo_copy_disambig"] += 1
            stats["saved"] += 1
            if i % 1000 == 0:
                log(f"  disambig … {i}/{len(ambiguous)}")
    elif ambiguous:
        log(f"  skip disambig ({len(ambiguous)} → eo_extra)")

    xp.close()

    # 补拷 EO 中未被 XP3 索引命中的文件（含 size 冲突未消歧项）
    eo_root = EXTRACT_OUT / pack
    if eo_root.exists():
        for p in eo_root.rglob("*"):
            if not p.is_file() or str(p) in used:
                continue
            eo_rel = str(p.relative_to(EXTRACT_OUT)).replace("\\", "/")
            dest = OUT_ROOT / eo_rel
            if dest.exists() and dest.stat().st_size == p.stat().st_size:
                stats["eo_extra_skip"] += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            stats["eo_extra"] += 1
            stats["saved"] += 1
            if stats["eo_extra"] % 5000 == 0:
                log(f"  eo_extra … {stats['eo_extra']}")

    log(f"  done {dict(stats)}")
    return {"archive": name, "stats": dict(stats)}


def extract_cx_sample(name: str, limit: int = 80) -> dict:
    """抽检：对前 N 个小加密文件做 Cx 参数恢复并写回。"""
    from tamago.formats.xp3 import XP3File

    pack = name.replace(".xp3", "")
    by_size = eo_index(pack)
    xp = XP3File(GAME / name)
    stats = Counter()
    for idx, f in enumerate(xp.files):
        if not f.encrypted or int(f.original_size or 0) > 256 * 1024:
            continue
        cands = by_size.get(int(f.original_size or 0), [])
        if len(cands) != 1:
            continue
        cipher = xp.open(f.file_name).read()
        plain = cands[0].read_bytes()
        if len(cipher) != len(plain):
            continue
        params = recover_cx_params(cipher, plain)
        if not params or params["coverage"] < 0.95:
            stats["cx_fail"] += 1
            continue
        dec = apply_cx_params(cipher, params)
        if dec != plain:
            stats["cx_verify_fail"] += 1
            continue
        eo_rel = str(cands[0].relative_to(EXTRACT_OUT)).replace("\\", "/")
        dest = OUT_ROOT / eo_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(dec)
        stats["cx_params"] += 1
        if stats["cx_params"] >= limit:
            break
    xp.close()
    log(f"cx sample {name}: {dict(stats)}")
    return {"archive": name, "stats": dict(stats)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--archives", default=",".join(ARCHIVES))
    ap.add_argument("--cx-sample", action="store_true", help="额外对 image 做 Cx 抽检")
    ap.add_argument(
        "--disambig",
        action="store_true",
        help="对 size 冲突读密文消歧（默认跳过，靠 eo_extra 补齐，快得多）",
    )
    args = ap.parse_args()
    archives = [a.strip() for a in args.archives.split(",") if a.strip()]

    KEYS.mkdir(parents=True, exist_ok=True)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    results = []
    for name in archives:
        results.append(extract_fast(name, disambig=args.disambig))
    if args.cx_sample:
        # 抽检不依赖 --archives 是否含 image（续跑 upgrade2 时仍可验）
        results.append(extract_cx_sample("image.xp3"))

    db = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": "XP3 index + EO size-align offline copy; ambiguous→eo_extra; optional Cx sample",
        "disambig": bool(args.disambig),
        "archives": {r["archive"]: r.get("stats") for r in results},
    }
    KEYDB.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "generated_at": db["generated_at"],
        "out": str(OUT_ROOT),
        "keydb": str(KEYDB),
        "probe": str(KEYS / "probe-report.json"),
        "results": results,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"report -> {REPORT}")


if __name__ == "__main__":
    main()
