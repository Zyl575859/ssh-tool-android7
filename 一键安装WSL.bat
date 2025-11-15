@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title 一键安装 WSL

echo.
echo ========================================
echo   一键安装 WSL (Windows子系统)
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 需要管理员权限
    echo.
    echo 请以管理员身份运行此脚本：
    echo   1. 右键点击此文件
    echo   2. 选择"以管理员身份运行"
    echo.
    pause
    exit /b 1
)

REM 检查是否已安装
wsl --list >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] WSL 已安装
    wsl --list
    echo.
    echo WSL已就绪，可以直接构建APK
    pause
    exit /b 0
)

echo [安装] 正在安装WSL...
echo [提示] 这可能需要几分钟，请耐心等待...
echo.

wsl --install

if %errorlevel% == 0 (
    echo.
    echo [OK] WSL 安装命令已执行
    echo.
    echo [重要] 需要重启电脑才能完成安装
    echo.
    set /p restart="是否现在重启电脑？(Y/N): "
    if /i "%restart%"=="Y" (
        echo.
        echo 系统将在10秒后重启...
        shutdown /r /t 10 /c "WSL安装完成，系统将在10秒后重启"
        timeout /t 10
    ) else (
        echo.
        echo 请手动重启电脑，然后运行: 构建APK.bat
    )
) else (
    echo.
    echo [错误] WSL 安装失败
    echo.
    echo 请检查：
    echo   1. 是否以管理员身份运行
    echo   2. 是否启用了虚拟化功能
    echo.
)

pause




