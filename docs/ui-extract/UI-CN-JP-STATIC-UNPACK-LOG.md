# 天使☆嚣嚣 RE-BOOT 中日界面静态解包日志

> 更新：2026-07-16  
> 范围：**仅中文 / 日文界面 UI**（不含剧情、音乐、配音、立绘、CG、adult、upgrade）

## 结论（进行中）

对照 CafeStella 已跑通的路径：`CxdecExtractorLoader` + **PostMessage(WM_DROPFILES)**。  
本工程先做静态索引 / HxNames 准备；CafeStella 中日解包完成后启动本游戏 Cxdec。

## 环境

| 项 | 值 |
|---|---|
| 游戏目录 | `E:\GAL\天使☆嚣嚣` |
| 可执行文件 | `tenshi_sz.exe`（Hikari Field / 官方中文） |
| 加密 | Wamsoft Hxv4 / Cxdec |
| 解包工具 | CxdecExtractorLoader（自 CafeStella vendor 复制） |
| HxNames | `tools/vendor/ten_sz_hxnames/HxNames-Tenshi.lst` |
| 工程 | `D:\gamedev\Angelic` |
| uv | `.venv`（tamagoarc / pillow / pefile） |

## 本次解包范围

### 包含
- `image.xp3` — UI 图像主包（对应 CafeStella `uipsd` 角色）
- `data.xp3` — 系统/界面脚本与中日文案（无独立 `main`/`uipsd`）

### 明确排除
- `voice.xp3`（配音）
- `fgimage.xp3` / `evimage.xp3` / `adult*.xp3`（立绘/CG）
- `upgrade*.xp3`（大型内容补丁，非纯界面）
- 筛出阶段再丢弃 `_en` / `_tw` 专属界面文件

## 产出路径

| 路径 | 说明 |
|---|---|
| `E:\GAL\天使☆嚣嚣\Extractor_Output\` | Cxdec 原始输出 |
| `docs/ui-extract/static-force/Extractor_Output/` | 镜像 |
| `docs/ui-extract/ui-cn-jp-static/` | 整理后的中日界面包 |
| `docs/ui-extract/static-force/ui-cn-jp-static.log` | 运行日志 |
| `docs/indexes/` | XP3 静态索引 |

## 复现命令

```powershell
cd D:\gamedev\Angelic
uv sync
uv run python tools/index_xp3.py
# CafeStella 解包进程结束后：
D:\gamedev\CafeStella\tools\vendor\python311-x86\python.exe -u tools\_run_cxdec_ui_cn_jp_x86.py
uv run python tools/finalize_ui_cn_jp.py
```

## 与 CafeStella 日志对照

CafeStella `UI-CN-JP-STATIC-UNPACK-LOG.md` / `ui-cn-jp-static.log` 关键经验：

1. SteamStub 需 Steamless（本游戏无 `.bind`，但有 `.adata` 段，启动失败时再处理壳）。
2. **必须 PostMessage 拖包**；SendMessage 会 0 文件。
3. 范围收窄到界面包，避免 scn/bgm/voice/立绘。

CafeStella 终态（2026-07-16 22:27）：`main` 55 + `patch` 3 + `uipsd` 155 = **216** 文件，已 DONE。

## 运行记录

### 2026-07-16 22:30 — 工程初始化

- 建立 uv 环境与 `tools/` 脚本
- 克隆 `ten_sz_hxnames`（57748 条）
- Cxdec 工具已复制到游戏目录
- 等待 / 确认 CafeStella 结束后启动本游戏解包

### 2026-07-16 22:32 — 启动 Cxdec 中日界面解包

- 脚本：`tools/_run_cxdec_ui_cn_jp_x86.py`
- 范围：`image.xp3,data.xp3`
- 状态：运行中…

### 2026-07-16 22:35 — Cxdec 结束

```json
{
  "generated_at": "2026-07-16T14:35:31.151022+00:00",
  "game": "天使☆嚣嚣 RE-BOOT (Hikari Field)",
  "scope": "CN/JP UI only",
  "archives": [
    "image.xp3",
    "data.xp3"
  ],
  "excluded": [
    "adult.xp3",
    "adult2.xp3",
    "adult3.xp3",
    "evimage.xp3",
    "fgimage.xp3",
    "upgrade.xp3",
    "upgrade2.xp3",
    "upgrade3.xp3",
    "voice.xp3"
  ],
  "method": "CxdecExtractorLoader + PostMessage WM_DROPFILES (CafeStella recipe)",
  "before": 0,
  "after": 1550,
  "results": [
    {
      "archive": "image.xp3",
      "added": 78,
      "after": 78
    },
    {
      "archive": "data.xp3",
      "added": 1472,
      "after": 1550
    }
  ],
  "organized": {
    "copied": 1548,
    "summary": {
      "image": {
        "files": 77,
        "status": "ok"
      },
      "data": {
        "files": 1471,
        "status": "ok"
      }
    },
    "out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\ui-cn-jp-static"
  },
  "paths": {
    "extractor": "E:\\GAL\\天使☆嚣嚣\\Extractor_Output",
    "mirror": "D:\\gamedev\\Angelic\\docs\\ui-extract\\static-force\\Extractor_Output",
    "ui_out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\ui-cn-jp-static",
    "log": "D:\\gamedev\\Angelic\\docs\\ui-extract\\static-force\\ui-cn-jp-static.log"
  }
}
```

### 2026-07-16 22:41 — Cxdec + HxNames 完成

- Cxdec：image.xp3 +78 / data.xp3 +1472 → 共 1550 文件
- 镜像：`docs/ui-extract/static-force/Extractor_Output/`
- HxNames 还原 1362；中日界面筛选见 finalize 报告
- 排除：voice / fgimage / evimage / adult* / upgrade* / locale en·tw / scenario

```json
{
  "generated_at": "2026-07-16T14:41:58.421036+00:00",
  "hx_entries": 57748,
  "renamed_files": 1362,
  "unmatched_skipped": 186,
  "filtered_cn_jp": 301,
  "text_previews": 45,
  "filtered_out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\ui-cn-jp-static\\filtered-cn-jp",
  "renamed_out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\ui-cn-jp-static\\renamed",
  "policy": "keep locale/jp + locale/cn + uipsd/title/option UI; drop en/tw/scenario/audio"
}
```

