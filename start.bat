@echo off
chcp 65001 >nul
title SSH连接工具
color 0A

:menu
cls
echo.
echo ========================================
echo          SSH连接工具
echo ========================================
echo.
echo 请选择操作:
echo.
echo [1] 查看GM命令模板
echo [2] 连接SSH服务器
echo [3] 使用配置文件连接
echo [4] 安装依赖
echo [0] 退出
echo.
set /p choice=请输入选项 (0-4): 

if "%choice%"=="1" goto show_template
if "%choice%"=="2" goto connect
if "%choice%"=="3" goto connect_config
if "%choice%"=="4" goto install
if "%choice%"=="0" goto end
goto menu

:show_template
cls
python ssh_tool.py -t
echo.
pause
goto menu

:connect
cls
echo.
echo 连接SSH服务器
echo ============
echo.
set /p host=请输入主机地址: 
set /p username=请输入用户名: 
set /p password=请输入密码: 
echo.
echo 正在连接...
python ssh_tool.py -H %host% -u %username% -p %password%
pause
goto menu

:connect_config
cls
echo.
echo 使用配置文件连接
echo ================
echo.
if not exist config.json (
    echo 配置文件不存在！
    echo.
    echo 正在创建示例配置文件...
    copy config.json.example config.json >nul
    echo 已创建 config.json，请编辑后重试
    pause
    goto menu
)
python ssh_tool.py -c config.json
pause
goto menu

:install
cls
echo.
echo 安装依赖
echo ========
echo.
echo 正在检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    goto menu
)
echo Python已安装
echo.
echo 正在安装依赖...
pip install -r requirements.txt
echo.
echo 安装完成！
pause
goto menu

:end
exit





