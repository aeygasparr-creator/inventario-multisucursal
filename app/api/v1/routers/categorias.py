import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_roles
from app.db.session import get_db
from app.models.categoria import Categoria
from app.models.usuario import RolEnum
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate

router = APIRouter()


@router.get("/", response_model=List[CategoriaOut], summary="Listar categorías")
def listar_categorias(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Categoria).all()


@router.post(
    "/", response_model=CategoriaOut, status_code=201, summary="Crear categoría (solo admin)"
)
def crear_categoria(
    payload: CategoriaCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    categoria = Categoria(**payload.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put(
    "/{categoria_id}", response_model=CategoriaOut, summary="Actualizar categoría (solo admin)"
)
def actualizar_categoria(
    categoria_id: uuid.UUID,
    payload: CategoriaUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete(
    "/{categoria_id}", status_code=204, summary="Eliminar categoría (solo admin)"
)
def eliminar_categoria(
    categoria_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RolEnum.admin)),
):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(categoria)
    db.commit()
