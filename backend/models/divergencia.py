from datetime import datetime, date
from typing import Optional, Dict, Union, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from decimal import Decimal
import json

class TipoDivergencia(str, Enum):
    """Tipos possíveis de divergência"""
    FICHA_SEM_EXECUCAO = "ficha_sem_execucao"
    EXECUCAO_SEM_FICHA = "execucao_sem_ficha"
    SESSAO_SEM_ASSINATURA = "sessao_sem_assinatura"
    DATA_DIVERGENTE = "data_divergente"
    GUIA_VENCIDA = "guia_vencida"
    QUANTIDADE_EXCEDIDA = "quantidade_excedida"
    FALTA_DATA_EXECUCAO = "falta_data_execucao"
    DUPLICIDADE = "duplicidade"

class StatusDivergencia(str, Enum):
    """Status possíveis de divergência"""
    PENDENTE = "pendente"
    EM_ANALISE = "em_analise"
    RESOLVIDA = "resolvida"
    IGNORADA = "ignorada"

class PrioridadeDivergencia(str, Enum):
    """Prioridades possíveis de divergência"""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class DivergenciaBase(BaseModel):
    """Modelo base para Divergencia"""
    numero_guia: str
    tipo: TipoDivergencia
    descricao: Optional[str] = None
    paciente_nome: Optional[str] = None
    codigo_ficha: Optional[str] = None
    data_execucao: Optional[date] = None
    data_atendimento: Optional[date] = None
    data_identificacao: Optional[date] = None
    carteirinha: Optional[str] = None
    prioridade: PrioridadeDivergencia = PrioridadeDivergencia.MEDIA
    status: StatusDivergencia = StatusDivergencia.PENDENTE
    detalhes: Optional[Dict] = None
    ficha_id: Optional[str] = None
    execucao_id: Optional[str] = None
    sessao_id: Optional[str] = None
    paciente_id: Optional[str] = None
    tentativas_resolucao: int = 0

    @field_validator('data_execucao', 'data_atendimento', 'data_identificacao', mode='before')
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
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: str(v)
        }
        
        @staticmethod
        def json_dumps(v, *, default):
            return json.dumps(v, cls=DateEncoder)

class DivergenciaCreate(DivergenciaBase):
    """Modelo para criação de Divergencia"""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero_guia": "guia-id-123",
                "tipo": "valor",
                "descricao": None,
                "paciente_nome": "Nome do Paciente",
                "data_atendimento": "2024-03-20",
                "data_execucao": "2024-03-20",
                "status": "pendente",
                "prioridade": "MEDIA",
                "detalhes": None,
                "data_identificacao": "2024-03-20",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }

class DivergenciaUpdate(BaseModel):
    """Modelo para atualização de Divergencia"""
    tipo: Optional[TipoDivergencia] = None
    descricao: Optional[str] = None
    paciente_nome: Optional[str] = None
    codigo_ficha: Optional[str] = None
    data_execucao: Optional[date] = None
    data_atendimento: Optional[date] = None
    data_identificacao: Optional[date] = None
    carteirinha: Optional[str] = None
    prioridade: Optional[PrioridadeDivergencia] = None
    status: Optional[StatusDivergencia] = None
    detalhes: Optional[Dict] = None
    ficha_id: Optional[str] = None
    execucao_id: Optional[str] = None
    sessao_id: Optional[str] = None
    paciente_id: Optional[str] = None
    tentativas_resolucao: Optional[int] = None

    @field_validator('data_execucao', 'data_atendimento', 'data_identificacao', mode='before')
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
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: str(v)
        }

class Divergencia(DivergenciaBase):
    """Modelo completo de Divergencia"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    data_resolucao: Optional[datetime] = None
    resolvido_por: Optional[str] = None