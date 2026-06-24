"""
Limpiar BD dejando solo datos SEED por defecto.
Borra datos de prueba, mantiene configuracion base.
"""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

print("=" * 60)
print("LIMPIANDO BASE DE DATOS - Solo quedan seeds")
print("=" * 60)

# === BORRAR DATOS DE PRUEBA (orden: primero hijos, luego padres) ===
tablas_limpiar = [
    # Movimientos y detalles
    "movimientos_caja_pos",
    "turnos_caja",
    "fichajes_pin",
    "legajo_eventos",
    "toma_inventario_detalles",
    "tomas_inventario",
    "movimientos_stock",
    "movimientos_banco",
    "movimientos_caja",
    "movimientos_cuenta",
    "codigos_barra_producto",
    "kit_detalles",
    "conversiones_uom",
    # Compras
    "cotizacion_compra_detalles",
    "cotizaciones_compra",
    "aprobaciones_compra",
    "factura_compra_detalles",
    "facturas_compra",
    "recepcion_detalles",
    "recepciones_compra",
    "lista_precio_detalles",
    "listas_precio_proveedor",
    "orden_compra_detalles",
    "ordenes_compra",
    "requisicion_detalles",
    "requisiciones",
    # Ventas
    "nota_credito_debito_detalles",
    "notas_credito_debito",
    "factura_venta_detalles",
    "facturas_venta",
    "remito_salida_detalles",
    "remitos_salida",
    "pedido_venta_detalles",
    "pedidos_venta",
    "presupuesto_detalles",
    "presupuestos",
    "lista_precio_venta_items",
    "reglas_descuento",
    "tipos_cambio",
    # Finanzas
    "asiento_detalles",
    "asientos",
    "factura_detalles",
    "facturas",
    # RRHH
    "liquidacion_detalle",
    "liquidaciones",
    "sac_liquidaciones",
    "sac_registros",
    "historico_sueldo",
    "aprobacion_extras",
    "adelantos",
    "vacaciones",
    "ausencias",
    "permisos_empleado",
    "asistencias",
    "cierres_asistencia",
    "cierres_liquidacion",
    # Reclutamiento
    "candidatos",
    "vacantes",
    # Inventario
    "numeros_serie",
    "lotes_producto",
    "stock_deposito",
    # Datos
    "audit_log",
    "direcciones_entrega_cliente",
    "contactos_cliente",
    # Maestros de prueba
    "clientes",
    "productos",
    "empleados",
    "proveedores",
]

for tabla in tablas_limpiar:
    try:
        cur.execute(f"TRUNCATE TABLE {tabla} CASCADE")
        print(f"  TRUNCATE {tabla}")
    except Exception as e:
        conn.rollback()
        conn.autocommit = True

# === SEEDS QUE DEBEN EXISTIR ===
print("\n" + "=" * 60)
print("INSERTANDO SEEDS POR DEFECTO")
print("=" * 60)

# Roles (primero, porque usuarios depende de roles)
cur.execute("TRUNCATE TABLE rol_permisos, usuario_permisos, permisos, usuarios, roles CASCADE")
cur.execute("""
INSERT INTO roles (id, nombre, descripcion, activo) VALUES
    (1, 'Administrador', 'Acceso total al sistema', TRUE),
    (2, 'Usuario', 'Acceso estandar', TRUE),
    (3, 'Cajero', 'Acceso al facturador y cajas', TRUE)
""")
print("  + Roles (3)")

# Usuario master
cur.execute("""
INSERT INTO usuarios (id, username, nombre_completo, email, password_hash, activo, rol_id)
VALUES (1, 'master', 'Administrador', 'admin@sistema.local', '$2b$12$LQv3c1yqBo9SkvXS7QTJPe6YJ5R5fR7VXR3x7VZV3Q3R3R3R3R3R3', TRUE, 1)
""")
print("  + Usuario master")

# Sucursal default
cur.execute("""
INSERT INTO sucursales (id, nombre, activo) VALUES (1, 'Casa Central', TRUE)
ON CONFLICT (id) DO UPDATE SET nombre='Casa Central'
""")
print("  + Sucursal Casa Central")

# Departamentos
cur.execute("""
INSERT INTO departamentos (id, nombre, activo) VALUES
    (1, 'Administracion', TRUE),
    (2, 'Ventas', TRUE),
    (3, 'Compras', TRUE),
    (4, 'Logistica', TRUE),
    (5, 'Produccion', TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Departamentos (5)")

# Cargos
cur.execute("""
INSERT INTO cargos (id, nombre, activo) VALUES
    (1, 'Gerente', TRUE),
    (2, 'Supervisor', TRUE),
    (3, 'Empleado', TRUE),
    (4, 'Vendedor', TRUE),
    (5, 'Cajero', TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Cargos (5)")

# Depositos
cur.execute("""
INSERT INTO depositos (id, nombre, tipo, activo) VALUES
    (1, 'Deposito Central', 'central', TRUE),
    (2, 'Deposito Sucursal', 'sucursal', TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Depositos (2)")

# Tipos de compra
cur.execute("""
INSERT INTO tipos_compra (id, nombre, activo) VALUES
    (1, 'Operativa', TRUE),
    (2, 'Productiva', TRUE),
    (3, 'Administrativa', TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Tipos Compra (3)")

# Tipos permiso empleado
cur.execute("TRUNCATE TABLE tipos_permiso CASCADE")
cur.execute("""
INSERT INTO tipos_permiso (id, nombre, con_goce, activo) VALUES
    (1, 'Enfermedad', TRUE, TRUE),
    (2, 'Estudio', TRUE, TRUE),
    (3, 'Maternidad', TRUE, TRUE),
    (4, 'Personal', FALSE, TRUE)
""")
print("  + Tipos Permiso (4)")

# Conceptos nomina basicos
cur.execute("DELETE FROM conceptos_nomina")
cur.execute("""
INSERT INTO conceptos_nomina (id, codigo, nombre, tipo, categoria, calculo, porcentaje, monto_fijo, base_calculo, aplica_a, activo) VALUES
    (1, 'ANTI', 'Antiguedad', 'haber', 'remunerativo', 'porcentaje', 1.0, NULL, 'basico', 'todos', TRUE),
    (2, 'PRES', 'Presentismo', 'haber', 'remunerativo', 'porcentaje', 8.33, NULL, 'basico', 'todos', TRUE),
    (3, 'JUB', 'Jubilacion', 'deduccion', 'retencion', 'porcentaje', 11.0, NULL, 'bruto', 'todos', TRUE),
    (4, 'OS', 'Obra Social', 'deduccion', 'retencion', 'porcentaje', 3.0, NULL, 'bruto', 'todos', TRUE),
    (5, 'SIND', 'Sindicato', 'deduccion', 'retencion', 'porcentaje', 2.5, NULL, 'bruto', 'todos', TRUE),
    (6, 'VIAT', 'Viaticos', 'haber', 'no_remunerativo', 'fijo', NULL, 0, 'basico', 'todos', TRUE),
    (7, 'BONO', 'Bono Extraordinario', 'haber', 'no_remunerativo', 'fijo', NULL, 0, 'basico', 'todos', TRUE),
    (8, 'COMI', 'Comision Ventas', 'haber', 'remunerativo', 'fijo', NULL, 0, 'basico', 'todos', TRUE),
    (9, 'ASIG', 'Asignacion Familiar', 'haber', 'no_remunerativo', 'fijo', NULL, 0, 'basico', 'todos', TRUE),
    (10, 'IIGG', 'Imp. Ganancias', 'deduccion', 'retencion', 'porcentaje', 0, NULL, 'bruto', 'todos', TRUE)
ON CONFLICT (id) DO UPDATE SET nombre=EXCLUDED.nombre, tipo=EXCLUDED.tipo, activo=TRUE
""")
print("  + Conceptos Nomina (10)")

# Config nomina (solo valores numericos)
cur.execute("DELETE FROM config_nomina")
cur.execute("""
INSERT INTO config_nomina (clave, valor, descripcion) VALUES
    ('multiplicador_extra', 1.50, 'Hora extra normal'),
    ('multiplicador_sabado', 1.50, 'Hora sabado'),
    ('multiplicador_domingo', 2.00, 'Hora domingo'),
    ('multiplicador_feriado', 2.00, 'Hora feriado'),
    ('multiplicador_nocturno', 1.75, 'Hora nocturna')
""")
print("  + Config Nomina (5)")

# Datos empresa minimos
cur.execute("DELETE FROM datos_empresa")
cur.execute("""
INSERT INTO datos_empresa (clave, valor) VALUES
    ('razon_social', 'Mi Empresa S.A.'),
    ('cuit', '20-12345678-9'),
    ('direccion', 'Av. Principal 123'),
    ('telefono', '(011) 1234-5678'),
    ('email', 'admin@miempresa.com'),
    ('cotizacion_pais', 'Argentina')
""")
print("  + Datos Empresa (6)")

# Unidades de medida (ya estan por script anterior, verificar)
cur.execute("""
INSERT INTO unidades_medida (codigo, nombre, activo) VALUES
    ('UN', 'Unidad', TRUE), ('KG', 'Kilogramo', TRUE), ('LT', 'Litro', TRUE),
    ('MT', 'Metro', TRUE), ('CJ', 'Caja', TRUE), ('PL', 'Pallet', TRUE),
    ('PK', 'Pack', TRUE), ('BL', 'Bolsa', TRUE), ('GL', 'Galon', TRUE), ('DZ', 'Docena', TRUE)
ON CONFLICT (codigo) DO NOTHING
""")
print("  + Unidades Medida (10)")

# Listas de precio venta
cur.execute("""
INSERT INTO listas_precio_venta (codigo, nombre, moneda, activo) VALUES
    ('GENERAL', 'Lista General', 'USD', TRUE),
    ('MAYORISTA', 'Lista Mayorista', 'USD', TRUE),
    ('MINORISTA', 'Lista Minorista', 'USD', TRUE),
    ('DISTRIBUIDOR', 'Lista Distribuidor', 'USD', TRUE),
    ('VIP', 'Lista VIP', 'USD', TRUE)
ON CONFLICT (codigo) DO NOTHING
""")
print("  + Listas Precio Venta (5)")

# Turnos laborales
cur.execute("""
INSERT INTO turnos_laborales (codigo, nombre, hora_entrada, hora_salida, es_nocturno, horas_jornada, activo) VALUES
    ('TM', 'Turno Manana', '06:00', '14:00', FALSE, 8, TRUE),
    ('TT', 'Turno Tarde', '14:00', '22:00', FALSE, 8, TRUE),
    ('TN', 'Turno Noche', '22:00', '06:00', TRUE, 8, TRUE),
    ('TC', 'Turno Comercial', '08:00', '17:00', FALSE, 9, TRUE),
    ('TP', 'Turno Part-Time', '08:00', '12:00', FALSE, 4, TRUE)
ON CONFLICT (codigo) DO NOTHING
""")
print("  + Turnos Laborales (5)")

# Caja POS default
cur.execute("""
INSERT INTO cajas_pos (id, codigo, nombre, activo) VALUES (1, 'CAJA1', 'Caja Principal', TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Caja POS (1)")

# Facturador default
cur.execute("""
INSERT INTO config_facturadores (id, codigo, nombre, sucursal_id, activo) VALUES (1, 'F01', 'Facturador Principal', 1, TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Facturador F01")

# Categoria producto default
cur.execute("""
INSERT INTO categorias_producto (id, nombre, activo) VALUES (1, 'General', TRUE)
ON CONFLICT (id) DO UPDATE SET activo=TRUE
""")
print("  + Categoria Producto (General)")

# Modulos
cur.execute("DELETE FROM modulos")
cur.execute("""
INSERT INTO modulos (id, codigo, nombre, icono, orden, activo) VALUES
    (1, 'rrhh', 'RRHH', 'fa5s.users', 1, TRUE),
    (2, 'configuracion', 'Configuracion', 'fa5s.cog', 2, TRUE),
    (3, 'compras', 'Compras', 'fa5s.shopping-cart', 3, TRUE),
    (4, 'inventario', 'Inventario', 'fa5s.boxes', 4, TRUE)
""")
print("  + Modulos (4)")

# Resetear secuencias
tablas_seq = [
    "usuarios", "roles", "sucursales", "departamentos", "cargos",
    "depositos", "tipos_compra", "tipos_permiso", "conceptos_nomina",
    "cajas_pos", "config_facturadores", "categorias_producto", "modulos",
]
for t in tablas_seq:
    try:
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{t}', 'id'), COALESCE((SELECT MAX(id) FROM {t}), 1))")
    except Exception:
        conn.rollback()
        conn.autocommit = True

print("\n  Secuencias reseteadas")

cur.close()
conn.close()
print("\n" + "=" * 60)
print("LISTO - BD limpia con seeds por defecto")
print("=" * 60)
