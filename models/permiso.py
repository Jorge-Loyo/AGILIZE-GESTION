from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin


class Modulo(Base, TimestampMixin):
    __tablename__ = "modulos"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True)  # ej: "empleados"
    nombre: Mapped[str] = mapped_column(String(100))  # ej: "Gestión de Empleados"
    icono: Mapped[str] = mapped_column(String(50), default="")
    orden: Mapped[int] = mapped_column(Integer, default=0)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    permisos = relationship("Permiso", back_populates="modulo", cascade="all, delete-orphan")


class Permiso(Base):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(primary_key=True)
    modulo_id: Mapped[int] = mapped_column(ForeignKey("modulos.id"))
    accion: Mapped[str] = mapped_column(String(20))  # ver, crear, editar, eliminar, exportar

    modulo = relationship("Modulo", back_populates="permisos")
    rol_permisos = relationship("RolPermiso", back_populates="permiso")
    usuario_permisos = relationship("UsuarioPermiso", back_populates="permiso")


class RolPermiso(Base):
    __tablename__ = "rol_permisos"

    id: Mapped[int] = mapped_column(primary_key=True)
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    permiso_id: Mapped[int] = mapped_column(ForeignKey("permisos.id"))

    rol = relationship("Rol", back_populates="rol_permisos")
    permiso = relationship("Permiso", back_populates="rol_permisos")


class UsuarioPermiso(Base):
    """Override de permisos por usuario individual."""
    __tablename__ = "usuario_permisos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    permiso_id: Mapped[int] = mapped_column(ForeignKey("permisos.id"))
    concedido: Mapped[bool] = mapped_column(Boolean, default=True)  # True=agregar, False=denegar

    usuario = relationship("Usuario", back_populates="usuario_permisos")
    permiso = relationship("Permiso", back_populates="usuario_permisos")
