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

# (str) 自定义源码包含/排除模式
#source.include_patterns = assets/*,images/*.png

# (str) 自定义源码排除模式
#source.exclude_patterns = license

# (list) 应用依赖（完整路径）
#requirements.source.kivy = ../../kivy

# (str) Python版本
python.version = 3

# (list) 应用依赖（Android特定）
#android.gradle_dependencies =

# (str) 启动活动
#android.entrypoint = org.kivy.android.PythonActivity

# (str) 应用图标
#icon.filename = %(source.dir)s/data/icon.png

# (str) 应用图标（Android）
#icon.filename = %(source.dir)s/data/icon.png

# (str) 预设图标（Android）
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) 预设图标（Android）
#presplash.filename = %(source.dir)s/data/presplash.png

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

# (list) Android应用元数据
#android.meta_data =

# (list) Android库
#android.add_compile_options =

# (list) Android Java类
#android.add_java_classes =

# (str) Android logcat过滤器
#android.logcat_filters = *:S python:D

# (str) Android额外配置
#android.extra_config =

# (list) Android额外Java类
#android.add_java_classes =

# (list) Android额外Java文件
#android.add_java_files =

# (list) Android额外AAR
#android.add_aars =

# (list) Android额外JAR
#android.add_jars =

# (list) Android额外Maven依赖
#android.add_maven_repositories =

# (list) Android额外Gradle依赖
#android.gradle_dependencies =

# (list) Android额外Gradle仓库
#android.gradle_repositories =

# (list) Android额外ProGuard规则
#android.proguard_rules =

# (str) Android应用主题
#android.theme = @android:style/Theme.NoTitleBar

# (list) Android应用活动
#android.activities =

# (list) Android应用服务
#android.services =

# (list) Android应用接收器
#android.receivers =

# (str) Android应用包类型
#android.package_type = apk

# (str) Android应用签名密钥
#android.signkey = debug.keystore

# (str) Android应用签名密钥别名
#android.signkey_alias = androiddebugkey

# (str) Android应用签名密钥密码
#android.signkey_passwd = android

# (bool) Android应用调试
#android.debug = False

# (str) Android应用版本代码
#android.version_code = 1

# (str) Android应用版本名称
#android.version_name = 1.0.0

# (list) Android应用意图过滤器
#android.intent_filters =

# (str) Android应用启动模式
#android.launch_mode = standard

# (list) Android应用额外配置
#android.extra_config =

[buildozer]

# (int) 日志级别 (0 = 仅错误, 1 = 信息, 2 = 调试)
log_level = 2

# (int) 显示警告级别 (0 = 所有, 1 = 跳过警告, 2 = 仅错误)
warn_on_root = 1




