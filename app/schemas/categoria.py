from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CategoriaBase(BaseModel):
    nombre_categoria: str = Field(..., min_length=3, max_length=100, example="Redes & VPN")
    descripcion: Optional[str] = Field(None, example="Problemas de conectividad remota o WiFi")
    tiempo_resolucion_horas: int = Field(..., gt=0, example=8, description="SLA de resolución en horas")
    tiempo_primera_respuesta_horas: int = Field(4, gt=0, example=1, description="SLA de 1ra respuesta en horas")


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaResponse(CategoriaBase):
    id_categoria: int
    activo: bool
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)