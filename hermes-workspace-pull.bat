@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo [Hermes] 同步工作区...

set "PC_NAME=%USERNAME%"

for /f "tokens=1-3 delims=: " %%a in ("%TIME%") do set "HH=%%a" & set "MM=%%b"
set "NOW=%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2% %HH%:%MM%"

:: 进入工作区目录并拉取
cd /d F:\AI\hermes
git pull --rebase origin main 2>&1
set "PULL_RESULT=%ERRORLEVEL%"

if %PULL_RESULT% EQU 0 (
    echo [Hermes] 工作区已更新 ✓
    wsl hermes send -t "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a" "%NOW% | %PC_NAME% | 工作区拉取 | ✅ 成功" 2>nul
) else (
    echo [Hermes] 拉取失败
    wsl hermes send -t "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a" "%NOW% | %PC_NAME% | 工作区拉取 | ❌ 失败" 2>nul
)
