"""Vista de Trazabilidad - Cadena completa de documentos de compra."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QFrame, QGridLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt
import qtawesome as qta


class TrazabilidadCompraView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Trazabilidad de Compras")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #D4AF37;")
        layout.addWidget(title)

        info = QLabel("Consulta la cadena completa de un documento: Requisicion → OC → Recepcion → Factura")
        info.setStyleSheet("font-size: 11px; color: #888;")
        layout.addWidget(info)

        # Busqueda
        search = QHBoxLayout()
        search.addWidget(QLabel("Documento:"))
        self._combo_tipo = QComboBox()
        self._combo_tipo.addItem("Orden de Compra", "orden_compra")
        self._combo_tipo.addItem("Factura de Compra", "factura_compra")
        self._combo_tipo.addItem("Recepcion", "recepcion")
        self._combo_tipo.setFixedHeight(28)
        self._combo_tipo.setMinimumWidth(160)
        search.addWidget(self._combo_tipo)

        search.addWidget(QLabel("ID:"))
        self._spin_id = QSpinBox()
        self._spin_id.setRange(1, 999999)
        self._spin_id.setFixedHeight(28)
        self._spin_id.setFixedWidth(80)
        search.addWidget(self._spin_id)

        btn_buscar = QPushButton("  Buscar")
        btn_buscar.setIcon(qta.icon("fa5s.search", color="#0f0f0f"))
        btn_buscar.setFixedHeight(28)
        btn_buscar.clicked.connect(self._buscar)
        search.addWidget(btn_buscar)
        search.addStretch()
        layout.addLayout(search)

        # Resultado visual - cadena
        self._frame_resultado = QFrame()
        self._frame_resultado.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; }")
        self._resultado_layout = QVBoxLayout(self._frame_resultado)
        self._resultado_layout.setContentsMargins(16, 16, 16, 16)
        self._resultado_layout.setSpacing(10)
        self._lbl_vacio = QLabel("Selecciona un documento y presiona Buscar")
        self._lbl_vacio.setStyleSheet("color: #666; font-size: 12px;")
        self._lbl_vacio.setAlignment(Qt.AlignCenter)
        self._resultado_layout.addWidget(self._lbl_vacio)
        layout.addWidget(self._frame_resultado, 1)

    def _buscar(self):
        tipo = self._combo_tipo.currentData()
        doc_id = self._spin_id.value()

        from services.compras.compras_service import compras_service
        traza = compras_service.obtener_trazabilidad(tipo, doc_id)

        # Limpiar resultado anterior
        while self._resultado_layout.count():
            child = self._resultado_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Verificar si hay datos
        if not traza["orden_compra"] and not traza["factura"] and not traza["recepcion"]:
            lbl = QLabel("No se encontro el documento o no tiene trazabilidad.")
            lbl.setStyleSheet("color: #ef4444; font-size: 12px;")
            lbl.setAlignment(Qt.AlignCenter)
            self._resultado_layout.addWidget(lbl)
            return

        # Header
        header = QLabel("Cadena de Trazabilidad")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37;")
        self._resultado_layout.addWidget(header)

        # Flujo visual
        flow = QHBoxLayout()
        flow.setSpacing(8)

        # OC
        if traza["orden_compra"]:
            oc = traza["orden_compra"]
            flow.addWidget(self._doc_card(
                "Orden de Compra",
                f"#{oc['numero']}",
                [
                    f"Fecha: {oc['fecha'].strftime('%d/%m/%Y') if oc['fecha'] else '--'}",
                    f"Proveedor: {oc['proveedor']}",
                    f"Total: $ {oc['total']:,.2f}",
                    f"Estado: {oc['estado']}",
                    f"Solicitante: {oc['solicitante']}",
                ],
                "#3b82f6"
            ))
            flow.addWidget(self._arrow())

        # Recepcion
        if traza["recepcion"]:
            rec = traza["recepcion"]
            flow.addWidget(self._doc_card(
                "Recepcion / Remito",
                f"#{rec['numero']}",
                [
                    f"Fecha: {rec['fecha'].strftime('%d/%m/%Y') if rec['fecha'] else '--'}",
                    f"Remito: {rec.get('remito', '--')}",
                ],
                "#10b981"
            ))
            flow.addWidget(self._arrow())

        # Factura
        if traza["factura"]:
            fact = traza["factura"]
            flow.addWidget(self._doc_card(
                "Factura Compra",
                fact["numero"],
                [
                    f"Fecha: {fact['fecha'].strftime('%d/%m/%Y') if fact['fecha'] else '--'}",
                    f"Total: $ {fact['total']:,.2f}",
                    f"Estado: {fact['estado']}",
                ],
                "#f59e0b"
            ))

        flow.addStretch()
        self._resultado_layout.addLayout(flow)

        # Aprobaciones
        if traza["aprobaciones"]:
            self._resultado_layout.addWidget(QLabel(""))
            lbl_apr = QLabel("Aprobaciones:")
            lbl_apr.setStyleSheet("font-weight: bold; font-size: 12px;")
            self._resultado_layout.addWidget(lbl_apr)

            tabla = QTableWidget()
            tabla.setColumnCount(4)
            tabla.setHorizontalHeaderLabels(["Estado", "Aprobador", "Fecha", "Comentario"])
            tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            tabla.setAlternatingRowColors(True)
            tabla.verticalHeader().setVisible(False)
            tabla.setEditTriggers(QTableWidget.NoEditTriggers)
            tabla.setMaximumHeight(100)
            tabla.setRowCount(len(traza["aprobaciones"]))
            for i, a in enumerate(traza["aprobaciones"]):
                estado_item = QTableWidgetItem(a["estado"].capitalize())
                if a["estado"] == "aprobada":
                    estado_item.setForeground(Qt.green)
                elif a["estado"] == "rechazada":
                    estado_item.setForeground(Qt.red)
                tabla.setItem(i, 0, estado_item)
                tabla.setItem(i, 1, QTableWidgetItem(a["aprobador"]))
                tabla.setItem(i, 2, QTableWidgetItem(a["fecha"].strftime("%d/%m/%Y") if a["fecha"] else ""))
                tabla.setItem(i, 3, QTableWidgetItem(a["comentario"]))
            self._resultado_layout.addWidget(tabla)

        self._resultado_layout.addStretch()

    def _doc_card(self, titulo: str, numero: str, lineas: list, color: str) -> QFrame:
        card = QFrame()
        card.setMinimumWidth(200)
        card.setMaximumWidth(250)
        card.setStyleSheet(f"QFrame {{ background-color: #252525; border: 2px solid {color}; border-radius: 8px; }}")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(3)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {color};")
        lay.addWidget(lbl_titulo)

        lbl_num = QLabel(numero)
        lbl_num.setStyleSheet("font-size: 14px; font-weight: bold; color: #F8F9FA;")
        lay.addWidget(lbl_num)

        for linea in lineas:
            lbl = QLabel(linea)
            lbl.setStyleSheet("font-size: 10px; color: #aaa;")
            lay.addWidget(lbl)

        return card

    def _arrow(self) -> QLabel:
        lbl = QLabel("→")
        lbl.setStyleSheet("font-size: 20px; color: #D4AF37; font-weight: bold;")
        lbl.setAlignment(Qt.AlignCenter)
        return lbl
