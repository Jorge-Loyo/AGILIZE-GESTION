from pathlib import Path
from dotenv import load_dotenv
import os
import sys


def _get_base_dir() -> Path:
    """Retorna el directorio base tanto en desarrollo como compilado."""
    if getattr(sys, 'frozen', False):
        # Ejecutando como .exe (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Ejecutando como script Python
        return Path(__file__).resolve().parent.parent


BASE_DIR = _get_base_dir()

# Cargar .env desde el directorio de la app
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Buscar en el directorio de trabajo actual
    cwd_env = Path.cwd() / ".env"
    if cwd_env.exists():
        load_dotenv(cwd_env)


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
    APP_VERSION = os.getenv("APP_VERSION", "1.1.0")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-cambiar")
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))


settings = Settings()
