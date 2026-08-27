import uuid
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProductoCreate(BaseModel):
    sku: str
    nombre: str
    categoria_id: uuid.UUID
    precio_unitario: Decimal
    unidad_medida: str = "unidad"


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[uuid.UUID] = None
    precio_unitario: Optional[Decimal] = None
    unidad_medida: Optional[str] = None
    activo: Optional[bool] = None


class ProductoOut(BaseModel):
    id: uuid.UUID
    sku: str
    nombre: str
    categoria_id: uuid.UUID
    precio_unitario: Decimal
    unidad_medida: str
    activo: bool

    class Config:
        from_attributes = True
