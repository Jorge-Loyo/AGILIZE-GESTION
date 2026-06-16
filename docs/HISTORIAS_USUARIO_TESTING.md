# Historias de Usuario — Testing Manual

## Agilize Gestión

---

## HU-01: Login

**Como** administrador  
**Quiero** iniciar sesión con usuario y contraseña  
**Para** acceder al sistema

### Camino feliz:
1. Abrir la aplicación
2. Ingresar usuario: `master`, contraseña: `master2025`
3. Click en "Ingresar"
4. ✅ Se muestra el Dashboard principal con módulos disponibles

---

## HU-02: Crear Empleado

**Como** admin de RRHH  
**Quiero** cargar un empleado nuevo  
**Para** que esté en el sistema y pueda ser liquidado

### Camino feliz:
1. RRHH > Empleados > + Nuevo
2. Completar: Nombre, Apellido, DNI (8 dígitos), CUIL (XX-XXXXXXXX-X), Fecha Nac.
3. Seleccionar Tipo Liquidación: "Por hora (fichado)" o "Sueldo mensual (sin fichado)"
4. Configurar valor hora o sueldo mensual según tipo
5. Click "Guardar"
6. ✅ Empleado aparece en la lista

---

## HU-03: Importar Empleados desde Excel

**Como** admin de RRHH  
**Quiero** cargar empleados masivamente desde un Excel  
**Para** no tener que ingresarlos uno por uno

### Camino feliz:
1. RRHH > Empleados > Importar
2. Seleccionar archivo .xlsx con empleados
3. Aparece diálogo: ¿Actualizar existentes? (checkbox)
4. Click "Importar"
5. ✅ Se muestra: "Creados: X, Actualizados: X"

---

## HU-04: Importar Fichadas (XLS reloj)

**Como** admin de RRHH  
**Quiero** importar el archivo del reloj fichador  
**Para** registrar la asistencia automáticamente

### Camino feliz:
1. RRHH > Asistencia > Importar Fichadas
2. Seleccionar archivo .xls del reloj
3. ✅ Se importan las fichadas vinculadas por legajo
4. Se muestra cantidad importada y errores si los hay

---

## HU-05: Importar Fichadas (XLSX manual) con Mapeo

**Como** admin de RRHH  
**Quiero** importar fichadas de una planilla manual XLSX  
**Para** registrar asistencia de empleados que no usan reloj

### Camino feliz:
1. RRHH > Asistencia > Importar Fichadas
2. Seleccionar archivo .xlsx
3. Si hay hojas no vinculadas → aparece el diálogo de Mapeo
4. Asignar cada hoja no encontrada a un empleado del combo
5. Click "Aplicar Mapeo"
6. ✅ Se importan las fichadas correctamente

---

## HU-06: Registrar Asistencia Manual

**Como** admin de RRHH  
**Quiero** registrar una fichada manualmente  
**Para** corregir o agregar registros que no se importaron

### Camino feliz:
1. RRHH > Asistencia > Registro Manual
2. Seleccionar empleado, fecha, hora entrada, hora salida
3. Click "Registrar"
4. ✅ Registro aparece en la tabla

---

## HU-07: Cerrar Quincena

**Como** admin de RRHH  
**Quiero** cerrar un rango de fechas de asistencia  
**Para** que no se modifiquen y poder liquidar

### Camino feliz:
1. RRHH > Cierres
2. Seleccionar rango: 01/06/2026 al 15/06/2026
3. Click "Cerrar Quincena"
4. ✅ Si no hay incompletos → se cierra exitosamente
5. ❌ Si hay incompletos → mensaje de error con cantidad

---

## HU-08: Liquidar Sueldo (empleado por hora)

**Como** admin de RRHH  
**Quiero** liquidar el sueldo de un empleado que ficha  
**Para** pagarle según sus horas trabajadas

### Camino feliz:
1. RRHH > Nómina > Liquidaciones > + Liquidar
2. Seleccionar período (debe tener cierre)
3. Seleccionar empleado [H] (por hora)
4. ✅ Se muestra desglose: hs normales, extra, sábado, domingo, feriado
5. Seleccionar conceptos adicionales (jubilación, viáticos, etc.)
6. Ver neto en tiempo real
7. Click "Confirmar Liquidación"
8. ✅ Liquidación registrada

---

## HU-09: Liquidar Sueldo (empleado mensual)

**Como** admin de RRHH  
**Quiero** liquidar el sueldo de un empleado mensual  
**Para** pagarle descontando solo sus faltas

### Camino feliz:
1. RRHH > Nómina > Liquidaciones > + Liquidar
2. Seleccionar período
3. Seleccionar empleado [M] (mensual)
4. ✅ Se muestra: Sueldo mensual, faltas, descuento, días trabajados
5. Tipo: MENSUAL
6. Seleccionar conceptos
7. Click "Confirmar Liquidación"
8. ✅ Liquidación registrada

---

## HU-10: Verificar Pendientes de Liquidación

**Como** admin de RRHH  
**Quiero** ver quiénes faltan liquidar en un período  
**Para** asegurarme que todos los activos estén pagados

### Camino feliz:
1. RRHH > Nómina > + Liquidar
2. Click "Verificar Periodo"
3. ✅ Se muestra: activos, a liquidar, liquidados, pendientes
4. Los empleados con datos faltantes aparecen marcados con ** motivo

---

## HU-11: Solicitar Vacaciones

**Como** admin de RRHH  
**Quiero** registrar una solicitud de vacaciones  
**Para** llevar control de los días de cada empleado

### Camino feliz:
1. RRHH > Asistencia > Vacaciones
2. Seleccionar empleado y período anual
3. ✅ Se muestra saldo: correspondientes / tomados / disponibles
4. Seleccionar desde/hasta
5. Click "Solicitar"
6. ✅ Solicitud creada en estado "Pendiente"
7. Seleccionar y click "Aprobar" → estado "Aprobada"
8. Click "Marcar Tomada" → estado "Tomada"

---

## HU-12: Búsqueda Global (Ctrl+K)

**Como** usuario del sistema  
**Quiero** buscar empleados rápidamente desde cualquier pantalla  
**Para** acceder a su detalle sin navegar menús

### Camino feliz:
1. Desde cualquier pantalla presionar Ctrl+K
2. ✅ Aparece barra de búsqueda
3. Escribir nombre, legajo o DNI
4. ✅ Se muestran resultados en dropdown
5. Click en un resultado → se abre detalle del empleado
6. Esc → se cierra la búsqueda

---

## HU-13: Configurar Período de Pago

**Como** administrador  
**Quiero** configurar cada cuánto se liquidan los sueldos  
**Para** adaptar el sistema a mi empresa

### Camino feliz:
1. RRHH > Configuración > Pestaña "Periodo de Pago"
2. Seleccionar: Mensual / Quincenal / Semanal / Diario
3. Click "Guardar Configuración"
4. ✅ El sistema genera períodos según la frecuencia elegida
5. ✅ Al liquidar, los períodos disponibles reflejan la frecuencia

---

## HU-14: Histórico de Sueldo

**Como** admin de RRHH  
**Quiero** ver el historial de cambios salariales de un empleado  
**Para** auditar modificaciones

### Camino feliz:
1. RRHH > Empleados > Click en empleado > Detalle
2. ✅ Si hubo cambios en valor_hora/sueldo_mensual, se muestra tabla "Histórico de Sueldo"
3. Columnas: Fecha, Campo, Valor Anterior, Valor Nuevo

---

## HU-15: Imprimir Recibo de Sueldo

**Como** admin de RRHH  
**Quiero** generar el recibo en PDF  
**Para** entregarlo al empleado

### Camino feliz:
1. RRHH > Nómina > Liquidaciones
2. Seleccionar una liquidación
3. Click "Imprimir Recibo"
4. ✅ Se genera PDF con detalle completo y se abre

---

## HU-16: Gestionar Feriados

**Como** admin de RRHH  
**Quiero** cargar los feriados del año  
**Para** que el sistema calcule correctamente las horas feriado

### Camino feliz:
1. RRHH > Configuración > Feriados
2. Ingresar fecha y descripción
3. Click "Agregar Feriado"
4. ✅ Feriado aparece en la lista del año
5. Se puede eliminar seleccionando y clickeando "Eliminar"

---

## HU-17: Aprobación de Horas Extra

**Como** supervisor  
**Quiero** aprobar o rechazar horas extra antes de liquidar  
**Para** controlar costos

### Camino feliz:
1. RRHH > Asistencia > Aprobación Extras
2. ✅ Se muestran registros pendientes de aprobación
3. Seleccionar uno o varios
4. Click "Aprobar Selección" → estado cambia a "Aprobada"
5. O click "Rechazar" → pide motivo → estado "Rechazada"
6. "Aprobar Todos" → aprueba masivamente

---

## HU-18: Resumen Quincenal/Mensual

**Como** admin de RRHH  
**Quiero** ver el resumen de nómina por quincena  
**Para** comparar costos entre períodos

### Camino feliz:
1. RRHH > Nómina > Resumen Mensual
2. Seleccionar mes/año
3. Seleccionar vista: Mes completo / Q1 / Q2 / Comparar
4. ✅ "Comparar Q1 vs Q2" muestra tabla con diferencias por empleado
5. Diferencias positivas en verde, negativas en rojo

---

## HU-19: Manual de Uso

**Como** usuario nuevo  
**Quiero** consultar cómo usar cada sección del sistema  
**Para** aprender sin necesidad de ayuda externa

### Camino feliz:
1. En el sidebar de cualquier módulo, click "Manual de uso"
2. ✅ Se abre una vista con instrucciones organizadas por sección
3. Cada opción del módulo tiene su explicación paso a paso

---

## Checklist de Testing

| # | Historia | Probado | OK | Observaciones |
|---|----------|---------|-----|---------------|
| 01 | Login | ☐ | ☐ | |
| 02 | Crear Empleado | ☐ | ☐ | |
| 03 | Importar Empleados | ☐ | ☐ | |
| 04 | Importar Fichadas XLS | ☐ | ☐ | |
| 05 | Importar Fichadas XLSX + Mapeo | ☐ | ☐ | |
| 06 | Registro Manual | ☐ | ☐ | |
| 07 | Cerrar Quincena | ☐ | ☐ | |
| 08 | Liquidar (por hora) | ☐ | ☐ | |
| 09 | Liquidar (mensual) | ☐ | ☐ | |
| 10 | Verificar Pendientes | ☐ | ☐ | |
| 11 | Vacaciones | ☐ | ☐ | |
| 12 | Búsqueda Global | ☐ | ☐ | |
| 13 | Período de Pago | ☐ | ☐ | |
| 14 | Histórico Sueldo | ☐ | ☐ | |
| 15 | Recibo PDF | ☐ | ☐ | |
| 16 | Feriados | ☐ | ☐ | |
| 17 | Aprobación Extras | ☐ | ☐ | |
| 18 | Resumen Quincenal | ☐ | ☐ | |
| 19 | Manual de Uso | ☐ | ☐ | |
