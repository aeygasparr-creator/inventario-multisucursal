import uuid
from typing import Optional

from pydantic import BaseModel


class InventarioOut(BaseModel):
    id: uuid.UUID
    producto_id: uuid.UUID
    sucursal_id: uuid.UUID
    stock_actual: int
    stock_minimo: int

    class Config:
        from_attributes = True


class EntradaStockCreate(BaseModel):
    producto_id: uuid.UUID
    sucursal_id: uuid.UUID
    cantidad: int
    motivo: Optional[str] = None


class SalidaStockCreate(BaseModel):
    producto_id: uuid.UUID
    sucursal_id: uuid.UUID
    cantidad: int
    motivo: Optional[str] = None


class TransferenciaStockCreate(BaseModel):
    producto_id: uuid.UUID
    sucursal_origen_id: uuid.UUID
    sucursal_destino_id: uuid.UUID
    cantidad: int
    motivo: Optional[str] = None


class ActualizarStockMinimo(BaseModel):
    stock_minimo: int
