import uuid
from typing import Optional

from pydantic import BaseModel


class SucursalCreate(BaseModel):
    nombre: str
    ciudad: str
    direccion: Optional[str] = None


class SucursalUpdate(BaseModel):
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class SucursalOut(BaseModel):
    id: uuid.UUID
    nombre: str
    ciudad: str
    direccion: Optional[str]
    activo: bool

    class Config:
        from_attributes = True
