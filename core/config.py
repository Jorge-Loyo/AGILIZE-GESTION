from pathlib import Path
from dotenv import load_dotenv
import os
import sys
import io


def _get_base_dir() -> Path:
    """Retorna el directorio base tanto en desarrollo como compilado."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent


def _load_env_safe(env_path: Path):
    """Carga .env manejando cualquier encoding de Windows."""
    try:
        # Leer como bytes para detectar encoding
        raw = env_path.read_bytes()

        # Detectar y convertir BOM UTF-16
        if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            content = raw.decode('utf-16')
        elif raw[:3] == b'\xef\xbb\xbf':
            content = raw.decode('utf-8-sig')
        else:
            # Intentar UTF-8, si falla usar latin-1 (nunca falla)
            try:
                content = raw.decode('utf-8')
            except UnicodeDecodeError:
                content = raw.decode('latin-1')

        # Reescribir el archivo como UTF-8 limpio para que no vuelva a fallar
        env_path.write_text(content, encoding='utf-8')

        # Cargar con dotenv
        load_dotenv(env_path, encoding='utf-8')
    except Exception:
        # Ultimo recurso: cargar sin especificar encoding
        load_dotenv(env_path)


BASE_DIR = _get_base_dir()

# Cargar .env desde el directorio de la app
env_path = BASE_DIR / ".env"
if env_path.exists():
    _load_env_safe(env_path)
else:
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        _load_env_safe(cwd_env)


class Settings:
    # Base de Datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "agilize_gestion")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "agilize2025")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Aplicacion
    APP_NAME = os.getenv("APP_NAME", "Agilize Gestion")
    APP_VERSION = os.getenv("APP_VERSION", "2.1.0")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-cambiar")
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))


settings = Settings()
