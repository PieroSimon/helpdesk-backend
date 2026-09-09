from typing import Optional, Literal
from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketPaginationResponse
)
from app.services.ticket_service import TicketService

router = APIRouter()


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo Ticket"
)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Registra un ticket de soporte calculando automáticamente:
    - Código único del ticket (TCK-YYYY-XXXX).
    - Fecha límite de SLA en base a la categoría seleccionada.
    """
    return TicketService.create_ticket(db=db, ticket_in=ticket_in)


@router.get(
    "/",
    response_model=TicketPaginationResponse,
    summary="Listar tickets con paginación y filtros"
)
def list_tickets(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad de registros por página"),
    estado: Optional[Literal["Abierto", "En Proceso", "Resuelto", "Cerrado"]] = Query(None, description="Filtrar por estado ITIL"),
    prioridad: Optional[Literal["Baja", "Media", "Alta", "Critica"]] = Query(None, description="Filtrar por prioridad"),
    id_solicitante: Optional[int] = Query(None, description="Filtrar por ID del solicitante"),
    id_asignado: Optional[int] = Query(None, description="Filtrar por ID del técnico asignado"),
    db: Session = Depends(get_db)
):
    total, tickets = TicketService.get_tickets(
        db=db,
        page=page,
        limit=limit,
        estado=estado,
        prioridad=prioridad,
        id_solicitante=id_solicitante,
        id_asignado=id_asignado
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": tickets
    }


@router.get(
    "/{id_ticket}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar un Ticket por ID"
)
def get_ticket(
    id_ticket: int = Path(..., gt=0, description="ID numérico del ticket"),
    db: Session = Depends(get_db)
):
    """
    Retorna la información completa de un ticket incluyendo datos anidados de:
    - Solicitante
    - Agente asignado
    - Categoría y SLA
    """
    return TicketService.get_ticket_by_id(db=db, id_ticket=id_ticket)


@router.patch(
    "/{id_ticket}",
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un Ticket - Ciclo de Vida ITIL"
)
def update_ticket(
    ticket_in: TicketUpdate,
    id_ticket: int = Path(..., gt=0, description="ID numérico del ticket a actualizar"),
    db: Session = Depends(get_db)
):
    """
    Permite actualizar atributos del ticket de soporte aplicando reglas ITIL:
    - Cambio a **'En Proceso'**: si `fecha_primera_respuesta` es nula, se asigna el timestamp actual.
    - Cambio a **'Resuelto'**: se asigna automáticamente `fecha_resolucion`.
    - Cambio a **'Cerrado'**: se asigna automáticamente `fecha_cierre`.
    """
    return TicketService.update_ticket(db=db, id_ticket=id_ticket, ticket_in=ticket_in)