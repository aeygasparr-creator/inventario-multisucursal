from sqlalchemy.orm import declarative_base

Base = declarative_base()

# A medida que se creen los modelos (Fase 1 en adelante), se importan aquí
# para que Alembic los detecte al generar migraciones automáticas.
# Ejemplo: from app.models.usuario import Usuario
