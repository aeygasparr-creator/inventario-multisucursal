import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.sucursal import Sucursal
from app.models.usuario import RolEnum
from app.schemas.sucursal import SucursalCreate, SucursalOut, SucursalUpdate

router = APIRouter()


@router.get("/", response_model=List[SucursalOut], summary="Listar sucursales activas")
def listar_sucursales(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Sucursal).filter(Sucursal.activo.is_(True)).all()


@router.post(
    "/", response_model=SucursalOut, status_code=201, summary="Crear sucursal (solo admin)"
)
def crear_sucursal(
    payload: SucursalCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    sucursal = Sucursal(**payload.model_dump())
    db.add(sucursal)
    db.commit()
    db.refresh(sucursal)
    return sucursal


@router.put(
    "/{sucursal_id}", response_model=SucursalOut, summary="Actualizar sucursal (solo admin)"
)
def actualizar_sucursal(
    sucursal_id: uuid.UUID,
    payload: SucursalUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(sucursal, campo, valor)
    db.commit()
    db.refresh(sucursal)
    return sucursal


@router.delete("/{sucursal_id}", status_code=204, summary="Desactivar sucursal (solo admin)")
def eliminar_sucursal(
    sucursal_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    sucursal.activo = False  # borrado lógico
    db.commit()
