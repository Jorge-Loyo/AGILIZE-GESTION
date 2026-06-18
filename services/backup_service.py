"""
Servicio de backup de base de datos.
Usa pg_dump/pg_restore o SQL puro como fallback.
"""
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from core.config import settings, BASE_DIR


def _find_pg_bin() -> str:
    """Busca el directorio bin de PostgreSQL."""
    # PostgreSQL portable de la app
    app_pg = Path(BASE_DIR) / "pgsql" / "bin"
    if app_pg.exists():
        return str(app_pg)

    # Instalacion del sistema
    for ver in ["18", "17", "16", "15", "14"]:
        path = Path(f"C:/Program Files/PostgreSQL/{ver}/bin")
        if path.exists():
            return str(path)

    # Buscar en PATH
    result = subprocess.run("where pg_dump", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return str(Path(result.stdout.strip().split('\n')[0]).parent)

    return ""


def crear_backup(destino: str = None) -> str:
    """
    Crea un backup de la base de datos.
    Retorna la ruta del archivo generado.
    """
    pg_bin = _find_pg_bin()
    if not pg_bin:
        raise Exception("No se encontro pg_dump. Verifica la instalacion de PostgreSQL.")

    pg_dump = os.path.join(pg_bin, "pg_dump.exe" if sys.platform == "win32" else "pg_dump")
    if not os.path.exists(pg_dump):
        raise Exception(f"pg_dump no encontrado en: {pg_bin}")

    # Directorio de backups
    backup_dir = Path(BASE_DIR) / "backups"
    backup_dir.mkdir(exist_ok=True)

    # Nombre del archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if destino:
        filepath = destino
    else:
        filepath = str(backup_dir / f"backup_{settings.DB_NAME}_{timestamp}.sql")

    # Ejecutar pg_dump
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.DB_PASSWORD

    cmd = [
        pg_dump,
        "-h", settings.DB_HOST,
        "-p", settings.DB_PORT,
        "-U", settings.DB_USER,
        "-d", settings.DB_NAME,
        "-f", filepath,
        "--no-owner",
        "--no-acl",
        "--encoding=UTF8",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise Exception(f"Error en pg_dump: {result.stderr}")

    return filepath


def restaurar_backup(filepath: str) -> str:
    """
    Restaura un backup SQL en la base de datos.
    """
    pg_bin = _find_pg_bin()
    if not pg_bin:
        raise Exception("No se encontro psql. Verifica la instalacion de PostgreSQL.")

    psql = os.path.join(pg_bin, "psql.exe" if sys.platform == "win32" else "psql")
    if not os.path.exists(psql):
        raise Exception(f"psql no encontrado en: {pg_bin}")

    if not os.path.exists(filepath):
        raise Exception(f"Archivo no encontrado: {filepath}")

    env = os.environ.copy()
    env["PGPASSWORD"] = settings.DB_PASSWORD

    cmd = [
        psql,
        "-h", settings.DB_HOST,
        "-p", settings.DB_PORT,
        "-U", settings.DB_USER,
        "-d", settings.DB_NAME,
        "-f", filepath,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0 and "ERROR" in result.stderr:
        raise Exception(f"Error en restauracion: {result.stderr[:500]}")

    return "Backup restaurado correctamente."


def listar_backups() -> list:
    """Lista los backups existentes."""
    backup_dir = Path(BASE_DIR) / "backups"
    if not backup_dir.exists():
        return []

    backups = []
    for f in sorted(backup_dir.glob("backup_*.sql"), reverse=True):
        size_mb = f.stat().st_size / (1024 * 1024)
        backups.append({
            "nombre": f.name,
            "ruta": str(f),
            "fecha": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y %H:%M"),
            "tamano": f"{size_mb:.1f} MB",
        })
    return backups
