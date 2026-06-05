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


theme_manager = ThemeManager()
