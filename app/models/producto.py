import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    nombre = Column(String(150), nullable=False)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categorias.id"), nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    unidad_medida = Column(String(20), default="unidad", nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    categoria = relationship("Categoria", back_populates="productos")
