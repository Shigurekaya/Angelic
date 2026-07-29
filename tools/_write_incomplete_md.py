#!/usr/bin/env python3
"""Generate docs/ui-extract/INCOMPLETE-UNPACK.md from audit JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from paths import EXTRACT_OUT, HXNAMES, UI_EXTRACT

DATA = UI_EXTRACT / "_incomplete_unpack_data.json"
OUT = UI_EXTRACT / "INCOMPLETE-UNPACK.md"


def fmt_size(n: int) -> str:
    if n >= 1_048_576:
        return f"{n / 1_048_576:.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n} B"


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    unmatched = data["unmatched"]
    by_pack = data["by_pack"]
    by_magic = data["by_magic"]
    tlg = data["tlg_by_pack"]
    tlg_total = sum(tlg.values())

    total_files = 58166
    hx_entries = sum(
        1
        for line in HXNAMES.read_text(encoding="utf-8", errors="replace").splitlines()
        if ":" in line
    )
    matched = total_files - len(unmatched)
    cover = 100.0 * matched / total_files

    renamed = UI_EXTRACT / "ui-cn-jp-static" / "renamed"
    filtered = UI_EXTRACT / "ui-cn-jp-static" / "filtered-cn-jp"
    renamed_n = sum(1 for f in renamed.rglob("*") if f.is_file()) if renamed.exists() else 0
    filtered_n = sum(1 for f in filtered.rglob("*") if f.is_file()) if filtered.exists() else 0

    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %z")
    lines: list[str] = []
    a = lines.append

    a("# 天使☆嚣嚣 — 未完全解包记录")
    a("")
    a(f"> 生成：{now}  ")
    a("> 对照：`E:\\GAL\\天使☆嚣嚣\\Extractor_Output` ↔ `Angelic/docs/ui-extract/full-static`  ")
    a("> HxNames：`tools/vendor/ten_sz_hxnames/HxNames-Tenshi.lst`")
    a("")
    a("## 结论摘要")
    a("")
    a("| 层级 | 状态 | 说明 |")
    a("|---|---|---|")
    a("| **Cxdec 解密落地** | ✅ 完成 | 11 个 `.xp3` 均已解密；EO / full-static 文件数一致（58166） |")
    a(
        f"| **HxNames 名表可匹配** | ⚠️ 部分 | {matched}/{total_files}（{cover:.1f}%）；**{len(unmatched)}** 个哈希不在名表 |"
    )
    a(
        f"| **全量路径还原到磁盘** | ❌ 未做 | full-static / Extractor_Output 仍为 HxV4 哈希名；仅 UI 子集还原（renamed={renamed_n}，filtered-cn-jp={filtered_n}） |"
    )
    a(
        f"| **TLG → PNG** | ❌ 未做 | 仍有 **{tlg_total}** 个 TLG（解密完成，格式未转换） |"
    )
    a("| **XP3 静态索引** | ❌ 失败 | `docs/indexes/summary.json`：`XP3File` 不可迭代 |")
    a("| **voice.xp3** | ✅ 完成 | 旧 `full-static-verify.json` 标 missing 已过时 |")
    a("")
    a("说明：**「未完全」指后处理（命名 / 格式 / 索引），不是 Cxdec 未解出。**")
    a("")
    a("## 1. 全量路径还原缺口")
    a("")
    a("- 名表条目：" + f"**{hx_entries}**")
    a(f"- 可匹配哈希：{matched}（{cover:.1f}%）")
    a(f"- **无法命名（不在 HxNames）：{len(unmatched)}** — 见下文完整清单")
    a(f"- 已还原到磁盘：仅 `ui-cn-jp-static/renamed`（{renamed_n}）+ `filtered-cn-jp`（{filtered_n}）")
    a("- `full-static/` 内 **0** 个带扩展名的内容文件（全部哈希名）")
    a("")
    a("### 1.1 无名哈希按包分布")
    a("")
    a("| 包 | 无名文件数 |")
    a("|---|---:|")
    for pack, n in sorted(by_pack.items(), key=lambda x: (-x[1], x[0])):
        a(f"| {pack} | {n} |")
    a(f"| **合计** | **{len(unmatched)}** |")
    a("")
    a("### 1.2 无名哈希按格式分布")
    a("")
    a("| 格式 | 数量 |")
    a("|---|---:|")
    for fmt, n in sorted(by_magic.items(), key=lambda x: (-x[1], x[0])):
        a(f"| {fmt} | {n} |")
    a("")
    a("## 2. TLG 未转 PNG")
    a("")
    a("内容已解密可读，但未做二次转码：")
    a("")
    a("| 包 | TLG 数 |")
    a("|---|---:|")
    for pack, n in sorted(tlg.items(), key=lambda x: (-x[1], x[0])):
        a(f"| {pack} | {n} |")
    a(f"| **合计** | **{tlg_total}** |")
    a("")
    a("## 3. 其它未完成项")
    a("")
    a("1. **`tools/index_xp3.py`**：静态索引失败（`TypeError: 'XP3File' object is not iterable`），`docs/indexes/` 无有效归档清单。")
    a("2. **工程范围**：README 明确配音/剧情按需接线；Ren'Py 侧以 UI 为主，不等于全资源可读树。")
    a("3. **重复副本**：游戏目录 `Extractor_Output` 与 `full-static` 各约 11 GB（内容等价）；`static-force/Extractor_Output` 已删。")
    a("")
    a("## 4. 建议补全顺序")
    a("")
    a("1. 对 `full-static`（或 EO）跑全量 HxNames 还原 → `renamed-full/`，无名项进 `unmatched/`。")
    a("2. 按需 TLG→PNG（优先 `fgimage`）。")
    a("3. 修复 `index_xp3.py` 或改用 `.alst` + HxNames 重建索引。")
    a("4. 更新 `full-static-verify.json`（补上 voice）。")
    a("")
    a("---")
    a("")
    a("## 5. 无名哈希完整清单（443）")
    a("")
    a("路径相对 `Extractor_Output/`（与 `full-static/` 同构）。内容已解密，仅缺官方文件名。")
    a("")
    a("| # | 包 | 大小 | 格式 | 相对路径 |")
    a("|---:|---|---:|---|---|")
    for i, row in enumerate(
        sorted(unmatched, key=lambda r: (r["pack"], r["rel"])), start=1
    ):
        a(
            f"| {i} | {row['pack']} | {fmt_size(row['size'])} | {row['format']} | `{row['rel']}` |"
        )
    a("")
    a("---")
    a("")
    a("## 附录：数据源")
    a("")
    a("| 文件 | 用途 |")
    a("|---|---|")
    a("| `INCOMPLETE-UNPACK.md` | 本记录 |")
    a("| `_incomplete_unpack_data.json` | 机器可读清单 |")
    a("| `FULL-STATIC-UNPACK-LOG.md` | Cxdec 全量解包日志（解密完成） |")
    a("| `static-force/full-static-verify.json` | 旧校验（voice 状态过时） |")
    a("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(unmatched)} unmatched)")


if __name__ == "__main__":
    main()
