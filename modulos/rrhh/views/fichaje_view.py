"""Vista de Fichaje por PIN y Gestion de Turnos."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QFrame, QTabWidget,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.core.auth_service import auth_service


class FichajeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Fichaje / Turnos")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        es_admin = auth_service.current_user and auth_service.current_user.rol_id == 1
        tabs = QTabWidget()

        TABS = [
            ("rrhh.fichaje.fichar", "Fichar", self._build_fichaje),
            ("rrhh.fichaje.importar", "Importar Fichadas", self._build_importar),
            ("rrhh.fichaje.turnos", "Turnos Laborales", self._build_turnos),
            ("rrhh.fichaje.hoy", "Fichajes del Dia", self._build_fichajes_hoy),
        ]
        for codigo, label, builder in TABS:
            if es_admin or auth_service.tiene_permiso(codigo, "ver"):
                tabs.addTab(builder(), label)
        layout.addWidget(tabs)

    def _build_fichaje(self):
        """Terminal de fichaje por legajo."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(16)

        lbl = QLabel("Terminal de Fichaje")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)

        lay.addWidget(QLabel("Ingrese legajo o escanee codigo:"))
        self._input_legajo = QLineEdit()
        self._input_legajo.setFixedHeight(40)
        self._input_legajo.setFixedWidth(200)
        self._input_legajo.setMaxLength(20)
        self._input_legajo.setStyleSheet("font-size: 18px; text-align: center;")
        self._input_legajo.setAlignment(Qt.AlignCenter)
        self._input_legajo.setPlaceholderText("Legajo")
        self._input_legajo.returnPressed.connect(self._fichar_entrada)
        lay.addWidget(self._input_legajo, alignment=Qt.AlignCenter)

        btns = QHBoxLayout()
        btn_entrada = QPushButton("  Entrada")
        btn_entrada.setIcon(qta.icon("fa5s.sign-in-alt", color="#10b981"))
        btn_entrada.setFixedHeight(40)
        btn_entrada.setFixedWidth(130)
        btn_entrada.clicked.connect(self._fichar_entrada)
        btns.addWidget(btn_entrada)

        btn_salida = QPushButton("  Salida")
        btn_salida.setIcon(qta.icon("fa5s.sign-out-alt", color="#ef4444"))
        btn_salida.setFixedHeight(40)
        btn_salida.setFixedWidth(130)
        btn_salida.clicked.connect(self._fichar_salida)
        btns.addWidget(btn_salida)
        lay.addLayout(btns)

        self._lbl_resultado = QLabel("")
        self._lbl_resultado.setStyleSheet("font-size: 14px;")
        self._lbl_resultado.setAlignment(Qt.AlignCenter)
        lay.addWidget(self._lbl_resultado)
        return w

    def _fichar_entrada(self):
        self._fichar("entrada")

    def _fichar_salida(self):
        self._fichar("salida")

    def _fichar(self, tipo: str):
        legajo = self._input_legajo.text().strip()
        if not legajo:
            return
        try:
            import socket
            from services.rrhh.asistencia_service import fichaje_service
            resultado = fichaje_service.fichar_por_legajo(legajo, tipo, socket.gethostname())
            self._lbl_resultado.setText(f"✓ {resultado['empleado']} - {tipo.upper()} {resultado['hora']}")
            self._lbl_resultado.setStyleSheet("font-size: 14px; color: #10b981;")
        except Exception as e:
            self._lbl_resultado.setText(f"✗ {e}")
            self._lbl_resultado.setStyleSheet("font-size: 14px; color: #ef4444;")
        self._input_legajo.clear()
        self._input_legajo.setFocus()

    def _build_turnos(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        self._tabla_turnos = QTableWidget()
        self._tabla_turnos.setColumnCount(5)
        self._tabla_turnos.setHorizontalHeaderLabels(["Codigo", "Nombre", "Entrada", "Salida", "Nocturno"])
        self._tabla_turnos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_turnos.setAlternatingRowColors(True)
        self._tabla_turnos.verticalHeader().setVisible(False)
        self._tabla_turnos.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._tabla_turnos)

        from services.rrhh.asistencia_service import turno_service
        turnos = turno_service.listar_turnos()
        self._tabla_turnos.setRowCount(len(turnos))
        for i, t in enumerate(turnos):
            self._tabla_turnos.setItem(i, 0, QTableWidgetItem(t.codigo))
            self._tabla_turnos.setItem(i, 1, QTableWidgetItem(t.nombre))
            self._tabla_turnos.setItem(i, 2, QTableWidgetItem(str(t.hora_entrada)))
            self._tabla_turnos.setItem(i, 3, QTableWidgetItem(str(t.hora_salida)))
            self._tabla_turnos.setItem(i, 4, QTableWidgetItem("Si" if t.es_nocturno else "No"))
        return w

    def _build_importar(self):
        """Tab para importar fichadas desde Excel (XLS reloj o XLSX manual)."""
        from PySide6.QtWidgets import QFileDialog
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        info = QLabel(
            "Importar fichadas desde archivo Excel del reloj fichador (.XLS)\n"
            "o desde archivo manual (.XLSX).\n\n"
            "Formato XLS (reloj): vincula por legajo automaticamente.\n"
            "Formato XLSX (manual): vincula por nombre de hoja."
        )
        info.setStyleSheet("font-size: 11px; color: #888;")
        lay.addWidget(info)

        row = QHBoxLayout()
        btn_seleccionar = QPushButton("  Seleccionar Archivo")
        btn_seleccionar.setIcon(qta.icon("fa5s.file-excel", color="#10b981"))
        btn_seleccionar.setFixedHeight(34)
        btn_seleccionar.clicked.connect(self._seleccionar_archivo_fichadas)
        row.addWidget(btn_seleccionar)

        self._lbl_archivo = QLabel("Ningun archivo seleccionado")
        self._lbl_archivo.setStyleSheet("font-size: 11px; color: #888;")
        row.addWidget(self._lbl_archivo)
        row.addStretch()
        lay.addLayout(row)

        btn_importar = QPushButton("  Importar Fichadas")
        btn_importar.setIcon(qta.icon("fa5s.upload", color="#0f0f0f"))
        btn_importar.setFixedHeight(34)
        btn_importar.clicked.connect(self._ejecutar_importacion)
        lay.addWidget(btn_importar)

        self._lbl_resultado_import = QLabel("")
        self._lbl_resultado_import.setStyleSheet("font-size: 12px;")
        lay.addWidget(self._lbl_resultado_import)

        lay.addStretch()
        self._archivo_fichadas = None
        return w

    def _seleccionar_archivo_fichadas(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de fichadas", "", "Excel (*.xls *.xlsx)"
        )
        if path:
            self._archivo_fichadas = path
            import os
            self._lbl_archivo.setText(os.path.basename(path))

    def _ejecutar_importacion(self):
        if not self._archivo_fichadas:
            QMessageBox.warning(self, "Aviso", "Seleccione un archivo primero.")
            return
        try:
            from services.rrhh.import_fichadas_service import importar_fichadas
            resultado = importar_fichadas(self._archivo_fichadas)
            msg = (
                f"Importados: {resultado['importados']}\n"
                f"No encontrados: {len(resultado.get('no_encontrados', []))}\n"
                f"Errores: {len(resultado.get('errores', []))}"
            )
            self._lbl_resultado_import.setText(msg)
            self._lbl_resultado_import.setStyleSheet("font-size: 12px; color: #10b981;")
            if resultado.get('no_encontrados'):
                msg += f"\n\nLegajos no encontrados:\n" + "\n".join(resultado['no_encontrados'][:10])
            QMessageBox.information(self, "Importacion Completada", msg)
        except Exception as e:
            self._lbl_resultado_import.setText(f"Error: {e}")
            self._lbl_resultado_import.setStyleSheet("font-size: 12px; color: #ef4444;")
            QMessageBox.critical(self, "Error", str(e))

    def _build_fichajes_hoy(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        btn = QPushButton("  Actualizar")
        btn.setIcon(qta.icon("fa5s.sync", color="#0f0f0f"))
        btn.setFixedHeight(28)
        btn.clicked.connect(lambda: self._cargar_fichajes_hoy())
        lay.addWidget(btn)

        self._tabla_fichajes = QTableWidget()
        self._tabla_fichajes.setColumnCount(4)
        self._tabla_fichajes.setHorizontalHeaderLabels(["Hora", "Empleado", "Tipo", "Dispositivo"])
        self._tabla_fichajes.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_fichajes.setAlternatingRowColors(True)
        self._tabla_fichajes.verticalHeader().setVisible(False)
        self._tabla_fichajes.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._tabla_fichajes)

        self._cargar_fichajes_hoy()
        return w

    def _cargar_fichajes_hoy(self):
        from services.rrhh.asistencia_service import fichaje_service
        fichajes = fichaje_service.fichajes_hoy()
        self._tabla_fichajes.setRowCount(len(fichajes))
        for i, f in enumerate(fichajes):
            self._tabla_fichajes.setItem(i, 0, QTableWidgetItem(str(f.hora)))
            emp_nombre = ""
            try:
                from core.database import get_db
                from models.empleado import Empleado
                with get_db() as db:
                    e = db.get(Empleado, f.empleado_id)
                    emp_nombre = f"{e.apellido}, {e.nombre}" if e else ""
            except Exception:
                pass
            self._tabla_fichajes.setItem(i, 1, QTableWidgetItem(emp_nombre))
            tipo_item = QTableWidgetItem(f.tipo.upper())
            if f.tipo == "entrada":
                tipo_item.setForeground(Qt.green)
            else:
                tipo_item.setForeground(Qt.red)
            self._tabla_fichajes.setItem(i, 2, tipo_item)
            self._tabla_fichajes.setItem(i, 3, QTableWidgetItem(f.dispositivo))
