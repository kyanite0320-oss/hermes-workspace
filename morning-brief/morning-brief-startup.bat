@echo off
chcp 65001 >nul
echo [Hermes] 晨报生成中...

:: 在 WSL 中运行晨报脚本
wsl python3 /mnt/f/AI/hermes/morning-brief/morning-brief.py

:: 启动 HTTP 服务器（如未运行）
wsl bash -c "if ! lsof -i :8000 >/dev/null 2>&1; then cd /mnt/f/AI/hermes && nohup python3 -m http.server 8000 > /dev/null 2>&1 & fi"

echo [Hermes] 晨报就绪 ✓
