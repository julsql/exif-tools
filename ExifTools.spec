# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = [
    ('assets', 'assets'),
    ('editor/map_leaflet.html', 'editor'),
]

hiddenimports = []

# Dépendances lourdes : on collecte SANS casser le bootloader
for pkg in ("birder", "torch", "torchvision"):
    _, _, hidden = collect_all(pkg)
    hiddenimports += hidden

hiddenimports += collect_submodules("PyQt6")
hiddenimports += collect_submodules("PyQt6.QtWebEngineCore")
hiddenimports += collect_submodules("PyQt6.QtWebEngineWidgets")
hiddenimports += collect_submodules("PyQt6.QtWebChannel")
hiddenimports += ["PyQt6.sip", "onnxscript.ir"]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],          # ⚠️ laisser vide en onefile Linux
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ExifTools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
