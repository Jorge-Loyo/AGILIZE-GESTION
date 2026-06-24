"""Tests para modulos: inventario, datos, cuentas, ventas, compras, finanzas."""
import pytest
from datetime import date


# === INVENTARIO ===

class TestInventarioService:
    def test_resumen_vacio(self):
        from services.inventario_service import inventario_service
        r = inventario_service.resumen()
        assert "total_productos" in r
        assert "total_depositos" in r
        assert "total_stock" in r
        assert "valor_inventario" in r
        assert "movimientos_hoy" in r

    def test_crear_categoria(self):
        from services.inventario_service import inventario_service
        cat = inventario_service.crear_categoria("Test Cat", "Categoria de prueba")
        assert cat is not None

    def test_crear_producto(self):
        from services.inventario_service import inventario_service
        p = inventario_service.crear_producto({
            "codigo": "TEST999",
            "nombre": "Producto Test",
            "precio_costo": 100.0,
            "precio_venta": 150.0,
            "stock_minimo": 5,
        })
        assert p is not None

    def test_crear_deposito(self):
        from services.inventario_service import inventario_service
        d = inventario_service.crear_deposito("Deposito Test")
        assert d is not None

    def test_buscar_productos(self):
        from services.inventario_service import inventario_service
        resultados = inventario_service.buscar_productos("TEST999")
        assert isinstance(resultados, list)

    def test_listar_productos(self):
        from services.inventario_service import inventario_service
        productos = inventario_service.listar_productos()
        assert isinstance(productos, list)

    def test_listar_depositos(self):
        from services.inventario_service import inventario_service
        depositos = inventario_service.listar_depositos()
        assert isinstance(depositos, list)

    def test_registrar_entrada_cantidad_invalida(self):
        from services.inventario_service import inventario_service
        with pytest.raises(ValueError):
            inventario_service.registrar_entrada(1, 1, -5)

    def test_registrar_salida_cantidad_invalida(self):
        from services.inventario_service import inventario_service
        with pytest.raises(ValueError):
            inventario_service.registrar_salida(1, 1, 0)

    def test_transferencia_mismo_deposito(self):
        from services.inventario_service import inventario_service
        with pytest.raises(ValueError):
            inventario_service.registrar_transferencia(1, 1, 1, 5)

    def test_productos_bajo_minimo(self):
        from services.inventario_service import inventario_service
        resultado = inventario_service.productos_bajo_minimo()
        assert isinstance(resultado, list)


# === DATOS (CLIENTES/PROVEEDORES) ===

class TestDatosService:
    def test_resumen(self):
        from services.datos_service import datos_service
        r = datos_service.resumen()
        assert "total_proveedores" in r
        assert "total_clientes" in r

    def test_crear_proveedor(self):
        from services.datos_service import datos_service
        p = datos_service.crear_proveedor({"razon_social": "Proveedor Test"})
        assert p is not None

    def test_crear_cliente(self):
        from services.datos_service import datos_service
        c = datos_service.crear_cliente({"razon_social": "Cliente Test"})
        assert c is not None

    def test_listar_proveedores(self):
        from services.datos_service import datos_service
        proveedores = datos_service.listar_proveedores()
        assert isinstance(proveedores, list)

    def test_listar_clientes(self):
        from services.datos_service import datos_service
        clientes = datos_service.listar_clientes()
        assert isinstance(clientes, list)

    def test_buscar_proveedores(self):
        from services.datos_service import datos_service
        r = datos_service.buscar_proveedores("Test")
        assert isinstance(r, list)

    def test_buscar_clientes(self):
        from services.datos_service import datos_service
        r = datos_service.buscar_clientes("Test")
        assert isinstance(r, list)


# === CUENTAS ===

class TestCuentasService:
    def test_obtener_saldo_inexistente(self):
        from services.cuentas_service import cuentas_service
        saldo = cuentas_service.obtener_saldo("cliente", 99999)
        assert saldo == 0.0

    def test_registrar_debe_monto_invalido(self):
        from services.cuentas_service import cuentas_service
        with pytest.raises(ValueError):
            cuentas_service.registrar_debe("cliente", 1, -100, "test")

    def test_registrar_haber_monto_invalido(self):
        from services.cuentas_service import cuentas_service
        with pytest.raises(ValueError):
            cuentas_service.registrar_haber("cliente", 1, 0, "test")

    def test_listar_movimientos_vacio(self):
        from services.cuentas_service import cuentas_service
        movs = cuentas_service.listar_movimientos("cliente", 99999)
        assert isinstance(movs, list)
        assert len(movs) == 0

    def test_resumen_general(self):
        from services.cuentas_service import cuentas_service
        r = cuentas_service.resumen_general()
        assert "saldo_clientes" in r
        assert "saldo_proveedores" in r

    def test_resumen_clientes(self):
        from services.cuentas_service import cuentas_service
        r = cuentas_service.resumen_clientes()
        assert isinstance(r, list)

    def test_resumen_proveedores(self):
        from services.cuentas_service import cuentas_service
        r = cuentas_service.resumen_proveedores()
        assert isinstance(r, list)


# === VENTAS ===

class TestVentasService:
    def test_listar_presupuestos(self):
        from services.ventas_service import ventas_service
        r = ventas_service.listar_presupuestos()
        assert isinstance(r, list)

    def test_listar_pedidos(self):
        from services.ventas_service import ventas_service
        r = ventas_service.listar_pedidos()
        assert isinstance(r, list)

    def test_crear_presupuesto(self):
        from services.ventas_service import ventas_service
        items = [{"descripcion": "Item test", "cantidad": 2, "precio_unitario": 100}]
        p = ventas_service.crear_presupuesto("Cliente Test", items)
        assert p is not None
        assert p.total > 0

    def test_crear_pedido(self):
        from services.ventas_service import ventas_service
        items = [{"descripcion": "Item test", "cantidad": 1, "precio_unitario": 50}]
        p = ventas_service.crear_pedido("Cliente Test", items)
        assert p is not None
        assert p.total > 0


# === COMPRAS ===

class TestComprasService:
    def test_listar_ordenes(self):
        from services.compras_service import compras_service
        r = compras_service.listar_ordenes()
        assert isinstance(r, list)

    def test_crear_orden(self):
        from services.compras_service import compras_service
        items = [{"descripcion": "Insumo test", "cantidad": 10, "precio_unitario": 25}]
        o = compras_service.crear_orden("Proveedor Test", items)
        assert o is not None
        assert o.total > 0


# === FINANZAS ===

class TestFinanzasService:
    def test_listar_cuentas_contables(self):
        from services.finanzas_service import finanzas_service
        cuentas = finanzas_service.listar_cuentas()
        assert isinstance(cuentas, list)

    def test_crear_asiento_descuadrado(self):
        from services.finanzas_service import finanzas_service
        cuentas = finanzas_service.listar_cuentas()
        if len(cuentas) >= 2:
            with pytest.raises(ValueError, match="descuadrado"):
                finanzas_service.crear_asiento(
                    date.today(), "Test descuadrado",
                    [{"cuenta_id": cuentas[0].id, "debe": 100, "haber": 0},
                     {"cuenta_id": cuentas[1].id, "debe": 0, "haber": 50}]
                )

    def test_crear_asiento_cuadrado(self):
        from services.finanzas_service import finanzas_service
        cuentas = finanzas_service.listar_cuentas()
        if len(cuentas) >= 2:
            cuentas_no_grupo = [c for c in cuentas if not c.es_grupo]
            if len(cuentas_no_grupo) >= 2:
                a = finanzas_service.crear_asiento(
                    date.today(), "Test cuadrado",
                    [{"cuenta_id": cuentas_no_grupo[0].id, "debe": 100, "haber": 0},
                     {"cuenta_id": cuentas_no_grupo[1].id, "debe": 0, "haber": 100}]
                )
                assert a is not None
                assert a.numero > 0

    def test_listar_asientos(self):
        from services.finanzas_service import finanzas_service
        asientos = finanzas_service.listar_asientos()
        assert isinstance(asientos, list)

    def test_listar_facturas(self):
        from services.finanzas_service import finanzas_service
        facturas = finanzas_service.listar_facturas()
        assert isinstance(facturas, list)

    def test_crear_factura(self):
        from services.finanzas_service import finanzas_service
        datos = {
            "tipo_comprobante": "factura",
            "letra": "",
            "tipo_entidad": "cliente",
            "entidad_nombre": "Test Cliente",
            "impuesto_porcentaje": 16,
        }
        items = [{"descripcion": "Servicio", "cantidad": 1, "precio_unitario": 1000}]
        f = finanzas_service.crear_factura(datos, items)
        assert f is not None
        assert f.total == 1160  # 1000 + 16%

    def test_listar_cuentas_bancarias(self):
        from services.finanzas_service import finanzas_service
        cuentas = finanzas_service.listar_cuentas_bancarias()
        assert isinstance(cuentas, list)

    def test_abrir_caja_doble(self):
        from services.finanzas_service import finanzas_service
        # Si hay caja abierta, cerrarla primero
        if finanzas_service.caja_actual():
            finanzas_service.cerrar_caja(0)
        finanzas_service.abrir_caja(1000)
        with pytest.raises(ValueError, match="Ya hay una caja abierta"):
            finanzas_service.abrir_caja(500)
        finanzas_service.cerrar_caja(1000)

    def test_resumen_caja_sin_abrir(self):
        from services.finanzas_service import finanzas_service
        if finanzas_service.caja_actual():
            finanzas_service.cerrar_caja(0)
        r = finanzas_service.resumen_caja()
        assert r is None


# === FACTURADOR CONFIG ===

class TestFacturadorConfig:
    def test_listar(self):
        from services.facturador_config_service import facturador_config_service
        r = facturador_config_service.listar()
        assert isinstance(r, list)

    def test_crear_facturador(self):
        from services.facturador_config_service import facturador_config_service
        f = facturador_config_service.crear("FTEST", "Test POS", depositos_ids="1,2")
        assert f is not None
        assert f.codigo == "FTEST"

    def test_obtener_por_codigo(self):
        from services.facturador_config_service import facturador_config_service
        f = facturador_config_service.obtener_por_codigo("FTEST")
        if f:
            assert f.codigo == "FTEST"

    def test_get_depositos_ids(self):
        from services.facturador_config_service import facturador_config_service
        f = facturador_config_service.obtener_por_codigo("FTEST")
        if f:
            ids = facturador_config_service.get_depositos_ids(f)
            assert isinstance(ids, list)
            assert 1 in ids
            assert 2 in ids

    def test_obtener_inexistente(self):
        from services.facturador_config_service import facturador_config_service
        f = facturador_config_service.obtener_por_codigo("NOEXISTE")
        assert f is None


# === REPORTES ===

class TestReportesService:
    def test_kpis_generales(self):
        from services.reportes_service import reportes_service
        r = reportes_service.kpis_generales()
        assert "ventas_mes" in r
        assert "compras_mes" in r
        assert "margen_mes" in r
        assert "saldo_bancos" in r
        assert "por_cobrar" in r
        assert "por_pagar" in r
        assert "total_productos" in r
        assert "total_clientes" in r

    def test_ventas_por_mes(self):
        from services.reportes_service import reportes_service
        r = reportes_service.ventas_por_mes(3)
        assert isinstance(r, list)
        assert len(r) == 3
        for item in r:
            assert "mes" in item
            assert "total" in item

    def test_top_clientes(self):
        from services.reportes_service import reportes_service
        r = reportes_service.top_clientes(5)
        assert isinstance(r, list)
