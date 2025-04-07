from datetime import datetime, date
from typing import Optional, Dict
from uuid import UUID
from pydantic import BaseModel

class AuditoriaExecucaoBase(BaseModel):
    """Modelo base para AuditoriaExecucao"""
    data_execucao: datetime
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    total_protocolos: int = 0
    total_divergencias: int = 0
    total_fichas: int = 0
    total_guias: int = 0
    total_resolvidas: int = 0
    total_execucoes: int = 0
    divergencias_por_tipo: Optional[Dict] = None
    metricas_adicionais: Optional[Dict] = None
    status: str = "em_andamento"

class AuditoriaExecucaoCreate(AuditoriaExecucaoBase):
    pass

class AuditoriaExecucaoUpdate(AuditoriaExecucaoBase):
    # Todos os campos como opcionais para update parcial
    data_execucao: Optional[datetime] = None
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    total_protocolos: Optional[int] = None
    total_divergencias: Optional[int] = None
    total_fichas: Optional[int] = None
    total_guias: Optional[int] = None
    total_resolvidas: Optional[int] = None
    total_execucoes: Optional[int] = None
    divergencias_por_tipo: Optional[Dict] = None
    metricas_adicionais: Optional[Dict] = None
    status: Optional[str] = None

class AuditoriaExecucao(AuditoriaExecucaoBase):
    """Modelo para a entidade AuditoriaExecucao"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True 