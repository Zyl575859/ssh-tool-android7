@echo off
chcp 65001 >nul 2>&1
cls
title 查看GitHub构建状态

echo.
echo ========================================
echo   查看GitHub构建状态
echo ========================================
echo.

echo [提示] 请提供你的GitHub仓库地址
echo.
set /p repo_url="请输入仓库地址（例如: https://github.com/用户名/仓库名）: "

if "!repo_url!"=="" (
    echo [取消] 未输入地址
    pause
    exit /b 0
)

echo.
echo [打开] 正在打开GitHub Actions页面...
echo.

REM 构建Actions URL
set actions_url=!repo_url!/actions

echo GitHub Actions地址: !actions_url!
echo.
echo [操作] 正在打开浏览器...
echo.

REM 打开浏览器
start "" "!actions_url!"

echo [提示] 浏览器已打开
echo.
echo 下一步操作:
echo   1. 查看构建进度
echo   2. 如果构建完成，点击构建记录
echo   3. 在Artifacts部分下载APK
echo.
echo 详细说明请查看: 上传后下一步操作.md
echo.
pause

