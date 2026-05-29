# Create Hermes Gateway auto-start task (Windows Scheduled Task)
# Gateway is already installed as systemd user service -- just need WSL to start

$taskName = "HermesGatewayStartup"

$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Task '$taskName' already exists, updating..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

$action = New-ScheduledTaskAction `
    -Execute "wsl.exe" `
    -Argument "-u kyanite systemctl --user start hermes-gateway"

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Force

Write-Host "Task '$taskName' registered successfully!"
Write-Host ""
Write-Host "How it works: Windows login -> WSL starts -> systemd -> hermes-gateway.service (enabled) auto-starts"
