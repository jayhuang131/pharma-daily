@echo off
chcp 65001 >nul
title Pharma Daily Auto Update
cd /d %~dp0

set "PATH=C:\Users\zijia\.workbuddy\vendor\PortableGit\cmd;%PATH%"
set "PYTHONUTF8=1"

set "PROXY=http://127.0.0.1:10808"
:: proxy health check (6s); if it fails, fall back to direct connection
curl.exe -s -o NUL --max-time 6 -x %PROXY% https://api.github.com
if errorlevel 1 (
  set "HTTP_PROXY="
  set "HTTPS_PROXY="
  git config --global --unset http.proxy >nul 2>&1
  git config --global --unset https.proxy >nul 2>&1
  echo [proxy] DOWN -> using DIRECT connection
) else (
  set "HTTP_PROXY=%PROXY%"
  set "HTTPS_PROXY=%PROXY%"
  git config --global http.proxy %PROXY% >nul 2>&1
  git config --global https.proxy %PROXY% >nul 2>&1
  echo [proxy] OK -> using PROXY
)

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
