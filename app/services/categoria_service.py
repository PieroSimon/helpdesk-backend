from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate


class CategoriaService:
    @staticmethod
    def get_active_categorias(db: Session) -> List[Categoria]:
        return db.query(Categoria).filter(Categoria.activo == True).order_by(Categoria.id_categoria.asc()).all()

    @staticmethod
    def create_categoria(db: Session, categoria_in: CategoriaCreate) -> Categoria:
        existing = db.query(Categoria).filter(
            Categoria.nombre_categoria.ilike(categoria_in.nombre_categoria.strip())
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría registrada con el nombre '{categoria_in.nombre_categoria}'"
            )

        nueva_categoria = Categoria(
            nombre_categoria=categoria_in.nombre_categoria.strip(),
            descripcion=categoria_in.descripcion,
            tiempo_resolucion_horas=categoria_in.tiempo_resolucion_horas,
            tiempo_primera_respuesta_horas=categoria_in.tiempo_primera_respuesta_horas,
            activo=True
        )
        db.add(nueva_categoria)
        db.commit()
        db.refresh(nueva_categoria)
        return nueva_categoria