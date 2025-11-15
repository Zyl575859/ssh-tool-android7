@echo off
REM 确保错误不会导致脚本静默退出
setlocal enabledelayedexpansion

REM 设置编码
chcp 65001 >nul 2>&1

REM 清屏并设置标题
cls
title SSH工具 - Android APK 一键构建

REM 添加错误处理：捕获所有错误
set "BUILD_RESULT=1"
set "SCRIPT_ERROR=0"

echo.
echo ========================================
echo   SSH工具 - Android APK 一键构建
echo ========================================
echo.
echo [信息] 脚本已启动
echo [信息] 当前目录: %CD%
echo.

REM 检查当前目录
if not exist "main.py" (
    echo [错误] 未找到main.py文件
    echo 请确保在项目根目录运行此脚本
    echo.
    echo 当前目录: %CD%
    echo.
    echo 按任意键退出...
    pause >nul 2>&1
    if errorlevel 1 timeout /t 5 /nobreak >nul 2>&1
    exit /b 1
)

echo [OK] 找到main.py文件
echo.

echo [1/4] 检查构建环境...
echo.

REM 优先使用Docker
echo [检查] 正在检查Docker...
where docker >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] 检测到Docker
    echo.
    echo [1.1] 检查Docker是否运行...
    docker ps >nul 2>&1
    if %errorlevel% neq 0 (
        echo [警告] Docker未运行，尝试启动...
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe" 2>nul
        echo [等待] 等待Docker启动（20秒）...
        timeout /t 20 /nobreak >nul
        docker ps >nul 2>&1
        if %errorlevel% neq 0 (
            echo [失败] Docker无法启动，切换到WSL方案...
            goto :check_wsl
        )
    )
    echo [OK] Docker正在运行
    echo.
    echo [1.2] 验证Docker可用性...
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        echo [失败] Docker无法正常工作，切换到WSL方案...
        goto :check_wsl
    )
    echo [OK] Docker可用
    echo.
    echo [2/4] 检查Docker镜像...
    docker images kivy/buildozer --format "{{.Repository}}:{{.Tag}}" 2>nul | findstr "kivy/buildozer" >nul
    if %errorlevel% neq 0 (
        echo [2.1] 拉取Kivy镜像（首次需要，请耐心等待）...
        docker pull kivy/buildozer
        if %errorlevel% neq 0 (
            echo [失败] 拉取镜像失败，切换到WSL方案...
            goto :check_wsl
        )
    )
    echo [OK] 镜像就绪
    echo.
    echo [3/4] 开始构建APK...
    echo [提示] 首次构建需要30分钟到1小时，请耐心等待...
    echo.
    docker run --rm --volume "%CD%:/home/user/hostcwd" kivy/buildozer buildozer android debug
    set BUILD_RESULT=%errorlevel%
    if %BUILD_RESULT% neq 0 (
        echo.
        echo [失败] Docker构建失败，尝试切换到WSL方案...
        echo.
        goto :check_wsl
    )
    goto :check_result
)

:check_wsl

REM 检查WSL
echo.
echo [切换] 尝试使用WSL构建...
echo.
echo [检查] 正在检查WSL...
wsl --list >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] 检测到WSL
    echo.
    echo [2/4] 检查WSL环境...
    wsl bash -c "command -v buildozer" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [2.1] 安装Buildozer（首次需要）...
        echo [提示] 这可能需要几分钟，请耐心等待...
        wsl bash -c "sudo apt-get update -qq && sudo apt-get install -y -qq git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev > /dev/null 2>&1 && pip3 install --user buildozer > /dev/null 2>&1"
        if %errorlevel% neq 0 (
            echo [失败] Buildozer安装失败
            goto :no_env
        )
        echo [OK] Buildozer安装完成
    ) else (
        echo [OK] Buildozer已安装
    )
    echo.
    echo [3/4] 开始构建APK...
    echo [提示] 首次构建需要30分钟到1小时，请耐心等待...
    echo.
    wsl bash -c "cd /mnt/c/Users/Lenovo/Desktop/999999999 && export PATH=\$PATH:~/.local/bin && buildozer android debug"
    set BUILD_RESULT=%errorlevel%
    if %BUILD_RESULT% neq 0 (
        echo.
        echo [失败] WSL构建失败
        echo.
    )
    goto :check_result
)

:no_env

REM 都没有
echo.
echo [错误] 未找到构建环境
echo.
echo 请安装以下工具之一：
echo.
echo [选项1] Docker Desktop（推荐）
echo   下载: https://www.docker.com/products/docker-desktop
echo   或运行: 一键安装Docker.bat
echo   安装后重新运行此脚本
echo.
echo [选项2] WSL（Windows子系统）
echo   在PowerShell（管理员）运行: wsl --install
echo   或运行: 一键安装WSL.bat
echo   重启后重新运行此脚本
echo.
echo 详细说明请查看: 快速开始_构建APK.md
echo.
echo [提示] 按任意键退出...
pause >nul 2>&1
if errorlevel 1 timeout /t 5 /nobreak >nul 2>&1
exit /b 1

:check_result
echo.
echo [4/4] 检查构建结果...
echo.

if not defined BUILD_RESULT set BUILD_RESULT=1
if %BUILD_RESULT% == 0 (
    if exist "bin\*.apk" (
        echo ========================================
        echo   [成功] 构建完成！
        echo ========================================
        echo.
        echo APK文件列表:
        echo ----------------------------------------
        for %%f in (bin\*.apk) do (
            echo   %%f
            for %%A in ("%%f") do (
                echo   大小: %%~zA 字节
            )
        )
        echo ----------------------------------------
        echo.
        
        REM 检查ADB
        where adb >nul 2>&1
        if %errorlevel% == 0 (
            echo [检测] 发现ADB工具
            adb devices >nul 2>&1
            if %errorlevel% == 0 (
                echo [检测] 发现连接的Android设备
                echo.
                set /p install="是否安装到连接的Android设备？(Y/N): "
                if /i "!install!"=="Y" (
                    echo.
                    echo [安装] 正在安装APK...
                    for %%f in (bin\*.apk) do (
                        adb install -r "%%f"
                    )
                    echo.
                    echo [OK] 安装完成！
                )
            ) else (
                echo [提示] 未检测到连接的Android设备
                echo [提示] 请连接设备并启用USB调试，或手动安装APK
            )
        ) else (
            echo.
            echo [提示] 可以使用ADB安装APK
            echo   1. 安装Android SDK Platform Tools
            echo   2. 连接Android设备
            echo   3. 运行: adb install bin\sshtool-*.apk
        )
        
        echo.
        echo 或者手动安装:
        echo   1. 将APK文件复制到Android设备
        echo   2. 在设备上启用"未知来源"安装
        echo   3. 点击APK文件安装
        echo.
    ) else (
        echo [警告] 构建完成，但未找到APK文件
        echo 请检查构建日志
        set BUILD_RESULT=1
    )
) else (
    echo ========================================
    echo   [失败] 构建失败
    echo ========================================
    echo.
    echo 请查看上方错误信息
    echo.
    echo 常见问题：
    echo   1. Docker Desktop无法启动
    echo      - 请手动启动Docker Desktop并等待完全启动
    echo      - 或使用WSL方案（脚本会自动切换）
    echo   2. 构建环境问题
    echo      - 请检查网络连接
    echo      - 确保有足够的磁盘空间
    echo.
    echo 详细说明请参考: android_build_guide.md
    echo.
)

REM 确保pause能执行，避免窗口立即关闭
echo.
echo ========================================
echo 脚本执行完成
echo ========================================
echo.
echo 退出代码: %BUILD_RESULT%
echo.
echo [提示] 按任意键退出...
echo.

REM 尝试多种方式暂停，确保用户能看到结果
pause >nul 2>&1
if errorlevel 1 (
    REM 如果pause失败，使用timeout等待
    echo [提示] pause命令失败，等待5秒后自动退出...
    timeout /t 5 /nobreak
) else (
    REM pause成功，但再等待一下确保用户看到
    timeout /t 1 /nobreak >nul 2>&1
)

REM 确保退出
if not defined BUILD_RESULT set BUILD_RESULT=1
exit /b %BUILD_RESULT%

