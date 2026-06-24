"""Crear tablas de toma de inventario fisico."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tomas_inventario (
    id SERIAL PRIMARY KEY,
    numero INTEGER NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    deposito_id INTEGER NOT NULL REFERENCES depositos(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'abierta',
    observaciones TEXT NOT NULL DEFAULT '',
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("tomas_inventario OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS toma_inventario_detalles (
    id SERIAL PRIMARY KEY,
    toma_id INTEGER NOT NULL REFERENCES tomas_inventario(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    stock_teorico INTEGER NOT NULL DEFAULT 0,
    conteo_fisico INTEGER,
    diferencia INTEGER NOT NULL DEFAULT 0,
    ajustado BOOLEAN NOT NULL DEFAULT FALSE
)
""")
print("toma_inventario_detalles OK")

cur.close()
conn.close()
print("LISTO")
