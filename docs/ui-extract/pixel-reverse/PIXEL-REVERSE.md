# 天使☆嚣嚣 — 像素级 UI 反推（对齐 Cafe Stella）

> 更新：2026-07-24

## 方法（对照 Cafe）

| 步骤 | Cafe Stella | Angelic |
|------|-------------|---------|
| 1. 静态解包 | HxCrypt / XP3 | `static-offline` + HxNames |
| 2. 图层几何 | FreeMote `PsbDecompile` → PSB `left/top/width/height` | **`pbd2json.exe`** → PBD `x/y/width/height` |
| 3. 烤板 | `build_settings_plates.py` / `rebuild_settings_1to1.py` 读 PSB | `build_settings_from_pbd2json.py` + `rebuild_settings_1to1.py` |
| 4. 同步 | `sync_all_ui_to_renpy.py` | rebuild 末尾 sync → `renpy-angelic` |

**结论：** Angelic 界面几何在 **PBD**（经官方 `pbd2json`），不是启发式扫描，也不是截图估点。  
FreeMote **不吃** Angelic PBD；等价工具是 Cafe 同款 vendor 里的 `pbd2json.exe`。

## 重跑

```bat
cd /d D:\gamedev\Angelic
python tools\unpack_pbd2json_ui.py
python tools\build_settings_from_pbd2json.py
python tools\rebuild_settings_1to1.py
```

或一键：`python tools\unpack_official_bare_pixels.py` 后 `rebuild_settings_1to1.py`。

## 产物

| 路径 | 说明 |
|------|------|
| `pixel-reverse/pbd2json-layers/*.hotspots.json` | 每屏官方绝对坐标（left=x, top=y） |
| `pixel-reverse/pbd2json-layers/manifest.json` | 53 PBD 汇总 |
| `settings-layout/angelic_settings_layout.json` | Cafe 式 tabs/rows |
| `settings-layout/official_bare_pixels.json` | 同上汇总 |
| `tlg-png/` + `_pack_slices/` | 官方精灵 |

## 简易页官方坐标（option_0simple.pbd）

- 双钮开关：`fullscreen_off/on` @ (130,188)/(550,188) · 380×50
- 行标签 y：137 / 303 / 469 / 635 / 801
- 滑轨：左 textspeed @ (199,518)；右 wave @ (1098,187) · 区 620×54
- 静音：@ (1021, y) · 54×54
- 底栏：reset/title/back @ y=989 · x=923/1252/1581
