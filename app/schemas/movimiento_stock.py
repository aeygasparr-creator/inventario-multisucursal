import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.movimiento_stock import TipoMovimiento


class MovimientoStockOut(BaseModel):
    id: uuid.UUID
    producto_id: uuid.UUID
    tipo: TipoMovimiento
    cantidad: int
    sucursal_origen_id: Optional[uuid.UUID]
    sucursal_destino_id: Optional[uuid.UUID]
    usuario_id: uuid.UUID
    motivo: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
