import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from app.models.orden_compra import EstadoOrdenCompra


class ItemOrdenCompra(BaseModel):
    """Un producto dentro de una orden de compra.

    El precio lo define el proveedor en la negociación, por eso aquí sí se
    recibe desde el request (a diferencia de una venta, donde el precio se
    toma del catálogo propio).
    """

    producto_id: uuid.UUID
    cantidad: int
    precio_unitario: Decimal


class OrdenCompraCreate(BaseModel):
    proveedor_id: uuid.UUID
    sucursal_id: uuid.UUID
    items: List[ItemOrdenCompra]


class DetalleOrdenCompraOut(BaseModel):
    id: uuid.UUID
    producto_id: uuid.UUID
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


class OrdenCompraOut(BaseModel):
    id: uuid.UUID
    proveedor_id: uuid.UUID
    sucursal_id: uuid.UUID
    usuario_id: uuid.UUID
    estado: EstadoOrdenCompra
    fecha: datetime
    total: Decimal
    detalles: List[DetalleOrdenCompraOut] = []

    class Config:
        from_attributes = True
