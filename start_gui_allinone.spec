# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('ssh_tool_gui.py', '.'), ('license_manager.py', '.'), ('licenses.json', '.'), ('config.json', '.'), ('config.json.example', '.'), ('gm_templates.json', '.'), ('gm_templates.json.backup', '.'), ('item_ids.json', '.'), ('connections.json', '.'), ('connections.json.backup', '.'), ('user_connections.json', '.'), ('license.key', '.')]
binaries = []
hiddenimports = ['pkgutil', 'paramiko', 'pytz', 'tkinter', 'tkinter.ttk', 'tkinter.scrolledtext', 'tkinter.messagebox', 'tkinter.filedialog', 'tkinter.simpledialog']
tmp_ret = collect_all('paramiko')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pytz')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['build\\obf\\start_gui_wrapper.py'],
    pathex=['build\\obf'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='start_gui_allinone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
