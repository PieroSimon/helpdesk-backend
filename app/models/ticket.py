from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id_ticket = Column(Integer, primary_key=True, index=True)
    codigo_ticket = Column(String(20), nullable=False, unique=True, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    id_solicitante = Column(Integer, ForeignKey("usuarios.id_usuario", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    id_asignado = Column(Integer, ForeignKey("usuarios.id_usuario", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)
    prioridad = Column(String(20), nullable=False, default="Media")
    estado = Column(String(20), nullable=False, default="Abierto")
    impacto = Column(String(20), default="Medio")
    urgencia = Column(String(20), default="Media")
    fecha_limite_sla = Column(DateTime, nullable=True)
    fecha_primera_respuesta = Column(DateTime, nullable=True)
    fecha_resolucion = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
    actualizado_en = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    categoria = relationship("Categoria", back_populates="tickets")
    solicitante = relationship("Usuario", foreign_keys=[id_solicitante], back_populates="tickets_solicitados")
    asignado = relationship("Usuario", foreign_keys=[id_asignado], back_populates="tickets_asignados")
    