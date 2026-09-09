from datetime import datetime, timedelta
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.ticket import Ticket
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    @staticmethod
    def _generate_ticket_code(db: Session) -> str:
        current_year = datetime.now().year
        total_tickets = db.query(Ticket).count() + 1
        return f"TCK-{current_year}-{total_tickets:04d}"

    @classmethod
    def create_ticket(cls, db: Session, ticket_in: TicketCreate) -> Ticket:
        # Validar categoría
        categoria = db.query(Categoria).filter(
            Categoria.id_categoria == ticket_in.id_categoria,
            Categoria.activo == True
        ).first()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Categoría no encontrada o inactiva"
            )

        # Validar solicitante
        solicitante = db.query(Usuario).filter(
            Usuario.id_usuario == ticket_in.id_solicitante,
            Usuario.activo == True
        ).first()
        if not solicitante:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Usuario solicitante no existe o está inactivo"
            )

        # Validar asignado (si se proporciona)
        if ticket_in.id_asignado:
            asignado = db.query(Usuario).filter(
                Usuario.id_usuario == ticket_in.id_asignado,
                Usuario.activo == True
            ).first()
            if not asignado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Usuario asignado no existe o está inactivo"
                )

        # SLA inicial calculado por categoría
        now = datetime.now()
        sla_limit = now + timedelta(hours=categoria.tiempo_resolucion_horas)

        nuevo_ticket = Ticket(
            codigo_ticket=cls._generate_ticket_code(db),
            titulo=ticket_in.titulo,
            descripcion=ticket_in.descripcion,
            id_categoria=ticket_in.id_categoria,
            id_solicitante=ticket_in.id_solicitante,
            id_asignado=ticket_in.id_asignado,
            prioridad=ticket_in.prioridad,
            impacto=ticket_in.impacto,
            urgencia=ticket_in.urgencia,
            estado="Abierto",
            fecha_limite_sla=sla_limit,
        )

        db.add(nuevo_ticket)
        db.commit()
        db.refresh(nuevo_ticket)

        return cls.get_ticket_by_id(db=db, id_ticket=nuevo_ticket.id_ticket)

    @staticmethod
    def get_tickets(
        db: Session,
        page: int = 1,
        limit: int = 10,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        id_solicitante: Optional[int] = None,
        id_asignado: Optional[int] = None,
    ) -> Tuple[int, List[Ticket]]:
        query = db.query(Ticket).options(
            joinedload(Ticket.categoria),
            joinedload(Ticket.solicitante),
            joinedload(Ticket.asignado)
        )

        if estado:
            query = query.filter(Ticket.estado == estado)
        if prioridad:
            query = query.filter(Ticket.prioridad == prioridad)
        if id_solicitante:
            query = query.filter(Ticket.id_solicitante == id_solicitante)
        if id_asignado:
            query = query.filter(Ticket.id_asignado == id_asignado)

        total = query.count()
        offset = (page - 1) * limit
        tickets = query.order_by(Ticket.id_ticket.desc()).offset(offset).limit(limit).all()

        return total, tickets

    @staticmethod
    def get_ticket_by_id(db: Session, id_ticket: int) -> Ticket:
        """
        Recupera un ticket por su ID cargando todas las relaciones mediante joinedload.
        Lanza HTTP 404 si el ticket no existe.
        """
        ticket = (
            db.query(Ticket)
            .options(
                joinedload(Ticket.categoria),
                joinedload(Ticket.solicitante),
                joinedload(Ticket.asignado)
            )
            .filter(Ticket.id_ticket == id_ticket)
            .first()
        )
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket con ID {id_ticket} no fue encontrado"
            )
        return ticket

    @classmethod
    def update_ticket(cls, db: Session, id_ticket: int, ticket_in: TicketUpdate) -> Ticket:
        """
        Actualiza los campos enviados del ticket y gestiona los hitos de ciclo de vida ITIL:
        - 'En Proceso': fija fecha_primera_respuesta si aún no existe.
        - 'Resuelto': fija fecha_resolucion.
        - 'Cerrado': fija fecha_cierre.
        """
        ticket = cls.get_ticket_by_id(db=db, id_ticket=id_ticket)
        update_data = ticket_in.model_dump(exclude_unset=True)

        # 1. Validaciones de integridad referencial opcionales
        if "id_categoria" in update_data and update_data["id_categoria"] is not None:
            cat = db.query(Categoria).filter(
                Categoria.id_categoria == update_data["id_categoria"],
                Categoria.activo == True
            ).first()
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="La categoría especificada no existe o está inactiva"
                )

        if "id_asignado" in update_data and update_data["id_asignado"] is not None:
            asig = db.query(Usuario).filter(
                Usuario.id_usuario == update_data["id_asignado"],
                Usuario.activo == True
            ).first()
            if not asig:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El usuario asignado especificado no existe o está inactivo"
                )

        # 2. Reglas de Ciclo de Vida ITIL
        if "estado" in update_data and update_data["estado"] is not None:
            nuevo_estado = update_data["estado"]
            ahora = datetime.now()

            if nuevo_estado == "En Proceso" and ticket.fecha_primera_respuesta is None:
                ticket.fecha_primera_respuesta = ahora

            elif nuevo_estado == "Resuelto":
                ticket.fecha_resolucion = ahora
                # Si pasa directo a resuelto sin haber registrado primera respuesta:
                if ticket.fecha_primera_respuesta is None:
                    ticket.fecha_primera_respuesta = ahora

            elif nuevo_estado == "Cerrado":
                ticket.fecha_cierre = ahora
                if ticket.fecha_resolucion is None:
                    ticket.fecha_resolucion = ahora

        # 3. Aplicar cambios a las columnas
        for field, value in update_data.items():
            setattr(ticket, field, value)

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return cls.get_ticket_by_id(db=db, id_ticket=ticket.id_ticket)