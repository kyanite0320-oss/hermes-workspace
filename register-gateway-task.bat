@echo off
REM 注册 Hermes Gateway 开机自启（Windows 登录时启动 WSL 内 tmux gateway）
schtasks /CREATE /SC ONLOGON /TN HermesGatewayStartup /TR "wsl -u kyanite bash -c 'tmux new -d -s hermes \"hermes gateway run\"'" /RL LIMITED /F
echo Gateway startup task registered.
