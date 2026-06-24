"""Crear tablas de listas de precios y cotizaciones de compra."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS listas_precio_proveedor (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER REFERENCES proveedores(id),
    nombre VARCHAR(200) NOT NULL DEFAULT '',
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    moneda VARCHAR(10) NOT NULL DEFAULT 'USD',
    vigente BOOLEAN NOT NULL DEFAULT TRUE,
    observaciones TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("listas_precio_proveedor OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS lista_precio_detalles (
    id SERIAL PRIMARY KEY,
    lista_id INTEGER REFERENCES listas_precio_proveedor(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id),
    codigo_proveedor VARCHAR(50) NOT NULL DEFAULT '',
    descripcion VARCHAR(250) NOT NULL,
    precio_unitario FLOAT NOT NULL DEFAULT 0,
    descuento FLOAT NOT NULL DEFAULT 0,
    precio_neto FLOAT NOT NULL DEFAULT 0
)
""")
print("lista_precio_detalles OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS cotizaciones_compra (
    id SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    descripcion VARCHAR(250) NOT NULL DEFAULT '',
    requisicion_id INTEGER REFERENCES requisiciones(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'abierta',
    proveedor_adjudicado_id INTEGER REFERENCES proveedores(id),
    observaciones TEXT NOT NULL DEFAULT '',
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("cotizaciones_compra OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS cotizacion_compra_detalles (
    id SERIAL PRIMARY KEY,
    cotizacion_id INTEGER REFERENCES cotizaciones_compra(id) ON DELETE CASCADE,
    proveedor_id INTEGER REFERENCES proveedores(id),
    descripcion VARCHAR(250) NOT NULL,
    cantidad FLOAT NOT NULL DEFAULT 1,
    precio_unitario FLOAT NOT NULL DEFAULT 0,
    plazo_entrega VARCHAR(50) NOT NULL DEFAULT '',
    condicion_pago VARCHAR(100) NOT NULL DEFAULT '',
    seleccionado BOOLEAN NOT NULL DEFAULT FALSE
)
""")
print("cotizacion_compra_detalles OK")

cur.close()
conn.close()
print("LISTO - Todas las tablas creadas")
