import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.usuario import RolEnum


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol: RolEnum = RolEnum.vendedor
    sucursal_id: Optional[uuid.UUID] = None


class UsuarioOut(BaseModel):
    id: uuid.UUID
    nombre: str
    email: EmailStr
    rol: RolEnum
    sucursal_id: Optional[uuid.UUID]
    activo: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
