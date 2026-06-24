"""Servicio de reclutamiento y seleccion."""
from datetime import date, datetime, timezone
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.reclutamiento import Vacante, Candidato
from models import sucursal, usuario, empleado, rol, permiso  # noqa
from services.core.auth_service import auth_service


def _hoy() -> date:
    return datetime.now(timezone.utc).date()


class ReclutamientoService:
    # === VACANTES ===
    def crear_vacante(self, datos: dict) -> Vacante:
        with get_db() as db:
            datos["fecha_publicacion"] = _hoy()
            datos["responsable_id"] = auth_service.current_user.id if auth_service.current_user else None
            vacante = Vacante(**datos)
            db.add(vacante)
            db.flush()
            return vacante

    def listar_vacantes(self, estado: str = None):
        with get_db() as db:
            q = db.query(Vacante)
            if estado:
                q = q.filter(Vacante.estado == estado)
            return q.order_by(Vacante.created_at.desc()).all()

    def cerrar_vacante(self, vacante_id: int):
        with get_db() as db:
            v = db.get(Vacante, vacante_id)
            if v:
                v.estado = "cerrada"
                v.fecha_cierre = _hoy()

    # === CANDIDATOS ===
    def agregar_candidato(self, vacante_id: int, datos: dict) -> Candidato:
        with get_db() as db:
            datos["vacante_id"] = vacante_id
            datos["fecha_postulacion"] = _hoy()
            candidato = Candidato(**datos)
            db.add(candidato)
            db.flush()
            return candidato

    def listar_candidatos(self, vacante_id: int, estado: str = None):
        with get_db() as db:
            q = db.query(Candidato).filter(Candidato.vacante_id == vacante_id)
            if estado:
                q = q.filter(Candidato.estado == estado)
            return q.order_by(Candidato.puntaje.desc()).all()

    def cambiar_estado_candidato(self, candidato_id: int, estado: str, notas: str = ""):
        with get_db() as db:
            c = db.get(Candidato, candidato_id)
            if not c:
                return
            c.estado = estado
            if notas:
                c.notas = (c.notas + "\n" + notas).strip()[:2000]
            if estado == "entrevista":
                c.fecha_entrevista = _hoy()
            elif estado == "rechazado" and notas:
                c.motivo_rechazo = notas[:200]

    def contratar_candidato(self, candidato_id: int) -> dict:
        """Marca como contratado y retorna datos para crear empleado."""
        with get_db() as db:
            c = db.get(Candidato, candidato_id)
            if not c:
                raise ValueError("Candidato no encontrado")
            c.estado = "contratado"
            vacante = db.get(Vacante, c.vacante_id)
            return {
                "nombre": c.nombre.split(" ")[0] if c.nombre else "",
                "apellido": " ".join(c.nombre.split(" ")[1:]) if c.nombre else "",
                "email": c.email,
                "telefono": c.telefono,
                "dni": c.documento,
                "departamento_id": vacante.departamento_id if vacante else None,
                "cargo_id": vacante.cargo_id if vacante else None,
                "sucursal_id": vacante.sucursal_id if vacante else None,
                "tipo_contrato": vacante.tipo_contrato if vacante else "indefinido",
            }

    def resumen(self) -> dict:
        with get_db() as db:
            vacantes_abiertas = db.query(Vacante).filter(Vacante.estado == "abierta").count()
            total_candidatos = db.query(Candidato).filter(Candidato.estado == "postulado").count()
            en_entrevista = db.query(Candidato).filter(Candidato.estado == "entrevista").count()
            contratados_mes = db.query(Candidato).filter(
                Candidato.estado == "contratado",
                Candidato.updated_at >= datetime.now(timezone.utc).replace(day=1),
            ).count()
            return {
                "vacantes_abiertas": vacantes_abiertas,
                "candidatos_pendientes": total_candidatos,
                "en_entrevista": en_entrevista,
                "contratados_mes": contratados_mes,
            }


reclutamiento_service = ReclutamientoService()
