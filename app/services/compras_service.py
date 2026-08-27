import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.orden_compra import EstadoOrdenCompra, OrdenCompra
from app.services.inventario_service import _aplicar_entrada


def crear_orden_compra(
    db: Session,
    proveedor_id: uuid.UUID,
    sucursal_id: uuid.UUID,
    usuario_id: uuid.UUID,
    items: List[dict],
) -> OrdenCompra:
    """Crea la orden en estado 'pendiente'. Todavía no mueve stock:
    el stock se suma recién cuando la mercadería llega (ver recibir_orden_compra).
    """
    if not items:
        raise HTTPException(status_code=400, detail="La orden debe tener al menos un producto")

    try:
        total = sum(item["cantidad"] * item["precio_unitario"] for item in items)
        orden = OrdenCompra(
            proveedor_id=proveedor_id,
            sucursal_id=sucursal_id,
            usuario_id=usuario_id,
            estado=EstadoOrdenCompra.pendiente,
            total=total,
        )
        db.add(orden)
        db.flush()

        for item in items:
            if item["cantidad"] <= 0:
                raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")
            db.add(
                DetalleOrdenCompra(
                    orden_compra_id=orden.id,
                    producto_id=item["producto_id"],
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio_unitario"],
                    subtotal=item["cantidad"] * item["precio_unitario"],
                )
            )

        db.commit()
        db.refresh(orden)
        return orden
    except Exception:
        db.rollback()
        raise


def recibir_orden_compra(db: Session, orden_id: uuid.UUID, usuario_id: uuid.UUID) -> OrdenCompra:
    """Marca la orden como recibida y suma el stock de TODOS sus productos
    en una sola transacción: si uno de los productos falla, no queda
    ningún producto sumado (nada de recepciones a medias).
    """
    try:
        orden = (
            db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).with_for_update().first()
        )
        if not orden:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
        if orden.estado != EstadoOrdenCompra.pendiente:
            raise HTTPException(
                status_code=400, detail=f"La orden ya está en estado '{orden.estado.value}'"
            )

        for detalle in orden.detalles:
            _aplicar_entrada(
                db,
                producto_id=detalle.producto_id,
                sucursal_id=orden.sucursal_id,
                cantidad=detalle.cantidad,
                usuario_id=usuario_id,
                motivo=f"Recepción de orden de compra {orden.id}",
            )

        orden.estado = EstadoOrdenCompra.recibida
        db.commit()
        db.refresh(orden)
        return orden
    except Exception:
        db.rollback()
        raise


def cancelar_orden_compra(db: Session, orden_id: uuid.UUID) -> OrdenCompra:
    try:
        orden = db.query(OrdenCompra).filter(OrdenCompra.id == orden_id).first()
        if not orden:
            raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
        if orden.estado != EstadoOrdenCompra.pendiente:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede cancelar una orden en estado '{orden.estado.value}'",
            )
        orden.estado = EstadoOrdenCompra.cancelada
        db.commit()
        db.refresh(orden)
        return orden
    except Exception:
        db.rollback()
        raise
