# Plan de Desarrollo — Módulo RRHH

## Agilize Gestión - Fase 2

**Fecha:** Junio 2026  
**Estado:** ✅ Completado — Fase 2 finalizada + Features adicionales  
**Responsable:** Agilize Soluciones

---

## Resumen

Este documento detalla las mejoras y nuevas funcionalidades planificadas para el módulo de RRHH, organizadas por bloques de ejecución según prioridad e impacto.

---

## Bloque 1: Rápido, Alto Impacto

### 1.1 Feriados — ABM desde UI

**Estado:** ✅ Completado  
**Esfuerzo:** Bajo  
**Ubicación:** RRHH > Configuración > Nueva pestaña "Feriados"

**Descripción:**
- Agregar, editar y eliminar feriados desde la interfaz
- Cargar feriados por año
- Importar feriados nacionales de Argentina automáticamente
- Los feriados impactan en el cálculo de horas (multiplicador feriado)

**Campos:**
- Fecha
- Descripción
- Tipo (nacional, provincial, puente)

---

### 1.2 Notificaciones en Dashboard

**Estado:** ✅ Completado  
**Esfuerzo:** Bajo  
**Ubicación:** RRHH > Dashboard

**Descripción:**
Agregar alertas visuales que informen al usuario de acciones pendientes:

- "X registros de asistencia incompletos" (con link a filtrar incompletos)
- "X empleados sin valor hora configurado"
- "Quincena pendiente de cierre (última cerrada: DD/MM)"
- "X empleados pendientes de liquidar en período actual"
- "X adelantos con saldo pendiente"

**Formato:** Cards de alerta con color (rojo=urgente, amarillo=atención, verde=ok)

---

### 1.3 Editar Empleados Masivamente

**Estado:** ✅ Completado  
**Esfuerzo:** Medio  
**Ubicación:** RRHH > Empleados > Importar

**Descripción:**
Actualmente la importación solo crea empleados nuevos (omite si el legajo/DNI ya existe). La mejora permite:

- Si el legajo ya existe → **actualizar** los datos del empleado con los valores del Excel
- Checkbox en la UI: "Actualizar existentes" (por defecto desactivado)
- Campos actualizables: nombre, apellido, email, teléfono, departamento, cargo, sucursal, valor hora, sueldo mensual
- NO actualiza: legajo, DNI (son identificadores)
- Reporte: "Creados: X, Actualizados: X, Sin cambios: X"

---

## Bloque 2: Medio, Necesario

### 2.1 Importar Fichadas XLSX con Mapeo Visual

**Estado:** ✅ Completado  
**Esfuerzo:** Medio  
**Ubicación:** RRHH > Asistencia > Importar Fichadas

**Descripción:**
Cuando se importa un XLSX manual y hay empleados no encontrados o duplicados:

1. Se muestra un **modal de mapeo** con:
   - Lista de hojas/nombres no vinculados
   - Desplegable para seleccionar el empleado (por legajo) para cada uno
   - Opción "Ignorar"
2. El usuario completa el mapeo manualmente
3. Se importan las fichadas con la vinculación correcta
4. Se guarda el mapeo para futuras importaciones del mismo formato

**Ejemplo:**
```
Hoja "EZEQUIEL" → [Desplegable: 18 - EZEQUIEL / 28 - EZEQUIEL] 
Hoja "ALAN "    → [Desplegable: 100 - ALAM]
```

---

### 2.2 Histórico de Cambios de Sueldo

**Estado:** ✅ Completado  
**Esfuerzo:** Bajo  
**Ubicación:** RRHH > Empleados > Detalle del empleado

**Descripción:**
Cada vez que se modifica el valor_hora, valor_hora_extra o sueldo_mensual de un empleado, se guarda un registro histórico.

**Modelo:**
```
historico_sueldo:
  - id
  - empleado_id
  - fecha_cambio
  - campo (valor_hora / valor_hora_extra / sueldo_mensual)
  - valor_anterior
  - valor_nuevo
  - usuario_id (quién hizo el cambio)
```

**UI:**
- En el detalle del empleado (modal), nueva sección "Histórico de Sueldo"
- Tabla con fecha, campo, valor anterior, valor nuevo

---

### 2.3 Resumen Quincenal

**Estado:** ✅ Completado  
**Esfuerzo:** Medio  
**Ubicación:** RRHH > Nómina > Resumen Mensual (mejorado)

**Descripción:**
Expandir el resumen mensual para mostrar el detalle por quincena:

- Selector de quincena (Q1 / Q2 / Mes completo)
- Totales por quincena: días, horas normales, extras, bruto
- Comparación Q1 vs Q2
- Estado del cierre de cada quincena
- Empleados que trabajaron en una quincena pero no en la otra

---

## Bloque 3: Más Complejo

### 3.1 Vacaciones

**Estado:** ✅ Completado  
**Esfuerzo:** Alto  
**Ubicación:** RRHH > Asistencia > Nueva pestaña "Vacaciones" + RRHH > Configuración

**Descripción:**
Sistema completo de gestión de vacaciones según legislación argentina.

**Reglas (Ley 20.744 Argentina):**
- Hasta 5 años de antigüedad: 14 días corridos
- De 5 a 10 años: 21 días corridos
- De 10 a 20 años: 28 días corridos
- Más de 20 años: 35 días corridos

**Modelo:**
```
vacaciones:
  - id
  - empleado_id
  - periodo_anual (2026)
  - dias_correspondientes (calculado por antigüedad)
  - dias_tomados
  - dias_disponibles
  - fecha_desde
  - fecha_hasta
  - estado (pendiente / aprobada / tomada / cancelada)
  - aprobado_por
```

**Funcionalidades:**
- Cálculo automático de días según antigüedad
- Solicitud de vacaciones (empleado o admin)
- Aprobación
- Descuento de días al tomar
- Saldo visible en detalle del empleado
- Las vacaciones se pagan con el sueldo bruto del último mes

---

### 3.2 Búsqueda Global

**Estado:** ✅ Completado  
**Esfuerzo:** Medio  
**Ubicación:** Header de la ventana principal (visible en todos los módulos)

**Descripción:**
Barra de búsqueda que permite encontrar:
- Empleados (por nombre, legajo, DNI)
- Liquidaciones (por período, empleado)
- Registros de asistencia

**Comportamiento:**
- Atajo: Ctrl+K para activar
- Resultados en dropdown mientras se escribe
- Click en resultado navega al detalle

---

### 3.3 Horas Extra Aprobadas vs Registradas

**Estado:** ✅ Completado  
**Esfuerzo:** Alto  
**Ubicación:** RRHH > Asistencia > Nueva pestaña "Aprobación de Extras"

**Descripción:**
Workflow para controlar que las horas extra se aprueben antes de liquidarlas.

**Flujo:**
1. El reloj registra hora de salida tardía → se genera hora extra automáticamente
2. Las extras quedan en estado "Pendiente de aprobación"
3. Un supervisor aprueba o rechaza desde la UI
4. Solo las aprobadas se incluyen en la liquidación

**Modelo:**
```
aprobacion_extras:
  - id
  - asistencia_id
  - horas_extra
  - estado (pendiente / aprobada / rechazada)
  - aprobado_por
  - fecha_aprobacion
  - motivo_rechazo
```

**Configuración:**
- Activar/desactivar en Configuración RRHH
- Si está desactivado, funciona como ahora (todas se pagan)

---

## Cronograma Estimado

| Bloque | Features | Tiempo estimado | Estado |
|--------|----------|-----------------|--------|
| 1 | Feriados + Notificaciones + Edición masiva | 1-2 días | ✅ Completado |
| 2 | Mapeo fichadas + Histórico sueldo + Resumen quincenal | 2-3 días | ✅ Completado |
| 3 | Vacaciones + Búsqueda global + Aprobación extras | 4-5 días | ✅ Completado |

**Total estimado:** 7-10 días de desarrollo

---

## Dependencias

- Bloque 2 depende de Bloque 1 (feriados necesarios para cálculos correctos)
- Bloque 3.1 (Vacaciones) depende de Bloque 2.2 (Histórico, para calcular antigüedad)
- Bloque 3.3 (Extras aprobadas) es independiente pero afecta la liquidación

---

## Notas

- Cada feature se desarrolla, prueba y commitea individualmente
- Se mantiene compatibilidad con la BD existente (migraciones Alembic)
- Se documenta en el README cada nueva funcionalidad
- Se genera release cuando se completa cada bloque

---

*Documento creado: Junio 2026*
