@echo off
chcp 65001 >nul
echo ============================================
echo  🔧 Hermes 另一台电脑配置脚本
echo  适用于：Windows 用户 loofnn，C 盘
echo  先确保 GitHub SSH 密钥已配好
echo ============================================
echo.

:: ── 0. 检查 GitHub SSH ──
echo [0/5] 检查 GitHub SSH 连接...
ssh -T git@github.com 2>nul
if %ERRORLEVEL% NEQ 1 (
    echo   ❌ GitHub SSH 未配置，请先添加 SSH 公钥到 GitHub
    echo   然后重新运行本脚本
    pause
    exit /b
)
echo   ✅ SSH OK

:: ── 1. 克隆工作区 ──
echo [1/5] 克隆工作区到 C:\AI\hermes...
if not exist "C:\AI\hermes" (
    mkdir C:\AI\hermes
    cd /d C:\AI\hermes
    git clone git@github.com:kyanite0320-oss/hermes-workspace.git .
) else (
    cd /d C:\AI\hermes
    git pull
)
echo   ✅ 工作区就绪

:: ── 2. 注册晨报任务 ──
echo [2/5] 注册晨报计划任务...
schtasks /Create /SC ONLOGON /TN HermesMorningBrief /TR "C:\AI\hermes\morning-brief\morning-brief-startup.bat" /RL LIMITED /IT /F >nul
echo   ✅ HermesMorningBrief

:: ── 3. 注册工作区同步任务 ──
echo [3/5] 注册工作区同步计划任务...
schtasks /Create /SC ONLOGON /TN HermesWorkspacePull /TR "C:\AI\hermes\hermes-workspace-pull.bat" /RL LIMITED /IT /F >nul
echo   ✅ HermesWorkspacePull

:: ── 4. 注册灵魂拉取任务 ──
echo [4/5] 注册灵魂同步拉取任务...
schtasks /Create /SC ONLOGON /TN HermesSoulPull /TR "C:\AI\hermes\soul-pull.bat" /RL LIMITED /IT /F >nul
echo   ✅ HermesSoulPull

:: ── 5. 创建桌面快捷方式 ──
echo [5/5] 创建桌面快捷方式...
set "DESKTOP=%USERPROFILE%\Desktop"
set "WS=C:\AI\hermes"

:: 晨报
if not exist "%DESKTOP%\🌅 晨报.bat" (
    copy "%WS%\morning-brief\open-morning-brief.bat" "%DESKTOP%\🌅 晨报.bat" >nul
)
:: 工作区
if not exist "%DESKTOP%\📁 工作区.bat" (
    echo start explorer C:\AI\hermes > "%DESKTOP%\📁 工作区.bat"
)
echo   ✅ 桌面快捷方式

echo.
echo ============================================
echo  🎉 全部配置完成！
echo  下次登录时所有任务自动运行
echo  快捷方式已放到桌面：
echo    🌅 晨报   — 打开今日晨报
echo    📁 工作区  — 打开工作区文件夹
echo ============================================
pause
