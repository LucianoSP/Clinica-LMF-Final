from datetime import datetime, date
from typing import Optional, Union, Dict, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum
from decimal import Decimal
import json

class StatusBiometria(str, Enum):
    NAO_VERIFICADO = "nao_verificado"
    VERIFICADO = "verificado"
    FALHA = "falha"

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class ExecucaoBase(BaseModel):
    """Modelo base para Execução"""
    sessao_id: Optional[str] = None
    guia_id: Optional[str] = None
    paciente_id: Optional[str] = None
    profissional_id: Optional[str] = None
    data_execucao: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    status: str = "pendente"  # pendente, realizada, cancelada
    tipo_execucao: Optional[str] = None  # presencial, teleconsulta
    procedimentos: List[dict] = []
    valor_total: Optional[Decimal] = None
    assinatura_paciente: Optional[str] = None
    assinatura_profissional: Optional[str] = None
    observacoes: Optional[str] = None
    anexos: List[dict] = []

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            Decimal: lambda v: float(v) if v is not None else None
        }
        
        @staticmethod
        def json_dumps(v, *, default):
            return json.dumps(v, cls=DateEncoder)

class ExecucaoCreate(ExecucaoBase):
    """Modelo para criação de Execução"""
    created_by: str
    updated_by: str

    @field_validator("created_by", "updated_by")
    def validate_user_id(cls, v: str) -> str:
        if not v:
            raise ValueError("ID do usuário é obrigatório")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "sessao_id": "sessao-id-123",
                "guia_id": "guia-id-123",
                "paciente_id": "paciente-id-123",
                "profissional_id": "prof-id-123",
                "data_execucao": "2024-03-20",
                "tipo_execucao": "presencial",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }

class ExecucaoUpdate(ExecucaoBase):
    """Modelo para atualização de Execução"""
    sessao_id: Optional[str] = None
    guia_id: Optional[str] = None
    paciente_id: Optional[str] = None
    profissional_id: Optional[str] = None
    data_execucao: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    status: Optional[str] = None
    tipo_execucao: Optional[str] = None
    procedimentos: Optional[List[dict]] = None
    valor_total: Optional[Decimal] = None
    assinatura_paciente: Optional[str] = None
    assinatura_profissional: Optional[str] = None
    observacoes: Optional[str] = None
    anexos: Optional[List[dict]] = None
    updated_by: str

    @field_validator("updated_by")
    def validate_updated_by(cls, v: str) -> str:
        if not v:
            raise ValueError("ID do usuário que está atualizando é obrigatório")
        return v

class Execucao(ExecucaoBase):
    """Modelo completo de Execução"""
    id: str
    
    # Campos adicionais do banco de dados
    paciente_nome: Optional[str] = None
    paciente_carteirinha: Optional[str] = None
    numero_guia: Optional[str] = None
    codigo_ficha: Optional[str] = None
    codigo_ficha_temp: Optional[bool] = None
    usuario_executante: Optional[str] = None
    origem: Optional[str] = None
    ip_origem: Optional[str] = None
    ordem_execucao: Optional[int] = None
    status_biometria: Optional[StatusBiometria] = None
    conselho_profissional: Optional[str] = None
    numero_conselho: Optional[str] = None
    uf_conselho: Optional[str] = None
    codigo_cbo: Optional[str] = None
    profissional_executante: Optional[str] = None
    data_atendimento: Optional[date] = None
    
    # Campos de auditoria
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None

class Registro(BaseModel):
    """Modelo para registros de execução de procedimentos"""
    data_atendimento: str
    paciente_carteirinha: str
    paciente_nome: str
    guia_id: str
    possui_assinatura: bool

class DadosGuia(BaseModel):
    codigo_ficha: str
    registros: List[Registro]