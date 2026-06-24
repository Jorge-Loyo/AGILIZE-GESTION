import psycopg2
conn = psycopg2.connect(host='100.105.199.110', port=5432, dbname='agilize_gestion', user='postgres', password='agilize2025')
conn.autocommit = True
cur = conn.cursor()
cols = [
    ("sexo", "VARCHAR(10) NOT NULL DEFAULT ''"),
    ("estado_civil", "VARCHAR(20) NOT NULL DEFAULT ''"),
    ("nacionalidad", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("celular", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("ciudad", "VARCHAR(100) NOT NULL DEFAULT ''"),
    ("codigo_postal", "VARCHAR(20) NOT NULL DEFAULT ''"),
    ("emergencia_nombre", "VARCHAR(150) NOT NULL DEFAULT ''"),
    ("emergencia_telefono", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("emergencia_parentesco", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("grupo_sanguineo", "VARCHAR(10) NOT NULL DEFAULT ''"),
    ("obra_social", "VARCHAR(100) NOT NULL DEFAULT ''"),
    ("nro_afiliado", "VARCHAR(30) NOT NULL DEFAULT ''"),
    ("alergias", "VARCHAR(250) NOT NULL DEFAULT ''"),
    ("tipo_contrato", "VARCHAR(30) NOT NULL DEFAULT 'indefinido'"),
    ("motivo_egreso", "VARCHAR(100) NOT NULL DEFAULT ''"),
    ("banco", "VARCHAR(100) NOT NULL DEFAULT ''"),
    ("tipo_cuenta", "VARCHAR(30) NOT NULL DEFAULT ''"),
    ("numero_cuenta", "VARCHAR(50) NOT NULL DEFAULT ''"),
    ("cbu_clabe", "VARCHAR(30) NOT NULL DEFAULT ''"),
]
for col, tipo in cols:
    try:
        cur.execute(f"ALTER TABLE empleados ADD COLUMN {col} {tipo}")
        print(f"+ {col}")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
cur.execute("""
CREATE TABLE IF NOT EXISTS legajo_eventos (
    id SERIAL PRIMARY KEY,
    empleado_id INTEGER NOT NULL REFERENCES empleados(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    valor_anterior VARCHAR(100) NOT NULL DEFAULT '',
    valor_nuevo VARCHAR(100) NOT NULL DEFAULT '',
    documento_adjunto VARCHAR(250) NOT NULL DEFAULT '',
    usuario_id INTEGER REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
)
""")
print("legajo_eventos OK")
cur.close()
conn.close()
print("LISTO")
