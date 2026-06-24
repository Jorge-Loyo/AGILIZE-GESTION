"""Sub-servicio: Catalogo (categorias, marcas, UOM, productos, depositos, ubicaciones)."""
from services.inventario._base import *


class CatalogoService:
    # === CATEGORIAS ===
    def listar_categorias(self):
        with get_db() as db:
            return db.query(CategoriaProducto).filter(
                CategoriaProducto.activo.is_(True)
            ).order_by(CategoriaProducto.nombre).all()

    def crear_categoria(self, nombre: str, descripcion: str = "") -> CategoriaProducto:
        with get_db() as db:
            cat = CategoriaProducto(nombre=nombre, descripcion=descripcion)
            db.add(cat)
            db.flush()
            return cat

    # === SUBCATEGORIAS ===
    def listar_subcategorias(self, categoria_id: int = None):
        with get_db() as db:
            q = db.query(SubcategoriaProducto).filter(SubcategoriaProducto.activo.is_(True))
            if categoria_id:
                q = q.filter(SubcategoriaProducto.categoria_id == categoria_id)
            return q.order_by(SubcategoriaProducto.nombre).all()

    def crear_subcategoria(self, categoria_id: int, nombre: str) -> SubcategoriaProducto:
        with get_db() as db:
            sub = SubcategoriaProducto(categoria_id=categoria_id, nombre=nombre)
            db.add(sub)
            db.flush()
            return sub

    # === MARCAS ===
    def listar_marcas(self):
        with get_db() as db:
            return db.query(MarcaProducto).filter(MarcaProducto.activo.is_(True)).order_by(MarcaProducto.nombre).all()

    def crear_marca(self, nombre: str) -> MarcaProducto:
        with get_db() as db:
            marca = MarcaProducto(nombre=nombre)
            db.add(marca)
            db.flush()
            return marca

    # === UNIDADES DE MEDIDA ===
    def listar_uom(self):
        with get_db() as db:
            return db.query(UnidadMedida).filter(UnidadMedida.activo.is_(True)).order_by(UnidadMedida.nombre).all()

    def crear_uom(self, codigo: str, nombre: str) -> UnidadMedida:
        with get_db() as db:
            uom = UnidadMedida(codigo=codigo.upper()[:10], nombre=nombre)
            db.add(uom)
            db.flush()
            return uom

    # === CONVERSIONES UOM ===
    def listar_conversiones(self, producto_id: int = None):
        with get_db() as db:
            q = db.query(ConversionUOM).options(
                joinedload(ConversionUOM.uom_origen), joinedload(ConversionUOM.uom_destino),
            )
            if producto_id:
                q = q.filter(ConversionUOM.producto_id == producto_id)
            return q.all()

    def crear_conversion(self, uom_origen_id: int, uom_destino_id: int, factor: float, producto_id: int = None) -> ConversionUOM:
        with get_db() as db:
            conv = ConversionUOM(producto_id=producto_id, uom_origen_id=uom_origen_id, uom_destino_id=uom_destino_id, factor=factor)
            db.add(conv)
            db.flush()
            return conv

    def convertir_cantidad(self, cantidad: float, uom_origen_id: int, uom_destino_id: int, producto_id: int = None) -> float:
        if uom_origen_id == uom_destino_id:
            return cantidad
        with get_db() as db:
            conv = db.query(ConversionUOM).filter(
                ConversionUOM.uom_origen_id == uom_origen_id, ConversionUOM.uom_destino_id == uom_destino_id, ConversionUOM.producto_id == producto_id,
            ).first() if producto_id else None
            if not conv:
                conv = db.query(ConversionUOM).filter(
                    ConversionUOM.uom_origen_id == uom_origen_id, ConversionUOM.uom_destino_id == uom_destino_id, ConversionUOM.producto_id.is_(None),
                ).first()
            if not conv:
                raise ValueError("No existe conversion entre estas unidades")
            return cantidad * conv.factor

    # === CODIGOS DE BARRA ===
    def listar_codigos_barra(self, producto_id: int):
        with get_db() as db:
            return db.query(CodigoBarraProducto).filter(CodigoBarraProducto.producto_id == producto_id).order_by(CodigoBarraProducto.principal.desc()).all()

    def agregar_codigo_barra(self, producto_id: int, codigo: str, tipo: str = "propio", principal: bool = False) -> CodigoBarraProducto:
        with get_db() as db:
            if principal:
                db.query(CodigoBarraProducto).filter(CodigoBarraProducto.producto_id == producto_id, CodigoBarraProducto.principal.is_(True)).update({"principal": False})
            cb = CodigoBarraProducto(producto_id=producto_id, codigo=codigo[:50], tipo=tipo[:30], principal=principal)
            db.add(cb)
            db.flush()
            return cb

    def eliminar_codigo_barra(self, codigo_id: int):
        with get_db() as db:
            cb = db.get(CodigoBarraProducto, codigo_id)
            if cb:
                db.delete(cb)

    def buscar_por_codigo_barra(self, codigo: str):
        with get_db() as db:
            cb = db.query(CodigoBarraProducto).filter(CodigoBarraProducto.codigo == codigo).first()
            if cb:
                return db.query(Producto).options(joinedload(Producto.categoria), joinedload(Producto.stock_depositos)).get(cb.producto_id)
            return None

    # === KIT / COMBO ===
    def listar_componentes_kit(self, kit_id: int):
        with get_db() as db:
            detalles = db.query(KitDetalle).filter(KitDetalle.kit_id == kit_id).all()
            return [{"id": d.id, "componente_id": d.componente_id, "codigo": (db.get(Producto, d.componente_id) or Producto()).codigo or "", "nombre": (db.get(Producto, d.componente_id) or Producto()).nombre or "", "cantidad": d.cantidad} for d in detalles]

    def agregar_componente_kit(self, kit_id: int, componente_id: int, cantidad: float = 1.0):
        with get_db() as db:
            kit = db.get(Producto, kit_id)
            if not kit or kit.tipo_articulo != "kit":
                raise ValueError("El producto no es un Kit")
            if kit_id == componente_id:
                raise ValueError("Un kit no puede contenerse a si mismo")
            detalle = KitDetalle(kit_id=kit_id, componente_id=componente_id, cantidad=cantidad)
            db.add(detalle)
            db.flush()
            return detalle

    def eliminar_componente_kit(self, detalle_id: int):
        with get_db() as db:
            d = db.get(KitDetalle, detalle_id)
            if d:
                db.delete(d)

    # === PRODUCTOS ===
    def listar_productos(self, solo_activos=True):
        with get_db() as db:
            q = db.query(Producto).options(joinedload(Producto.categoria), joinedload(Producto.subcategoria), joinedload(Producto.marca), joinedload(Producto.stock_depositos))
            if solo_activos:
                q = q.filter(Producto.activo.is_(True))
            return q.order_by(Producto.nombre).all()

    def buscar_productos(self, texto: str):
        with get_db() as db:
            por_barra = db.query(CodigoBarraProducto.producto_id).filter(CodigoBarraProducto.codigo == texto).scalar()
            if por_barra:
                return db.query(Producto).options(joinedload(Producto.categoria), joinedload(Producto.stock_depositos)).filter(Producto.id == por_barra).all()
            return db.query(Producto).options(joinedload(Producto.categoria), joinedload(Producto.stock_depositos)).filter(
                Producto.activo.is_(True), (Producto.nombre.ilike(f"%{texto}%")) | (Producto.codigo.ilike(f"%{texto}%"))
            ).order_by(Producto.nombre).all()

    def obtener_producto(self, producto_id: int):
        with get_db() as db:
            return db.get(Producto, producto_id)

    def crear_producto(self, datos: dict) -> Producto:
        with get_db() as db:
            producto = Producto(**datos)
            db.add(producto)
            db.flush()
            return producto

    def actualizar_producto(self, producto_id: int, datos: dict):
        with get_db() as db:
            producto = db.get(Producto, producto_id)
            if not producto:
                raise ValueError("Producto no encontrado")
            for k, v in datos.items():
                setattr(producto, k, v)

    def desactivar_producto(self, producto_id: int):
        with get_db() as db:
            producto = db.get(Producto, producto_id)
            if producto:
                producto.activo = not producto.activo

    # === DEPOSITOS ===
    def listar_depositos(self, solo_activos=True):
        with get_db() as db:
            q = db.query(Deposito).options(joinedload(Deposito.sucursal))
            if solo_activos:
                q = q.filter(Deposito.activo.is_(True))
            return q.order_by(Deposito.nombre).all()

    def crear_deposito(self, nombre: str, direccion: str = "", sucursal_id: int = None) -> Deposito:
        with get_db() as db:
            deposito = Deposito(nombre=nombre, direccion=direccion, sucursal_id=sucursal_id)
            db.add(deposito)
            db.flush()
            return deposito

    def actualizar_deposito(self, deposito_id: int, datos: dict):
        with get_db() as db:
            deposito = db.get(Deposito, deposito_id)
            if not deposito:
                raise ValueError("Deposito no encontrado")
            for k, v in datos.items():
                setattr(deposito, k, v)

    # === UBICACIONES ===
    def listar_ubicaciones(self, deposito_id: int):
        with get_db() as db:
            return db.query(UbicacionDeposito).filter(UbicacionDeposito.deposito_id == deposito_id, UbicacionDeposito.activo.is_(True)).order_by(UbicacionDeposito.codigo).all()

    def crear_ubicacion(self, deposito_id: int, pasillo: str, estanteria: str, altura: str, descripcion: str = "", capacidad: int = 0) -> UbicacionDeposito:
        codigo = f"{pasillo}-{estanteria}-{altura}".strip("-")
        with get_db() as db:
            ub = UbicacionDeposito(deposito_id=deposito_id, codigo=codigo[:30], pasillo=pasillo[:10], estanteria=estanteria[:10], altura=altura[:10], descripcion=descripcion[:100], capacidad=capacidad)
            db.add(ub)
            db.flush()
            return ub

    def crear_ubicaciones_masivo(self, deposito_id: int, pasillos: list, estantes: int, alturas: int):
        creadas = 0
        with get_db() as db:
            for pasillo in pasillos:
                for est in range(1, estantes + 1):
                    for alt in range(1, alturas + 1):
                        codigo = f"{pasillo}-{est:02d}-{alt}"
                        if not db.query(UbicacionDeposito).filter(UbicacionDeposito.deposito_id == deposito_id, UbicacionDeposito.codigo == codigo).first():
                            db.add(UbicacionDeposito(deposito_id=deposito_id, codigo=codigo, pasillo=pasillo, estanteria=str(est), altura=str(alt)))
                            creadas += 1
        return creadas

    def eliminar_ubicacion(self, ubicacion_id: int):
        with get_db() as db:
            ub = db.get(UbicacionDeposito, ubicacion_id)
            if ub:
                ub.activo = False
