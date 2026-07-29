# Angelic 全量 UI 解包 — 交接（对齐 Cafe Stella）

> 更新：2026-07-24 22:10 +0800  
> **状态：✅ UI 几何全量 pbd2json 解包完成**（53/53 PBD）

---

## 一句话

按 Cafe 流程：`pbd2json` = FreeMote `left/top` 等价物。  
全屏 UI 官方绝对坐标已进 `pbd2json-layers/` + `renpy-angelic`；pack 切片 **71 包 / 702 片**。

---

## Cafe 对照

| 步骤 | Cafe Stella | Angelic |
|------|-------------|---------|
| XP3 静态解包 | HxCrypt | `static-offline` ✅ 58168 |
| 图层坐标 | FreeMote PSB `left/top` | **`pbd2json` PBD `x/y`** ✅ 53 |
| 精灵 | PSB 图层 PNG | TLG→PNG + `__pack` 切片 ✅ |
| 烤板/同步 | `rebuild_*` / `sync_all` | 同左 ✅ |

---

## 一键重跑

```bat
cd /d D:\gamedev\Angelic
python tools\complete_ui_unpack.py
python tools\build_title_1to1.py
python tools\rebuild_settings_1to1.py
python tools\build_other_screens_1to1.py
python tools\sync_all_ui_to_renpy.py
```

分步：

```bat
python tools\unpack_pbd2json_ui.py
python tools\build_settings_from_pbd2json.py
```

工具：`CafeStella/tools/vendor/hxv4_unhash_tools/binaries/pbd2json.exe`

---

## 产物

| 路径 | 内容 |
|------|------|
| `pixel-reverse/pbd2json-layers/*.hotspots.json` | 53 屏官方热区 |
| `pixel-reverse/screen-atlas.json` | 分界面汇总 |
| `pixel-reverse/_pack_slices/` | 702 官方切片 |
| `pixel-reverse/tlg-png/` | 71 TLG→PNG |
| `pixel-reverse/FULL-UI-UNPACK-REPORT.json` | 本轮报告 |
| `settings-layout/angelic_settings_layout.json` | 设定 Cafe 式 layout |
| `renpy-angelic/game/images/angelic/**/hotspots.json` | 已接线 |

### 各屏热区数量（primary）

title 11 · settings 85 · file/load 40 · qconf 18 · hud 28 · touch 30 · cg 63 · flowchart 37 · phonechat 11 · afterstory 12 · langselect 31

### 标题底栏（title_locale_cn.pbd）

`start..exit` @ y=984 · x=88/306/525/743/962/1180/1399/1617 · 命中盒 215×96

### 设定简易页（option_0simple.pbd）

双钮 (130,188)/(550,188) 380×50；滑轨左 199 / 右 1098；底栏 y=989

---

## XP3 全量（此前已完成）

见 `HANDOFF-STATIC-OFFLINE.md`：named 57723 / unmatched 445。

---

## 仍非本轮范围

- 剧情 scn / 语音全量进 Ren'Py 播放器（Cafe 另有 scn 管线）
- 立绘差分运行时叠层（需 stand/sinfo + pbd2json 图层）
- 抓图 `_orig_capture`（几何已改信 pbd2json，不再依赖）

---

## 不要做

- 不要再用启发式扫 PBD 当坐标真值  
- 不要让 `extract_angelic_settings_from_unpack` 覆盖 interaction_slots  
- 不要把 Cafe 841/637 几何泄漏进 Angelic 烤板  
