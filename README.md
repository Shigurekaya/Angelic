# angelic-extract

《天使☆嚣嚣 RE-BOOT!》（Hikari Field 官方中文）中日界面静态解包 + Ren'Py 复刻工具。

## 范围

界面 UI 为主。配音不解；剧情/立绘/CG 原图按需从 full-static 接线。

## 解包

```powershell
cd D:\gamedev\Angelic
uv sync
uv run python tools/index_xp3.py
D:\gamedev\CafeStella\tools\vendor\python311-x86\python.exe -u tools\_run_cxdec_ui_cn_jp_x86.py
uv run python tools/finalize_ui_cn_jp.py
# 全量（除 voice）：
D:\gamedev\CafeStella\tools\vendor\python311-x86\python.exe -u tools\_run_cxdec_rest_x86.py
```

## 1:1 烘焙 → renpy-angelic

标题按 **renpy-cafe 同款方法**：只用解包 `title_bg*` / `title_logo_cn` / `*_pack` 切片叠层，**禁止截图抠图**。

```powershell
.venv\Scripts\python.exe tools\build_title_1to1.py
.venv\Scripts\python.exe tools\build_other_screens_1to1.py
.venv\Scripts\python.exe tools\wire_cg_runtime.py
.venv\Scripts\python.exe tools\sync_all_ui_to_renpy.py
```

可运行工程：`D:\gamedev\renpy-angelic`（双击启动游戏.bat）。

## 产出

| 路径 | 内容 |
|------|------|
| `docs/ui-extract/full-static/` | Cxdec 全量静态 |
| `docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/` | 中日界面筛选 |
| `docs/ui-extract/pixel-reverse/` | PBD 热区 + TLG PNG |
| `ui-preview/` | HTML 预览 |
| `../renpy-angelic/` | Ren'Py 可运行 UI |
