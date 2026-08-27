import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.reportes import (
    AlertaStockOut,
    ProductoMasVendidoOut,
    RotacionStockOut,
    VentasPorPeriodoOut,
    VentasPorSucursalOut,
)
from app.services import reportes_service

router = APIRouter()


@router.get(
    "/productos-mas-vendidos",
    response_model=List[ProductoMasVendidoOut],
    summary="Productos más vendidos",
)
def productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=100),
    sucursal_id: Optional[uuid.UUID] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return reportes_service.productos_mas_vendidos(
        db,
        limite=limite,
        sucursal_id=sucursal_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


@router.get(
    "/ventas-por-sucursal",
    response_model=List[VentasPorSucursalOut],
    summary="Total de ventas agrupado por sucursal",
)
def ventas_por_sucursal(
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return reportes_service.ventas_por_sucursal(db, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@router.get(
    "/ventas-por-periodo",
    response_model=List[VentasPorPeriodoOut],
    summary="Ventas agrupadas por día o mes (para gráficos de tendencia)",
)
def ventas_por_periodo(
    agrupar_por: str = Query("dia", pattern="^(dia|mes)$"),
    sucursal_id: Optional[uuid.UUID] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return reportes_service.ventas_por_periodo(
        db,
        agrupar_por=agrupar_por,
        sucursal_id=sucursal_id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


@router.get(
    "/alertas-stock",
    response_model=List[AlertaStockOut],
    summary="Productos en quiebre o por debajo del stock mínimo",
)
def alertas_stock(
    sucursal_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return reportes_service.alertas_stock(db, sucursal_id=sucursal_id)


@router.get(
    "/rotacion-stock",
    response_model=List[RotacionStockOut],
    summary="Índice de rotación: unidades vendidas del periodo / stock actual",
)
def rotacion_stock(
    dias: int = Query(30, ge=1, le=365),
    sucursal_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return reportes_service.rotacion_stock(db, dias=dias, sucursal_id=sucursal_id)
