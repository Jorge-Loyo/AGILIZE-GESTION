"""Vista de Aprobaciones de Compra - Reglas + Pendientes."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QMessageBox, QComboBox, QLineEdit, QDoubleSpinBox,
    QFormLayout, QTextEdit, QTabWidget,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class AprobacionesCompraView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Aprobaciones de Compra")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_pendientes(), "Pendientes")
        self._tabs.addTab(self._build_historial(), "Historial")
        self._tabs.addTab(self._build_reglas(), "Reglas")
        layout.addWidget(self._tabs)

    # === TAB PENDIENTES ===
    def _build_pendientes(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("  Actualizar")
        btn_refresh.setIcon(qta.icon("fa5s.sync", color="#0f0f0f"))
        btn_refresh.setFixedHeight(28)
        btn_refresh.clicked.connect(self._cargar_pendientes)
        btn_row.addWidget(btn_refresh)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._tabla_pend = QTableWidget()
        self._tabla_pend.setColumnCount(6)
        self._tabla_pend.setHorizontalHeaderLabels(["ID", "Documento", "Nro", "Monto", "Solicitante", "Fecha"])
        self._tabla_pend.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self._tabla_pend.setAlternatingRowColors(True)
        self._tabla_pend.verticalHeader().setVisible(False)
        self._tabla_pend.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_pend.setSelectionBehavior(QTableWidget.SelectRows)
        self._tabla_pend.setColumnHidden(0, True)
        layout.addWidget(self._tabla_pend, 1)

        btns = QHBoxLayout()
        btn_aprobar = QPushButton("  Aprobar")
        btn_aprobar.setIcon(qta.icon("fa5s.check", color="#10b981"))
        btn_aprobar.setFixedHeight(30)
        btn_aprobar.clicked.connect(self._aprobar)
        btns.addWidget(btn_aprobar)

        btn_rechazar = QPushButton("  Rechazar")
        btn_rechazar.setIcon(qta.icon("fa5s.times", color="#ef4444"))
        btn_rechazar.setFixedHeight(30)
        btn_rechazar.clicked.connect(self._rechazar)
        btns.addWidget(btn_rechazar)
        btns.addStretch()
        layout.addLayout(btns)

        self._cargar_pendientes()
        return w

    def _cargar_pendientes(self):
        from services.compras.compras_service import compras_service
        pendientes = compras_service.listar_aprobaciones_pendientes()
        self._pendientes = pendientes
        self._tabla_pend.setRowCount(len(pendientes))
        for i, a in enumerate(pendientes):
            self._tabla_pend.setItem(i, 0, QTableWidgetItem(str(a.id)))
            tipo = "OC" if a.documento_tipo == "orden_compra" else a.documento_tipo.capitalize()
            self._tabla_pend.setItem(i, 1, QTableWidgetItem(tipo))
            self._tabla_pend.setItem(i, 2, QTableWidgetItem(str(a.documento_numero)))
            monto_item = QTableWidgetItem(f"$ {a.monto:,.2f}")
            monto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._tabla_pend.setItem(i, 3, monto_item)
            # Solicitante
            solicitante = self._obtener_nombre_usuario(a.solicitante_id)
            self._tabla_pend.setItem(i, 4, QTableWidgetItem(solicitante))
            fecha = a.created_at.strftime("%d/%m/%Y %H:%M") if a.created_at else ""
            self._tabla_pend.setItem(i, 5, QTableWidgetItem(fecha))

    def _aprobar(self):
        row = self._tabla_pend.currentRow()
        if row < 0:
            return
        aprob_id = int(self._tabla_pend.item(row, 0).text())
        from services.compras.compras_service import compras_service
        compras_service.aprobar_documento(aprob_id)
        QMessageBox.information(self, "OK", "Documento aprobado.")
        self._cargar_pendientes()

    def _rechazar(self):
        row = self._tabla_pend.currentRow()
        if row < 0:
            return
        aprob_id = int(self._tabla_pend.item(row, 0).text())
        # Pedir comentario
        dlg = QDialog(self)
        dlg.setWindowTitle("Motivo de Rechazo")
        dlg.setMinimumWidth(350)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Comentario:"))
        txt = QTextEdit()
        txt.setMaximumHeight(80)
        txt.document().setMaximumBlockCount(10)  # Limitar lineas
        lay.addWidget(txt)
        btn = QPushButton("Rechazar")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            from services.compras.compras_service import compras_service
            compras_service.rechazar_documento(aprob_id, txt.toPlainText())
            QMessageBox.information(self, "OK", "Documento rechazado.")
            self._cargar_pendientes()

    # === TAB HISTORIAL ===
    def _build_historial(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        self._tabla_hist = QTableWidget()
        self._tabla_hist.setColumnCount(7)
        self._tabla_hist.setHorizontalHeaderLabels(["Documento", "Nro", "Monto", "Estado", "Aprobador", "Fecha", "Comentario"])
        self._tabla_hist.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self._tabla_hist.setAlternatingRowColors(True)
        self._tabla_hist.verticalHeader().setVisible(False)
        self._tabla_hist.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla_hist, 1)

        btn = QPushButton("  Actualizar")
        btn.setIcon(qta.icon("fa5s.sync", color="#0f0f0f"))
        btn.setFixedHeight(28)
        btn.clicked.connect(self._cargar_historial)
        layout.addWidget(btn)

        self._cargar_historial()
        return w

    def _cargar_historial(self):
        from services.compras.compras_service import compras_service
        aprobs = compras_service.listar_aprobaciones()
        self._tabla_hist.setRowCount(len(aprobs))
        for i, a in enumerate(aprobs):
            tipo = "OC" if a.documento_tipo == "orden_compra" else a.documento_tipo.capitalize()
            self._tabla_hist.setItem(i, 0, QTableWidgetItem(tipo))
            self._tabla_hist.setItem(i, 1, QTableWidgetItem(str(a.documento_numero)))
            self._tabla_hist.setItem(i, 2, QTableWidgetItem(f"$ {a.monto:,.2f}"))
            estado_item = QTableWidgetItem(a.estado.capitalize())
            if a.estado == "aprobada":
                estado_item.setForeground(Qt.green)
            elif a.estado == "rechazada":
                estado_item.setForeground(Qt.red)
            self._tabla_hist.setItem(i, 3, estado_item)
            aprobador = self._obtener_nombre_usuario(a.aprobador_id)
            self._tabla_hist.setItem(i, 4, QTableWidgetItem(aprobador))
            fecha = a.fecha_respuesta.strftime("%d/%m/%Y") if a.fecha_respuesta else ""
            self._tabla_hist.setItem(i, 5, QTableWidgetItem(fecha))
            self._tabla_hist.setItem(i, 6, QTableWidgetItem(a.comentario or ""))

    # === TAB REGLAS ===
    def _build_reglas(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)

        info = QLabel("Configura reglas para que documentos requieran aprobacion antes de procesarse.")
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        btn_nueva = QPushButton("  Nueva Regla")
        btn_nueva.setIcon(qta.icon("fa5s.plus", color="#0f0f0f"))
        btn_nueva.setFixedHeight(28)
        btn_nueva.clicked.connect(self._nueva_regla)
        btn_row.addWidget(btn_nueva)
        btn_row.addStretch()
        btn_del = QPushButton("  Eliminar")
        btn_del.setIcon(qta.icon("fa5s.trash", color="#ef4444"))
        btn_del.setFixedHeight(28)
        btn_del.clicked.connect(self._eliminar_regla)
        btn_row.addWidget(btn_del)
        layout.addLayout(btn_row)

        self._tabla_reglas = QTableWidget()
        self._tabla_reglas.setColumnCount(6)
        self._tabla_reglas.setHorizontalHeaderLabels(["ID", "Nombre", "Documento", "Condicion", "Valor", "Aprobador"])
        self._tabla_reglas.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tabla_reglas.setAlternatingRowColors(True)
        self._tabla_reglas.verticalHeader().setVisible(False)
        self._tabla_reglas.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tabla_reglas.setColumnHidden(0, True)
        layout.addWidget(self._tabla_reglas, 1)

        self._cargar_reglas()
        return w

    def _cargar_reglas(self):
        from services.compras.compras_service import compras_service
        reglas = compras_service.listar_reglas_aprobacion()
        self._tabla_reglas.setRowCount(len(reglas))
        for i, r in enumerate(reglas):
            self._tabla_reglas.setItem(i, 0, QTableWidgetItem(str(r.id)))
            self._tabla_reglas.setItem(i, 1, QTableWidgetItem(r.nombre))
            doc = "Orden de Compra" if r.documento == "orden_compra" else r.documento.capitalize()
            self._tabla_reglas.setItem(i, 2, QTableWidgetItem(doc))
            cond = f"Monto > {r.valor_condicion:,.0f} {r.moneda}" if r.condicion == "monto_mayor" else "Siempre"
            self._tabla_reglas.setItem(i, 3, QTableWidgetItem(cond))
            self._tabla_reglas.setItem(i, 4, QTableWidgetItem(f"$ {r.valor_condicion:,.0f}"))
            aprobador = self._obtener_nombre_usuario(r.aprobador_usuario_id)
            self._tabla_reglas.setItem(i, 5, QTableWidgetItem(aprobador))

    def _obtener_nombre_usuario(self, usuario_id: int) -> str:
        if not usuario_id:
            return ""
        from core.database import get_db
        from models.usuario import Usuario
        with get_db() as db:
            u = db.get(Usuario, usuario_id)
            return u.nombre_completo if u else ""

    def _nueva_regla(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Nueva Regla de Aprobacion")
        dlg.setMinimumWidth(450)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()

        input_nombre = QLineEdit()
        input_nombre.setMaxLength(150)
        input_nombre.setPlaceholderText("Ej: OC mayor a 5000 USD")
        form.addRow("Nombre:", input_nombre)

        combo_doc = QComboBox()
        combo_doc.addItem("Orden de Compra", "orden_compra")
        combo_doc.addItem("Requisicion", "requisicion")
        form.addRow("Documento:", combo_doc)

        combo_cond = QComboBox()
        combo_cond.addItem("Monto mayor a...", "monto_mayor")
        combo_cond.addItem("Siempre", "siempre")
        form.addRow("Condicion:", combo_cond)

        spin_valor = QDoubleSpinBox()
        spin_valor.setRange(0, 99999999)
        spin_valor.setDecimals(0)
        spin_valor.setValue(5000)
        spin_valor.setPrefix("$ ")
        form.addRow("Valor:", spin_valor)

        combo_moneda = QComboBox()
        combo_moneda.addItems(["USD", "ARS", "VES"])
        form.addRow("Moneda:", combo_moneda)

        combo_aprobador = QComboBox()
        combo_aprobador.addItem("-- Seleccionar --", None)
        from core.database import get_db
        from models.usuario import Usuario
        with get_db() as db:
            for u in db.query(Usuario).filter(Usuario.activo == True).order_by(Usuario.nombre_completo).all():
                combo_aprobador.addItem(u.nombre_completo, u.id)
        form.addRow("Aprobador:", combo_aprobador)

        lay.addLayout(form)
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(dlg.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Crear Regla")
        btn_ok.clicked.connect(dlg.accept)
        btns.addWidget(btn_ok)
        lay.addLayout(btns)

        if dlg.exec() == QDialog.Accepted:
            nombre = input_nombre.text().strip()
            if not nombre:
                QMessageBox.warning(self, "Error", "Ingresa un nombre.")
                return
            aprobador_id = combo_aprobador.currentData()
            if aprobador_id is None:
                QMessageBox.warning(self, "Error", "Selecciona un aprobador.")
                return
            from services.compras.compras_service import compras_service
            compras_service.crear_regla_aprobacion({
                "nombre": nombre,
                "documento": combo_doc.currentData(),
                "condicion": combo_cond.currentData(),
                "valor_condicion": spin_valor.value(),
                "moneda": combo_moneda.currentText(),
                "aprobador_usuario_id": aprobador_id,
            })
            self._cargar_reglas()

    def _eliminar_regla(self):
        row = self._tabla_reglas.currentRow()
        if row < 0:
            return
        regla_id = int(self._tabla_reglas.item(row, 0).text())
        if QMessageBox.question(self, "Confirmar", "Eliminar esta regla?") == QMessageBox.Yes:
            from services.compras.compras_service import compras_service
            compras_service.eliminar_regla_aprobacion(regla_id)
            self._cargar_reglas()
