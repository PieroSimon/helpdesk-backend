from fastapi import APIRouter
from app.api.v1.endpoints import tickets, usuarios, categorias

api_router = APIRouter()
api_router.include_router(tickets.router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(categorias.router, prefix="/categorias", tags=["Categorías"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])