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
    "Proveedores": (
        "Base de datos de proveedores de la empresa.\n\n"
        "COMO CREAR UN PROVEEDOR:\n"
        "1. Click en '+ Nuevo' en la parte superior\n"
        "2. Completar los datos obligatorios:\n"
        "   • Razon Social: nombre legal del proveedor\n"
        "   • CUIT/RIF: identificacion fiscal\n"
        "   • Condicion de pago: contado, 15, 30 o 60 dias\n"
        "3. Datos opcionales pero recomendados:\n"
        "   • Contacto: nombre, telefono y email del vendedor asignado\n"
        "   • Banco: datos para transferencias\n"
        "   • Categoria: critico, estrategico, regular, esporadico\n"
        "   • Calificacion: 1 a 5 estrellas\n\n"
        "PARA QUE SIRVE:\n"
        "• Al crear una Orden de Compra, seleccionas el proveedor y\n"
        "  el sistema autocompleta condiciones de pago y descuentos\n"
        "• Los reportes de cumplimiento evaluan entregas a tiempo\n"
        "• La calificacion ayuda a decidir a quien comprarle"
    ),
    "Requerimientos": (
        "Solicitudes internas de compra. Cuando un area necesita algo,\n"
        "crea un requerimiento para que Compras gestione la adquisicion.\n\n"
        "COMO CREAR UN REQUERIMIENTO:\n"
        "1. Click '+ Nuevo Requerimiento'\n"
        "2. Seleccionar:\n"
        "   • Sucursal: donde se necesita (o 'General')\n"
        "   • Departamento: quien lo solicita\n"
        "   • Tipo de Compra: operativa, productiva, administrativa\n"
        "3. Buscar productos por codigo o nombre\n"
        "   • Se muestra stock actual, ultimo precio de compra y venta\n"
        "   • Doble click o boton 'Agregar' para incluir al requerimiento\n"
        "4. Click 'Crear Requerimiento'\n\n"
        "QUE PASA DESPUES:\n"
        "• El requerimiento queda en estado 'Pendiente'\n"
        "• Compras lo revisa y puede generar una OC desde el\n"
        "• El solicitante se registra automaticamente (usuario logueado)\n\n"
        "ESTADOS: Pendiente → Aprobado → En OC → Completado"
    ),
    "Req. Sugerido": (
        "El sistema analiza tu inventario y sugiere que comprar.\n\n"
        "COMO FUNCIONA:\n"
        "1. Configurar parametros:\n"
        "   • Cobertura deseada: cuantos dias de stock quieres tener (ej: 30)\n"
        "   • Periodo de analisis: ultimos N dias para calcular consumo\n"
        "   • Filtros: 'Solo bajo minimo' o 'Solo con ventas'\n"
        "2. Click 'Analizar Stock'\n"
        "3. El sistema calcula para cada producto:\n"
        "   • Consumo diario = salidas del periodo / dias\n"
        "   • Cobertura actual = stock / consumo diario\n"
        "   • Cantidad sugerida = (consumo × dias cobertura) - stock\n"
        "4. Click 'Generar Requerimiento' para crear automaticamente\n\n"
        "INDICADORES (cards superiores):\n"
        "• Productos a Reponer: total con necesidad de compra\n"
        "• Inversion Estimada: cuanto costaria reponer todo\n"
        "• Criticos (stock 0): productos sin existencia\n"
        "• Cobertura Promedio: dias promedio que dura el stock\n\n"
        "COLORES EN LA TABLA:\n"
        "• Rojo: stock = 0 (critico)\n"
        "• Amarillo: bajo minimo\n"
        "• Cyan: cantidad sugerida a comprar"
    ),
    "Ordenes de Compra": (
        "Documento formal que se envia al proveedor para solicitar mercaderia.\n\n"
        "COMO CREAR UNA OC:\n"
        "1. Click '+ Nueva Orden'\n"
        "2. Seleccionar proveedor\n"
        "3. Agregar items: descripcion, cantidad, precio unitario\n"
        "4. El sistema calcula subtotal + IVA automaticamente\n"
        "5. Confirmar\n\n"
        "FLUJO DE ESTADOS:\n"
        "• Pendiente: recien creada\n"
        "• Pendiente Aprobacion: si supera el monto de la regla configurada\n"
        "• Enviada: se envio al proveedor (click 'Marcar Enviada')\n"
        "• Recibida: llego la mercaderia (se genera desde Recepcion)\n\n"
        "APROBACION AUTOMATICA:\n"
        "Si configuraste una regla (ej: OC > $5,000 requiere gerente),\n"
        "la OC queda bloqueada hasta que el aprobador la autorice\n"
        "desde la seccion 'Aprobaciones'.\n\n"
        "DESDE REQUERIMIENTO:\n"
        "Tambien puedes generar OC automaticamente desde un requerimiento\n"
        "aprobado, heredando todos los items."
    ),
    "Recepcion": (
        "Registro de mercaderia que llega del proveedor.\n\n"
        "COMO RECIBIR:\n"
        "1. Click 'Recibir OC'\n"
        "2. Seleccionar la OC enviada que estas recibiendo\n"
        "3. Ingresar numero de remito del proveedor\n"
        "4. Click 'Confirmar Recepcion'\n\n"
        "QUE HACE EL SISTEMA:\n"
        "• Copia los items de la OC como recibidos\n"
        "• Cambia el estado de la OC a 'Recibida'\n"
        "• Queda registrado para el Three-Way Match\n\n"
        "DIFERENCIAS:\n"
        "Si lo recibido no coincide con lo pedido (cantidad menor,\n"
        "producto equivocado), queda marcado como 'Con Diferencia'\n"
        "para que el area de compras investigue."
    ),
    "Facturas": (
        "Registro de facturas recibidas de proveedores.\n\n"
        "COMO REGISTRAR:\n"
        "1. Click 'Registrar Factura'\n"
        "2. Ingresar: numero de factura, proveedor, total, vencimiento\n"
        "3. Vincular a una OC (opcional pero recomendado)\n"
        "4. Registrar\n\n"
        "THREE-WAY MATCH (Conciliacion):\n"
        "El boton 'Conciliar' verifica que la factura coincida con:\n"
        "• La Orden de Compra (lo que pediste)\n"
        "• La Recepcion (lo que recibiste)\n"
        "• La Factura (lo que te cobran)\n"
        "Si los tres coinciden → factura conciliada ✓\n\n"
        "TRAZABILIDAD:\n"
        "El boton 'Trazabilidad' muestra la cadena completa:\n"
        "OC → Recepcion → Factura, con fechas y responsables.\n\n"
        "ESTADOS: Pendiente → Pagada / Anulada"
    ),
    "Listas de Precios": (
        "Catalogo de precios por proveedor. Permite saber cuanto\n"
        "cobra cada proveedor por cada producto.\n\n"
        "COMO CREAR UNA LISTA:\n"
        "1. Seleccionar proveedor en el filtro superior\n"
        "2. Click 'Nueva Lista' (nombre + moneda) o\n"
        "3. Click 'Importar Excel' para carga masiva\n\n"
        "FORMATO EXCEL PARA IMPORTAR:\n"
        "Fila 1 = headers (se ignora)\n"
        "Columnas: Codigo Proveedor | Descripcion | Precio | Descuento %\n"
        "(Click 'Plantilla' para descargar el formato)\n\n"
        "PARA QUE SIRVE:\n"
        "• Al crear una OC, el sistema sugiere el precio correcto\n"
        "• Puedes comparar precios entre proveedores\n"
        "• Se marca como 'Vigente' o no vigente"
    ),
    "Cotizaciones": (
        "Comparacion de presupuestos de multiples proveedores\n"
        "para una misma necesidad (Sourcing).\n\n"
        "COMO USAR:\n"
        "1. Click 'Nueva Cotizacion'\n"
        "2. Describir la necesidad (ej: 'Materiales oficina Q1')\n"
        "3. Agregar lineas: seleccionar proveedor, producto, precio,\n"
        "   plazo de entrega y condicion de pago\n"
        "4. Repetir para 2 o 3 proveedores distintos con mismo item\n"
        "5. Click 'Crear Cotizacion'\n\n"
        "COMPARAR:\n"
        "• Seleccionar cotizacion + click 'Comparar'\n"
        "• Tabla resumen: total por proveedor, ★ marca el mas barato\n"
        "• Detalle linea por linea con precios y plazos\n\n"
        "ADJUDICAR:\n"
        "• Click 'Adjudicar' → elegir proveedor ganador\n"
        "• Click 'Generar OC' → crea Orden de Compra automatica\n"
        "  con los items del proveedor adjudicado"
    ),
    "Aprobaciones": (
        "Circuito de aprobaciones para documentos que superan cierto monto.\n\n"
        "3 TABS:\n\n"
        "PENDIENTES:\n"
        "• Lista de OC esperando aprobacion\n"
        "• Muestra: tipo documento, numero, monto, solicitante\n"
        "• Botones: Aprobar (libera la OC) o Rechazar (pide motivo)\n\n"
        "HISTORIAL:\n"
        "• Todas las aprobaciones realizadas con estado y comentario\n\n"
        "REGLAS (configuracion):\n"
        "• Crear regla: 'Si OC > $5,000 USD, requiere aprobacion de [usuario]'\n"
        "• Campos: nombre, documento, condicion (monto mayor / siempre),\n"
        "  valor umbral, moneda, aprobador asignado\n"
        "• Se evalua automaticamente al crear cada OC\n\n"
        "EJEMPLO: Si creas una OC por $8,000 y hay regla de $5,000,\n"
        "la OC queda en 'Pendiente Aprobacion' hasta que el gerente\n"
        "entre a esta seccion y la apruebe."
    ),
    "Trazabilidad": (
        "Permite ver la cadena completa de documentos vinculados.\n\n"
        "COMO USAR:\n"
        "1. Seleccionar tipo de documento (OC, Factura o Recepcion)\n"
        "2. Ingresar el ID del documento\n"
        "3. Click 'Buscar'\n\n"
        "QUE MUESTRA:\n"
        "• Cards visuales conectadas por flechas:\n"
        "  [OC #15] → [Recepcion #8] → [Factura A-0001-123]\n"
        "• Cada card muestra: numero, fecha, proveedor, total, estado\n"
        "• Solicitante original de la OC\n"
        "• Aprobaciones vinculadas con estado y aprobador\n\n"
        "ACCESO RAPIDO:\n"
        "Desde la vista de Facturas, el boton 'Trazabilidad'\n"
        "abre esta vista pre-cargada con la factura seleccionada."
    ),
    "Reportes KPI": (
        "Indicadores clave del area de compras. 3 reportes:\n\n"
        "1. ROTACION DE STOCK:\n"
        "• Muestra productos con problemas: sin stock, bajo minimo,\n"
        "  alta rotacion (se vende mucho), sin movimiento (30 dias)\n"
        "• Boton 'Generar Requerimiento' crea pedido con los criticos\n\n"
        "2. ANALISIS DE GASTOS:\n"
        "• Filtrar por periodo (1/3/6/12 meses)\n"
        "• Agrupar por: Proveedor, Categoria de producto, o Departamento\n"
        "• Cards: total compras, promedio por OC, cantidad de OC\n"
        "• Ranking con % del total + barras visuales top 5\n\n"
        "3. CUMPLIMIENTO PROVEEDORES:\n"
        "• Evalua si cumplen con plazos y cantidades\n"
        "• Metricas: OC enviadas vs recibidas, % cumplimiento,\n"
        "  entregas a tiempo vs con diferencia\n"
        "• Calificacion automatica: ★ a ★★★★★\n"
        "• Colores: verde >= 90%, amarillo >= 70%, rojo < 70%"
    ),
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
