"""
Script de build para generar ejecutable de Agilize Gestion.
Uso:
    python scripts/build.py

Genera ejecutable en dist/AgilizeGestion/
"""
import subprocess
import sys
import platform
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ICON_PATH = BASE_DIR / "assets" / "logos" / "agilize_dev.jpg"
MAIN_FILE = BASE_DIR / "main.py"
APP_NAME = "AgilizeGestion"


def build():
    system = platform.system()
    print(f"[BUILD] Sistema: {system}")
    print(f"[BUILD] Generando ejecutable...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--windowed",
        "--noconfirm",
        "--clean",
        # Incluir archivos necesarios
        "--add-data", f"{BASE_DIR / 'ui' / 'styles'}{os.pathsep}ui/styles",
        "--add-data", f"{BASE_DIR / 'assets'}{os.pathsep}assets",
        "--add-data", f"{BASE_DIR / 'alembic'}{os.pathsep}alembic",
        "--add-data", f"{BASE_DIR / 'alembic.ini'}{os.pathsep}.",
        "--add-data", f"{BASE_DIR / '.env.example'}{os.pathsep}.",
        # Imports ocultos que PyInstaller no detecta
        "--hidden-import", "PySide6.QtSvg",
        "--hidden-import", "qtawesome",
        "--hidden-import", "psycopg2",
        "--hidden-import", "bcrypt",
        "--hidden-import", "loguru",
        "--hidden-import", "reportlab",
        "--hidden-import", "openpyxl",
    ]

    # Icono solo en Windows
    if system == "Windows" and ICON_PATH.exists():
        # Convertir a .ico si es necesario
        cmd.extend(["--icon", str(ICON_PATH)])

    cmd.append(str(MAIN_FILE))

    print(f"[BUILD] Comando: {' '.join(cmd[:5])}...")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))

    if result.returncode == 0:
        print(f"\n[OK] Ejecutable generado en: dist/{APP_NAME}/")
        print(f"[OK] Para ejecutar: dist/{APP_NAME}/{APP_NAME}{'.exe' if system == 'Windows' else ''}")
    else:
        print(f"\n[ERROR] Build fallo con codigo {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    import os
    build()
