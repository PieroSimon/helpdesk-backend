from typing import Tuple, List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.usuario import Usuario


class UsuarioService:
    @staticmethod
    def get_usuarios(
        db: Session,
        page: int = 1,
        limit: int = 10,
        id_rol: Optional[int] = None,
        departamento: Optional[str] = None,
    ) -> Tuple[int, List[Usuario]]:
        query = db.query(Usuario).options(joinedload(Usuario.rol)).filter(Usuario.activo == True)

        if id_rol is not None:
            query = query.filter(Usuario.id_rol == id_rol)
        if departamento:
            query = query.filter(Usuario.departamento.ilike(f"%{departamento.strip()}%"))

        total = query.count()
        offset = (page - 1) * limit
        usuarios = query.order_by(Usuario.id_usuario.asc()).offset(offset).limit(limit).all()

        return total, usuarios

    @staticmethod
    def get_usuario_by_id(db: Session, id_usuario: int) -> Usuario:
        usuario = (
            db.query(Usuario)
            .options(joinedload(Usuario.rol))
            .filter(Usuario.id_usuario == id_usuario, Usuario.activo == True)
            .first()
        )
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {id_usuario} no fue encontrado o está inactivo"
            )
        return usuario