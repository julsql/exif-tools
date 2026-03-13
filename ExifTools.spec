from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

datas = [
    ('assets', 'assets'),
    ('editor/map_leaflet.html', 'editor'),
]
binaries = []
hiddenimports = [
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebChannel',
    ]

hiddenimports += collect_submodules("PyQt6")
hiddenimports += collect_submodules("PyQt6.QtWebEngineCore")
hiddenimports += collect_submodules("PyQt6.QtWebEngineWidgets")
hiddenimports += collect_submodules("PyQt6.QtWebChannel")
hiddenimports += ["PyQt6.sip"]
hiddenimports += ["onnxscript.ir"]

for pkg in ("birder", "torch", "torchvision"):
    tmp = collect_all(pkg)
    datas += tmp[0]
    binaries += tmp[1]
    hiddenimports += tmp[2]

import sys
if sys.platform.startswith("win"):
    excludes = ["onnxscript", "onnx", "torch", "torchvision"]
else:
    excludes = []

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ExifTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon="assets/icon.icns",
)

app = BUNDLE(
    exe,
    name="ExifTools.app",
    icon="assets/icon.icns",
    bundle_identifier="com.julsql.exiftools",
)
