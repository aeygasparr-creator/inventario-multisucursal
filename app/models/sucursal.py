import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Sucursal(Base):
    __tablename__ = "sucursales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(120), nullable=False)
    ciudad = Column(String(100), nullable=False)
    direccion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)

    usuarios = relationship("Usuario", back_populates="sucursal")
