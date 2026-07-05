"""Servicio de historial del dolar. Scrapea BCV (Venezuela) o fuente segun pais."""
import re
import ssl
import urllib.request
import threading
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from core.logging_config import logger
from core.database import get_db
from models.historial_dolar import HistorialDolar


# Fuentes por pais
FUENTES = {
    "venezuela": {
        "url": "https://www.bcv.org.ve/",
        "nombre": "BCV",
        "patron": r'dolar.*?<strong[^>]*>([\d.,]+)</strong>',
    },
    "argentina": {
        "url": "https://www.bna.com.ar/Personas",
        "nombre": "BNA",
        "patron": r'Dolar U\.S\.A.*?<td[^>]*>([\d.,]+)</td>',
    },
}


def _scrape_valor(pais: str) -> Decimal | None:
    """Scrapea el valor del dolar desde la fuente del pais."""
    config = FUENTES.get(pais)
    if not config:
        return None

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            config["url"],
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        html = resp.read().decode("utf-8", errors="ignore")

        match = re.search(config["patron"], html, re.DOTALL | re.IGNORECASE)
        if match:
            raw = match.group(1).strip().replace(".", "").replace(",", ".")
            return Decimal(raw)
    except Exception as e:
        logger.warning(f"Error scrapeando dolar ({pais}): {e}")
    return None


class DolarService:
    _timer: threading.Timer | None = None

    def obtener_hoy(self, pais: str) -> HistorialDolar | None:
        with get_db() as db:
            return db.query(HistorialDolar).filter_by(
                fecha=date.today(), pais=pais
            ).order_by(HistorialDolar.hora_consulta.desc()).first()

    def obtener_historial(self, pais: str, dias: int = 90) -> list[HistorialDolar]:
        desde = date.today() - timedelta(days=dias)
        with get_db() as db:
            return db.query(HistorialDolar).filter(
                HistorialDolar.pais == pais,
                HistorialDolar.fecha >= desde,
            ).order_by(HistorialDolar.fecha.desc(), HistorialDolar.hora_consulta.desc()).all()

    def obtener_ultimo(self, pais: str) -> HistorialDolar | None:
        with get_db() as db:
            return db.query(HistorialDolar).filter_by(pais=pais).order_by(
                HistorialDolar.fecha.desc(), HistorialDolar.hora_consulta.desc()
            ).first()

    def scrape_y_guardar(self, pais: str) -> HistorialDolar | None:
        """Scrapea el valor actual y lo guarda como nuevo registro."""
        valor = _scrape_valor(pais)
        if valor is None:
            logger.warning(f"No se pudo obtener valor dolar para {pais}")
            return None

        config = FUENTES.get(pais, {})
        ahora = datetime.now().time().replace(microsecond=0)

        with get_db() as db:
            registro = HistorialDolar(
                fecha=date.today(),
                hora_consulta=ahora,
                valor=valor,
                fuente=config.get("nombre", ""),
                pais=pais,
            )
            db.add(registro)
            db.flush()
            db.refresh(registro)
            logger.info(f"Dolar {pais} guardado: {valor} a las {ahora}")
            return registro

    def iniciar_scheduler(self, pais: str, hora: int = 12):
        """Programa scraping diario. Se ejecuta al iniciar la app."""
        if not self.obtener_hoy(pais):
            threading.Thread(target=self.scrape_y_guardar, args=(pais,), daemon=True).start()

        self._programar_siguiente(pais, hora)

    def _programar_siguiente(self, pais: str, hora: int):
        """Programa el proximo scrape a la hora indicada."""
        ahora = datetime.now()
        objetivo = ahora.replace(hour=hora, minute=0, second=0, microsecond=0)
        if ahora >= objetivo:
            objetivo += timedelta(days=1)

        segundos = (objetivo - ahora).total_seconds()
        self._timer = threading.Timer(segundos, self._ejecutar_y_reprogramar, args=(pais, hora))
        self._timer.daemon = True
        self._timer.start()
        logger.info(f"Dolar scheduler: proximo scrape en {segundos/3600:.1f}h ({objetivo})")

    def _ejecutar_y_reprogramar(self, pais: str, hora: int):
        self.scrape_y_guardar(pais)
        self._programar_siguiente(pais, hora)

    def detener_scheduler(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None


dolar_service = DolarService()
