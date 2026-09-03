# -*- mode: python ; coding: utf-8 -*-


# La collezione dei suoni condivisa va portata dentro il pacchetto, altrimenti
# Acusticator non la trova e l'eseguibile resta senza i suoni presi da li'.
# E' il difetto che ha tenuto muto batnav compilato fino alla 2.4.0.
import os

import GBUtils

COLLEZIONE = os.path.join(os.path.dirname(GBUtils.__file__), 'Acu_Collection.json')

a = Analysis(
    ['batnav.py'],
    pathex=[],
    binaries=[],
    datas=[(COLLEZIONE, '.')],
    hiddenimports=[],
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
    name='batnav',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
