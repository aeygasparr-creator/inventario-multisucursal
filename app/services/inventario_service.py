import uuid
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.inventario import Inventario
from app.models.movimiento_stock import MovimientoStock, TipoMovimiento


def _obtener_o_crear_inventario(
    db: Session,
    producto_id: uuid.UUID,
    sucursal_id: uuid.UUID,
    bloquear: bool = False,
) -> Inventario:
    """Busca la fila de inventario para (producto, sucursal); si no existe, la crea en 0.

    Con bloquear=True usa SELECT ... FOR UPDATE para evitar que dos ventas o
    transferencias simultáneas lean el mismo stock antes de que la primera
    termine de actualizarlo (condición de carrera).
    """
    query = db.query(Inventario).filter(
        Inventario.producto_id == producto_id,
        Inventario.sucursal_id == sucursal_id,
    )
    if bloquear:
        query = query.with_for_update()
    inventario = query.first()
    if inventario is None:
        inventario = Inventario(
            producto_id=producto_id, sucursal_id=sucursal_id, stock_actual=0, stock_minimo=0
        )
        db.add(inventario)
        db.flush()  # asigna el id sin cerrar la transacción todavía
    return inventario


# --- Funciones internas: mueven stock pero NO hacen commit -----------------
# Se usan solas (envueltas por registrar_entrada/salida/transferencia) o
# encadenadas dentro de una transacción más grande, como recibir una orden
# de compra con 5 productos o confirmar una venta con 3 productos: todo o
# nada, sin dejar movimientos a medias si uno de los items falla.


def _aplicar_entrada(
    db: Session,
    producto_id: uuid.UUID,
    sucursal_id: uuid.UUID,
    cantidad: int,
    usuario_id: uuid.UUID,
    motivo: Optional[str] = None,
) -> MovimientoStock:
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")
    inventario = _obtener_o_crear_inventario(db, producto_id, sucursal_id, bloquear=True)
    inventario.stock_actual += cantidad

    movimiento = MovimientoStock(
        producto_id=producto_id,
        tipo=TipoMovimiento.entrada,
        cantidad=cantidad,
        sucursal_destino_id=sucursal_id,
        usuario_id=usuario_id,
        motivo=motivo,
    )
    db.add(movimiento)
    db.flush()
    return movimiento


def _aplicar_salida(
    db: Session,
    producto_id: uuid.UUID,
    sucursal_id: uuid.UUID,
    cantidad: int,
    usuario_id: uuid.UUID,
    motivo: Optional[str] = None,
) -> MovimientoStock:
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")
    inventario = _obtener_o_crear_inventario(db, producto_id, sucursal_id, bloquear=True)
    if inventario.stock_actual < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en la sucursal")
    inventario.stock_actual -= cantidad

    movimiento = MovimientoStock(
        producto_id=producto_id,
        tipo=TipoMovimiento.salida,
        cantidad=cantidad,
        sucursal_origen_id=sucursal_id,
        usuario_id=usuario_id,
        motivo=motivo,
    )
    db.add(movimiento)
    db.flush()
    return movimiento


def _aplicar_transferencia(
    db: Session,
    producto_id: uuid.UUID,
    sucursal_origen_id: uuid.UUID,
    sucursal_destino_id: uuid.UUID,
    cantidad: int,
    usuario_id: uuid.UUID,
    motivo: Optional[str] = None,
) -> MovimientoStock:
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")
    if sucursal_origen_id == sucursal_destino_id:
        raise HTTPException(
            status_code=400,
            detail="La sucursal de origen y destino no pueden ser la misma",
        )

    # Bloqueamos las dos filas de inventario en un orden fijo (por id) para
    # que dos transferencias cruzadas (A->B y B->A) nunca se bloqueen
    # mutuamente en espera infinita (deadlock).
    if str(sucursal_origen_id) < str(sucursal_destino_id):
        primero_id, segundo_id = sucursal_origen_id, sucursal_destino_id
    else:
        primero_id, segundo_id = sucursal_destino_id, sucursal_origen_id

    inv_primero = _obtener_o_crear_inventario(db, producto_id, primero_id, bloquear=True)
    inv_segundo = _obtener_o_crear_inventario(db, producto_id, segundo_id, bloquear=True)

    inventario_origen = inv_primero if primero_id == sucursal_origen_id else inv_segundo
    inventario_destino = inv_segundo if segundo_id == sucursal_destino_id else inv_primero

    if inventario_origen.stock_actual < cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente en la sucursal de origen")

    inventario_origen.stock_actual -= cantidad
    inventario_destino.stock_actual += cantidad

    movimiento = MovimientoStock(
        producto_id=producto_id,
        tipo=TipoMovimiento.transferencia,
        cantidad=cantidad,
        sucursal_origen_id=sucursal_origen_id,
        sucursal_destino_id=sucursal_destino_id,
        usuario_id=usuario_id,
        motivo=motivo,
    )
    db.add(movimiento)
    db.flush()
    return movimiento


# --- Funciones públicas: usadas directamente por los endpoints de la API ---
# Cada una es su propia transacción completa (aplican el cambio y confirman).


def registrar_entrada(db: Session, **kwargs) -> MovimientoStock:
    try:
        movimiento = _aplicar_entrada(db, **kwargs)
        db.commit()
        db.refresh(movimiento)
        return movimiento
    except Exception:
        db.rollback()
        raise


def registrar_salida(db: Session, **kwargs) -> MovimientoStock:
    try:
        movimiento = _aplicar_salida(db, **kwargs)
        db.commit()
        db.refresh(movimiento)
        return movimiento
    except Exception:
        db.rollback()
        raise


def registrar_transferencia(db: Session, **kwargs) -> MovimientoStock:
    try:
        movimiento = _aplicar_transferencia(db, **kwargs)
        db.commit()
        db.refresh(movimiento)
        return movimiento
    except Exception:
        db.rollback()
        raise
