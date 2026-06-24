# Estandar de Base de Datos — Agilize Gestion

## ORM

**SQLAlchemy 2.0** con `DeclarativeBase`, `Mapped` + `mapped_column`.

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

@contextmanager
def get_db() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

## Convenciones de naming

| Elemento | Convencion | Ejemplo |
|----------|-----------|---------|
| Tablas | plural snake_case | `usuarios`, `productos`, `movimientos_stock` |
| Columnas | snake_case | `password_hash`, `precio_venta` |
| Clave primaria | `id` (SERIAL) | `id INTEGER PRIMARY KEY` |
| Clave foranea | `{tabla_singular}_id` | `cliente_id`, `deposito_id` |
| Relaciones | singular o descriptivo | `producto`, `stock_depositos` |
| Timestamps | `created_at`, `updated_at` | `TIMESTAMPTZ DEFAULT NOW()` |

## TimestampMixin

Todos los modelos incluyen:

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
```

## Modelos del sistema

### Core
- `usuarios` — login, autenticacion
- `roles` — permisos agrupados
- `permisos` — accion por modulo
- `rol_permisos` — asignacion
- `audit_log` — historial de operaciones

### RRHH
- `empleados`, `departamentos`, `cargos`
- `asistencias`, `feriados`
- `liquidaciones`, `liquidacion_detalle`
- `conceptos_nomina`, `config_nomina`
- `adelantos`, `vacaciones`
- `cierres_asistencia`, `cierres_liquidacion`
- `sac_registros`, `sac_liquidaciones`
- `historico_sueldo`, `aprobacion_extras`

### Inventario
- `categorias_producto`
- `productos`
- `depositos`
- `stock_deposito`
- `movimientos_stock`

### Comercial
- `clientes`, `proveedores`
- `presupuestos`, `presupuesto_detalles`
- `pedidos_venta`, `pedido_venta_detalles`
- `ordenes_compra`, `orden_compra_detalles`

### Finanzas
- `cuentas_contables`
- `asientos`, `asiento_detalles`
- `facturas`, `factura_detalles`
- `cuentas_bancarias`, `movimientos_banco`
- `cajas`, `movimientos_caja`

### Cuentas
- `movimientos_cuenta` — debe/haber de clientes y proveedores

### Configuracion
- `datos_empresa` — clave/valor
- `sucursales`
- `config_facturadores`

## Migraciones

**Alembic** con auto-upgrade al iniciar la app. Fallback: `Base.metadata.create_all()`.

## Soft delete

No se eliminan registros. Columna `activo: bool = True`. Filtrar siempre `WHERE activo = true`.

## PostgreSQL

- Version: 16+
- Encoding: UTF-8
- Pool: `pool_size=5, max_overflow=10`
- Busquedas: `ILIKE` para case-insensitive
