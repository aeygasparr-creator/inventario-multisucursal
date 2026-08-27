import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from app.models.venta import EstadoVenta


class ItemVenta(BaseModel):
    """Un producto dentro de una venta.

    Solo se pide producto_id y cantidad: el precio se toma del catálogo
    (Producto.precio_unitario) en el momento de confirmar la venta, para
    que el cliente de la API no pueda manipular el precio de venta.
    """

    producto_id: uuid.UUID
    cantidad: int


class VentaCreate(BaseModel):
    sucursal_id: uuid.UUID
    items: List[ItemVenta]


class DetalleVentaOut(BaseModel):
    id: uuid.UUID
    producto_id: uuid.UUID
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class VentaOut(BaseModel):
    id: uuid.UUID
    sucursal_id: uuid.UUID
    usuario_id: uuid.UUID
    estado: EstadoVenta
    fecha: datetime
    total: Decimal
    detalles: List[DetalleVentaOut] = []

    class Config:
        from_attributes = True
