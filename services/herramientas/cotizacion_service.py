"""
Servicio de cotizacion de divisas.
Obtiene el valor del dolar desde fuentes oficiales por pais.
Guarda un registro por dia en la BD.
"""
import re
from datetime import date
from core.logging_config import logger

PAISES = {
    "Venezuela": {
        "url": "https://www.bcv.org.ve/",
        "moneda": "Bs.",
        "descripcion": "Dolar BCV",
    },
    "Argentina": {
        "url": "https://www.bna.com.ar/Personas",
        "moneda": "AR$",
        "descripcion": "Dolar BNA",
    },
}


def obtener_cotizacion_hoy(pais: str) -> dict | None:
    """
    Obtiene la cotizacion del dia desde la BD.
    Retorna None si no hay registro para hoy.
    """
    from services.core.empresa_service import empresa_service
    hoy = date.today().isoformat()
    clave = f"cotizacion_{pais.lower()}_{hoy}"
    valor = empresa_service.obtener(clave)
    if valor:
        return {"fecha": hoy, "valor": float(valor), "pais": pais}
    return None


def guardar_cotizacion(pais: str, valor: float):
    """Guarda la cotizacion del dia en la BD."""
    from services.core.empresa_service import empresa_service
    hoy = date.today().isoformat()
    clave = f"cotizacion_{pais.lower()}_{hoy}"
    empresa_service.guardar(clave, f"{valor:.4f}")
    # Guardar tambien como "ultima cotizacion" para referencia rapida
    empresa_service.guardar(f"cotizacion_{pais.lower()}_ultima", f"{valor:.4f}")
    empresa_service.guardar(f"cotizacion_{pais.lower()}_fecha", hoy)


def obtener_cotizacion_web(pais: str) -> float:
    """
    Scrapea la cotizacion desde la fuente oficial.
    Retorna el valor del dolar en moneda local.
    """
    import urllib.request
    import ssl

    if pais not in PAISES:
        raise ValueError(f"Pais no soportado: {pais}. Opciones: {list(PAISES.keys())}")

    url = PAISES[pais]["url"]

    # Contexto SSL permisivo (algunos sitios tienen certificados vencidos)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        raise ConnectionError(f"No se pudo conectar a {url}: {e}")

    if pais == "Venezuela":
        return _parsear_bcv(html)
    elif pais == "Argentina":
        return _parsear_bna(html)

    raise ValueError(f"Parser no implementado para {pais}")


def _parsear_bcv(html: str) -> float:
    """Extrae el dolar del BCV (Banco Central de Venezuela)."""
    # Buscar el valor del dolar - el BCV lo muestra como "USD" seguido del valor
    # Patron: id="dolar" ... <strong>XX,XXXXXXXX</strong>
    patron = r'id="dolar".*?<strong>([\d.,]+)</strong>'
    match = re.search(patron, html, re.DOTALL)
    if match:
        valor_str = match.group(1).strip()
        # Formato venezolano: 36,81520000 (coma decimal)
        valor_str = valor_str.replace(".", "").replace(",", ".")
        return float(valor_str)

    # Patron alternativo: buscar "Dolar" cerca de un numero
    patron2 = r'[Dd][oó]lar.*?([\d]+[,.][\d]+)'
    match2 = re.search(patron2, html, re.DOTALL)
    if match2:
        valor_str = match2.group(1).replace(".", "").replace(",", ".")
        return float(valor_str)

    raise ValueError("No se pudo extraer la cotizacion del BCV. El formato de la pagina pudo haber cambiado.")


def _parsear_bna(html: str) -> float:
    """Extrae el dolar billete del BNA (Banco Nacion Argentina)."""
    # Buscar la tabla de "Billetes" - dolar compra/venta
    # El BNA muestra: Dolar U.S.A | compra | venta
    patron = r'Dolar U\.S\.A.*?<td[^>]*>([\d.,]+)</td>\s*<td[^>]*>([\d.,]+)</td>'
    match = re.search(patron, html, re.DOTALL | re.IGNORECASE)
    if match:
        # Tomar el valor de venta (segundo valor)
        venta_str = match.group(2).strip()
        venta_str = venta_str.replace(".", "").replace(",", ".")
        return float(venta_str)

    # Patron alternativo mas flexible
    patron2 = r'[Dd]olar.*?[Vv]enta.*?([\d]+[,.][\d]+)'
    match2 = re.search(patron2, html, re.DOTALL)
    if match2:
        valor_str = match2.group(1).replace(".", "").replace(",", ".")
        return float(valor_str)

    raise ValueError("No se pudo extraer la cotizacion del BNA. El formato de la pagina pudo haber cambiado.")


def actualizar_cotizacion(pais: str) -> dict:
    """
    Obtiene cotizacion de hoy. Si ya existe en BD, retorna la guardada.
    Si no, la scrapea y la guarda.
    """
    # Verificar si ya tenemos la de hoy
    existente = obtener_cotizacion_hoy(pais)
    if existente:
        return existente

    # Scrapear
    valor = obtener_cotizacion_web(pais)
    guardar_cotizacion(pais, valor)
    logger.info(f"Cotizacion {pais}: {valor}")

    return {
        "fecha": date.today().isoformat(),
        "valor": valor,
        "pais": pais,
    }


def obtener_ultima_cotizacion(pais: str) -> dict | None:
    """Obtiene la ultima cotizacion guardada (cualquier fecha)."""
    from services.core.empresa_service import empresa_service
    valor = empresa_service.obtener(f"cotizacion_{pais.lower()}_ultima")
    fecha = empresa_service.obtener(f"cotizacion_{pais.lower()}_fecha")
    if valor and fecha:
        return {"fecha": fecha, "valor": float(valor), "pais": pais}
    return None
