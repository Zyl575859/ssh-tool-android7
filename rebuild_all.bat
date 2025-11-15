@echo off
chcp 65001 >nul
echo ========================================
echo 重新打包所有程序
echo ========================================
echo.

echo [1/5] 关闭可能正在运行的程序...
taskkill /F /IM "流浪GM工具v1.0.1豪华版.exe" >nul 2>&1
taskkill /F /IM "流浪GM工具v1.0.1豪华版（子机）.exe" >nul 2>&1
taskkill /F /IM "流浪GM工具-授权服务器（母机）.exe" >nul 2>&1
timeout /t 2 >nul
echo 完成
echo.

echo [2/5] 打包主程序...
pyinstaller --clean --noconfirm ssh_tool_gui.spec
if errorlevel 1 (
    echo 主程序打包失败！
    pause
    exit /b 1
)
echo.

echo [3/5] 打包客户端程序...
pyinstaller --clean --noconfirm ssh_tool_gui_client.spec
if errorlevel 1 (
    echo 客户端程序打包失败！
    pause
    exit /b 1
)
echo.

echo [4/5] 打包授权服务器...
pyinstaller --clean --noconfirm license_server_gui.spec
if errorlevel 1 (
    echo 授权服务器打包失败！
    pause
    exit /b 1
)
echo.

echo [5/5] 打包完成！
echo.
echo ========================================
echo 所有程序已重新打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\
echo   - 流浪GM工具v1.0.1豪华版.exe
echo   - 流浪GM工具v1.0.1豪华版（子机）.exe
echo   - 流浪GM工具-授权服务器（母机）.exe
echo.
pause


