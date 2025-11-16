[app]

title = SSH工具
package.name = sshtool
package.domain = org.liulang
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
source.include_patterns = main.py
source.exclude_exts = spec,bat,md,txt,xlsx,xlsm,exe,pyc,pyo
source.exclude_dirs = build,dist,__pycache__,.git
requirements = python3,kivy,paramiko,pyjnius
python.version = 3
version = 1.0.1
android.version_code = 2
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.archs = arm64-v8a,armeabi-v7a
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
