@echo off
chcp 65001 >nul
title 生物医药晨报 - 同步隧道
cd /d %~dp0

echo.
echo ========================================
echo   生物医药晨报 · 收藏同步隧道
echo ========================================
echo.

:: 1. 如果 cloudflared 没装，自动下载
if not exist cloudflared.exe (
    echo [1/3] 下载 cloudflared...
    curl -Lo cloudflared.exe https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    if not exist cloudflared.exe (
        echo [错误] 下载失败，请检查网络后重试。
        pause
        exit /b 1
    )
) else (
    echo [1/3] cloudflared 已存在，跳过下载。
)

:: 2. 确保同步服务在跑
echo [2/3] 检查同步服务...
netstat -ano | findstr ":8000.*LISTENING" >nul
if errorlevel 1 (
    echo 同步服务未启动，正在启动...
    start "" pythonw pharma_server.py 8000
    timeout /t 3 /nobreak >nul
)

:: 3. 启动隧道
echo [3/3] 启动公网隧道...
echo.
echo ========================================
echo   隧道已启动！以下是公网地址：
echo ========================================
echo.

cloudflared.exe tunnel --url http://localhost:8000

pause
