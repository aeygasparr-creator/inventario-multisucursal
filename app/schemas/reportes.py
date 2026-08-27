import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ProductoMasVendidoOut(BaseModel):
    producto_id: uuid.UUID
    sku: str
    nombre: str
    cantidad_vendida: int
    monto_vendido: Decimal

    class Config:
        from_attributes = True


class VentasPorSucursalOut(BaseModel):
    sucursal_id: uuid.UUID
    nombre: str
    cantidad_ventas: int
    monto_total: Decimal

    class Config:
        from_attributes = True


class VentasPorPeriodoOut(BaseModel):
    periodo: datetime
    cantidad_ventas: int
    monto_total: Decimal

    class Config:
        from_attributes = True


class AlertaStockOut(BaseModel):
    inventario_id: uuid.UUID
    producto_id: uuid.UUID
    producto_nombre: str
    sku: str
    sucursal_id: uuid.UUID
    sucursal_nombre: str
    stock_actual: int
    stock_minimo: int

    class Config:
        from_attributes = True


class RotacionStockOut(BaseModel):
    producto_id: uuid.UUID
    producto_nombre: str
    sucursal_id: uuid.UUID
    sucursal_nombre: str
    stock_actual: int
    vendido_en_periodo: int
    indice_rotacion: Optional[float]
