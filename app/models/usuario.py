from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=False, unique=True, index=True)
    clave_hash = Column(String(255), nullable=False)
    telefono = Column(String(30))
    departamento = Column(String(100))
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    rol = relationship("Rol", back_populates="usuarios")
    tickets_solicitados = relationship("Ticket", back_populates="solicitante", foreign_keys="Ticket.id_solicitante")
    tickets_asignados = relationship("Ticket", back_populates="asignado", foreign_keys="Ticket.id_asignado")