"""
Launcher que inicia PostgreSQL portable (si existe) antes de la app.
Se usa como entry point cuando hay PG embebido.
"""
import os
import sys
import subprocess
import time
from pathlib import Path


def start_postgres_if_needed():
    """Inicia PostgreSQL portable si existe en el directorio."""
    app_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
    pg_ctl = app_dir / "pgsql" / "bin" / "pg_ctl.exe"
    data_dir = app_dir / "pgdata"

    if not pg_ctl.exists() or not data_dir.exists():
        return  # No hay PG portable, usa BD externa

    # Verificar si ya corre
    result = subprocess.run(
        [str(pg_ctl), "status", "-D", str(data_dir)],
        capture_output=True, text=True
    )
    if "server is running" in result.stdout.lower():
        return  # Ya está corriendo

    # Iniciar
    subprocess.run(
        [str(pg_ctl), "start", "-D", str(data_dir), "-w", "-o", "-p 5432"],
        capture_output=True, text=True
    )
    time.sleep(1)  # Dar tiempo a iniciar


if __name__ == "__main__":
    start_postgres_if_needed()
