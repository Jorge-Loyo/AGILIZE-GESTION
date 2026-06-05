"""Componentes visuales mejorados: animaciones, sombras, efectos."""
from PySide6.QtWidgets import QWidget, QPushButton, QGraphicsDropShadowEffect, QFrame
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, QRect,
    QParallelAnimationGroup, Qt, Property, QSize,
)
from PySide6.QtGui import QColor


def add_shadow(widget: QWidget, blur: int = 20, offset: tuple = (0, 4), color: str = "#000000", opacity: float = 0.3):
    """Agrega sombra a un widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(*offset)
    c = QColor(color)
    c.setAlphaF(opacity)
    shadow.setColor(c)
    widget.setGraphicsEffect(shadow)


def fade_in(widget: QWidget, duration: int = 300):
    """Animación de aparición con fade."""
    widget.setWindowOpacity(0)
    widget.show()
    anim = QPropertyAnimation(widget, b"windowOpacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    widget._fade_anim = anim  # Mantener referencia


class AnimatedButton(QPushButton):
    """Botón con efecto hover animado."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._animation = QPropertyAnimation(self, b"minimumSize")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        self._animation.stop()
        current = self.size()
        self._animation.setStartValue(QSize(current.width(), current.height()))
        self._animation.setEndValue(QSize(current.width(), current.height() + 2))
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animation.stop()
        current = self.size()
        self._animation.setStartValue(QSize(current.width(), current.height()))
        self._animation.setEndValue(QSize(current.width(), current.height() - 2))
        self._animation.start()
        super().leaveEvent(event)


class CardFrame(QFrame):
    """Card con sombra y hover effect."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        add_shadow(self, blur=16, offset=(0, 4), color="#000000", opacity=0.25)

    def enterEvent(self, event):
        effect = self.graphicsEffect()
        if effect:
            effect.setBlurRadius(24)
            effect.setOffset(0, 6)
        super().enterEvent(event)

    def leaveEvent(self, event):
        effect = self.graphicsEffect()
        if effect:
            effect.setBlurRadius(16)
            effect.setOffset(0, 4)
        super().leaveEvent(event)
