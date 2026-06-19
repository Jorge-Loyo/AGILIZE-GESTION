from pathlib import Path
import os
import sys


def _get_base_dir() -> Path:
    """Retorna el directorio base tanto en desarrollo como compilado."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent.parent


def _parse_env_file(env_path: Path) -> dict:
    """Lee y parsea un archivo .env manualmente, manejando cualquier encoding."""
    result = {}
    try:
        raw = env_path.read_bytes()

        # Detectar encoding
        if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            text = raw.decode('utf-16')
        elif raw[:3] == b'\xef\xbb\xbf':
            text = raw.decode('utf-8-sig')
        else:
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                text = raw.decode('latin-1')

        # Reescribir como UTF-8 limpio
        try:
            env_path.write_bytes(text.encode('utf-8'))
        except Exception:
            pass

        # Parsear lineas
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key:
                    result[key] = value
    except Exception:
        pass
    return result


BASE_DIR = _get_base_dir()

# Cargar .env
_env_data = {}
env_path = BASE_DIR / ".env"
if env_path.exists():
    _env_data = _parse_env_file(env_path)
else:
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        _env_data = _parse_env_file(cwd_env)

# Setear en os.environ para compatibilidad
for k, v in _env_data.items():
    os.environ.setdefault(k, v)


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
