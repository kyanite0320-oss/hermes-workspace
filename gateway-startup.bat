@echo off
REM 开机自启 Hermes Gateway（在 WSL tmux 中后台运行）
REM 由 Windows 计划任务触发

wsl -u kyanite bash -c "
  tmux has-session -t hermes 2>/dev/null && echo 'Gateway already running in tmux' || {
    tmux new -d -s hermes 'hermes gateway run'
    echo 'Gateway started in tmux session: hermes'
  }
"
