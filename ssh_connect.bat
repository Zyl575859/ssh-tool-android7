@echo off
chcp 65001 >nul
title SSH快速连接
color 0B

echo SSH连接工具
echo ===========
echo.

if "%1"=="" (
    echo 使用方法:
    echo   ssh_connect.bat [主机地址] [用户名] [密码]
    echo.
    echo 示例:
    echo   ssh_connect.bat 192.168.1.100 root mypassword
    echo.
    echo 或者运行 start.bat 使用图形菜单
    echo 或者直接运行查看GM模板:
    echo   python ssh_tool.py -t
    echo.
    pause
    exit /b
)

set HOST=%1
set USER=%2
set PASS=%3

if "%PASS%"=="" (
    python ssh_tool.py -H %HOST% -u %USER%
) else (
    python ssh_tool.py -H %HOST% -u %USER% -p %PASS%
)

if errorlevel 1 (
    echo.
    echo 连接失败或发生错误
    pause
)

