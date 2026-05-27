@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo [Hermes] 晨报生成中...

:: 获取脚本所在目录（自动适配 C:\ 或 F:\）
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: 转成 WSL 路径
for /f %%i in ('wsl wslpath -a "%SCRIPT_DIR%"') do set "WSL_DIR=%%i"

:: 运行晨报脚本
wsl python3 "%WSL_DIR%/morning-brief.py"

:: 获取上级目录（HTTP 服务器根目录）
for /f %%i in ('wsl dirname "%WSL_DIR%"') do set "WSL_ROOT=%%i"

:: 启动 HTTP 服务器（如未运行）
wsl bash -c "if ! lsof -i :8000 >/dev/null 2>&1; then cd '%WSL_ROOT:/=\%' && nohup python3 -m http.server 8000 > /dev/null 2>&1 & fi"

echo [Hermes] 晨报就绪 ✓
