@echo off
chcp 65001 >nul
cd /d %~dp0
echo 正在启动「生物医药晨报」收藏同步服务...
echo 启动后，用浏览器打开： http://127.0.0.1:8000/index.html
echo 同一局域网内的其他设备，把 127.0.0.1 换成这台电脑的 IP 即可（收藏自动跨设备同步）。
echo 如需公网访问并加密码，请先设置环境变量 FAV_TOKEN 再运行本脚本。
echo.
python pharma_server.py 8000
pause
