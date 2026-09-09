from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(255))
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

    usuarios = relationship("Usuario", back_populates="rol")
    