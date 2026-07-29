# -*- coding: utf-8 -*-
"""Official bare pixels for Angelic settings — Cafe Stella style.

Cafe: FreeMote PSB -> left/top
Angelic: pbd2json.exe -> x/y/width/height
"""
from __future__ import annotations

from unpack_pbd2json_ui import main as unpack_all
from build_settings_from_pbd2json import main as build_layout


def main() -> None:
    unpack_all()
    build_layout()


if __name__ == "__main__":
    main()
