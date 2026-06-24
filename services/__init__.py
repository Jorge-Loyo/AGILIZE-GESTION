"""
Paquete de servicios de Agilize Gestion.

Estructura logica por modulo:

CORE (infraestructura):
    - auth_service          -> Autenticacion y sesion
    - audit_service         -> Log de auditoria
    - empresa_service       -> Datos de empresa
    - dashboard_service     -> Indicadores del dashboard
    - backup_service        -> Respaldo de BD
    - update_service        -> Actualizaciones
    - reset_service         -> Reset de datos
    - logo_service          -> Logo de la app

RRHH (recursos humanos):
    - empleado_service      -> CRUD empleados
    - asistencia_service    -> Fichadas y asistencia
    - calculo_asistencia_service -> Calculo de horas
    - import_fichadas_service -> Importacion de reloj
    - nomina_service        -> Liquidacion de sueldos
    - config_nomina_service -> Configuracion de nomina
    - liquidacion_pendiente_service -> Pendientes de liquidar
    - recibo_pdf_service    -> Generacion de recibos PDF
    - sac_service           -> Aguinaldo / SAC
    - vacaciones_service    -> Vacaciones
    - permiso_ausencia_service -> Permisos y ausencias
    - aprobacion_extras_service -> Aprobacion horas extra
    - adelanto_service      -> Adelantos con cuotas
    - cierre_service        -> Cierres de periodo
    - periodo_service       -> Periodo de pago
    - formulario_alta_service -> PDF formulario alta

INVENTARIO (paquete modular: services/inventario/):
    - inventario_service    -> Fachada unificada
      - catalogo_service    -> Categorias, marcas, UOM, productos, depositos
      - stock_service       -> Movimientos, transferencias, ajustes
      - lotes_service       -> Lotes y vencimientos
      - series_service      -> Numeros de serie y garantias
      - toma_service        -> Inventario fisico
      - valorizacion_service -> PPP, FIFO, LIFO
      - alertas_service     -> Stock min/max, reposicion automatica

COMPRAS:
    - compras_service       -> Circuito OC, requisiciones, recepciones, facturas

VENTAS:
    - ventas_service        -> Circuito presupuestos, pedidos, remitos, facturas
    - reportes_venta_service -> ABC, comisiones, margen

CLIENTES (paquete modular: services/clientes/):
    - cliente_service       -> Fachada unificada
      - crud_service        -> CRUD clientes
      - direcciones_service -> Direcciones y contactos
      - credito_service     -> Credito, bloqueos, pagos

PRECIOS (paquete modular: services/precios/):
    - precios_venta_service -> Fachada unificada
      - listas_service      -> Multi-listas de precios
      - descuentos_service  -> Reglas de descuento
      - moneda_service      -> Tipo de cambio, conversion

FINANZAS:
    - finanzas_service      -> Contabilidad, caja, bancos
    - cuentas_service       -> Plan de cuentas
    - estado_cuenta_service -> Estado de cuenta clientes/proveedores
    - riesgo_venta_service  -> Control credito y margen

HERRAMIENTAS:
    - etiquetas_service     -> Generacion de etiquetas
    - limpiador_service     -> Limpieza de productos
    - cotizacion_service    -> Tipo de cambio BCV/BNA
    - export_service        -> Exportacion Excel
    - import_service        -> Importacion masiva

DATOS MAESTROS:
    - datos_service         -> Proveedores, departamentos, cargos
    - admin_service         -> Administracion general
    - facturador_config_service -> Config facturadores/POS
"""
