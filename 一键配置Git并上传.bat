@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cls
title 一键配置Git并上传到GitHub

echo.
echo ========================================
echo   一键配置Git并上传到GitHub
echo ========================================
echo.

REM 检查Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未安装Git
    echo.
    echo 请先安装Git:
    echo   下载: https://git-scm.com/download/win
    echo   安装后重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo [OK] Git已安装
echo.

REM 步骤1: 配置Git用户信息
echo ========================================
echo [步骤1] 配置Git用户信息
echo ========================================
echo.

git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo 这是首次使用Git，需要配置用户信息（只需配置一次）
    echo.
    set /p git_name="请输入你的名字: "
    if "!git_name!"=="" (
        echo [错误] 名字不能为空，请重新运行脚本
        pause
        exit /b 1
    )
    set /p git_email="请输入你的邮箱: "
    if "!git_email!"=="" (
        echo [错误] 邮箱不能为空，请重新运行脚本
        pause
        exit /b 1
    )
    git config --global user.name "!git_name!"
    git config --global user.email "!git_email!"
    echo.
    echo [OK] Git用户信息已配置
    echo   名字: !git_name!
    echo   邮箱: !git_email!
) else (
    for /f "tokens=*" %%n in ('git config user.name') do set git_name=%%n
    for /f "tokens=*" %%e in ('git config user.email') do set git_email=%%e
    echo [OK] Git用户信息已配置
    echo   名字: !git_name!
    echo   邮箱: !git_email!
)
echo.

REM 步骤2: 初始化Git仓库
echo ========================================
echo [步骤2] 初始化Git仓库
echo ========================================
echo.

if not exist ".git" (
    git init
    if %errorlevel% neq 0 (
        echo [失败] Git初始化失败
        pause
        exit /b 1
    )
    echo [OK] Git仓库已初始化
) else (
    echo [OK] Git仓库已存在
)
echo.

REM 步骤3: 添加文件
echo ========================================
echo [步骤3] 添加所有文件
echo ========================================
echo.

git add .
if %errorlevel% neq 0 (
    echo [失败] 添加文件失败
    pause
    exit /b 1
)
echo [OK] 文件已添加到暂存区
echo.

REM 步骤4: 创建提交
echo ========================================
echo [步骤4] 创建提交
echo ========================================
echo.

REM 检查是否有需要提交的文件
git diff --cached --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在创建提交...
    git commit -m "初始提交"
    if %errorlevel% neq 0 (
        echo.
        echo [失败] 提交失败
        echo.
        echo 请检查Git配置是否正确:
        git config --list | findstr user
        echo.
        pause
        exit /b 1
    )
    echo [OK] 提交成功
) else (
    echo [提示] 没有需要提交的文件
    REM 检查是否有提交记录
    git rev-parse --verify HEAD >nul 2>&1
    if %errorlevel% neq 0 (
        echo [提示] 创建空提交...
        git commit --allow-empty -m "初始提交"
        echo [OK] 空提交创建成功
    ) else (
        echo [提示] 已有提交记录，跳过
    )
)
echo.

REM 步骤5: 配置远程仓库
echo ========================================
echo [步骤5] 配置GitHub远程仓库
echo ========================================
echo.

echo 请先在GitHub上创建仓库:
echo   1. 访问: https://github.com/new
echo   2. 输入仓库名（例如: ssh-tool-android）
echo   3. 选择 Public
echo   4. 点击 Create repository
echo   5. 复制仓库地址
echo.
set /p repo_url="请输入GitHub仓库地址: "
if "!repo_url!"=="" (
    echo [取消] 未输入仓库地址
    pause
    exit /b 0
)

REM 移除旧的远程仓库
git remote remove origin >nul 2>&1

REM 添加新的远程仓库
git remote add origin "!repo_url!"
if %errorlevel% neq 0 (
    echo [提示] 尝试更新远程地址...
    git remote set-url origin "!repo_url!"
)
echo [OK] 远程仓库已配置: !repo_url!
echo.

REM 步骤6: 确保使用main分支
echo ========================================
echo [步骤6] 准备上传
echo ========================================
echo.

git branch -M main >nul 2>&1
echo [OK] 使用main分支
echo.

REM 步骤7: 上传代码
echo ========================================
echo [步骤7] 上传代码到GitHub
echo ========================================
echo.

echo [重要提示]
echo   如果是第一次上传，需要GitHub认证:
echo   1. 用户名: 输入你的GitHub用户名
echo   2. 密码: 输入Personal Access Token（不是GitHub密码）
echo.
echo   如何获取Token:
echo   1. 访问: https://github.com/settings/tokens
echo   2. Generate new token ^(classic^)
echo   3. 勾选 repo 权限
echo   4. 生成并复制token
echo.
echo 按任意键继续上传...
pause >nul

git push -u origin main
if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo   [成功] 代码已上传到GitHub！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 访问: !repo_url!
    echo   2. 点击 "Actions" 标签
    echo   3. 查看自动构建进度（约10-20分钟）
    echo   4. 构建完成后下载APK
    echo.
) else (
    echo.
    echo ========================================
    echo   [失败] 上传失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo   1. 认证失败 - 请使用Personal Access Token
    echo   2. 网络问题 - 请检查网络连接
    echo   3. 仓库地址错误 - 请确认地址正确
    echo.
    echo 详细说明: 上传代码到GitHub_详细步骤.md
    echo.
)

pause

