@echo off
chcp 65001 >nul
echo [Hermes] 同步工作区...

:: 获取脚本所在目录（自动适配 C:\ 或 F:\）
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for /f %%i in ('wsl wslpath -a "%SCRIPT_DIR%"') do set "WSL_DIR=%%i"

:: Git 拉取
wsl bash -c "cd '%WSL_DIR:/=\%' && git pull origin main 2>&1"

echo [Hermes] 工作区已更新 ✓
