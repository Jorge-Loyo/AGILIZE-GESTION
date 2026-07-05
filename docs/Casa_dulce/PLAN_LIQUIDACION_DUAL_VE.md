# Plan de Desarrollo: Liquidación Dual (Bs/USD) — Casa Dulce

**Fecha:** Julio 2026  
**Cliente:** Casa Dulce (Venezuela)  
**Módulo:** RRHH > Nómina  
**Rama:** `deploy/casa-dulce`

---

## 1. Contexto

- **No hay fichaje** — todos son mensuales, se paga el mes completo
- Solo se descuenta si falta (proporcional al día)
- Pago real en USD, sueldo legal en Bs
- Tasa BCV la elige quien liquida (selecciona fecha del historial)
- 2 recibos: legal (Bs) + real (USD)

---

## 2. Fórmula

```
complemento_usd = (pago_total_usd - canasta_usd - bono_empresa_usd) - (sueldo_legal_bs / tasa_bcv)
descuento_falta = pago_total_usd / 30
```

---

## 3. Análisis de Dependencias Actuales

### Archivos que se MODIFICAN:

| Archivo | Qué se toca | Por qué |
|---|---|---|
| `models/empleado.py` | +4 campos | sueldo_legal_bs, pago_total_usd, canasta_usd, bono_empresa_usd |
| `models/__init__.py` | +1 import | Registrar nuevo modelo LiquidacionDual |
| `modulos/rrhh/views/form_empleado.py` | +1 sección UI | Grupo "Liquidación Dual (VE)" con los 4 campos |
| `modulos/rrhh/views/liquidar_view.py` | Agregar modo dual | Selector tasa, campo faltas, preview USD, botón liquidar dual |
| `modulos/rrhh/views/nomina_view.py` | Columna tipo + botón recibo real | Distinguir liquidaciones legales vs duales |
| `services/rrhh/nomina_service.py` | Mínimo cambio | Llamar al servicio dual después de liquidar legal |
| `services/rrhh/liquidacion_pendiente_service.py` | Ajustar para mensuales sin asistencia | Casa Dulce no ficha, todos son mensuales pendientes siempre |
| `main.py` | +1 import modelo | Fallback create_all |
| `agilize.spec` | +hidden imports | Nuevos servicios/modelos |

### Archivos que se CREAN:

| Archivo | Descripción |
|---|---|
| `models/liquidacion_dual.py` | Modelo LiquidacionDual |
| `services/rrhh/nomina_ve_service.py` | Lógica cálculo dual + liquidar |
| `services/rrhh/recibo_real_ve_service.py` | PDF recibo real en USD |
| `alembic/versions/c3d4e5f6a7b8_add_liquidacion_dual_ve.py` | Migración |

### Archivos que NO se tocan:

| Archivo | Por qué |
|---|---|
| `services/rrhh/recibo_ve_service.py` | Recibo legal ya funciona, no cambia |
| `services/rrhh/calculo_asistencia_service.py` | El cálculo mensual existente sigue sirviendo para la parte legal (Bs) |
| `services/rrhh/config_nomina_service.py` | Multiplicadores no aplican a la dual |
| `modulos/rrhh/views/asistencia_view.py` | No hay fichaje en esta rama |
| `modulos/rrhh/views/fichaje_view.py` | No aplica |

---

## 4. Flujo Detallado

### 4.1 Carga de datos del empleado (`form_empleado.py`)

Agregar sección **"Pago Real (USD)"** después de "Jornada y Remuneración":

```
┌─ Pago Real (USD) ──────────────────────────────────┐
│ Sueldo Legal Bs: [1300.00]  Pago Total USD: [240.00]│
│ Canasta USD:     [40.00]    Bono Empresa:   [70.00] │
└─────────────────────────────────────────────────────┘
```

- Estos campos se guardan en el modelo Empleado
- El `tipo_liquidacion` se fuerza a "mensual" en esta rama
- El `sueldo_mensual` existente se usa para el sueldo legal (= `sueldo_legal_bs`)

**Decisión:** Usar `sueldo_mensual` existente como sueldo legal Bs (ya existe, no duplicar). Solo agregar 3 campos nuevos: `pago_total_usd`, `canasta_usd`, `bono_empresa_usd`.

### 4.2 Liquidación (`liquidar_view.py`)

El flujo actual es:
1. Seleccionar periodo → empleado → ver bruto → conceptos → confirmar

Para Casa Dulce se agrega **modo dual**:
1. Seleccionar periodo → empleado
2. **Selector de tasa BCV** (combo con fechas del historial_dolar, default = última)
3. **Campo faltas** (spinbox, default 0) — reemplaza el sistema de ausencias
4. **Campo bono** (precargado de ficha, editable)
5. **Preview dual** en tiempo real:
   - Sueldo legal Bs → USD
   - Complemento USD
   - Bono USD
   - Descuento faltas
   - Canasta (informativo)
   - Neto USD
6. Confirma → genera liquidación legal (Bs) + dual (USD)

**Detección automática:** Si el empleado tiene `pago_total_usd > 0`, se activa el modo dual. Si no, se usa el flujo actual.

### 4.3 Servicio `nomina_ve_service.py`

```python
class NominaVEService:
    def obtener_tasas_disponibles(periodo: str) -> list[tuple[date, Decimal]]
        # Retorna fechas+valores del historial_dolar del mes del periodo

    def calcular_preview(empleado_id, tasa_bcv, faltas=0, bono_override=None) -> dict
        # Calcula todo sin guardar, para el preview

    def liquidar_dual(empleado_id, periodo, fecha_tasa, faltas=0, bono_override=None) -> LiquidacionDual
        # 1. Liquidar legal (Bs) usando nomina_service existente
        # 2. Calcular componentes USD
        # 3. Guardar LiquidacionDual
        # 4. Retornar

    def listar_duales(periodo=None, empleado_id=None) -> list[LiquidacionDual]
```

### 4.4 Recibo Real (`recibo_real_ve_service.py`)

PDF con:
- Header: empresa + periodo + tasa BCV usada + fecha tasa
- Datos empleado
- Haberes USD: sueldo legal (Bs→USD), complemento, bono
- Descuento faltas (si hay)
- Subtotal nómina
- Canasta (línea separada)
- Total bruto USD
- Deducciones legales (convertidas a USD)
- **Neto USD** + equivalente Bs
- Firma

### 4.5 `liquidacion_pendiente_service.py` — Ajuste

Problema actual: para empleados mensuales, el servicio busca `Ausencia` para contar faltas. En Casa Dulce **no se registran ausencias** — las faltas se ingresan al liquidar.

**Solución:** Para la liquidación dual, las faltas se pasan como parámetro al liquidar. El `calculo_asistencia_service._calcular_mensual()` sigue funcionando (retorna faltas=0 si no hay ausencias registradas), y el descuento real se aplica en el servicio dual sobre el monto USD.

---

## 5. Modelo de Datos

### 5.1 Campos nuevos en `Empleado` (3 campos)

```python
# Ya existe: sueldo_mensual → se usa como sueldo_legal_bs
pago_total_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
canasta_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
bono_empresa_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
```

### 5.2 Modelo `LiquidacionDual`

```python
class LiquidacionDual(Base, TimestampMixin):
    __tablename__ = "liquidaciones_dual"

    id: Mapped[int] = mapped_column(primary_key=True)
    liquidacion_legal_id: Mapped[int | None] = mapped_column(ForeignKey("liquidaciones.id"), nullable=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo: Mapped[str] = mapped_column(String(7))
    fecha: Mapped[date] = mapped_column(Date)

    # Tasa
    tasa_bcv: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    fecha_tasa: Mapped[date] = mapped_column(Date)

    # Snapshot del empleado al liquidar
    sueldo_legal_bs: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    pago_total_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    canasta_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    bono_empresa_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # Calculados
    sueldo_legal_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    complemento_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    faltas: Mapped[int] = mapped_column(Integer, default=0)
    descuento_faltas_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    deducciones_legal_bs: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    deducciones_legal_usd: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))

    # Totales
    neto_nomina_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    neto_total_usd: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    neto_total_bs: Mapped[Decimal] = mapped_column(Numeric(18, 2))
```

---

## 6. Orden de Implementación

### Paso 1: Modelo + Migración
1. Crear `models/liquidacion_dual.py`
2. Agregar 3 campos a `models/empleado.py`
3. Registrar en `models/__init__.py`
4. Crear migración alembic
5. Agregar a `main.py` fallback + `agilize.spec`

### Paso 2: Servicio de cálculo
1. Crear `services/rrhh/nomina_ve_service.py`
   - `obtener_tasas_disponibles()`
   - `calcular_preview()`
   - `liquidar_dual()`

### Paso 3: UI Ficha Empleado
1. Modificar `form_empleado.py` — agregar sección "Pago Real (USD)"
2. Modificar `_cargar_datos()` y `_guardar()` para los nuevos campos

### Paso 4: UI Liquidación
1. Modificar `liquidar_view.py`:
   - Detectar si empleado tiene `pago_total_usd > 0`
   - Mostrar selector tasa + campo faltas + campo bono
   - Preview dual
   - Confirmar genera ambas liquidaciones

### Paso 5: Recibo Real
1. Crear `services/rrhh/recibo_real_ve_service.py`
2. Modificar `nomina_view.py` — botón "Recibo Real" para liquidaciones duales

### Paso 6: Rebuild exe
1. Actualizar `agilize.spec` con nuevos hidden imports
2. Rebuild y testear

---

## 7. Riesgos

| Riesgo | Mitigación |
|---|---|
| No hay tasa del día elegido | Mostrar warning, permitir elegir otra fecha |
| Empleado sin datos USD | No se activa modo dual, usa flujo normal |
| Cambio salario mínimo | Editar `sueldo_mensual` en ficha del empleado |
| Bono diferente un mes | Campo editable al liquidar (override puntual) |

---

## 8. Lo que NO se toca en esta rama

- Fichaje / Turnos (no aplica)
- Importación de fichadas (no aplica)
- Cierres de asistencia (no aplica)
- Horas extra por fichado (no aplica)
- Aprobación de extras (no aplica)
- SAC/Aguinaldo (se mantiene como está)
- Vacaciones (se mantiene)
- Recibo legal VE (ya funciona)
