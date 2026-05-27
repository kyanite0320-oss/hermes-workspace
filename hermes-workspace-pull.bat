@echo off
chcp 65001 >nul
echo [Hermes] 同步工作区...

:: 拉取最新代码
cd /d F:\AI\hermes
wsl bash -c "cd /mnt/f/AI/hermes && git pull origin main 2>&1"

echo [Hermes] 工作区已更新 ✓
