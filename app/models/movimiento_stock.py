import enum
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class TipoMovimiento(str, enum.Enum):
    entrada = "entrada"
    salida = "salida"
    transferencia = "transferencia"


class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False)
    tipo = Column(SqlEnum(TipoMovimiento, name="tipo_movimiento_enum"), nullable=False)
    cantidad = Column(Integer, nullable=False)

    # En una entrada solo se llena destino; en una salida solo origen;
    # en una transferencia se llenan ambas.
    sucursal_origen_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=True)
    sucursal_destino_id = Column(UUID(as_uuid=True), ForeignKey("sucursales.id"), nullable=True)

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    motivo = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    producto = relationship("Producto")
    usuario = relationship("Usuario")
