# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get the directory where the spec file is located
spec_root = os.path.dirname(SPEC)

# Define data files to include
datas = [
    (os.path.join(spec_root, 'ui'), 'ui'),  # Include the entire ui folder
    (os.path.join(spec_root, 'eye.png'), '.'),  # Include the icon
    (os.path.join(spec_root, 'har_and_cookies'), 'har_and_cookies'),  # Include har_and_cookies folder
]

# Add any other data files from dependencies if needed
# datas += collect_data_files('pywebview')

a = Analysis(
    ['main.py'],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.cef',
        'webview.platforms.edgechromium',
        'screen_capture_api',
        'window_manager',
        'mouse_handler',
        'ai',
        'ai_checks',
        'image_text',
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
    name='InvisAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console output for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, 'eye.png'),  # Set the application icon
)
