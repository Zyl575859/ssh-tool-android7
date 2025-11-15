@echo off
chcp 65001 >nul 2>&1
cls
title SSH工具 - 构建Android APK

echo.
echo ========================================
echo   SSH工具 - Android APK 构建
echo ========================================
echo.
echo [推荐] 使用GitHub Actions在线构建（最简单）
echo   详见: 构建APK_在线构建.md
echo.
echo ========================================
echo.

REM 检查是否在Git仓库中
git status >nul 2>&1
if %errorlevel% == 0 (
    echo [检测] 当前目录是Git仓库
    echo.
    echo [选项1] 推送到GitHub并在线构建（推荐）
    echo   1. git add .
    echo   2. git commit -m "更新"
    echo   3. git push
    echo   4. 在GitHub Actions中查看构建进度
    echo.
    echo [选项2] 本地构建（需要Docker或WSL）
    set /p choice="选择 (1=在线构建, 2=本地构建, 其他=退出): "
    if "!choice!"=="1" (
        echo.
        echo [提示] 请按照 构建APK_在线构建.md 的说明操作
        echo.
        pause
        exit /b 0
    )
    if "!choice!"=="2" (
        goto :local_build
    )
    exit /b 0
) else (
    echo [提示] 当前目录不是Git仓库
    echo.
    echo [推荐] 使用GitHub Actions在线构建：
    echo   1. 创建GitHub仓库
    echo   2. 初始化Git: git init
    echo   3. 上传代码: git add . ^&^& git commit -m "初始" ^&^& git push
    echo   4. 在GitHub Actions中构建
    echo.
    echo 详细说明: 构建APK_在线构建.md
    echo.
    set /p choice="是否继续本地构建? (Y/n): "
    if /i not "!choice!"=="n" (
        goto :local_build
    )
    exit /b 0
)

:local_build
echo.
echo ========================================
echo   本地构建（需要Docker或WSL）
echo ========================================
echo.

REM 检查Docker
where docker >nul 2>&1
if %errorlevel% == 0 (
    echo [检测] Docker已安装
    docker ps >nul 2>&1
    if %errorlevel% == 0 (
        echo [OK] Docker正在运行
        echo.
        echo [构建] 使用Docker构建...
        docker run --rm --volume "%CD%:/home/user/hostcwd" kivy/buildozer buildozer android debug
        if %errorlevel% == 0 (
            echo.
            echo [成功] 构建完成！APK在 bin/ 目录
            pause
            exit /b 0
        )
    ) else (
        echo [提示] Docker未运行，请先启动Docker Desktop
    )
)

REM 检查WSL
wsl --list >nul 2>&1
if %errorlevel% == 0 (
    echo [检测] WSL已安装
    echo.
    echo [构建] 使用WSL构建...
    wsl bash -c "cd /mnt/c/Users/Lenovo/Desktop/999999999 && export PATH=\$PATH:~/.local/bin && buildozer android debug"
    if %errorlevel% == 0 (
        echo.
        echo [成功] 构建完成！APK在 bin/ 目录
        pause
        exit /b 0
    )
)

echo.
echo [错误] 未找到构建环境
echo.
echo 推荐使用GitHub Actions在线构建（最简单）：
echo   详见: 构建APK_在线构建.md
echo.
pause
exit /b 1
