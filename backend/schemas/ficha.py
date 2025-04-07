from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class StatusFicha(str, Enum):
    PENDENTE = "pendente"
    CONFERIDA = "conferida"
    FATURADA = "faturada"
    CANCELADA = "cancelada"


class FichaBase(BaseModel):
    """Modelo base para Ficha"""
    codigo_ficha: Optional[str] = None
    numero_guia: str
    paciente_nome: str
    paciente_carteirinha: str
    arquivo_digitalizado: Optional[str] = None
    arquivo_hash: Optional[str] = None
    observacoes: Optional[str] = None
    status: StatusFicha = StatusFicha.PENDENTE
    data_atendimento: date
    sessoes_conferidas: Optional[int] = 0

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v) if v is not None else None,
            date: lambda v: v.isoformat() if v is not None else None,
            StatusFicha: lambda v: v.value if v is not None else None
        }


class FichaCreate(FichaBase):
    pass


class FichaUpdate(BaseModel):
    codigo_ficha: Optional[str] = None
    numero_guia: Optional[str] = None
    paciente_nome: Optional[str] = None
    paciente_carteirinha: Optional[str] = None
    arquivo_digitalizado: Optional[str] = None
    arquivo_hash: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[StatusFicha] = None
    data_atendimento: Optional[date] = None
    sessoes_conferidas: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v) if v is not None else None,
            date: lambda v: v.isoformat() if v is not None else None,
            StatusFicha: lambda v: v.value if v is not None else None
        }


class Ficha(FichaBase):
    """Modelo para a entidade Ficha"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v is not None else None,
            date: lambda v: v.isoformat() if v is not None else None,
            StatusFicha: lambda v: v.value if v is not None else None
        }
