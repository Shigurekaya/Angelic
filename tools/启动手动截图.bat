@echo off
chcp 65001 >nul
cd /d D:\gamedev\Angelic\tools
echo.
echo === Angelic 手动点界面 · 自动存截图 ===
echo 1. 先打开原版 tenshi_sz.exe，窗口不要最小化
echo 2. 本窗口保持运行，你去点：设定各页 / 存读档 / CG / 流程树 / 履历 / 剧情等
echo 3. 点完后回到这里按 Ctrl+C 结束
echo.
python _capture_manual_session.py
pause
