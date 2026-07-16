# 天使☆嚣嚣 全量静态解包日志（除剧本/音乐/配音）

> 更新：2026-07-16 23:34  
> **状态：完成**  
> 排除：`voice.xp3`（配音）；无独立 `scn`/`bgm` 包

## 结论

合计约 **50589** 个文件 → `D:\gamedev\Angelic\docs\ui-extract\full-static\`

| 包 | 文件数 | 说明 |
|---|---:|---|
| image | 77 | UI（此前已解） |
| data | 1471 | 系统/界面（此前已解） |
| fgimage | 2539 | 立绘 |
| evimage | 166 | CG |
| adult | 11077 | R18 |
| adult2 | 81 | R18 补丁（新增文件少，多为覆盖） |
| adult3 | 10 | 同上 |
| upgrade | 1460 | 内容补丁 |
| upgrade2 | 33691 | 内容补丁（主量） |
| upgrade3 | 7 | 小补丁 |
| voice | — | **未解（配音）** |

方法：CxdecExtractorLoader + `PostMessage(WM_DROPFILES)`

## 运行记录

### 2026-07-16 23:14 — 启动剩余包

- 脚本：`tools/_run_cxdec_rest_x86.py`
- 日志：`docs/ui-extract/static-force/full-static-rest.log`
- 报告：`docs/ui-extract/static-force/full-static-rest-report.json`

### 2026-07-16 23:34 — 完成

- before=1550 → after=50589
- 产出已整理到 `docs/ui-extract/full-static/`
