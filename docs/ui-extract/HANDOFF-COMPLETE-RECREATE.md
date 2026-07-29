# Angelic 完全复刻 — 现状交接

> 更新：2026-07-29  
> 原版：`E:\GAL\天使☆嚣嚣`  
> 解包：`D:\gamedev\Angelic`  
> 复刻：`D:\gamedev\renpy-angelic`

---

## 目标

按 Cafe 同款路径，用**官方解包素材 + pbd2json uistates**在 Ren'Py 复刻 UI（除去剧情 scn/语音播放器）。

---

## 设定权威脚本（硬约束）

| 角色 | 脚本 |
|------|------|
| **设定主烤** | `tools/bake_settings_from_pbd_uistates.py` |
| 总流水线 | `tools/recreate_renpy_ui.py`（已改为调用上者） |
| **废弃进线** | `tools/rebuild_settings_1to1.py`（勿再跑；会盖成空标签板） |
| 其它屏 | `tools/build_other_screens_1to1.py`（**不再**烤/覆盖 settings） |

Keep-set 页：`0,1,2,3,4,5a,5b,6,8`（无鼠标 7 / 手柄 9）。

---

## 已完成

| 层 | 状态 |
|----|------|
| XP3 静态解包 | ✅ |
| UI 几何 pbd2json | ✅ |
| Pack 切片 | ✅ `_pack_slices` |
| 标题入场 + 底栏 | ✅ layers + pbd2json 热区 |
| 设定烤板 | ✅ uistates 裁切叠层（双钮/滑条/翼标） |
| Runtime | ✅ 官方芯片原尺寸覆盖；tab0 吃 interaction_slots |
| 同步 | ✅ `images/angelic/settings/` |
| 自检 | `tools/_audit_settings_selfcheck.py`（按 keep-set） |

### 启动

```bat
D:\gamedev\renpy-8.5.3-sdk\renpy.exe D:\gamedev\renpy-angelic
```

或 `renpy-angelic\启动游戏.bat`。改资源后请**完全退出再开**。

### 一键重烤

```bat
cd /d D:\gamedev\Angelic
.venv\Scripts\python.exe tools\recreate_renpy_ui.py
```

仅重烤设定：

```bat
.venv\Scripts\python.exe tools\bake_settings_from_pbd_uistates.py
```

QA 对照：`tools/_qa_tab0_official.png` · `tools/_compare_settings_qa.py`

---

## 对照原版仍差（下一轮）

- **设定页问题全清单（持续更新）**：[`SETTINGS-PAGE-ISSUES.md`](./SETTINGS-PAGE-ISSUES.md)（同步副本：`renpy-angelic/docs/SETTINGS-PAGE-ISSUES.md`）
- 设定高级页部分 CN 字模仍为系统字体描字（`option_locale` 未解出）
- 读档/CG/流程图板面精细度可再对照原版抓帧
- 色盘环图可换 Angelic 原片
- 剧情 scn / 语音 / 立绘差分运行时 — **未接**

---

## 硬约束

- 坐标只信 **pbd2json** `x/y` + `uistates.storage/cx/cy/w/h`
- 禁止 `make_chip` / atlas 整包堆到画面中央
- `color_win` 等存 HSV list，UI 类型必须是 `color_target`
- `build_title_1to1` 不得 `rmtree` 标题 `layers/`
