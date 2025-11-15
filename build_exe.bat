@echo off
chcp 65001 >nul
echo ========================================
echo SSH连接工具 - EXE打包脚本
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

echo.
echo [2/4] 检查并安装PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller
if errorlevel 1 (
    echo 错误: PyInstaller安装失败
    pause
    exit /b 1
)

echo.
echo [3/4] 检查并安装依赖库...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 部分依赖库安装失败，继续打包...
)

echo.
echo [4/4] 开始打包程序...
echo 正在打包，请稍候...
echo.

REM 使用PyInstaller打包
pyinstaller --clean --noconfirm ssh_tool_gui.spec

if errorlevel 1 (
    echo.
    echo 错误: 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\流浪GM工具v1.0.1豪华版.exe
echo.
echo 提示:
echo 1. 首次运行可能需要几秒钟启动
echo 2. 建议将exe文件复制到单独文件夹使用
echo 3. 配置文件会在exe同目录下自动创建
echo.
pause








































