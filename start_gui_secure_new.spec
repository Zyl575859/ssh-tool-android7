# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['build\\obf\\start_gui_wrapper.py'],
    pathex=['build\\obf'],
    binaries=[],
    datas=[('ssh_tool_gui.py', '.'), ('license_manager.py', '.'), ('licenses.json', '.'), ('config.json', '.'), ('config.json.example', '.'), ('gm_templates.json', '.'), ('gm_templates.json.backup', '.'), ('item_ids.json', '.'), ('connections.json', '.'), ('connections.json.backup', '.'), ('user_connections.json', '.'), ('license.key', '.')],
    hiddenimports=['pkgutil'],
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
    name='start_gui_secure_new',
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
