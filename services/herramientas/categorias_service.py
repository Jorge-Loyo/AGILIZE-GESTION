"""Servicio de limpieza de categorías.

Lee el Reporte de Categorías (xlsx), extrae categorías y productos,
y genera un Excel limpio con productos organizados por categoría.
"""
from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass, field

import pandas as pd
from core.logging_config import logger


@dataclass
class ProductoCategoria:
    codigo: str
    descripcion: str
    categoria: str
    existencia: float = 0


@dataclass
class CategoriasMaster:
    categorias: dict[str, list[ProductoCategoria]] = field(default_factory=dict)

    @property
    def lista_categorias(self) -> list[str]:
        return sorted(self.categorias.keys())

    @property
    def total_productos(self) -> int:
        return sum(len(v) for v in self.categorias.values())


class CategoriasService:
    def __init__(self):
        self._master: CategoriasMaster | None = None

    @property
    def master(self) -> CategoriasMaster | None:
        return self._master

    def cargar_reporte(self, ruta: str | Path) -> CategoriasMaster:
        """Parsea el Reporte de Categorías y extrae categoría -> productos."""
        ruta = Path(ruta)
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

        df = pd.read_excel(ruta, engine="openpyxl", header=None)
        master = CategoriasMaster()
        categoria_actual = "SIN CATEGORIA"

        for i in range(len(df)):
            row = df.iloc[i]
            val_a = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""

            # Detectar línea de categoría: "Categorias : NOMBRE"
            if "categorias" in val_a.lower() or "categorías" in val_a.lower():
                # El nombre puede estar en col C (index 2) o D (index 3)
                nombre = None
                for col_idx in [2, 3, 4]:
                    if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                        nombre = str(row.iloc[col_idx]).strip()
                        if nombre and nombre.lower() not in ("descripción", "descripcion", "código", "codigo"):
                            break
                        nombre = None
                if nombre:
                    categoria_actual = nombre.upper().strip()
                else:
                    categoria_actual = "SIN CATEGORIA"
                if categoria_actual not in master.categorias:
                    master.categorias[categoria_actual] = []
                continue

            # Detectar línea de encabezado (Código / Descripción) - skip
            if "código" in val_a.lower() or "codigo" in val_a.lower():
                continue

            # Detectar producto: tiene código en col A o descripción en col C/D
            if not val_a or val_a.lower() in ("none", "nan", "reporte general"):
                continue

            # Buscar descripción en columnas 2 o 3
            descripcion = ""
            for col_idx in [2, 3]:
                if col_idx < len(row) and pd.notna(row.iloc[col_idx]):
                    desc = str(row.iloc[col_idx]).strip()
                    if desc and desc.lower() not in ("none", "nan"):
                        descripcion = desc
                        break

            if not descripcion:
                continue

            # Existencia en última columna con valor numérico
            existencia = 0
            for col_idx in range(len(row) - 1, 14, -1):
                if pd.notna(row.iloc[col_idx]):
                    try:
                        existencia = float(row.iloc[col_idx])
                        break
                    except (ValueError, TypeError):
                        continue

            if categoria_actual not in master.categorias:
                master.categorias[categoria_actual] = []

            master.categorias[categoria_actual].append(ProductoCategoria(
                codigo=val_a,
                descripcion=descripcion,
                categoria=categoria_actual,
                existencia=existencia,
            ))

        # Eliminar categorías vacías
        master.categorias = {k: v for k, v in master.categorias.items() if v}

        self._master = master
        logger.info(
            f"Categorías: {len(master.lista_categorias)} categorías, "
            f"{master.total_productos} productos"
        )
        return master

    def exportar(self, ruta: str | Path) -> Path:
        """Exporta Excel con una hoja resumen y una hoja por categoría."""
        if not self._master:
            raise ValueError("No hay datos cargados.")

        ruta = Path(ruta)
        all_rows = []
        for cat, productos in sorted(self._master.categorias.items()):
            for p in productos:
                all_rows.append({
                    "Categoria": p.categoria,
                    "Codigo": p.codigo,
                    "Descripcion": p.descripcion,
                    "Existencia": p.existencia,
                })

        with pd.ExcelWriter(ruta, engine="openpyxl") as writer:
            # Hoja resumen
            df_all = pd.DataFrame(all_rows)
            df_all.to_excel(writer, index=False, sheet_name="Todos")

            # Hoja de categorías
            cat_rows = [{"Categoria": k, "Productos": len(v)}
                        for k, v in sorted(self._master.categorias.items())]
            pd.DataFrame(cat_rows).to_excel(writer, index=False, sheet_name="Categorias")

            # Una hoja por categoría (nombre truncado a 31 chars)
            for cat, productos in sorted(self._master.categorias.items()):
                sheet_name = cat[:31].replace("/", "-").replace("\\", "-")
                rows = [{"Codigo": p.codigo, "Descripcion": p.descripcion,
                         "Existencia": p.existencia} for p in productos]
                pd.DataFrame(rows).to_excel(writer, index=False, sheet_name=sheet_name)

        logger.info(f"Categorías exportadas a {ruta.name}")
        return ruta


categorias_service = CategoriasService()
