# Angelic 设置 UI — 可读源码位置

对照 Cafe：Cafe 的「可读布局」= FreeMote 解出的 PSB JSON（含 left/top/width/height）。
Angelic 对应物如下。

## 1. 脚本逻辑（已反编译）

工具：`tools/vendor/tjs2-decompiler`（UlyssesWu/tjs2-decompiler）

输出目录：
`docs/ui-extract/pixel-reverse/settings-layout/tjs-decompiled/`

| 文件 | 内容 |
|------|------|
| `option.tjs` | 设置系统框架（滑条/开关/音量模块等） |
| `uioption.tjs` | 本作 CustomOption 绑定（facemode、各 entryMyOption…） |
| `uiparts.tjs` / `uisystem.tjs` / `uimain.tjs` / `pagebase.tjs` / `system.tjs` | 相关 UI 支撑 |

原始字节码仍在：
`docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/sysscn/option.tjs`
`docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/main/uioption.tjs`

流程脚本（本来就是文本）：
`docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/sysscn/option.ks`

## 2. 布局数据（PBD = Cafe 的 PSB 角色）

路径：`docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/uipsd/option*.pbd`

可读导出：
`docs/ui-extract/pixel-reverse/settings-layout/pbd-readable/`
（`tools/dump_pbd_readable.py`）

注意：Angelic PBD **没有** Cafe 那种 `left`/`top` 字段（严格扫描 left 命中 0）。
有 `ox`/`oy`（各约 187 次）、少量 `storagex`/`storagey`；`cx`/`cy` 多数噪声大。
像素绝对坐标需用 `960+cx-ox` 公式 + 更严聚类，或原版截图模板匹配。

## 3. 文案 / 槽位拓扑

- `locale/cn/uitexts_cn.toml`
- `locale/cn/help_opt_cn.txt`（label_a…j ↔ 详细页跳转）
- 槽位拓扑与 Cafe `0_simple` 的 a–j 一致（已由 PBD 层名证实）

## 4. 官方 chrome

- `uipsd/option__bg0.tlg` → `pixel-reverse/tlg-png/option__bg0.png`
- `uipsd/option__pack.tlg` → `_pack_slices/option__pack/`
