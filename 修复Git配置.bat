@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion
cls
title 修复Git配置

echo.
echo ========================================
echo   修复Git配置
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

echo [检查] 当前Git配置...
echo.

REM 检查用户信息
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo [配置] Git用户信息未配置
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
        echo [失败] 配置失败
        pause
        exit /b 1
    )
    echo [OK] Git用户信息已配置
) else (
    for /f "tokens=*" %%n in ('git config user.name') do set git_name=%%n
    for /f "tokens=*" %%e in ('git config user.email') do set git_email=%%e
    echo [OK] Git用户信息已配置
    echo   名字: !git_name!
    echo   邮箱: !git_email!
    echo.
    set /p change="是否修改? (Y/n): "
    if /i "!change!"=="Y" (
        set /p git_name="请输入你的名字: "
        set /p git_email="请输入你的邮箱: "
        git config --global user.name "!git_name!"
        git config --global user.email "!git_email!"
        echo [OK] Git用户信息已更新
    )
)

echo.
echo [验证] 当前Git配置:
echo.
git config --list | findstr user
echo.

echo [OK] Git配置检查完成
echo.
echo 现在可以重新运行: 一键上传并构建.bat
echo.
pause

