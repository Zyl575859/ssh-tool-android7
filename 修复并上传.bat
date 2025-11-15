@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cls
title 修复Git问题并上传到GitHub

echo.
echo ========================================
echo   修复Git问题并上传到GitHub
echo ========================================
echo.

REM 检查Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未安装Git
    echo 请先安装Git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [步骤1] 检查Git配置...
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [配置] 需要配置Git用户信息
    set /p git_name="请输入你的名字: "
    set /p git_email="请输入你的邮箱: "
    git config --global user.name "!git_name!"
    git config --global user.email "!git_email!"
    echo [OK] Git用户信息已配置
    echo.
)

REM 初始化Git（如果还没有）
if not exist ".git" (
    echo [步骤2] 初始化Git仓库...
    git init
    echo [OK] Git仓库已初始化
    echo.
)

REM 添加所有文件
echo [步骤3] 添加所有文件...
git add .
if %errorlevel% neq 0 (
    echo [失败] 添加文件失败
    pause
    exit /b 1
)
echo [OK] 文件已添加
echo.

REM 检查是否有提交
git rev-parse --verify HEAD >nul 2>&1
if %errorlevel% neq 0 (
    echo [步骤4] 创建第一次提交...
    git commit -m "初始提交"
    if %errorlevel% neq 0 (
        echo [失败] 提交失败，可能没有配置用户信息
        pause
        exit /b 1
    )
    echo [OK] 提交完成
    echo.
)

REM 确保有main分支
git branch -M main >nul 2>&1

REM 配置远程仓库
echo [步骤5] 配置GitHub远程仓库...
echo.
echo 请先在GitHub上创建仓库:
echo   1. 访问: https://github.com/new
echo   2. 创建新仓库（例如: ssh-tool-android）
echo   3. 复制仓库地址
echo.
set /p repo_url="请输入GitHub仓库地址: "
if "!repo_url!"=="" (
    echo [取消] 未输入仓库地址
    pause
    exit /b 0
)

REM 移除旧的远程仓库（如果存在）
git remote remove origin >nul 2>&1

REM 添加新的远程仓库
git remote add origin "!repo_url!"
if %errorlevel% neq 0 (
    echo [提示] 远程仓库可能已存在，尝试更新...
    git remote set-url origin "!repo_url!"
)
echo [OK] 远程仓库已配置: !repo_url!
echo.

REM 上传代码
echo [步骤6] 上传代码到GitHub...
echo [提示] 如果是第一次，需要输入GitHub用户名和密码
echo [提示] 密码处可以输入Personal Access Token（更安全）
echo.
git push -u origin main
if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo   [成功] 代码已上传到GitHub！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 访问你的GitHub仓库: !repo_url!
    echo   2. 点击 "Actions" 标签
    echo   3. 查看自动构建进度
    echo   4. 构建完成后下载APK
    echo.
) else (
    echo.
    echo ========================================
    echo   [失败] 上传失败
    echo ========================================
    echo.
    echo 可能的原因和解决方法:
    echo.
    echo 1. 需要GitHub认证
    echo    解决方法:
    echo    a) 使用Personal Access Token（推荐）
    echo       - GitHub → Settings → Developer settings
    echo       - Personal access tokens → Tokens (classic)
    echo       - Generate new token → 勾选 repo 权限
    echo       - 复制token，push时密码处输入token
    echo    b) 或使用GitHub Desktop（更简单）
    echo.
    echo 2. 仓库地址错误
    echo    确保地址格式正确: https://github.com/用户名/仓库名.git
    echo.
    echo 3. 网络问题
    echo    检查网络连接，或稍后重试
    echo.
    echo 详细说明: 上传代码到GitHub_详细步骤.md
    echo.
)

pause

