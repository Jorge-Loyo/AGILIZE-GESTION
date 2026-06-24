import psycopg2
conn = psycopg2.connect(host='100.105.199.110', port=5432, dbname='agilize_gestion', user='postgres', password='agilize2025')
conn.autocommit = True
cur = conn.cursor()
cols = [
    ("categoria", "VARCHAR(30) NOT NULL DEFAULT 'remunerativo'"),
    ("base_calculo", "VARCHAR(20) NOT NULL DEFAULT 'basico'"),
    ("aplica_a", "VARCHAR(20) NOT NULL DEFAULT 'todos'"),
    ("orden", "INTEGER NOT NULL DEFAULT 0"),
]
for col, tipo in cols:
    try:
        cur.execute(f"ALTER TABLE conceptos_nomina ADD COLUMN {col} {tipo}")
        print(f"+ {col}")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        conn.autocommit = True
        print(f"= {col} ya existe")
cur.close()
conn.close()
print("OK")
