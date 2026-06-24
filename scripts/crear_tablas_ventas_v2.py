"""Crear tablas del circuito documental de ventas."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

# Columnas nuevas en pedidos_venta
cols_pedido = [
    ("direccion_entrega_id", "INTEGER REFERENCES direcciones_entrega_cliente(id)"),
    ("condicion_pago", "VARCHAR(100) NOT NULL DEFAULT ''"),
    ("fecha_entrega", "DATE"),
]
for col, tipo in cols_pedido:
    try:
        cur.execute(f"ALTER TABLE pedidos_venta ADD COLUMN {col} {tipo}")
        print(f"  + pedidos_venta.{col} OK")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True

# Remitos de salida
cur.execute("""
CREATE TABLE IF NOT EXISTS remitos_salida (
    id SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    pedido_id INTEGER REFERENCES pedidos_venta(id),
    cliente_id INTEGER REFERENCES clientes(id),
    cliente_nombre VARCHAR(200) NOT NULL DEFAULT '',
    direccion_entrega VARCHAR(250) NOT NULL DEFAULT '',
    deposito_id INTEGER REFERENCES depositos(id),
    transportista VARCHAR(150) NOT NULL DEFAULT '',
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    observaciones TEXT NOT NULL DEFAULT '',
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("remitos_salida OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS remito_salida_detalles (
    id SERIAL PRIMARY KEY,
    remito_id INTEGER NOT NULL REFERENCES remitos_salida(id) ON DELETE CASCADE,
    descripcion VARCHAR(250) NOT NULL,
    cantidad FLOAT NOT NULL DEFAULT 1,
    precio_unitario FLOAT NOT NULL DEFAULT 0
)
""")
print("remito_salida_detalles OK")

# Facturas de venta
cur.execute("""
CREATE TABLE IF NOT EXISTS facturas_venta (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    tipo_comprobante VARCHAR(5) NOT NULL DEFAULT 'A',
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    cliente_id INTEGER REFERENCES clientes(id),
    cliente_nombre VARCHAR(200) NOT NULL DEFAULT '',
    cliente_cuit VARCHAR(30) NOT NULL DEFAULT '',
    pedido_id INTEGER REFERENCES pedidos_venta(id),
    remito_id INTEGER REFERENCES remitos_salida(id),
    condicion_pago VARCHAR(100) NOT NULL DEFAULT '',
    subtotal FLOAT NOT NULL DEFAULT 0,
    descuento FLOAT NOT NULL DEFAULT 0,
    subtotal_neto FLOAT NOT NULL DEFAULT 0,
    iva_porcentaje FLOAT NOT NULL DEFAULT 0,
    iva_monto FLOAT NOT NULL DEFAULT 0,
    percepciones FLOAT NOT NULL DEFAULT 0,
    total FLOAT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'emitida',
    cae VARCHAR(20) NOT NULL DEFAULT '',
    cae_vencimiento DATE,
    observaciones TEXT NOT NULL DEFAULT '',
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("facturas_venta OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS factura_venta_detalles (
    id SERIAL PRIMARY KEY,
    factura_id INTEGER NOT NULL REFERENCES facturas_venta(id) ON DELETE CASCADE,
    descripcion VARCHAR(250) NOT NULL,
    cantidad FLOAT NOT NULL DEFAULT 1,
    precio_unitario FLOAT NOT NULL DEFAULT 0,
    descuento FLOAT NOT NULL DEFAULT 0,
    subtotal FLOAT NOT NULL DEFAULT 0
)
""")
print("factura_venta_detalles OK")

# Notas de credito/debito
cur.execute("""
CREATE TABLE IF NOT EXISTS notas_credito_debito (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(50) NOT NULL,
    tipo VARCHAR(10) NOT NULL,
    tipo_comprobante VARCHAR(5) NOT NULL DEFAULT 'A',
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    cliente_id INTEGER REFERENCES clientes(id),
    cliente_nombre VARCHAR(200) NOT NULL DEFAULT '',
    factura_id INTEGER REFERENCES facturas_venta(id),
    motivo VARCHAR(250) NOT NULL DEFAULT '',
    subtotal FLOAT NOT NULL DEFAULT 0,
    iva_monto FLOAT NOT NULL DEFAULT 0,
    total FLOAT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'emitida',
    observaciones TEXT NOT NULL DEFAULT '',
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("notas_credito_debito OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS nota_credito_debito_detalles (
    id SERIAL PRIMARY KEY,
    nota_id INTEGER NOT NULL REFERENCES notas_credito_debito(id) ON DELETE CASCADE,
    descripcion VARCHAR(250) NOT NULL,
    cantidad FLOAT NOT NULL DEFAULT 1,
    precio_unitario FLOAT NOT NULL DEFAULT 0,
    subtotal FLOAT NOT NULL DEFAULT 0
)
""")
print("nota_credito_debito_detalles OK")

cur.close()
conn.close()
print("\nLISTO - Circuito ventas completo")
