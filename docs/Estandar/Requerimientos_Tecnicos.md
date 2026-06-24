# Requerimientos Tecnicos — Agilize Gestion

## Stack

| Componente | Tecnologia | Version |
|-----------|-----------|---------|
| Lenguaje | Python | 3.11+ |
| GUI | PySide6 (Qt6) | 6.7+ |
| Base de datos | PostgreSQL | 16+ |
| ORM | SQLAlchemy | 2.0+ |
| Migraciones | Alembic | 1.13+ |
| Autenticacion | bcrypt | 4.1+ |
| Logging | Loguru | 0.7+ |
| Tests | pytest | 8+ |
| Excel | OpenPyXL + xlrd + pandas | 3.1+ |
| PDF | ReportLab | 4+ |
| Iconos | QtAwesome (Font Awesome 5) | 1.4+ |
| Compilacion | PyInstaller | 6+ |
| Instalador | Inno Setup | 6+ |
| VPN | Tailscale | ultima |

## Arquitectura

```
[Cliente Windows]          [Servidor Ubuntu VM]
  App PySide6    ←─ Tailscale VPN ─→  PostgreSQL 16
  (nativa, local)                      (centralizado)
```

- App corre nativa en cada PC (rendimiento optimo)
- BD centralizada en servidor (datos compartidos)
- Conexion via Tailscale (encriptada, sin puertos abiertos)

## Estructura de ventana

```
┌─────────────────────────────────────┐
│  Sidebar (200px)  │  Contenido      │
│  - Menu           │  - QStackedWidget│
│  - Submodulos     │  - Vistas       │
│  - Tema           │                 │
│  - Cerrar sesion  │                 │
└─────────────────────────────────────┘
```

## Patrones de codigo

### Servicios
```python
class MiService:
    def listar(self):
        with get_db() as db:
            return db.query(Modelo).filter(Modelo.activo == True).all()

    def crear(self, datos: dict):
        with get_db() as db:
            obj = Modelo(**datos)
            db.add(obj)
            db.flush()
            return obj
```

### Vistas
```python
class MiView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._cargar()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        # ...

    def _cargar(self):
        # llamar servicio
        pass
```

## Seguridad

- Passwords hasheadas con bcrypt (rounds >= 10)
- SQLAlchemy ORM previene SQL injection
- .env con credenciales NO se commitea
- SECRET_KEY unica por instalacion
- Conexion BD solo via Tailscale (no expuesta a internet)
- Soft delete (nunca se borran registros fisicamente)

## Rendimiento

Benchmarks verificados (100 consultas):
- Listar productos: < 1s
- Buscar productos: < 0.5s
- KPIs generales: < 2s
- Listar facturas: < 1s
- Movimientos cuenta: < 1s

## Instalador

- Inno Setup genera `Setup_AgilizeGestion_vX.Y.Z.exe`
- Pide IP del servidor + password BD
- Escribe `.env` en UTF-8
- Crea acceso directo con icono
- No incluye PostgreSQL (BD esta en servidor)
