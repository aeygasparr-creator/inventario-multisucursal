import uuid

from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class DetalleOrdenCompra(Base):
    __tablename__ = "detalle_orden_compra"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    orden_compra_id = Column(UUID(as_uuid=True), ForeignKey("ordenes_compra.id"), nullable=False)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    orden_compra = relationship("OrdenCompra", back_populates="detalles")
    producto = relationship("Producto")
