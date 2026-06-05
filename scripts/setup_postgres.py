"""
Script para descargar, configurar e iniciar PostgreSQL portable.
Se ejecuta como parte del instalador.
"""
import os
import sys
import subprocess
import zipfile
import urllib.request
import shutil
from pathlib import Path

# PostgreSQL 16 portable (binaries zip oficial)
PG_VERSION = "16.9-1"
PG_URL = f"https://get.enterprisedb.com/postgresql/postgresql-{PG_VERSION}-windows-x64-binaries.zip"
PG_ZIP_NAME = f"postgresql-{PG_VERSION}-windows-x64-binaries.zip"


def setup_postgres(install_dir: str, db_password: str = "agilize2025", progress_callback=None):
    """
    Descarga, configura e inicia PostgreSQL portable.
    Retorna dict con info de conexion.
    """
    pg_dir = os.path.join(install_dir, "pgsql")
    data_dir = os.path.join(install_dir, "pgdata")
    pg_bin = os.path.join(pg_dir, "bin")
    pg_zip = os.path.join(install_dir, PG_ZIP_NAME)

    def log(msg):
        if progress_callback:
            progress_callback(msg)
        print(msg)

    # 1. Descargar si no existe
    if not os.path.exists(os.path.join(pg_bin, "postgres.exe")):
        if not os.path.exists(pg_zip):
            log("Descargando PostgreSQL (esto puede tardar)...")
            try:
                urllib.request.urlretrieve(PG_URL, pg_zip, _download_progress(log))
            except Exception as e:
                log(f"Error descargando: {e}")
                # Intentar URL alternativa
                alt_url = f"https://sbp.enterprisedb.com/getfile.jsp?fileid=1259310"
                try:
                    urllib.request.urlretrieve(alt_url, pg_zip)
                except Exception:
                    raise Exception(
                        "No se pudo descargar PostgreSQL.\n"
                        "Descargalo manualmente desde https://www.postgresql.org/download/\n"
                        "y coloca los binarios en la carpeta pgsql/"
                    )

        # 2. Extraer
        log("Extrayendo PostgreSQL...")
        with zipfile.ZipFile(pg_zip, 'r') as zf:
            zf.extractall(install_dir)
        # El zip extrae en "pgsql/" directamente
        if os.path.exists(pg_zip):
            os.remove(pg_zip)
        log("[OK] PostgreSQL extraido")

    # 3. Inicializar data si no existe
    if not os.path.exists(os.path.join(data_dir, "PG_VERSION")):
        log("Inicializando base de datos...")
        initdb = os.path.join(pg_bin, "initdb.exe")
        env = os.environ.copy()
        env["PGDATA"] = data_dir
        result = subprocess.run(
            [initdb, "-D", data_dir, "-U", "postgres", "-E", "UTF8", "--locale=C"],
            capture_output=True, text=True, env=env
        )
        if result.returncode != 0:
            raise Exception(f"Error initdb: {result.stderr}")
        log("[OK] Base de datos inicializada")

        # 4. Configurar para aceptar conexiones por red
        _configure_network(data_dir)
        log("[OK] Configurado para red local")

        # 5. Configurar password
        _set_password(pg_bin, data_dir, db_password)
        log("[OK] Password configurado")
    else:
        log("[OK] Base de datos ya existe")

    # 6. Iniciar PostgreSQL
    log("Iniciando PostgreSQL...")
    _start_postgres(pg_bin, data_dir)
    log("[OK] PostgreSQL corriendo en puerto 5432")

    # 7. Crear BD de la app si no existe
    log("Verificando base de datos de la aplicacion...")
    _create_app_db(pg_bin, db_password)
    log("[OK] Base de datos lista")

    return {
        "host": "localhost",
        "port": "5432",
        "user": "postgres",
        "password": db_password,
        "db_name": "agilize_gestion",
        "pg_bin": pg_bin,
        "data_dir": data_dir,
    }


def _download_progress(log_fn):
    """Callback para mostrar progreso de descarga."""
    def reporthook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, int(block_num * block_size * 100 / total_size))
            if percent % 10 == 0:
                log_fn(f"  Descargando... {percent}%")
    return reporthook


def _configure_network(data_dir: str):
    """Configura PostgreSQL para aceptar conexiones de red local."""
    # pg_hba.conf - permitir red local
    hba_path = os.path.join(data_dir, "pg_hba.conf")
    with open(hba_path, "a") as f:
        f.write("\n# Red local - Agilize Gestion\n")
        f.write("host all all 0.0.0.0/0 md5\n")
        f.write("host all all ::0/0 md5\n")

    # postgresql.conf - escuchar en todas las interfaces
    conf_path = os.path.join(data_dir, "postgresql.conf")
    with open(conf_path, "a") as f:
        f.write("\n# Agilize Gestion - Red local\n")
        f.write("listen_addresses = '*'\n")
        f.write("port = 5432\n")


def _set_password(pg_bin: str, data_dir: str, password: str):
    """Inicia PG temporalmente para setear password."""
    pg_ctl = os.path.join(pg_bin, "pg_ctl.exe")

    # Iniciar temporalmente
    subprocess.run(
        [pg_ctl, "start", "-D", data_dir, "-w", "-o", "-p 5432"],
        capture_output=True, text=True
    )

    # Setear password
    psql = os.path.join(pg_bin, "psql.exe")
    subprocess.run(
        [psql, "-U", "postgres", "-p", "5432", "-c", f"ALTER USER postgres PASSWORD '{password}';"],
        capture_output=True, text=True
    )

    # Detener
    subprocess.run(
        [pg_ctl, "stop", "-D", data_dir, "-w"],
        capture_output=True, text=True
    )


def _start_postgres(pg_bin: str, data_dir: str):
    """Inicia PostgreSQL si no está corriendo."""
    pg_ctl = os.path.join(pg_bin, "pg_ctl.exe")

    # Verificar si ya corre
    result = subprocess.run(
        [pg_ctl, "status", "-D", data_dir],
        capture_output=True, text=True
    )
    if "server is running" in result.stdout.lower():
        return

    # Iniciar
    result = subprocess.run(
        [pg_ctl, "start", "-D", data_dir, "-w", "-o", "-p 5432"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Error iniciando PostgreSQL: {result.stderr}")


def _create_app_db(pg_bin: str, password: str):
    """Crea la base de datos de la app si no existe."""
    psql = os.path.join(pg_bin, "psql.exe")
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    # Verificar si existe
    result = subprocess.run(
        [psql, "-U", "postgres", "-p", "5432", "-tc",
         "SELECT 1 FROM pg_database WHERE datname='agilize_gestion'"],
        capture_output=True, text=True, env=env
    )

    if "1" not in result.stdout:
        subprocess.run(
            [psql, "-U", "postgres", "-p", "5432", "-c",
             "CREATE DATABASE agilize_gestion;"],
            capture_output=True, text=True, env=env
        )


def stop_postgres(install_dir: str):
    """Detiene PostgreSQL portable."""
    pg_ctl = os.path.join(install_dir, "pgsql", "bin", "pg_ctl.exe")
    data_dir = os.path.join(install_dir, "pgdata")
    subprocess.run(
        [pg_ctl, "stop", "-D", data_dir, "-w"],
        capture_output=True, text=True
    )


def create_startup_task(install_dir: str):
    """Crea tarea programada para iniciar PostgreSQL al arrancar Windows."""
    pg_ctl = os.path.join(install_dir, "pgsql", "bin", "pg_ctl.exe")
    data_dir = os.path.join(install_dir, "pgdata")

    cmd = f'schtasks /create /tn "AgilizeGestion_PostgreSQL" /tr "\"{pg_ctl}\" start -D \"{data_dir}\" -w" /sc onlogon /rl highest /f'
    subprocess.run(cmd, shell=True, capture_output=True)


if __name__ == "__main__":
    # Test
    install_dir = os.path.join(os.environ.get("LOCALAPPDATA", "."), "AgilizeGestion")
    info = setup_postgres(install_dir)
    print(f"\nConexion: {info}")
