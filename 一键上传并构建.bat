@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cd /d "%~dp0"
cls
title 一键上传到GitHub并构建APK

echo.
echo ========================================
echo   一键上传到GitHub并构建APK
echo ========================================
echo.

REM 检查Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未安装Git
    echo 下载: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM 检查必需文件
echo [检查] 正在检查必需文件...
set MISSING=0

if not exist "main.py" (
    echo [错误] main.py 不存在
    set MISSING=1
)
if not exist "buildozer.spec" (
    echo [错误] buildozer.spec 不存在
    set MISSING=1
)
if not exist ".github\workflows\build_apk.yml" (
    echo [警告] .github\workflows\build_apk.yml 不存在
    echo [提示] 将自动创建GitHub Actions配置
)

if %MISSING%==1 (
    echo [失败] 缺少必需文件
    pause
    exit /b 1
)

echo [OK] 必需文件检查完成
echo.

REM 创建GitHub Actions配置（如果不存在）
if not exist ".github\workflows\build_apk.yml" (
    echo [创建] 正在创建GitHub Actions配置...
    if not exist ".github\workflows" mkdir ".github\workflows"
    
    (
        echo name: 构建Android APK
        echo.
        echo on:
        echo   workflow_dispatch:
        echo   push:
        echo     branches: [ main, master ]
        echo     paths:
        echo       - 'main.py'
        echo       - 'buildozer.spec'
        echo.
        echo jobs:
        echo   build:
        echo     runs-on: ubuntu-latest
        echo     
        echo     steps:
        echo     - name: 检出代码
        echo       uses: actions/checkout@v3
        echo       
        echo     - name: 设置Python
        echo       uses: actions/setup-python@v4
        echo       with:
        echo         python-version: '3.10'
        echo         
        echo     - name: 安装系统依赖
        echo       run: ^|
        echo         sudo apt-get update
        echo         sudo apt-get install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
        echo         
        echo     - name: 安装Buildozer
        echo       run: ^|
        echo         pip3 install --user buildozer
        echo         echo "$HOME/.local/bin" ^>^> $GITHUB_PATH
        echo         
        echo     - name: 构建APK
        echo       run: buildozer android debug
        echo         
        echo     - name: 上传APK
        echo       uses: actions/upload-artifact@v3
        echo       with:
        echo         name: android-apk
        echo         path: bin/*.apk
        echo         retention-days: 30
    ) > ".github\workflows\build_apk.yml
    
    echo [OK] GitHub Actions配置已创建
    echo.
)

REM 初始化Git（如果需要）
if not exist ".git" (
    echo [初始化] 正在初始化Git仓库...
    git init >nul 2>&1
    echo [OK] Git仓库已初始化
    echo.
)

REM 配置Git用户（如果需要）
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [配置] 需要配置Git用户信息（只需一次）
    echo.
    set /p git_name="请输入你的名字: "
    if "!git_name!"=="" (
        echo [错误] 名字不能为空
        pause
        exit /b 1
    )
    set /p git_email="请输入你的邮箱: "
    if "!git_email!"=="" (
        echo [错误] 邮箱不能为空
        pause
        exit /b 1
    )
    git config --global user.name "!git_name!"
    git config --global user.email "!git_email!"
    if %errorlevel% neq 0 (
        echo [失败] Git用户信息配置失败
        pause
        exit /b 1
    )
    echo [OK] Git用户信息已配置: !git_name! ^<!git_email!^>
    echo.
) else (
    for /f "tokens=*" %%n in ('git config user.name') do set git_name=%%n
    for /f "tokens=*" %%e in ('git config user.email') do set git_email=%%e
    echo [OK] Git用户信息: !git_name! ^<!git_email!^>
    echo.
)

REM 添加文件
echo [添加] 正在添加文件...
git add main.py buildozer.spec .github\workflows\build_apk.yml >nul 2>&1
echo [OK] 文件已添加
echo.

REM 提交
echo [提交] 正在提交...

REM 再次确认Git用户信息已配置
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Git用户信息未配置，无法提交
    echo 请重新运行脚本并输入用户信息
    pause
    exit /b 1
)

REM 检查是否有需要提交的文件
git diff --cached --quiet >nul 2>&1
if %errorlevel% neq 0 (
    git commit -m "初始提交：添加APK构建文件"
    if %errorlevel% neq 0 (
        echo [失败] 提交失败
        echo.
        echo 请检查Git配置:
        git config --list | findstr user
        echo.
        pause
        exit /b 1
    )
    echo [OK] 提交完成
) else (
    REM 检查是否已有提交记录
    git rev-parse --verify HEAD >nul 2>&1
    if %errorlevel% neq 0 (
        echo [提示] 没有需要提交的文件，创建空提交...
        git commit --allow-empty -m "初始提交"
        if %errorlevel% neq 0 (
            echo [失败] 创建提交失败
            pause
            exit /b 1
        )
        echo [OK] 空提交创建成功
    ) else (
        echo [提示] 已有提交记录，跳过
    )
)
echo.

REM 确保使用main分支
git branch -M main >nul 2>&1

REM 配置远程仓库
echo [配置] 需要配置GitHub远程仓库
echo.
echo 请先在GitHub上创建仓库:
echo   1. 访问: https://github.com/new
echo   2. 输入仓库名（例如: ssh-tool-android）
echo   3. 选择 Public
echo   4. 点击 Create repository
echo   5. 复制仓库地址
echo.
set /p repo_url="请输入GitHub仓库地址（例如: https://github.com/用户名/仓库名.git）: "

if "!repo_url!"=="" (
    echo [取消] 未输入仓库地址
    echo.
    echo [提示] 稍后可以手动添加:
    echo   git remote add origin ^<仓库地址^>
    echo   git push -u origin main
    pause
    exit /b 0
)

REM 移除旧的远程仓库
git remote remove origin >nul 2>&1

REM 添加新的远程仓库
git remote add origin "!repo_url!" >nul 2>&1
if %errorlevel% neq 0 (
    git remote set-url origin "!repo_url!" >nul 2>&1
)
echo [OK] 远程仓库已配置
echo.

REM 上传代码
echo [上传] 正在上传代码到GitHub...
echo [提示] 如果是第一次，需要输入GitHub用户名和Token
echo [提示] 获取Token: https://github.com/settings/tokens
echo.
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [失败] 上传失败
    echo.
    echo 可能的原因:
    echo   1. 需要GitHub认证（使用Personal Access Token）
    echo   2. 仓库地址错误
    echo   3. 网络问题
    echo.
    echo [提示] 可以稍后手动上传:
    echo   git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   [成功] 代码已上传到GitHub！
echo ========================================
echo.

REM 打开GitHub Actions页面
set actions_url=!repo_url:/github.com/=github.com/!
set actions_url=!actions_url:.git=/actions!

echo [打开] 正在打开GitHub Actions页面...
echo.
start "" "!actions_url!"

echo ========================================
echo   下一步操作
echo ========================================
echo.
echo 1. 在打开的页面中，点击 "Run workflow" 按钮
echo 2. 选择分支（main）
echo 3. 点击 "Run workflow" 确认
echo 4. 等待构建完成（10-20分钟）
echo 5. 构建完成后，在Artifacts中下载APK
echo.
echo GitHub Actions地址: !actions_url!
echo.
echo 详细说明请查看: 上传后下一步操作.md
echo.
pause

