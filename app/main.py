from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.routers import (
    auth,
    categorias,
    inventario,
    ordenes_compra,
    productos,
    proveedores,
    reportes,
    sucursales,
    ventas,
)
from app.core.swagger_theme import HUD_THEME_CSS
from app.db.session import get_db

DESCRIPCION = """
API REST para gestionar inventario, transferencias entre sucursales,
compras a proveedores y ventas de una cadena de tiendas con múltiples
locales.

**Funcionalidades:**
* Autenticación JWT con roles (`admin`, `gerente_sucursal`, `vendedor`)
* Sucursales, categorías y productos
* Inventario por sucursal con transferencias atómicas (sin stock fantasma)
* Proveedores y órdenes de compra (suman stock al recibirse)
* Ventas: validan y descuentan stock antes de confirmar
* Reportes: productos más vendidos, ventas por sucursal/periodo, alertas de quiebre, rotación de stock

**Cómo probar la API aquí:**
1. Crea un usuario en `POST /auth/register`
2. Inicia sesión en `POST /auth/login`
3. Haz clic en **Authorize** (arriba a la derecha) e ingresa tus credenciales
4. Ya puedes probar los endpoints protegidos

Proyecto de portafolio — Ingeniería de Sistemas.
"""

TAGS_METADATA = [
    {
        "name": "auth",
        "description": "Registro e inicio de sesión. Genera el token JWT que protege el resto de la API.",
    },
    {
        "name": "sucursales",
        "description": "Gestión de las sucursales (tiendas) de la cadena. Solo `admin` puede crear, editar o eliminar.",
    },
    {
        "name": "categorias",
        "description": "Categorías del catálogo de productos. Solo `admin` puede crear, editar o eliminar.",
    },
    {
        "name": "productos",
        "description": "Catálogo de productos. `admin` y `gerente_sucursal` pueden crear y editar.",
    },
    {
        "name": "inventario",
        "description": (
            "Stock por sucursal: entradas, salidas y transferencias. "
            "Las transferencias son atómicas: si algo falla, no queda stock "
            "descontado de un lado sin haberse sumado en el otro."
        ),
    },
    {
        "name": "proveedores",
        "description": "Proveedores de mercadería. Solo `admin` puede crear, editar o eliminar.",
    },
    {
        "name": "ordenes_compra",
        "description": (
            "Órdenes de compra a proveedores. Se crean en estado 'pendiente' y "
            "el stock se suma recién al marcarlas como 'recibidas'."
        ),
    },
    {
        "name": "ventas",
        "description": (
            "Registro de ventas. Antes de confirmar, valida que haya stock "
            "suficiente de cada producto; si falta stock de cualquiera, "
            "la venta completa se rechaza sin descontar nada."
        ),
    },
    {
        "name": "reportes",
        "description": (
            "Analítica de solo lectura: productos más vendidos, ventas por "
            "sucursal y periodo, alertas de quiebre de stock y rotación de "
            "inventario. Pensado para conectar con Power BI."
        ),
    },
]

SWAGGER_UI_PARAMETERS = {
    "persistAuthorization": True,  # ya no se pierde el login al recargar
    "docExpansion": "list",  # secciones cerradas por defecto, menos scroll
    "defaultModelsExpandDepth": -1,  # oculta el bloque de "Schemas" del final
    "displayRequestDuration": True,
}

app = FastAPI(
    title="Sistema de Inventario y Ventas Multi-sucursal",
    description=DESCRIPCION,
    version="0.1.0",
    openapi_tags=TAGS_METADATA,
    docs_url=None,  # se reemplaza por la versión con tema oscuro más abajo
    swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
)

# Permite que el panel en React (que corre en otro puerto, ej. localhost:5173)
# pueda llamar a esta API desde el navegador sin que CORS lo bloquee.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/docs", include_in_schema=False)
async def swagger_ui_html_personalizado():
    """Sirve Swagger con el tema oscuro tipo consola (estilo HUD)."""
    respuesta = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} — Panel de control",
        swagger_ui_parameters=SWAGGER_UI_PARAMETERS,
    )
    html = respuesta.body.decode("utf-8").replace("</head>", HUD_THEME_CSS + "</head>")
    return HTMLResponse(html)


@app.get("/", include_in_schema=False)
def root():
    """Redirige la raíz del sitio a la documentación interactiva."""
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["sistema"], summary="Estado de la API")
def health_check():
    """Verifica que la API está viva."""
    return {"status": "ok"}


@app.get("/health/db", tags=["sistema"], summary="Estado de la conexión a PostgreSQL")
def health_check_db(db: Session = Depends(get_db)):
    """Verifica que la API puede conectarse y consultar PostgreSQL."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(sucursales.router, prefix="/api/v1/sucursales", tags=["sucursales"])
app.include_router(categorias.router, prefix="/api/v1/categorias", tags=["categorias"])
app.include_router(productos.router, prefix="/api/v1/productos", tags=["productos"])
app.include_router(inventario.router, prefix="/api/v1/inventario", tags=["inventario"])
app.include_router(proveedores.router, prefix="/api/v1/proveedores", tags=["proveedores"])
app.include_router(
    ordenes_compra.router, prefix="/api/v1/ordenes-compra", tags=["ordenes_compra"]
)
app.include_router(ventas.router, prefix="/api/v1/ventas", tags=["ventas"])
app.include_router(reportes.router, prefix="/api/v1/reportes", tags=["reportes"])
