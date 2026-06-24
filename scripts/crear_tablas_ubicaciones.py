"""Crear tabla ubicaciones_deposito y agregar columnas a depositos/stock/movimientos."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

# Ubicaciones de deposito
cur.execute("""
CREATE TABLE IF NOT EXISTS ubicaciones_deposito (
    id SERIAL PRIMARY KEY,
    deposito_id INTEGER NOT NULL REFERENCES depositos(id) ON DELETE CASCADE,
    codigo VARCHAR(30) NOT NULL,
    pasillo VARCHAR(10) NOT NULL DEFAULT '',
    estanteria VARCHAR(10) NOT NULL DEFAULT '',
    altura VARCHAR(10) NOT NULL DEFAULT '',
    descripcion VARCHAR(100) NOT NULL DEFAULT '',
    capacidad INTEGER NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("ubicaciones_deposito OK")

# Columnas nuevas en depositos
cols_depositos = [
    ("tipo", "VARCHAR(30) NOT NULL DEFAULT 'general'"),
    ("responsable", "VARCHAR(150) NOT NULL DEFAULT ''"),
]
for col, tipo in cols_depositos:
    try:
        cur.execute(f"ALTER TABLE depositos ADD COLUMN {col} {tipo}")
        print(f"  + depositos.{col} OK")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
        print(f"  = depositos.{col} ya existe")

# Columna ubicacion_id en stock_deposito
try:
    cur.execute("ALTER TABLE stock_deposito ADD COLUMN ubicacion_id INTEGER REFERENCES ubicaciones_deposito(id)")
    print("  + stock_deposito.ubicacion_id OK")
except psycopg2.errors.DuplicateColumn:
    conn.rollback()
    conn.autocommit = True
    print("  = stock_deposito.ubicacion_id ya existe")

# Columnas en movimientos_stock
cols_mov = [
    ("ubicacion_id", "INTEGER REFERENCES ubicaciones_deposito(id)"),
    ("ubicacion_destino_id", "INTEGER REFERENCES ubicaciones_deposito(id)"),
]
for col, tipo in cols_mov:
    try:
        cur.execute(f"ALTER TABLE movimientos_stock ADD COLUMN {col} {tipo}")
        print(f"  + movimientos_stock.{col} OK")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
        print(f"  = movimientos_stock.{col} ya existe")

cur.close()
conn.close()
print("\nLISTO - Multi-deposito con ubicaciones")
