import uuid
from typing import Optional

from pydantic import BaseModel


class ProveedorCreate(BaseModel):
    razon_social: str
    ruc: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None


class ProveedorUpdate(BaseModel):
    razon_social: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    activo: Optional[bool] = None


class ProveedorOut(BaseModel):
    id: uuid.UUID
    razon_social: str
    ruc: str
    contacto: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    activo: bool

    class Config:
        from_attributes = True
