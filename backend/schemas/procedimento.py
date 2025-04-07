from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal

class ProcedimentoBase(BaseModel):
    """Modelo base para Procedimento"""
    codigo: str = Field(..., min_length=1, max_length=20)
    nome: str
    descricao: Optional[str] = None
    tipo: str  # tipo_procedimento
    valor: Optional[Decimal] = Field(None, ge=0)
    valor_filme: Optional[Decimal] = Field(None, ge=0)
    valor_operacional: Optional[Decimal] = Field(None, ge=0)
    valor_total: Optional[Decimal] = Field(None, ge=0)
    tempo_medio_execucao: Optional[str] = None
    requer_autorizacao: bool = True
    observacoes: Optional[str] = None
    ativo: bool = True

class ProcedimentoCreate(ProcedimentoBase):
    pass

class ProcedimentoUpdate(BaseModel):
    """Modelo para atualização de Procedimento"""
    codigo: Optional[str] = Field(None, min_length=1, max_length=20)
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    valor: Optional[Decimal] = Field(None, ge=0)
    valor_filme: Optional[Decimal] = Field(None, ge=0)
    valor_operacional: Optional[Decimal] = Field(None, ge=0)
    valor_total: Optional[Decimal] = Field(None, ge=0)
    tempo_medio_execucao: Optional[str] = None
    requer_autorizacao: Optional[bool] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

class Procedimento(ProcedimentoBase):
    """Modelo para a entidade Procedimento"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True