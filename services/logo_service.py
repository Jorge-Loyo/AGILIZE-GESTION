from pathlib import Path
from core.config import BASE_DIR

DEFAULT_LOGO = str(BASE_DIR / "assets" / "logos" / "agilize_dev.jpg")
APP_ICON = str(BASE_DIR / "assets" / "logos" / "app_icon.ico")


def get_app_icon_path() -> str:
    """Retorna el path del icono .ico de la app (para ventana y barra de tareas)."""
    if Path(APP_ICON).exists():
        return APP_ICON
    return get_dev_logo_path()


def get_dev_logo_path() -> str:
    """Retorna el path del logo del desarrollador (icono de la app)."""
    try:
        from services.empresa_service import empresa_service
        path = empresa_service.obtener("dev_logo_path")
        if path and Path(path).exists():
            return path
    except Exception:
        pass
    if Path(DEFAULT_LOGO).exists():
        return DEFAULT_LOGO
    return ""


def get_empresa_logo_path() -> str:
    """Retorna el path del logo de la empresa cliente."""
    try:
        from services.empresa_service import empresa_service
        path = empresa_service.obtener("logo_path")
        if path and Path(path).exists():
            return path
    except Exception:
        pass
    return ""
