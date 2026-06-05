from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    nombre_completo: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), default="")
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    rol = relationship("Rol", back_populates="usuarios")
    usuario_permisos = relationship("UsuarioPermiso", back_populates="usuario", cascade="all, delete-orphan")
