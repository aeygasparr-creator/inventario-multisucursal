import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.orden_compra import OrdenCompra
from app.models.usuario import RolEnum, Usuario
from app.schemas.orden_compra import OrdenCompraCreate, OrdenCompraOut
from app.services import compras_service

router = APIRouter()


@router.get("/", response_model=List[OrdenCompraOut], summary="Listar órdenes de compra")
def listar_ordenes(
    sucursal_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(OrdenCompra)
    if sucursal_id:
        query = query.filter(OrdenCompra.sucursal_id == sucursal_id)
    return query.order_by(OrdenCompra.fecha.desc()).all()


@router.get("/{orden_id}", response_model=OrdenCompraOut, summary="Ver el detalle de una orden")
def obtener_orden(
    orden_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)
):
    orden = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    return orden


@router.post(
    "/",
    response_model=OrdenCompraOut,
    status_code=201,
    summary="Crear orden de compra (admin y gerente_sucursal)",
)
def crear_orden(
    payload: OrdenCompraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    return compras_service.crear_orden_compra(
        db,
        proveedor_id=payload.proveedor_id,
        sucursal_id=payload.sucursal_id,
        usuario_id=current_user.id,
        items=[item.model_dump() for item in payload.items],
    )


@router.post(
    "/{orden_id}/recibir",
    response_model=OrdenCompraOut,
    summary="Recibir orden de compra: suma el stock a la sucursal",
)
def recibir_orden(
    orden_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    return compras_service.recibir_orden_compra(db, orden_id=orden_id, usuario_id=current_user.id)


@router.post(
    "/{orden_id}/cancelar",
    response_model=OrdenCompraOut,
    summary="Cancelar orden de compra pendiente",
)
def cancelar_orden(
    orden_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    return compras_service.cancelar_orden_compra(db, orden_id=orden_id)
