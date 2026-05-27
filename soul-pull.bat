@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
echo [Hermes] 灵魂同步拉取中...

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for /f %%i in ('wsl wslpath -a "%SCRIPT_DIR%"') do set "WSL_DIR=%%i"
set "PC_NAME=%USERNAME%"

for /f "tokens=1-3 delims=: " %%a in ("%TIME%") do set "HH=%%a" & set "MM=%%b"
set "NOW=%DATE:~0,4%-%DATE:~5,2%-%DATE:~8,2% %HH%:%MM%"

:: 拉取灵魂数据
wsl bash -c "
  set -e
  cd ~/hermes-data
  git pull origin main 2>&1
  cp MEMORY.md ~/.hermes/memories/
  cp USER.md ~/.hermes/memories/
  rsync -a --delete skills/ ~/.hermes/skills/
  echo '灵魂同步完成'
"
set "PULL_RESULT=%ERRORLEVEL%"

if %PULL_RESULT% EQU 0 (
    echo [Hermes] 灵魂已同步 ✓
    wsl hermes send -t "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a" "%NOW% | %PC_NAME% | 灵魂拉取 | ✅ 成功" 2>nul
) else (
    echo [Hermes] 拉取失败
    wsl hermes send -t "feishu:oc_85533c0c4d0542e0dbc8a2b918b7839a" "%NOW% | %PC_NAME% | 灵魂拉取 | ❌ 失败" 2>nul
)
