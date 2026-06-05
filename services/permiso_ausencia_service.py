from datetime import date
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.permiso_empleado import TipoPermiso, PermisoEmpleado, Ausencia


class PermisoAusenciaService:
    # === Tipos de Permiso ===
    def listar_tipos(self) -> list[TipoPermiso]:
        with get_db() as db:
            return db.query(TipoPermiso).filter(TipoPermiso.activo == True).order_by(TipoPermiso.nombre).all()

    def crear_tipo(self, nombre: str, con_goce: bool, dias_max: int | None) -> TipoPermiso:
        with get_db() as db:
            tipo = TipoPermiso(nombre=nombre, con_goce=con_goce, dias_max=dias_max)
            db.add(tipo)
            db.flush()
            db.refresh(tipo)
            return tipo

    # === Permisos ===
    def listar_permisos(self, empleado_id: int | None = None) -> list[PermisoEmpleado]:
        with get_db() as db:
            query = db.query(PermisoEmpleado).options(
                joinedload(PermisoEmpleado.empleado),
                joinedload(PermisoEmpleado.tipo_permiso),
            )
            if empleado_id:
                query = query.filter(PermisoEmpleado.empleado_id == empleado_id)
            return query.order_by(PermisoEmpleado.fecha_desde.desc()).all()

    def crear_permiso(self, empleado_id: int, tipo_id: int, fecha_desde: date, fecha_hasta: date, motivo: str = "") -> PermisoEmpleado:
        dias = (fecha_hasta - fecha_desde).days + 1
        with get_db() as db:
            permiso = PermisoEmpleado(
                empleado_id=empleado_id,
                tipo_permiso_id=tipo_id,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                dias=dias,
                motivo=motivo,
            )
            db.add(permiso)
            db.flush()
            db.refresh(permiso)
            return permiso

    # === Ausencias ===
    def listar_ausencias(self, periodo: str = "", empleado_id: int | None = None) -> list[Ausencia]:
        with get_db() as db:
            query = db.query(Ausencia).options(joinedload(Ausencia.empleado))
            if periodo:
                query = query.filter(Ausencia.periodo == periodo)
            if empleado_id:
                query = query.filter(Ausencia.empleado_id == empleado_id)
            return query.order_by(Ausencia.fecha.desc()).all()

    def registrar_ausencia(self, empleado_id: int, fecha: date, justificada: bool, motivo: str = "") -> Ausencia:
        periodo = fecha.strftime("%Y-%m")
        with get_db() as db:
            ausencia = Ausencia(
                empleado_id=empleado_id,
                fecha=fecha,
                justificada=justificada,
                motivo=motivo,
                periodo=periodo,
            )
            db.add(ausencia)
            db.flush()
            db.refresh(ausencia)
            return ausencia


permiso_ausencia_service = PermisoAusenciaService()
