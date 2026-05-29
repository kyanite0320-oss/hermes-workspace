@echo off
REM 开机启动 Hermes Gateway：启动 WSL，systemd 会自动拉起 gateway 服务
wsl -u kyanite systemctl --user start hermes-gateway
