# 设定页问题全清单（renpy-angelic）

> 更新：2026-07-29 22:06（UTC+8）  
> 依据：实机截图（文本页）+ 板图裁切 + `meta.json` / `interaction_slots.json` + bake / `angelic_*.rpy` + `option_4text.pbd`  
> 原版：`E:\GAL\天使☆嚣嚣` · 解包：`D:\gamedev\Angelic` · 复刻：`D:\gamedev\renpy-angelic`  
> 裁切证据：`D:\gamedev\Angelic\tools\_audit_crops\`（`tab_0_*` / `tab_4_*`）  
> 同步副本：`D:\gamedev\Angelic\docs\ui-extract\SETTINGS-PAGE-ISSUES.md`

**总判**：不是「差一点对齐」，而是 **烤板标签串义/漏字 + 预览图层错位粘贴 + runtime 空壳芯片 + 色盘资源名错** 叠加；设定页目前不可用。

| 统计 | 数量 |
|------|------|
| 截图当场可见 | 9 |
| P0 根因级 | 7 |
| P1 结构/交互 | 16 |
| P2 完成度/流程 | 12 |
| **合计条目** | **44**（含分组内子项） |

权威烤板：`Angelic/tools/bake_settings_from_pbd_uistates.py`  
废弃进线：`rebuild_settings_1to1.py`（勿再跑）  
Keep-set 页：`0, 1, 2, 3, 4, 5a, 5b, 6, 8`（无鼠标 7 / 手柄 9）

---

## 0. 截图当场可见（用户 2026-07-29「文本」页）

| ID | 现象 |
|----|------|
| S01 | 顶栏选中「文本」，左侧却是「显示模式 / 画面比例 / 文本显示速度」——**基本页文案** |
| S02 | 右中「BGM」标签压在校舍预览上（文本页不该用基本页 `label_g` 文案） |
| S03 | 左上角一块校舍图裁出顶栏；中下又一大块校舍横条 |
| S04 | 成排空蓝角括号 `[ ]`，无「开/关」「窗口/全屏」等字 |
| S05 | 白云/翼形白标悬空，未对齐控件 |
| S06 | 滑条区只有淡轨/空框，缺清晰旋钮与数值底 |
| S07 | 底栏「恢复默认 / 标题」像裸字；「游戏画面」才有完整皮 |
| S08 | 「天使☆嚣嚣 RE-BOOT!」飘在预览附近（winsample 文案） |
| S09 | 帮助区有字但偏小；有时是泛用说明而非当前控件 |

---

## 1. P0 — 根因级（工程证据已坐实）

### P0-1 跨页 `label_*` 共用错误中文表（串页文案）

- **证据**：`option_4text.pbd` 层名含 `label_a / label_b / label_c / label_g ...`（与基本页同名）。
- **烤板** `LABEL_CN` 把 `label_a→显示模式`、`label_b→画面比例`、`label_c→文本显示速度`、`label_g→ＢＧＭ` 写成**基本页语义**，却用于**所有页**的 `label_*`。
- **结果**：`tab_4.png` 左侧裁切已是基本页三行标签；右下「BGM」同理。  
  → 截图「文本页看起来像基本页」**主要是烤错字，不一定是 `plate_image` 指错文件**。
- **正确源**：`uitexts_cn.toml` 的 `config_label_*`（按设定项语义，非 `label_a` 字母）。
- **文件**：`bake_settings_from_pbd_uistates.py` → `LABEL_CN`。

### P0-1b 文本页大量 `label_*` 在 `LABEL_CN` 中缺失 → 空白标签

`option_4text.pbd` 实测映射：

| 层名 | LABEL_CN 结果 | 坐标约 |
|------|---------------|--------|
| label_a | 显示模式（**错义**） | 106,137 |
| label_b | 画面比例（**错义**） | 106,275 |
| label_c | 文本显示速度（可能碰巧近义） | 106,551 |
| label_g | ＢＧＭ（**错义**） | 1005,635 |
| label_a1 / a2 / d1 / d2 / e1 / e2 / f1 / f2 | **(EMPTY)** 不画字 | 多处 |

→ 文本页一半标签空白、一半串成基本页，板上必然「空洞 + 乱字」。

### P0-2 `winsample_orig_*` 以 (0,0) 烤进文本板

- **证据**：pbd2json  
  - `winsample_orig_base` / `winsample_orig_color` → `x=0,y=0,w=800,h=156`  
  - 正规 `winsample` / `rendersample` / `winsample_back` → `1030,685,800,156`
- **烤板**对「有 uistate 且非 chip/mute/check」的层会 `paste` → 校舍贴到**左上角**。
- 正规 `winsample` 再贴内容区 → 中下第二块校舍。  
  → 截图「两块校舍」= **同素材烤了两次（错位 + 正位）**。
- Runtime 文本页再叠 `Solid` 半透明条 + `RE-BOOT!`（`angelic_screens.rpy`）→ **三重叠**风险。

### P0-3 烤板不烤 chip；runtime 只见空角括号

- 烤板对 `*_off` / `*_on` **`continue` 跳过**（避免与 runtime 抢态）。
- `chip_off.png` 为官方空心角括号（~326B，mean α≈29）——未选中时就是「空框」。
- 选中应用 `chip_on` + 白字；截图大量空框 ⇒ **字没叠上，和/或 `background Transform` 被 `style angelic_empty_button` 吃掉 / 未刷新**。
- 相关：`angelic_screens.rpy` toggle 段；`style angelic_empty_button` 默认透明底。

### P0-4 点击反馈双定义债

- `angelic_prefs.rpy` **后加载覆盖** `angelic_pick_toggle` / `angelic_set_help` / `angelic_dialog_set`（压过 `angelic_core.rpy`）。
- 曾缺 `renpy.restart_interaction()` → 点了值变界面不刷。prefs 末尾已补；**以后改交互必须改 prefs，或合并为单一实现**。

### P0-5 色盘 SV 资源名不一致

- 磁盘：`chrome/colorpicker/sv_000.png` …（约 148 文件）
- 代码：`angelic_color_tri_path` → `tri_%03d.png`  
  → 色盘三角层**基本加载失败**（有 ring 时仍残缺）。

### P0-6 footer 回退引用未定义 `_page0`

- `angelic_screens.rpy` ~483：`if not _footer and _page0.get("footer_xs")`  
- **screen 内未赋值 `_page0`** → 若 meta 缺 footer，可能 `NameError` 直接炸设定屏（当前 meta 有 footer，属潜伏雷）。

### P0-7 QA 基准失真

- `_qa_tab0_official.png` 与当前 `tab_0.png` **逐字节相同**（烤后自拷）。
- 现板为「无芯片 + 系统描字」策略产物，**不再代表「带官方芯片的观感」**；`_compare_settings_qa` 易假绿。

---

## 2. P1 — 结构 / 布局 / 交互

| ID | 问题 | 说明 |
|----|------|------|
| P1-1 | 页签 6→8 空隙约 **102px** | 去掉鼠标(7)/手柄(9)后几何未收拢 |
| P1-2 | 音频拆成 5a/5b 半宽热区 | 板上多半仍一个「音频」字；与原版单页观感不一致 |
| P1-3 | 页签选中态弱/易误解 | 已去 runtime 蓝块；只靠 plate pgdot；易与串页文案一起误判 |
| P1-4 | 顶栏/标签为系统描字 | `option_locale` 未解出；非官方字模 |
| P1-5 | 详细箭头仅 tab0 槽位带 `detail` | tab0 `with_detail=10`；其它页 `0` |
| P1-6 | 键盘页 87×`button` **无 `chips[]`** | fallback 横排；options 多为内部英文 key |
| P1-7 | `slider_num.png` 缺失 | 自检禁止合成；数字靠纯 text，易飘/对比差 |
| P1-8 | winsample 默认 `text_y=220` 但 meta `h=156` | 文案默认落在框外 |
| P1-9 | core `setdefault` winsample `y=543,h=312` vs meta `y=685,h=156` | meta 丢失时回退错误 |
| P1-10 | 底栏三钮样式不统一 | init/title 透明热区；back 用 sysbtn hover |
| P1-11 | mute 图标尺寸 vs 热区 | chrome≈38×27，热区常更大 |
| P1-12 | 滑条双轨风险 | 板可烤 rail/knob，runtime 再叠 rail+thumb |
| P1-13 | `reload_settings` 与 truth 合并 | `settings_truth.json` 可能 `setdefault` 改 help_box/footer |
| P1-14 | 白云悬空 | jump/pgdot/装饰未对齐，或 chip 残影 |
| P1-15 | `color_target` 芯片未按槽位缩放 | 部分路径用原图 `chip_on/off` 不 `Transform`，与 toggle 路径不一致 |
| P1-16 | `dialog_onoff` 仍用 `Transform(..., size=)` | 与 toggle 的 `xysize` 混用；且同样吃 empty_button style |

---

## 3. P2 — 完成度 / 资源 / 流程

| ID | 问题 |
|----|------|
| P2-1 | 帮助已烤入 `help` 262 条（UTF-16 `help_opt_cn.txt`），控件 hover key 对不上仍落泛句 |
| P2-2 | 确认页/键盘页字模、键名中文化未完成 |
| P2-3 | 5b 爪印/角色音量、sysvo 等复杂态未逐条对照原版 |
| P2-4 | `color_*` 必须走 `color_target`（HSV list）；回归要盯 |
| P2-5 | `.rpyc` / `game/cache` 未清时易看旧逻辑 |
| P2-6 | `rebuild_settings_1to1.py` 仍在树内；误跑会再盖空板 |
| P2-7 | 自检 PASS ≠ 可用；不能替代肉眼/原版抓帧 |
| P2-8 | 标题/存读档/CG/流程图等其它 UI 不在本清单 |
| P2-9 | 剧情 scn / 语音 / 立绘播放 — 明确不在设定复原范围 |
| P2-10 | `value_on.png` 极小（~562B），wide_value 可能几乎看不见 |
| P2-11 | 各页 `LABEL_CN` 缺项会系统性漏标（不限文本页） |
| P2-12 | ui-preview 与 renpy `images/angelic/settings` 双份同步；只改一处会漂 |

---

## 4. 各页槽位快照（`interaction_slots.json`）

| tid | slots | 类型概要 | 备注 |
|-----|------:|----------|------|
| 0 | 11 | slider7 + toggle3 + check1 | detail×10；mute 齐 |
| 1 | 14 | slider2 + toggle8 + check4 | 无 detail |
| 2 | 12 | toggle×12 | |
| 3 | 9 | slider3 + toggle3 + check3 | |
| 4 | 14 | color_target5 + slider4 + toggle4 + check1 | **文案/预览重灾区** |
| 5a | 15 | slider11 + toggle2 + check2 | |
| 5b | 32 | toggle1 + check31 | 爪印密集 |
| 6 | 24 | toggle22 + check2 | |
| 8 | 87 | button×87 | **全部无 chips[]** |

Chrome：chip/slider/mute/check/detail/sysbtn 基本齐全；**缺** `slider_num.png`；色盘有 `sv_*` **无** `tri_*`。  
Plates：9 张 keep-set，1920×1080；无残留 `tab_5/7/9`。  
tabs_layout：`6→8` gap≈102。

---

## 5. Runtime / 双定义风险表

| 符号 | core | prefs（后胜） | 风险 |
|------|------|---------------|------|
| `angelic_set_help` | 有 | **覆盖** | 改错文件无效 |
| `angelic_pick_toggle` | 有 | **覆盖** | 必须带 restart |
| `angelic_dialog_set` | 有 | **覆盖** | 行为可能分叉 |
| `angelic_help_text` | 调 prefs_help | — | 依赖 meta.help |
| `plate_image` | 仅 core | — | 按 `tabs[i].plate` |
| `current_hotspots` | 仅 core | — | 按 `settings_tab_id()` |

`style angelic_empty_button`：全局透明 `background`/`hover_background`——实例属性在部分 Ren'Py 版本会被吃，导致 **芯片皮消失只剩命中框**（与 S04 高度吻合）。

---

## 6. 建议修复顺序（未开工，仅规划）

1. **按页 / 按 uitexts `config_label_*` 解析标签**，禁止全局 `label_a→显示模式`；补全 `label_a1` 等；重烤全部 plate。  
2. **bake 黑名单**：`winsample_orig*`、以及 `x=0,y=0` 的大尺寸预览层禁止 paste；winsample 几何进 meta，预览图策略二选一（只烤板 / 只 runtime）。  
3. **芯片**：确认 `button`+`Transform` 不被 style 吃掉；保证 options 中文必显；必要时改 `imagebutton`/`add`+透明热区。  
4. **色盘** `tri_*`↔`sv_*` 对齐。  
5. 修 `_page0` 未定义；winsample `text_y`；页签空隙；键盘 chips。  
6. 换 QA 基准图；清 rpyc 后逐页抓帧对照原版。

---

## 7. 相关路径速查

```
renpy-angelic/docs/SETTINGS-PAGE-ISSUES.md          # 本清单（主）
Angelic/docs/ui-extract/SETTINGS-PAGE-ISSUES.md     # 同步副本
renpy-angelic/game/angelic_screens.rpy              # screen angelic_settings
renpy-angelic/game/angelic_core.rpy                 # plate / hotspots / 被覆盖 helpers
renpy-angelic/game/angelic_prefs.rpy                # 实际生效 pick_toggle / set_help
renpy-angelic/game/angelic_color_picker.rpy         # tri_ 路径错误
renpy-angelic/game/images/angelic/settings/         # plates / chrome / meta / slots
Angelic/tools/bake_settings_from_pbd_uistates.py
Angelic/tools/_audit_settings_selfcheck.py
Angelic/tools/_audit_crops/                         # 裁切证据
Angelic/docs/ui-extract/HANDOFF-COMPLETE-RECREATE.md
```

---

## 8. 变更记录

| 日期 | 说明 |
|------|------|
| 2026-07-29 21:50 | 初版：截图 P0–P2 + 串义 LABEL、winsample_orig@0,0、空壳 chip、色盘名、双定义 |
| 2026-07-29 22:06 | 补全：LABEL 缺失表、`_page0` NameError、QA 失真升 P0、P1-15/16、P2-10~12；条目统计 |
