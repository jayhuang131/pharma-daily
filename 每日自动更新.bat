@echo off
chcp 65001 >nul
title 生物医药晨报 · 自动更新
cd /d %~dp0

echo ========================================
echo   生物医药晨报 自动更新流水线
echo   %date% %time%
echo ========================================
echo.

:: 使用 PAT 做 git 鉴权（替换成你自己的 token）
:: git remote set-url origin https://YOUR_TOKEN@github.com/jayhuang131/pharma-daily.git

echo [1/3] 抓取所有渠道...
C:\Users\zijia\.workbuddy\binaries\python\versions\3.13.12\python.exe auto_build.py
echo.

echo 完成！pharmadaily.cloud 已更新。
