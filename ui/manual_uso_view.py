"""Manual de uso integrado por modulo - Estilo visual mejorado."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt


# === CONTENIDO DE MANUALES POR MODULO ===

MANUAL_RRHH = {
    "Dashboard": (
        "Resumen general del modulo RRHH.\n\n"
        "• Cards con metricas: empleados activos, registros del mes, liquidaciones\n"
        "• Notificaciones: alertas de registros incompletos, pendientes de liquidar\n"
        "• Click en una alerta te guia a la seccion correspondiente"
    ),
    "Empleados": (
        "Gestion completa del personal.\n\n"
        "• + Nuevo: datos personales, laborales, contacto emergencia, cuenta bancaria\n"
        "• Tipo Liquidacion: 'Por hora' (fichado) o 'Mensual' (descuento faltas)\n"
        "• Tipo Contrato: indefinido, temporal, pasantia, eventual\n"
        "• Importar/Exportar: carga masiva desde Excel\n"
        "• Detalle: doble click para ver ficha completa"
    ),
    "Legajo": (
        "Expediente digital del empleado.\n\n"
        "• Historial completo: ascensos, cambios de sueldo, sanciones\n"
        "• Entrega de herramientas (PC, uniforme, telefono)\n"
        "• Evaluaciones de desempeno con resultado\n"
        "• Capacitaciones realizadas\n"
        "• Cada evento registra fecha, usuario y valores anterior/nuevo"
    ),
    "Asistencia": (
        "Control de fichadas y asistencia.\n\n"
        "• Filtrar por empleado, periodo, estado\n"
        "• Importar fichadas desde reloj (XLS) o planilla (XLSX)\n"
        "• Registro manual individual\n"
        "• Vacaciones: solicitar, aprobar, calcular por antiguedad\n"
        "• Aprobacion de horas extra con workflow"
    ),
    "Fichaje / Turnos": (
        "Terminal de fichaje y gestion de turnos.\n\n"
        "FICHAR:\n"
        "• Ingresar legajo + Entrada o Salida\n"
        "• Al fichar salida se registra asistencia automatica\n"
        "• Compatible con lectores de codigo de barras\n\n"
        "IMPORTAR FICHADAS:\n"
        "• XLS (reloj fichador): vincula por legajo\n"
        "• XLSX (manual): vincula por nombre de hoja\n\n"
        "TURNOS LABORALES:\n"
        "• Manana, Tarde, Noche, Comercial, Part-Time\n"
        "• Tolerancia de entrada configurable\n"
        "• Calculo automatico de tardanzas y salidas anticipadas\n\n"
        "TIPOS DE HORA EXTRA:\n"
        "• 50%: exceso jornada normal o sabado\n"
        "• 100%: domingo o feriado\n"
        "• Nocturna: entre 21:00 y 06:00"
    ),
    "Cierres": (
        "Cierre de periodos de asistencia.\n\n"
        "• Seleccionar rango de fechas\n"
        "• Si hay incompletos, NO permite cerrar\n"
        "• Una vez cerrado, no se puede modificar\n"
        "• Se puede reabrir si es necesario\n"
        "• Requisito para liquidar el periodo"
    ),
    "Nomina": (
        "Liquidacion de sueldos.\n\n"
        "CONCEPTOS:\n"
        "• Haberes remunerativos: sueldo, antiguedad, presentismo, comisiones\n"
        "• Haberes no remunerativos: viaticos, bonos\n"
        "• Retenciones: jubilacion, obra social, impuestos\n"
        "• Calculo: porcentaje, fijo, o por dia\n\n"
        "LIQUIDACION:\n"
        "• Individual o MASIVA (toda la plantilla)\n"
        "• Descuenta adelantos automaticamente\n"
        "• Registra para SAC\n\n"
        "RECIBOS PDF:\n"
        "• Generacion individual o masiva\n"
        "• Detalle de horas, conceptos, multiplicadores"
    ),
    "Reclutamiento": (
        "Seleccion de personal (ATS basico).\n\n"
        "VACANTES:\n"
        "• Crear oferta con departamento, cargo, requisitos\n"
        "• Prioridad: baja, normal, alta, urgente\n"
        "• Estados: abierta, en proceso, cerrada\n\n"
        "CANDIDATOS:\n"
        "• Agregar postulantes con datos y CV\n"
        "• Pipeline: Postulado → Entrevista → Evaluando → Contratado/Rechazado\n"
        "• Al contratar: genera datos para crear empleado directo"
    ),
    "Configuracion": (
        "Parametros del modulo RRHH.\n\n"
        "• Periodo de pago: mensual, quincenal, semanal, diario\n"
        "• Multiplicadores: hora extra, sabado, domingo, feriado\n"
        "• Conceptos de nomina: CRUD configurables\n"
        "• Feriados: ABM por ano"
    ),
}

MANUAL_COMPRAS = {
    "Proveedores": "Gestion de proveedores: datos fiscales, contacto, condiciones comerciales, evaluacion.",
    "Requerimientos": "Solicitudes internas de compra. Seleccionar sucursal, departamento, tipo de compra y productos.",
    "Req. Sugerido": "Analisis inteligente: stock vs consumo vs cobertura. Genera requerimiento automatico.",
    "Ordenes de Compra": "Circuito OC: crear, enviar, recibir. Aprobacion automatica si supera monto configurado.",
    "Recepcion": "Registro de mercaderia recibida. Vincula con OC, descuenta de pendientes.",
    "Facturas": "Facturas de compra con Three-Way Match (OC + Recepcion + Factura).",
    "Listas de Precios": "Importar listas de proveedores desde Excel. Precio sugerido automatico en OC.",
    "Cotizaciones": "Comparar presupuestos de 3+ proveedores. Adjudicar y generar OC.",
    "Aprobaciones": "Reglas configurables: si OC > $5,000 requiere firma de gerente.",
    "Trazabilidad": "Cadena completa: Requisicion → OC → Recepcion → Factura.",
    "Reportes KPI": "Rotacion stock, analisis gastos (proveedor/categoria), cumplimiento proveedores.",
}

MANUAL_INVENTARIO = {
    "Productos": "Maestro de articulos: fisico, servicio, kit. Multiples codigos de barra, UOM, marcas.",
    "Depositos": "Multi-deposito con ubicaciones (pasillo-estante-altura). Tipos: central, fallados, transito.",
    "Movimientos": "Entrada, salida, transferencia (en transito), consumo interno, ajuste, reubicacion.",
    "Lotes": "Control de lotes con vencimiento. Alertas FEFO. Recall por lote.",
    "Series": "Numeros de serie unitarios. Trazabilidad venta + garantia + devolucion.",
    "Toma Stock": "Inventario fisico: congelar teorico, conteo ciego, ajuste automatico.",
    "Valorizacion": "PPP (promedio), FIFO (primero entrado), LIFO (ultimo entrado).",
    "Alertas": "Stock min/max, punto de pedido, reposicion automatica a Compras.",
}

MANUAL_VENTAS = {
    "Clientes": "Ficha expandida: fiscal, direcciones entrega multiples, contactos, credito, cobrador.",
    "Presupuestos": "Cotizacion con validez. Convertir a pedido con un click.",
    "Pedidos": "Compromete stock. Direccion entrega, condicion pago, fecha entrega.",
    "Remitos": "Despacho que mueve stock. Transportista, deposito origen.",
    "Facturas": "Documento fiscal: tipo A/B/C/E, IVA, descuentos, CAE electronico.",
    "Notas Cred/Deb": "Devoluciones, anulaciones, correccion de precios.",
    "Riesgo": "Control credito automatico + margen minimo + descuento maximo.",
    "Reportes": "ABC productos/clientes, comisiones vendedores, margen contribucion.",
}

MANUAL_FACTURADOR = {
    "Punto de Venta": "POS rapido: escanear codigo, F12 cobrar, vuelto automatico, pago partido.",
    "Facturacion Central": "B2B: buscar cliente, importar pedido/remito previo, condiciones a plazo.",
    "Cajas / Turnos": "Abrir turno con fondo, retiros/ingresos, cierre con arqueo ciego.",
    "Historial": "Lista de facturas emitidas con filtros.",
}

MANUAL_FINANZAS = {
    "Contabilidad": "Plan de cuentas, asientos contables, libro diario.",
    "Facturacion": "Emision de facturas de venta con integracion fiscal.",
    "Bancos": "Cuentas bancarias, movimientos, conciliacion.",
    "Caja": "Caja diaria, ingresos/egresos, cierre.",
}

MANUAL_CONFIG = {
    "Datos Empresa": "Razon social, CUIT, direccion. Aparece en recibos y facturas.",
    "Visual": "Logo y nombre comercial personalizable.",
    "Usuarios": "Crear usuarios, asignar roles, activar/desactivar.",
    "Roles y Permisos": "Matriz de permisos por modulo y accion.",
    "Auditoria": "Log de todas las acciones: quien, que, cuando.",
    "Actualizar": "Verificar nueva version y actualizar desde Git.",
}


# === WIDGET DE MANUAL CON ESTILO MEJORADO ===

class ManualUsoView(QWidget):
    def __init__(self, contenido: dict, titulo: str = "Manual de Uso", parent=None):
        super().__init__(parent)
        self._build_ui(contenido, titulo)

    def _build_ui(self, contenido: dict, titulo: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(0)

        # Header con icono
        header = QHBoxLayout()
        icon_lbl = QLabel("📖")
        icon_lbl.setStyleSheet("font-size: 24px;")
        header.addWidget(icon_lbl)
        title = QLabel(titulo)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(16)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        clayout = QVBoxLayout(content)
        clayout.setSpacing(12)
        clayout.setContentsMargins(0, 0, 12, 0)

        for seccion, texto in contenido.items():
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-left: 4px solid #D4AF37;
                    border-radius: 6px;
                    padding: 12px;
                }
            """)
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(12, 8, 12, 8)
            card_lay.setSpacing(6)

            lbl_sec = QLabel(f"▸ {seccion}")
            lbl_sec.setStyleSheet("font-size: 14px; font-weight: bold; color: #D4AF37; border: none;")
            card_lay.addWidget(lbl_sec)

            lbl_txt = QLabel(texto)
            lbl_txt.setWordWrap(True)
            lbl_txt.setStyleSheet("font-size: 12px; color: #ccc; border: none; line-height: 1.4;")
            card_lay.addWidget(lbl_txt)

            clayout.addWidget(card)

        clayout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
