from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel
from enum import Enum
import json
from uuid import UUID

class StatusFicha(str, Enum):
    """Status possíveis para uma ficha"""
    PENDENTE = "pendente"
    CONFERIDA = "conferida"
    FATURADA = "faturada"
    CANCELADA = "cancelada"

class Date(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class FichaBase(BaseModel):
    """Modelo base para Ficha"""
    codigo_ficha: str
    guia_id: Optional[str] = None
    numero_guia: str
    paciente_nome: str
    paciente_carteirinha: str
    arquivo_digitalizado: Optional[str] = None
    status: StatusFicha = StatusFicha.PENDENTE
    data_atendimento: date
    total_sessoes: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
        }
        
        @staticmethod
        def json_dumps(v, *, default):
            return json.dumps(v, cls=DateEncoder)

class FichaCreate(FichaBase):
    """Modelo para criação de Ficha"""
    created_by: str
    updated_by: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "codigo_ficha": "F123",
                "numero_guia": "G123",
                "paciente_nome": "João da Silva",
                "paciente_carteirinha": "123456",
                "data_atendimento": "2024-02-21",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }

class FichaUpdate(FichaBase):
    """Modelo para atualização de Ficha"""
    codigo_ficha: Optional[str] = None
    guia_id: Optional[str] = None
    numero_guia: Optional[str] = None
    paciente_nome: Optional[str] = None
    paciente_carteirinha: Optional[str] = None
    arquivo_digitalizado: Optional[str] = None
    status: Optional[StatusFicha] = None
    data_atendimento: Optional[date] = None
    total_sessoes: Optional[int] = None
    updated_by: str

class Ficha(FichaBase):
    """Modelo para a entidade Ficha"""
    id: str
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            StatusFicha: lambda v: v.value
        }