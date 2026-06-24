import pytest
from datetime import date
from decimal import Decimal
from services.core.empresa_service import empresa_service
from services.rrhh.periodo_service import rango_de_periodo, generar_periodos_mes, periodo_actual, obtener_frecuencia
from services.rrhh.vacaciones_service import vacaciones_service, calcular_dias_por_antiguedad
from services.rrhh.calculo_asistencia_service import calculo_asistencia_service
from services.rrhh.liquidacion_pendiente_service import liquidacion_pendiente_service


@pytest.fixture(autouse=True)
def reset():
    yield
    empresa_service.guardar("periodo_pago", "mensual")


# === PERIODO SERVICE ===

def test_rango_mensual():
    empresa_service.guardar("periodo_pago", "mensual")
    d, h = rango_de_periodo("2026-06")
    assert d == date(2026, 6, 1) and h == date(2026, 6, 30)

def test_rango_quincenal_q1():
    empresa_service.guardar("periodo_pago", "quincenal")
    d, h = rango_de_periodo("2026-06-Q1")
    assert d == date(2026, 6, 1) and h == date(2026, 6, 15)

def test_rango_quincenal_q2():
    empresa_service.guardar("periodo_pago", "quincenal")
    d, h = rango_de_periodo("2026-06-Q2")
    assert d == date(2026, 6, 16) and h == date(2026, 6, 30)

def test_rango_semanal():
    empresa_service.guardar("periodo_pago", "semanal")
    d, h = rango_de_periodo("2026-W25")
    assert d.weekday() == 0 and (h - d).days == 6

def test_rango_diario():
    empresa_service.guardar("periodo_pago", "diario")
    d, h = rango_de_periodo("2026-06-15")
    assert d == h == date(2026, 6, 15)

def test_generar_mensual():
    empresa_service.guardar("periodo_pago", "mensual")
    assert generar_periodos_mes(2026, 6) == ["2026-06"]

def test_generar_quincenal():
    empresa_service.guardar("periodo_pago", "quincenal")
    assert generar_periodos_mes(2026, 6) == ["2026-06-Q1", "2026-06-Q2"]

def test_generar_semanal():
    empresa_service.guardar("periodo_pago", "semanal")
    p = generar_periodos_mes(2026, 6)
    assert len(p) >= 4 and all("W" in x for x in p)

def test_generar_diario():
    empresa_service.guardar("periodo_pago", "diario")
    p = generar_periodos_mes(2026, 6)
    assert len(p) == 30

def test_periodo_actual():
    empresa_service.guardar("periodo_pago", "mensual")
    assert len(periodo_actual()) == 7

def test_frecuencia_default():
    assert obtener_frecuencia() in ("mensual", "quincenal", "semanal", "diario")


# === VACACIONES ===

def test_antiguedad_menor_5():
    fecha = date(2024, 1, 1)
    assert calcular_dias_por_antiguedad(fecha) == 14

def test_antiguedad_mayor_5():
    fecha = date(2020, 1, 1)
    assert calcular_dias_por_antiguedad(fecha) == 21

def test_antiguedad_mayor_10():
    fecha = date(2015, 1, 1)
    assert calcular_dias_por_antiguedad(fecha) == 28

def test_antiguedad_mayor_20():
    fecha = date(2000, 1, 1)
    assert calcular_dias_por_antiguedad(fecha) == 35


# === CALCULO ASISTENCIA ===

def test_calculo_empleado_inexistente():
    resultado = calculo_asistencia_service.calcular_bruto_periodo(99999, "2026-06")
    assert resultado["bruto"] == Decimal("0")
    assert resultado["dias_trabajados"] == 0


# === LIQUIDACION PENDIENTE ===

def test_resumen_periodo_estructura():
    r = liquidacion_pendiente_service.resumen_periodo("2026-06")
    assert "pendientes" in r
    assert "liquidados" in r
    assert "total_activos" in r
    assert "completo" in r

def test_info_pendiente_inexistente():
    info = liquidacion_pendiente_service.info_pendiente(99999, "2026-06")
    assert info["puede_liquidar"] == False
