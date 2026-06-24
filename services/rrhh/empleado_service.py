from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from core.database import get_db
from models.empleado import Empleado, Departamento, Cargo, LegajoEvento
from models.sucursal import Sucursal
from datetime import date, datetime, timezone


class EmpleadoService:
    def listar(self, busqueda: str = "", solo_activos: bool = True) -> list[Empleado]:
        with get_db() as db:
            query = db.query(Empleado).options(joinedload(Empleado.departamento), joinedload(Empleado.cargo), joinedload(Empleado.sucursal))
            if solo_activos:
                query = query.filter(Empleado.activo == True)
            if busqueda:
                filtro = f"%{busqueda}%"
                query = query.filter(
                    or_(
                        Empleado.nombre.ilike(filtro),
                        Empleado.apellido.ilike(filtro),
                        Empleado.dni.ilike(filtro),
                        Empleado.cuil.ilike(filtro),
                    )
                )
            return query.order_by(Empleado.apellido, Empleado.nombre).all()

    def obtener(self, empleado_id: int) -> Empleado | None:
        with get_db() as db:
            return db.get(
                Empleado, empleado_id,
                options=[joinedload(Empleado.departamento), joinedload(Empleado.cargo), joinedload(Empleado.sucursal)]
            )

    def crear(self, datos: dict) -> Empleado:
        with get_db() as db:
            # Generar legajo si no tiene
            if not datos.get("legajo"):
                count = db.query(Empleado).count()
                datos["legajo"] = str(count + 1)
            empleado = Empleado(**datos)
            db.add(empleado)
            db.flush()
            db.refresh(empleado)
        from services.core.audit_service import registrar_auditoria
        registrar_auditoria("CREATE", "empleados", empleado.id, f"{empleado.apellido}, {empleado.nombre}")
        return empleado

    def actualizar(self, empleado_id: int, datos: dict) -> Empleado | None:
        with get_db() as db:
            empleado = db.get(Empleado, empleado_id)
            if not empleado:
                return None
            # Registrar cambios salariales en histórico
            from models.historico_sueldo import HistoricoSueldo
            from decimal import Decimal
            campos_sueldo = ("valor_hora", "valor_hora_extra", "sueldo_mensual")
            for campo in campos_sueldo:
                if campo in datos:
                    anterior = getattr(empleado, campo) or Decimal("0")
                    nuevo = datos[campo] if datos[campo] else Decimal("0")
                    if Decimal(str(anterior)) != Decimal(str(nuevo)):
                        db.add(HistoricoSueldo(
                            empleado_id=empleado_id,
                            campo=campo,
                            valor_anterior=anterior,
                            valor_nuevo=nuevo,
                        ))
            for key, value in datos.items():
                setattr(empleado, key, value)
            db.flush()
            db.refresh(empleado)
        from services.core.audit_service import registrar_auditoria
        registrar_auditoria("UPDATE", "empleados", empleado_id, f"Actualizado")
        return empleado

    def eliminar(self, empleado_id: int) -> bool:
        """Baja lógica (no borra de la BD)."""
        with get_db() as db:
            empleado = db.get(Empleado, empleado_id)
            if not empleado:
                return False
            empleado.activo = False
        from services.core.audit_service import registrar_auditoria
        registrar_auditoria("DELETE", "empleados", empleado_id, "Baja logica")
        return True

    def listar_departamentos(self) -> list[Departamento]:
        with get_db() as db:
            return db.query(Departamento).filter(Departamento.activo == True).order_by(Departamento.nombre).all()

    def listar_cargos(self) -> list[Cargo]:
        with get_db() as db:
            return db.query(Cargo).filter(Cargo.activo == True).order_by(Cargo.nombre).all()

    def crear_departamento(self, nombre: str) -> Departamento:
        with get_db() as db:
            dep = Departamento(nombre=nombre)
            db.add(dep)
            db.flush()
            db.refresh(dep)
            return dep

    def crear_cargo(self, nombre: str) -> Cargo:
        with get_db() as db:
            cargo = Cargo(nombre=nombre)
            db.add(cargo)
            db.flush()
            db.refresh(cargo)
            return cargo

    # === LEGAJO / HISTORIAL ===
    def registrar_evento_legajo(self, empleado_id: int, tipo: str, titulo: str,
                                 descripcion: str = "", valor_anterior: str = "",
                                 valor_nuevo: str = "") -> LegajoEvento:
        """Registra evento en el legajo: ascenso, sancion, herramienta, evaluacion, etc."""
        from services.core.auth_service import auth_service
        with get_db() as db:
            evento = LegajoEvento(
                empleado_id=empleado_id,
                fecha=datetime.now(timezone.utc).date(),
                tipo=tipo[:30],
                titulo=titulo[:200],
                descripcion=descripcion[:2000],
                valor_anterior=valor_anterior[:100],
                valor_nuevo=valor_nuevo[:100],
                usuario_id=auth_service.current_user.id if auth_service.current_user else None,
            )
            db.add(evento)
            db.flush()
            return evento

    def listar_legajo(self, empleado_id: int) -> list:
        with get_db() as db:
            return db.query(LegajoEvento).filter(
                LegajoEvento.empleado_id == empleado_id
            ).order_by(LegajoEvento.fecha.desc()).all()

    def registrar_ascenso(self, empleado_id: int, cargo_nuevo_id: int, descripcion: str = ""):
        """Registra ascenso: cambia cargo y registra en legajo."""
        with get_db() as db:
            emp = db.get(Empleado, empleado_id)
            if not emp:
                raise ValueError("Empleado no encontrado")
            cargo_anterior = db.get(Cargo, emp.cargo_id) if emp.cargo_id else None
            cargo_nuevo = db.get(Cargo, cargo_nuevo_id)
            nombre_ant = cargo_anterior.nombre if cargo_anterior else "(sin cargo)"
            nombre_new = cargo_nuevo.nombre if cargo_nuevo else "(sin cargo)"
            emp.cargo_id = cargo_nuevo_id
        self.registrar_evento_legajo(
            empleado_id, "ascenso", f"Ascenso: {nombre_ant} -> {nombre_new}",
            descripcion, nombre_ant, nombre_new
        )

    def registrar_sancion(self, empleado_id: int, titulo: str, descripcion: str = ""):
        self.registrar_evento_legajo(empleado_id, "sancion", titulo, descripcion)

    def registrar_entrega_herramienta(self, empleado_id: int, herramienta: str, descripcion: str = ""):
        self.registrar_evento_legajo(empleado_id, "herramienta", f"Entrega: {herramienta}", descripcion)

    def registrar_evaluacion(self, empleado_id: int, titulo: str, resultado: str = "", descripcion: str = ""):
        self.registrar_evento_legajo(empleado_id, "evaluacion", titulo, descripcion, valor_nuevo=resultado)


empleado_service = EmpleadoService()
