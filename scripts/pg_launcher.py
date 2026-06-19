"""
Launcher que inicia PostgreSQL portable (si existe) antes de la app.
Si no fue inicializado durante la instalacion, lo hace ahora.
"""
import os
import sys
import subprocess
import socket
import time
from pathlib import Path


def start_postgres_if_needed():
    """Inicia PostgreSQL portable si existe en el directorio."""
    app_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
    pg_ctl = app_dir / "pgsql" / "bin" / "pg_ctl.exe"
    data_dir = app_dir / "pgdata"
    initdb = app_dir / "pgsql" / "bin" / "initdb.exe"
    psql = app_dir / "pgsql" / "bin" / "psql.exe"

    if not pg_ctl.exists():
        return  # No hay PG portable

    # Si no hay pgdata, inicializar ahora
    if not (data_dir / "PG_VERSION").exists():
        if not initdb.exists():
            return
        # Crear pgdata
        data_dir.mkdir(exist_ok=True)
        subprocess.run(
            [str(initdb), "-D", str(data_dir), "-U", "postgres", "-E", "UTF8", "--locale=C"],
            capture_output=True, text=True
        )
        # Configurar red
        if (data_dir / "pg_hba.conf").exists():
            with open(data_dir / "pg_hba.conf", "a") as f:
                f.write("\nhost all all 0.0.0.0/0 md5\n")
                f.write("host all all ::0/0 md5\n")
        if (data_dir / "postgresql.conf").exists():
            with open(data_dir / "postgresql.conf", "a") as f:
                f.write("\nlisten_addresses = '*'\nport = 5432\n")

    if not (data_dir / "PG_VERSION").exists():
        return  # initdb fallo

    # Verificar si ya corre
    result = subprocess.run(
        [str(pg_ctl), "status", "-D", str(data_dir)],
        capture_output=True, text=True
    )
    if "server is running" in result.stdout.lower():
        return

    # Verificar si el puerto esta libre
    if _port_in_use(5432):
        return  # Otro PostgreSQL ya usa el puerto

    # Iniciar
    subprocess.run(
        [str(pg_ctl), "start", "-D", str(data_dir), "-w", "-o", "-p 5432"],
        capture_output=True, text=True
    )
    time.sleep(2)

    # Si es primera vez, setear password y crear BD
    if psql.exists() and not (data_dir / ".agilize_initialized").exists():
        env = os.environ.copy()
        subprocess.run(
            [str(psql), "-U", "postgres", "-h", "localhost", "-p", "5432", "-w",
             "-c", "ALTER USER postgres PASSWORD 'agilize2025';"],
            capture_output=True, text=True, env=env
        )
        subprocess.run(
            [str(psql), "-U", "postgres", "-h", "localhost", "-p", "5432", "-w",
             "-c", "CREATE DATABASE agilize_gestion;"],
            capture_output=True, text=True, env=env
        )
        # Marcar como inicializado
        try:
            (data_dir / ".agilize_initialized").write_text("ok")
        except Exception:
            pass


def _port_in_use(port: int) -> bool:
    """Verifica si un puerto TCP esta en uso."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        return result == 0
    except Exception:
        return False


if __name__ == "__main__":
    start_postgres_if_needed()
