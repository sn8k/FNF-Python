# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path


ROOT = Path(SPECPATH).resolve().parents[1]
EXCLUDES = [
    "clr",
    "clr_loader",
    "jinja2",
    "numpy",
    "OpenGL",
    "PIL",
    "pkg_resources",
    "psutil",
    "pygments",
    "pyreadline3",
    "pytest",
    "pythoncom",
    "pythonnet",
    "pywintypes",
    "setuptools",
    "win32com",
    "yaml",
]


def build_datas():
    datas = []
    for directory_name in ("assets", "data", "DOCS"):
        directory = ROOT / directory_name
        if directory.exists():
            datas.append((str(directory), directory_name))

    for file_name in ("README.md", "CHANGELOG.md", "requirements.txt"):
        file_path = ROOT / file_name
        if file_path.exists():
            datas.append((str(file_path), "."))

    return datas


a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=build_datas(),
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FNF-Python-Debug",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    contents_directory=".",
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="FNF-Python-debug",
)
