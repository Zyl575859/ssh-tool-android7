@echo off
chcp 65001 >nul
title SSH连接工具 - 图形界面
color 0A

echo.
echo 正在启动SSH连接工具（图形界面）...
echo.

python ssh_tool_gui.py

if errorlevel 1 (
    echo.
    echo 启动失败，可能的原因：
    echo 1. 缺少Python
    echo 2. 缺少依赖库（运行: pip install paramiko）
    echo.
    pause
)





