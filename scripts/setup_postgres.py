"""
Script para descargar, configurar e iniciar PostgreSQL portable.
Se ejecuta como parte del instalador. Garantiza que PostgreSQL
quede funcionando sin intervención del usuario.
"""
import os
import sys
import subprocess
import zipfile
import urllib.request
import ssl
import shutil
import time
import socket
from pathlib import Path

# PostgreSQL portable - multiples versiones/URLs como fallback
PG_DOWNLOADS = [
    {
        "version": "16.9-1",
        "url": "https://get.enterprisedb.com/postgresql/postgresql-16.9-1-windows-x64-binaries.zip",
        "zip_name": "postgresql-16.9-1-windows-x64-binaries.zip",
    },
    {
        "version": "16.8-1",
        "url": "https://get.enterprisedb.com/postgresql/postgresql-16.8-1-windows-x64-binaries.zip",
        "zip_name": "postgresql-16.8-1-windows-x64-binaries.zip",
    },
    {
        "version": "15.13-1",
        "url": "https://get.enterprisedb.com/postgresql/postgresql-15.13-1-windows-x64-binaries.zip",
        "zip_name": "postgresql-15.13-1-windows-x64-binaries.zip",
    },
]

DB_NAME = "agilize_gestion"
DB_PORT = "5432"


def setup_postgres(install_dir: str, db_password: str = "agilize2025", progress_callback=None):
    """
    Descarga, configura e inicia PostgreSQL portable.
    Retorna dict con info de conexion.
    """
    pg_dir = os.path.join(install_dir, "pgsql")
    data_dir = os.path.join(install_dir, "pgdata")
    pg_bin = os.path.join(pg_dir, "bin")

    def log(msg):
        if progress_callback:
            progress_callback(msg)
        print(msg)

    # 1. Obtener binarios de PostgreSQL
    if not os.path.exists(os.path.join(pg_bin, "postgres.exe")):
        _download_and_extract(install_dir, pg_dir, log)

    if not os.path.exists(os.path.join(pg_bin, "postgres.exe")):
        raise Exception("No se encontraron binarios de PostgreSQL despues de la descarga.")

    # 2. Inicializar data directory
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

        # Configurar red y password
        _configure_network(data_dir)
        log("[OK] Configurado para red local")
        _set_password(pg_bin, data_dir, db_password)
        log("[OK] Password configurado")
    else:
        log("[OK] Data directory ya existe")

    # 3. Iniciar PostgreSQL
    log("Iniciando PostgreSQL...")
    _start_postgres(pg_bin, data_dir)

    # Verificar que realmente responde
    if not _wait_for_port("localhost", int(DB_PORT), timeout=15):
        raise Exception("PostgreSQL inicio pero no responde en puerto 5432")
    log("[OK] PostgreSQL corriendo en puerto 5432")

    # 4. Crear BD
    log("Verificando base de datos de la aplicacion...")
    _create_app_db(pg_bin, db_password)
    log("[OK] Base de datos lista")

    # 5. Firewall
    _add_firewall_rule(log)

    return {
        "host": "localhost",
        "port": DB_PORT,
        "user": "postgres",
        "password": db_password,
        "db_name": DB_NAME,
        "pg_bin": pg_bin,
        "data_dir": data_dir,
    }


def _download_and_extract(install_dir: str, pg_dir: str, log):
    """Intenta descargar PostgreSQL desde multiples URLs."""
    # Crear contexto SSL permisivo por si hay problemas de certificados corporativos
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for pg in PG_DOWNLOADS:
        pg_zip = os.path.join(install_dir, pg["zip_name"])
        url = pg["url"]
        log(f"Descargando PostgreSQL {pg['version']}...")
        log(f"  URL: {url}")

        try:
            # Intentar con SSL normal primero
            try:
                urllib.request.urlretrieve(url, pg_zip, _download_progress(log))
            except (urllib.error.URLError, ssl.SSLError):
                # Reintentar sin verificacion SSL
                log("  Reintentando sin verificacion SSL...")
                opener = urllib.request.build_opener(
                    urllib.request.HTTPSHandler(context=ctx)
                )
                with opener.open(url, timeout=120) as response:
                    total = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    block_size = 1024 * 256
                    with open(pg_zip, 'wb') as f:
                        while True:
                            chunk = response.read(block_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                pct = int(downloaded * 100 / total)
                                if pct % 10 == 0:
                                    log(f"  Descargando... {pct}% ({downloaded // (1024*1024)}MB)")

            # Verificar que se descargo
            if not os.path.exists(pg_zip) or os.path.getsize(pg_zip) < 10_000_000:
                log(f"  [WARN] Archivo muy pequeno o no descargado, intentando siguiente URL...")
                if os.path.exists(pg_zip):
                    os.remove(pg_zip)
                continue

            # Extraer
            log("Extrayendo PostgreSQL...")
            with zipfile.ZipFile(pg_zip, 'r') as zf:
                zf.extractall(install_dir)

            # Limpiar zip
            if os.path.exists(pg_zip):
                os.remove(pg_zip)

            # Verificar extraccion
            if os.path.exists(os.path.join(pg_dir, "bin", "postgres.exe")):
                log(f"[OK] PostgreSQL {pg['version']} extraido correctamente")
                return
            else:
                log("  [WARN] Extraccion incompleta, intentando siguiente URL...")
                if os.path.exists(pg_dir):
                    shutil.rmtree(pg_dir, ignore_errors=True)

        except Exception as e:
            log(f"  [WARN] Fallo con {pg['version']}: {e}")
            if os.path.exists(pg_zip):
                os.remove(pg_zip)
            continue

    raise Exception(
        "No se pudo descargar PostgreSQL desde ninguna fuente.\n"
        "Verifica tu conexion a internet.\n"
        "Alternativa: descargalo manualmente desde https://www.postgresql.org/download/windows/"
    )


def _download_progress(log_fn):
    """Callback para mostrar progreso de descarga."""
    last_pct = [-1]

    def reporthook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, int(block_num * block_size * 100 / total_size))
            if percent >= last_pct[0] + 10:
                last_pct[0] = percent
                mb = block_num * block_size // (1024 * 1024)
                log_fn(f"  Descargando... {percent}% ({mb}MB)")
    return reporthook


def _configure_network(data_dir: str):
    """Configura PostgreSQL para aceptar conexiones de red local."""
    hba_path = os.path.join(data_dir, "pg_hba.conf")
    with open(hba_path, "a") as f:
        f.write("\n# Red local - Agilize Gestion\n")
        f.write("host all all 0.0.0.0/0 md5\n")
        f.write("host all all ::0/0 md5\n")

    conf_path = os.path.join(data_dir, "postgresql.conf")
    with open(conf_path, "a") as f:
        f.write("\n# Agilize Gestion - Red local\n")
        f.write("listen_addresses = '*'\n")
        f.write(f"port = {DB_PORT}\n")


def _set_password(pg_bin: str, data_dir: str, password: str):
    """Inicia PG temporalmente para setear password."""
    pg_ctl = os.path.join(pg_bin, "pg_ctl.exe")
    psql = os.path.join(pg_bin, "psql.exe")

    # Iniciar temporalmente
    subprocess.run(
        [pg_ctl, "start", "-D", data_dir, "-w", "-o", f"-p {DB_PORT}"],
        capture_output=True, text=True
    )
    _wait_for_port("localhost", int(DB_PORT), timeout=10)

    # Setear password
    subprocess.run(
        [psql, "-U", "postgres", "-p", DB_PORT, "-c",
         f"ALTER USER postgres PASSWORD '{password}';"],
        capture_output=True, text=True
    )

    # Detener
    subprocess.run(
        [pg_ctl, "stop", "-D", data_dir, "-w"],
        capture_output=True, text=True
    )
    time.sleep(1)


def _start_postgres(pg_bin: str, data_dir: str):
    """Inicia PostgreSQL si no esta corriendo."""
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
        [pg_ctl, "start", "-D", data_dir, "-w", "-o", f"-p {DB_PORT}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Error iniciando PostgreSQL: {result.stderr}")


def _wait_for_port(host: str, port: int, timeout: int = 10) -> bool:
    """Espera a que un puerto este disponible."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def _create_app_db(pg_bin: str, password: str):
    """Crea la base de datos de la app si no existe."""
    psql = os.path.join(pg_bin, "psql.exe")
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    result = subprocess.run(
        [psql, "-U", "postgres", "-p", DB_PORT, "-tc",
         f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'"],
        capture_output=True, text=True, env=env
    )

    if "1" not in result.stdout:
        subprocess.run(
            [psql, "-U", "postgres", "-p", DB_PORT, "-c",
             f"CREATE DATABASE {DB_NAME};"],
            capture_output=True, text=True, env=env
        )


def _add_firewall_rule(log):
    """Agrega regla de firewall para permitir conexiones al puerto de PostgreSQL."""
    try:
        # Verificar si ya existe
        check = subprocess.run(
            'netsh advfirewall firewall show rule name="Agilize - PostgreSQL"',
            shell=True, capture_output=True, text=True
        )
        if "Agilize - PostgreSQL" in check.stdout:
            return

        subprocess.run(
            f'netsh advfirewall firewall add rule name="Agilize - PostgreSQL" '
            f'dir=in action=allow protocol=TCP localport={DB_PORT}',
            shell=True, capture_output=True
        )
        log("[OK] Regla de firewall creada (puerto 5432)")
    except Exception:
        log("[WARN] No se pudo crear regla de firewall (ejecutar como admin)")


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

    # Tarea programada
    cmd = (
        f'schtasks /create /tn "AgilizeGestion_PostgreSQL" '
        f'/tr "\"{pg_ctl}\" start -D \"{data_dir}\" -w" '
        f'/sc onlogon /rl highest /f'
    )
    subprocess.run(cmd, shell=True, capture_output=True)

    # Tambien crear un .bat de arranque manual por si falla la tarea
    bat_path = os.path.join(install_dir, "iniciar_postgres.bat")
    with open(bat_path, "w") as f:
        f.write(f'@echo off\n')
        f.write(f'echo Iniciando PostgreSQL...\n')
        f.write(f'"{pg_ctl}" start -D "{data_dir}" -w\n')
        f.write(f'echo PostgreSQL iniciado.\n')
        f.write(f'pause\n')


if __name__ == "__main__":
    install_dir = os.path.join(os.environ.get("LOCALAPPDATA", "."), "AgilizeGestion")
    info = setup_postgres(install_dir)
    print(f"\nConexion: {info}")
