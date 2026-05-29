@echo off
REM Hermes WSL Keepalive - keeps WSL VM alive so systemd services (Hermes Gateway) stay running
REM Called by hermes-wsl-keepalive.vbs (hidden window) at Windows logon via scheduled task

wsl.exe -d Ubuntu -- /usr/bin/sleep infinity
