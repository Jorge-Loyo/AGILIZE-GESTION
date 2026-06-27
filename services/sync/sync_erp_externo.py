"""
Servicio de sincronizacion con ERP externo via API REST.
Consume endpoints de eComunik2Server (DBISAM) y sincroniza con PostgreSQL.

Endpoints consumidos:
- GET /articulo    -> productos + precios + existencia
- GET /deposito    -> depositos
- GET /cliente     -> clientes

Uso manual:
    python -m services.sync.sync_erp_externo

Cron (cada 10 min):
    */10 * * * * cd /opt/agilize && venv/bin/python -m services.sync.sync_erp_externo >> logs/sync_erp.log 2>&1

Variables de entorno:
    ERP_API_URL=http://192.168.1.100:9000
    ERP_DEPOSITO=1
"""
import os
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Configuracion
ERP_API_URL = os.environ.get("ERP_API_URL", "http://192.168.1.100:9000")
ERP_DEPOSITO = int(os.environ.get("ERP_DEPOSITO", "1"))

# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SYNC] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/sync_erp.log", encoding="utf-8")],
)
logger = logging.getLogger(__name__)


def _get(endpoint: str, params: dict = None) -> dict | list | None:
    """GET request a la API del ERP externo."""
    url = f"{ERP_API_URL}{endpoint}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url += f"?{query}"
    try:
        req = Request(url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        logger.error(f"HTTP {e.code} en {endpoint}: {e.reason}")
        return None
    except URLError as e:
        logger.error(f"Error conexion a {url}: {e.reason}")
        return None
    except Exception as e:
        logger.error(f"Error en GET {endpoint}: {e}")
        return None


def _get_db():
    """Obtiene conexion a PostgreSQL."""
    import psycopg2
    env_path = Path(__file__).parent.parent.parent / ".env"
    cfg = {"host": "localhost", "port": 5432, "dbname": "agilize_gestion", "user": "postgres", "password": "agilize2025"}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    k, v = k.strip(), v.strip().strip("\"'")
                    if k == "DB_HOST": cfg["host"] = v
                    elif k == "DB_PORT": cfg["port"] = int(v)
                    elif k == "DB_NAME": cfg["dbname"] = v
                    elif k == "DB_USER": cfg["user"] = v
                    elif k == "DB_PASS": cfg["password"] = v
    return psycopg2.connect(**cfg)


def sync_depositos(conn) -> int:
    """Sincroniza depositos desde API."""
    data = _get("/deposito")
    if not data:
        return 0
    cur = conn.cursor()
    count = 0
    for dep in data:
        codigo = dep.get("codigo")
        nombre = dep.get("descripcion", f"Deposito {codigo}")
        activo = dep.get("activo", True)
        cur.execute("""
            INSERT INTO depositos (id, nombre, tipo, activo)
            VALUES (%s, %s, 'general', %s)
            ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre, activo = EXCLUDED.activo
        """, (int(codigo), nombre[:100], activo))
        count += 1
    cur.close()
    return count


def sync_productos(conn) -> dict:
    """Sincroniza productos con precios y existencia desde API."""
    # Obtener todos los articulos con paginacion
    page = 1
    limit = 500
    total_productos = 0
    total_precios = 0
    total_stock = 0

    cur = conn.cursor()

    while True:
        data = _get("/articulo", {"page": str(page), "limit": str(limit), "deposito": str(ERP_DEPOSITO)})
        if not data:
            break

        # Manejar respuesta paginada o array directo
        if isinstance(data, dict) and "data" in data:
            articulos = data["data"]
            total_pages = data.get("total_pages", 1)
        elif isinstance(data, list):
            articulos = data
            total_pages = 1
        else:
            break

        if not articulos:
            break

        for art in articulos:
            codigo = str(art.get("codigo", "")).strip()
            if not codigo:
                continue

            nombre = art.get("descripcion", "")[:200]
            unidad = art.get("unidad", "UN")[:20]
            categoria_nombre = art.get("categoriaNombre", "")
            marca = art.get("marca", "")
            activo = art.get("activo", True)
            costo = float(art.get("costo", 0) or 0)
            precio1 = float(art.get("precio1", 0) or 0)
            existencia = float(art.get("existencia", 0) or 0)
            deposito_id = int(art.get("deposito", ERP_DEPOSITO) or ERP_DEPOSITO)

            # Buscar/crear categoria
            cat_id = None
            if categoria_nombre:
                cur.execute("SELECT id FROM categorias_producto WHERE nombre = %s", (categoria_nombre[:100],))
                row = cur.fetchone()
                if row:
                    cat_id = row[0]
                else:
                    cur.execute("INSERT INTO categorias_producto (nombre, activo) VALUES (%s, TRUE) RETURNING id", (categoria_nombre[:100],))
                    cat_id = cur.fetchone()[0]

            # Upsert producto
            cur.execute("""
                INSERT INTO productos (codigo, nombre, unidad_medida, categoria_id, precio_costo, precio_venta, activo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (codigo) DO UPDATE SET
                    nombre = EXCLUDED.nombre,
                    unidad_medida = EXCLUDED.unidad_medida,
                    categoria_id = EXCLUDED.categoria_id,
                    precio_costo = EXCLUDED.precio_costo,
                    precio_venta = EXCLUDED.precio_venta,
                    activo = EXCLUDED.activo
            """, (codigo, nombre, unidad, cat_id, costo, precio1, activo))
            total_productos += 1

            # Actualizar stock
            cur.execute("SELECT id FROM productos WHERE codigo = %s", (codigo,))
            prod_row = cur.fetchone()
            if prod_row:
                producto_id = prod_row[0]
                cur.execute("""
                    INSERT INTO stock_deposito (producto_id, deposito_id, cantidad)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (producto_id, deposito_id) DO UPDATE SET cantidad = EXCLUDED.cantidad
                """, (producto_id, deposito_id, int(existencia)))
                total_stock += 1

            # Guardar precios multiples en lista_precio_venta_items
            precios_map = {
                "GENERAL": float(art.get("precio1", 0) or 0),
                "MAYORISTA": float(art.get("precio2", 0) or 0),
                "MINORISTA": float(art.get("precio3", 0) or 0),
                "DISTRIBUIDOR": float(art.get("precio4", 0) or 0),
                "VIP": float(art.get("precio5", 0) or 0),
            }
            if prod_row:
                for lista_codigo, precio in precios_map.items():
                    if precio > 0:
                        cur.execute("SELECT id FROM listas_precio_venta WHERE codigo = %s", (lista_codigo,))
                        lista_row = cur.fetchone()
                        if lista_row:
                            cur.execute("""
                                INSERT INTO lista_precio_venta_items (lista_id, producto_id, precio)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (lista_id, producto_id) DO UPDATE SET precio = EXCLUDED.precio
                            """, (lista_row[0], producto_id, precio))
                            total_precios += 1

        if page >= total_pages:
            break
        page += 1

    cur.close()
    return {"productos": total_productos, "precios": total_precios, "stock": total_stock}


def sync_clientes(conn) -> int:
    """Sincroniza clientes desde API."""
    page = 1
    limit = 500
    total = 0
    cur = conn.cursor()

    while True:
        data = _get("/cliente", {"page": str(page), "limit": str(limit)})
        if not data:
            break

        if isinstance(data, dict) and "data" in data:
            clientes = data["data"]
            total_pages = data.get("total_pages", 1)
        elif isinstance(data, list):
            clientes = data
            total_pages = 1
        else:
            break

        if not clientes:
            break

        for cli in clientes:
            rif = str(cli.get("rif", "")).strip()
            nombre = str(cli.get("nombre", "")).strip()[:200]
            if not nombre:
                continue

            direccion = str(cli.get("direccion", ""))[:250]
            telefono = str(cli.get("telefono", ""))[:50]
            email = str(cli.get("email", ""))[:150]
            activo = cli.get("activo", True)

            cur.execute("""
                INSERT INTO clientes (razon_social, cuit_rif, direccion, telefono, email, activo)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT ON CONSTRAINT clientes_pkey DO NOTHING
            """, (nombre, rif, direccion, telefono, email, activo))

            # Si no se inserto por PK, intentar por RIF
            if cur.rowcount == 0 and rif:
                cur.execute("""
                    UPDATE clientes SET
                        razon_social = %s, direccion = %s, telefono = %s, email = %s, activo = %s
                    WHERE cuit_rif = %s
                """, (nombre, direccion, telefono, email, activo, rif))

            total += 1

        if page >= total_pages:
            break
        page += 1

    cur.close()
    return total


def verificar_api() -> bool:
    """Verifica que la API este accesible."""
    data = _get("/")
    if data and data.get("status") == "online":
        logger.info(f"API conectada: v{data.get('version', '?')} - DB: {data.get('database', '?')}")
        return True
    logger.error(f"API no disponible en {ERP_API_URL}")
    return False


def ejecutar_sync():
    """Ejecuta sincronizacion completa."""
    logger.info(f"=== Sync iniciada | API: {ERP_API_URL} | Deposito: {ERP_DEPOSITO} ===")

    if not verificar_api():
        return

    conn = _get_db()
    conn.autocommit = True

    try:
        n_dep = sync_depositos(conn)
        logger.info(f"  Depositos: {n_dep}")

        result_prod = sync_productos(conn)
        logger.info(f"  Productos: {result_prod['productos']} | Precios: {result_prod['precios']} | Stock: {result_prod['stock']}")

        n_cli = sync_clientes(conn)
        logger.info(f"  Clientes: {n_cli}")

        logger.info("=== Sync completada ===")
    except Exception as e:
        logger.error(f"Error en sync: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    ejecutar_sync()
