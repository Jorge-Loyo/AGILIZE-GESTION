"""Tests de rendimiento, seguridad e integridad del modulo de inventario."""
import time
import sys
sys.path.insert(0, '.')


def test_rendimiento():
    from services.inventario import inventario_service
    print("=" * 60)
    print("TESTS DE RENDIMIENTO - MODULO INVENTARIO")
    print("=" * 60)

    tests = [
        ("Listar productos", lambda: inventario_service.listar_productos()),
        ("Listar categorias", lambda: inventario_service.listar_categorias()),
        ("Listar subcategorias", lambda: inventario_service.listar_subcategorias()),
        ("Listar marcas", lambda: inventario_service.listar_marcas()),
        ("Listar UOM", lambda: inventario_service.listar_uom()),
        ("Listar conversiones", lambda: inventario_service.listar_conversiones()),
        ("Listar depositos", lambda: inventario_service.listar_depositos()),
        ("Alertas stock", lambda: inventario_service.alertas_stock()),
        ("Resumen", lambda: inventario_service.resumen()),
        ("Valorizar PPP", lambda: inventario_service.valorizar_inventario("ppp")),
        ("Valorizar FIFO", lambda: inventario_service.valorizar_inventario("fifo")),
        ("Valorizar LIFO", lambda: inventario_service.valorizar_inventario("lifo")),
        ("Lotes por vencer", lambda: inventario_service.lotes_por_vencer(30)),
        ("Lotes vencidos", lambda: inventario_service.lotes_vencidos()),
        ("Series en garantia", lambda: inventario_service.series_en_garantia_activa()),
        ("Transferencias en transito", lambda: inventario_service.listar_transferencias_en_transito()),
        ("Movimientos (100)", lambda: inventario_service.listar_movimientos(limite=100)),
    ]

    for nombre, fn in tests:
        start = time.time()
        try:
            result = fn()
            ms = (time.time() - start) * 1000
            count = len(result) if hasattr(result, '__len__') else (result if isinstance(result, (int, dict)) else "?")
            print(f"[OK] {nombre}: {ms:.0f}ms ({count})")
        except Exception as e:
            print(f"[ERR] {nombre}: {e}")

    # Stock disponible
    prods = inventario_service.listar_productos()
    if prods:
        start = time.time()
        sd = inventario_service.obtener_stock_disponible(prods[0].id)
        print(f"[OK] Stock disponible: {(time.time()-start)*1000:.0f}ms ({sd})")


def test_seguridad():
    from services.inventario import inventario_service
    print("\n" + "=" * 60)
    print("TESTS DE SEGURIDAD - SQL INJECTION")
    print("=" * 60)

    payloads = [
        "'; DROP TABLE productos; --",
        "1' OR '1'='1",
        "'; DELETE FROM stock_deposito; --",
        "<script>alert('xss')</script>",
        "' UNION SELECT * FROM usuarios --",
        "Robert'); DROP TABLE movimientos_stock;--",
    ]

    # Buscar productos con payloads
    for payload in payloads:
        try:
            result = inventario_service.buscar_productos(payload)
            print(f"[OK] buscar_productos: '{payload[:35]}...' -> {len(result)} (sin crash)")
        except Exception as e:
            print(f"[WARN] buscar_productos: {type(e).__name__}")

    # Buscar por codigo de barra con payload
    for payload in payloads[:3]:
        try:
            result = inventario_service.buscar_por_codigo_barra(payload)
            print(f"[OK] buscar_por_codigo_barra: '{payload[:35]}...' -> {result}")
        except Exception as e:
            print(f"[WARN] buscar_por_codigo_barra: {type(e).__name__}")

    # Buscar serie con payload
    for payload in payloads[:3]:
        try:
            result = inventario_service.buscar_serie(payload)
            print(f"[OK] buscar_serie: '{payload[:35]}...' -> {result}")
        except Exception as e:
            print(f"[WARN] buscar_serie: {type(e).__name__}")


def test_validaciones():
    from services.inventario import inventario_service
    print("\n" + "=" * 60)
    print("TESTS DE VALIDACIONES - EDGE CASES")
    print("=" * 60)

    # Entrada con cantidad 0
    try:
        inventario_service.registrar_entrada(1, 1, 0)
        print("[FAIL] Entrada cant=0 aceptada")
    except ValueError as e:
        print(f"[OK] Entrada cant=0 rechazada: {e}")

    # Entrada con cantidad negativa
    try:
        inventario_service.registrar_entrada(1, 1, -5)
        print("[FAIL] Entrada negativa aceptada")
    except ValueError as e:
        print(f"[OK] Entrada negativa rechazada: {e}")

    # Salida con stock insuficiente
    try:
        inventario_service.registrar_salida(1, 1, 999999)
        print("[FAIL] Salida sin stock aceptada")
    except ValueError as e:
        print(f"[OK] Salida sin stock rechazada: {e}")

    # Transferencia mismo deposito
    try:
        inventario_service.registrar_transferencia(1, 1, 1, 5)
        print("[FAIL] Transferencia mismo deposito aceptada")
    except ValueError as e:
        print(f"[OK] Transferencia mismo deposito rechazada: {e}")

    # Consumo interno con cantidad 0
    try:
        inventario_service.registrar_consumo_interno(1, 1, 0)
        print("[FAIL] Consumo cant=0 aceptado")
    except ValueError as e:
        print(f"[OK] Consumo cant=0 rechazado: {e}")

    # Producto servicio no mueve stock
    try:
        # Buscar o simular producto servicio
        from core.database import get_db
        from models.inventario import Producto
        with get_db() as db:
            serv = db.query(Producto).filter(Producto.tipo_articulo == "servicio").first()
            if serv:
                try:
                    inventario_service.registrar_entrada(serv.id, 1, 10)
                    print("[FAIL] Servicio acepto entrada de stock")
                except ValueError as e:
                    print(f"[OK] Servicio no mueve stock: {e}")
            else:
                print("[SKIP] No hay producto tipo servicio para testear")
    except Exception as e:
        print(f"[SKIP] Test servicio: {e}")

    # Valorizar con metodo invalido
    try:
        inventario_service.valorizar_inventario("metodo_falso")
        print("[FAIL] Metodo invalido aceptado")
    except ValueError as e:
        print(f"[OK] Metodo invalido rechazado: {e}")

    # Conversion UOM inexistente
    try:
        inventario_service.convertir_cantidad(10, 999, 998)
        print("[FAIL] Conversion inexistente aceptada")
    except ValueError as e:
        print(f"[OK] Conversion inexistente rechazada: {e}")

    # Kit: agregar a si mismo
    try:
        inventario_service.agregar_componente_kit(1, 1, 5)
        print("[FAIL] Kit autocontenido aceptado")
    except ValueError as e:
        print(f"[OK] Kit autocontenido rechazado: {e}")

    # Confirmar transferencia inexistente
    try:
        inventario_service.confirmar_transferencia(999999)
        print("[FAIL] Confirmar transferencia inexistente aceptada")
    except ValueError as e:
        print(f"[OK] Confirmar transferencia inexistente rechazada: {e}")

    # Cancelar transferencia inexistente
    try:
        inventario_service.cancelar_transferencia(999999)
        print("[FAIL] Cancelar transferencia inexistente aceptada")
    except ValueError as e:
        print(f"[OK] Cancelar transferencia inexistente rechazada: {e}")

    # Vender serie inexistente
    try:
        inventario_service.vender_serie(999999)
        print("[FAIL] Vender serie inexistente aceptada")
    except ValueError as e:
        print(f"[OK] Vender serie inexistente rechazada: {e}")

    # Consumir lote inexistente
    try:
        inventario_service.consumir_lote(999999, 10)
        print("[FAIL] Consumir lote inexistente aceptado")
    except ValueError as e:
        print(f"[OK] Consumir lote inexistente rechazado: {e}")

    # Toma inventario inexistente
    try:
        inventario_service.aplicar_ajustes_toma(999999)
        print("[FAIL] Ajustar toma inexistente aceptada")
    except ValueError as e:
        print(f"[OK] Ajustar toma inexistente rechazada: {e}")

    # Reubicar: origen = destino
    try:
        inventario_service.reubicar_producto(1, 1, 1, 1, 5)
        print("[FAIL] Reubicacion mismo lugar aceptada")
    except ValueError as e:
        print(f"[OK] Reubicacion mismo lugar rechazada: {e}")


def test_integridad():
    from services.inventario import inventario_service
    print("\n" + "=" * 60)
    print("TESTS DE INTEGRIDAD - LOGICA DE NEGOCIO")
    print("=" * 60)

    # Reposicion automatica
    try:
        n = inventario_service.generar_reposicion_automatica()
        print(f"[OK] Reposicion automatica: {n} items generados")
    except Exception as e:
        print(f"[ERR] Reposicion automatica: {e}")

    # Alertas stock
    alertas = inventario_service.alertas_stock()
    tipos = {}
    for a in alertas:
        tipos[a["tipo_alerta"]] = tipos.get(a["tipo_alerta"], 0) + 1
    print(f"[OK] Alertas: {len(alertas)} total - {tipos}")

    # Valorizacion consistente
    ppp = inventario_service.valorizar_inventario("ppp")
    fifo = inventario_service.valorizar_inventario("fifo")
    lifo = inventario_service.valorizar_inventario("lifo")
    print(f"[OK] Valorizacion: PPP=${ppp['total']:,.2f} | FIFO=${fifo['total']:,.2f} | LIFO=${lifo['total']:,.2f}")

    # Resumen
    r = inventario_service.resumen()
    print(f"[OK] Resumen: {r['total_productos']} prods, {r['total_depositos']} deps, stock={r['total_stock']}, valor=${r['valor_inventario']:,.2f}")

    # Stock disponible
    prods = inventario_service.listar_productos()
    if prods:
        sd = inventario_service.obtener_stock_disponible(prods[0].id)
        formula_ok = sd["disponible"] == sd["stock_real"] - sd["comprometido"] + sd["en_camino"]
        print(f"[{'OK' if formula_ok else 'FAIL'}] Formula stock disponible: {sd['stock_real']} - {sd['comprometido']} + {sd['en_camino']} = {sd['disponible']}")


def test_overflow():
    from services.inventario import inventario_service
    print("\n" + "=" * 60)
    print("TESTS DE SEGURIDAD - OVERFLOW / LIMITES")
    print("=" * 60)

    # String extremadamente largo
    try:
        inventario_service.buscar_productos("A" * 10000)
        print("[OK] Busqueda con string 10K chars: no crash")
    except Exception as e:
        print(f"[WARN] String largo: {type(e).__name__}")

    # Producto ID negativo
    try:
        result = inventario_service.obtener_stock_disponible(-1)
        print(f"[OK] Stock disponible ID=-1: retorna sin crash ({result})")
    except Exception as e:
        print(f"[OK] Stock disponible ID=-1: {type(e).__name__}")

    # Listar con limite extremo
    try:
        inventario_service.listar_movimientos(limite=0)
        print("[OK] Limite=0: no crash")
    except Exception as e:
        print(f"[WARN] Limite 0: {e}")

    # Lotes por vencer con dias=0
    try:
        result = inventario_service.lotes_por_vencer(0)
        print(f"[OK] Lotes por vencer dias=0: {len(result)}")
    except Exception as e:
        print(f"[WARN] Lotes dias=0: {e}")


if __name__ == "__main__":
    test_rendimiento()
    test_seguridad()
    test_validaciones()
    test_integridad()
    test_overflow()
    print("\n" + "=" * 60)
    print("TESTS INVENTARIO COMPLETADOS")
    print("=" * 60)
