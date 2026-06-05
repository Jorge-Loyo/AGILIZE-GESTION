from sqlalchemy import String, Integer, ForeignKey, Date, Numeric, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin
from datetime import date
from decimal import Decimal


class Adelanto(Base, TimestampMixin):
    __tablename__ = "adelantos"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id"))
    fecha: Mapped[date] = mapped_column(Date)
    monto: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    cuotas: Mapped[int] = mapped_column(Integer, default=1)
    cuotas_descontadas: Mapped[int] = mapped_column(Integer, default=0)
    monto_descontado: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    saldo_pendiente: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0"))
    motivo: Mapped[str] = mapped_column(String(250), default="")
    completado: Mapped[bool] = mapped_column(Boolean, default=False)

    empleado = relationship("Empleado")

    @property
    def monto_cuota(self) -> Decimal:
        if self.cuotas <= 0:
            return self.monto
        return (self.monto / self.cuotas).quantize(Decimal("0.01"))
