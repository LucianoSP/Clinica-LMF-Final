from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

class SessaoBase(BaseModel):
    """Modelo base para Sessao"""
    ficha_id: UUID
    data_sessao: date
    possui_assinatura: Optional[bool] = False
    procedimento_id: Optional[UUID] = None
    profissional_executante: Optional[str] = None
    valor_sessao: Optional[Decimal] = Field(None, ge=0)
    status: str = "pendente"
    valor_faturado: Optional[Decimal] = Field(None, ge=0)
    observacoes_sessao: Optional[str] = None
    executado: Optional[bool] = False
    data_execucao: Optional[date] = None
    executado_por: Optional[UUID] = None
    paciente_id: Optional[UUID] = None

class SessaoCreate(SessaoBase):
    pass

class SessaoUpdate(BaseModel):
    """Modelo para atualização de Sessao"""
    ficha_id: Optional[UUID] = None
    data_sessao: Optional[date] = None
    possui_assinatura: Optional[bool] = None
    procedimento_id: Optional[UUID] = None
    profissional_executante: Optional[str] = None
    valor_sessao: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = None
    valor_faturado: Optional[Decimal] = Field(None, ge=0)
    observacoes_sessao: Optional[str] = None
    executado: Optional[bool] = None
    data_execucao: Optional[date] = None
    executado_por: Optional[UUID] = None
    paciente_id: Optional[UUID] = None

class Sessao(SessaoBase):
    """Modelo completo para Sessao"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True