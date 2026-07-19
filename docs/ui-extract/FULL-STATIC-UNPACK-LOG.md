# 天使☆嚣嚣 全量静态解包日志

> 更新：2026-07-19 16:57  
> **状态：完成（全部 XP3，含 voice）**  
> 安装目录无独立 `scn`/`bgm` 包；11 个 `.xp3` 均已 Cxdec 解密落地

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
