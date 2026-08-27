import uuid
from typing import Optional

from pydantic import BaseModel


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaOut(BaseModel):
    id: uuid.UUID
    nombre: str
    descripcion: Optional[str]

    class Config:
        from_attributes = True
