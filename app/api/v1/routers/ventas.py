import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.usuario import Usuario
from app.models.venta import Venta
from app.schemas.venta import VentaCreate, VentaOut
from app.services import ventas_service

router = APIRouter()


@router.get("/", response_model=List[VentaOut], summary="Listar ventas")
def listar_ventas(
    sucursal_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Venta)
    if sucursal_id:
        query = query.filter(Venta.sucursal_id == sucursal_id)
    return query.order_by(Venta.fecha.desc()).all()


@router.get("/{venta_id}", response_model=VentaOut, summary="Ver el detalle de una venta")
def obtener_venta(venta_id: uuid.UUID, db: Session = Depends(get_db), _=Depends(get_current_user)):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@router.post(
    "/",
    response_model=VentaOut,
    status_code=201,
    summary="Registrar una venta (valida y descuenta stock)",
)
def crear_venta(
    payload: VentaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Cualquier usuario autenticado puede vender (admin, gerente_sucursal o
    # vendedor) — a diferencia de crear productos o sucursales, que están
    # restringidos por rol.
    return ventas_service.crear_venta(
        db,
        sucursal_id=payload.sucursal_id,
        usuario_id=current_user.id,
        items=[item.model_dump() for item in payload.items],
    )
