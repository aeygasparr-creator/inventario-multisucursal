import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class EstadoVenta(str, enum.Enum):
    confirmada = "confirmada"
    anulada = "anulada"


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    estado = Column(
        SqlEnum(EstadoVenta, name="estado_venta_enum"),
        nullable=False,
        default=EstadoVenta.confirmada,
    )
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    total = Column(Numeric(12, 2), nullable=False, default=0)

    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
