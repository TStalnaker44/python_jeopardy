# Run from the repository root: python -m PyInstaller --clean --noconfirm Jeopardy.spec
from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / "launcher.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(root / "questions"), "questions"),
           (str(root / "resources"), "resources"),
           (str(root / "utils" / "menuButtons.csv"), "utils"),
           (str(root / "LICENSE"), ".")],
    hiddenimports=["jeopardyGame"],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[],
    noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="Jeopardy", debug=False, bootloader_ignore_signals=False,
    strip=False, upx=True, upx_exclude=[], runtime_tmpdir=None,
    console=False, disable_windowed_traceback=False, argv_emulation=False,
    target_arch=None, codesign_identity=None, entitlements_file=None,
    icon=[str(root / "resources" / "images" / "jeopardy_window_icon.png")],
)
