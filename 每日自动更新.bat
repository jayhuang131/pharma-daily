@echo off
chcp 65001 >nul
title 生物医药晨报 · 自动更新
cd /d %~dp0

:: 计划任务里也能找到 git，并让抓取走本机代理
set "PATH=C:\Users\zijia\.workbuddy\vendor\PortableGit\cmd;%PATH%"
set "HTTP_PROXY=http://127.0.0.1:10808"
set "HTTPS_PROXY=http://127.0.0.1:10808"

:: 日志（追加写；*.log 已被 .gitignore 排除，不会提交）
set "LOG=%~dp0auto_run.log"
echo. >> "%LOG%"
echo ======================================== >> "%LOG%"
echo 生物医药晨报 自动更新  %date% %time% >> "%LOG%"
echo ======================================== >> "%LOG%"

:: 运行流水线，全部输出写入日志
C:\Users\zijia\.workbuddy\binaries\python\versions\3.13.12\python.exe auto_build.py >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"

echo. >> "%LOG%"
echo 退出码 %RC%  结束时间 %date% %time% >> "%LOG%"
echo 完成（退出码 %RC%），日志：auto_run.log
