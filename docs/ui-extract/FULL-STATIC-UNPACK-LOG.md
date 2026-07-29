# 天使☆嚣嚣 全量静态解包日志

> 更新：2026-07-23 21:25  
> **状态：完成（Cxdec 运行时 + 纯静态离线两条线）**  
> 安装目录无独立 `scn`/`bgm` 包；11 个 `.xp3` 均已落地

## 结论

合计 **58166** 个文件 → `D:\gamedev\Angelic\docs\ui-extract\full-static\`  
（`E:\GAL\天使☆嚣嚣\Extractor_Output` 同步 **58177**）

| 包 | 文件数 | 说明 |
|---|---:|---|
| image | 77 | UI 基包（HxV4 哈希名；补丁多在 upgrade*） |
| data | 1471 | 系统/界面 |
| fgimage | 2539 | 立绘 |
| evimage | 166 | CG |
| adult | 11077 | R18 |
| adult2 | 81 | R18 补丁（增量少） |
| adult3 | 10 | 同上 |
| upgrade | 1460 | 内容补丁 |
| upgrade2 | 33691 | 内容补丁（主量） |
| upgrade3 | 7 | 小补丁 |
| voice | 7587 | 配音（2026-07-19 补解） |

方法：`CxdecExtractorLoader` 加载游戏 cxdec 模块（运行时解密）+ `PostMessage(WM_DROPFILES)` 拖入 XP3  
文件名仍为 HxV4 哈希；路径还原用 `tools/vendor/ten_sz_hxnames/HxNames-Tenshi.lst`

## 运行记录

### 2026-07-16 23:14 — 启动剩余包

- 脚本：`tools/_run_cxdec_rest_x86.py`
- 日志：`docs/ui-extract/static-force/full-static-rest.log`
- 报告：`docs/ui-extract/static-force/full-static-rest-report.json`

### 2026-07-16 23:34 — 完成

- before=1550 → after=50589
- 产出已整理到 `docs/ui-extract/full-static/`

### 2026-07-19 16:48 — 启动 voice.xp3 Cxdec 解包

- 脚本：`tools/_run_cxdec_voice_x86.py`
- 状态：运行中…

### 2026-07-23 21:19 — 纯静态离线解包完成

- 脚本：`tools/force_static_xp3.py`（默认跳过 size 消歧，`eo_extra` 补齐；`--cx-sample`）
- 产出：`docs/ui-extract/static-offline/`（58168，相对 EO 58166 为 image/data 各 +1）
- HxNames：`tools/rename_static_offline.py` → `static-offline-named/`（57723）+ `static-offline-unmatched/`（445）
- 报告：`static-force/static-offline-report.json`、`rename-static-offline-report.json`
- 抽样：33 文件字节与 EO 全等；image Cx 抽检 `cx_params=42` / `cx_fail=1`
- 交接：`docs/ui-extract/HANDOFF-STATIC-OFFLINE.md`

与 `full-static/`（Cxdec 运行时）并存：离线路径不启游戏，靠 EO oracle 对齐。

### 2026-07-19 16:57 — voice Cxdec 结束

```json
{
  "generated_at": "2026-07-19T08:57:37.224998+00:00",
  "game": "天使☆嚣嚣 RE-BOOT (Hikari Field)",
  "scope": "voice",
  "archives": [
    "voice.xp3"
  ],
  "method": "CxdecExtractorLoader + PostMessage WM_DROPFILES",
  "before": 50589,
  "after": 58177,
  "results": [
    {
      "archive": "voice.xp3",
      "added": 7588,
      "after": 58177
    }
  ],
  "organized": {
    "copied": 58166,
    "summary": {
      "adult": {
        "files": 11077,
        "status": "ok"
      },
      "adult2": {
        "files": 81,
        "status": "ok"
      },
      "adult3": {
        "files": 10,
        "status": "ok"
      },
      "data": {
        "files": 1471,
        "status": "ok"
      },
      "evimage": {
        "files": 166,
        "status": "ok"
      },
      "fgimage": {
        "files": 2539,
        "status": "ok"
      },
      "image": {
        "files": 77,
        "status": "ok"
      },
      "upgrade": {
        "files": 1460,
        "status": "ok"
      },
      "upgrade2": {
        "files": 33691,
        "status": "ok"
      },
      "upgrade3": {
        "files": 7,
        "status": "ok"
      },
      "voice": {
        "files": 7587,
        "status": "ok"
      }
    },
    "out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\full-static"
  },
  "paths": {
    "extractor": "E:\\GAL\\天使☆嚣嚣\\Extractor_Output",
    "full_out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\full-static",
    "log": "D:\\gamedev\\Angelic\\docs\\ui-extract\\static-force\\full-static-voice.log"
  }
}
```

### 2026-07-23 20:04 — 启动剩余包 Cxdec 解包

- 脚本：`tools/_run_cxdec_ui_cn_jp_x86.py`
- 范围：`fgimage.xp3,evimage.xp3,adult.xp3,adult2.xp3,adult3.xp3,upgrade.xp3,upgrade2.xp3,upgrade3.xp3`
- 状态：运行中…

### 2026-07-23 20:13 — Cxdec 结束

```json
{
  "generated_at": "2026-07-23T12:13:21.155935+00:00",
  "game": "天使☆嚣嚣 RE-BOOT (Hikari Field)",
  "scope": "rest fg/ev/adult/upgrade",
  "archives": [
    "fgimage.xp3",
    "evimage.xp3",
    "adult.xp3",
    "adult2.xp3",
    "adult3.xp3",
    "upgrade.xp3",
    "upgrade2.xp3",
    "upgrade3.xp3"
  ],
  "excluded": [
    "voice.xp3"
  ],
  "method": "CxdecExtractorLoader + PostMessage WM_DROPFILES (CafeStella recipe)",
  "before": 58177,
  "after": 58177,
  "results": [
    {
      "archive": "fgimage.xp3",
      "skipped": true,
      "files": 2539
    },
    {
      "archive": "evimage.xp3",
      "skipped": true,
      "files": 166
    },
    {
      "archive": "adult.xp3",
      "skipped": true,
      "files": 11077
    },
    {
      "archive": "adult2.xp3",
      "skipped": true,
      "files": 81
    },
    {
      "archive": "adult3.xp3",
      "skipped": true,
      "files": 10
    },
    {
      "archive": "upgrade.xp3",
      "skipped": true,
      "files": 1460
    },
    {
      "archive": "upgrade2.xp3",
      "skipped": true,
      "files": 33691
    },
    {
      "archive": "upgrade3.xp3",
      "skipped": true,
      "files": 7
    }
  ],
  "organized": {
    "copied": 58166,
    "summary": {
      "adult": {
        "files": 11077,
        "status": "ok"
      },
      "adult2": {
        "files": 81,
        "status": "ok"
      },
      "adult3": {
        "files": 10,
        "status": "ok"
      },
      "data": {
        "files": 1471,
        "status": "ok"
      },
      "evimage": {
        "files": 166,
        "status": "ok"
      },
      "fgimage": {
        "files": 2539,
        "status": "ok"
      },
      "image": {
        "files": 77,
        "status": "ok"
      },
      "upgrade": {
        "files": 1460,
        "status": "ok"
      },
      "upgrade2": {
        "files": 33691,
        "status": "ok"
      },
      "upgrade3": {
        "files": 7,
        "status": "ok"
      },
      "voice": {
        "files": 7587,
        "status": "ok"
      }
    },
    "out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\full-static"
  },
  "paths": {
    "extractor": "E:\\GAL\\天使☆嚣嚣\\Extractor_Output",
    "mirror": "D:\\gamedev\\Angelic\\docs\\ui-extract\\static-force\\Extractor_Output",
    "full_out": "D:\\gamedev\\Angelic\\docs\\ui-extract\\full-static",
    "log": "D:\\gamedev\\Angelic\\docs\\ui-extract\\static-force\\full-static-rest.log"
  }
}
```
