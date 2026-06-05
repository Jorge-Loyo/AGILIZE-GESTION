from sqlalchemy import String, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from decimal import Decimal


class SACRegistro(Base, TimestampMixin):
    """Registro mensual de remuneración para cálculo de SAC."""
    __tablename__ = "sac_registros"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    periodo: Mapped[str] = mapped_column(String(7))  # YYYY-MM
    semestre: Mapped[int] = mapped_column(Integer)  # 1 o 2
    anio: Mapped[int] = mapped_column(Integer)
    remuneracion_bruta: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    empleado = relationship("Empleado")


class SACLiquidacion(Base, TimestampMixin):
    """Liquidación de SAC (aguinaldo) por semestre."""
    __tablename__ = "sac_liquidaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    semestre: Mapped[int] = mapped_column(Integer)  # 1 o 2
    anio: Mapped[int] = mapped_column(Integer)
    metodo: Mapped[str] = mapped_column(String(20))  # "mayor" o "promedio"
    base_calculo: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    monto_sac: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    empleado = relationship("Empleado")
