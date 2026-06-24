from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QFrame, QMessageBox, QScrollArea,
)
from PySide6.QtCore import Qt, QThread, Signal
import qtawesome as qta
from services.core.empresa_service import empresa_service


class CotizacionesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar_ultima()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setMaximumWidth(650)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        title = QLabel("Cotizacion de Divisas")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Obtiene el valor del dolar desde fuentes oficiales. Se guarda un valor por dia.")
        subtitle.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(subtitle)

        GRP_STYLE = "QGroupBox { font-weight: bold; font-size: 12px; padding-top: 14px; margin-top: 4px; }"

        # --- Seleccion de pais ---
        grp_pais = QGroupBox("Pais y Fuente")
        grp_pais.setStyleSheet(GRP_STYLE)
        pais_layout = QHBoxLayout(grp_pais)
        pais_layout.setSpacing(10)

        pais_layout.addWidget(QLabel("Pais:"))
        self._combo_pais = QComboBox()
        self._combo_pais.setFixedHeight(30)
        self._combo_pais.setMinimumWidth(180)
        self._combo_pais.addItem("Venezuela", "Venezuela")
        self._combo_pais.addItem("Argentina", "Argentina")
        self._combo_pais.currentIndexChanged.connect(self._on_pais_change)
        pais_layout.addWidget(self._combo_pais)

        self._lbl_fuente = QLabel("")
        self._lbl_fuente.setStyleSheet("font-size: 11px; color: #aaa;")
        pais_layout.addWidget(self._lbl_fuente, 1)

        self._btn_actualizar = QPushButton("  Obtener cotizacion")
        self._btn_actualizar.setIcon(qta.icon("fa5s.sync", color="#0f0f0f"))
        self._btn_actualizar.setFixedHeight(32)
        self._btn_actualizar.setFixedWidth(180)
        self._btn_actualizar.setCursor(Qt.PointingHandCursor)
        self._btn_actualizar.clicked.connect(self._actualizar)
        pais_layout.addWidget(self._btn_actualizar)

        layout.addWidget(grp_pais)

        # --- Cotizacion actual ---
        grp_cotiz = QGroupBox("Cotizacion del Dia")
        grp_cotiz.setStyleSheet(GRP_STYLE)
        cotiz_layout = QVBoxLayout(grp_cotiz)
        cotiz_layout.setSpacing(10)

        # Cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        self._card_valor = self._create_card("Dolar", "---")
        self._card_fecha = self._create_card("Fecha", "---")
        self._card_estado = self._create_card("Estado", "Sin datos")

        cards_row.addWidget(self._card_valor)
        cards_row.addWidget(self._card_fecha)
        cards_row.addWidget(self._card_estado)
        cotiz_layout.addLayout(cards_row)

        self._lbl_detalle = QLabel("")
        self._lbl_detalle.setStyleSheet("font-size: 11px; color: #888;")
        self._lbl_detalle.setWordWrap(True)
        cotiz_layout.addWidget(self._lbl_detalle)

        layout.addWidget(grp_cotiz)

        # --- Guardar como predeterminado ---
        grp_default = QGroupBox("Pais Predeterminado")
        grp_default.setStyleSheet(GRP_STYLE)
        default_layout = QHBoxLayout(grp_default)
        default_layout.setSpacing(8)

        self._lbl_pais_actual = QLabel("")
        self._lbl_pais_actual.setStyleSheet("font-size: 12px;")
        default_layout.addWidget(self._lbl_pais_actual, 1)

        btn_guardar_pais = QPushButton("  Guardar como predeterminado")
        btn_guardar_pais.setIcon(qta.icon("fa5s.save", color="#10b981"))
        btn_guardar_pais.setFixedHeight(30)
        btn_guardar_pais.setFixedWidth(220)
        btn_guardar_pais.setCursor(Qt.PointingHandCursor)
        btn_guardar_pais.clicked.connect(self._guardar_pais)
        default_layout.addWidget(btn_guardar_pais)

        layout.addWidget(grp_default)

        layout.addStretch()

        # Centrar
        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addStretch()
        wrapper_layout.addWidget(page)
        wrapper_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(wrapper)
        main_layout.addWidget(scroll)

        self._on_pais_change()

    def _create_card(self, label: str, value: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumWidth(160)
        card.setMinimumHeight(70)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-size: 11px; color: #888; font-weight: normal;")
        card_layout.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        card_layout.addWidget(val)

        card._value_label = val
        return card

    def _set_card(self, card: QFrame, value: str):
        card._value_label.setText(value)

    def _on_pais_change(self):
        pais = self._combo_pais.currentData()
        from services.herramientas.cotizacion_service import PAISES
        info = PAISES.get(pais, {})
        self._lbl_fuente.setText(f"Fuente: {info.get('url', '')}")

        # Cargar pais guardado
        pais_guardado = empresa_service.obtener("cotizacion_pais") or ""
        self._lbl_pais_actual.setText(
            f"Pais actual: {pais_guardado}" if pais_guardado else "Sin pais configurado"
        )

    def _cargar_ultima(self):
        """Carga la ultima cotizacion guardada al abrir."""
        pais_guardado = empresa_service.obtener("cotizacion_pais")
        if pais_guardado:
            idx = self._combo_pais.findData(pais_guardado)
            if idx >= 0:
                self._combo_pais.setCurrentIndex(idx)

            from services.herramientas.cotizacion_service import obtener_ultima_cotizacion
            ultima = obtener_ultima_cotizacion(pais_guardado)
            if ultima:
                from services.herramientas.cotizacion_service import PAISES
                moneda = PAISES.get(pais_guardado, {}).get("moneda", "$")
                self._set_card(self._card_valor, f"{moneda} {ultima['valor']:,.4f}")
                self._set_card(self._card_fecha, ultima["fecha"])
                self._set_card(self._card_estado, "Guardada")
                self._lbl_detalle.setText(
                    f"Ultima cotizacion de {pais_guardado} obtenida el {ultima['fecha']}"
                )

    def _actualizar(self):
        pais = self._combo_pais.currentData()
        self._btn_actualizar.setEnabled(False)
        self._btn_actualizar.setText("  Consultando...")
        self._set_card(self._card_estado, "Consultando...")

        class Worker(QThread):
            finished = Signal(dict)
            error = Signal(str)

            def __init__(self, pais):
                super().__init__()
                self._pais = pais

            def run(self):
                try:
                    from services.herramientas.cotizacion_service import actualizar_cotizacion
                    result = actualizar_cotizacion(self._pais)
                    self.finished.emit(result)
                except Exception as e:
                    self.error.emit(str(e))

        self._worker = Worker(pais)
        self._worker.finished.connect(self._on_ok)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_ok(self, result: dict):
        self._btn_actualizar.setEnabled(True)
        self._btn_actualizar.setText("  Obtener cotizacion")

        pais = result["pais"]
        from services.herramientas.cotizacion_service import PAISES
        moneda = PAISES.get(pais, {}).get("moneda", "$")

        self._set_card(self._card_valor, f"{moneda} {result['valor']:,.4f}")
        self._set_card(self._card_fecha, result["fecha"])
        self._set_card(self._card_estado, "Actualizada")
        self._lbl_detalle.setText(
            f"1 USD = {moneda} {result['valor']:,.4f} (fuente: {PAISES[pais]['descripcion']})"
        )

    def _on_error(self, msg: str):
        self._btn_actualizar.setEnabled(True)
        self._btn_actualizar.setText("  Obtener cotizacion")
        self._set_card(self._card_estado, "Error")
        self._lbl_detalle.setText(f"Error: {msg}")
        QMessageBox.critical(self, "Error", f"No se pudo obtener la cotizacion:\n\n{msg}")

    def _guardar_pais(self):
        pais = self._combo_pais.currentData()
        empresa_service.guardar("cotizacion_pais", pais)
        self._lbl_pais_actual.setText(f"Pais actual: {pais}")
        QMessageBox.information(self, "OK", f"Pais predeterminado guardado: {pais}")
