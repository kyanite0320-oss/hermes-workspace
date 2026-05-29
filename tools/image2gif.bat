@echo off
setlocal enabledelayedexpansion

REM ============================================
REM  Image2GIF — 图片文件夹拖拽转GIF
REM  用法：把图片文件夹拖到此bat文件上
REM  帧间隔默认0.1秒，可编辑下面 fps 值
REM ============================================

if "%~1"=="" (
    echo [用法] 把图片文件夹拖到本bat上即可生成GIF
    pause
    exit /b 1
)

set "input_dir=%~1"
if not exist "%input_dir%" (
    echo [错误] 文件夹不存在: %input_dir%
    pause
    exit /b 1
)

echo 输入文件夹: %input_dir%

REM 手动转成 WSL 路径: C:\path\to\folder → /mnt/c/path/to/folder
set "drive=%input_dir:~0,1%"
for %%d in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
    if /i "%drive%"=="%%d" set "drive=%%d"
)
set "remain=%input_dir:~2%"
set "remain=%remain:\=/%"
set "wsl_dir=/mnt/%drive%/%remain:~1%"

echo WSL路径: %wsl_dir%
echo 正在通过 WSL 调用 FFmpeg...
echo.

REM 调用 WSL 侧的处理脚本
wsl bash /mnt/c/AI/hermes/tools/image2gif.sh "%wsl_dir%"

if errorlevel 1 (
    echo.
    echo [失败] 处理出错。常见原因：
    echo   - 文件夹中没有图片
    echo   - WSL 未安装或未初始化
    echo   - FFmpeg 未在 WSL 中安装
)

echo.
pause
