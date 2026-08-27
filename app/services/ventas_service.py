import uuid
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.detalle_venta import DetalleVenta
from app.models.producto import Producto
from app.models.venta import EstadoVenta, Venta
from app.services.inventario_service import _aplicar_salida


def crear_venta(
    db: Session,
    sucursal_id: uuid.UUID,
    usuario_id: uuid.UUID,
    items: List[dict],
) -> Venta:
    """Confirma una venta con uno o varios productos como una sola
    transacción: se valida y descuenta el stock de cada producto, y si
    CUALQUIERA no tiene stock suficiente, la venta completa se cancela
    (no se descuenta nada de los productos que sí alcanzaban).
    """
    if not items:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto")

    try:
        venta = Venta(
            sucursal_id=sucursal_id,
            usuario_id=usuario_id,
            estado=EstadoVenta.confirmada,
            total=0,
        )
        db.add(venta)
        db.flush()

        total = 0
        for item in items:
            if item["cantidad"] <= 0:
                raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")

            producto = db.query(Producto).filter(Producto.id == item["producto_id"]).first()
            if not producto or not producto.activo:
                raise HTTPException(status_code=404, detail="Producto no encontrado")

            # El precio se toma del catálogo (no del request) para que el
            # cliente de la API no pueda manipular el precio de venta.
            precio_unitario = producto.precio_unitario
            subtotal = item["cantidad"] * precio_unitario

            _aplicar_salida(
                db,
                producto_id=producto.id,
                sucursal_id=sucursal_id,
                cantidad=item["cantidad"],
                usuario_id=usuario_id,
                motivo=f"Venta {venta.id}",
            )

            db.add(
                DetalleVenta(
                    venta_id=venta.id,
                    producto_id=producto.id,
                    cantidad=item["cantidad"],
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                )
            )
            total += subtotal

        venta.total = total
        db.commit()
        db.refresh(venta)
        return venta
    except Exception:
        db.rollback()
        raise
