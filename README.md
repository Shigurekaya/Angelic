# angelic-extract

《天使☆嚣嚣 RE-BOOT!》（Hikari Field 官方中文）中日界面静态解包工具。

## 范围

仅 **中文 / 日文界面 UI**。排除配音、剧情、立绘 CG、adult、upgrade。

## 命令

```powershell
cd D:\gamedev\Angelic
uv sync
uv run python tools/index_xp3.py
# 32-bit：Cxdec 强解 image.xp3 + data.xp3
D:\gamedev\CafeStella\tools\vendor\python311-x86\python.exe -u tools\_run_cxdec_ui_cn_jp_x86.py
uv run python tools/finalize_ui_cn_jp.py
```

## 产出

- `docs/ui-extract/UI-CN-JP-STATIC-UNPACK-LOG.md` — 解包日志
- `docs/ui-extract/ui-cn-jp-static/filtered-cn-jp/` — 中日界面筛选结果
- `docs/ui-extract/static-force/ui-cn-jp-static.log` — 运行日志
