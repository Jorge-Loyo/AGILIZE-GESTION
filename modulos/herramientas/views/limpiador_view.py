from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QGroupBox, QDialog, QDialogButtonBox,
)
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta


class LimpiadorView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cotizacion_actual = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel("Limpiador de Maestro de Productos")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()

        self.btn_cargar = QPushButton("  Cargar Excel")
        self.btn_cargar.setIcon(qta.icon("fa5s.upload", color="#0f0f0f"))
        self.btn_cargar.setCursor(Qt.PointingHandCursor)
        self.btn_cargar.setFixedHeight(36)
        self.btn_cargar.clicked.connect(self._on_cargar)
        header.addWidget(self.btn_cargar)

        self.btn_exportar = QPushButton("  Exportar")
        self.btn_exportar.setIcon(qta.icon("fa5s.file-export", color="#0f0f0f"))
        self.btn_exportar.setCursor(Qt.PointingHandCursor)
        self.btn_exportar.setFixedHeight(36)
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.clicked.connect(self._on_exportar)
        header.addWidget(self.btn_exportar)

        self.btn_pagina = QPushButton("  Archivo Pagina")
        self.btn_pagina.setIcon(qta.icon("fa5s.globe", color="#0f0f0f"))
        self.btn_pagina.setCursor(Qt.PointingHandCursor)
        self.btn_pagina.setFixedHeight(36)
        self.btn_pagina.setEnabled(False)
        self.btn_pagina.clicked.connect(self._on_exportar_pagina)
        header.addWidget(self.btn_pagina)

        layout.addLayout(header)

        # Info
        self.lbl_info = QLabel("Seleccione un archivo Excel (.xls / .xlsx) para cargar la lista de precios")
        self.lbl_info.setObjectName("subtitle")
        layout.addWidget(self.lbl_info)

        # Stats cards
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(12)

        self._stat_productos = self._create_stat_card("Productos", "0")
        self._stat_stock = self._create_stat_card("Stock Total", "0")
        self._stat_inventario = self._create_stat_card("Valor Inventario", "$ 0")
        self._stat_promedio = self._create_stat_card("Precio Promedio", "$ 0")
        self._stat_dolar = self._create_stat_card("Dolar", "---")

        stats_layout.addWidget(self._stat_productos)
        stats_layout.addWidget(self._stat_stock)
        stats_layout.addWidget(self._stat_inventario)
        stats_layout.addWidget(self._stat_promedio)
        stats_layout.addWidget(self._stat_dolar)

        layout.addWidget(stats_frame)

        # Formula info
        try:
            from services.empresa_service import empresa_service
            iva_val = empresa_service.obtener("iva_porcentaje") or "16"
        except Exception:
            iva_val = "16"
        formula_lbl = QLabel(f"IVA {iva_val}%  |  Precio sin IVA = Precio c/IVA / {1 + float(iva_val)/100:.4f}  |  USD = Precio / Cotizacion del dia")
        formula_lbl.setStyleSheet("font-size: 11px; color: #888; padding: 4px 0;")
        layout.addWidget(formula_lbl)

        # Table
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "Codigo", "Descripcion", "Costo", "Precio sin IVA",
            "Precio con IVA", "% Utilidad", "Stock",
            "USD sin IVA", "USD con IVA", "USD s/IVA Rd", "USD c/IVA Rd"
        ])
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        h = self.tabla.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        h.setSectionResizeMode(1, QHeaderView.Stretch)
        for i in range(2, 11):
            h.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        layout.addWidget(self.tabla, 1)

    def _create_stat_card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(130)
        card.setMinimumHeight(70)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #888; font-weight: normal;")
        card_layout.addWidget(lbl)

        val = QLabel(value)
        val.setObjectName("card_valor")
        val.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        val.setWordWrap(True)
        card_layout.addWidget(val)

        card._value_label = val
        return card

    def _set_stat(self, card: QFrame, value: str):
        card._value_label.setText(value)

    def _on_cargar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar lista de precios", "",
            "Archivos Excel (*.xls *.xlsx);;Excel antiguo (*.xls);;Excel moderno (*.xlsx)"
        )
        if not ruta:
            return

        # Verificar cotizacion antes de cargar
        cotizacion = self._obtener_cotizacion_o_pedir()
        if cotizacion is None:
            return

        self._cotizacion_actual = cotizacion
        self.btn_cargar.setEnabled(False)
        self.btn_cargar.setText("  Cargando...")

        class Worker(QThread):
            finished = Signal(object)
            error = Signal(str)

            def __init__(self, ruta):
                super().__init__()
                self._ruta = ruta

            def run(self):
                try:
                    from services.limpiador_service import limpiador_service
                    limpiador_service.cargar(self._ruta)
                    self.finished.emit(limpiador_service)
                except Exception as e:
                    self.error.emit(str(e))

        self._worker = Worker(ruta)
        self._worker.finished.connect(self._on_carga_ok)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _obtener_cotizacion_o_pedir(self) -> float | None:
        """Obtiene cotizacion del dia. Si no hay, abre modal para actualizar."""
        from services.cotizacion_service import (
            obtener_cotizacion_hoy, obtener_ultima_cotizacion, PAISES
        )
        from services.empresa_service import empresa_service

        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"

        # Intentar obtener la de hoy
        hoy = obtener_cotizacion_hoy(pais)
        if hoy:
            return hoy["valor"]

        # No hay cotizacion de hoy - mostrar modal
        dlg = QDialog(self)
        dlg.setWindowTitle("Cotizacion Requerida")
        dlg.setMinimumWidth(420)
        lay = QVBoxLayout(dlg)
        lay.setSpacing(12)

        lay.addWidget(QLabel(
            f"No hay cotizacion del dolar para hoy ({pais}).\n"
            f"Se necesita para calcular precios en divisas."
        ))

        ultima = obtener_ultima_cotizacion(pais)
        if ultima:
            moneda = PAISES.get(pais, {}).get("moneda", "$")
            lbl_ultima = QLabel(f"Ultima: {moneda} {ultima['valor']:,.4f} ({ultima['fecha']})")
            lbl_ultima.setStyleSheet("font-size: 12px; color: #D4AF37; font-weight: bold;")
            lay.addWidget(lbl_ultima)

        resultado = {"valor": None}

        btn_row = QHBoxLayout()

        btn_actualizar = QPushButton("  Actualizar ahora")
        btn_actualizar.setIcon(qta.icon("fa5s.sync", color="#0f0f0f"))
        btn_actualizar.setFixedHeight(32)
        btn_actualizar.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(btn_actualizar)

        btn_usar_ultima = QPushButton("  Usar ultima")
        btn_usar_ultima.setIcon(qta.icon("fa5s.history", color="#F8F9FA"))
        btn_usar_ultima.setFixedHeight(32)
        btn_usar_ultima.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; }")
        btn_usar_ultima.setEnabled(ultima is not None)
        btn_usar_ultima.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(btn_usar_ultima)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setFixedHeight(32)
        btn_cancelar.setStyleSheet("QPushButton { background-color: #2D2D2D; color: #F8F9FA; }")
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_row.addWidget(btn_cancelar)

        lay.addLayout(btn_row)

        def on_actualizar():
            btn_actualizar.setEnabled(False)
            btn_actualizar.setText("  Consultando...")
            try:
                from services.cotizacion_service import actualizar_cotizacion
                r = actualizar_cotizacion(pais)
                resultado["valor"] = r["valor"]
                dlg.accept()
            except Exception as e:
                btn_actualizar.setEnabled(True)
                btn_actualizar.setText("  Actualizar ahora")
                QMessageBox.critical(dlg, "Error", f"No se pudo obtener cotizacion:\n{e}")

        def on_usar_ultima():
            if ultima:
                resultado["valor"] = ultima["valor"]
                dlg.accept()

        btn_actualizar.clicked.connect(on_actualizar)
        btn_usar_ultima.clicked.connect(on_usar_ultima)
        btn_cancelar.clicked.connect(dlg.reject)

        if dlg.exec() == QDialog.Accepted:
            return resultado["valor"]
        return None

    def _on_carga_ok(self, service):
        self.btn_cargar.setEnabled(True)
        self.btn_cargar.setText("  Cargar Excel")
        self.btn_exportar.setEnabled(True)
        self.btn_pagina.setEnabled(True)

        master = service.master
        resumen = service.resumen()
        moneda = getattr(service, '_moneda', 'Bs.')
        cotizacion = self._cotizacion_actual

        self._set_stat(self._stat_productos, str(resumen["total_productos"]))
        self._set_stat(self._stat_stock, f"{resumen['total_stock']:,}")
        self._set_stat(self._stat_inventario, f"{moneda} {resumen['valor_inventario']:,.0f}")
        self._set_stat(self._stat_promedio, f"{moneda} {resumen['precio_promedio']:,.2f}")

        if cotizacion and cotizacion > 0:
            self._set_stat(self._stat_dolar, f"{moneda} {cotizacion:,.4f}")
        else:
            self._set_stat(self._stat_dolar, "---")

        self.lbl_info.setText(f"\u2713 {resumen['total_productos']} productos cargados correctamente")
        self.lbl_info.setStyleSheet("font-size: 12px; color: #10b981;")

        # Poblar tabla
        self.tabla.setRowCount(len(master))
        for i, p in enumerate(master.productos):
            self.tabla.setItem(i, 0, QTableWidgetItem(p.codigo))
            self.tabla.setItem(i, 1, QTableWidgetItem(p.descripcion))
            self.tabla.setItem(i, 2, self._num_item(p.costo))
            self.tabla.setItem(i, 3, self._num_item(p.precio_sin_iva))
            self.tabla.setItem(i, 4, self._num_item(p.precio_con_iva))
            self.tabla.setItem(i, 5, self._num_item(p.porcentaje_utilidad))
            self.tabla.setItem(i, 6, self._num_item(p.stock))

            if cotizacion and cotizacion > 0:
                usd_sin_iva = p.precio_sin_iva / cotizacion
                usd_con_iva = p.precio_con_iva / cotizacion
                usd_sin_iva_rd = self._redondear_arriba_05(usd_sin_iva)
                usd_con_iva_rd = self._redondear_arriba_05(usd_con_iva)
                self.tabla.setItem(i, 7, self._num_item(usd_sin_iva))
                self.tabla.setItem(i, 8, self._num_item(usd_con_iva))
                self.tabla.setItem(i, 9, self._num_item(usd_sin_iva_rd))
                self.tabla.setItem(i, 10, self._num_item(usd_con_iva_rd))
            else:
                self.tabla.setItem(i, 7, QTableWidgetItem("---"))
                self.tabla.setItem(i, 8, QTableWidgetItem("---"))
                self.tabla.setItem(i, 9, QTableWidgetItem("---"))
                self.tabla.setItem(i, 10, QTableWidgetItem("---"))

    def _on_error(self, msg: str):
        self.btn_cargar.setEnabled(True)
        self.btn_cargar.setText("  Cargar Excel")
        self.lbl_info.setText(f"Error: {msg}")
        self.lbl_info.setStyleSheet("font-size: 12px; color: #ef4444;")
        QMessageBox.critical(self, "Error", msg)

    def _on_exportar(self):
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar maestro de productos",
            "Maestro_de_Productos.xlsx", "Excel (*.xlsx)"
        )
        if not ruta:
            return

        try:
            from services.limpiador_service import limpiador_service
            result = limpiador_service.exportar(ruta, cotizacion=self._cotizacion_actual)
            QMessageBox.information(
                self, "Exportacion completada",
                f"Maestro exportado correctamente:\n\n{result}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_exportar_pagina(self):
        """Genera archivo para pagina web: codigo, descripcion, USD con IVA redondeado, stock."""
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo para pagina",
            "Productos_Pagina.xlsx", "Excel (*.xlsx);;CSV (*.csv)"
        )
        if not ruta:
            return

        try:
            from services.limpiador_service import limpiador_service
            import math

            master = limpiador_service.master
            if not master:
                QMessageBox.warning(self, "Error", "No hay datos cargados.")
                return

            cotizacion = self._cotizacion_actual
            if not cotizacion or cotizacion <= 0:
                QMessageBox.warning(self, "Error", "No hay cotizacion disponible para calcular USD.")
                return

            rows = []
            for p in master.productos:
                codigo = p.codigo.strip()
                descripcion = p.descripcion.strip()
                if not codigo or not descripcion:
                    continue

                usd_con_iva = p.precio_con_iva / cotizacion
                usd_redondeado = math.ceil(usd_con_iva * 20) / 20
                stock = max(0, p.stock)

                rows.append({
                    "Codigo": codigo,
                    "Descripcion": descripcion,
                    "Precio_USD": round(usd_redondeado, 2),
                    "Stock": stock,
                })

            import pandas as pd
            df = pd.DataFrame(rows)

            if ruta.endswith(".csv"):
                df.to_csv(ruta, index=False, encoding="utf-8")
            else:
                df.to_excel(ruta, index=False, sheet_name="Productos")

            QMessageBox.information(
                self, "Archivo Generado",
                f"Archivo para pagina generado con {len(rows)} productos:\n\n{ruta}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    @staticmethod
    def _redondear_arriba_05(valor: float) -> float:
        """Redondea hacia arriba al 0.05 mas cercano.
        Ej: 2.56 -> 2.60, 1.44 -> 1.45, 3.01 -> 3.05, 5.00 -> 5.00"""
        import math
        return math.ceil(valor * 20) / 20

    @staticmethod
    def _num_item(value) -> QTableWidgetItem:
        item = QTableWidgetItem(f"{value:,.2f}" if isinstance(value, float) else str(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return item
