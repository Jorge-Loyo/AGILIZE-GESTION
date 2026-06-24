"""Crear tablas nuevas de inventario: subcategorias, marcas, UOM, conversiones, codigos barra, kits."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

# Subcategorias
cur.execute("""
CREATE TABLE IF NOT EXISTS subcategorias_producto (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias_producto(id),
    nombre VARCHAR(100) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("subcategorias_producto OK")

# Marcas
cur.execute("""
CREATE TABLE IF NOT EXISTS marcas_producto (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("marcas_producto OK")

# Unidades de medida
cur.execute("""
CREATE TABLE IF NOT EXISTS unidades_medida (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("unidades_medida OK")

# Seed UOM basicas
cur.execute("""
INSERT INTO unidades_medida (codigo, nombre) VALUES
    ('UN', 'Unidad'),
    ('KG', 'Kilogramo'),
    ('LT', 'Litro'),
    ('MT', 'Metro'),
    ('CJ', 'Caja'),
    ('PL', 'Pallet'),
    ('PK', 'Pack'),
    ('BL', 'Bolsa'),
    ('GL', 'Galon'),
    ('DZ', 'Docena')
ON CONFLICT (codigo) DO NOTHING
""")
print("seed UOM OK")

# Conversiones UOM
cur.execute("""
CREATE TABLE IF NOT EXISTS conversiones_uom (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id),
    uom_origen_id INTEGER REFERENCES unidades_medida(id),
    uom_destino_id INTEGER REFERENCES unidades_medida(id),
    factor FLOAT NOT NULL DEFAULT 1.0
)
""")
print("conversiones_uom OK")

# Agregar columnas nuevas a productos (si no existen)
columnas_nuevas = [
    ("tipo_articulo", "VARCHAR(20) NOT NULL DEFAULT 'fisico'"),
    ("subcategoria_id", "INTEGER REFERENCES subcategorias_producto(id)"),
    ("marca_id", "INTEGER REFERENCES marcas_producto(id)"),
    ("uom_compra_id", "INTEGER REFERENCES unidades_medida(id)"),
    ("uom_venta_id", "INTEGER REFERENCES unidades_medida(id)"),
]
for col, tipo in columnas_nuevas:
    try:
        cur.execute(f"ALTER TABLE productos ADD COLUMN {col} {tipo}")
        print(f"  + productos.{col} OK")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
        print(f"  = productos.{col} ya existe")

# Codigos de barra
cur.execute("""
CREATE TABLE IF NOT EXISTS codigos_barra_producto (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    codigo VARCHAR(50) NOT NULL,
    tipo VARCHAR(30) NOT NULL DEFAULT 'propio',
    descripcion VARCHAR(100) NOT NULL DEFAULT '',
    principal BOOLEAN NOT NULL DEFAULT FALSE
)
""")
print("codigos_barra_producto OK")

# Kit detalles
cur.execute("""
CREATE TABLE IF NOT EXISTS kit_detalles (
    id SERIAL PRIMARY KEY,
    kit_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    componente_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad FLOAT NOT NULL DEFAULT 1.0
)
""")
print("kit_detalles OK")

cur.close()
conn.close()
print("\nLISTO - Inventario expandido")
