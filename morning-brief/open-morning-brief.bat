@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 获取脚本所在目录，自动适配 C:\ 或 F:\
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for /f %%i in ('wsl wslpath -a "%SCRIPT_DIR%"') do set "WSL_DIR=%%i"
for /f %%i in ('wsl dirname "%WSL_DIR%"') do set "WSL_ROOT=%%i"

:: 启动 HTTP 服务器（如未运行）
wsl bash -c "cd '%WSL_ROOT:/=\%' && nohup python3 -m http.server 8000 > /dev/null 2>&1 &"

:: 用 Chrome 打开晨报
start chrome "http://localhost:8000/morning-brief/morning-brief.html"
