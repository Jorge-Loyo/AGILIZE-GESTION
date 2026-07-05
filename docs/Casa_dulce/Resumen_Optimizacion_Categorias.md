# Optimización de Categorías — Casa Dulce

**Fecha:** Julio 2026  
**Preparado por:** Agilize Soluciones

---

## Resumen Ejecutivo

Se realizó una optimización del catálogo de categorías de productos de Casa Dulce, reduciendo de **96 categorías** a **30 categorías** bien estructuradas, manteniendo los 2800 productos intactos.

---

## Problema Detectado

El sistema de categorías original presentaba:

1. **Fragmentación excesiva**: 96 categorías para 2800 productos (promedio 29 prods/cat)
2. **Duplicados semánticos**: Múltiples categorías para el mismo tipo de producto
   - 8 categorías distintas de "Colorantes" (por marca)
   - 7 categorías de "Discos" (por material/tipo)
   - 9 categorías de "Moldes/Torteras" (por forma/tamaño)
3. **Categorías mínimas**: 9 categorías con 1-3 productos
4. **Nombres ambiguos**: "LIQUIDA", "POLVO", "LISAS", "UNTABLE" — no describen el producto
5. **Errores tipográficos**: "ENVASRES", "RETANGULAR", "CONDESADA"

---

## Solución Aplicada

### Criterios de agrupación:
- **Por función/uso** del producto (no por marca ni tamaño)
- **Mínimo 5 productos** por categoría
- **Nombres descriptivos** que cualquier empleado pueda entender
- **Sin duplicados** semánticos

### Resultado:

| Métrica | Antes | Después |
|---------|-------|---------|
| Categorías | 96 | 30 |
| Productos | 2800 | 2800 |
| Promedio prods/categoría | 29 | 93 |
| Categorías con <5 prods | 9 | 0 |
| Categorías duplicadas | ~40 | 0 |

---

## Mapeo Completo de Categorías

### ACCESORIOS (225 productos)
- ACCESORIOS → ACCESORIOS
- ACRILICOS → ACCESORIOS
- VOLCAN → ACCESORIOS

### AREQUIPE (59 productos)
- AREQUIPE → AREQUIPE

### AZUCAR Y ENDULZANTES (15 productos)
- AZUCAR PULVERIZADA → AZUCAR Y ENDULZANTES

### BASE DE HELADO (28 productos)
- BASE DE HELADO → BASE DE HELADO

### BOLSAS Y EMPAQUES (56 productos)
- BOLSAS CELOFAN/PLASTICAS → BOLSAS Y EMPAQUES

### BOQUILLAS Y MANGAS (100 productos)
- BOQUILLAS ATECO → BOQUILLAS Y MANGAS
- LISAS → BOQUILLAS Y MANGAS

### CAJAS Y EMPAQUES (122 productos)
- CAJAS DE CARTON → CAJAS Y EMPAQUES
- CAJAS PARA TORTAS → CAJAS Y EMPAQUES
- DOMOS PARA TORTAS → CAJAS Y EMPAQUES

### CAPACILLOS (26 productos)
- CAPACILLOS DE PAPEL → CAPACILLOS
- CAPACILLOS METALIZADOS → CAPACILLOS

### CHOCOLATE Y CACAO (110 productos)
- CHOCOLATE → CHOCOLATE Y CACAO
- CHOCOLATES DE COBERTURA → CHOCOLATE Y CACAO
- POLVO → CHOCOLATE Y CACAO (eran todos cacaos en polvo)
- UNTABLE → CHOCOLATE Y CACAO (chocotinas y cremas de chocolate)

### COBERTURAS Y BRILLOS (56 productos)
- BRILLO Y GEL DE GLUCOSA → COBERTURAS Y BRILLOS
- COBERTURA → COBERTURAS Y BRILLOS

### COLORANTES (263 productos)
- CANDY COLOR CHEF MASTER → COLORANTES
- COLORANTE LIPOSOLUBLE CHOCOLATIER → COLORANTES
- COLORANTES → COLORANTES
- COLORANTES CHEF MASTER → COLORANTES
- COLORANTES EN POLVO → COLORANTES
- COLORANTES FAB → COLORANTES
- COLORANTES PAYASITO → COLORANTES
- COLORANTES REPO ART → COLORANTES
- COLORANTES TASTY → COLORANTES
- FAB SOFT GEL → COLORANTES
- MARCADORES FAB → COLORANTES
- POLVOS METALIZADOS → COLORANTES

### CONDIMENTOS (60 productos)
- CONDIMENTOS → CONDIMENTOS

### CORONAS Y TOPPERS (55 productos)
- CORONA COMESTIBLE → CORONAS Y TOPPERS
- CORONA DE METAL → CORONAS Y TOPPERS
- CORONAS → CORONAS Y TOPPERS
- TOPPERS → CORONAS Y TOPPERS

### DECORACIONES Y SPRINKLES (170 productos)
- ESCARCHAS → DECORACIONES Y SPRINKLES
- ESFERAS DECORATIVAS → DECORACIONES Y SPRINKLES
- ESPIRALES → DECORACIONES Y SPRINKLES
- LLUVIA → DECORACIONES Y SPRINKLES
- LLUVIAS, BLOK ETC → DECORACIONES Y SPRINKLES
- NUMEROS → DECORACIONES Y SPRINKLES
- PERLAS → DECORACIONES Y SPRINKLES
- PERLAS Y SPRINKLES → DECORACIONES Y SPRINKLES
- SPRINKLES → DECORACIONES Y SPRINKLES
- VELAS → DECORACIONES Y SPRINKLES

### DISCOS Y BASES (83 productos)
- BASES CUADRADAS Y RECTANGULARES → DISCOS Y BASES
- DISCOS DE ANIME → DISCOS Y BASES
- DISCOS DE MADERA → DISCOS Y BASES
- DISCOS DRUM → DISCOS Y BASES
- DISCOS ECONOMICOS → DISCOS Y BASES
- DISCOS KAPATO O SCALLOPED → DISCOS Y BASES
- DISCOS PARA TORTAS → DISCOS Y BASES
- DISCOS SEMI DRUM → DISCOS Y BASES
- SOPORTES → DISCOS Y BASES

### ELECTRODOMESTICOS (5 productos)
- ELECTRODOMESTICOS → ELECTRODOMESTICOS

### ENVASES Y DESCARTABLES (203 productos)
- CARTULINA → ENVASES Y DESCARTABLES
- DELIVERY → ENVASES Y DESCARTABLES
- MINI BOTELLAS → ENVASES Y DESCARTABLES
- PLASTICOS/CONSUMIBLES/ENVASRES PORCION → ENVASES Y DESCARTABLES

### ESENCIAS Y SABORIZANTES (239 productos)
- ESENCIAS → ESENCIAS Y SABORIZANTES
- LIQUIDA → ESENCIAS Y SABORIZANTES (eran todas esencias/vainillas líquidas)

### FONDANT (41 productos)
- FONDANT → FONDANT

### FRUTOS SECOS (103 productos)
- FRUTOS CUBIERTOS → FRUTOS SECOS
- FRUTOS SECOS → FRUTOS SECOS

### GELATINA Y FLAN (67 productos)
- FLAN → GELATINA Y FLAN
- GELATINA → GELATINA Y FLAN

### LACTEOS Y CREMAS (48 productos)
- CHANTILLY → LACTEOS Y CREMAS
- CREMA DE LECHE → LACTEOS Y CREMAS
- LECHE CONDESADA → LACTEOS Y CREMAS

### LICORES (21 productos)
- LICORES → LICORES

### MATERIA GRASA (47 productos)
- MATERIA GRASA → MATERIA GRASA

### MOLDES Y TORTERAS (308 productos)
- MOLDES DE CORAZON → MOLDES Y TORTERAS
- MOLDES DE SILICON → MOLDES Y TORTERAS
- MOLDES RETANGULAR → MOLDES Y TORTERAS
- MOLDES Y PONQUES DONAS → MOLDES Y TORTERAS
- QUESILLERAS → MOLDES Y TORTERAS
- SAVARIN BUNDT CAKE → MOLDES Y TORTERAS
- TORTERA 15CM ALTURA → MOLDES Y TORTERAS
- TORTERAS 10CM ALTO → MOLDES Y TORTERAS
- TORTERAS 4CM ALTO → MOLDES Y TORTERAS
- TORTERAS 6CM ALTO → MOLDES Y TORTERAS
- TORTERAS Y MOLDES → MOLDES Y TORTERAS

### NAVIDAD (54 productos)
- NAVIDAD → NAVIDAD

### QUIMICOS (73 productos)
- QUIMICOS → QUIMICOS

### SIN CATEGORIA (10 productos)
- #N/A → SIN CATEGORIA
- PRECIOS AL MAYOR → SIN CATEGORIA
- SIN CATEGORIA → SIN CATEGORIA
- TRADICIONAL → SIN CATEGORIA

### UTENSILIOS REPOSTERIA (55 productos)
- EXTENSORES Y PAPEL → UTENSILIOS REPOSTERIA
- MADERA → UTENSILIOS REPOSTERIA
- REPOSTERO → UTENSILIOS REPOSTERIA
- SCRAPER Y PEINES → UTENSILIOS REPOSTERIA

### VIVERES Y ENLATADOS (98 productos)
- ENLATADOS → VIVERES Y ENLATADOS
- VIVERES → VIVERES Y ENLATADOS

---

## Archivos Generados

| Archivo | Descripción |
|---------|-------------|
| `Maestro_Productos_Categorizado.xlsx` | Maestro con columna "Categoria Optimizada" agregada |
| `Categorias_Productos_Limpio.xlsx` | Reporte original limpio por categoría (96 cats) |
| `Resumen_Optimizacion_Categorias.md` | Este documento |

---

## Próximos Pasos Sugeridos

1. **Validar** con el equipo de Casa Dulce que las agrupaciones tienen sentido para su operación
2. **Revisar ACCESORIOS** (225 prods) — podría subdividirse más si lo necesitan
3. **Aplicar** en el sistema de punto de venta reemplazando la categoría original
4. **Revisar SIN CATEGORIA** (10 prods) — asignar manualmente donde corresponda
