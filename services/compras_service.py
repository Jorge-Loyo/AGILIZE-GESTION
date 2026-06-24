"""Servicio de compras: ordenes de compra, requisiciones, recepciones, facturas."""
from datetime import date, timezone, datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.comercial import OrdenCompra, OrdenCompraDetalle
from models.datos import Proveedor  # noqa: asegurar registro del mapper
from models.compras import (
    Requisicion, RequisicionDetalle,
    RecepcionCompra, RecepcionDetalle,
    FacturaCompra, FacturaCompraDetalle,
    ListaPrecioProveedor, ListaPrecioDetalle,
    CotizacionCompra, CotizacionCompraDetalle,
    ReglaAprobacion, AprobacionCompra,
)
from services.auth_service import auth_service
from services.empresa_service import empresa_service


def _hoy() -> date:
    """Retorna fecha actual timezone-aware."""
    return datetime.now(timezone.utc).date()


def _usuario_id() -> int | None:
    return auth_service.current_user.id if auth_service.current_user else None


def _sanitize(value: str, max_len: int) -> str:
    """Trunca y limpia string para prevenir inyeccion."""
    if not value:
        return ""
    # Eliminar caracteres de control
    cleaned = "".join(c for c in str(value) if c.isprintable() or c in ("\n", "\t"))
    return cleaned[:max_len]


class ComprasService:
    def _get_iva(self) -> float:
        pais = empresa_service.obtener("cotizacion_pais") or "Venezuela"
        return 16.0 if pais == "Venezuela" else 21.0

    # === REQUISICIONES ===
    def crear_requisicion(self, solicitante: str, items: list) -> Requisicion:
        if not items:
            raise ValueError("Debe incluir al menos un item")
        solicitante = _sanitize(solicitante, 150)
        with get_db() as db:
            ultimo = db.query(func.max(Requisicion.numero)).scalar() or 0
            req = Requisicion(
                numero=ultimo + 1, fecha=_hoy(), solicitante=solicitante,
                usuario_id=_usuario_id(),
            )
            db.add(req)
            db.flush()
            for item in items:
                cantidad = max(0.01, float(item.get("cantidad", 1)))
                db.add(RequisicionDetalle(
                    requisicion_id=req.id,
                    descripcion=_sanitize(item["descripcion"], 250),
                    cantidad=cantidad,
                ))
            return req

    def listar_requisiciones(self, limite: int = 100):
        with get_db() as db:
            return db.query(Requisicion).order_by(Requisicion.fecha.desc(), Requisicion.id.desc()).limit(limite).all()

    def cambiar_estado_requisicion(self, req_id: int, estado: str):
        with get_db() as db:
            r = db.get(Requisicion, req_id)
            if r:
                r.estado = estado

    def generar_oc_desde_requisicion(self, req_id: int):
        with get_db() as db:
            req = db.get(Requisicion, req_id)
            if not req:
                raise ValueError("Requisicion no encontrada")
            detalles = db.query(RequisicionDetalle).filter(RequisicionDetalle.requisicion_id == req_id).all()
            items = [{"descripcion": d.descripcion, "cantidad": d.cantidad, "precio_unitario": 0} for d in detalles]
        self.crear_orden(req.solicitante, items)

    # === ORDENES DE COMPRA ===
    def crear_orden(self, proveedor_nombre: str, items: list, proveedor_id: int = None,
                    observaciones: str = "") -> OrdenCompra:
        if not items:
            raise ValueError("Debe incluir al menos un item")
        proveedor_nombre = _sanitize(proveedor_nombre, 200)
        observaciones = _sanitize(observaciones, 500)
        with get_db() as db:
            ultimo = db.query(func.max(OrdenCompra.numero)).scalar() or 0
            subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in items)
            iva_pct = self._get_iva()
            impuesto = round(subtotal * iva_pct / 100, 2)
            total = subtotal + impuesto
            orden = OrdenCompra(
                numero=ultimo + 1, fecha=_hoy(),
                proveedor_id=proveedor_id, proveedor_nombre=proveedor_nombre,
                subtotal=subtotal, impuesto=impuesto, total=total,
                observaciones=observaciones,
                usuario_id=_usuario_id(),
            )
            db.add(orden)
            db.flush()
            for item in items:
                db.add(OrdenCompraDetalle(
                    orden_id=orden.id,
                    descripcion=_sanitize(item["descripcion"], 250),
                    cantidad=item["cantidad"], precio_unitario=item["precio_unitario"],
                    subtotal=round(item["cantidad"] * item["precio_unitario"], 2),
                ))
            db.flush()
            self._check_aprobacion_oc(db, orden)
            return orden

    def _check_aprobacion_oc(self, db, orden: OrdenCompra):
        """Revisa reglas y crea aprobacion pendiente si aplica."""
        reglas = db.query(ReglaAprobacion).filter(
            ReglaAprobacion.activo.is_(True),
            ReglaAprobacion.documento == "orden_compra",
        ).all()
        for regla in reglas:
            if not self._regla_aplica(regla, orden.total):
                continue
            aprob = AprobacionCompra(
                regla_id=regla.id,
                documento_tipo="orden_compra",
                documento_id=orden.id,
                documento_numero=orden.numero,
                monto=orden.total,
                solicitante_id=_usuario_id(),
                aprobador_id=regla.aprobador_usuario_id,
            )
            db.add(aprob)
            orden.estado = "pendiente_aprobacion"
            break

    def _regla_aplica(self, regla: ReglaAprobacion, monto: float) -> bool:
        if regla.condicion == "siempre":
            return True
        if regla.condicion == "monto_mayor" and monto > regla.valor_condicion:
            return True
        return False

    def listar_ordenes(self, limite: int = 100):
        with get_db() as db:
            return db.query(OrdenCompra).order_by(OrdenCompra.fecha.desc(), OrdenCompra.id.desc()).limit(limite).all()

    def cambiar_estado(self, orden_id: int, estado: str):
        with get_db() as db:
            o = db.get(OrdenCompra, orden_id)
            if o:
                o.estado = estado

    # === RECEPCION ===
    def registrar_recepcion(self, orden_compra_id: int, remito_proveedor: str = "") -> RecepcionCompra:
        with get_db() as db:
            oc = db.get(OrdenCompra, orden_compra_id)
            if not oc:
                raise ValueError("Orden de compra no encontrada")

            ultimo = db.query(func.max(RecepcionCompra.numero)).scalar() or 0
            recepcion = RecepcionCompra(
                numero=ultimo + 1, fecha=_hoy(),
                orden_compra_id=orden_compra_id,
                proveedor_nombre=oc.proveedor_nombre,
                remito_proveedor=remito_proveedor,
                usuario_id=_usuario_id(),
            )
            db.add(recepcion)
            db.flush()

            detalles_oc = db.query(OrdenCompraDetalle).filter(OrdenCompraDetalle.orden_id == orden_compra_id).all()
            for d in detalles_oc:
                db.add(RecepcionDetalle(
                    recepcion_id=recepcion.id, descripcion=d.descripcion,
                    cantidad_esperada=d.cantidad, cantidad_recibida=d.cantidad,
                    precio_unitario=d.precio_unitario,
                ))

            oc.estado = "recibida"
            return recepcion

    def listar_recepciones(self, limite: int = 100):
        with get_db() as db:
            return db.query(RecepcionCompra).order_by(RecepcionCompra.fecha.desc(), RecepcionCompra.id.desc()).limit(limite).all()

    # === FACTURAS DE COMPRA ===
    def registrar_factura_compra(self, numero_factura: str, proveedor_nombre: str, total: float,
                                  fecha_vencimiento=None, orden_compra_id: int = None) -> FacturaCompra:
        numero_factura = _sanitize(numero_factura, 50)
        proveedor_nombre = _sanitize(proveedor_nombre, 200)
        with get_db() as db:
            iva_pct = self._get_iva()
            subtotal = round(total / (1 + iva_pct / 100), 2)
            impuesto = total - subtotal

            factura = FacturaCompra(
                numero_factura=numero_factura, fecha=_hoy(),
                fecha_vencimiento=fecha_vencimiento,
                proveedor_nombre=proveedor_nombre,
                orden_compra_id=orden_compra_id,
                subtotal=subtotal, impuesto_porcentaje=iva_pct,
                impuesto_monto=impuesto, total=total,
                usuario_id=_usuario_id(),
            )
            db.add(factura)
            db.flush()
            return factura

    def listar_facturas_compra(self, limite: int = 100):
        with get_db() as db:
            return db.query(FacturaCompra).order_by(FacturaCompra.fecha.desc(), FacturaCompra.id.desc()).limit(limite).all()

    def conciliar_factura(self, factura_id: int):
        """Three-Way Match: verifica OC + Recepcion + Factura."""
        with get_db() as db:
            f = db.get(FacturaCompra, factura_id)
            if f:
                f.conciliada = True

    def cambiar_estado_factura(self, factura_id: int, estado: str):
        with get_db() as db:
            f = db.get(FacturaCompra, factura_id)
            if f:
                f.estado = estado

    # === LISTAS DE PRECIOS ===
    def crear_lista_precio(self, proveedor_id: int, nombre: str, moneda: str = "USD", items: list = None) -> ListaPrecioProveedor:
        with get_db() as db:
            lista = ListaPrecioProveedor(
                proveedor_id=proveedor_id, nombre=nombre,
                fecha=_hoy(), moneda=moneda,
            )
            db.add(lista)
            db.flush()
            if items:
                for item in items:
                    precio = item.get("precio_unitario", 0)
                    desc = item.get("descuento", 0)
                    neto = round(precio * (1 - desc / 100), 2) if desc else precio
                    db.add(ListaPrecioDetalle(
                        lista_id=lista.id,
                        producto_id=item.get("producto_id"),
                        codigo_proveedor=item.get("codigo_proveedor", ""),
                        descripcion=item.get("descripcion", ""),
                        precio_unitario=precio,
                        descuento=desc,
                        precio_neto=neto,
                    ))
            return lista

    def listar_listas_precio(self, proveedor_id: int = None):
        with get_db() as db:
            q = db.query(ListaPrecioProveedor).options(joinedload(ListaPrecioProveedor.proveedor))
            if proveedor_id:
                q = q.filter(ListaPrecioProveedor.proveedor_id == proveedor_id)
            return q.order_by(ListaPrecioProveedor.fecha.desc()).all()

    def obtener_lista_detalles(self, lista_id: int):
        with get_db() as db:
            return db.query(ListaPrecioDetalle).filter(ListaPrecioDetalle.lista_id == lista_id).all()

    def eliminar_lista_precio(self, lista_id: int):
        with get_db() as db:
            lista = db.get(ListaPrecioProveedor, lista_id)
            if lista:
                db.delete(lista)

    def obtener_precio_sugerido(self, producto_id: int = None, descripcion: str = "") -> list:
        """Busca precio en listas vigentes. Retorna lista de {proveedor, precio, moneda}."""
        with get_db() as db:
            q = db.query(ListaPrecioDetalle).join(ListaPrecioProveedor).options(
                joinedload(ListaPrecioDetalle.lista).joinedload(ListaPrecioProveedor.proveedor)
            ).filter(ListaPrecioProveedor.vigente.is_(True))
            if producto_id:
                q = q.filter(ListaPrecioDetalle.producto_id == producto_id)
            elif descripcion:
                q = q.filter(ListaPrecioDetalle.descripcion.ilike(f"%{descripcion}%"))
            else:
                return []
            resultados = []
            for d in q.all():
                resultados.append({
                    "proveedor": d.lista.proveedor.razon_social if d.lista.proveedor else "",
                    "proveedor_id": d.lista.proveedor_id,
                    "precio": d.precio_neto or d.precio_unitario,
                    "moneda": d.lista.moneda,
                    "lista": d.lista.nombre,
                })
            return resultados

    # === COTIZACIONES / SOURCING ===
    def crear_cotizacion(self, descripcion: str, items: list = None, requisicion_id: int = None) -> CotizacionCompra:
        with get_db() as db:
            ultimo = db.query(func.max(CotizacionCompra.numero)).scalar() or 0
            cot = CotizacionCompra(
                numero=ultimo + 1, fecha=_hoy(),
                descripcion=descripcion,
                requisicion_id=requisicion_id,
                usuario_id=_usuario_id(),
            )
            db.add(cot)
            db.flush()
            if items:
                for item in items:
                    db.add(CotizacionCompraDetalle(
                        cotizacion_id=cot.id,
                        proveedor_id=item["proveedor_id"],
                        descripcion=item["descripcion"],
                        cantidad=item.get("cantidad", 1),
                        precio_unitario=item.get("precio_unitario", 0),
                        plazo_entrega=item.get("plazo_entrega", ""),
                        condicion_pago=item.get("condicion_pago", ""),
                    ))
            return cot

    def listar_cotizaciones(self, limite: int = 100):
        with get_db() as db:
            return db.query(CotizacionCompra).order_by(CotizacionCompra.fecha.desc()).limit(limite).all()

    def obtener_cotizacion_detalles(self, cotizacion_id: int):
        with get_db() as db:
            detalles = db.query(CotizacionCompraDetalle).filter(
                CotizacionCompraDetalle.cotizacion_id == cotizacion_id
            ).all()
            result = []
            for d in detalles:
                prov = db.get(Proveedor, d.proveedor_id)
                result.append({
                    "id": d.id, "proveedor": prov.razon_social if prov else "",
                    "proveedor_id": d.proveedor_id, "descripcion": d.descripcion,
                    "cantidad": d.cantidad, "precio_unitario": d.precio_unitario,
                    "total": d.cantidad * d.precio_unitario,
                    "plazo_entrega": d.plazo_entrega, "condicion_pago": d.condicion_pago,
                    "seleccionado": d.seleccionado,
                })
            return result

    def adjudicar_cotizacion(self, cotizacion_id: int, proveedor_id: int):
        """Marca proveedor ganador y cierra cotizacion."""
        with get_db() as db:
            cot = db.get(CotizacionCompra, cotizacion_id)
            if cot:
                cot.proveedor_adjudicado_id = proveedor_id
                cot.estado = "adjudicada"
                db.query(CotizacionCompraDetalle).filter(
                    CotizacionCompraDetalle.cotizacion_id == cotizacion_id,
                    CotizacionCompraDetalle.proveedor_id == proveedor_id,
                ).update({"seleccionado": True})

    def generar_oc_desde_cotizacion(self, cotizacion_id: int):
        """Genera OC con los items adjudicados de la cotizacion."""
        with get_db() as db:
            cot = db.get(CotizacionCompra, cotizacion_id)
            if not cot or not cot.proveedor_adjudicado_id:
                raise ValueError("Cotizacion sin proveedor adjudicado")
            prov = db.get(Proveedor, cot.proveedor_adjudicado_id)
            detalles = db.query(CotizacionCompraDetalle).filter(
                CotizacionCompraDetalle.cotizacion_id == cotizacion_id,
                CotizacionCompraDetalle.seleccionado.is_(True),
            ).all()
            items = [{"descripcion": d.descripcion, "cantidad": d.cantidad, "precio_unitario": d.precio_unitario} for d in detalles]
        self.crear_orden(prov.razon_social if prov else "", items, proveedor_id=cot.proveedor_adjudicado_id)

    # === APROBACIONES ===
    def verificar_aprobacion_requerida(self, documento_tipo: str, documento_id: int, monto: float) -> bool:
        """Verifica si el documento requiere aprobacion segun reglas activas."""
        with get_db() as db:
            reglas = db.query(ReglaAprobacion).filter(
                ReglaAprobacion.activo.is_(True),
                ReglaAprobacion.documento == documento_tipo,
            ).all()
            for regla in reglas:
                if not self._regla_aplica(regla, monto):
                    continue
                doc_numero = self._obtener_numero_documento(db, documento_tipo, documento_id)
                aprob = AprobacionCompra(
                    regla_id=regla.id,
                    documento_tipo=documento_tipo,
                    documento_id=documento_id,
                    documento_numero=doc_numero,
                    monto=monto,
                    solicitante_id=_usuario_id(),
                    aprobador_id=regla.aprobador_usuario_id,
                )
                db.add(aprob)
                if documento_tipo == "orden_compra":
                    oc = db.get(OrdenCompra, documento_id)
                    if oc:
                        oc.estado = "pendiente_aprobacion"
                return True
            return False

    def _obtener_numero_documento(self, db, tipo: str, doc_id: int) -> int:
        if tipo == "orden_compra":
            oc = db.get(OrdenCompra, doc_id)
            return oc.numero if oc else 0
        if tipo == "requisicion":
            req = db.get(Requisicion, doc_id)
            return req.numero if req else 0
        return 0

    def listar_aprobaciones_pendientes(self, usuario_id: int = None):
        with get_db() as db:
            q = db.query(AprobacionCompra).filter(AprobacionCompra.estado == "pendiente")
            if usuario_id:
                q = q.filter(AprobacionCompra.aprobador_id == usuario_id)
            return q.order_by(AprobacionCompra.created_at.desc()).all()

    def listar_aprobaciones(self, limite: int = 100):
        with get_db() as db:
            return db.query(AprobacionCompra).order_by(AprobacionCompra.created_at.desc()).limit(limite).all()

    def aprobar_documento(self, aprobacion_id: int, comentario: str = ""):
        with get_db() as db:
            a = db.get(AprobacionCompra, aprobacion_id)
            if not a:
                return
            a.estado = "aprobada"
            a.fecha_respuesta = _hoy()
            a.comentario = comentario
            a.aprobador_id = _usuario_id() or a.aprobador_id
            if a.documento_tipo == "orden_compra":
                oc = db.get(OrdenCompra, a.documento_id)
                if oc:
                    oc.estado = "pendiente"

    def rechazar_documento(self, aprobacion_id: int, comentario: str = ""):
        with get_db() as db:
            a = db.get(AprobacionCompra, aprobacion_id)
            if not a:
                return
            a.estado = "rechazada"
            a.fecha_respuesta = _hoy()
            a.comentario = comentario
            a.aprobador_id = _usuario_id() or a.aprobador_id
            if a.documento_tipo == "orden_compra":
                oc = db.get(OrdenCompra, a.documento_id)
                if oc:
                    oc.estado = "rechazada"

    # Reglas CRUD
    def listar_reglas_aprobacion(self):
        with get_db() as db:
            return db.query(ReglaAprobacion).order_by(ReglaAprobacion.id).all()

    def crear_regla_aprobacion(self, datos: dict) -> ReglaAprobacion:
        with get_db() as db:
            regla = ReglaAprobacion(**datos)
            db.add(regla)
            db.flush()
            return regla

    def eliminar_regla_aprobacion(self, regla_id: int):
        with get_db() as db:
            r = db.get(ReglaAprobacion, regla_id)
            if r:
                db.delete(r)

    # === TRAZABILIDAD ===
    def obtener_trazabilidad(self, documento_tipo: str, documento_id: int) -> dict:
        """Retorna la cadena completa de trazabilidad de un documento."""
        traza = {"requisicion": None, "orden_compra": None, "recepcion": None, "factura": None, "aprobaciones": []}
        with get_db() as db:
            if documento_tipo == "factura_compra":
                self._traza_desde_factura(db, documento_id, traza)
            elif documento_tipo == "orden_compra":
                self._traza_desde_oc(db, documento_id, traza)
            elif documento_tipo == "recepcion":
                self._traza_desde_recepcion(db, documento_id, traza)
            self._traza_aprobaciones(db, documento_tipo, documento_id, traza)
        return traza

    def _traza_desde_factura(self, db, doc_id: int, traza: dict):
        fact = db.get(FacturaCompra, doc_id)
        if not fact:
            return
        traza["factura"] = {
            "id": fact.id, "numero": fact.numero_factura,
            "fecha": fact.fecha, "proveedor": fact.proveedor_nombre,
            "total": fact.total, "estado": fact.estado,
        }
        if fact.recepcion_id:
            rec = db.get(RecepcionCompra, fact.recepcion_id)
            if rec:
                traza["recepcion"] = {
                    "id": rec.id, "numero": rec.numero, "fecha": rec.fecha,
                    "remito": rec.remito_proveedor, "orden_compra_id": rec.orden_compra_id,
                }
        oc_id = fact.orden_compra_id
        if not oc_id and traza["recepcion"]:
            oc_id = traza["recepcion"]["orden_compra_id"]
        if oc_id:
            self._traza_oc(db, oc_id, traza)

    def _traza_desde_oc(self, db, doc_id: int, traza: dict):
        self._traza_oc(db, doc_id, traza)
        if not traza["orden_compra"]:
            return
        rec = db.query(RecepcionCompra).filter(RecepcionCompra.orden_compra_id == doc_id).first()
        if rec:
            traza["recepcion"] = {"id": rec.id, "numero": rec.numero, "fecha": rec.fecha, "remito": rec.remito_proveedor}
        fact = db.query(FacturaCompra).filter(FacturaCompra.orden_compra_id == doc_id).first()
        if fact:
            traza["factura"] = {"id": fact.id, "numero": fact.numero_factura, "fecha": fact.fecha, "total": fact.total, "estado": fact.estado}

    def _traza_desde_recepcion(self, db, doc_id: int, traza: dict):
        rec = db.get(RecepcionCompra, doc_id)
        if not rec:
            return
        traza["recepcion"] = {
            "id": rec.id, "numero": rec.numero, "fecha": rec.fecha,
            "remito": rec.remito_proveedor, "orden_compra_id": rec.orden_compra_id,
        }
        if rec.orden_compra_id:
            self._traza_oc(db, rec.orden_compra_id, traza)
        fact = db.query(FacturaCompra).filter(FacturaCompra.recepcion_id == rec.id).first()
        if fact:
            traza["factura"] = {"id": fact.id, "numero": fact.numero_factura, "fecha": fact.fecha, "total": fact.total, "estado": fact.estado}

    def _traza_oc(self, db, oc_id: int, traza: dict):
        from models.usuario import Usuario
        oc = db.get(OrdenCompra, oc_id)
        if not oc:
            return
        solicitante = ""
        if oc.usuario_id:
            u = db.get(Usuario, oc.usuario_id)
            solicitante = u.nombre_completo if u else ""
        traza["orden_compra"] = {
            "id": oc.id, "numero": oc.numero, "fecha": oc.fecha,
            "proveedor": oc.proveedor_nombre, "total": oc.total,
            "estado": oc.estado, "solicitante": solicitante,
        }

    def _traza_aprobaciones(self, db, doc_tipo: str, doc_id: int, traza: dict):
        from models.usuario import Usuario
        aprobs = db.query(AprobacionCompra).filter(
            AprobacionCompra.documento_tipo == doc_tipo,
            AprobacionCompra.documento_id == doc_id,
        ).all()
        for a in aprobs:
            aprobador = ""
            if a.aprobador_id:
                u = db.get(Usuario, a.aprobador_id)
                aprobador = u.nombre_completo if u else ""
            traza["aprobaciones"].append({
                "estado": a.estado, "aprobador": aprobador,
                "fecha": a.fecha_respuesta, "comentario": a.comentario,
            })


compras_service = ComprasService()
