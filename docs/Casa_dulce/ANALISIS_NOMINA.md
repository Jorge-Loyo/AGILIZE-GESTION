# Análisis de Nómina - Casa Dulce Oriente

## Empresa
**COMERCIALIZADORA CASA DULCE ORIENTE, C.A.**  
Moneda: Bolívares (Bs.)  
Tasa BCV referencia (31/03/2026): 487.1192 Bs/USD

---

## Estructura de Personal

### Empleados (Nómina CDO) - 5 personas
| COD | Nombre | Cédula | Cargo | Departamento | Ingreso |
|-----|--------|--------|-------|--------------|---------|
| 1 | Dairilys Guaregua | 16067033 | Encargada de Tienda | Administración | 16/03/2023 |
| 2 | Emilio Pinto | 8326409 | Logística | Operaciones | 16/03/2023 |
| 3 | Jesús Aray | 8234036 | Logística | Operaciones | 19/10/2023 |
| 4 | Theisy Nadales | 19316663 | Asesora de Ventas | Atención al Cliente | 01/07/2025 |
| 5 | María Guaita | 31311552 | Cajera | Atención al Cliente | 01/07/2025 |

### Directivos - 2 personas
| COD | Nombre | Cédula | Cargo | Departamento | Ingreso |
|-----|--------|--------|-------|--------------|---------|
| D-1 | Elias Nayati | 15514275 | Presidente | Presidencia | 20/10/2023 |
| D-2 | Karelis Espluguez | 16489561 | Vicepresidente | Presidencia | 20/10/2023 |

---

## Estructura Salarial

### Empleados (tipo mensual, 30 días)
| Concepto | Bs. | USD (ref) | Observación |
|----------|-----|-----------|-------------|
| Salario diario | 43.33 | ~0.09 | Salario mínimo legal |
| Salario mensual | 1,300 | ~2.67 | Diario × 30 |
| Salario complementario | 63,325.50 | ~130.00 | Pago en Bs indexado a USD |
| Bono de guerra complementario | 8,442.38 | ~17.33 | Bono gubernamental |
| **Total devengado** | **73,067.88** | **~150.00** | Suma de todo |

### Directivos (tipo mensual, 30 días)
| Concepto | Bs. | USD (ref) | Observación |
|----------|-----|-----------|-------------|
| Salario diario | 4,871.19 | ~10.00 | Mayor que empleados |
| Salario mensual | 146,135.76 | ~300.00 | Diario × 30 |
| Bono complementario | 0 | 0 | No aplica |
| **Total devengado** | **146,135.76** | **~300.00** | Solo salario |

---

## Fórmulas de Cálculo

### Asignaciones (Devengado)
```
Total Devengado = Salario Mensual + Salario Complementario + Bono Guerra 
                  + Reembolsos + Tiempo de Viaje + Horas Extras
```

### Deducciones
| Concepto | Base de cálculo | Porcentaje | Aplica a |
|----------|----------------|------------|----------|
| S.S.O. (Seguro Social) | Salario mensual legal | 1.8462% | Empleados |
| Paro Forzoso | Salario mensual legal | 0.4615% | Empleados |
| Ahorro Habitacional (FAOV) | Total devengado | 1.0000% | Empleados |
| I.S.L.R. (empleados) | Total devengado | 1.3300% | Empleados |
| I.S.L.R. (directivos) | Total devengado | 2.6300% | Directivos |

**Nota**: SSO y Paro Forzoso se calculan sobre el salario legal (1,300 Bs), NO sobre el total devengado. FAOV e ISLR sí se calculan sobre el total devengado.

### Fórmula Final
```
Total Pagado = Total Devengado - Total Deducciones
```

---

## Horas Extras y Sobretiempo

Tipos registrados (todos en 0 para abril 2026):
- **Feriado**: Horas trabajadas en feriado
- **Horas extras diurnas**: Sobretiempo diurno
- **Sábado**: Horas en sábado
- **S.D. (Sobretiempo Diurno)**: Referencia ley 24/06/2015
- **S.N. (Sobretiempo Nocturno)**: Horas nocturnas
- **Recargo Domingo**: Recargo por trabajo dominical

---

## Asistencia

- Período: semanal (lunes a sábado visible)
- Marcaje: X = asistió (entrada + salida en columnas separadas)
- Campos resumen: Total días pagados, Tiempo de viaje, Descuento horas
- Todos los empleados: 30 días trabajados, 0 descuentos en abril

---

## Recibo de Pago (Comprobante)

Estructura del recibo:
```
COMERCIALIZADORA CASA DULCE ORIENTE, C.A.
COMPROBANTE DE PAGO                          Nº [COD]
DESDE EL [fecha_inicio] AL [fecha_fin]

Nombre | CI | Fecha Ingreso | Cargo | Departamento

--- DEVENGADO ---
Días: 30    Salario diario: X    Salario mensual: X
H. Extras Diurnas:    Nº Horas: X    Bs. X
H. Extras Nocturnas:  Nº Horas: X    Bs. X
Sábado:               Nº Horas: X    Bs. X
Recargo Domingo:                     Bs. X
Feriado:              Nº Horas: X    Bs. X
Reembolso:                           Bs. X
Tiempo de Viaje:      X Horas        Bs. X
Bono Complementario:                 Bs. X
                    TOTAL DEVENGADO   Bs. X

--- DEDUCCIONES ---
S.S.O.:              Bs. X
I.S.L.R:             Bs. X
Ahorro Habitacional: Bs. X
Paro Forzoso:        Bs. X
Desc. Préstamos:     Bs. X
Otras:               Bs. X
TOTAL DEDUCCIONES:   Bs. X    TOTAL RECIBIDO Bs. X

                                    FIRMA
```

---

## Particularidades Venezuela (LOTTT)

1. **Doble estructura salarial**: Salario legal mínimo + complemento indexado a USD
2. **Bono de guerra**: Asignación gubernamental adicional (solo empleados, no directivos)
3. **SSO y Paro**: Se calculan SOLO sobre salario legal (no sobre complemento)
4. **FAOV e ISLR**: Se calculan sobre total devengado (incluye complemento)
5. **ISLR diferenciado**: Empleados 1.33%, Directivos 2.63%
6. **Tasa BCV**: Se registra la tasa del mes para referencia
7. **Directivos no aportan SSO/Paro/FAOV**: Solo pagan ISLR

---

## Mapeo a Agilize Gestión

### Lo que ya existe en el sistema:
- ✅ Empleados con datos personales, cargo, departamento, fecha ingreso
- ✅ Liquidación mensual (30 días)
- ✅ Conceptos de nómina configurables (porcentaje, monto fijo)
- ✅ Horas extras tipificadas
- ✅ Recibo PDF
- ✅ Moneda Bs (país Venezuela configurado)

### Lo que necesita adaptación/implementación:
| Requerimiento | Estado | Acción |
|---------------|--------|--------|
| Salario complementario (indexado USD) | 🔶 Parcial | Concepto con monto variable por tasa BCV |
| Bono de guerra | 🔶 Parcial | Concepto configurable, solo empleados |
| Tasa BCV del período | ❌ Nuevo | Campo en liquidación o config mensual |
| SSO sobre salario legal (no total) | ❌ Nuevo | Base de cálculo diferenciada |
| Paro Forzoso sobre salario legal | ❌ Nuevo | Base de cálculo diferenciada |
| FAOV sobre total devengado | ✅ Existe | Concepto % sobre total |
| ISLR diferenciado por tipo | 🔶 Parcial | % variable según categoría empleado/directivo |
| Categoría Empleado vs Directivo | ❌ Nuevo | Clasificación que afecta deducciones |
| Reembolsos | ✅ Existe | Concepto monto fijo |
| Tiempo de viaje (horas → pago) | ❌ Nuevo | Cálculo por horas con tarifa |
| Recibo formato Venezuela | 🔶 Parcial | Adaptar PDF al formato del Excel |
| Nómina separada empleados/directivos | 🔶 Parcial | Filtro o agrupación en vista |

---

## Plan de Implementación Propuesto

### Fase 1: Configuración base
1. Agregar campo `categoria_nomina` al empleado (EMPLEADO / DIRECTIVO)
2. Agregar campo `tasa_cambio` al período de liquidación
3. Configurar conceptos de asignación: Salario complementario, Bono de guerra

### Fase 2: Motor de cálculo Venezuela
4. Implementar lógica de base de cálculo diferenciada para deducciones:
   - SSO/Paro → sobre `salario_mensual_legal`
   - FAOV/ISLR → sobre `total_devengado`
5. ISLR con porcentaje variable según categoría

### Fase 3: Recibo PDF
6. Adaptar template de recibo al formato venezolano (comprobante de pago)

### Fase 4: Importación
7. Importar empleados desde este Excel (datos ya mapeados)
