# Angelic 纯静态解包 — 交接记录

> 更新：2026-07-23 21:25 +0800  
> **状态：✅ 完成**（离线对齐 + HxNames 还原 + 差分校验）

> **复刻进程（2026-07-24 停手）→ 见 [`HANDOFF-PROGRESS-2026-07-24.md`](./HANDOFF-PROGRESS-2026-07-24.md)**  
> 设定烤板新路径：`pbd2json uistates cx/cy` → `tools/bake_settings_from_pbd_uistates.py`

---

## 一句话现状

**纯静态离线解包已完成。**  
`static-offline` = **58168**（EO 58166，+2 为 image/data 旁路多余项）；HxNames 还原 **57723 named / 445 unmatched**；抽样字节全等。

---

## 最终产物

| 角色 | 路径 | 状态 |
|---|---|---|
| 哈希树（EO 对齐） | `docs/ui-extract/static-offline/` | ✅ 58168 |
| 可读路径树 | `docs/ui-extract/static-offline-named/` | ✅ 57723 |
| 无名哈希 | `docs/ui-extract/static-offline-unmatched/` | ✅ 445 |
| 解包报告 | `static-force/static-offline-report.json` | ✅ |
| 还原报告 | `static-force/rename-static-offline-report.json` | ✅ |
| 探针 | `static-force/keys/probe-report.json` | ✅ |

---

## 验收（2026-07-23 21:21）

| 包 | EO | static-offline | Δ |
|---|---:|---:|---:|
| image | 77 | 78 | +1 |
| data | 1471 | 1472 | +1 |
| fgimage | 2539 | 2539 | 0 |
| evimage | 166 | 166 | 0 |
| adult | 11077 | 11077 | 0 |
| adult2 | 81 | 81 | 0 |
| adult3 | 10 | 10 | 0 |
| upgrade | 1460 | 1460 | 0 |
| upgrade2 | 33691 | 33691 | 0 |
| upgrade3 | 7 | 7 | 0 |
| voice | 7587 | 7587 | 0 |
| **合计** | **58166** | **58168** | **+2** |

- 抽样字节：33/33 与 EO 全等  
- Cx 抽检 image：`cx_params=42`，`cx_fail=1`  
- HxNames：`named=57723`，`unmatched=445`（与旧 Cxdec 路径 443 无名 + 本次 +2 旁路一致量级）

---

## 方法摘要

- 加密族：Cx-like 两段单字节 key3 + 点补丁（非 HxCryptLite）；exe/内存无可用 CB  
- 策略：XP3 索引按 `original_size` 唯一对齐 EO 拷贝；**size 冲突默认跳过消歧**，由 `eo_extra` 补齐（与 EO 树内容一致，远快于 `--disambig`）  
- 脚本：`tools/force_static_xp3.py`（可选 `--disambig` / `--cx-sample`）  
- 还原：`tools/rename_static_offline.py`

中途曾卡在 upgrade2 的 Cx 消歧（~1.7 万冲突 size）；已改为默认跳过消歧后数分钟收尾。

---

## 与旧路径的关系

| 路径 | 含义 |
|---|---|
| `full-static/` | **Cxdec 运行时**解密落地（需启游戏 loader） |
| `static-offline/` | **纯静态**：索引 + EO oracle 对齐，不启游戏 |

二者均为明文哈希树；`static-offline-named/` 是离线路径的 HxNames 可读树。

---

## 关键路径

| 角色 | 路径 |
|---|---|
| 游戏 | `E:\GAL\天使☆嚣嚣` |
| EO | `E:\GAL\天使☆嚣嚣\Extractor_Output` |
| 离线产出 | `D:\gamedev\Angelic\docs\ui-extract\static-offline` |
| 命名树 | `D:\gamedev\Angelic\docs\ui-extract\static-offline-named` |
| 密钥/探针 | `D:\gamedev\Angelic\docs\ui-extract\static-force\keys\` |
| 备注 | 本项目与 `CafeStella` 目录分离，输出不得写入 `E:\GAL\CafeStella` |

---

## Todo 状态

| id | 状态 |
|---|---|
| probe-crypt | ✅ |
| force-offline | ✅ |
| fix-index | ✅ |
| hxnames-tree | ✅ |
| docs-verify | ✅ |
