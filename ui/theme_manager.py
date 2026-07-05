from pathlib import Path
from PySide6.QtWidgets import QApplication

STYLES_DIR = Path(__file__).parent / "styles"


class ThemeManager:
    DARK = "dark"
    LIGHT = "light"

    def __init__(self):
        self.current = self.DARK

    def apply(self, app: QApplication, theme: str | None = None):
        if theme:
            self.current = theme
        qss_file = STYLES_DIR / f"{self.current}_theme.qss"
        app.setStyleSheet(qss_file.read_text(encoding="utf-8"))

    def toggle(self, app: QApplication):
        self.current = self.LIGHT if self.current == self.DARK else self.DARK
        self.apply(app)
        self._guardar(self.current)

    def cargar_tema_guardado(self) -> str:
        """Lee el tema guardado en BD. Retorna DARK si no hay."""
        try:
            from services.core.empresa_service import empresa_service
            tema = empresa_service.obtener("tema_default")
            if tema in (self.DARK, self.LIGHT):
                self.current = tema
        except Exception:
            pass
        return self.current

    def _guardar(self, tema: str):
        try:
            from services.core.empresa_service import empresa_service
            empresa_service.guardar("tema_default", tema)
        except Exception:
            pass


theme_manager = ThemeManager()
