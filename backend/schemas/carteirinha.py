from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel

class CarteirinhaBase(BaseModel):
    """Modelo base para Carteirinha"""
    paciente_id: UUID
    plano_saude_id: UUID
    numero_carteirinha: str
    data_validade: Optional[date] = None
    status: str = "ativa"
    motivo_inativacao: Optional[str] = None
    historico_status: Optional[List[dict]] = None

class CarteirinhaCreate(CarteirinhaBase):
    pass

class CarteirinhaUpdate(CarteirinhaBase):
    paciente_id: Optional[UUID] = None
    plano_saude_id: Optional[UUID] = None
    numero_carteirinha: Optional[str] = None
    data_validade: Optional[date] = None
    status: Optional[str] = None
    motivo_inativacao: Optional[str] = None
    historico_status: Optional[List[dict]] = None

class Carteirinha(CarteirinhaBase):
    """Modelo para a entidade Carteirinha"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True
