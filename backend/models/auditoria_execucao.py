from datetime import datetime, date
from typing import Optional, Union, Dict
from pydantic import BaseModel, field_validator


class AuditoriaExecucaoBase(BaseModel):
    """Modelo base para AuditoriaExecucao"""
    data_execucao: date
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

    @field_validator('data_execucao', 'data_inicial', 'data_final', mode='before')
    @classmethod
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                # Tenta primeiro o formato ISO
                return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except ValueError:
                try:
                    # Tenta o formato dd/mm/yyyy
                    return datetime.strptime(value, '%d/%m/%Y').date()
                except ValueError:
                    try:
                        # Tenta o formato yyyy-mm-dd
                        return datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValueError(f'Data inválida: {value}')
        raise ValueError(f'Formato de data inválido: {value}')

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }


class AuditoriaExecucaoCreate(AuditoriaExecucaoBase):
    """Modelo para criação de AuditoriaExecucao"""
    pass


class AuditoriaExecucaoUpdate(BaseModel):
    """Modelo para atualização de AuditoriaExecucao"""
    data_execucao: Optional[date] = None
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

    @field_validator('data_execucao', 'data_inicial', 'data_final', mode='before')
    @classmethod
    def parse_date(cls, value):
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                # Tenta primeiro o formato ISO
                return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
            except ValueError:
                try:
                    # Tenta o formato dd/mm/yyyy
                    return datetime.strptime(value, '%d/%m/%Y').date()
                except ValueError:
                    try:
                        # Tenta o formato yyyy-mm-dd
                        return datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        raise ValueError(f'Data inválida: {value}')
        raise ValueError(f'Formato de data inválido: {value}')

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }


class AuditoriaExecucao(AuditoriaExecucaoBase):
    """Modelo completo de AuditoriaExecucao"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True 