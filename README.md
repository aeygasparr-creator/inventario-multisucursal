# Sistema de Inventario y Ventas Multi-sucursal

![Tests](https://github.com/aeygasparr-creator/inventario-multisucursal/actions/workflows/tests.yml/badge.svg)

API backend con FastAPI + PostgreSQL para gestionar inventario, transferencias
entre sucursales, compras a proveedores y ventas de una cadena de tiendas,
con reportes pensados para conectar con Power BI.



## Funcionalidades

- **Autenticación JWT con roles** (`admin`, `gerente_sucursal`, `vendedor`)
- **Sucursales, categorías y productos** con CRUD protegido por rol
- **Inventario multi-sucursal** con transferencias atómicas (sin stock fantasma:
  si algo falla a mitad de camino, no queda descontado de un lado sin sumarse al otro)
- **Proveedores y órdenes de compra**: se crean en `pendiente` y suman stock
  automáticamente al marcarse como `recibida`
- **Ventas**: validan y descuentan stock antes de confirmar; si falta stock de
  cualquier producto, la venta completa se rechaza. El precio se toma del
  catálogo, no del request, para que no se pueda manipular
- **Reportes**: productos más vendidos, ventas por sucursal/periodo, alertas
  de quiebre de stock, rotación de inventario
- **10 tests con pytest** sobre la lógica transaccional, corriendo en
  GitHub Actions en cada push

## Stack

FastAPI · PostgreSQL · SQLAlchemy · Alembic · JWT (python-jose + passlib) ·
Docker Compose · pytest · GitHub Actions

## Cómo levantar el proyecto

1. Copia el archivo de variables de entorno:
   ```
   copy .env.example .env
   ```
   (en Mac/Linux: `cp .env.example .env`)

2. Edita `.env` si quieres cambiar el usuario/contraseña de PostgreSQL o el
   `SECRET_KEY` (para producción, este debe ser una clave larga y aleatoria).

3. Levanta los contenedores:
   ```
   docker compose up --build
   ```

4. Verifica que todo esté funcionando abriendo en el navegador:
   - `http://localhost:8000/` → redirige a la documentación
   - `http://localhost:8000/docs` → documentación interactiva (Swagger UI)
   - `http://localhost:8000/health/db` → confirma que la API se conecta a PostgreSQL

5. Para probar los endpoints protegidos: crea un usuario en
   `POST /api/v1/auth/register`, inicia sesión en `POST /api/v1/auth/login`,
   y usa el botón **Authorize** de Swagger con esas credenciales.

## Estructura del proyecto

```
app/
├── main.py               # Punto de entrada de FastAPI
├── core/                 # Configuración, seguridad (JWT/hashing), dependencias de auth
├── db/                   # Conexión y sesión de SQLAlchemy
├── models/                # Modelos de las 11 tablas
├── schemas/                # Esquemas Pydantic (request/response)
├── services/                # Lógica de negocio: transferencias, compras, ventas, reportes
├── api/v1/routers/           # Endpoints agrupados por dominio
alembic/                      # Migraciones de base de datos
tests/                        # Pruebas con pytest (rollback automático por test)
.github/workflows/             # CI: corre los tests en cada push
```

## Comandos útiles

```
# Generar una migración automática después de crear/editar modelos
docker compose exec api alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones pendientes
docker compose exec api alembic upgrade head

# Correr los tests
docker compose exec api pytest -v

# Ver logs de la API
docker compose logs -f api
```

## Panel de administración (React)

Este repositorio incluye también un panel visual en `frontend/`, hecho en
React + TypeScript, con la misma estética oscura del Swagger. Instrucciones
completas en `frontend/README.md`; en resumen:

```
cd frontend
npm install
copy .env.example .env
npm run dev
```

Luego abre `http://localhost:5173` (con el backend ya corriendo en el 8000).

## Próximos pasos (fuera de este repositorio)

- Dashboard en Power BI conectado a los endpoints de `/api/v1/reportes`
