"""Crear tablas de lotes y numeros de serie."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS lotes_producto (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    numero_lote VARCHAR(50) NOT NULL,
    fecha_fabricacion DATE,
    fecha_vencimiento DATE,
    proveedor_id INTEGER REFERENCES proveedores(id),
    deposito_id INTEGER REFERENCES depositos(id),
    cantidad_inicial INTEGER NOT NULL DEFAULT 0,
    cantidad_actual INTEGER NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    observaciones VARCHAR(250) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("lotes_producto OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS numeros_serie (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    numero_serie VARCHAR(100) NOT NULL UNIQUE,
    lote_id INTEGER REFERENCES lotes_producto(id),
    deposito_id INTEGER REFERENCES depositos(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible',
    cliente_id INTEGER REFERENCES clientes(id),
    fecha_venta DATE,
    factura_referencia VARCHAR(50) NOT NULL DEFAULT '',
    garantia_meses INTEGER NOT NULL DEFAULT 0,
    fecha_fin_garantia DATE,
    observaciones VARCHAR(250) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("numeros_serie OK")

# Columnas en movimientos_stock
cols = [
    ("lote_id", "INTEGER REFERENCES lotes_producto(id)"),
    ("numero_serie_id", "INTEGER REFERENCES numeros_serie(id)"),
]
for col, tipo in cols:
    try:
        cur.execute(f"ALTER TABLE movimientos_stock ADD COLUMN {col} {tipo}")
        print(f"  + movimientos_stock.{col} OK")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
        print(f"  = movimientos_stock.{col} ya existe")

cur.close()
conn.close()
print("\nLISTO - Lotes y Series")
