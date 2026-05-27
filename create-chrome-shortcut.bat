@echo off
chcp 65001 >nul
echo [Hermes] 创建调试版 Chrome 快捷方式...

:: 桌面路径
set "DESKTOP=%USERPROFILE%\Desktop"
set "CHROME=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
set "SHORTCUT=%DESKTOP%\hermes.lnk"

:: 用 PowerShell 创建快捷方式
powershell -Command "
$ws = New-Object -ComObject WScript.Shell;
$sc = $ws.CreateShortcut('%SHORTCUT%');
$sc.TargetPath = '%CHROME%';
$sc.Arguments = '--remote-debugging-port=9222 --user-data-dir=c:\chrome-hermes-profile --remote-allow-origins=*';
$sc.IconLocation = '%CHROME%,0';
$sc.Description = 'Hermes Chrome - 远程调试模式';
$sc.Save();
Write-Output '快捷方式已创建: %SHORTCUT%'
"

echo [Hermes] 完成！桌面已有 hermes.lnk
pause
