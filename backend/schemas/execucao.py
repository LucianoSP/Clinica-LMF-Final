from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enum import Enum

class StatusBiometria(str, Enum):
    NAO_VERIFICADO = "nao_verificado"
    VERIFICADO = "verificado"
    FALHA = "falha"

class ExecucaoBase(BaseModel):
    """Modelo base para Execucao"""
    guia_id: UUID
    sessao_id: UUID
    data_execucao: date
    data_atendimento: Optional[date] = None
    paciente_nome: str
    paciente_carteirinha: str
    numero_guia: str
    codigo_ficha: str
    codigo_ficha_temp: bool = False
    usuario_executante: Optional[UUID] = None
    origem: str = "manual"
    ip_origem: Optional[str] = None
    ordem_execucao: Optional[int] = None
    status_biometria: StatusBiometria = StatusBiometria.NAO_VERIFICADO
    conselho_profissional: Optional[str] = None
    numero_conselho: Optional[str] = None
    uf_conselho: Optional[str] = None
    codigo_cbo: Optional[str] = None
    profissional_executante: Optional[str] = None

class ExecucaoCreate(ExecucaoBase):
    pass

class ExecucaoUpdate(BaseModel):
    guia_id: Optional[UUID] = None
    sessao_id: Optional[UUID] = None
    data_execucao: Optional[date] = None
    data_atendimento: Optional[date] = None
    paciente_nome: Optional[str] = None
    paciente_carteirinha: Optional[str] = None
    numero_guia: Optional[str] = None
    codigo_ficha: Optional[str] = None
    codigo_ficha_temp: Optional[bool] = None
    usuario_executante: Optional[UUID] = None
    origem: Optional[str] = None
    ip_origem: Optional[str] = None
    ordem_execucao: Optional[int] = None
    status_biometria: Optional[StatusBiometria] = None
    conselho_profissional: Optional[str] = None
    numero_conselho: Optional[str] = None
    uf_conselho: Optional[str] = None
    codigo_cbo: Optional[str] = None
    profissional_executante: Optional[str] = None

class Execucao(ExecucaoBase):
    """Modelo para a entidade Execucao"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None

    class Config:
        from_attributes = True