# Angelic 完全复刻 — 进程记录（停手点）

> **停手时间：** 2026-07-24 23:09 +0800  
> **明天从这里继续。**  
> 原版：`E:\GAL\天使☆嚣嚣`  
> 解包：`D:\gamedev\Angelic`  
> 复刻：`D:\gamedev\renpy-angelic`

---

## 一句话

设定页已摸到 **Cafe 同款正确路径**：`pbd2json` 的 **`uistates.storage + cx/cy/w/h`** 从官方 atlas 裁切叠层。  
新烤板 `_qa_tab0_official.png` **肉眼已接近原版**（双钮/滑条翼标球/页签/底栏），但 runtime 叠层与高级页槽位尚未收干净。

---

## 关键突破（务必记住）

| Cafe | Angelic |
|------|---------|
| FreeMote PSB `left/top` + layer PNG | **`pbd2json` `x/y` + `uistates.{off,on,…}.cx/cy/w/h` + `storage`** |

示例（`fullscreen_off`）：

```text
storage = option__pack
off:  cx=106 cy=0   w=380 h=50   ← 角括号框（未选）
on:   cx=106 cy=50  w=380 h=50   ← 实心蓝条（选中）
over: cx=106 cy=100 w=380 h=50
贴到画面: left=130 top=188
```

- Atlas：`docs/ui-extract/pixel-reverse/tlg-png/option__pack.png`（约 527×830）  
- **禁止**再靠 matchTemplate / 整包 atlas 堆中央（那是旧烂板根因）  
- `label_*` 等 `storage=""` → 引擎描字（现用微软雅黑临时代替；真·CN 可能在未解出的 `option_locale` import）

---

## 已完成

1. XP3 静态解包 ✅（见 `HANDOFF-STATIC-OFFLINE.md`）  
2. 53/53 PBD → `pbd2json-layers/` ✅  
3. 标题：pbd2json 热区 + mtn 入场层；`build_title` 不再 rmtree 删 layers ✅  
4. 设定崩溃修复 ✅  
   - `color_win` 等存 HSV **list**，UI 类型必须是 **`color_target`**（不能 `int(list)`）  
   - `angelic_int_value()` 防护  
   - 色盘：`chrome/colorpicker/`（暂借 Cafe 环图；PBD `hsv` @ 1492,187）  
5. **新烤板脚本（主路径）**  
   - `Angelic/tools/bake_settings_from_pbd_uistates.py`  
   - 产物：`ui-preview/assets/settings/plates/tab_*.png` → 已 sync 到 `renpy-angelic/.../settings/`  
   - QA 图：`Angelic/tools/_qa_tab0_official.png`

---

## 未完成 / 明天优先

### P0 — 设定 runtime 与烤板对齐

1. **开关语义**（已确认）  
   - 选中 = **实心蓝**（cy=50 / uistate `on`）+ 白字  
   - 未选 = **角括号框**（cy=0 / uistate `off`）  
   - 修正 `export_chip_chrome` / `angelic_screens.rpy` 里 chip_on/off 与文字颜色（勿反）  
2. **避免双重绘制**  
   - 烤板已含双钮+轨+翼标球；runtime 若再 `Transform` 错尺寸芯片会「发糊/错位」  
   - 建议：交互用官方 380×50 裁片覆盖同坐标，或透明热区 + 按值重贴  
3. **页签**  
   - `page0..page9` 在 PBD 里多为 `storage=""`（纯热区）；顶栏字/点来自 **`&GetUIImport("option_locale")`**  
   - **明天要解/找 `option_locale`**（当前 filtered-cn-jp 里没有同名文件）  
4. **底栏**  
   - `reset/title/back` 为 copy 空 uistate；装饰钮是 **`_sysbtn`**（有 on/over/off）  
   - 勿把「结束游戏」和「游戏画面」搞混  
5. **高级页 interaction_slots**  
   - 新脚本对 tab1+ 槽位收集不完整（板有图、槽位少）→ 按各页 PBD 按钮/滑条自动生成槽位  

### P1 — 其它屏 1:1

- 读档/CG/流程图：热区已接，烤板精细度仍差  
- 色盘环图改为 Angelic 原片（勿长期借 Cafe）  

### P2 — 非本轮

- 剧情 scn / 语音 / 立绘差分运行时  

---

## 明天一键续跑

```bat
cd /d D:\gamedev\Angelic
python tools\bake_settings_from_pbd_uistates.py
REM 然后修 angelic_screens 开关 on/off 语义 + 去双重绘制
D:\gamedev\renpy-8.5.3-sdk\renpy.exe D:\gamedev\renpy-angelic
```

对照 QA：

- 新：`Angelic/tools/_qa_tab0_official.png`（应对齐原版观感）  
- 旧烂板：atlas 堆中央（已废弃路径）

---

## 关键文件

| 路径 | 作用 |
|------|------|
| `tools/bake_settings_from_pbd_uistates.py` | **设定主烤（明天继续改这个）** |
| `tools/rebuild_settings_1to1.py` | 旧烤板（启发式/描字），勿再当几何真值 |
| `tools/recreate_renpy_ui.py` | 总复刻流水线（应改为先调 uistates 烤板） |
| `renpy-angelic/game/angelic_screens.rpy` | runtime；`angelic_int_value` / `color_target` 已有 |
| `renpy-angelic/game/images/angelic/settings/` | 当前 sync 目标 |
| `docs/ui-extract/HANDOFF-COMPLETE-RECREATE.md` | 总览 |
| `docs/ui-extract/HANDOFF-FULL-UI-UNPACK.md` | UI 解包 |
| 本文 `HANDOFF-PROGRESS-2026-07-24.md` | **今日停手进程** |

---

## 不要做

- 不要再用 `slice_placements.json` 的 cv 匹配往画面中央堆 pack  
- 不要对 `color_win` 等做 `int(values[key])`  
- 不要 `build_title_1to1` rmtree 标题目录（已改 merge-copy；勿回退）  
- 不要把 Cafe 841/637 几何泄漏进 Angelic  

---

## 用户诉求备忘

> 「完全修复，差距还是很大」→ 已用 uistates 裁切拉近视觉；明天收 runtime + locale 字模后应再上一大截。  
> 「完全复刻 @Angelic @原版」→ UI 壳优先；剧情另线。
