import pytest
from fastapi import HTTPException

from app.models.inventario import Inventario
from app.services import inventario_service


def _stock(db_session, producto_id, sucursal_id):
    inv = (
        db_session.query(Inventario)
        .filter(Inventario.producto_id == producto_id, Inventario.sucursal_id == sucursal_id)
        .first()
    )
    return inv.stock_actual if inv else 0


def test_transferencia_exitosa_mueve_stock_entre_sucursales(
    db_session, producto_test, sucursal_origen, sucursal_destino, usuario_test
):
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=50,
        usuario_id=usuario_test.id,
    )

    inventario_service.registrar_transferencia(
        db_session,
        producto_id=producto_test.id,
        sucursal_origen_id=sucursal_origen.id,
        sucursal_destino_id=sucursal_destino.id,
        cantidad=20,
        usuario_id=usuario_test.id,
    )

    assert _stock(db_session, producto_test.id, sucursal_origen.id) == 30
    assert _stock(db_session, producto_test.id, sucursal_destino.id) == 20


def test_transferencia_con_stock_insuficiente_no_mueve_nada(
    db_session, producto_test, sucursal_origen, sucursal_destino, usuario_test
):
    """El caso que motivó la transacción atómica: si falla, no debe quedar
    stock descontado del origen sin haberse sumado al destino.
    """
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=10,
        usuario_id=usuario_test.id,
    )

    with pytest.raises(HTTPException) as exc_info:
        inventario_service.registrar_transferencia(
            db_session,
            producto_id=producto_test.id,
            sucursal_origen_id=sucursal_origen.id,
            sucursal_destino_id=sucursal_destino.id,
            cantidad=999,
            usuario_id=usuario_test.id,
        )
    assert exc_info.value.status_code == 400

    assert _stock(db_session, producto_test.id, sucursal_origen.id) == 10
    assert _stock(db_session, producto_test.id, sucursal_destino.id) == 0


def test_transferencia_a_la_misma_sucursal_falla(db_session, producto_test, sucursal_origen, usuario_test):
    with pytest.raises(HTTPException) as exc_info:
        inventario_service.registrar_transferencia(
            db_session,
            producto_id=producto_test.id,
            sucursal_origen_id=sucursal_origen.id,
            sucursal_destino_id=sucursal_origen.id,
            cantidad=5,
            usuario_id=usuario_test.id,
        )
    assert exc_info.value.status_code == 400


def test_salida_con_stock_insuficiente_falla(db_session, producto_test, sucursal_origen, usuario_test):
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=5,
        usuario_id=usuario_test.id,
    )

    with pytest.raises(HTTPException) as exc_info:
        inventario_service.registrar_salida(
            db_session,
            producto_id=producto_test.id,
            sucursal_id=sucursal_origen.id,
            cantidad=100,
            usuario_id=usuario_test.id,
        )
    assert exc_info.value.status_code == 400
    assert _stock(db_session, producto_test.id, sucursal_origen.id) == 5
