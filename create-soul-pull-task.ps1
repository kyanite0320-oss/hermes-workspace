# 创建 HermesSoulPull Windows 登录任务
$TaskName = "HermesSoulPull"
$WslExe = "C:\Windows\System32\wsl.exe"

# 构建 wsl 命令
$Action = New-ScheduledTaskAction -Execute $WslExe -Argument "-u administrator bash -c 'cd /home/administrator && bash ~/.hermes/scripts/soul-pull.sh'"

# 登录时触发（当前用户）
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# 基本设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

# 注册任务
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Limited -Force

Write-Output "任务 '$TaskName' 创建成功"
