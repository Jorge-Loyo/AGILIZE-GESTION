"""Sub-servicio: Stock (movimientos, transferencias, consumo interno, reubicacion)."""
from services.inventario._base import *
from services.inventario._base import _hoy


class StockService:
    # === STOCK ===
    def obtener_stock(self, producto_id: int, deposito_id: int) -> int:
        with get_db() as db:
            sd = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id).first()
            return sd.cantidad if sd else 0

    def obtener_stock_total(self, producto_id: int) -> int:
        with get_db() as db:
            return db.query(func.sum(StockDeposito.cantidad)).filter(StockDeposito.producto_id == producto_id).scalar() or 0

    def stock_por_deposito(self, deposito_id: int):
        with get_db() as db:
            return db.query(StockDeposito).filter(StockDeposito.deposito_id == deposito_id, StockDeposito.cantidad > 0).all()

    def stock_por_ubicacion(self, deposito_id: int):
        with get_db() as db:
            return db.query(StockDeposito).options(joinedload(StockDeposito.producto), joinedload(StockDeposito.ubicacion)).filter(
                StockDeposito.deposito_id == deposito_id, StockDeposito.cantidad > 0,
            ).order_by(StockDeposito.ubicacion_id).all()

    def productos_bajo_minimo(self):
        with get_db() as db:
            productos = db.query(Producto).filter(Producto.activo.is_(True), Producto.stock_minimo > 0).all()
            resultado = []
            for p in productos:
                total = db.query(func.sum(StockDeposito.cantidad)).filter(StockDeposito.producto_id == p.id).scalar() or 0
                if total < p.stock_minimo:
                    resultado.append({"producto": p, "stock_actual": total, "stock_minimo": p.stock_minimo})
            return resultado

    # === MOVIMIENTOS ===
    def registrar_entrada(self, producto_id: int, deposito_id: int, cantidad: int, motivo: str = "", referencia: str = ""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        with get_db() as db:
            prod = db.get(Producto, producto_id)
            if prod and prod.tipo_articulo == "servicio":
                raise ValueError("Los servicios no mueven stock")
            self._ajustar_stock(db, producto_id, deposito_id, cantidad)
            db.add(MovimientoStock(producto_id=producto_id, deposito_id=deposito_id, tipo="entrada", cantidad=cantidad, motivo=motivo, referencia=referencia, fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))

    def registrar_salida(self, producto_id: int, deposito_id: int, cantidad: int, motivo: str = "", referencia: str = ""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        with get_db() as db:
            prod = db.get(Producto, producto_id)
            if prod and prod.tipo_articulo == "servicio":
                raise ValueError("Los servicios no mueven stock")
            stock_actual = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id).first()
            if not stock_actual or stock_actual.cantidad < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual.cantidad if stock_actual else 0}")
            self._ajustar_stock(db, producto_id, deposito_id, -cantidad)
            db.add(MovimientoStock(producto_id=producto_id, deposito_id=deposito_id, tipo="salida", cantidad=cantidad, motivo=motivo, referencia=referencia, fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))

    def registrar_transferencia(self, producto_id: int, deposito_origen_id: int, deposito_destino_id: int, cantidad: int, motivo: str = "", en_transito: bool = True):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if deposito_origen_id == deposito_destino_id:
            raise ValueError("Origen y destino deben ser diferentes")
        with get_db() as db:
            stock_origen = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_origen_id).first()
            if not stock_origen or stock_origen.cantidad < cantidad:
                raise ValueError(f"Stock insuficiente en origen. Disponible: {stock_origen.cantidad if stock_origen else 0}")
            self._ajustar_stock(db, producto_id, deposito_origen_id, -cantidad)
            tipo = "transferencia_transito" if en_transito else "transferencia"
            if not en_transito:
                self._ajustar_stock(db, producto_id, deposito_destino_id, cantidad)
            mov = MovimientoStock(producto_id=producto_id, deposito_id=deposito_origen_id, deposito_destino_id=deposito_destino_id, tipo=tipo, cantidad=cantidad, motivo=motivo, referencia="en_transito" if en_transito else "completada", fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None)
            db.add(mov)
            db.flush()
            return mov

    def confirmar_transferencia(self, movimiento_id: int):
        with get_db() as db:
            mov = db.get(MovimientoStock, movimiento_id)
            if not mov or mov.tipo != "transferencia_transito":
                raise ValueError("Movimiento no es una transferencia en transito")
            if mov.referencia == "completada":
                raise ValueError("Esta transferencia ya fue confirmada")
            self._ajustar_stock(db, mov.producto_id, mov.deposito_destino_id, mov.cantidad)
            mov.tipo = "transferencia"
            mov.referencia = "completada"
            db.add(MovimientoStock(producto_id=mov.producto_id, deposito_id=mov.deposito_destino_id, tipo="entrada", cantidad=mov.cantidad, motivo=f"Recepcion transferencia #{mov.id}", referencia=f"transf_{mov.id}", fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))

    def cancelar_transferencia(self, movimiento_id: int):
        with get_db() as db:
            mov = db.get(MovimientoStock, movimiento_id)
            if not mov or mov.tipo != "transferencia_transito":
                raise ValueError("Movimiento no es una transferencia en transito")
            if mov.referencia == "completada":
                raise ValueError("Esta transferencia ya fue confirmada")
            self._ajustar_stock(db, mov.producto_id, mov.deposito_id, mov.cantidad)
            mov.tipo = "transferencia_cancelada"
            mov.referencia = "cancelada"

    def listar_transferencias_en_transito(self):
        with get_db() as db:
            return db.query(MovimientoStock).filter(MovimientoStock.tipo == "transferencia_transito", MovimientoStock.referencia == "en_transito").order_by(MovimientoStock.fecha.desc()).all()

    def registrar_consumo_interno(self, producto_id: int, deposito_id: int, cantidad: int, motivo: str = "", departamento: str = ""):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        with get_db() as db:
            prod = db.get(Producto, producto_id)
            if prod and prod.tipo_articulo == "servicio":
                raise ValueError("Los servicios no mueven stock")
            stock_actual = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id).first()
            if not stock_actual or stock_actual.cantidad < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {stock_actual.cantidad if stock_actual else 0}")
            self._ajustar_stock(db, producto_id, deposito_id, -cantidad)
            motivo_final = f"Consumo interno{' - ' + departamento if departamento else ''}{': ' + motivo if motivo else ''}"
            db.add(MovimientoStock(producto_id=producto_id, deposito_id=deposito_id, tipo="consumo_interno", cantidad=cantidad, motivo=motivo_final[:250], referencia=departamento[:100] if departamento else "", fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))

    def registrar_ajuste(self, producto_id: int, deposito_id: int, nueva_cantidad: int, motivo: str = ""):
        with get_db() as db:
            prod = db.get(Producto, producto_id)
            if prod and prod.tipo_articulo == "servicio":
                raise ValueError("Los servicios no mueven stock")
            sd = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id).first()
            cantidad_anterior = sd.cantidad if sd else 0
            diferencia = nueva_cantidad - cantidad_anterior
            if not sd:
                sd = StockDeposito(producto_id=producto_id, deposito_id=deposito_id, cantidad=nueva_cantidad)
                db.add(sd)
            else:
                sd.cantidad = nueva_cantidad
            db.add(MovimientoStock(producto_id=producto_id, deposito_id=deposito_id, tipo="ajuste", cantidad=diferencia, motivo=motivo or f"Ajuste de {cantidad_anterior} a {nueva_cantidad}", fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))

    def reubicar_producto(self, producto_id: int, deposito_id: int, ubicacion_origen_id: int, ubicacion_destino_id: int, cantidad: int):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if ubicacion_origen_id == ubicacion_destino_id:
            raise ValueError("Origen y destino deben ser diferentes")
        with get_db() as db:
            sd_origen = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id, StockDeposito.ubicacion_id == ubicacion_origen_id).first()
            if not sd_origen or sd_origen.cantidad < cantidad:
                raise ValueError("Stock insuficiente en ubicacion origen")
            sd_origen.cantidad -= cantidad
            sd_destino = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id, StockDeposito.ubicacion_id == ubicacion_destino_id).first()
            if not sd_destino:
                sd_destino = StockDeposito(producto_id=producto_id, deposito_id=deposito_id, ubicacion_id=ubicacion_destino_id, cantidad=0)
                db.add(sd_destino)
                db.flush()
            sd_destino.cantidad += cantidad
            db.add(MovimientoStock(producto_id=producto_id, deposito_id=deposito_id, ubicacion_id=ubicacion_origen_id, ubicacion_destino_id=ubicacion_destino_id, tipo="reubicacion", cantidad=cantidad, motivo="Reubicacion interna", fecha=_hoy(), usuario_id=auth_service.current_user.id if auth_service.current_user else None))

    def listar_movimientos(self, producto_id: int = None, deposito_id: int = None, tipo: str = None, limite: int = 100):
        with get_db() as db:
            q = db.query(MovimientoStock)
            if producto_id:
                q = q.filter(MovimientoStock.producto_id == producto_id)
            if deposito_id:
                q = q.filter(MovimientoStock.deposito_id == deposito_id)
            if tipo:
                q = q.filter(MovimientoStock.tipo == tipo)
            return q.order_by(MovimientoStock.created_at.desc()).limit(limite).all()

    def resumen(self) -> dict:
        with get_db() as db:
            return {
                "total_productos": db.query(Producto).filter(Producto.activo.is_(True)).count(),
                "total_depositos": db.query(Deposito).filter(Deposito.activo.is_(True)).count(),
                "total_stock": int(db.query(func.sum(StockDeposito.cantidad)).scalar() or 0),
                "valor_inventario": float(db.query(func.sum(StockDeposito.cantidad * Producto.precio_costo)).join(Producto).scalar() or 0),
                "movimientos_hoy": db.query(MovimientoStock).filter(MovimientoStock.fecha == _hoy()).count(),
            }

    @staticmethod
    def _ajustar_stock(db, producto_id: int, deposito_id: int, cantidad: int):
        sd = db.query(StockDeposito).filter(StockDeposito.producto_id == producto_id, StockDeposito.deposito_id == deposito_id).first()
        if not sd:
            sd = StockDeposito(producto_id=producto_id, deposito_id=deposito_id, cantidad=0)
            db.add(sd)
            db.flush()
        sd.cantidad += cantidad
