# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['teams_connex/launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/*', 'resources')],
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
    [],
    exclude_binaries=True,
    name='TeamConnex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='x86_64',
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
app = BUNDLE(
    coll,
    name='Teams Connex.app',
    icon='resources/app-icon.icns',
    bundle_identifier='ninja.neon',
    version='1',
    info_plist={
        'LSUIElement': True,
    },
)
