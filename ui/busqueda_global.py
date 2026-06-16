from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QListWidgetItem, QLabel, QFrame,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from services.empleado_service import empleado_service


class BusquedaGlobalWidget(QWidget):
    """Barra de búsqueda global con Ctrl+K. Busca empleados por nombre/legajo/DNI."""
    empleado_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(0)
        self._visible = False
        self._build_ui()
        self._setup_shortcut()

    def _build_ui(self):
        self.setObjectName("busqueda_global")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._container = QFrame()
        self._container.setStyleSheet("""
            QFrame { background: #1e1e1e; border: 1px solid #D4AF37; border-radius: 8px; }
        """)
        self._container.setVisible(False)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(8)

        # Input
        self._input = QLineEdit()
        self._input.setPlaceholderText("Buscar empleado (nombre, legajo, DNI)...")
        self._input.setMinimumHeight(36)
        self._input.setStyleSheet("QLineEdit { font-size: 14px; padding: 4px 8px; }")
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._on_enter)
        container_layout.addWidget(self._input)

        # Resultados
        self._list = QListWidget()
        self._list.setMaximumHeight(200)
        self._list.setStyleSheet("QListWidget { border: none; } QListWidget::item { padding: 6px; } QListWidget::item:selected { background: #D4AF37; color: #121212; }")
        self._list.itemDoubleClicked.connect(self._on_item_selected)
        container_layout.addWidget(self._list)

        # Hint
        hint = QLabel("Esc para cerrar  |  Enter para seleccionar")
        hint.setStyleSheet("color: #666; font-size: 11px;")
        hint.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(hint)

        layout.addWidget(self._container)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._buscar)

    def _setup_shortcut(self):
        # El shortcut se conecta desde MainWindow
        pass

    def toggle(self):
        self._visible = not self._visible
        self._container.setVisible(self._visible)
        if self._visible:
            self.setFixedHeight(300)
            self._input.setFocus()
            self._input.selectAll()
        else:
            self.setFixedHeight(0)
            self._input.clear()
            self._list.clear()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self._visible:
                self.toggle()
                return
        super().keyPressEvent(event)

    def _on_text_changed(self, text):
        self._timer.start()

    def _buscar(self):
        texto = self._input.text().strip()
        self._list.clear()
        if len(texto) < 2:
            return

        empleados = empleado_service.listar(busqueda=texto)
        for emp in empleados[:15]:
            item = QListWidgetItem(f"{emp.legajo} — {emp.nombre} {emp.apellido or ''} | DNI: {emp.dni or '-'}")
            item.setData(Qt.UserRole, emp.id)
            self._list.addItem(item)

        if not empleados:
            self._list.addItem(QListWidgetItem("Sin resultados"))

    def _on_enter(self):
        item = self._list.currentItem()
        if item and item.data(Qt.UserRole):
            self._on_item_selected(item)
        elif self._list.count() > 0:
            first = self._list.item(0)
            if first.data(Qt.UserRole):
                self._on_item_selected(first)

    def _on_item_selected(self, item: QListWidgetItem):
        emp_id = item.data(Qt.UserRole)
        if emp_id:
            self.empleado_selected.emit(emp_id)
            self.toggle()
