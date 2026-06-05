# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para Agilize Gestion.
Uso: pyinstaller agilize.spec
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(os.path.abspath('.')).resolve()

a = Analysis(
    ['main.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[
        ('ui/styles', 'ui/styles'),
        ('assets', 'assets'),
        ('alembic', 'alembic'),
        ('alembic.ini', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'qtawesome',
        'psycopg2',
        'bcrypt',
        'loguru',
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'openpyxl',
        'sqlalchemy',
        'alembic',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AgilizeGestion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/logos/agilize_dev.jpg',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AgilizeGestion',
)
