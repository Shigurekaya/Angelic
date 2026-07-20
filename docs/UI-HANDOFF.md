# 天使☆嚣嚣 · Angelic / renpy-angelic 界面与实现交接

> 换对话用。对齐 Cafe 的 `renpy-cafe/docs/UI-HANDOFF.md` 写法。  
> Ren'Py 工程：`D:\gamedev\renpy-angelic`  
> 解包 / 烤板 / 工具：`D:\gamedev\Angelic`  
> 原版安装：`E:\GAL\天使☆嚣嚣`  
> Ren'Py SDK：`D:\gamedev\renpy-8.5.3-sdk\renpy.exe`  
> 对照工程：`D:\gamedev\renpy-cafe` + `D:\gamedev\CafeStella`  
> 分辨率：**1920×1080**  
> 原则（近期硬约束）：**完全用官方解包素材整片**，禁止 `make_chip` 手绘壳、禁止对官方切片二次裁切 / 九切片造假 chrome。

---

## 1. 工程怎么跑

```bat
D:\gamedev\renpy-8.5.3-sdk\renpy.exe D:\gamedev\renpy-angelic
```

或双击 `D:\gamedev\renpy-angelic\启动游戏.bat`。

改 `.rpy` / 换图后建议 **完全退出再开** 或 **Shift+R**；必要时删对应 `.rpyc`。

本工程**除去剧情**：「从头开始 / 继续」未接剧本。

---

## 2. 三路径职责

| 路径 | 职责 |
|------|------|
| `E:\GAL\天使☆嚣嚣` | 原版游戏（运行对照 / 截图真值） |
| `D:\gamedev\Angelic` | 静态解包、PBD/TJS 反推、烤板脚本、`ui-preview` |
| `D:\gamedev\renpy-angelic` | Ren'Py 复刻工程（运行时 screen + 同步后的 images） |

解包主目录（中日过滤静态）：

`Angelic/docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/`

像素反推产物：

`Angelic/docs/ui-extract/pixel-reverse/`

- `tlg-png/` — TLG→PNG（含 `option__bg0.png`、各 `option_*__pack.png`）
- `_pack_slices/` — pack 切片（`option__pack/s000_….png` + `slices.json`）
- `settings-layout/` — 设置布局文档与 JSON（见下）

同步目标：

`renpy-angelic/game/images/angelic/`

预览镜像：

`Angelic/ui-preview/assets/`

---

## 3. 全部界面一览

| 界面 | Screen / 入口 | 主脚本 | 资源目录 / 数据 |
|------|---------------|--------|-----------------|
| 标题 | `angelic_title` / `main_menu` | `angelic_title_anim.rpy`, `screens.rpy`, `script.rpy` | `images/angelic/title/` + `hotspots.json`, `title_chars.json` |
| 设定 | `angelic_settings` / `preferences` | `angelic_screens.rpy`, `angelic_core.rpy` | `images/angelic/settings/` + `meta.json`, `interaction_slots.json` |
| 读档 | `angelic_load` / `load` | `angelic_screens.rpy` | `images/angelic/file/` 或 `load/` |
| 存档 | `angelic_save` / `save` | 同上 | `file/composite_*.png` + meta |
| 流程图 | `angelic_flowchart` | `angelic_screens.rpy` | `images/angelic/flowchart/` |
| CG 鉴赏 | `angelic_cg` | `angelic_screens.rpy` | `images/angelic/cg/` + `cg_hotspots.json` |
| 退出确认 | `confirm` / `angelic_qconf` | `screens.rpy`, `angelic_screens.rpy` | `images/angelic/qconf/` |
| HUD / 快捷 | `angelic_hud` | `angelic_screens.rpy` | `images/angelic/hud/`, `touch/` |
| 历史 | `angelic_backlog` | `angelic_screens.rpy` | — |
| 语言选择 | 标题内 / langselect | 标题相关 | `images/angelic/langselect/` |
| 手机聊天 | `angelic_phonechat` | `angelic_screens.rpy` | `images/angelic/phonechat/` |
| AfterStory | `angelic_afterstory` | `angelic_screens.rpy` | `images/angelic/afterstory/` |

核心数据总线：`angelic_core.rpy`（`angelic` store：tab、values、plate、file/cg meta、prefs 同步）。

默认 `screens.rpy` 把 `main_menu` / `preferences` / `load` / `save` 等转到 angelic 版。

---

## 4. 标题 UI（已相对成型）

| 层 | 解包来源 |
|----|----------|
| 入场底 | `_mtn/title_bg` → `title/layers/bg_plain.png` |
| 入场角色 | 四人单独层 `ch_ama/noa/kag/kur`（`title_bg.mtn` → `char_move`），`title_chars.json` |
| 终局/静态背景 | `title_bg0..7.png` |
| Logo+框 | `title_logo_cn.png` |
| 底栏 8 钮 | `title_locale_cn__pack` 切片 |
| 语言 / 切背景 | `langselect` / `title__pack` |

- 入场时序对齐 FreeMote `title_bg.mtn`（logo≈0.68s，每人 char_move≈0.5→1.5s，总长≈2.02s）
- 热区：`game/images/angelic/title/hotspots.json`
- 重烤：`Angelic/tools/build_title_1to1.py`、`build_title_char_layers.py`

已知：PBD 坐标噪声大，标题位置用模板匹配/均分，不是裸 FreeMote 像素坐标。

---

## 5. 设定 UI（近期主战场 · 状态摘要）

### 5.1 方法（对齐 Cafe，几何用 Angelic 原生）

- **拓扑**：Cafe `settings-layout.json` 的 **keys/types only**（简易页 a–j 与 Angelic PBD / `help_opt` 一致）
- **几何**：**不要用 Cafe 的 841×46 / 637×29**；用官方 `option__pack` 尺寸：
  - 标签条 **313×57**（s005 / s009）
  - 滑轨 **288×13**（s014）
- **交互**：plate 烤背景+标签字；运行时叠官方 chrome 整片（滑钮/开关壳/静音/详细）
- **硬约束（用户明确）**：**完全官方素材，不要自己剪切**  
  - 禁止 `make_chip`  
  - 禁止对 s010/s011 等官方片二次半切/四切  
  - 禁止九切片造假 chrome  
  - 允许：官方 `s*.png` **整片**复制为别名；分页 pack **逐片整片摆放**

### 5.2 重烤命令

```bat
cd /d D:\gamedev\Angelic
python tools\rebuild_settings_1to1.py
```

产出：

- `Angelic/ui-preview/assets/settings/`
- 同步 → `renpy-angelic/game/images/angelic/settings/`
- 布局 JSON → `docs/ui-extract/pixel-reverse/settings-layout/angelic_settings_layout.json`

自检脚本（结构/字节对照，**不能**代替视觉真值）：

- `tools/_audit_settings_selfcheck.py`
- `tools/_audit_ui_gap.py`

### 5.3 运行时文件

| 文件 | 职责 |
|------|------|
| `angelic_screens.rpy` → `screen angelic_settings` | plate + 页签 on/over/label + 滑条/chip/mute/detail/footer |
| `angelic_core.rpy` | `reload_settings`、`plate_image`、`current_hotspots`、`angelic_settings_detail`、mute/prefs |
| `settings/meta.json` | tabs、tabs_layout、footer、help |
| `settings/interaction_slots.json` | 各页热区（key=`0`…`9` / `5a`/`5b`） |
| `settings/plates/tab_*.png` | 11 页整页烤板 |
| `settings/chrome/` | 官方切片别名 + `official/` 归档 |
| `settings/tabs/` | `label_*.png`（中文 locale 字）+ `on/over`（官方翼标/箭头整片） |

`plate_image()`：优先返回磁盘相对路径 `angelic/settings/plates/...`（对齐 Cafe）；`init python` 另注册 `angelic_plate_*`。

详细跳转（简易页 → 高级页 index）：

```text
fullscreen/sqscr → 1
skipall → 2          # 对齐 Cafe label_e_jump（曾误跳 4）
textspeed/autospeed → 4
wave/bgm/se/voice/movie → 5   # 即 5a
```

### 5.4 `option__pack` 官方切片角色（整片使用）

路径：`Angelic/docs/ui-extract/pixel-reverse/_pack_slices/option__pack/`

| 索引 | 文件尺寸 | 用途（当前映射） |
|------|----------|------------------|
| s000 | 80×731 | 左侧装饰条（烤进 plate） |
| s001 | 16×610 | 细竖条 |
| s002 | 412×383 | 复合装饰板（勿当单一控件） |
| s003 | 56×33 | **麦克风** → `voice_mic.png`（**绝不当详细按钮**） |
| s004 | 30×30 | check_on |
| s005 | 313×57 | 标签条 / chip_off |
| s006 | 30×30 | check_off |
| s007/s008 | 30×30 | check over 态 |
| s009 | 313×57 | 亮标签条 / chip_on·over |
| s010 | 76×54 | **静音整片**（内含四态，不四切）→ mute_* |
| s011 | 124×32 | **详细箭头整片**（内含双态，不半切）→ detail_* |
| s012 | 138×37 | SYSTEM 字图 |
| s013 | 144×37 | SETTING 字图 |
| s014 | 288×13 | 滑轨 |
| s015 | 421×265 | 复合装饰（勿硬缩放塞 help） |
| s016/s017 | 19×35 | 小箭头 → tabs over |
| s018 | 47×46 | 翼标 → knob / tabs on |

底栏钮：`option_cmds__pack` **s000**（242×60）→ `stdbtn_*`。

### 5.5 分页官方 pack（已接线进烤板）

| 页 id | pack | 说明 |
|-------|------|------|
| 4 | `option_4text__pack` | 文本/色板类 |
| 5a | `option_5sound1__pack` | 音频1 / 立绘语音 |
| 5b | `option_5sound2__pack` | 音频2 |
| 6 | `option_6dialog__pack` | 确认 |
| 7 | `option_7mouse__pack` | 鼠标图 |
| 8 | `option_8keyboard1__pack` | 键盘图 |
| 9 | `option_9gamepad__pack` | 手柄图 |
| — | `option_cmds__pack` / `option_keyinput__pack` | 命令条 / 键位（量大） |

烤板对分页采用 **逐 `s*.png` 整片流式摆放**（`paste_page_pack_slices`），不贴整包 atlas、不裁片内。

### 5.6 设定页签（11）

`0` 基本 · `1` 画面 · `2` 游戏1 · `3` 游戏2 · `4` 文本 · `5a` 音频1 · `5b` 音频2 · `6` 确认 · `7` 鼠标 · `8` 键盘 · `9` 手柄

槽位密度：主页较满；**7/8/9 仍极稀**（2/1/2），属反推缺口。

### 5.7 设定可读源（反推）

详见：`Angelic/docs/ui-extract/pixel-reverse/settings-layout/READABLE-SOURCES.md`

| 类型 | 位置 |
|------|------|
| TJS 反编译 | `settings-layout/tjs-decompiled/`（`option.tjs` / `uioption.tjs`…）工具 `tjs2-decompiler` |
| PBD 可读 | `settings-layout/pbd-readable/option_*.json` |
| 文案 | `locale/cn/uitexts_cn.toml`、`help_opt_cn.txt` |
| **关键差异** | Angelic PBD **无** Cafe 式 `left/top`；有 `ox/oy`，绝对坐标噪声大 |

Cafe 等价：FreeMote **PSB** 有精确 left/top；**FreeMote 不吃 Angelic PBD**。

---

## 6. 其它界面（摘要）

| 界面 | 要点 | 重烤/工具 |
|------|------|-----------|
| 存读档 | `file/composite_*.png` + meta | `build_other_screens_1to1.py` |
| 流程图 | `scnchart__bg0` 裁到 1080 | `rebake_settings_flowchart_1to1.py` |
| CG | `view_state` + thumbs + `cg_hotspots.json` | `wire_cg_runtime.py` |
| 确认 | `qconf` 防 yesno 崩 | 同步 `ui-preview/assets/qconf` |
| HUD/触控 | `hud/` `touch/` + hotspots json | 解包 packs |

全量同步：

```bat
cd /d D:\gamedev\Angelic
python tools\sync_all_ui_to_renpy.py
```

常用管线（README）：

```bat
python tools\build_title_1to1.py
python tools\build_other_screens_1to1.py
python tools\wire_cg_runtime.py
python tools\rebuild_settings_1to1.py
python tools\sync_all_ui_to_renpy.py
```

---

## 7. 关键脚本索引

### renpy-angelic/game

| 文件 | 职责 |
|------|------|
| `angelic_core.rpy` | store、plate、settings/file/cg、prefs、详细跳转/mute |
| `angelic_screens.rpy` | 设定/存读档/流程图/CG/HUD/确认等 screen |
| `angelic_title_anim.rpy` | 标题入场与静态 |
| `screens.rpy` | 默认入口覆盖 → angelic |
| `script.rpy` / `options.rpy` / `gui.rpy` | 入口与默认 GUI |

### Angelic/tools（UI 相关）

| 脚本 | 职责 |
|------|------|
| `rebuild_settings_1to1.py` | **设定烤板主脚本（当前政策：官方整片）** |
| `sync_all_ui_to_renpy.py` | 同步到 renpy-angelic |
| `build_title_1to1.py` | 标题 |
| `build_other_screens_1to1.py` | 其它屏 |
| `slice_all_ui_packs.py` | pack 切片 |
| `dump_pbd_readable.py` | PBD 可读导出 |
| `_audit_settings_selfcheck.py` / `_audit_ui_gap.py` | 设定自检 |

---

## 8. 已知坑（续聊优先）

1. **设定视觉差距大**：曾用 `make_chip` 合成壳 → 用户判定「很多 UI 图没了」。已改为官方整片；**仍未像素级对齐原版**（分页摆放是流式，不是原版坐标）。  
2. **s003 = 麦克风**，绝不当「详细设定」；详细用 **s011 整片**。  
3. **PBD 无 left/top**：不能照搬 Cafe FreeMote 坐标当真值；启发式 `ox/oy` 噪声大。  
4. **截图不可当设定真值**：不少 `ig_option_*` / 白屏 / 退出框混入。  
5. **官方复合片**：s002/s015/声优大图等片内自带多图标；用户禁止手切 → 整片用会显得挤/歪，需等官方 UV/PBD 子矩形。  
6. **鼠标/手柄页已按用户要求移除**；键盘页保留但槽位仍稀。  
7. **Cafe 841/637 几何禁止泄漏**进 Angelic 烤板常量。  
8. **`renpy.loadable` 对 images 短路径**：Cafe 有 `cafe_extra_asset` 铁律；Angelic 目前多用 `angelic/...` 相对路径，若遇丢图对照 Cafe 做法。  
9. **上次「结构 PASS」误导**：路径存在 ≠ 官方图；自检应查 **官方切片字节覆盖率**。  
10. **无剧情**：start/continue 仅 UI 壳。

---

## 9. 建议下一对话可做

- [x] 去掉鼠标 / 手柄页（用户要求）；保留基本/画面/游戏1/2/文本/音频1/2/确认/键盘
- [x] 分页 pack 由流式改为定点摆放；有装饰图的页改左栏布局
- [x] 开关槽停止把 313×57 官方片压扁，小槽改用 check 整片
- [ ] 用原版 `ig_option_*` 真图再精调标签/滑轨像素坐标（当前网格仍为启发式 + 部分锚点）
- [ ] 音频页立绘语音等小切片按原版坐标补全（现仅主面板定点）
- [ ] 标题/存读档/CG 与原版视觉抽检

---

## 10. 相关文档与产物

| 文档/产物 | 路径 |
|-----------|------|
| 本交接 | `renpy-angelic/docs/UI-HANDOFF.md` |
| 摆片匹配 | `Angelic/.../settings-layout/slice_placements.json` |
| 原版抓图 | `Angelic/.../_orig_capture/ig_option_*_1080.png` |
| Cafe 对照 | `renpy-cafe/docs/UI-HANDOFF.md` |

---

## 11. 会话结论快照（2026-07-20 续）

- 已用 ImageGrab 抓到可用设定真图（`ig_option_*_1080`）；PrintWindow 不可用。
- 按用户要求 **排除鼠标(7)/手柄(9)**，保留 9 页（含确认/键盘）。
- 烤板：`PAGE_PACK_PLACEMENTS` 定点；侧栏 (58,161)；底栏 y≈973。
- 运行时：toggle/dialog 小槽不再压扁 chip。
- 重烤：`python Angelic/tools/rebuild_settings_1to1.py`

---

*生成用途：换对话框续作 Angelic UI 1:1。*
