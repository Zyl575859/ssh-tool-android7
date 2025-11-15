@echo off
chcp 65001 >nul 2>&1
cls
title 快速上传代码到GitHub

echo.
echo ========================================
echo   快速上传代码到GitHub
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

REM 检查是否在Git仓库中
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo [初始化] 当前目录不是Git仓库，正在初始化...
    git init
    if %errorlevel% neq 0 (
        echo [失败] Git初始化失败
        pause
        exit /b 1
    )
    echo [OK] Git仓库初始化完成
    echo.
)

REM 检查是否配置了用户信息
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [配置] 首次使用，需要配置Git用户信息
    echo.
    set /p git_name="请输入你的名字: "
    set /p git_email="请输入你的邮箱: "
    git config --global user.name "!git_name!"
    git config --global user.email "!git_email!"
    echo [OK] Git用户信息已配置
    echo.
)

REM 检查是否有未提交的更改或文件
git status --porcelain >nul 2>&1
set has_changes=%errorlevel%

REM 检查是否有提交
git rev-parse --verify HEAD >nul 2>&1
set has_commit=%errorlevel%

if %has_changes% == 0 (
    echo [检测] 发现未提交的文件
    echo.
    echo [步骤1] 添加所有文件...
    git add .
    if %errorlevel% neq 0 (
        echo [失败] 添加文件失败
        pause
        exit /b 1
    )
    echo [OK] 文件已添加
    echo.
    
    echo [步骤2] 创建提交...
    set /p commit_msg="请输入提交信息（直接回车使用默认）: "
    if "!commit_msg!"=="" set commit_msg=初始提交
    git commit -m "!commit_msg!"
    if %errorlevel% neq 0 (
        echo [失败] 提交失败
        pause
        exit /b 1
    )
    echo [OK] 提交完成
    echo.
) else if %has_commit% neq 0 (
    echo [检测] 没有提交记录，需要先提交文件
    echo.
    echo [步骤1] 添加所有文件...
    git add .
    if %errorlevel% neq 0 (
        echo [失败] 添加文件失败
        pause
        exit /b 1
    )
    echo [OK] 文件已添加
    echo.
    
    echo [步骤2] 创建第一次提交...
    git commit -m "初始提交"
    if %errorlevel% neq 0 (
        echo [失败] 提交失败
        pause
        exit /b 1
    )
    echo [OK] 提交完成
    echo.
)

REM 检查远程仓库
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo [配置] 需要添加GitHub远程仓库地址
    echo.
    echo 请先在GitHub上创建仓库，然后:
    echo   1. 访问: https://github.com/new
    echo   2. 创建新仓库
    echo   3. 复制仓库地址
    echo.
    set /p repo_url="请输入GitHub仓库地址（例如: https://github.com/用户名/仓库名.git）: "
    if "!repo_url!"=="" (
        echo [取消] 未输入仓库地址
        pause
        exit /b 0
    )
    git remote add origin "!repo_url!"
    if %errorlevel% neq 0 (
        echo [失败] 添加远程仓库失败，可能已存在
        echo [提示] 尝试更新远程地址...
        git remote set-url origin "!repo_url!"
    )
    echo [OK] 远程仓库已配置
    echo.
)

REM 检查当前分支
git branch --show-current >nul 2>&1
if %errorlevel% neq 0 (
    REM 检查是否有提交
    git rev-parse --verify HEAD >nul 2>&1
    if %errorlevel% == 0 (
        REM 有提交，创建main分支
        git checkout -b main >nul 2>&1
        if %errorlevel% neq 0 (
            REM 如果main分支已存在，切换到main
            git checkout main >nul 2>&1
        )
    ) else (
        REM 没有提交，先创建main分支
        git branch -M main >nul 2>&1
    )
)

REM 获取当前分支名
for /f "tokens=*" %%b in ('git branch --show-current 2^>nul') do set current_branch=%%b
if "!current_branch!"=="" (
    REM 如果没有分支，尝试使用master
    git branch -M master >nul 2>&1
    set current_branch=master
)

echo [步骤3] 上传代码到GitHub...
echo [提示] 如果是第一次，可能需要输入GitHub用户名和密码
echo [提示] 当前分支: !current_branch!
echo.
git push -u origin !current_branch!
if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo   [成功] 代码已上传到GitHub！
    echo ========================================
    echo.
    echo 下一步:
    echo   1. 访问你的GitHub仓库
    echo   2. 点击 "Actions" 标签
    echo   3. 查看自动构建进度
    echo   4. 构建完成后下载APK
    echo.
    echo 详细说明请查看: 上传代码到GitHub_详细步骤.md
    echo.
) else (
    echo.
    echo ========================================
    echo   [失败] 上传失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo   1. 需要GitHub认证（使用Personal Access Token）
    echo   2. 网络连接问题
    echo   3. 仓库地址错误
    echo.
    echo 详细说明请查看: 上传代码到GitHub_详细步骤.md
    echo.
)

pause

