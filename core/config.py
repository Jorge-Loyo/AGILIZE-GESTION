from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # Base de Datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "agilize_gestion")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Aplicación
    APP_NAME = os.getenv("APP_NAME", "Agilize Gestión")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    # Seguridad
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-cambiar")
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))


settings = Settings()
