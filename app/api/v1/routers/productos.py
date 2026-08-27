import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.producto import Producto
from app.models.usuario import RolEnum
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoUpdate

router = APIRouter()


@router.get("/", response_model=List[ProductoOut], summary="Listar productos activos")
def listar_productos(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Producto).filter(Producto.activo.is_(True)).all()


@router.post(
    "/",
    response_model=ProductoOut,
    status_code=201,
    summary="Crear producto (admin y gerente_sucursal)",
)
def crear_producto(
    payload: ProductoCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    existente = db.query(Producto).filter(Producto.sku == payload.sku).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese SKU")
    producto = Producto(**payload.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@router.put(
    "/{producto_id}",
    response_model=ProductoOut,
    summary="Actualizar producto (admin y gerente_sucursal)",
)
def actualizar_producto(
    producto_id: uuid.UUID,
    payload: ProductoUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


@router.delete(
    "/{producto_id}", status_code=204, summary="Desactivar producto (solo admin)"
)
def eliminar_producto(
    producto_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto.activo = False  # borrado lógico
    db.commit()
