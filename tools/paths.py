"""天使☆嚣嚣 RE-BOOT 工程 / 游戏路径。"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GAME = Path(r"E:\GAL\天使☆嚣嚣")

GAME_EXE = GAME / "tenshi_sz.exe"
LOADER = GAME / "CxdecExtractorLoader.exe"
CXDEC_DLL = GAME / "CxdecExtractor.dll"

EXTRACT_OUT = GAME / "Extractor_Output"
DOCS = REPO / "docs"
UI_EXTRACT = DOCS / "ui-extract"
STATIC_FORCE = UI_EXTRACT / "static-force"
UI_CN_JP = UI_EXTRACT / "ui-cn-jp-static"
INDEXES = DOCS / "indexes"

X86_PY = Path(r"D:\gamedev\CafeStella\tools\vendor\python311-x86\python.exe")
HXNAMES = REPO / "tools" / "vendor" / "ten_sz_hxnames" / "HxNames-Tenshi.lst"

# 中日界面相关包（对照 CafeStella 的 main/patch/uipsd）
# image ≈ UI 图；data ≈ 系统/界面脚本与文案（无独立 uipsd/main）
UI_ARCHIVES = ["image.xp3", "data.xp3"]

# 明确排除：配音 / 立绘 CG / adult / 大型升级包（非纯界面）
EXCLUDE_ARCHIVES = {
    "voice.xp3",
    "fgimage.xp3",
    "evimage.xp3",
    "adult.xp3",
    "adult2.xp3",
    "adult3.xp3",
    "upgrade.xp3",
    "upgrade2.xp3",
    "upgrade3.xp3",
}
