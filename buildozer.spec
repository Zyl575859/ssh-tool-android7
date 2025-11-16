[app]

# (str) 应用标题
title = SSH工具

# (str) 包名
package.name = sshtool

# (str) 包域名
package.domain = org.liulang

# (str) 源代码目录
source.dir = .

# (str) 应用入口文件
source.include_exts = py,png,jpg,kv,atlas,json

# (list) 应用源代码文件
# 只包含main.py作为入口
source.include_patterns = main.py

# (list) 排除的文件/目录
source.exclude_exts = spec,bat,md,txt,xlsx,xlsm,exe,pyc,pyo
source.exclude_dirs = build,dist,__pycache__,.git

# (list) 应用依赖
requirements = python3,kivy,paramiko,pyjnius

# (str) Python版本
python.version = 3

# (str) 应用版本
version = 1.0.1

# (str) 应用版本代码（每次发布递增）
android.version_code = 2

# (list) 应用权限
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (int) Android API级别
android.api = 30

# (int) Android最小API级别
android.minapi = 21

# (int) Android NDK版本
android.ndk = 23b

# (int) Android SDK版本
android.sdk = 30

# (str) Android架构
android.archs = arm64-v8a,armeabi-v7a

# (bool) 启用AndroidX支持
android.enable_androidx = True

[buildozer]

# (int) 日志级别 (0 = 仅错误, 1 = 信息, 2 = 调试)
log_level = 2

# (int) 显示警告级别 (0 = 所有, 1 = 跳过警告, 2 = 仅错误)
warn_on_root = 1
