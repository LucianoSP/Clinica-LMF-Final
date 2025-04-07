from datetime import datetime, date
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, field_validator
from decimal import Decimal
import json

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class PlanoSaudeBase(BaseModel):
    """Modelo base para Plano de Saúde"""
    nome: str
    codigo_operadora: Optional[str] = None
    registro_ans: Optional[str] = None
    tipo_plano: Optional[str] = None
    abrangencia: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True
    dados_contrato: Optional[dict] = None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
        }
        
        @staticmethod
        def json_dumps(v, *, default):
            return json.dumps(v, cls=DateEncoder)

class PlanoSaudeCreate(PlanoSaudeBase):
    """Modelo para criação de Plano de Saúde"""
    created_by: str
    updated_by: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Plano Exemplo",
                "codigo_operadora": "12345",
                "registro_ans": "ANS123",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }

class PlanoSaudeUpdate(PlanoSaudeBase):
    """Modelo para atualização de Plano de Saúde"""
    nome: Optional[str] = None
    codigo_operadora: Optional[str] = None
    registro_ans: Optional[str] = None
    tipo_plano: Optional[str] = None
    abrangencia: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None
    dados_contrato: Optional[dict] = None
    updated_by: str

class PlanoSaude(PlanoSaudeBase):
    """Modelo completo de Plano de Saúde"""
    id: str
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            Decimal: str
        }