"""One-shot: compare Extractor_Output vs full-static; classify magic types."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from paths import EXTRACT_OUT, UI_EXTRACT

FULL = UI_EXTRACT / "full-static"
FORCE_MIRROR = UI_EXTRACT / "static-force" / "Extractor_Output"


def kind(b: bytes) -> str:
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if b[:4] in (b"TLG0", b"TLG5", b"TLG6"):
        return "TLG"
    if b[:4] == b"OggS":
        return "OGG"
    if b[:4] == b"RIFF":
        return "WAV/RIFF"
    if b[:2] in (b"\xff\xfe", b"\xfe\xff") or b[:3] == b"\xef\xbb\xbf":
        return "TEXT"
    if b[:4] == b"PSB\x00" or b[:3] == b"PSB":
        return "PSB"
    if len(b) >= 2 and b[0] == 0xFF and b[1] == 0xD8:
        return "JPEG"
    return "OTHER"


def count_files(root: Path) -> dict[str, int]:
    out: dict[str, int] = {}
    if not root.exists():
        return out
    for p in root.iterdir():
        if p.is_dir():
            out[p.name] = sum(1 for f in p.rglob("*") if f.is_file())
    return out


def classify_pack(pack_dir: Path) -> tuple[int, int, Counter[str], Counter[str]]:
    c: Counter[str] = Counter()
    other: Counter[str] = Counter()
    n = empty = 0
    for f in pack_dir.rglob("*"):
        if not f.is_file():
            continue
        n += 1
        if f.stat().st_size == 0:
            empty += 1
            c["EMPTY"] += 1
            continue
        with open(f, "rb") as fh:
            b = fh.read(16)
        if len(b) < 4:
            c["TINY"] += 1
            continue
        k = kind(b)
        c[k] += 1
        if k == "OTHER":
            other["%02X%02X%02X%02X" % tuple(b[:4])] += 1
    return n, empty, c, other


def main() -> None:
    print("EXTRACT_OUT", EXTRACT_OUT, EXTRACT_OUT.exists())
    print("FULL", FULL, FULL.exists())
    print("FORCE_MIRROR", FORCE_MIRROR, FORCE_MIRROR.exists())

    ea = count_files(EXTRACT_OUT)
    fa = count_files(FULL)
    ma = count_files(FORCE_MIRROR)
    packs = sorted(set(ea) | set(fa) | set(ma))
    print("\n=== file counts ===")
    for pack in packs:
        e, f, m = ea.get(pack, -1), fa.get(pack, -1), ma.get(pack, -1)
        print(f"{pack}\tEO={e}\tfull={f}\tmirror={m}\tok={e == f == m}")

    print("\n=== magic types (Extractor_Output) ===")
    for pack in sorted(ea):
        n, empty, c, other = classify_pack(EXTRACT_OUT / pack)
        top = ", ".join(f"{k}={v}" for k, v in c.most_common(10))
        print(f"{pack}\tfiles={n}\tempty={empty}\t{top}")
        if other:
            ot = ", ".join(f"{k}={v}" for k, v in other.most_common(8))
            print(f"  OTHER: {ot}")

    # HxNames coverage estimate on EO hashes
    hx = Path(__file__).resolve().parents[1] / "tools" / "vendor" / "ten_sz_hxnames" / "HxNames-Tenshi.lst"
    hx_map = {}
    for line in hx.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        h, name = line.split(":", 1)
        hx_map[h.upper()] = name
    print(f"\n=== HxNames entries={len(hx_map)} ===")
    matched = unmatched = 0
    by_pack: dict[str, list[int]] = {}
    for pack, _ in sorted(ea.items()):
        m = u = 0
        for f in (EXTRACT_OUT / pack).rglob("*"):
            if not f.is_file():
                continue
            if f.name.upper() in hx_map:
                m += 1
            else:
                u += 1
        by_pack[pack] = [m, u]
        matched += m
        unmatched += u
    for pack, (m, u) in by_pack.items():
        total = m + u
        pct = 100.0 * m / total if total else 0
        print(f"{pack}\tmatched={m}\tunmatched={u}\tcover={pct:.1f}%")
    total = matched + unmatched
    print(f"TOTAL\tmatched={matched}\tunmatched={unmatched}\tcover={100.0*matched/total:.1f}%")


if __name__ == "__main__":
    main()
