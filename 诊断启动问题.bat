@echo off
chcp 65001 >nul 2>&1
title SSH工具启动诊断

echo.
echo ========================================
echo   SSH工具启动诊断
echo ========================================
echo.

python 诊断启动问题.py

if errorlevel 1 (
    echo.
    echo 诊断过程中发现错误！
    pause
    exit /b 1
)

pause



