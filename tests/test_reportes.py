from app.services import inventario_service, reportes_service, ventas_service


def test_productos_mas_vendidos_refleja_las_ventas(
    db_session, producto_test, sucursal_origen, usuario_test
):
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=50,
        usuario_id=usuario_test.id,
    )
    ventas_service.crear_venta(
        db_session,
        sucursal_id=sucursal_origen.id,
        usuario_id=usuario_test.id,
        items=[{"producto_id": producto_test.id, "cantidad": 4}],
    )

    resultados = reportes_service.productos_mas_vendidos(db_session, sucursal_id=sucursal_origen.id)

    encontrado = next(r for r in resultados if r.producto_id == producto_test.id)
    assert encontrado.cantidad_vendida == 4
    assert encontrado.monto_vendido == producto_test.precio_unitario * 4


def test_alertas_stock_detecta_quiebre(db_session, producto_test, sucursal_origen, usuario_test):
    # Entra stock y luego se vende todo: queda en 0, por debajo del mínimo (0 por defecto se sube a mano).
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=5,
        usuario_id=usuario_test.id,
    )
    from app.models.inventario import Inventario

    inv = (
        db_session.query(Inventario)
        .filter(
            Inventario.producto_id == producto_test.id,
            Inventario.sucursal_id == sucursal_origen.id,
        )
        .first()
    )
    inv.stock_minimo = 10  # el stock actual (5) queda por debajo del mínimo
    db_session.flush()

    alertas = reportes_service.alertas_stock(db_session, sucursal_id=sucursal_origen.id)

    assert any(a.producto_id == producto_test.id for a in alertas)


def test_rotacion_stock_calcula_indice(db_session, producto_test, sucursal_origen, usuario_test):
    inventario_service.registrar_entrada(
        db_session,
        producto_id=producto_test.id,
        sucursal_id=sucursal_origen.id,
        cantidad=20,
        usuario_id=usuario_test.id,
    )
    ventas_service.crear_venta(
        db_session,
        sucursal_id=sucursal_origen.id,
        usuario_id=usuario_test.id,
        items=[{"producto_id": producto_test.id, "cantidad": 10}],
    )
    # queda stock_actual=10, vendido_en_periodo=10 -> índice esperado 1.0

    resultados = reportes_service.rotacion_stock(db_session, dias=30, sucursal_id=sucursal_origen.id)

    fila = next(r for r in resultados if r["producto_id"] == producto_test.id)
    assert fila["stock_actual"] == 10
    assert fila["vendido_en_periodo"] == 10
    assert fila["indice_rotacion"] == 1.0
