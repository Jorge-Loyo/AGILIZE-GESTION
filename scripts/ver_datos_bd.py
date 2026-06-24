"""Ver datos actuales en la BD y limpiar dejando solo seeds."""
import psycopg2

conn = psycopg2.connect(
    host='100.105.199.110', port=5432,
    dbname='agilize_gestion', user='postgres', password='agilize2025'
)
conn.autocommit = True
cur = conn.cursor()

# Listar tablas con datos
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
tablas = [r[0] for r in cur.fetchall()]
print(f"{len(tablas)} tablas\n")
print("TABLAS CON DATOS:")
for t in tablas:
    try:
        cur.execute(f"SELECT COUNT(*) FROM \"{t}\"")
        count = cur.fetchone()[0]
        if count > 0:
            print(f"  {t}: {count}")
    except Exception:
        conn.rollback()
        conn.autocommit = True

cur.close()
conn.close()
