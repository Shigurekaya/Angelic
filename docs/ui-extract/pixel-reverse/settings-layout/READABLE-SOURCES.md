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

注意：用长度前缀**启发式扫描**时看不到可靠 `left`/`top`。
**正确做法（对齐 Cafe）：** 用 `CafeStella/tools/vendor/.../pbd2json.exe` 解 PBD，
`result.*.x/y/width/height` 即为官方绝对坐标（等价 FreeMote `left/top`）。
产物：`pixel-reverse/pbd2json-layers/`。

## 3. 文案 / 槽位拓扑

- `locale/cn/uitexts_cn.toml`
- `locale/cn/help_opt_cn.txt`（label_a…j ↔ 详细页跳转）
- 槽位拓扑与 Cafe `0_simple` 的 a–j 一致（已由 PBD 层名证实）

## 4. 官方 chrome

- `uipsd/option__bg0.tlg` → `pixel-reverse/tlg-png/option__bg0.png`
- `uipsd/option__pack.tlg` → `_pack_slices/option__pack/`

## 5. 官方裸像素坐标（当前真值）

Angelic PBD **无** Cafe FreeMote 式 `left`/`top`。设定页绝对坐标来自：

| 产物 | 路径 | 说明 |
|------|------|------|
| 抓图真值 | `settings_truth.json` | `ig_option_*_1080` 蓝块/控件量测 |
| 切片落点 | `slice_placements.json` | 官方 pack 片模板匹配 |
| **汇总** | `official_bare_pixels.json` | Cafe 式 tabs/rows 绝对 x/y/w/h |
| 烤板布局 | `angelic_settings_layout.json` | rebuild 写入，与上表 grid 一致 |

重跑：

```bat
cd /d D:\gamedev\Angelic
python tools\unpack_official_bare_pixels.py
python tools\rebuild_settings_1to1.py
```

简易页关键裸像素（1920×1080）：

- 行 y：`237 / 483 / 728 / 880`
- 左控件 x：`195`；宽值条：`571×75`
- 右滑轨 x：`1655`；静音 x：`1544`
- 底栏 y：`973`；按钮 x：`940 / 1187 / 1434`
