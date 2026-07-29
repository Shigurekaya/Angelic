#!/usr/bin/env python3
"""纯静态探针：确认 Angelic XP3 为 Cx 两段 key3 形态，写出 probe-report.json。"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paths import EXTRACT_OUT, GAME, STATIC_FORCE

KEYS = STATIC_FORCE / "keys"


def recover_cx_params(cipher: bytes, plain: bytes) -> dict | None:
    if len(cipher) != len(plain) or len(cipher) < 64:
        return None
    xor = bytes(c ^ p for c, p in zip(cipher, plain))
    win = 128 if len(xor) >= 512 else max(32, len(xor) // 8)
    dom = []
    for i in range(0, len(xor) - win + 1, win):
        dom.append((i, Counter(xor[i : i + win]).most_common(1)[0][0]))
    split_approx = None
    for i in range(1, len(dom)):
        if dom[i][1] != dom[0][1]:
            split_approx = dom[i][0]
            break
    if split_approx is None:
        k3 = Counter(xor).most_common(1)[0][0]
        patches = sum(1 for b in xor if b != k3)
        return {
            "regions": 1,
            "split": len(xor),
            "k3_left": k3,
            "k3_right": k3,
            "npatch": patches,
            "coverage": 1 - patches / len(xor),
        }
    best = None
    for split in range(max(1, split_approx - win), min(len(xor) - 1, split_approx + win) + 1):
        left = Counter(xor[:split]).most_common(1)[0][0]
        right = Counter(xor[split:]).most_common(1)[0][0]
        bad = sum(1 for b in xor[:split] if b != left) + sum(
            1 for b in xor[split:] if b != right
        )
        if best is None or bad < best[0]:
            best = (bad, split, left, right)
    bad, split, left, right = best
    return {
        "regions": 2 if left != right else 1,
        "split": split,
        "k3_left": left,
        "k3_right": right,
        "npatch": bad,
        "coverage": 1 - bad / len(xor),
    }


def main() -> None:
    KEYS.mkdir(parents=True, exist_ok=True)
    from tamago.formats.xp3 import XP3File

    eo = EXTRACT_OUT / "image"
    by_size: dict[int, list[Path]] = defaultdict(list)
    for p in eo.rglob("*"):
        if p.is_file() and p.stat().st_size < 500_000:
            by_size[p.stat().st_size].append(p)

    xp = XP3File(GAME / "image.xp3")
    samples = []
    for f in list(xp.files):
        if not f.encrypted or f.original_size >= 500_000:
            continue
        cands = by_size.get(f.original_size, [])
        if len(cands) != 1:
            continue
        plain = cands[0].read_bytes()
        cipher = xp.open(f.file_name).read()
        if len(plain) != len(cipher):
            continue
        params = recover_cx_params(cipher, plain)
        if not params:
            continue
        samples.append(
            {
                "key": f"0x{f.key:08x}",
                "size": len(cipher),
                "plain_head": plain[:8].hex(),
                "cipher_head": cipher[:8].hex(),
                **params,
            }
        )
        if len(samples) >= 40:
            break
    xp.close()

    # mask/offset fit
    hits = []
    masks = [0x1E6, 0x65, 0x26E, 0x92, 0x15E, 0xEA, 0xFF, 0xFFF, 0xFFFF]
    for mask in masks:
        offs: Counter[int] = Counter()
        for s in samples:
            off = s["split"] - (int(s["key"], 16) & mask)
            if 0 <= off <= 0x100000:
                offs[off] += 1
        if not offs:
            continue
        off, _n = offs.most_common(1)[0]
        exact = sum(1 for s in samples if s["split"] == (int(s["key"], 16) & mask) + off)
        hits.append({"mask": hex(mask), "offset": off, "exact": exact, "total": len(samples)})
    hits.sort(key=lambda h: -h["exact"])

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "archive": "image.xp3",
        "conclusion": {
            "family": "Cx-like two-region single-byte key3 + point patches",
            "hx_crypt_lite": False,
            "control_block_in_exe": False,
            "control_block_memory_sig": False,
            "disk_cb_entropy_match": False,
            "strategy": "known-plaintext oracle keydb (split/k3_left/k3_right/patches) then offline apply",
        },
        "samples": len(samples),
        "mean_coverage": round(sum(s["coverage"] for s in samples) / len(samples), 4) if samples else 0,
        "mean_npatch": round(sum(s["npatch"] for s in samples) / len(samples), 2) if samples else 0,
        "two_region": sum(1 for s in samples if s["regions"] == 2),
        "mask_offset_best": hits[:5],
        "entries": samples[:20],
        "notes": [
            "XOR(cipher, EO_plain) is ~96-99% a single key3 per region with one split.",
            "Standard tamago CxEncryption + entropy CB candidates from dll/exe did not match.",
            "Memory scan for 'Encryption control block' returned 0 hits.",
            "force_static_xp3.py recovers per-file params from EO oracle and re-decrypts XP3 offline.",
        ],
    }
    out = KEYS / "probe-report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "entries"}, ensure_ascii=False, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
