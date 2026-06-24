"""
Modulo fiscal: Conectores de factura electronica por pais.

Arquitectura desacoplada:
- ConectorFiscalBase: interfaz abstracta que define el contrato
- ConectorFiscalAR: Argentina (AFIP - WSFE)
- ConectorFiscalVE: Venezuela (SENIAT)
- ConectorFiscalGenerico: Sin conexion fiscal (modo offline)

Para agregar un pais nuevo: crear clase que herede de ConectorFiscalBase.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime, timezone
from core.database import get_db
from models.comercial import FacturaVenta
import json


def _hoy() -> date:
    return datetime.now(timezone.utc).date()


class ConectorFiscalBase(ABC):
    """Interfaz abstracta para conectores fiscales."""

    @abstractmethod
    def autorizar_factura(self, factura_id: int) -> dict:
        """Envia factura al fisco y retorna resultado."""
        ...

    @abstractmethod
    def consultar_estado(self, factura_id: int) -> dict:
        """Consulta estado de autorizacion de una factura."""
        ...

    @abstractmethod
    def generar_qr(self, factura_id: int) -> str:
        """Genera datos del codigo QR fiscal."""
        ...

    def _actualizar_fiscal(self, factura_id: int, estado: str, codigo: str = "",
                           vencimiento: date = None, qr: str = "", response: str = ""):
        """Actualiza campos fiscales en la factura."""
        with get_db() as db:
            f = db.get(FacturaVenta, factura_id)
            if not f:
                return
            f.estado_fiscal = estado
            f.codigo_autorizacion = codigo
            f.codigo_autorizacion_vto = vencimiento
            f.codigo_qr = qr
            f.fiscal_response = response
            # Alias legacy AR
            if codigo:
                f.cae = codigo[:20]
                f.cae_vencimiento = vencimiento


class ConectorFiscalAR(ConectorFiscalBase):
    """Conector fiscal Argentina - AFIP WSFE (factura electronica)."""

    def autorizar_factura(self, factura_id: int) -> dict:
        """
        En produccion: conecta a WSFE de AFIP.
        Aqui: simulacion que retorna CAE.
        Para conectar AFIP real, implementar con libreria pyafipws o similar.
        """
        with get_db() as db:
            f = db.get(FacturaVenta, factura_id)
            if not f:
                return {"exito": False, "error": "Factura no encontrada"}
            if f.estado_fiscal == "aprobado":
                return {"exito": True, "mensaje": "Ya autorizada", "cae": f.codigo_autorizacion}

        # --- AQUI VA LA CONEXION REAL A AFIP ---
        # from pyafipws.wsfev1 import WSFEv1
        # ws = WSFEv1()
        # ws.Conectar()
        # ws.CAESolicitar()
        # cae = ws.CAE
        # vto = ws.Vencimiento

        # SIMULACION (reemplazar por conexion real)
        import random
        cae_simulado = f"{random.randint(10**13, 10**14-1)}"
        from datetime import timedelta
        vto = _hoy() + timedelta(days=10)

        qr_data = self.generar_qr(factura_id)

        self._actualizar_fiscal(
            factura_id, "aprobado", cae_simulado, vto, qr_data,
            json.dumps({"cae": cae_simulado, "vto": str(vto), "simulado": True})
        )
        return {"exito": True, "cae": cae_simulado, "vencimiento": str(vto), "qr": qr_data}

    def consultar_estado(self, factura_id: int) -> dict:
        with get_db() as db:
            f = db.get(FacturaVenta, factura_id)
            if not f:
                return {"estado": "no_encontrada"}
            return {
                "estado": f.estado_fiscal,
                "cae": f.codigo_autorizacion,
                "vencimiento": str(f.codigo_autorizacion_vto) if f.codigo_autorizacion_vto else None,
            }

    def generar_qr(self, factura_id: int) -> str:
        """Genera URL del QR segun formato AFIP."""
        with get_db() as db:
            f = db.get(FacturaVenta, factura_id)
            if not f:
                return ""
            # Formato QR AFIP (simplificado)
            datos = {
                "ver": 1, "fecha": str(f.fecha), "cuit": "20000000001",
                "ptoVta": 1, "tipoCmp": 1, "nroCmp": f.numero,
                "importe": f.total, "moneda": "PES", "ctz": 1,
                "tipoDocRec": 80, "nroDocRec": f.cliente_cuit or "0",
                "tipoCodAut": "E", "codAut": f.codigo_autorizacion or "",
            }
            import base64
            qr_payload = base64.b64encode(json.dumps(datos).encode()).decode()
            return f"https://www.afip.gob.ar/fe/qr/?p={qr_payload}"


class ConectorFiscalVE(ConectorFiscalBase):
    """Conector fiscal Venezuela - SENIAT."""

    def autorizar_factura(self, factura_id: int) -> dict:
        """
        En produccion: conecta a SENIAT.
        Aqui: simulacion. Venezuela usa numero de control + serie de maquina fiscal.
        """
        with get_db() as db:
            f = db.get(FacturaVenta, factura_id)
            if not f:
                return {"exito": False, "error": "Factura no encontrada"}
            if f.estado_fiscal == "aprobado":
                return {"exito": True, "mensaje": "Ya autorizada"}

        # SIMULACION
        import random
        nro_control = f"00-{random.randint(100000, 999999)}"

        self._actualizar_fiscal(
            factura_id, "aprobado", nro_control, None, "",
            json.dumps({"nro_control": nro_control, "simulado": True})
        )
        return {"exito": True, "nro_control": nro_control}

    def consultar_estado(self, factura_id: int) -> dict:
        with get_db() as db:
            f = db.get(FacturaVenta, factura_id)
            if not f:
                return {"estado": "no_encontrada"}
            return {"estado": f.estado_fiscal, "nro_control": f.codigo_autorizacion}

    def generar_qr(self, factura_id: int) -> str:
        return ""  # Venezuela no usa QR fiscal obligatorio


class ConectorFiscalGenerico(ConectorFiscalBase):
    """Modo sin conexion fiscal (para paises sin requerimiento o modo offline)."""

    def autorizar_factura(self, factura_id: int) -> dict:
        self._actualizar_fiscal(factura_id, "no_aplica")
        return {"exito": True, "mensaje": "Sin fiscalizacion requerida"}

    def consultar_estado(self, factura_id: int) -> dict:
        return {"estado": "no_aplica"}

    def generar_qr(self, factura_id: int) -> str:
        return ""
