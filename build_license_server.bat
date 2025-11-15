@echo off
chcp 65001 >nul
echo ========================================
echo 授权服务器（母机） - EXE打包脚本
echo ========================================
echo.

REM [1/4] 检查Python环境
echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python环境
    echo 请先安装Python 3.7或更高版本
    pause
    exit /b 1
)
echo.

REM [2/4] 检查并安装PyInstaller
echo [2/4] 检查并安装PyInstaller...
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller
if errorlevel 1 (
    echo 警告: PyInstaller安装失败，尝试继续...
)
echo.

REM [3/4] 检查并安装依赖库
echo [3/4] 检查并安装依赖库...
if exist requirements.txt (
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
) else (
    echo 警告: 未找到requirements.txt文件
)
echo.

REM [4/4] 开始打包程序
echo [4/4] 开始打包程序...
echo 正在打包，请稍候...
echo.

REM 使用PyInstaller打包（使用spec文件）
pyinstaller --clean --noconfirm license_server_gui.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo 打包失败！
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\流浪GM工具-授权服务器（母机）.exe
echo.
echo 使用spec文件打包（更稳定）
echo.
echo 提示:
echo 1. 首次运行可能需要几秒钟启动
echo 2. 建议将exe文件复制到单独文件夹使用
echo 3. 授权码列表文件（licenses.json）会在exe同目录下自动创建
echo.
pause

