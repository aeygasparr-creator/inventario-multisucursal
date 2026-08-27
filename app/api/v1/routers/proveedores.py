import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.proveedor import Proveedor
from app.models.usuario import RolEnum
from app.schemas.proveedor import ProveedorCreate, ProveedorOut, ProveedorUpdate

router = APIRouter()


@router.get("/", response_model=List[ProveedorOut], summary="Listar proveedores activos")
def listar_proveedores(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Proveedor).filter(Proveedor.activo.is_(True)).all()


@router.post(
    "/", response_model=ProveedorOut, status_code=201, summary="Crear proveedor (solo admin)"
)
def crear_proveedor(
    payload: ProveedorCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    existente = db.query(Proveedor).filter(Proveedor.ruc == payload.ruc).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese RUC")
    proveedor = Proveedor(**payload.model_dump())
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.put(
    "/{proveedor_id}",
    response_model=ProveedorOut,
    summary="Actualizar proveedor (solo admin)",
)
def actualizar_proveedor(
    proveedor_id: uuid.UUID,
    payload: ProveedorUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(proveedor, campo, valor)
    db.commit()
    db.refresh(proveedor)
    return proveedor


@router.delete(
    "/{proveedor_id}", status_code=204, summary="Desactivar proveedor (solo admin)"
)
def eliminar_proveedor(
    proveedor_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    proveedor.activo = False
    db.commit()
