import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class EstadoOrdenCompra(str, enum.Enum):
    pendiente = "pendiente"
    recibida = "recibida"
    cancelada = "cancelada"


class OrdenCompra(Base):
    __tablename__ = "ordenes_compra"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proveedor_id = Column(UUID(as_uuid=True), ForeignKey("proveedores.id"), nullable=False)
    sucursal_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    estado = Column(
        SqlEnum(EstadoOrdenCompra, name="estado_orden_compra_enum"),
        nullable=False,
        default=EstadoOrdenCompra.pendiente,
    )
    fecha = Column(DateTime(timezone=True), server_default=func.now())
    total = Column(Numeric(12, 2), nullable=False, default=0)

    detalles = relationship(
        "DetalleOrdenCompra", back_populates="orden_compra", cascade="all, delete-orphan"
    )
