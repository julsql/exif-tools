# python
# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = [
    ('assets', 'assets'),
    ('editor/map_leaflet.html', 'editor'),
]
binaries = []
hiddenimports = []

for pkg in ("birder", "torch", "torchvision"):
    tmp = collect_all(pkg)
    datas += tmp[0]
    binaries += tmp[1]
    hiddenimports += tmp[2]

hiddenimports += collect_submodules("PyQt6")
hiddenimports += collect_submodules("PyQt6.QtWebEngineCore")
hiddenimports += collect_submodules("PyQt6.QtWebEngineWidgets")
hiddenimports += collect_submodules("PyQt6.QtWebChannel")
hiddenimports += ["PyQt6.sip"]
hiddenimports += ["onnxscript.ir"]

import sys
if sys.platform.startswith("win"):
    excludes = ["onnxscript", "onnx", "torch", "torchvision"]
else:
    excludes = []

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

version_file = os.path.join("build", "version_info.txt")
exe_kwargs = {}
if os.path.exists(version_file):
    exe_kwargs["version"] = version_file

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ExifTools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    **exe_kwargs,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name="ExifTools",
)

app = BUNDLE(
    coll,
    name="ExifTools.app",
    icon="assets/icon.icns",
    bundle_identifier="com.julsql.exiftools",
)