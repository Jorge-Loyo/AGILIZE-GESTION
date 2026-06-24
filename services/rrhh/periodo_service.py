"""Servicio de periodos — genera periodos segun frecuencia configurada."""
from datetime import date, timedelta
from services.core.empresa_service import empresa_service


def obtener_frecuencia() -> str:
    """Retorna la frecuencia de pago configurada: mensual/quincenal/semanal/diario."""
    return empresa_service.obtener("periodo_pago") or "mensual"


def periodo_actual() -> str:
    """Retorna el periodo actual segun la frecuencia configurada."""
    hoy = date.today()
    freq = obtener_frecuencia()
    if freq == "mensual":
        return hoy.strftime("%Y-%m")
    elif freq == "quincenal":
        q = "Q1" if hoy.day <= 15 else "Q2"
        return f"{hoy.strftime('%Y-%m')}-{q}"
    elif freq == "semanal":
        return f"{hoy.year}-W{hoy.isocalendar()[1]:02d}"
    else:  # diario
        return hoy.strftime("%Y-%m-%d")


def rango_de_periodo(periodo: str) -> tuple[date, date]:
    """Dado un periodo string, retorna (desde, hasta) inclusive."""
    freq = obtener_frecuencia()

    if freq == "mensual" or (len(periodo) == 7 and "-Q" not in periodo and "-W" not in periodo):
        # YYYY-MM
        anio, mes = int(periodo[:4]), int(periodo[5:7])
        desde = date(anio, mes, 1)
        if mes == 12:
            hasta = date(anio + 1, 1, 1) - timedelta(days=1)
        else:
            hasta = date(anio, mes + 1, 1) - timedelta(days=1)
        return desde, hasta

    elif "-Q" in periodo:
        # YYYY-MM-Q1 o YYYY-MM-Q2
        base = periodo[:7]
        anio, mes = int(base[:4]), int(base[5:7])
        if periodo.endswith("Q1"):
            desde = date(anio, mes, 1)
            hasta = date(anio, mes, 15)
        else:
            desde = date(anio, mes, 16)
            if mes == 12:
                hasta = date(anio + 1, 1, 1) - timedelta(days=1)
            else:
                hasta = date(anio, mes + 1, 1) - timedelta(days=1)
        return desde, hasta

    elif "-W" in periodo:
        # YYYY-WNN
        anio = int(periodo[:4])
        semana = int(periodo.split("W")[1])
        # Lunes de esa semana
        desde = date.fromisocalendar(anio, semana, 1)
        hasta = desde + timedelta(days=6)
        return desde, hasta

    else:
        # YYYY-MM-DD (diario)
        d = date.fromisoformat(periodo)
        return d, d


def generar_periodos_mes(anio: int, mes: int) -> list[str]:
    """Genera todos los periodos de un mes segun la frecuencia."""
    freq = obtener_frecuencia()

    if freq == "mensual":
        return [f"{anio}-{mes:02d}"]
    elif freq == "quincenal":
        return [f"{anio}-{mes:02d}-Q1", f"{anio}-{mes:02d}-Q2"]
    elif freq == "semanal":
        periodos = []
        d = date(anio, mes, 1)
        if mes == 12:
            fin = date(anio + 1, 1, 1)
        else:
            fin = date(anio, mes + 1, 1)
        semanas_vistas = set()
        while d < fin:
            w = f"{d.year}-W{d.isocalendar()[1]:02d}"
            if w not in semanas_vistas:
                semanas_vistas.add(w)
                periodos.append(w)
            d += timedelta(days=1)
        return periodos
    else:  # diario
        import calendar
        dias = calendar.monthrange(anio, mes)[1]
        return [f"{anio}-{mes:02d}-{d:02d}" for d in range(1, dias + 1)]
