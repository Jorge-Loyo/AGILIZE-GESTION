# Flujo de Trabajo — Agilize Gestion

## Git

Rama unica `main` con tags de version.

### Convenciones de commits

```
tipo: mensaje breve en presente
```

| Tipo | Uso |
|------|-----|
| `feat:` | Nueva funcionalidad |
| `fix:` | Correccion de error |
| `refactor:` | Cambio sin cambio funcional |
| `ui:` | Cambios visuales/esteticos |
| `docs:` | Documentacion |
| `test:` | Tests |
| `chore:` | Mantenimiento (build, deps) |

Ejemplos:
```
feat: modulo Inventario con CRUD productos y depositos
fix: error encoding UTF-8 al leer .env en Windows
ui: rediseño pagina Desarrollador con scroll
docs: guia de despliegue servidor con Tailscale
```

## Tests

**pytest** como framework. Tests en `tests/`.

Tipos de tests:
- `test_services.py` — tests de RRHH (periodos, vacaciones, liquidacion)
- `test_modulos.py` — tests de modulos nuevos (inventario, datos, cuentas, ventas, compras, finanzas)
- `test_rendimiento_seguridad.py` — rendimiento y seguridad

Ejecutar:
```bash
venv/Scripts/pytest tests/ -v
```

## Build y Release

1. Compilar app: `venv\Scripts\pyinstaller AgilizeGestion.spec --noconfirm`
2. Compilar instalador: `iscc scripts\inno\setup.iss`
3. Crear tag: `git tag -a vX.Y.Z -m "descripcion"`
4. Push: `git push origin main --tags`
5. Release: `gh release create vX.Y.Z dist\Setup_AgilizeGestion_vX.Y.Z.exe`

## Despliegue

- Servidor: Ubuntu Server + PostgreSQL + Tailscale
- Clientes: Setup.exe (instala app + configura conexion)
- Conexion: Tailscale VPN (sin abrir puertos)

## Flujo diario

1. Desarrollar en `c:\Desarrollo\Agilize-Gestion`
2. Probar: `venv/Scripts/python main.py`
3. Tests: `venv/Scripts/pytest tests/ -v`
4. Commit cuando este listo
5. Build + release si es version nueva
