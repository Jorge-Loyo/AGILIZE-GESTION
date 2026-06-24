"""Expandir tabla clientes + crear direcciones_entrega y contactos."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

# Columnas nuevas en clientes
cols = [
    ("tipo_contribuyente", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("condicion_iva", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("numero_ingresos_brutos", "VARCHAR(30) NOT NULL DEFAULT ''"),
    ("codigo_postal", "VARCHAR(20) NOT NULL DEFAULT ''"),
    ("pais", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("dias_pago", "INTEGER NOT NULL DEFAULT 0"),
    ("lista_precio", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("descuento_default", "FLOAT NOT NULL DEFAULT 0"),
    ("moneda", "VARCHAR(10) NOT NULL DEFAULT ''"),
    ("credito_bloqueado", "BOOLEAN NOT NULL DEFAULT FALSE"),
    ("cobrador_id", "INTEGER REFERENCES usuarios(id)"),
    ("zona", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("ruta", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("banco", "VARCHAR(100) NOT NULL DEFAULT ''"),
    ("tipo_cuenta_banco", "VARCHAR(30) NOT NULL DEFAULT ''"),
    ("numero_cuenta", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("cbu_clabe", "VARCHAR(30) NOT NULL DEFAULT ''"),
]
for col, tipo in cols:
    try:
        cur.execute(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}")
        print(f"  + clientes.{col} OK")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True

# Direcciones de entrega
cur.execute("""
CREATE TABLE IF NOT EXISTS direcciones_entrega_cliente (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(250) NOT NULL,
    ciudad VARCHAR(100) NOT NULL DEFAULT '',
    provincia_estado VARCHAR(100) NOT NULL DEFAULT '',
    codigo_postal VARCHAR(20) NOT NULL DEFAULT '',
    contacto_nombre VARCHAR(150) NOT NULL DEFAULT '',
    contacto_telefono VARCHAR(50) NOT NULL DEFAULT '',
    horario_entrega VARCHAR(100) NOT NULL DEFAULT '',
    principal BOOLEAN NOT NULL DEFAULT FALSE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("direcciones_entrega_cliente OK")

# Contactos
cur.execute("""
CREATE TABLE IF NOT EXISTS contactos_cliente (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id) ON DELETE CASCADE,
    nombre VARCHAR(150) NOT NULL,
    cargo VARCHAR(100) NOT NULL DEFAULT '',
    telefono VARCHAR(50) NOT NULL DEFAULT '',
    celular VARCHAR(50) NOT NULL DEFAULT '',
    email VARCHAR(150) NOT NULL DEFAULT '',
    es_facturacion BOOLEAN NOT NULL DEFAULT FALSE,
    es_compras BOOLEAN NOT NULL DEFAULT FALSE,
    principal BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("contactos_cliente OK")

cur.close()
conn.close()
print("\nLISTO - Clientes expandido")
