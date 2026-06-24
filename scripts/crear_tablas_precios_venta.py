"""Crear tablas de listas de precios venta, descuentos y tipos de cambio."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS listas_precio_venta (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    moneda VARCHAR(10) NOT NULL DEFAULT 'USD',
    margen_sobre_costo FLOAT NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("listas_precio_venta OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS lista_precio_venta_items (
    id SERIAL PRIMARY KEY,
    lista_id INTEGER NOT NULL REFERENCES listas_precio_venta(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    precio FLOAT NOT NULL DEFAULT 0
)
""")
print("lista_precio_venta_items OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS reglas_descuento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    producto_id INTEGER REFERENCES productos(id),
    categoria_id INTEGER REFERENCES categorias_producto(id),
    cliente_id INTEGER REFERENCES clientes(id),
    categoria_cliente VARCHAR(50) NOT NULL DEFAULT '',
    cantidad_minima FLOAT NOT NULL DEFAULT 0,
    descuento_porcentaje FLOAT NOT NULL DEFAULT 0,
    descuento_monto FLOAT NOT NULL DEFAULT 0,
    fecha_desde DATE,
    fecha_hasta DATE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    prioridad INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("reglas_descuento OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS tipos_cambio (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    moneda_origen VARCHAR(10) NOT NULL,
    moneda_destino VARCHAR(10) NOT NULL,
    tasa_compra FLOAT NOT NULL DEFAULT 0,
    tasa_venta FLOAT NOT NULL DEFAULT 0,
    fuente VARCHAR(50) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("tipos_cambio OK")

# Seed listas basicas
cur.execute("""
INSERT INTO listas_precio_venta (codigo, nombre, moneda) VALUES
    ('GENERAL', 'Lista General', 'USD'),
    ('MAYORISTA', 'Lista Mayorista', 'USD'),
    ('MINORISTA', 'Lista Minorista', 'USD'),
    ('DISTRIBUIDOR', 'Lista Distribuidor', 'USD'),
    ('VIP', 'Lista VIP', 'USD')
ON CONFLICT (codigo) DO NOTHING
""")
print("seed listas OK")

cur.close()
conn.close()
print("\nLISTO")
