"""Servicio de limpieza de maestro de productos.

Lee archivos Excel de listas de precios, limpia datos y calcula
precios sin IVA (Venezuela 16%).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from core.logging_config import logger

IVA_VENEZUELA = 0.16
IVA_FACTOR = 1 + IVA_VENEZUELA


def _get_config():
    """Obtiene configuracion de la BD o usa defaults."""
    try:
        from services.core.empresa_service import empresa_service
        datos = empresa_service.obtener_todos()
        iva = float(datos.get("iva_porcentaje", "16.00")) / 100
        col_map = {
            "codigo": int(datos.get("col_codigo", "0")),
            "descripcion": int(datos.get("col_descripcion", "1")),
            "costo": int(datos.get("col_costo", "8")),
            "precio_con_iva": int(datos.get("col_precio_con_iva", "16")),
            "porcentaje_utilidad": int(datos.get("col_porcentaje_utilidad", "20")),
            "stock": int(datos.get("col_stock", "25")),
        }
        moneda = datos.get("moneda_simbolo", "Bs.")
        return iva, col_map, moneda
    except Exception:
        return IVA_VENEZUELA, COL_MAP, "Bs."

# Mapeo de columnas por indice (estructura ListadePrecios.Xls)
COL_MAP = {
    "codigo": 0,
    "descripcion": 1,
    "costo": 8,
    "precio_con_iva": 16,
    "porcentaje_utilidad": 20,
    "stock": 25,
}


@dataclass
class Producto:
    codigo: str
    descripcion: str
    costo: float
    precio_con_iva: float
    porcentaje_utilidad: float
    stock: int
    _iva: float = 0.16

    @property
    def precio_sin_iva(self) -> float:
        return round(self.precio_con_iva / (1 + self._iva), 2)


@dataclass
class ProductoMaster:
    productos: list[Producto] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.productos)

    @property
    def total_stock(self) -> int:
        return sum(p.stock for p in self.productos)

    @property
    def valor_inventario(self) -> float:
        return round(sum(p.costo * p.stock for p in self.productos), 2)

    @property
    def precio_promedio(self) -> float:
        if not self.productos:
            return 0.0
        return round(sum(p.precio_con_iva for p in self.productos) / len(self.productos), 2)


class LimpiadorService:
    def __init__(self):
        self._master: ProductoMaster | None = None

    @property
    def master(self) -> ProductoMaster | None:
        return self._master

    def cargar(self, ruta: str | Path) -> ProductoMaster:
        ruta = Path(ruta)
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

        iva, col_map, moneda = _get_config()
        self._moneda = moneda

        engine = "xlrd" if ruta.suffix.lower() == ".xls" else "openpyxl"
        df = pd.read_excel(ruta, engine=engine, header=None)

        header_row = self._detect_header(df)
        master = ProductoMaster()

        for i in range(header_row + 1, len(df)):
            row = df.iloc[i]
            codigo = row[col_map["codigo"]]
            if pd.isna(codigo):
                continue

            master.productos.append(Producto(
                codigo=str(codigo).strip(),
                descripcion=str(row[col_map["descripcion"]]).strip()
                if pd.notna(row[col_map["descripcion"]]) else "",
                costo=float(row[col_map["costo"]])
                if pd.notna(row[col_map["costo"]]) else 0.0,
                precio_con_iva=float(row[col_map["precio_con_iva"]])
                if pd.notna(row[col_map["precio_con_iva"]]) else 0.0,
                porcentaje_utilidad=float(row[col_map["porcentaje_utilidad"]])
                if pd.notna(row[col_map["porcentaje_utilidad"]]) else 0.0,
                stock=int(float(row[col_map["stock"]]))
                if pd.notna(row[col_map["stock"]]) else 0,
                _iva=iva,
            ))

        self._master = master
        logger.info(f"Limpiador: cargados {len(master)} productos desde {ruta.name}")
        return master

    def exportar(self, ruta: str | Path, cotizacion: float = None) -> Path:
        if not self._master:
            raise ValueError("No hay datos cargados para exportar.")
        ruta = Path(ruta)
        import math
        rows = []
        for p in self._master.productos:
            row = {
                "Codigo": p.codigo,
                "Descripcion": p.descripcion,
                "Costo": p.costo,
                "Precio sin IVA": p.precio_sin_iva,
                "Precio con IVA": p.precio_con_iva,
                "% Utilidad": p.porcentaje_utilidad,
                "Stock": p.stock,
            }
            if cotizacion and cotizacion > 0:
                usd_sin = p.precio_sin_iva / cotizacion
                usd_con = p.precio_con_iva / cotizacion
                usd_sin_rd = math.ceil(usd_sin * 20) / 20
                usd_con_rd = math.ceil(usd_con * 20) / 20
                row["USD sin IVA"] = round(usd_sin, 8)
                row["USD con IVA"] = round(usd_con, 8)
                row["USD sin IVA Redondeado"] = round(usd_sin_rd, 2)
                row["USD con IVA Redondeado"] = round(usd_con_rd, 2)
            rows.append(row)
        df = pd.DataFrame(rows)
        df.to_excel(ruta, index=False, sheet_name="Maestro de Productos")
        logger.info(f"Limpiador: exportados {len(rows)} productos a {ruta.name}")
        return ruta

    def resumen(self) -> dict:
        if not self._master:
            return {}
        return {
            "total_productos": len(self._master),
            "total_stock": self._master.total_stock,
            "valor_inventario": self._master.valor_inventario,
            "precio_promedio": self._master.precio_promedio,
        }

    @staticmethod
    def _detect_header(df: pd.DataFrame) -> int:
        for i in range(min(20, len(df))):
            val = str(df.iloc[i, 0]).strip().lower()
            if "código" in val or "codigo" in val:
                return i
        raise ValueError("No se encontró la fila de encabezado en el archivo Excel.")


limpiador_service = LimpiadorService()
