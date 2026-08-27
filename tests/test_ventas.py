import uuid

import pytest
from fastapi import HTTPException

from app.models.inventario import Inventario
from app.models.producto import Producto
from app.services import inventario_service, ventas_service


def _stock(db_session, producto_id, sucursal_id):
    inv = (
        db_session.query(Inventario)
        .filter(Inventario.producto_id == producto_id, Inventario.sucursal_id == sucursal_id)
        .first()
    )
    return inv.stock_actual if inv else 0


def test_venta_descuenta_stock_y_calcula_total(db_session, producto_test, sucursal_origen, usuario_test):
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=20,
        usuario_id=usuario_test.id,
    )

    venta = ventas_service.crear_venta(
        db_session,
        sucursal_id=sucursal_origen.id,
        usuario_id=usuario_test.id,
        items=[{"producto_id": producto_test.id, "cantidad": 3}],
    )

    assert venta.total == producto_test.precio_unitario * 3
    assert _stock(db_session, producto_test.id, sucursal_origen.id) == 17


def test_venta_toma_el_precio_del_catalogo(db_session, producto_test, sucursal_origen, usuario_test):
    """El schema ItemVenta ni siquiera acepta un precio en el request; esto
    confirma que el precio guardado en el detalle es el del producto.
    """
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=10,
        usuario_id=usuario_test.id,
    )

    venta = ventas_service.crear_venta(
        db_session,
        sucursal_id=sucursal_origen.id,
        usuario_id=usuario_test.id,
        items=[{"producto_id": producto_test.id, "cantidad": 1}],
    )

    assert venta.detalles[0].precio_unitario == producto_test.precio_unitario


def test_venta_con_un_producto_sin_stock_no_descuenta_ningun_producto(
    db_session, categoria_test, sucursal_origen, usuario_test
):
    """Venta con 2 productos: uno sí tiene stock, el otro no. Debe
    rechazarse completa y no descontar nada, ni siquiera del que sí
    alcanzaba — así como probamos a mano con la transferencia.
    """
    producto_con_stock = Producto(
        sku=f"A-{uuid.uuid4().hex[:8]}",
        nombre="Con stock",
        categoria_id=categoria_test.id,
        precio_unitario=5,
    )
    producto_sin_stock = Producto(
        sku=f"B-{uuid.uuid4().hex[:8]}",
        nombre="Sin stock",
        categoria_id=categoria_test.id,
        precio_unitario=5,
    )
    db_session.add_all([producto_con_stock, producto_sin_stock])
    db_session.flush()

    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_con_stock.id,
        sucursal_id=sucursal_origen.id,
        cantidad=10,
        usuario_id=usuario_test.id,
    )
    # producto_sin_stock se queda deliberadamente en 0

    with pytest.raises(HTTPException) as exc_info:
        ventas_service.crear_venta(
            db_session,
            sucursal_id=sucursal_origen.id,
            usuario_id=usuario_test.id,
            items=[
                {"producto_id": producto_con_stock.id, "cantidad": 2},
                {"producto_id": producto_sin_stock.id, "cantidad": 2},
            ],
        )
    assert exc_info.value.status_code == 400

    assert _stock(db_session, producto_con_stock.id, sucursal_origen.id) == 10
