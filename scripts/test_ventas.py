"""Tests de rendimiento, seguridad e integridad del modulo de ventas."""
import time
import sys
sys.path.insert(0, '.')


def test_rendimiento():
    from services.cliente_service import cliente_service
    from services.precios_venta_service import precios_venta_service
    from services.riesgo_venta_service import riesgo_venta_service
    from services.reportes_venta_service import reportes_venta_service

    print("=" * 60)
    print("TESTS DE RENDIMIENTO - MODULO VENTAS")
    print("=" * 60)

    tests = [
        ("Listar clientes", lambda: cliente_service.listar_clientes()),
        ("Buscar clientes", lambda: cliente_service.buscar_clientes("test")),
        ("Clientes con deuda", lambda: cliente_service.clientes_con_deuda()),
        ("Clientes bloqueados", lambda: cliente_service.clientes_bloqueados()),
        ("Verificar credito", lambda: cliente_service.verificar_credito(1, 5000)),
        ("Listas de precios", lambda: precios_venta_service.listar_listas()),
        ("Precio en lista", lambda: precios_venta_service.obtener_precio_lista(1, "GENERAL")),
        ("Calcular descuento", lambda: precios_venta_service.calcular_descuento(1, 100, 1, "mayorista")),
        ("Reglas descuento", lambda: precios_venta_service.listar_reglas_descuento()),
        ("Tipo cambio", lambda: precios_venta_service.obtener_tipo_cambio("USD", "ARS")),
        ("Validar venta", lambda: riesgo_venta_service.validar_venta(1, 10000)),
        ("Validar margen", lambda: riesgo_venta_service.validar_margen(1, 150, 10)),
        ("Descuento max", lambda: riesgo_venta_service.descuento_maximo_permitido(1, 200, 10)),
        ("Resumen riesgo", lambda: riesgo_venta_service.resumen_riesgo()),
        ("Ranking productos", lambda: reportes_venta_service.ranking_productos(90)),
        ("Ranking clientes", lambda: reportes_venta_service.ranking_clientes(90)),
        ("Ranking vendedores", lambda: reportes_venta_service.ranking_vendedores(90)),
        ("Comisiones", lambda: reportes_venta_service.calcular_comisiones(30, 5)),
        ("Margen contribucion", lambda: reportes_venta_service.margen_contribucion(90)),
        ("Margen por cliente", lambda: reportes_venta_service.margen_por_cliente(90)),
    ]

    for nombre, fn in tests:
        start = time.time()
        try:
            result = fn()
            ms = (time.time() - start) * 1000
            count = len(result) if hasattr(result, '__len__') else (result if isinstance(result, (int, float)) else "ok")
            print(f"[OK] {nombre}: {ms:.0f}ms ({count})")
        except Exception as e:
            print(f"[ERR] {nombre}: {e}")


def test_seguridad():
    from services.cliente_service import cliente_service
    from services.precios_venta_service import precios_venta_service

    print("\n" + "=" * 60)
    print("TESTS DE SEGURIDAD - SQL INJECTION")
    print("=" * 60)

    payloads = [
        "'; DROP TABLE clientes; --",
        "1' OR '1'='1",
        "'; DELETE FROM facturas_venta; --",
        "<script>alert('xss')</script>",
        "' UNION SELECT * FROM usuarios --",
        "Robert'); DROP TABLE pedidos_venta;--",
    ]

    # Buscar clientes
    for payload in payloads:
        try:
            result = cliente_service.buscar_clientes(payload)
            print(f"[OK] buscar_clientes: '{payload[:35]}...' -> {len(result)} (sin crash)")
        except Exception as e:
            print(f"[WARN] buscar_clientes: {type(e).__name__}")

    # Obtener precio con lista inyectada
    for payload in payloads[:3]:
        try:
            result = precios_venta_service.obtener_precio_lista(1, payload)
            print(f"[OK] obtener_precio_lista: '{payload[:35]}...' -> {result}")
        except Exception as e:
            print(f"[WARN] obtener_precio_lista: {type(e).__name__}")

    # Tipo cambio con moneda inyectada
    for payload in payloads[:3]:
        try:
            result = precios_venta_service.obtener_tipo_cambio(payload, "ARS")
            print(f"[OK] tipo_cambio: '{payload[:35]}...' -> sin crash")
        except Exception as e:
            print(f"[WARN] tipo_cambio: {type(e).__name__}")


def test_validaciones():
    from services.cliente_service import cliente_service
    from services.riesgo_venta_service import riesgo_venta_service
    from services.precios_venta_service import precios_venta_service

    print("\n" + "=" * 60)
    print("TESTS DE VALIDACIONES - EDGE CASES")
    print("=" * 60)

    # Cliente inexistente
    try:
        cliente_service.verificar_credito(999999, 100)
        print("[FAIL] Credito cliente inexistente aceptado")
    except ValueError as e:
        print(f"[OK] Credito cliente inexistente: {e}")

    # Validar venta cliente inexistente
    r = riesgo_venta_service.validar_venta(999999, 100)
    assert r["puede_vender"] is False
    print(f"[OK] Venta cliente inexistente: puede_vender=False")

    # Margen producto inexistente
    r = riesgo_venta_service.validar_margen(999999, 100, 10)
    assert r["valido"] is False
    print(f"[OK] Margen producto inexistente: valido=False")

    # Descuento max producto inexistente
    r = riesgo_venta_service.descuento_maximo_permitido(999999, 100, 10)
    print(f"[OK] Descuento max producto inexistente: {r}%")

    # Validar descuento que rompe margen
    r = riesgo_venta_service.validar_descuento(1, 110, 95, 10)
    print(f"[OK] Descuento 95% sobre $110: valido={r['valido']}, alerta='{r.get('alerta', '')[:50]}'")

    # Registrar cargo cliente inexistente
    try:
        cliente_service.registrar_cargo(999999, 100)
        print("[FAIL] Cargo cliente inexistente aceptado")
    except ValueError as e:
        print(f"[OK] Cargo cliente inexistente: {e}")

    # Registrar pago cliente inexistente
    try:
        cliente_service.registrar_pago(999999, 100)
        print("[FAIL] Pago cliente inexistente aceptado")
    except ValueError as e:
        print(f"[OK] Pago cliente inexistente: {e}")

    # Convertir moneda sin tipo de cambio
    try:
        precios_venta_service.convertir_monto(1000, "XYZ", "ABC")
        print("[FAIL] Conversion sin TC aceptada")
    except ValueError as e:
        print(f"[OK] Conversion sin TC: {e}")

    # Precio en lista inexistente
    r = precios_venta_service.obtener_precio_lista(1, "LISTA_FALSA")
    assert r == 0
    print(f"[OK] Precio lista inexistente: {r}")

    # Monto negativo en validar venta
    r = riesgo_venta_service.validar_venta(1, -5000)
    print(f"[OK] Venta monto negativo: puede_vender={r['puede_vender']}")

    # Descuento 0%
    r = riesgo_venta_service.validar_descuento(1, 100, 0, 10)
    print(f"[OK] Descuento 0%: valido={r['valido']}")

    # Descuento 100%
    r = riesgo_venta_service.validar_descuento(1, 100, 100, 10)
    print(f"[OK] Descuento 100%: valido={r['valido']}, alerta='{r.get('alerta', '')[:40]}'")


def test_integridad():
    from services.cliente_service import cliente_service
    from services.riesgo_venta_service import riesgo_venta_service
    from services.precios_venta_service import precios_venta_service
    from services.reportes_venta_service import reportes_venta_service

    print("\n" + "=" * 60)
    print("TESTS DE INTEGRIDAD - LOGICA DE NEGOCIO")
    print("=" * 60)

    # Resumen riesgo consistente
    r = riesgo_venta_service.resumen_riesgo()
    assert r["total_clientes"] >= r["bloqueados"]
    assert r["total_clientes"] >= r["con_deuda"]
    print(f"[OK] Resumen riesgo: {r['total_clientes']} clientes, {r['bloqueados']} bloq, {r['con_deuda']} deuda")

    # Listas de precios existen
    listas = precios_venta_service.listar_listas()
    assert len(listas) >= 5
    codigos = [l.codigo for l in listas]
    assert "GENERAL" in codigos
    assert "MAYORISTA" in codigos
    print(f"[OK] Listas precios: {len(listas)} ({', '.join(codigos)})")

    # Ranking productos estructura correcta
    rp = reportes_venta_service.ranking_productos(365)
    assert "items" in rp
    assert "total_ventas" in rp
    print(f"[OK] Ranking productos: estructura valida, {len(rp['items'])} items")

    # Comisiones estructura
    com = reportes_venta_service.calcular_comisiones(365, 3, "facturado")
    for c in com:
        assert "vendedor" in c
        assert "comision" in c
        assert c["comision"] >= 0
    print(f"[OK] Comisiones: {len(com)} vendedores, todas >= 0")

    # Margen estructura
    mg = reportes_venta_service.margen_contribucion(365)
    assert mg["total_venta"] >= 0
    assert mg["total_costo"] >= 0
    print(f"[OK] Margen: venta=${mg['total_venta']:,.0f}, costo=${mg['total_costo']:,.0f}, margen={mg['margen_pct']}%")


def test_overflow():
    from services.cliente_service import cliente_service
    from services.precios_venta_service import precios_venta_service

    print("\n" + "=" * 60)
    print("TESTS DE SEGURIDAD - OVERFLOW / LIMITES")
    print("=" * 60)

    # String 10K en busqueda
    try:
        cliente_service.buscar_clientes("A" * 10000)
        print("[OK] Busqueda 10K chars: no crash")
    except Exception as e:
        print(f"[WARN] Busqueda 10K: {type(e).__name__}")

    # ID negativo
    try:
        cliente_service.verificar_credito(-1, 100)
        print("[OK] Credito ID=-1: no crash (o ValueError)")
    except ValueError:
        print("[OK] Credito ID=-1: ValueError")

    # Monto extremo
    from services.riesgo_venta_service import riesgo_venta_service
    r = riesgo_venta_service.validar_venta(1, 99999999999)
    print(f"[OK] Venta monto extremo: puede_vender={r['puede_vender']}")

    # Dias=0 en reportes
    from services.reportes_venta_service import reportes_venta_service
    try:
        reportes_venta_service.ranking_productos(0)
        print("[OK] Ranking dias=0: no crash")
    except Exception as e:
        print(f"[WARN] Ranking dias=0: {e}")


if __name__ == "__main__":
    test_rendimiento()
    test_seguridad()
    test_validaciones()
    test_integridad()
    test_overflow()
    print("\n" + "=" * 60)
    print("TESTS VENTAS COMPLETADOS")
    print("=" * 60)
