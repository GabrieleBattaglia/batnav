# -*- mode: python ; coding: utf-8 -*-
# batnav, ricetta di compilazione.
# Autori: Gabriele Battaglia (IZ4APU) & ClaudIA (Claude Fable 5.1, UltraCode).
# La collezione dei suoni condivisa va portata dentro il pacchetto, altrimenti
# Acusticator non la trova e l'eseguibile resta senza i suoni presi da li'.
# E' il difetto che ha tenuto muto batnav compilato fino alla 2.4.0.
# Il manuale viaggia anch'esso dentro l'eseguibile, che e' un file unico.
import os

import GBUtils

COLLEZIONE = os.path.join(os.path.dirname(GBUtils.__file__), 'Acu_Collection.json')
MANUALE = os.path.join(SPECPATH, 'README.md')

a = Analysis(
    ['batnav.py'],
    pathex=[],
    binaries=[],
    datas=[(COLLEZIONE, '.'), (MANUALE, '.')],
    # requests e compagni servono al controllo aggiornamenti di GBUtils:
    # senza, l'eseguibile parte ma non riesce a contattare GitHub.
    # scipy.signal lo importa Acusticator dentro le funzioni, quindi
    # PyInstaller non lo trova da solo: senza, l'eseguibile si chiude al
    # primo suono con ModuleNotFoundError. Non toglierli.
    hiddenimports=[
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'chardet',
        'scipy.signal',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # batnav usa numpy, scipy, sounddevice e la libreria standard. Le
    # interfacce grafiche arriverebbero seguendo le catene di import di
    # GBUtils, che qui non si usano.
    excludes=[
        'wx',
        'PyQt5',
        'PySide2',
        'PySide6',
        'matplotlib',
        'IPython',
        'notebook',
        'nbconvert',
        'qtpy',
        'pytest',
        'tkinter',
    ],
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
