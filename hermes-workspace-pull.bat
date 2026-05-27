@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo [Hermes] 同步工作区...

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for /f %%i in ('wsl wslpath -a "%SCRIPT_DIR%"') do set "WSL_DIR=%%i"

:: 获取电脑名（取用户名最后部分）
for /f %%i in ('whoami') do set "USERNAME=%%i"
set "PC_NAME=%USERNAME:*\=%-PC"

:: 获取当前时间
for /f "tokens=1-3 delims=: " %%a in ("%TIME%") do set "HH=%%a" & set "MM=%%b"
set "NOW=%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2% %HH%:%MM%"

:: Git 拉取
wsl bash -c "cd '%WSL_DIR:/=\%' && git pull origin main 2>&1"
set "PULL_RESULT=%ERRORLEVEL%"

if %PULL_RESULT% EQU 0 (
    echo [Hermes] 工作区已更新 ✓
    wsl hermes send -t "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a" "%NOW% | %PC_NAME% | 工作区拉取 | ✅ 成功" 2>nul
) else (
    echo [Hermes] 拉取失败
    wsl hermes send -t "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a" "%NOW% | %PC_NAME% | 工作区拉取 | ❌ 失败" 2>nul
)
