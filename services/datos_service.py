"""Servicio de datos: proveedores y clientes."""
from core.database import get_db
from models.datos import Proveedor, Cliente


class DatosService:
    # === PROVEEDORES ===
    def listar_proveedores(self, solo_activos=True):
        with get_db() as db:
            q = db.query(Proveedor)
            if solo_activos:
                q = q.filter(Proveedor.activo == True)
            return q.order_by(Proveedor.razon_social).all()

    def buscar_proveedores(self, texto: str):
        with get_db() as db:
            return db.query(Proveedor).filter(
                Proveedor.activo == True,
                (Proveedor.razon_social.ilike(f"%{texto}%")) |
                (Proveedor.nombre_fantasia.ilike(f"%{texto}%")) |
                (Proveedor.cuit_rif.ilike(f"%{texto}%"))
            ).order_by(Proveedor.razon_social).all()

    def obtener_proveedor(self, proveedor_id: int):
        with get_db() as db:
            return db.get(Proveedor, proveedor_id)

    def crear_proveedor(self, datos: dict) -> Proveedor:
        with get_db() as db:
            prov = Proveedor(**datos)
            db.add(prov)
            db.flush()
            return prov

    def actualizar_proveedor(self, proveedor_id: int, datos: dict):
        with get_db() as db:
            prov = db.get(Proveedor, proveedor_id)
            if not prov:
                raise ValueError("Proveedor no encontrado")
            for k, v in datos.items():
                setattr(prov, k, v)

    def desactivar_proveedor(self, proveedor_id: int):
        with get_db() as db:
            prov = db.get(Proveedor, proveedor_id)
            if prov:
                prov.activo = not prov.activo

    # === CLIENTES ===
    def listar_clientes(self, solo_activos=True):
        with get_db() as db:
            q = db.query(Cliente)
            if solo_activos:
                q = q.filter(Cliente.activo == True)
            return q.order_by(Cliente.razon_social).all()

    def buscar_clientes(self, texto: str):
        with get_db() as db:
            return db.query(Cliente).filter(
                Cliente.activo == True,
                (Cliente.razon_social.ilike(f"%{texto}%")) |
                (Cliente.nombre_fantasia.ilike(f"%{texto}%")) |
                (Cliente.cuit_rif.ilike(f"%{texto}%")) |
                (Cliente.numero_documento.ilike(f"%{texto}%"))
            ).order_by(Cliente.razon_social).all()

    def obtener_cliente(self, cliente_id: int):
        with get_db() as db:
            return db.get(Cliente, cliente_id)

    def crear_cliente(self, datos: dict) -> Cliente:
        with get_db() as db:
            cli = Cliente(**datos)
            db.add(cli)
            db.flush()
            return cli

    def actualizar_cliente(self, cliente_id: int, datos: dict):
        with get_db() as db:
            cli = db.get(Cliente, cliente_id)
            if not cli:
                raise ValueError("Cliente no encontrado")
            for k, v in datos.items():
                setattr(cli, k, v)

    def desactivar_cliente(self, cliente_id: int):
        with get_db() as db:
            cli = db.get(Cliente, cliente_id)
            if cli:
                cli.activo = not cli.activo

    # === RESUMEN ===
    def resumen(self) -> dict:
        with get_db() as db:
            total_proveedores = db.query(Proveedor).filter(Proveedor.activo == True).count()
            total_clientes = db.query(Cliente).filter(Cliente.activo == True).count()
            return {
                "total_proveedores": total_proveedores,
                "total_clientes": total_clientes,
            }


datos_service = DatosService()
