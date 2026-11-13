@echo off
chcp 65001 >nul
title Pharma Daily Auto Update
cd /d %~dp0

set "PATH=C:\Users\zijia\.workbuddy\vendor\PortableGit\cmd;%PATH%"
set "HTTP_PROXY=http://127.0.0.1:10808"
set "HTTPS_PROXY=http://127.0.0.1:10808"
set "PYTHONUTF8=1"

set "LOG=%~dp0auto_run.log"
echo. >> "%LOG%"
echo ======================================== >> "%LOG%"
echo Pharma Daily Auto Update  %date% %time% >> "%LOG%"
echo ======================================== >> "%LOG%"

C:\Users\zijia\.workbuddy\binaries\python\versions\3.13.12\python.exe auto_build.py >> "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"

echo. >> "%LOG%"
echo exit=%RC%  time=%date% %time% >> "%LOG%"
echo done, exit=%RC%
