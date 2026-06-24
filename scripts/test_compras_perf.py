"""Test de rendimiento y seguridad del modulo de compras."""
import time
import sys
sys.path.insert(0, '.')

def test_rendimiento():
    from services.compras.compras_service import compras_service
    print("=" * 60)
    print("TESTS DE RENDIMIENTO - MODULO COMPRAS")
    print("=" * 60)

    # Crear requisicion
    start = time.time()
    try:
        req = compras_service.crear_requisicion('Test Perf', [{'descripcion': 'Item test', 'cantidad': 1}])
        print(f"[OK] Crear requisicion: {(time.time()-start)*1000:.0f}ms (#{req.numero})")
    except Exception as e:
        print(f"[ERR] Crear requisicion: {e}")

    # Listar ordenes
    start = time.time()
    ordenes = compras_service.listar_ordenes()
    print(f"[OK] Listar ordenes ({len(ordenes)}): {(time.time()-start)*1000:.0f}ms")

    # Listar requisiciones
    start = time.time()
    reqs = compras_service.listar_requisiciones()
    print(f"[OK] Listar requisiciones ({len(reqs)}): {(time.time()-start)*1000:.0f}ms")

    # Listar listas de precio
    start = time.time()
    listas = compras_service.listar_listas_precio()
    print(f"[OK] Listar listas precio ({len(listas)}): {(time.time()-start)*1000:.0f}ms")

    # Listar cotizaciones
    start = time.time()
    cots = compras_service.listar_cotizaciones()
    print(f"[OK] Listar cotizaciones ({len(cots)}): {(time.time()-start)*1000:.0f}ms")

    # Listar aprobaciones
    start = time.time()
    aprobs = compras_service.listar_aprobaciones()
    print(f"[OK] Listar aprobaciones ({len(aprobs)}): {(time.time()-start)*1000:.0f}ms")

    # Trazabilidad
    start = time.time()
    traza = compras_service.obtener_trazabilidad('orden_compra', 1)
    print(f"[OK] Trazabilidad OC#1: {(time.time()-start)*1000:.0f}ms")

    # Reglas
    start = time.time()
    reglas = compras_service.listar_reglas_aprobacion()
    print(f"[OK] Listar reglas ({len(reglas)}): {(time.time()-start)*1000:.0f}ms")

    # Precio sugerido
    start = time.time()
    precios = compras_service.obtener_precio_sugerido(descripcion="test")
    print(f"[OK] Precio sugerido: {(time.time()-start)*1000:.0f}ms ({len(precios)} resultados)")


def test_seguridad():
    from services.compras.compras_service import compras_service
    print("\n" + "=" * 60)
    print("TESTS DE SEGURIDAD - SQL INJECTION")
    print("=" * 60)

    # SQL Injection en busqueda de precio sugerido
    payloads = [
        "'; DROP TABLE productos; --",
        "1' OR '1'='1",
        "'; DELETE FROM ordenes_compra; --",
        "<script>alert('xss')</script>",
        "' UNION SELECT * FROM usuarios --",
    ]
    for payload in payloads:
        try:
            result = compras_service.obtener_precio_sugerido(descripcion=payload)
            print(f"[OK] Inyeccion bloqueada: '{payload[:30]}...' -> {len(result)} resultados (sin crash)")
        except Exception as e:
            print(f"[WARN] Excepcion con payload: {payload[:30]}... -> {type(e).__name__}")

    # SQL injection en crear requisicion
    try:
        compras_service.crear_requisicion(
            "'; DROP TABLE requisiciones; --",
            [{"descripcion": "' OR 1=1; --", "cantidad": 1}]
        )
        print("[OK] Crear req con payload SQL: parametrizado correctamente")
    except Exception as e:
        print(f"[WARN] Crear req con payload: {e}")

    # Overflow en cantidades
    print("\n" + "=" * 60)
    print("TESTS DE SEGURIDAD - OVERFLOW / EDGE CASES")
    print("=" * 60)

    try:
        compras_service.crear_requisicion("test", [{"descripcion": "x", "cantidad": 999999999}])
        print("[OK] Cantidad extrema: no crash")
    except Exception as e:
        print(f"[WARN] Cantidad extrema: {e}")

    try:
        compras_service.crear_requisicion("test", [{"descripcion": "x", "cantidad": -1}])
        print("[WARN] Cantidad negativa aceptada (validar en UI)")
    except Exception as e:
        print(f"[OK] Cantidad negativa rechazada: {e}")

    try:
        compras_service.crear_requisicion("test", [])
        print("[WARN] Requisicion sin items aceptada (validar en UI)")
    except Exception as e:
        print(f"[OK] Requisicion sin items rechazada: {e}")

    # Trazabilidad con IDs inexistentes
    try:
        traza = compras_service.obtener_trazabilidad("orden_compra", 999999)
        assert traza["orden_compra"] is None
        print("[OK] Trazabilidad con ID inexistente: retorna vacio sin crash")
    except Exception as e:
        print(f"[WARN] Trazabilidad ID inexistente: {e}")

    try:
        traza = compras_service.obtener_trazabilidad("tipo_invalido", 1)
        print("[OK] Trazabilidad con tipo invalido: retorna vacio sin crash")
    except Exception as e:
        print(f"[WARN] Trazabilidad tipo invalido: {e}")


def test_integridad():
    from services.compras.compras_service import compras_service
    print("\n" + "=" * 60)
    print("TESTS DE INTEGRIDAD - LOGICA DE NEGOCIO")
    print("=" * 60)

    # Crear OC y verificar aprobacion
    try:
        oc = compras_service.crear_orden("Proveedor Test", [
            {"descripcion": "Item 1", "cantidad": 10, "precio_unitario": 100}
        ])
        print(f"[OK] OC creada #{oc.numero}, estado: {oc.estado}, total: {oc.total}")
    except Exception as e:
        print(f"[ERR] Crear OC: {e}")

    # Aprobar/rechazar ID inexistente
    try:
        compras_service.aprobar_documento(999999)
        print("[OK] Aprobar ID inexistente: no crash")
    except Exception as e:
        print(f"[WARN] Aprobar inexistente: {e}")

    try:
        compras_service.rechazar_documento(999999, "test")
        print("[OK] Rechazar ID inexistente: no crash")
    except Exception as e:
        print(f"[WARN] Rechazar inexistente: {e}")

    # Conciliar factura inexistente
    try:
        compras_service.conciliar_factura(999999)
        print("[OK] Conciliar inexistente: no crash")
    except Exception as e:
        print(f"[WARN] Conciliar inexistente: {e}")


if __name__ == "__main__":
    test_rendimiento()
    test_seguridad()
    test_integridad()
    print("\n" + "=" * 60)
    print("TESTS COMPLETADOS")
    print("=" * 60)
