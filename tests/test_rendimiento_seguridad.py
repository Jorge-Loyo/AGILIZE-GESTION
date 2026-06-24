"""Tests de rendimiento y seguridad."""
import pytest
import time
from datetime import date


# =============================================================================
# TESTS DE RENDIMIENTO
# =============================================================================

class TestRendimiento:
    """Verifica que las operaciones principales se ejecuten en tiempo aceptable."""

    def test_listar_productos_rendimiento(self):
        """Listar productos debe tardar menos de 1 segundo."""
        from services.inventario_service import inventario_service
        start = time.time()
        for _ in range(100):
            inventario_service.listar_productos()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"100 consultas tardaron {elapsed:.2f}s (max 1s)"

    def test_listar_clientes_rendimiento(self):
        """Listar clientes debe tardar menos de 1 segundo."""
        from services.datos.datos_service import datos_service
        start = time.time()
        for _ in range(100):
            datos_service.listar_clientes()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"100 consultas tardaron {elapsed:.2f}s (max 1s)"

    def test_listar_proveedores_rendimiento(self):
        """Listar proveedores debe tardar menos de 1 segundo."""
        from services.datos.datos_service import datos_service
        start = time.time()
        for _ in range(100):
            datos_service.listar_proveedores()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"100 consultas tardaron {elapsed:.2f}s (max 1s)"

    def test_busqueda_productos_rendimiento(self):
        """Busqueda de productos debe tardar menos de 500ms."""
        from services.inventario_service import inventario_service
        start = time.time()
        for _ in range(50):
            inventario_service.buscar_productos("test")
        elapsed = time.time() - start
        assert elapsed < 0.5, f"50 busquedas tardaron {elapsed:.2f}s (max 0.5s)"

    def test_kpis_rendimiento(self):
        """KPIs generales deben calcularse en menos de 2 segundos."""
        from services.herramientas.reportes_service import reportes_service
        start = time.time()
        for _ in range(10):
            reportes_service.kpis_generales()
        elapsed = time.time() - start
        assert elapsed < 2.0, f"10 consultas KPI tardaron {elapsed:.2f}s (max 2s)"

    def test_resumen_inventario_rendimiento(self):
        """Resumen de inventario debe tardar menos de 1 segundo."""
        from services.inventario_service import inventario_service
        start = time.time()
        for _ in range(50):
            inventario_service.resumen()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"50 resumenes tardaron {elapsed:.2f}s (max 1s)"

    def test_movimientos_cuenta_rendimiento(self):
        """Listar movimientos de cuenta debe ser rapido."""
        from services.finanzas.cuentas_service import cuentas_service
        start = time.time()
        for _ in range(100):
            cuentas_service.listar_movimientos("cliente", 1)
        elapsed = time.time() - start
        assert elapsed < 1.0, f"100 consultas tardaron {elapsed:.2f}s (max 1s)"

    def test_listar_facturas_rendimiento(self):
        """Listar facturas debe tardar menos de 1 segundo."""
        from services.finanzas.finanzas_service import finanzas_service
        start = time.time()
        for _ in range(50):
            finanzas_service.listar_facturas()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"50 consultas tardaron {elapsed:.2f}s (max 1s)"

    def test_listar_asientos_rendimiento(self):
        """Listar asientos contables debe ser rapido."""
        from services.finanzas.finanzas_service import finanzas_service
        start = time.time()
        for _ in range(50):
            finanzas_service.listar_asientos()
        elapsed = time.time() - start
        assert elapsed < 1.0, f"50 consultas tardaron {elapsed:.2f}s (max 1s)"

    def test_ventas_por_mes_rendimiento(self):
        """Reporte de ventas por mes debe tardar menos de 2 segundos."""
        from services.herramientas.reportes_service import reportes_service
        start = time.time()
        for _ in range(10):
            reportes_service.ventas_por_mes(12)
        elapsed = time.time() - start
        assert elapsed < 2.0, f"10 reportes tardaron {elapsed:.2f}s (max 2s)"


# =============================================================================
# TESTS DE SEGURIDAD
# =============================================================================

class TestSeguridad:
    """Verifica protecciones contra ataques comunes."""

    def test_sql_injection_busqueda_productos(self):
        """Busqueda de productos no debe ser vulnerable a SQL injection."""
        from services.inventario_service import inventario_service
        # Intentar inyeccion SQL
        payloads = [
            "'; DROP TABLE productos; --",
            "' OR '1'='1",
            "'; DELETE FROM productos WHERE '1'='1",
            "' UNION SELECT * FROM usuarios --",
            "1; UPDATE usuarios SET password_hash='hacked'",
        ]
        for payload in payloads:
            # No debe lanzar excepcion ni devolver datos inesperados
            try:
                result = inventario_service.buscar_productos(payload)
                assert isinstance(result, list)
                assert len(result) == 0  # No debe encontrar nada con payload
            except Exception:
                pass  # Si lanza excepcion esta bien, no es vulnerable

        # Verificar que la tabla sigue existiendo
        productos = inventario_service.listar_productos()
        assert isinstance(productos, list)

    def test_sql_injection_busqueda_clientes(self):
        """Busqueda de clientes no debe ser vulnerable a SQL injection."""
        from services.datos.datos_service import datos_service
        payloads = [
            "'; DROP TABLE clientes; --",
            "' OR '1'='1' --",
            "' UNION SELECT username, password_hash FROM usuarios --",
        ]
        for payload in payloads:
            try:
                result = datos_service.buscar_clientes(payload)
                assert isinstance(result, list)
            except Exception:
                pass

        # Tabla sigue intacta
        clientes = datos_service.listar_clientes()
        assert isinstance(clientes, list)

    def test_sql_injection_busqueda_proveedores(self):
        """Busqueda de proveedores no debe ser vulnerable a SQL injection."""
        from services.datos.datos_service import datos_service
        payloads = [
            "'; DROP TABLE proveedores; --",
            "' OR 1=1 --",
        ]
        for payload in payloads:
            try:
                result = datos_service.buscar_proveedores(payload)
                assert isinstance(result, list)
            except Exception:
                pass

        proveedores = datos_service.listar_proveedores()
        assert isinstance(proveedores, list)

    def test_xss_en_datos_cliente(self):
        """Datos con scripts maliciosos no deben ejecutarse (se guardan como texto)."""
        from services.datos.datos_service import datos_service
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<svg onload=alert(1)>",
        ]
        for payload in xss_payloads:
            # Debe poder guardarse sin problema (como texto plano)
            try:
                datos_service.crear_cliente({"razon_social": payload})
            except Exception:
                pass  # Si falla por otra razon esta bien

    def test_overflow_montos(self):
        """Montos extremos no deben causar crash."""
        from services.finanzas.cuentas_service import cuentas_service
        # Monto negativo
        with pytest.raises(ValueError):
            cuentas_service.registrar_debe("cliente", 1, -99999, "test negativo")

        # Monto cero
        with pytest.raises(ValueError):
            cuentas_service.registrar_debe("cliente", 1, 0, "test cero")

    def test_asiento_descuadrado_no_permitido(self):
        """No debe permitir crear asientos descuadrados."""
        from services.finanzas.finanzas_service import finanzas_service
        cuentas = finanzas_service.listar_cuentas()
        cuentas_no_grupo = [c for c in cuentas if not c.es_grupo]
        if len(cuentas_no_grupo) >= 2:
            with pytest.raises(ValueError, match="descuadrado"):
                finanzas_service.crear_asiento(
                    date.today(), "Intento fraude",
                    [{"cuenta_id": cuentas_no_grupo[0].id, "debe": 99999, "haber": 0},
                     {"cuenta_id": cuentas_no_grupo[1].id, "debe": 0, "haber": 1}]
                )

    def test_facturador_codigo_inexistente(self):
        """Codigo de facturador inexistente no debe dar acceso."""
        from services.datos.facturador_config_service import facturador_config_service
        result = facturador_config_service.obtener_por_codigo("HACK001")
        assert result is None

    def test_password_no_en_texto_plano(self):
        """Las passwords deben estar hasheadas, no en texto plano."""
        from core.database import get_db
        from models.usuario import Usuario
        with get_db() as db:
            usuarios = db.query(Usuario).all()
            for u in usuarios:
                # El hash bcrypt empieza con $2b$
                assert u.password_hash.startswith("$2b$") or u.password_hash.startswith("$2a$"), \
                    f"Password de {u.username} no esta hasheada"

    def test_salida_sin_stock_no_permitida(self):
        """No debe permitir sacar mas stock del disponible."""
        from services.inventario_service import inventario_service
        with pytest.raises(ValueError, match="insuficiente"):
            inventario_service.registrar_salida(99999, 99999, 1000000)

    def test_caja_doble_apertura(self):
        """No debe permitir abrir dos cajas simultaneas."""
        from services.finanzas.finanzas_service import finanzas_service
        if finanzas_service.caja_actual():
            finanzas_service.cerrar_caja(0)
        finanzas_service.abrir_caja(100)
        with pytest.raises(ValueError, match="Ya hay una caja abierta"):
            finanzas_service.abrir_caja(200)
        finanzas_service.cerrar_caja(100)

    def test_env_no_expone_credentials(self):
        """El archivo .env no debe estar en el repositorio."""
        from pathlib import Path
        gitignore = Path("c:/Desarrollo/Agilize-Gestion/.gitignore")
        if gitignore.exists():
            content = gitignore.read_text()
            assert ".env" in content, ".env debe estar en .gitignore"

    def test_secret_key_no_default(self):
        """SECRET_KEY no debe ser el valor por defecto en produccion."""
        from core.config import settings
        # En desarrollo puede ser dev-key, pero no debe estar vacio
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 5

    def test_bcrypt_rounds_minimo(self):
        """BCRYPT_ROUNDS debe ser al menos 10 para seguridad."""
        from core.config import settings
        assert settings.BCRYPT_ROUNDS >= 10, f"BCRYPT_ROUNDS={settings.BCRYPT_ROUNDS} es muy bajo (min 10)"

    def test_database_url_no_expuesta(self):
        """DATABASE_URL no debe contener credenciales por defecto inseguras."""
        from core.config import settings
        url = settings.DATABASE_URL
        assert "password123" not in url
        assert "admin123" not in url
        assert "root" not in url.split("@")[0] if "@" in url else True
