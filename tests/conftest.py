import uuid

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.db import base_all  # noqa: F401  (registra todos los modelos en Base.metadata)
from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.models.usuario import RolEnum, Usuario

engine = create_engine(settings.database_url)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def db_session():
    """Cada test corre dentro de su propia transacción, que se revierte al
    final (rollback). Aunque el código bajo prueba llame a db.commit()
    internamente, un listener reabre un SAVEPOINT automáticamente, así que
    nada de lo que pase en el test sobrevive más allá de ese test — se
    prueba contra la base de datos real sin ensuciarla.
    """
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _reabrir_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def usuario_test(db_session):
    usuario = Usuario(
        nombre="Usuario de prueba",
        email=f"test-{uuid.uuid4()}@test.com",
        password_hash=hash_password("test1234"),
        rol=RolEnum.admin,
    )
    db_session.add(usuario)
    db_session.flush()
    return usuario


@pytest.fixture()
def sucursal_origen(db_session):
    sucursal = Sucursal(nombre="Sucursal origen (test)", ciudad="Lima")
    db_session.add(sucursal)
    db_session.flush()
    return sucursal


@pytest.fixture()
def sucursal_destino(db_session):
    sucursal = Sucursal(nombre="Sucursal destino (test)", ciudad="Arequipa")
    db_session.add(sucursal)
    db_session.flush()
    return sucursal


@pytest.fixture()
def categoria_test(db_session):
    categoria = Categoria(nombre=f"Categoría test {uuid.uuid4()}")
    db_session.add(categoria)
    db_session.flush()
    return categoria


@pytest.fixture()
def producto_test(db_session, categoria_test):
    producto = Producto(
        sku=f"TEST-{uuid.uuid4().hex[:8]}",
        nombre="Producto de prueba",
        categoria_id=categoria_test.id,
        precio_unitario=10,
    )
    db_session.add(producto)
    db_session.flush()
    return producto
