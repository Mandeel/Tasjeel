# -*- mode: python ; coding: utf-8 -*-

import os
import sys

from pathlib import Path

from pylibdmtx import pylibdmtx
from pyzbar import pyzbar
import cffi
import _cffi_backend
import qtawesome as qta

block_cipher = None

all_hidden_imports = _cffi_backend # + ....

a = Analysis(
    ['tasjeel.py'],
    pathex=[],
    binaries=[],
    datas=[("src/pyqt/MainMenuGUI.ui", "src/pyqt"),("src/pyqt/AboutMenuGUI.ui", "src/pyqt"),("src/logo/Sadiq150x150.png","src/logo"),("src/logo/Alrafifain150x150.png","src/logo"), ("src/sounds/notification.mp3","src/sounds"),
    ("src/sounds/wrong-answer.mp3","src/sounds"), ("src/version/version.txt","src/version"), ("src/font/Cairo-Medium.ttf", "src/font"),
    ("src/icons/tasjeel.png","src/icons")],
	hiddenimports=['_cffi_backend'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)


a.binaries += TOC([
    (Path(dep._name).name, dep._name, 'BINARY')
    for dep in pylibdmtx.EXTERNAL_DEPENDENCIES + pyzbar.EXTERNAL_DEPENDENCIES
])


pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Tasjeel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon='src/icons/tasjeel.png'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Tasjeel',
)
