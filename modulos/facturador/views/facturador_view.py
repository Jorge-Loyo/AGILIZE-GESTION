"""
Modulo Facturador - Menu principal con submódulos.
Permite elegir facturador y acceder a POS, Facturacion Central, Cajas.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QDialog, QFormLayout, QComboBox,
    QStackedWidget, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
import qtawesome as qta
from ui.theme_manager import theme_manager


SUBMODULOS_FACTURADOR = [
    {"codigo": "pos", "label": "Punto de Venta", "icon": "fa5s.cash-register"},
    {"codigo": "central", "label": "Facturacion Central", "icon": "fa5s.file-invoice-dollar"},
    {"codigo": "cajas", "label": "Cajas / Turnos", "icon": "fa5s.money-bill-wave"},
    {"codigo": "historial", "label": "Historial Facturas", "icon": "fa5s.history"},
]


class FacturadorView(QWidget):
    volver_dashboard = Signal()
    logout_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = None
        self._depositos_ids = []
        self._buttons: list[QPushButton] = []
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 16, 12, 16)
        sidebar_layout.setSpacing(4)

        btn_volver = QPushButton("  Menu")
        btn_volver.setIcon(qta.icon("fa5s.arrow-left", color="#8a8a8a"))
        btn_volver.setCursor(Qt.PointingHandCursor)
        btn_volver.setStyleSheet("QPushButton { background-color: transparent; color: #8a8a8a; border: none; text-align: left; padding: 8px 12px; } QPushButton:hover { color: #F8F9FA; }")
        btn_volver.clicked.connect(self.volver_dashboard.emit)
        sidebar_layout.addWidget(btn_volver)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))
        lbl = QLabel("Facturador")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(lbl)

        # Selector de facturador
        sidebar_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self._combo_facturador = QComboBox()
        self._combo_facturador.setFixedHeight(28)
        self._cargar_facturadores()
        self._combo_facturador.currentIndexChanged.connect(self._cambiar_facturador)
        sidebar_layout.addWidget(self._combo_facturador)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Botones submódulos
        self.stack = QStackedWidget()
        for i, sub in enumerate(SUBMODULOS_FACTURADOR):
            btn = QPushButton(f"  {sub['label']}")
            btn.setIcon(qta.icon(sub["icon"], color="#8a8a8a"))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_layout.addWidget(btn)
            self._buttons.append(btn)
            self.stack.addWidget(self._create_submodule(sub["codigo"]))

        sidebar_layout.addStretch()

        btn_manual = QPushButton("  Manual de uso")
        btn_manual.setIcon(qta.icon("fa5s.question-circle", color="#D4AF37"))
        btn_manual.setCursor(Qt.PointingHandCursor)
        btn_manual.setStyleSheet("QPushButton { background-color: transparent; color: #D4AF37; border: 1px solid #D4AF37; border-radius: 4px; padding: 6px 10px; } QPushButton:hover { background-color: #D4AF37; color: #0f0f0f; }")
        btn_manual.clicked.connect(self._ver_manual)
        sidebar_layout.addWidget(btn_manual)

        # Info caja
        self._lbl_caja = QLabel("Sin turno abierto")
        self._lbl_caja.setStyleSheet("font-size: 10px; color: #666;")
        sidebar_layout.addWidget(self._lbl_caja)
        self._actualizar_info_caja()

        btn_theme = QPushButton("  Cambiar modo")
        btn_theme.setIcon(qta.icon("fa5s.adjust", color="#8a8a8a"))
        btn_theme.setCursor(Qt.PointingHandCursor)
        btn_theme.clicked.connect(lambda: theme_manager.toggle(__import__('PySide6.QtWidgets', fromlist=['QApplication']).QApplication.instance()))
        sidebar_layout.addWidget(btn_theme)

        sidebar_layout.addSpacerItem(QSpacerItem(0, 4, QSizePolicy.Minimum, QSizePolicy.Fixed))
        btn_logout = QPushButton("  Cerrar sesion")
        btn_logout.setIcon(qta.icon("fa5s.sign-out-alt", color="#ffffff"))
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn_logout.clicked.connect(self.logout_signal.emit)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)
        layout.addWidget(self.stack)
        if self._buttons:
            self._navigate(0)

    def _cargar_facturadores(self):
        self._combo_facturador.clear()
        try:
            from services.datos.facturador_config_service import facturador_config_service
            configs = facturador_config_service.listar()
            for c in configs:
                self._combo_facturador.addItem(f"{c.codigo} - {c.nombre}", c.codigo)
            if configs:
                self._config = configs[0]
                self._depositos_ids = facturador_config_service.get_depositos_ids(configs[0])
        except Exception:
            pass

    def _cambiar_facturador(self):
        codigo = self._combo_facturador.currentData()
        if not codigo:
            return
        try:
            from services.datos.facturador_config_service import facturador_config_service
            self._config = facturador_config_service.obtener_por_codigo(codigo)
            if self._config:
                self._depositos_ids = facturador_config_service.get_depositos_ids(self._config)
        except Exception:
            pass

    def _actualizar_info_caja(self):
        try:
            from services.ventas.caja_pos_service import caja_pos_service
            turno = caja_pos_service.turno_activo()
            if turno:
                self._lbl_caja.setText(f"Caja abierta | Fondo: ${turno.fondo_inicial:,.0f}")
                self._lbl_caja.setStyleSheet("font-size: 10px; color: #10b981;")
            else:
                self._lbl_caja.setText("Sin turno abierto")
                self._lbl_caja.setStyleSheet("font-size: 10px; color: #666;")
        except Exception:
            pass

    def _create_submodule(self, codigo: str) -> QWidget:
        if codigo == "pos":
            return self._build_pos()
        if codigo == "central":
            from modulos.facturador.views.facturacion_central_view import FacturacionCentralView
            return FacturacionCentralView()
        if codigo == "cajas":
            return self._build_cajas()
        if codigo == "historial":
            return self._build_historial()
        return QWidget()

    def _navigate(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _ver_manual(self):
        from ui.manual_uso_view import ManualUsoView, MANUAL_FACTURADOR
        if not hasattr(self, '_manual_idx'):
            manual = ManualUsoView(MANUAL_FACTURADOR, "Manual - Facturador")
            self._manual_idx = self.stack.addWidget(manual)
        self.stack.setCurrentIndex(self._manual_idx)
        for btn in self._buttons:
            btn.setChecked(False)

    # ===================
    # POS
    # ===================
    def _build_pos(self):
        from modulos.facturador.views.pos_view import POSView
        return POSView(self)

    # ===================
    # CAJAS
    # ===================
    def _build_cajas(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Gestion de Cajas / Turnos")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        # Acciones
        btns = QHBoxLayout()
        btn_abrir = QPushButton("  Abrir Turno")
        btn_abrir.setIcon(qta.icon("fa5s.play", color="#10b981"))
        btn_abrir.setFixedHeight(34)
        btn_abrir.clicked.connect(self._abrir_turno)
        btns.addWidget(btn_abrir)

        btn_retiro = QPushButton("  Retiro Efectivo")
        btn_retiro.setIcon(qta.icon("fa5s.arrow-up", color="#f59e0b"))
        btn_retiro.setFixedHeight(34)
        btn_retiro.clicked.connect(self._retiro_caja)
        btns.addWidget(btn_retiro)

        btn_ingreso = QPushButton("  Ingreso Efectivo")
        btn_ingreso.setIcon(qta.icon("fa5s.arrow-down", color="#3b82f6"))
        btn_ingreso.setFixedHeight(34)
        btn_ingreso.clicked.connect(self._ingreso_caja)
        btns.addWidget(btn_ingreso)

        btn_cerrar = QPushButton("  Cerrar Turno (Arqueo)")
        btn_cerrar.setIcon(qta.icon("fa5s.stop", color="#ef4444"))
        btn_cerrar.setFixedHeight(34)
        btn_cerrar.clicked.connect(self._cerrar_turno)
        btns.addWidget(btn_cerrar)
        btns.addStretch()
        layout.addLayout(btns)

        # Historial turnos
        self._tabla_turnos = QTableWidget()
        self._tabla_turnos.setColumnCount(7)
        self._tabla_turnos.setHorizontalHeaderLabels(["Fecha", "Caja", "Cajero", "Fondo", "Ventas", "Diferencia", "Estado"])
        self._tabla_turnos.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla_turnos.setAlternatingRowColors(True)
        self._tabla_turnos.verticalHeader().setVisible(False)
        self._tabla_turnos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla_turnos, 1)

        self._cargar_turnos()
        return w

    def _cargar_turnos(self):
        try:
            from services.ventas.caja_pos_service import caja_pos_service
            from core.database import get_db
            from models.usuario import Usuario
            turnos = caja_pos_service.historial_turnos(limite=30)
            self._tabla_turnos.setRowCount(len(turnos))
            for i, t in enumerate(turnos):
                self._tabla_turnos.setItem(i, 0, QTableWidgetItem(t.fecha.strftime("%d/%m/%Y") if t.fecha else ""))
                self._tabla_turnos.setItem(i, 1, QTableWidgetItem(str(t.caja_id)))
                cajero = ""
                with get_db() as db:
                    u = db.get(Usuario, t.cajero_id)
                    cajero = u.nombre_completo if u else ""
                self._tabla_turnos.setItem(i, 2, QTableWidgetItem(cajero))
                self._tabla_turnos.setItem(i, 3, QTableWidgetItem(f"${t.fondo_inicial:,.0f}"))
                total_v = t.total_efectivo + t.total_tarjeta_debito + t.total_tarjeta_credito + t.total_transferencia
                self._tabla_turnos.setItem(i, 4, QTableWidgetItem(f"${total_v:,.0f}"))
                dif = QTableWidgetItem(f"${t.diferencia:,.2f}")
                if t.diferencia != 0:
                    dif.setForeground(Qt.red)
                self._tabla_turnos.setItem(i, 5, dif)
                self._tabla_turnos.setItem(i, 6, QTableWidgetItem(t.estado.capitalize()))
        except Exception:
            pass

    def _abrir_turno(self):
        from services.ventas.caja_pos_service import caja_pos_service
        dlg = QDialog(self)
        dlg.setWindowTitle("Abrir Turno")
        dlg.setMinimumWidth(300)
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        combo_caja = QComboBox()
        for c in caja_pos_service.listar_cajas():
            combo_caja.addItem(f"{c.codigo} - {c.nombre}", c.id)
        form.addRow("Caja:", combo_caja)
        input_fondo = QLineEdit()
        input_fondo.setPlaceholderText("0")
        input_fondo.setMaxLength(12)
        form.addRow("Fondo inicial $:", input_fondo)
        lay.addLayout(form)
        btn = QPushButton("Abrir")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            try:
                fondo = float(input_fondo.text() or "0")
                caja_pos_service.abrir_turno(combo_caja.currentData(), fondo)
                QMessageBox.information(self, "OK", "Turno abierto.")
                self._cargar_turnos()
                self._actualizar_info_caja()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _retiro_caja(self):
        from services.ventas.caja_pos_service import caja_pos_service
        turno = caja_pos_service.turno_activo()
        if not turno:
            QMessageBox.warning(self, "Aviso", "No hay turno abierto.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Retiro de Efectivo")
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        input_monto = QLineEdit()
        input_monto.setMaxLength(12)
        form.addRow("Monto $:", input_monto)
        input_motivo = QLineEdit()
        input_motivo.setMaxLength(100)
        form.addRow("Motivo:", input_motivo)
        lay.addLayout(form)
        btn = QPushButton("Registrar Retiro")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            try:
                caja_pos_service.registrar_retiro(turno.id, float(input_monto.text() or "0"), input_motivo.text())
                QMessageBox.information(self, "OK", "Retiro registrado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _ingreso_caja(self):
        from services.ventas.caja_pos_service import caja_pos_service
        turno = caja_pos_service.turno_activo()
        if not turno:
            QMessageBox.warning(self, "Aviso", "No hay turno abierto.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Ingreso de Efectivo")
        lay = QVBoxLayout(dlg)
        form = QFormLayout()
        input_monto = QLineEdit()
        input_monto.setMaxLength(12)
        form.addRow("Monto $:", input_monto)
        input_motivo = QLineEdit()
        input_motivo.setMaxLength(100)
        form.addRow("Motivo:", input_motivo)
        lay.addLayout(form)
        btn = QPushButton("Registrar Ingreso")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            try:
                caja_pos_service.registrar_ingreso(turno.id, float(input_monto.text() or "0"), input_motivo.text())
                QMessageBox.information(self, "OK", "Ingreso registrado.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _cerrar_turno(self):
        from services.ventas.caja_pos_service import caja_pos_service
        turno = caja_pos_service.turno_activo()
        if not turno:
            QMessageBox.warning(self, "Aviso", "No hay turno abierto.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("Cierre de Caja - Arqueo")
        dlg.setMinimumWidth(350)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Cuente el efectivo en la caja y registre el total:"))
        input_contado = QLineEdit()
        input_contado.setFixedHeight(36)
        input_contado.setStyleSheet("font-size: 18px;")
        input_contado.setPlaceholderText("$ efectivo contado")
        input_contado.setMaxLength(12)
        lay.addWidget(input_contado)
        lay.addWidget(QLabel("Observaciones:"))
        input_obs = QLineEdit()
        input_obs.setMaxLength(250)
        lay.addWidget(input_obs)
        btn = QPushButton("Cerrar Turno")
        btn.setStyleSheet("QPushButton { background-color: #ef4444; } QPushButton:hover { background-color: #dc2626; }")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec() == QDialog.Accepted:
            try:
                contado = float(input_contado.text() or "0")
                resultado = caja_pos_service.cerrar_turno(turno.id, contado, input_obs.text())
                dif = resultado["diferencia"]
                msg = (f"Turno cerrado.\n\n"
                       f"Efectivo esperado: ${resultado['efectivo_esperado']:,.2f}\n"
                       f"Efectivo contado: ${contado:,.2f}\n"
                       f"Diferencia: ${dif:,.2f}")
                if dif > 0:
                    msg += "\n\n⚠️ SOBRANTE detectado"
                elif dif < 0:
                    msg += "\n\n⚠️ FALTANTE detectado"
                else:
                    msg += "\n\n✓ Caja cuadrada"
                QMessageBox.information(self, "Arqueo", msg)
                self._cargar_turnos()
                self._actualizar_info_caja()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ===================
    # HISTORIAL
    # ===================
    def _build_historial(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Historial de Facturas Emitidas")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        self._tabla_facturas = QTableWidget()
        self._tabla_facturas.setColumnCount(6)
        self._tabla_facturas.setHorizontalHeaderLabels(["Numero", "Fecha", "Cliente", "Total", "Medio", "Estado"])
        self._tabla_facturas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self._tabla_facturas.setAlternatingRowColors(True)
        self._tabla_facturas.verticalHeader().setVisible(False)
        self._tabla_facturas.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._tabla_facturas, 1)

        try:
            from services.ventas.motor_facturacion import motor_facturacion
            facturas = motor_facturacion.listar_facturas_venta(limite=50)
            self._tabla_facturas.setRowCount(len(facturas))
            for i, f in enumerate(facturas):
                self._tabla_facturas.setItem(i, 0, QTableWidgetItem(f.numero))
                self._tabla_facturas.setItem(i, 1, QTableWidgetItem(f.fecha.strftime("%d/%m/%Y") if f.fecha else ""))
                self._tabla_facturas.setItem(i, 2, QTableWidgetItem(f.cliente_nombre))
                t = QTableWidgetItem(f"${f.total:,.2f}")
                t.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._tabla_facturas.setItem(i, 3, t)
                self._tabla_facturas.setItem(i, 4, QTableWidgetItem(f.condicion_pago))
                self._tabla_facturas.setItem(i, 5, QTableWidgetItem(f.estado.capitalize()))
        except Exception:
            pass

        return w
