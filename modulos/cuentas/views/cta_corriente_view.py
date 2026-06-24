from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QMessageBox,
    QFrame, QTextEdit,
)
from PySide6.QtCore import Qt
import qtawesome as qta
from services.cuentas_service import cuentas_service


class CtaCorrienteView(QWidget):
    def __init__(self, tipo_entidad: str, parent=None):
        super().__init__(parent)
        self._tipo = tipo_entidad  # "cliente" o "proveedor"
        self._entidad_id = None
        self._build_ui()
        self._cargar_entidades()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        titulo = "Cuenta Corriente - Clientes" if self._tipo == "cliente" else "Cuenta Corriente - Proveedores"
        title = QLabel(titulo)
        title.setObjectName("title")
        layout.addWidget(title)

        # Selector de entidad + saldo
        sel_row = QHBoxLayout()
        sel_row.setSpacing(10)

        lbl = QLabel("Cliente:" if self._tipo == "cliente" else "Proveedor:")
        sel_row.addWidget(lbl)

        self._combo_entidad = QComboBox()
        self._combo_entidad.setFixedHeight(30)
        self._combo_entidad.setMinimumWidth(250)
        self._combo_entidad.currentIndexChanged.connect(self._on_entidad_change)
        sel_row.addWidget(self._combo_entidad)

        sel_row.addStretch()

        self._lbl_saldo = QLabel("Saldo: $ 0.00")
        self._lbl_saldo.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        sel_row.addWidget(self._lbl_saldo)

        layout.addLayout(sel_row)

        # Botones debe/haber
        btns_row = QHBoxLayout()
        btns_row.setSpacing(8)

        btn_debe = QPushButton("  Registrar Debe")
        btn_debe.setIcon(qta.icon("fa5s.plus-circle", color="#ef4444"))
        btn_debe.setFixedHeight(32)
        btn_debe.setCursor(Qt.PointingHandCursor)
        btn_debe.clicked.connect(self._registrar_debe)
        btns_row.addWidget(btn_debe)

        btn_haber = QPushButton("  Registrar Haber")
        btn_haber.setIcon(qta.icon("fa5s.minus-circle", color="#10b981"))
        btn_haber.setFixedHeight(32)
        btn_haber.setCursor(Qt.PointingHandCursor)
        btn_haber.clicked.connect(self._registrar_haber)
        btns_row.addWidget(btn_haber)

        btns_row.addStretch()

        # Botones estado de cuenta y notificaciones (solo clientes)
        if self._tipo == "cliente":
            btn_estado = QPushButton("  Estado de Cuenta")
            btn_estado.setIcon(qta.icon("fa5s.file-pdf", color="#3b82f6"))
            btn_estado.setFixedHeight(32)
            btn_estado.setCursor(Qt.PointingHandCursor)
            btn_estado.clicked.connect(self._generar_estado_cuenta)
            btns_row.addWidget(btn_estado)

            btn_whatsapp = QPushButton("  WhatsApp")
            btn_whatsapp.setIcon(qta.icon("fa5b.whatsapp", color="#25d366"))
            btn_whatsapp.setFixedHeight(32)
            btn_whatsapp.setCursor(Qt.PointingHandCursor)
            btn_whatsapp.clicked.connect(self._enviar_whatsapp)
            btns_row.addWidget(btn_whatsapp)

            btn_email = QPushButton("  Email")
            btn_email.setIcon(qta.icon("fa5s.envelope", color="#D4AF37"))
            btn_email.setFixedHeight(32)
            btn_email.setCursor(Qt.PointingHandCursor)
            btn_email.clicked.connect(self._enviar_email)
            btns_row.addWidget(btn_email)

        layout.addLayout(btns_row)

        # Tabla de movimientos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Concepto", "Comprobante", "Debe", "Haber", "Saldo"])
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabla, 1)

    def _cargar_entidades(self):
        self._combo_entidad.clear()
        self._combo_entidad.addItem("-- Seleccionar --", None)
        if self._tipo == "cliente":
            from services.datos_service import datos_service
            for c in datos_service.listar_clientes():
                self._combo_entidad.addItem(c.razon_social, c.id)
        else:
            from services.datos_service import datos_service
            for p in datos_service.listar_proveedores():
                self._combo_entidad.addItem(p.razon_social, p.id)

    def _on_entidad_change(self):
        self._entidad_id = self._combo_entidad.currentData()
        if not self._entidad_id:
            self.tabla.setRowCount(0)
            self._lbl_saldo.setText("Saldo: $ 0.00")
            return
        self._cargar_movimientos()

    def _cargar_movimientos(self):
        if not self._entidad_id:
            return
        movimientos = cuentas_service.listar_movimientos(self._tipo, self._entidad_id)
        saldo = cuentas_service.obtener_saldo(self._tipo, self._entidad_id)

        self._lbl_saldo.setText(f"Saldo: $ {saldo:,.2f}")
        if saldo > 0:
            self._lbl_saldo.setStyleSheet("font-size: 16px; font-weight: bold; color: #ef4444;")
        elif saldo < 0:
            self._lbl_saldo.setStyleSheet("font-size: 16px; font-weight: bold; color: #10b981;")
        else:
            self._lbl_saldo.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")

        self.tabla.setRowCount(len(movimientos))
        for i, m in enumerate(movimientos):
            self.tabla.setItem(i, 0, QTableWidgetItem(m.fecha.strftime("%d/%m/%Y") if m.fecha else ""))
            self.tabla.setItem(i, 1, QTableWidgetItem(m.concepto))
            self.tabla.setItem(i, 2, QTableWidgetItem(m.comprobante or ""))

            if m.tipo == "debe":
                debe_item = QTableWidgetItem(f"{m.monto:,.2f}")
                debe_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla.setItem(i, 3, debe_item)
                self.tabla.setItem(i, 4, QTableWidgetItem(""))
            else:
                self.tabla.setItem(i, 3, QTableWidgetItem(""))
                haber_item = QTableWidgetItem(f"{m.monto:,.2f}")
                haber_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.tabla.setItem(i, 4, haber_item)

            saldo_item = QTableWidgetItem(f"{m.saldo:,.2f}")
            saldo_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabla.setItem(i, 5, saldo_item)

    def _registrar_debe(self):
        if not self._entidad_id:
            QMessageBox.warning(self, "Error", "Selecciona un cliente/proveedor primero.")
            return
        dlg = MovimientoCtaDialog("debe", parent=self)
        if dlg.exec() == QDialog.Accepted:
            datos = dlg.datos()
            try:
                cuentas_service.registrar_debe(
                    self._tipo, self._entidad_id,
                    datos["monto"], datos["concepto"], datos["comprobante"], datos["notas"]
                )
                self._cargar_movimientos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _registrar_haber(self):
        if not self._entidad_id:
            QMessageBox.warning(self, "Error", "Selecciona un cliente/proveedor primero.")
            return
        dlg = MovimientoCtaDialog("haber", parent=self)
        if dlg.exec() == QDialog.Accepted:
            datos = dlg.datos()
            try:
                cuentas_service.registrar_haber(
                    self._tipo, self._entidad_id,
                    datos["monto"], datos["concepto"], datos["comprobante"], datos["notas"]
                )
                self._cargar_movimientos()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _generar_estado_cuenta(self):
        if not self._entidad_id:
            QMessageBox.warning(self, "Error", "Selecciona un cliente primero.")
            return

        from PySide6.QtWidgets import QFileDialog
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar Estado de Cuenta",
            f"estado_cuenta_{self._combo_entidad.currentText().replace(' ', '_')}.pdf",
            "PDF (*.pdf)"
        )
        if not ruta:
            return

        try:
            from services.estado_cuenta_service import generar_estado_cuenta_pdf
            cliente_nombre = self._combo_entidad.currentText()
            movimientos = cuentas_service.listar_movimientos(self._tipo, self._entidad_id)
            saldo = cuentas_service.obtener_saldo(self._tipo, self._entidad_id)
            generar_estado_cuenta_pdf(ruta, cliente_nombre, movimientos, saldo)
            QMessageBox.information(self, "OK", f"Estado de cuenta generado:\n{ruta}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _enviar_whatsapp(self):
        if not self._entidad_id:
            QMessageBox.warning(self, "Error", "Selecciona un cliente primero.")
            return

        saldo = cuentas_service.obtener_saldo(self._tipo, self._entidad_id)
        if saldo <= 0:
            QMessageBox.information(self, "Info", "Este cliente no tiene saldo pendiente.")
            return

        cliente_nombre = self._combo_entidad.currentText()

        # Obtener telefono del cliente
        from services.datos_service import datos_service
        cliente = datos_service.obtener_cliente(self._entidad_id)
        telefono = ""
        if cliente:
            telefono = cliente.celular or cliente.telefono or ""

        mensaje = (
            f"Estimado/a {cliente_nombre},\n\n"
            f"Le informamos que su saldo pendiente es de $ {saldo:,.2f}.\n"
            f"Por favor, regularice su situacion a la brevedad.\n\n"
            f"Gracias."
        )

        # Limpiar telefono
        telefono_limpio = "".join(c for c in telefono if c.isdigit() or c == "+")

        import urllib.parse
        import webbrowser
        msg_encoded = urllib.parse.quote(mensaje)

        if telefono_limpio:
            url = f"https://wa.me/{telefono_limpio}?text={msg_encoded}"
        else:
            url = f"https://wa.me/?text={msg_encoded}"

        webbrowser.open(url)

    def _enviar_email(self):
        if not self._entidad_id:
            QMessageBox.warning(self, "Error", "Selecciona un cliente primero.")
            return

        saldo = cuentas_service.obtener_saldo(self._tipo, self._entidad_id)
        if saldo <= 0:
            QMessageBox.information(self, "Info", "Este cliente no tiene saldo pendiente.")
            return

        cliente_nombre = self._combo_entidad.currentText()

        # Obtener email del cliente
        from services.datos_service import datos_service
        cliente = datos_service.obtener_cliente(self._entidad_id)
        email = cliente.email if cliente else ""

        asunto = f"Estado de Cuenta - {cliente_nombre}"
        cuerpo = (
            f"Estimado/a {cliente_nombre},\n\n"
            f"Le informamos que su saldo pendiente es de $ {saldo:,.2f}.\n"
            f"Por favor, regularice su situacion a la brevedad.\n\n"
            f"Gracias."
        )

        import urllib.parse
        import webbrowser
        mailto = f"mailto:{email}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
        webbrowser.open(mailto)


class MovimientoCtaDialog(QDialog):
    def __init__(self, tipo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Registrar {'Debe' if tipo == 'debe' else 'Haber'}")
        self.setMinimumWidth(400)
        self._tipo = tipo
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        self._input_monto = QDoubleSpinBox()
        self._input_monto.setRange(0.01, 99999999)
        self._input_monto.setDecimals(2)
        self._input_monto.setFixedHeight(28)
        form.addRow("Monto:", self._input_monto)

        self._input_concepto = QLineEdit()
        self._input_concepto.setFixedHeight(28)
        self._input_concepto.setPlaceholderText("Ej: Factura A-0001, Pago transferencia...")
        form.addRow("Concepto:", self._input_concepto)

        self._input_comprobante = QLineEdit()
        self._input_comprobante.setFixedHeight(28)
        self._input_comprobante.setPlaceholderText("Nro factura, recibo, etc.")
        form.addRow("Comprobante:", self._input_comprobante)

        self._input_notas = QTextEdit()
        self._input_notas.setMaximumHeight(50)
        form.addRow("Notas:", self._input_notas)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(30)
        btn_cancelar.clicked.connect(self.reject)
        btns.addWidget(btn_cancelar)
        btn_ok = QPushButton("Confirmar")
        btn_ok.setFixedHeight(30)
        btn_ok.clicked.connect(self._confirmar)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _confirmar(self):
        if self._input_monto.value() <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0.")
            return
        if not self._input_concepto.text().strip():
            QMessageBox.warning(self, "Error", "El concepto es obligatorio.")
            return
        self.accept()

    def datos(self) -> dict:
        return {
            "monto": self._input_monto.value(),
            "concepto": self._input_concepto.text().strip(),
            "comprobante": self._input_comprobante.text().strip(),
            "notas": self._input_notas.toPlainText().strip(),
        }
