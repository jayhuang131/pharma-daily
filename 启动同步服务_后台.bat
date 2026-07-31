@echo off
chcp 65001 >nul
cd /d %~dp0
:: 用 pythonw 后台无窗口启动同步服务（适合常开电脑 / 开机自启）
start "" pythonw pharma_server.py 8000
echo 同步服务已在后台启动（无窗口）。日志在同目录 server.log。
pause
