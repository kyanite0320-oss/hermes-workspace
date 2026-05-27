@echo off
chcp 65001 >nul
echo [Hermes] 灵魂同步拉取中...

:: 获取脚本所在目录（C:\AI\hermes）
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for /f %%i in ('wsl wslpath -a "%SCRIPT_DIR%"') do set "WSL_DIR=%%i"

:: 拉取灵魂数据
wsl bash -c "cd '%WSL_DIR:/=\%' && git pull origin main 2>&1"

:: 还原到 Hermes 记忆目录
wsl bash -c "
  cp ~/hermes-data/MEMORY.md ~/.hermes/memories/
  cp ~/hermes-data/USER.md ~/.hermes/memories/
  rsync -a --delete ~/hermes-data/skills/ ~/.hermes/skills/
  echo '灵魂同步完成'
"

echo [Hermes] 灵魂已同步 ✓
