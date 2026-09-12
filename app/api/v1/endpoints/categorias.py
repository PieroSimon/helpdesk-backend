from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.categoria import CategoriaCreate, CategoriaResponse
from app.services.categoria_service import CategoriaService

router = APIRouter()


@router.get("/", response_model=List[CategoriaResponse], summary="Listar categorías activas con SLA")
def list_categorias(db: Session = Depends(get_db)):
    return CategoriaService.get_active_categorias(db=db)


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED, summary="Crear categoría")
def create_categoria(categoria_in: CategoriaCreate, db: Session = Depends(get_db)):
    return CategoriaService.create_categoria(db=db, categoria_in=categoria_in)