from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


class RolSimpleResponse(BaseModel):
    id_rol: int
    nombre_rol: str

    model_config = ConfigDict(from_attributes=True)


class UsuarioResponse(BaseModel):
    id_usuario: int
    id_rol: int
    nombre: str
    apellido: str
    correo: EmailStr
    telefono: Optional[str] = None
    departamento: Optional[str] = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    rol: RolSimpleResponse

    model_config = ConfigDict(from_attributes=True)


class UsuarioPaginationResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[UsuarioResponse]