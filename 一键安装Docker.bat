@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

title 一键安装 Docker Desktop

echo.
echo ========================================
echo   一键安装 Docker Desktop
echo ========================================
echo.

REM 检查是否已安装
docker --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Docker 已安装
    docker --version
    echo.
    echo Docker已就绪，可以直接构建APK
    pause
    exit /b 0
)

echo [1/2] 下载Docker Desktop...
echo.

set "TEMP_DIR=%TEMP%\docker_install"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

set "DOCKER_URL=https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
set "DOCKER_INSTALLER=%TEMP_DIR%\DockerDesktopInstaller.exe"

echo 下载地址: %DOCKER_URL%
echo 保存位置: %DOCKER_INSTALLER%
echo.
echo 正在下载（这可能需要几分钟）...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ProgressPreference = 'SilentlyContinue'; " ^
"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
"try { " ^
"  Invoke-WebRequest -Uri '%DOCKER_URL%' -OutFile '%DOCKER_INSTALLER%' -UseBasicParsing; " ^
"  Write-Host '[OK] 下载完成' -ForegroundColor Green; " ^
"} catch { " ^
"  Write-Host '[错误] 下载失败，请检查网络连接' -ForegroundColor Red; " ^
"  Write-Host '错误信息:' $_.Exception.Message; " ^
"  exit 1; " ^
"}"

if %errorlevel% neq 0 (
    echo.
    echo [错误] 自动下载失败
    echo.
    echo 请手动下载：
    echo   访问: https://www.docker.com/products/docker-desktop
    echo.
    start https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

if not exist "%DOCKER_INSTALLER%" (
    echo [错误] 下载的文件不存在
    pause
    exit /b 1
)

echo.
echo [2/2] 启动安装程序...
echo [提示] 请按照安装向导完成安装
echo.

start "" "%DOCKER_INSTALLER%"

echo.
echo ========================================
echo   安装程序已启动
echo ========================================
echo.
echo 请按照安装向导完成安装，然后：
echo   1. 启动 Docker Desktop
echo   2. 等待Docker完全启动
echo   3. 运行: 构建APK.bat
echo.
pause




