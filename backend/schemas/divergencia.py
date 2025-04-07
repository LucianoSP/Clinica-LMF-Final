from datetime import datetime, date
from typing import Optional, Dict
from uuid import UUID
from pydantic import BaseModel
from enum import Enum

class TipoDivergencia(str, Enum):
    DUPLICIDADE = 'duplicidade'
    DADOS_INVALIDOS = 'dados_invalidos'
    FALTA_ASSINATURA = 'falta_assinatura'
    FALTA_BIOMETRIA = 'falta_biometria'
    SESAO_NAO_ENCONTRADA = 'sesao_nao_encontrada'
    GUIA_INVALIDA = 'guia_invalida'

class StatusDivergencia(str, Enum):
    PENDENTE = 'pendente'
    EM_ANALISE = 'em_analise'
    RESOLVIDA = 'resolvida'
    CANCELADA = 'cancelada'

class PrioridadeDivergencia(str, Enum):
    BAIXA = 'BAIXA'
    MEDIA = 'MEDIA'
    ALTA = 'ALTA'

class DivergenciaBase(BaseModel):
    """Modelo base para Divergencia"""
    numero_guia: str
    tipo: TipoDivergencia
    descricao: Optional[str] = None
    paciente_nome: Optional[str] = None
    codigo_ficha: Optional[str] = None
    data_execucao: Optional[date] = None
    data_atendimento: Optional[date] = None
    carteirinha: Optional[str] = None
    prioridade: PrioridadeDivergencia = PrioridadeDivergencia.MEDIA
    status: StatusDivergencia = StatusDivergencia.PENDENTE
    detalhes: Optional[Dict] = None
    ficha_id: Optional[UUID] = None
    execucao_id: Optional[UUID] = None
    sessao_id: Optional[UUID] = None
    paciente_id: Optional[UUID] = None
    tentativas_resolucao: int = 0

class DivergenciaCreate(DivergenciaBase):
    pass

class DivergenciaUpdate(BaseModel):
    """Modelo para atualização de Divergencia"""
    numero_guia: Optional[str] = None
    tipo: Optional[TipoDivergencia] = None
    descricao: Optional[str] = None
    paciente_nome: Optional[str] = None
    codigo_ficha: Optional[str] = None
    data_execucao: Optional[date] = None
    data_atendimento: Optional[date] = None
    carteirinha: Optional[str] = None
    prioridade: Optional[PrioridadeDivergencia] = None
    status: Optional[StatusDivergencia] = None
    detalhes: Optional[Dict] = None
    ficha_id: Optional[UUID] = None
    execucao_id: Optional[UUID] = None
    sessao_id: Optional[UUID] = None
    paciente_id: Optional[UUID] = None
    tentativas_resolucao: Optional[int] = None
    data_resolucao: Optional[datetime] = None
    resolvido_por: Optional[UUID] = None

class Divergencia(DivergenciaBase):
    """Modelo para a entidade Divergencia"""
    id: UUID
    data_identificacao: datetime
    data_resolucao: Optional[datetime] = None
    resolvido_por: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True 