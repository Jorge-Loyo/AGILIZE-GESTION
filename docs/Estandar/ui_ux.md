# Estandar UI/UX — Agilize Gestion

## Colores

### Paleta oficial

```python
COLORS = {
    # Primarios (dorado marca)
    "primary":         "#D4AF37",
    "primary_hover":   "#e0c04a",
    "primary_dark":    "#b8962e",

    # Fondos oscuro
    "bg_dark":         "#0f0f0f",
    "surface_dark":    "#141414",
    "card_dark":       "#161616",
    "elevated_dark":   "#1a1a1a",

    # Fondos claro
    "bg_light":        "#fafafa",
    "card_light":      "#ffffff",

    # Texto
    "text_dark":       "#F8F9FA",
    "text_light":      "#1a1a1a",
    "text_muted":      "#888888",

    # Semanticos
    "error":           "#ef4444",
    "success":         "#10b981",
    "warning":         "#f59e0b",
    "info":            "#3b82f6",
}
```

## Temas

Dos temas: **oscuro** (default) y **claro**. Toggle desde dashboard o sidebar.

## Tipografia

- Titulos: 18-24px, bold
- Cuerpo: 12-13px, regular
- Labels: 11px, color #888
- Tablas: 12px
- Consola/errores: Consolas 11px

## Componentes estandar

### Sidebar
- Ancho fijo: 200px
- Fondo: card_dark
- Items: icono + texto, checkable
- Color activo: primary (#D4AF37)
- Color inactivo: #8a8a8a
- Boton "Menu" (volver) arriba
- Boton "Cerrar sesion" (rojo) abajo

### Dashboard
- Grid de botones: 6 columnas, 160x120px
- Icono 40px + label 13px bold
- Border-radius: 14px

### Tablas
- AlternatingRowColors: true
- Header stretch en columna principal
- VerticalHeader oculto
- EditTriggers: NoEditTriggers
- SelectionBehavior: SelectRows

### Botones
- Altura fija: 28-36px
- Botones de accion con ancho fijo (no full-width)
- Alineados a la derecha con addStretch()
- Boton principal: background primary
- Boton secundario: background #2D2D2D
- Boton peligro: background #ef4444

### Cards/Stats
- MinimumWidth: 130-160px
- MinimumHeight: 65-70px
- Label: 10-11px color #888
- Valor: 15-16px bold color #D4AF37
- WordWrap en valores largos

### Formularios
- Inputs: FixedHeight 28px
- Labels: 11px color #aaa
- GridLayout con columnStretch
- MaxWidth 600-750px centrado con wrapper
- Boton guardar: 140px alineado derecha

### Dialogs
- MinimumWidth: 400-600px
- FormLayout para campos
- Botones: Cancelar + Confirmar alineados derecha
- Validacion antes de accept()

### Scroll
- QScrollArea con setWidgetResizable(True)
- FrameShape: NoFrame
- Contenido centrado con wrapper HBoxLayout + stretch

## Iconos

Font Awesome 5 via QtAwesome (`fa5s.` y `fa5b.`).

Iconos principales:
| Modulo | Icono |
|--------|-------|
| RRHH | fa5s.user-friends |
| Ventas | fa5s.cash-register |
| Compras | fa5s.truck-loading |
| Facturador | fa5s.barcode |
| Inventario | fa5s.warehouse |
| Cuentas | fa5s.file-invoice-dollar |
| Finanzas | fa5s.chart-pie |
| Reportes | fa5s.tachometer-alt |
| Herramientas | fa5s.tools |
| Conexiones | fa5s.plug |
| Configuracion | fa5s.sliders-h |

## Reglas generales

- No usar botones full-width para acciones
- Centrar contenido con maxWidth + wrapper
- Scroll en paginas con mucho contenido
- Labels sutiles (11px, #aaa) para jerarquia
- Errores copiables en QTextEdit/Dialog
- Validar antes de guardar (no guardar vacio)
- Soft delete (nunca eliminar fisicamente)
