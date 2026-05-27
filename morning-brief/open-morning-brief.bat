@echo off
chcp 65001 >nul
:: 启动 HTTP 服务器（如未运行）
wsl bash -c "cd /mnt/f/AI/hermes && nohup python3 -m http.server 8000 > /dev/null 2>&1 &"
:: 用 Chrome 打开晨报
start chrome "http://localhost:8000/morning-brief/morning-brief.html"
