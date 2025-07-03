# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Get the directory where the spec file is located
spec_root = os.path.dirname(SPEC)

# Define data files to include
datas = [
    (os.path.join(spec_root, 'ui'), 'ui'),  # Include the entire ui folder
    (os.path.join(spec_root, 'google-eye.png'), '.'), 
    (os.path.join(spec_root, 'google-eye.ico'), '.'),  # Include the ICO icon
    (os.path.join(spec_root, 'notepad.ico'), '.'),  # Include the ICO notepad icon
]

# Define binary files to include
binaries = [
    (os.path.join(spec_root, 'chromedriver.exe'), '.'),  # Include the ChromeDriver executable
]

# Add any other data files from dependencies if needed
datas += collect_data_files('webview')
datas += collect_data_files('g4f', includes=['**/*.json', '**/*.txt', '**/*.py'])

a = Analysis(
    ['main.py'],
    pathex=[spec_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'webview',
        'webview.platforms.winforms',
        'webview.platforms.cef',
        'webview.platforms.edgechromium',
        'webview.platforms.mshtml',
        'webview.platforms.gtk',
        'webview.platforms.qt',
        'webview.util',
        'webview.js',
        'apis.screen_capture_api',
        'window_manager',
        'ai.ai',
        'ai.ai_checks',
        'utils.image_text',
        'apis.main_api',
        'apis.window_api',
        'apis.mouse_events_api',
        'other.settings_manager',
        'other.loading_screen',
        'utils.app_utils',
        'other.har_capture',
        'utils.path_utils',
        'g4f',
        'g4f.cookies',
        'g4f.models',
        'g4f.Provider',
        'g4f.providers',
        'browser_cookie3',
        'shadowcopy',
        'wmi',
        'pythoncom',
        'win32com',
        'win32com.client',
        'pywintypes',
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
    console=False,  # Enable console for debugging ChromeDriver issues
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(spec_root, 'google-eye.ico'),  # Set the application icon
    onefile=True,  # Create a single executable file
)
