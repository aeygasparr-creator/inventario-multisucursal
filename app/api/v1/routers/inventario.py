import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.inventario import Inventario
from app.models.usuario import RolEnum, Usuario
from app.schemas.inventario import (
    ActualizarStockMinimo,
    EntradaStockCreate,
    InventarioOut,
    SalidaStockCreate,
    TransferenciaStockCreate,
)
from app.schemas.movimiento_stock import MovimientoStockOut
from app.services import inventario_service

router = APIRouter()


@router.get("/", response_model=List[InventarioOut], summary="Consultar stock por sucursal")
def listar_inventario(
    sucursal_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    query = db.query(Inventario)
    if sucursal_id:
        query = query.filter(Inventario.sucursal_id == sucursal_id)
    return query.all()


@router.patch(
    "/{inventario_id}/stock-minimo",
    response_model=InventarioOut,
    summary="Definir el stock mínimo de alerta (admin y gerente_sucursal)",
)
def actualizar_stock_minimo(
    inventario_id: uuid.UUID,
    payload: ActualizarStockMinimo,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    inventario = db.query(Inventario).filter(Inventario.id == inventario_id).first()
    if not inventario:
        raise HTTPException(status_code=404, detail="Registro de inventario no encontrado")
    inventario.stock_minimo = payload.stock_minimo
    db.commit()
    db.refresh(inventario)
    return inventario


@router.post(
    "/entradas",
    response_model=MovimientoStockOut,
    status_code=201,
    summary="Registrar entrada de stock",
)
def crear_entrada(
    payload: EntradaStockCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    return inventario_service.registrar_entrada(
        db,
        producto_id=payload.producto_id,
        sucursal_id=payload.sucursal_id,
        cantidad=payload.cantidad,
        usuario_id=current_user.id,
        motivo=payload.motivo,
    )


@router.post(
    "/salidas",
    response_model=MovimientoStockOut,
    status_code=201,
    summary="Registrar salida de stock",
)
def crear_salida(
    payload: SalidaStockCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    return inventario_service.registrar_salida(
        db,
        producto_id=payload.producto_id,
        sucursal_id=payload.sucursal_id,
        cantidad=payload.cantidad,
        usuario_id=current_user.id,
        motivo=payload.motivo,
    )


@router.post(
    "/transferencias",
    response_model=MovimientoStockOut,
    status_code=201,
    summary="Transferir stock entre sucursales",
)
def crear_transferencia(
    payload: TransferenciaStockCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(RolEnum.admin, RolEnum.gerente_sucursal)),
):
    return inventario_service.registrar_transferencia(
        db,
        producto_id=payload.producto_id,
        sucursal_origen_id=payload.sucursal_origen_id,
        sucursal_destino_id=payload.sucursal_destino_id,
        cantidad=payload.cantidad,
        usuario_id=current_user.id,
        motivo=payload.motivo,
    )
