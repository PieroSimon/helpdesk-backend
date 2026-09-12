from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.usuario import UsuarioResponse, UsuarioPaginationResponse
from app.services.usuario_service import UsuarioService

router = APIRouter()


@router.get("/", response_model=UsuarioPaginationResponse, summary="Listar usuarios activos paginados y filtrados")
def list_usuarios(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Registros por página"),
    id_rol: Optional[int] = Query(None, description="Filtrar por identificador de rol"),
    departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    db: Session = Depends(get_db)
):
    total, usuarios = UsuarioService.get_usuarios(
        db=db,
        page=page,
        limit=limit,
        id_rol=id_rol,
        departamento=departamento
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": usuarios
    }


@router.get("/{id_usuario}", response_model=UsuarioResponse, summary="Obtener detalle de usuario por ID")
def get_usuario(
    id_usuario: int = Path(..., gt=0, description="ID único del usuario"),
    db: Session = Depends(get_db)
):
    return UsuarioService.get_usuario_by_id(db=db, id_usuario=id_usuario)