"""Sub-servicio: CRUD clientes."""
from services.clientes._base import *


class CrudClienteService:
    def listar_clientes(self, solo_activos: bool = True, categoria: str = None, cobrador_id: int = None):
        with get_db() as db:
            q = db.query(Cliente)
            if solo_activos:
                q = q.filter(Cliente.activo.is_(True))
            if categoria:
                q = q.filter(Cliente.categoria == categoria)
            if cobrador_id:
                q = q.filter(Cliente.cobrador_id == cobrador_id)
            return q.order_by(Cliente.razon_social).all()

    def buscar_clientes(self, texto: str):
        with get_db() as db:
            return db.query(Cliente).filter(
                Cliente.activo.is_(True),
                (Cliente.razon_social.ilike(f"%{texto}%")) |
                (Cliente.nombre_fantasia.ilike(f"%{texto}%")) |
                (Cliente.cuit_rif.ilike(f"%{texto}%"))
            ).order_by(Cliente.razon_social).all()

    def obtener_cliente(self, cliente_id: int):
        with get_db() as db:
            return db.query(Cliente).options(
                joinedload(Cliente.direcciones_entrega),
                joinedload(Cliente.contactos),
            ).get(cliente_id)

    def crear_cliente(self, datos: dict) -> Cliente:
        with get_db() as db:
            cliente = Cliente(**datos)
            db.add(cliente)
            db.flush()
            return cliente

    def actualizar_cliente(self, cliente_id: int, datos: dict):
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if not cliente:
                raise ValueError("Cliente no encontrado")
            for k, v in datos.items():
                setattr(cliente, k, v)

    def desactivar_cliente(self, cliente_id: int):
        with get_db() as db:
            cliente = db.get(Cliente, cliente_id)
            if cliente:
                cliente.activo = not cliente.activo
