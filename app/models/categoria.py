from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    tiempo_resolucion_horas = Column(Integer, nullable=False, default=24)
    tiempo_primera_respuesta_horas = Column(Integer, nullable=False, default=4)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    tickets = relationship("Ticket", back_populates="categoria")

    