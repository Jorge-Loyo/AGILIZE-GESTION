import base64
import tempfile
from pathlib import Path
from core.config import BASE_DIR

DEFAULT_LOGO = str(BASE_DIR / "assets" / "logos" / "agilize_dev.jpg")
APP_ICON = str(BASE_DIR / "assets" / "logos" / "app_icon.ico")

_cache: dict[str, str] = {}


def get_app_icon_path() -> str:
    if Path(APP_ICON).exists():
        return APP_ICON
    return get_dev_logo_path()


def get_dev_logo_path() -> str:
    """Retorna path al logo dev. Primero intenta base64 de BD, luego archivo."""
    if "dev" in _cache and Path(_cache["dev"]).exists():
        return _cache["dev"]
    try:
        from services.core.empresa_service import empresa_service
        b64 = empresa_service.obtener("dev_logo_base64")
        if b64:
            path = _b64_to_tempfile(b64, "dev_logo")
            _cache["dev"] = path
            return path
        # Fallback a ruta antigua
        path = empresa_service.obtener("dev_logo_path")
        if path and Path(path).exists():
            return path
    except Exception:
        pass
    if Path(DEFAULT_LOGO).exists():
        return DEFAULT_LOGO
    return ""


def get_empresa_logo_path() -> str:
    """Retorna path al logo empresa. Primero intenta base64 de BD, luego archivo."""
    if "empresa" in _cache and Path(_cache["empresa"]).exists():
        return _cache["empresa"]
    try:
        from services.core.empresa_service import empresa_service
        b64 = empresa_service.obtener("logo_base64")
        if b64:
            path = _b64_to_tempfile(b64, "empresa_logo")
            _cache["empresa"] = path
            return path
        # Fallback a ruta antigua
        path = empresa_service.obtener("logo_path")
        if path and Path(path).exists():
            return path
    except Exception:
        pass
    return ""


def _b64_to_tempfile(b64_str: str, prefix: str) -> str:
    """Decodifica base64 y lo guarda en un archivo temporal. Retorna el path."""
    img_bytes = base64.b64decode(b64_str)
    tmp = Path(tempfile.gettempdir()) / f"{prefix}.png"
    tmp.write_bytes(img_bytes)
    return str(tmp)
