"""Modelos de reclutamiento y seleccion (ATS basico)."""
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date


class Vacante(Base, TimestampMixin):
    """Oferta de empleo / posicion abierta."""
    __tablename__ = "vacantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    departamento_id: Mapped[int] = mapped_column(ForeignKey("departamentos.id"), nullable=True)
    cargo_id: Mapped[int] = mapped_column(ForeignKey("cargos.id"), nullable=True)
    sucursal_id: Mapped[int] = mapped_column(ForeignKey("sucursales.id"), nullable=True)
    cantidad_puestos: Mapped[int] = mapped_column(Integer, default=1)
    tipo_contrato: Mapped[str] = mapped_column(String(30), default="indefinido")
    jornada: Mapped[str] = mapped_column(String(30), default="completa")  # completa, parcial, freelance
    rango_salarial: Mapped[str] = mapped_column(String(100), default="")
    descripcion: Mapped[str] = mapped_column(Text, default="")
    requisitos: Mapped[str] = mapped_column(Text, default="")
    fecha_publicacion: Mapped[date] = mapped_column(Date, nullable=True)
    fecha_cierre: Mapped[date] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="abierta")  # abierta, en_proceso, cerrada, cancelada
    prioridad: Mapped[str] = mapped_column(String(20), default="normal")  # baja, normal, alta, urgente
    responsable_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    candidatos = relationship("Candidato", back_populates="vacante", cascade="all, delete-orphan")


class Candidato(Base, TimestampMixin):
    """Postulante a una vacante."""
    __tablename__ = "candidatos"

    id: Mapped[int] = mapped_column(primary_key=True)
    vacante_id: Mapped[int] = mapped_column(ForeignKey("vacantes.id"))
    nombre: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), default="")
    telefono: Mapped[str] = mapped_column(String(50), default="")
    documento: Mapped[str] = mapped_column(String(30), default="")
    # CV y datos
    cv_archivo: Mapped[str] = mapped_column(String(250), default="")  # path al archivo
    experiencia_anios: Mapped[int] = mapped_column(Integer, default=0)
    pretension_salarial: Mapped[str] = mapped_column(String(100), default="")
    fuente: Mapped[str] = mapped_column(String(50), default="")  # portal, referido, espontaneo
    # Estado de seleccion
    estado: Mapped[str] = mapped_column(String(20), default="postulado")  # postulado, entrevista, evaluando, finalista, contratado, rechazado
    fecha_postulacion: Mapped[date] = mapped_column(Date, default=date.today)
    fecha_entrevista: Mapped[date] = mapped_column(Date, nullable=True)
    puntaje: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    notas: Mapped[str] = mapped_column(Text, default="")
    motivo_rechazo: Mapped[str] = mapped_column(String(200), default="")

    vacante = relationship("Vacante", back_populates="candidatos")
