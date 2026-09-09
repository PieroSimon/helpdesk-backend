from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UsuarioSimpleResponse(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    correo: str
    departamento: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategoriaSimpleResponse(BaseModel):
    id_categoria: int
    nombre_categoria: str
    tiempo_resolucion_horas: int

    model_config = ConfigDict(from_attributes=True)


class TicketBase(BaseModel):
    titulo: str = Field(..., min_length=5, max_length=200, example="Falla en conexión a VPN corporativa")
    descripcion: str = Field(..., min_length=10, example="No puedo autenticarme al servidor remoto desde casa")
    id_categoria: int = Field(..., gt=0)
    id_solicitante: int = Field(..., gt=0)
    id_asignado: Optional[int] = Field(None, gt=0)
    prioridad: Literal["Baja", "Media", "Alta", "Critica"] = "Media"
    impacto: Optional[Literal["Bajo", "Medio", "Alto"]] = "Medio"
    urgencia: Optional[Literal["Baja", "Media", "Alta"]] = "Media"


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=5, max_length=200)
    descripcion: Optional[str] = None
    id_categoria: Optional[int] = None
    id_asignado: Optional[int] = None
    prioridad: Optional[Literal["Baja", "Media", "Alta", "Critica"]] = None
    estado: Optional[Literal["Abierto", "En Proceso", "Resuelto", "Cerrado"]] = None
    impacto: Optional[Literal["Bajo", "Medio", "Alto"]] = None
    urgencia: Optional[Literal["Baja", "Media", "Alta"]] = None


class TicketResponse(BaseModel):
    id_ticket: int
    codigo_ticket: str
    titulo: str
    descripcion: str
    prioridad: str
    estado: str
    impacto: Optional[str]
    urgencia: Optional[str]
    fecha_limite_sla: Optional[datetime]
    fecha_primera_respuesta: Optional[datetime]
    fecha_resolucion: Optional[datetime]
    fecha_cierre: Optional[datetime]
    creado_en: datetime
    actualizado_en: datetime

    categoria: CategoriaSimpleResponse
    solicitante: UsuarioSimpleResponse
    asignado: Optional[UsuarioSimpleResponse] = None

    model_config = ConfigDict(from_attributes=True)


class TicketPaginationResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[TicketResponse]