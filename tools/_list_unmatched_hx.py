"""List HxNames unmatched hashes from Extractor_Output."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from paths import EXTRACT_OUT, HXNAMES


def main() -> None:
    hx_map: dict[str, str] = {}
    for line in HXNAMES.read_text(encoding="utf-8", errors="replace").splitlines():
        if ":" not in line:
            continue
        h, name = line.split(":", 1)
        hx_map[h.upper()] = name

    unmatched: list[tuple[str, str, int, str]] = []
    for pack_dir in sorted(p for p in EXTRACT_OUT.iterdir() if p.is_dir()):
        for f in pack_dir.rglob("*"):
            if not f.is_file():
                continue
            if f.name.upper() in hx_map:
                continue
            with open(f, "rb") as fh:
                b = fh.read(8)
            unmatched.append((pack_dir.name, f.name, f.stat().st_size, b[:4].hex()))

    print("unmatched", len(unmatched))
    print("by_pack", dict(Counter(u[0] for u in unmatched)))
    print("by_magic", dict(Counter(u[3] for u in unmatched)))
    for u in unmatched[:40]:
        print(f"{u[0]}\t{u[2]}\t{u[3]}\t{u[1][:48]}")


if __name__ == "__main__":
    main()
