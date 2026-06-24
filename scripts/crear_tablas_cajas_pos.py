"""Crear tablas de cajas POS y turnos."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS cajas_pos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    sucursal_id INTEGER REFERENCES sucursales(id),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("cajas_pos OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS turnos_caja (
    id SERIAL PRIMARY KEY,
    caja_id INTEGER NOT NULL REFERENCES cajas_pos(id),
    cajero_id INTEGER NOT NULL REFERENCES usuarios(id),
    fecha DATE NOT NULL,
    hora_apertura TIMESTAMP NOT NULL,
    hora_cierre TIMESTAMP,
    fondo_inicial FLOAT NOT NULL DEFAULT 0,
    total_efectivo FLOAT NOT NULL DEFAULT 0,
    total_tarjeta_debito FLOAT NOT NULL DEFAULT 0,
    total_tarjeta_credito FLOAT NOT NULL DEFAULT 0,
    total_transferencia FLOAT NOT NULL DEFAULT 0,
    total_otros FLOAT NOT NULL DEFAULT 0,
    retiros FLOAT NOT NULL DEFAULT 0,
    ingresos FLOAT NOT NULL DEFAULT 0,
    efectivo_esperado FLOAT NOT NULL DEFAULT 0,
    efectivo_contado FLOAT,
    diferencia FLOAT NOT NULL DEFAULT 0,
    estado VARCHAR(20) NOT NULL DEFAULT 'abierto',
    observaciones TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("turnos_caja OK")

cur.execute("""
CREATE TABLE IF NOT EXISTS movimientos_caja_pos (
    id SERIAL PRIMARY KEY,
    turno_id INTEGER NOT NULL REFERENCES turnos_caja(id),
    tipo VARCHAR(20) NOT NULL,
    medio_pago VARCHAR(30) NOT NULL DEFAULT 'efectivo',
    monto FLOAT NOT NULL DEFAULT 0,
    referencia VARCHAR(100) NOT NULL DEFAULT '',
    detalle_medios TEXT NOT NULL DEFAULT '',
    hora TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("movimientos_caja_pos OK")

cur.execute("""
INSERT INTO cajas_pos (codigo, nombre) VALUES ('CAJA1', 'Caja Principal')
ON CONFLICT (codigo) DO NOTHING
""")
print("seed CAJA1 OK")

cur.close()
conn.close()
print("LISTO")
