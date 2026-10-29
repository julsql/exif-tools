# python
# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# "full" (avec IA, défaut) ou "lite" (sans torch/birder)
EDITION = os.environ.get("EXIFTOOLS_EDITION", "full").lower()
if sys.platform.startswith("win"):
    EDITION = "lite"  # torch non supporté dans le build Windows
AI_PACKAGES = ["birder", "torch", "torchvision", "onnx", "onnxscript"]

datas = [
    ('assets', 'assets'),
    ('editor/map_leaflet.html', 'editor'),
]
binaries = []
hiddenimports = []

if EDITION == "full":
    for pkg in ("birder", "torch", "torchvision"):
        tmp = collect_all(pkg)
        datas += tmp[0]
        binaries += tmp[1]
        hiddenimports += tmp[2]
    hiddenimports += ["onnxscript.ir"]

# Uniquement les modules Qt utilisés (les hooks PyInstaller tirent leurs dépendances Qt)
hiddenimports += [
    "PyQt6.sip",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "PyQt6.QtWidgets",
    "PyQt6.QtNetwork",
    "PyQt6.QtWebChannel",
    "PyQt6.QtWebEngineCore",
    "PyQt6.QtWebEngineWidgets",
]

# Bindings Qt inutilisés par l'app
QT_UNUSED = [
    "PyQt6.Qt3DAnimation",
    "PyQt6.Qt3DCore",
    "PyQt6.Qt3DExtras",
    "PyQt6.Qt3DInput",
    "PyQt6.Qt3DLogic",
    "PyQt6.Qt3DRender",
    "PyQt6.QtBluetooth",
    "PyQt6.QtCharts",
    "PyQt6.QtDataVisualization",
    "PyQt6.QtDBus",
    "PyQt6.QtDesigner",
    "PyQt6.QtHelp",
    "PyQt6.QtMultimedia",
    "PyQt6.QtMultimediaWidgets",
    "PyQt6.QtNfc",
    "PyQt6.QtPdfWidgets",
    "PyQt6.QtQuick3D",
    "PyQt6.QtRemoteObjects",
    "PyQt6.QtSensors",
    "PyQt6.QtSerialPort",
    "PyQt6.QtSpatialAudio",
    "PyQt6.QtSql",
    "PyQt6.QtStateMachine",
    "PyQt6.QtTest",
    "PyQt6.QtTextToSpeech",
    "PyQt6.uic",
]

excludes = QT_UNUSED + ([] if EDITION == "full" else AI_PACKAGES)

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

# Ménage post-analyse : fichiers Qt tirés par les hooks mais inutiles à l'app
KEEP_LOCALES = ("fr.pak", "en-US.pak")
DROP_PATTERNS = (
    "/qml/",
    "Quick3D",
    "QuickControls2",
    "QuickDialogs2",
    "QuickTemplates2",
    "QtMultimedia",
    "qtwebengine_devtools_resources",
)


def _keep(entry) -> bool:
    dest = entry[0].replace("\\", "/")
    if "qtwebengine_locales/" in dest:
        return dest.endswith(KEEP_LOCALES)
    return not any(p in dest for p in DROP_PATTERNS)


a.datas = [e for e in a.datas if _keep(e)]
a.binaries = [e for e in a.binaries if _keep(e)]

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