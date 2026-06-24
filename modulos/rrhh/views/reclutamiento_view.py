"""Vista de Reclutamiento y Seleccion."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QMessageBox, QDialog, QLineEdit, QTextEdit, QFormLayout,
    QTabWidget, QSpinBox,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class ReclutamientoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Reclutamiento y Seleccion")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_vacantes(), "Vacantes")
        tabs.addTab(self._build_candidatos(), "Candidatos")
        layout.addWidget(tabs)

    def _build_vacantes(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        btns = QHBoxLayout()
        btn_nueva = QPushButton("  Nueva Vacante")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(28)
        btn_nueva.clicked.connect(self._nueva_vacante)
        btns.addWidget(btn_nueva)
        btns.addStretch()
        lay.addLayout(btns)

        self._tabla_vac = QTableWidget()
        self._tabla_vac.setColumnCount(6)
        self._tabla_vac.setHorizontalHeaderLabels(["ID", "Titulo", "Departamento", "Puestos", "Prioridad", "Estado"])
        self._tabla_vac.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_vac.setAlternatingRowColors(True)
        self._tabla_vac.verticalHeader().setVisible(False)
        self._tabla_vac.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_vac.setColumnHidden(0, True)
        lay.addWidget(self._tabla_vac, 1)

        self._cargar_vacantes()
        return w

    def _cargar_vacantes(self):
        from services.rrhh.reclutamiento_service import reclutamiento_service
        vacantes = reclutamiento_service.listar_vacantes()
        self._tabla_vac.setRowCount(len(vacantes))
        for i, v in enumerate(vacantes):
            self._tabla_vac.setItem(i, 0, QTableWidgetItem(str(v.id)))
            self._tabla_vac.setItem(i, 1, QTableWidgetItem(v.titulo))
            self._tabla_vac.setItem(i, 2, QTableWidgetItem(str(v.departamento_id or "")))
            self._tabla_vac.setItem(i, 3, QTableWidgetItem(str(v.cantidad_puestos)))
            prio = QTableWidgetItem(v.prioridad.capitalize())
            if v.prioridad == "urgente":
                prio.setForeground(Qt.red)
            elif v.prioridad == "alta":
                prio.setForeground(Qt.yellow)
            self._tabla_vac.setItem(i, 4, prio)
            estado = QTableWidgetItem(v.estado.capitalize())
            if v.estado == "cerrada":
                estado.setForeground(Qt.green)
            self._tabla_vac.setItem(i, 5, estado)

    def _nueva_vacante(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Nueva Vacante")
        dlg.setMinimumWidth(450)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        input_titulo = QLineEdit()
        input_titulo.setMaxLength(200)
        form.addRow("Titulo:", input_titulo)
        combo_jornada = QComboBox()
        combo_jornada.addItems(["completa", "parcial", "freelance"])
        form.addRow("Jornada:", combo_jornada)
        combo_prio = QComboBox()
        combo_prio.addItems(["baja", "normal", "alta", "urgente"])
        combo_prio.setCurrentIndex(1)
        form.addRow("Prioridad:", combo_prio)
        spin_puestos = QSpinBox()
        spin_puestos.setRange(1, 50)
        form.addRow("Puestos:", spin_puestos)
        input_desc = QTextEdit()
        input_desc.setMaximumHeight(80)
        form.addRow("Descripcion:", input_desc)
        lay.addLayout(form)
        btn = QPushButton("Crear Vacante")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        if dlg.exec() == QDialog.Accepted and input_titulo.text().strip():
            from services.rrhh.reclutamiento_service import reclutamiento_service
            reclutamiento_service.crear_vacante({
                "titulo": input_titulo.text().strip(),
                "jornada": combo_jornada.currentText(),
                "prioridad": combo_prio.currentText(),
                "cantidad_puestos": spin_puestos.value(),
                "descripcion": input_desc.toPlainText(),
            })
            self._cargar_vacantes()

    def _build_candidatos(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)

        row = QHBoxLayout()
        row.addWidget(QLabel("Vacante:"))
        self._combo_vac = QComboBox()
        self._combo_vac.setMinimumWidth(250)
        self._combo_vac.currentIndexChanged.connect(self._cargar_candidatos)
        row.addWidget(self._combo_vac)
        row.addStretch()
        btn_add = QPushButton("  Agregar Candidato")
        btn_add.setIcon(qta.icon("fa5s.user-plus", color="#0f0f0f"))
        btn_add.setFixedHeight(28)
        btn_add.clicked.connect(self._agregar_candidato)
        row.addWidget(btn_add)
        lay.addLayout(row)

        self._tabla_cand = QTableWidget()
        self._tabla_cand.setColumnCount(6)
        self._tabla_cand.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Puntaje", "Estado", "Fecha"])
        self._tabla_cand.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_cand.setAlternatingRowColors(True)
        self._tabla_cand.verticalHeader().setVisible(False)
        self._tabla_cand.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_cand.setColumnHidden(0, True)
        lay.addWidget(self._tabla_cand, 1)

        # Botones de accion
        bot = QHBoxLayout()
        for estado, color in [("entrevista", "#3b82f6"), ("evaluando", "#f59e0b"), ("contratado", "#10b981"), ("rechazado", "#ef4444")]:
            btn = QPushButton(f"  {estado.capitalize()}")
            btn.setFixedHeight(28)
            btn.clicked.connect(lambda _, e=estado: self._cambiar_estado(e))
            bot.addWidget(btn)
        bot.addStretch()
        lay.addLayout(bot)

        self._cargar_combo_vacantes()
        return w

    def _cargar_combo_vacantes(self):
        from services.rrhh.reclutamiento_service import reclutamiento_service
        self._combo_vac.clear()
        for v in reclutamiento_service.listar_vacantes():
            self._combo_vac.addItem(f"{v.titulo} ({v.estado})", v.id)

    def _cargar_candidatos(self):
        vac_id = self._combo_vac.currentData()
        if not vac_id:
            return
        from services.rrhh.reclutamiento_service import reclutamiento_service
        candidatos = reclutamiento_service.listar_candidatos(vac_id)
        self._tabla_cand.setRowCount(len(candidatos))
        for i, c in enumerate(candidatos):
            self._tabla_cand.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self._tabla_cand.setItem(i, 1, QTableWidgetItem(c.nombre))
            self._tabla_cand.setItem(i, 2, QTableWidgetItem(c.email))
            self._tabla_cand.setItem(i, 3, QTableWidgetItem(str(c.puntaje)))
            estado = QTableWidgetItem(c.estado.capitalize())
            if c.estado == "contratado":
                estado.setForeground(Qt.green)
            elif c.estado == "rechazado":
                estado.setForeground(Qt.red)
            self._tabla_cand.setItem(i, 4, estado)
            self._tabla_cand.setItem(i, 5, QTableWidgetItem(c.fecha_postulacion.strftime("%d/%m/%Y") if c.fecha_postulacion else ""))

    def _agregar_candidato(self):
        vac_id = self._combo_vac.currentData()
        if not vac_id:
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Agregar Candidato")
        dlg.setMinimumWidth(400)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        input_nombre = QLineEdit()
        input_nombre.setMaxLength(150)
        form.addRow("Nombre:", input_nombre)
        input_email = QLineEdit()
        input_email.setMaxLength(150)
        form.addRow("Email:", input_email)
        input_tel = QLineEdit()
        input_tel.setMaxLength(50)
        form.addRow("Telefono:", input_tel)
        combo_fuente = QComboBox()
        combo_fuente.addItems(["portal", "referido", "espontaneo", "linkedin", "otro"])
        form.addRow("Fuente:", combo_fuente)
        lay.addLayout(form)
        btn = QPushButton("Agregar")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        if dlg.exec() == QDialog.Accepted and input_nombre.text().strip():
            from services.rrhh.reclutamiento_service import reclutamiento_service
            reclutamiento_service.agregar_candidato(vac_id, {
                "nombre": input_nombre.text().strip(),
                "email": input_email.text().strip(),
                "telefono": input_tel.text().strip(),
                "fuente": combo_fuente.currentText(),
            })
            self._cargar_candidatos()

    def _cambiar_estado(self, estado: str):
        row = self._tabla_cand.currentRow()
        if row < 0:
            return
        cand_id = int(self._tabla_cand.item(row, 0).text())
        from services.rrhh.reclutamiento_service import reclutamiento_service
        reclutamiento_service.cambiar_estado_candidato(cand_id, estado)
        self._cargar_candidatos()
