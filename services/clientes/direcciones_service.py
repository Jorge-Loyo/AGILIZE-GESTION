"""Sub-servicio: Direcciones de entrega y contactos."""
from services.clientes._base import *


class DireccionesContactosService:
    def listar_direcciones(self, cliente_id: int):
        with get_db() as db:
            return db.query(DireccionEntregaCliente).filter(
                DireccionEntregaCliente.cliente_id == cliente_id,
                DireccionEntregaCliente.activo.is_(True),
            ).order_by(DireccionEntregaCliente.principal.desc()).all()

    def agregar_direccion(self, cliente_id: int, datos: dict) -> DireccionEntregaCliente:
        with get_db() as db:
            if datos.get("principal"):
                db.query(DireccionEntregaCliente).filter(
                    DireccionEntregaCliente.cliente_id == cliente_id,
                    DireccionEntregaCliente.principal.is_(True),
                ).update({"principal": False})
            dir_ent = DireccionEntregaCliente(cliente_id=cliente_id, **datos)
            db.add(dir_ent)
            db.flush()
            return dir_ent

    def eliminar_direccion(self, direccion_id: int):
        with get_db() as db:
            d = db.get(DireccionEntregaCliente, direccion_id)
            if d:
                d.activo = False

    def listar_contactos(self, cliente_id: int):
        with get_db() as db:
            return db.query(ContactoCliente).filter(
                ContactoCliente.cliente_id == cliente_id,
            ).order_by(ContactoCliente.principal.desc()).all()

    def agregar_contacto(self, cliente_id: int, datos: dict) -> ContactoCliente:
        with get_db() as db:
            if datos.get("principal"):
                db.query(ContactoCliente).filter(
                    ContactoCliente.cliente_id == cliente_id,
                    ContactoCliente.principal.is_(True),
                ).update({"principal": False})
            contacto = ContactoCliente(cliente_id=cliente_id, **datos)
            db.add(contacto)
            db.flush()
            return contacto

    def eliminar_contacto(self, contacto_id: int):
        with get_db() as db:
            c = db.get(ContactoCliente, contacto_id)
            if c:
                db.delete(c)
