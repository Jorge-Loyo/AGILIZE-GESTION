# Plan de Test Manual — RRHH Liquidación Dual (Casa Dulce)

**Fecha:** Julio 2026  
**Rama:** `deploy/casa-dulce`  
**BD:** `casa_dulce_agilize_dev` (localhost)  
**Login:** `master` / `master2025`

---

## Pre-requisitos

```bash
cd /c/Desarrollo/Agilize-Gestion
source venv/Scripts/activate
python main.py
```

---

## TEST 1: Verificar Labels Venezuela

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 1.1 | Ir a **RRHH > Empleados > + Nuevo** | Se abre formulario |  |
| 1.2 | Verificar label del primer campo de documento | Dice **"C.I. *"** (no "DNI") |  |
| 1.3 | Verificar label del segundo campo fiscal | Dice **"RIF *"** (no "CUIL") |  |
| 1.4 | Verificar placeholder del campo C.I. | Dice **"Documento de identidad"** (no "7-9 dígitos") |  |

---

## TEST 2: Crear Empleado Dual

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 2.1 | Completar: Nombre=`María`, Apellido=`González` | — |  |
| 2.2 | C.I.=`V-12345678`, RIF=`J-12345678-0` | — |  |
| 2.3 | Fecha Nac: `01/01/1990` | Edad muestra ~36 años |  |
| 2.4 | Fecha Ingreso: fecha de hoy | — |  |
| 2.5 | Tipo Liquidación: **Sueldo mensual (sin fichado)** | — |  |
| 2.6 | Sueldo Mensual: `1300` | — |  |
| 2.7 | Verificar sección **"Pago Real (USD)"** visible | Grupo con 3 campos + texto info |  |
| 2.8 | Pago Total USD: `240` | — |  |
| 2.9 | Canasta USD: `40` | — |  |
| 2.10 | Bono Empresa USD: `70` | — |  |
| 2.11 | Click **Guardar** | Mensaje éxito, vuelve a lista |  |
| 2.12 | Empleado aparece en la lista | Nombre visible |  |

---

## TEST 3: Editar Empleado — Persistencia de Campos USD

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 3.1 | Seleccionar María González > **Editar** | Se abre form con datos |  |
| 3.2 | Verificar Pago Total USD | Muestra `240.00` |  |
| 3.3 | Verificar Canasta USD | Muestra `40.00` |  |
| 3.4 | Verificar Bono Empresa USD | Muestra `70.00` |  |
| 3.5 | Verificar Sueldo Mensual | Muestra `1300.00` |  |

---

## TEST 4: Verificar Tasa BCV

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 4.1 | Ir a **Finanzas > Historial Dólar** | Se abre la vista |  |
| 4.2 | Verificar que hay al menos 1 tasa | Debería mostrar `667.05` (scrapeado auto) |  |
| 4.3 | Si no hay, cargar manual: Fecha=hoy, Valor=`667.05` | Se guarda OK |  |

---

## TEST 5: Liquidar — Detección Modo Dual

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 5.1 | Ir a **RRHH > Nómina > + Liquidar** | Se abre vista liquidación |  |
| 5.2 | Seleccionar periodo `2026-07` | Lista de empleados carga |  |
| 5.3 | Seleccionar **María González [M]** | — |  |
| 5.4 | Verificar panel **"Liquidación Dual (USD)"** visible | Panel aparece automáticamente |  |
| 5.5 | Combo Tasa muestra fecha + valor (ej: `2026-07-05 — 667.05 Bs`) | Tasa cargada |  |
| 5.6 | Campo Bono precargado con `70.00` | Valor de la ficha |  |
| 5.7 | Campo Faltas en `0` | Default |  |

---

## TEST 6: Preview Dual en Tiempo Real

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 6.1 | Con faltas=0, verificar preview | Legal: ~1.95 \| Compl: ~128.05 \| Bono: 70.00 \| Desc: 0.00 |  |
| 6.2 | Verificar NETO USD | ~$200.00 |  |
| 6.3 | Verificar TOTAL (con canasta) | ~$240.00 |  |
| 6.4 | Cambiar **Faltas a 2** | Desc cambia a ~16.00, Neto baja a ~$184.00 |  |
| 6.5 | Cambiar **Bono a 80** | Complemento baja, Neto sube |  |
| 6.6 | Volver Bono a `70`, Faltas a `1` | Para confirmar |  |

---

## TEST 7: Confirmar Liquidación Dual

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 7.1 | Click **Confirmar Liquidación** | Diálogo "¿Liquidar período 2026-07 (Bs + USD)?" |  |
| 7.2 | Click **Sí** | Mensaje "Liquidación dual registrada (Bs + USD)" |  |
| 7.3 | Vuelve a lista de liquidaciones | Nueva liquidación visible |  |

---

## TEST 8: Recibo Real USD (PDF)

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 8.1 | Seleccionar la liquidación de María en la tabla | Fila seleccionada |  |
| 8.2 | Click botón verde **"Recibo Real (USD)"** | Se abre PDF |  |
| 8.3 | PDF tiene header con tasa BCV y periodo | ✓ |  |
| 8.4 | PDF muestra: Sueldo Legal USD, Complemento, Bono | ✓ |  |
| 8.5 | PDF muestra descuento por faltas (si hay) | ✓ |  |
| 8.6 | PDF muestra TOTAL A COBRAR USD + equivalente Bs | ✓ |  |
| 8.7 | PDF tiene firmas | ✓ |  |

---

## TEST 9: Recibo Legal Bs

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 9.1 | Misma liquidación seleccionada | — |  |
| 9.2 | Click botón gris **"Imprimir Recibo"** | Se abre PDF legal |  |
| 9.3 | PDF muestra sueldo en Bs (1300 - descuento faltas) | ✓ |  |

---

## TEST 10: Empleado NO Dual (Flujo Normal)

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 10.1 | Crear empleado: `Pedro Ramirez`, C.I.=`V-99999999`, RIF=`J-99999999-0` | — |  |
| 10.2 | Sueldo Mensual: `1300`, **Pago Total USD: 0** (dejar vacío) | — |  |
| 10.3 | Guardar | OK |  |
| 10.4 | Ir a Liquidar > seleccionar Pedro | — |  |
| 10.5 | Verificar que **NO aparece** panel "Liquidación Dual (USD)" | Solo flujo normal Bs |  |

---

## TEST 11: Sucursales (Bug Fix)

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 11.1 | Ir a **Administrador > Empresa > Sucursales** | Vista CRUD |  |
| 11.2 | Click **Nuevo** > escribir "Barcelona" | — |  |
| 11.3 | Confirmar | Se crea sin error NOT NULL |  |
| 11.4 | Ir a **Configuración > Datos Empresa** | — |  |
| 11.5 | Verificar que **NO hay sección Sucursales** | Solo Info Legal + País |  |

---

## TEST 12: Configuración País

| # | Acción | Resultado Esperado | ✅/❌ |
|---|--------|-------------------|------|
| 12.1 | Ir a **Configuración > Datos Empresa** | — |  |
| 12.2 | Combo País muestra **Venezuela** | Configurado correctamente |  |

---

## Resumen de Bugs Corregidos

| Bug | Fix |
|-----|-----|
| Labels "DNI" / "CUIL" en Venezuela | Ahora usa `label_doc_identidad()` → "C.I." y `label_id_fiscal()` → "RIF" |
| Placeholder "7-9 dígitos" | Cambiado a "Documento de identidad" |
| Sucursales redundante en Config | Eliminada (solo queda en Administrador) |
| Error NOT NULL al crear sucursal | Campos `direccion` y `telefono` ahora nullable |
| País no configurado en BD dev | Insertado "Venezuela" en datos_empresa |

---

## Notas

- La app se corre con `python main.py` (no necesita exe para desarrollo)
- La BD local es `casa_dulce_agilize_dev` en PostgreSQL 18 (localhost)
- Para volver a producción: cambiar `.env` → `DB_HOST=100.127.184.115`, `DB_NAME=agilize_gestion`
- El warning de `ausencias` al liquidar es normal (tabla no usada en Casa Dulce)
