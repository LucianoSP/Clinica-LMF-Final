from datetime import datetime, date, timedelta
from typing import Optional, Union, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
import json

class DateEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class ProcedimentoBase(BaseModel):
    """Modelo base para Procedimento"""
    codigo: str = Field(..., min_length=1, max_length=20)
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    valor: Optional[Decimal] = Field(None, ge=0)
    valor_filme: Optional[Decimal] = Field(None, ge=0)
    valor_operacional: Optional[Decimal] = Field(None, ge=0)
    valor_total: Optional[Decimal] = Field(None, ge=0)
    tempo_medio_execucao: Optional[str] = None
    requer_autorizacao: bool = True
    observacoes: Optional[str] = None
    ativo: bool = True
    especialidade: Optional[str] = None
    duracao_minutos: Optional[int] = None

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

class ProcedimentoCreate(ProcedimentoBase):
    """Modelo para criação de Procedimento"""
    created_by: str
    updated_by: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Consulta Padrão",
                "codigo": "CONS001",
                "valor": 150.00,
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }

class ProcedimentoUpdate(ProcedimentoBase):
    """Modelo para atualização de Procedimento"""
    codigo: Optional[str] = None
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
    especialidade: Optional[str] = None
    duracao_minutos: Optional[int] = None
    updated_by: str

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            Decimal: lambda v: float(v) if v is not None else None
        }

class Procedimento(ProcedimentoBase):
    """Modelo completo de Procedimento"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None

    @property
    def tempo_medio_execucao_delta(self) -> Optional[timedelta]:
        if self.tempo_medio_execucao:
            try:
                hours, minutes, seconds = map(int, self.tempo_medio_execucao.split(':'))
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except (ValueError, AttributeError):
                return None
        return None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            Decimal: lambda v: float(v) if v is not None else None
        }
