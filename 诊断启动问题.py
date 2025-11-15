#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断SSH工具启动问题
"""

import sys
import traceback

print("=" * 80)
print("SSH工具启动诊断")
print("=" * 80)
print()

# 检查Python版本
print(f"[1] Python版本: {sys.version}")
print()

# 检查必要的模块
print("[2] 检查必要的模块...")
modules_to_check = [
    'tkinter',
    'paramiko',
    'pytz',
    'license_manager'
]

for module_name in modules_to_check:
    try:
        if module_name == 'tkinter':
            import tkinter
            print(f"  [OK] {module_name} - 已安装")
        elif module_name == 'paramiko':
            import paramiko
            print(f"  [OK] {module_name} - 已安装 (版本: {paramiko.__version__})")
        elif module_name == 'pytz':
            import pytz
            print(f"  [OK] {module_name} - 已安装")
        elif module_name == 'license_manager':
            from license_manager import LicenseManager
            print(f"  [OK] {module_name} - 已安装")
    except ImportError as e:
        print(f"  [失败] {module_name} - 未安装: {e}")
    except Exception as e:
        print(f"  [警告] {module_name} - 检查时出错: {e}")

print()

# 尝试导入主程序
print("[3] 尝试导入主程序...")
try:
    import ssh_tool_gui
    print("  [OK] ssh_tool_gui 模块导入成功")
except Exception as e:
    print(f"  [失败] ssh_tool_gui 模块导入失败:")
    print(f"  错误: {e}")
    print(f"  详细错误:")
    traceback.print_exc()
    print()
    input("按回车键退出...")
    sys.exit(1)

print()

# 尝试创建Tkinter窗口
print("[4] 尝试创建Tkinter窗口...")
try:
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    print("  [OK] Tkinter窗口创建成功")
    root.destroy()
except Exception as e:
    print(f"  [失败] Tkinter窗口创建失败:")
    print(f"  错误: {e}")
    print(f"  详细错误:")
    traceback.print_exc()
    print()
    input("按回车键退出...")
    sys.exit(1)

print()

# 尝试初始化主程序
print("[5] 尝试初始化主程序...")
print("  [提示] Tkinter必须在主线程中运行，这里只做基本检查")
print("  [提示] 如果程序能正常启动，说明初始化没问题")
print("  [提示] 如果程序闪退，请查看实际的错误信息")
try:
    # 只检查类定义，不实际创建实例（因为Tkinter必须在主线程中）
    if hasattr(ssh_tool_gui, 'SSHToolGUI'):
        print("  [OK] SSHToolGUI 类定义存在")
        print("  [提示] 实际运行程序时，如果出现错误会显示详细信息")
    else:
        print("  [失败] SSHToolGUI 类不存在")
        print()
        input("按回车键退出...")
        sys.exit(1)
except Exception as e:
    print(f"  [失败] 检查过程出错:")
    print(f"  错误: {e}")
    print(f"  详细错误:")
    traceback.print_exc()
    print()
    input("按回车键退出...")
    sys.exit(1)

print()
print("=" * 80)
print("诊断完成！")
print("=" * 80)
print()
print("如果所有检查都通过，但程序仍然闪退，可能是以下原因：")
print("1. 授权码问题 - 检查是否有有效的授权码")
print("2. 配置文件问题 - 检查 connections.json 等配置文件是否损坏")
print("3. 权限问题 - 尝试以管理员身份运行")
print()
input("按回车键退出...")

