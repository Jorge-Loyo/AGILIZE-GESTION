"""Crear tablas de aprobaciones de compra."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS reglas_aprobacion_compra (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    documento VARCHAR(30) NOT NULL DEFAULT 'orden_compra',
    condicion VARCHAR(20) NOT NULL DEFAULT 'monto_mayor',
    valor_condicion FLOAT NOT NULL DEFAULT 0,
    moneda VARCHAR(10) NOT NULL DEFAULT 'USD',
    aprobador_usuario_id INTEGER REFERENCES usuarios(id),
    aprobador_rol_id INTEGER REFERENCES roles(id),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("reglas_aprobacion_compra OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS aprobaciones_compra (
    id SERIAL PRIMARY KEY,
    regla_id INTEGER REFERENCES reglas_aprobacion_compra(id),
    documento_tipo VARCHAR(30) NOT NULL,
    documento_id INTEGER NOT NULL,
    documento_numero INTEGER NOT NULL DEFAULT 0,
    monto FLOAT NOT NULL DEFAULT 0,
    solicitante_id INTEGER REFERENCES usuarios(id),
    aprobador_id INTEGER REFERENCES usuarios(id),
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_respuesta DATE,
    comentario TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("aprobaciones_compra OK")

cur.close()
conn.close()
print("LISTO")
