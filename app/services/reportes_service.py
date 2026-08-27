import uuid
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.detalle_venta import DetalleVenta
from app.models.inventario import Inventario
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.models.venta import EstadoVenta, Venta


def productos_mas_vendidos(
    db: Session,
    limite: int = 10,
    sucursal_id: Optional[uuid.UUID] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
):
    query = (
        db.query(
            Producto.id.label("producto_id"),
            Producto.sku,
            Producto.nombre,
            func.coalesce(func.sum(DetalleVenta.cantidad), 0).label("cantidad_vendida"),
            func.coalesce(func.sum(DetalleVenta.subtotal), 0).label("monto_vendido"),
        )
        .join(DetalleVenta, DetalleVenta.producto_id == Producto.id)
        .join(Venta, Venta.id == DetalleVenta.venta_id)
        .filter(Venta.estado == EstadoVenta.confirmada)
    )
    if sucursal_id:
        query = query.filter(Venta.sucursal_id == sucursal_id)
    if fecha_inicio:
        query = query.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Venta.fecha <= fecha_fin)

    return (
        query.group_by(Producto.id, Producto.sku, Producto.nombre)
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .limit(limite)
        .all()
    )


def ventas_por_sucursal(
    db: Session,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
):
    query = (
        db.query(
            Sucursal.id.label("sucursal_id"),
            Sucursal.nombre,
            func.count(Venta.id).label("cantidad_ventas"),
            func.coalesce(func.sum(Venta.total), 0).label("monto_total"),
        )
        .join(Venta, Venta.sucursal_id == Sucursal.id)
        .filter(Venta.estado == EstadoVenta.confirmada)
    )
    if fecha_inicio:
        query = query.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Venta.fecha <= fecha_fin)

    return (
        query.group_by(Sucursal.id, Sucursal.nombre).order_by(func.sum(Venta.total).desc()).all()
    )


def ventas_por_periodo(
    db: Session,
    agrupar_por: str = "dia",
    sucursal_id: Optional[uuid.UUID] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
):
    unidad = "day" if agrupar_por == "dia" else "month"
    periodo = func.date_trunc(unidad, Venta.fecha).label("periodo")

    query = db.query(
        periodo,
        func.count(Venta.id).label("cantidad_ventas"),
        func.coalesce(func.sum(Venta.total), 0).label("monto_total"),
    ).filter(Venta.estado == EstadoVenta.confirmada)

    if sucursal_id:
        query = query.filter(Venta.sucursal_id == sucursal_id)
    if fecha_inicio:
        query = query.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Venta.fecha <= fecha_fin)

    return query.group_by(periodo).order_by(periodo).all()


def alertas_stock(db: Session, sucursal_id: Optional[uuid.UUID] = None):
    """Productos cuyo stock actual ya llegó (o está por debajo) del mínimo
    definido para esa sucursal.
    """
    query = (
        db.query(
            Inventario.id.label("inventario_id"),
            Producto.id.label("producto_id"),
            Producto.nombre.label("producto_nombre"),
            Producto.sku,
            Sucursal.id.label("sucursal_id"),
            Sucursal.nombre.label("sucursal_nombre"),
            Inventario.stock_actual,
            Inventario.stock_minimo,
        )
        .join(Producto, Producto.id == Inventario.producto_id)
        .join(Sucursal, Sucursal.id == Inventario.sucursal_id)
        .filter(Inventario.stock_actual <= Inventario.stock_minimo)
    )
    if sucursal_id:
        query = query.filter(Inventario.sucursal_id == sucursal_id)
    return query.order_by(Inventario.stock_actual.asc()).all()


def rotacion_stock(
    db: Session, dias: int = 30, sucursal_id: Optional[uuid.UUID] = None
) -> List[dict]:
    """Aproximación simple de rotación de inventario: unidades vendidas en
    los últimos N días, dividido entre el stock actual. Un índice alto
    (ej. 3.0) significa que se vendió 3 veces el stock que hay ahora mismo
    — se mueve rápido. Un índice cercano a 0 sugiere stock estancado.
    """
    desde = datetime.now(timezone.utc) - timedelta(days=dias)

    vendidos = (
        db.query(
            DetalleVenta.producto_id.label("producto_id"),
            Venta.sucursal_id.label("sucursal_id"),
            func.sum(DetalleVenta.cantidad).label("cantidad_vendida"),
        )
        .join(Venta, Venta.id == DetalleVenta.venta_id)
        .filter(Venta.estado == EstadoVenta.confirmada, Venta.fecha >= desde)
        .group_by(DetalleVenta.producto_id, Venta.sucursal_id)
        .subquery()
    )

    query = (
        db.query(
            Producto.id.label("producto_id"),
            Producto.nombre.label("producto_nombre"),
            Sucursal.id.label("sucursal_id"),
            Sucursal.nombre.label("sucursal_nombre"),
            Inventario.stock_actual,
            func.coalesce(vendidos.c.cantidad_vendida, 0).label("vendido_en_periodo"),
        )
        .join(Producto, Producto.id == Inventario.producto_id)
        .join(Sucursal, Sucursal.id == Inventario.sucursal_id)
        .outerjoin(
            vendidos,
            (vendidos.c.producto_id == Inventario.producto_id)
            & (vendidos.c.sucursal_id == Inventario.sucursal_id),
        )
    )
    if sucursal_id:
        query = query.filter(Inventario.sucursal_id == sucursal_id)

    resultado = []
    for fila in query.all():
        vendido = int(fila.vendido_en_periodo or 0)
        stock = fila.stock_actual or 0
        indice = round(vendido / stock, 2) if stock > 0 else None
        resultado.append(
            {
                "producto_id": fila.producto_id,
                "producto_nombre": fila.producto_nombre,
                "sucursal_id": fila.sucursal_id,
                "sucursal_nombre": fila.sucursal_nombre,
                "stock_actual": stock,
                "vendido_en_periodo": vendido,
                "indice_rotacion": indice,
            }
        )

    resultado.sort(key=lambda r: (r["indice_rotacion"] is None, -(r["indice_rotacion"] or 0)))
    return resultado
