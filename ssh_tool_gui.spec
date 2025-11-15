# -*- mode: python ; coding: utf-8 -*-
# SSH连接工具 - PyInstaller配置文件

block_cipher = None

a = Analysis(
    ['ssh_tool_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含示例配置文件（如果有）
        ('config.json.example', '.'),
        # 不包含用户数据文件（connections.json、gm_templates.json、item_ids.json）
        # 这些文件会在程序首次运行时自动创建
    ],
    hiddenimports=[
        'paramiko',
        'pytz',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'license_manager',
        'connection_monitor',
        'cryptography',
        'bcrypt',
        'openpyxl',
        'xlrd',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='流浪GM工具v1.0.1豪华版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口（GUI程序）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径，例如: 'icon.ico'
)

