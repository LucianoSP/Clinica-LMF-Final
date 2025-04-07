from datetime import datetime, date
from typing import Optional, Union, List, Literal
from pydantic import BaseModel
from decimal import Decimal
import json

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class CarteirinhaBase(BaseModel):
    """Modelo base para Carteirinha"""
    paciente_id: str
    plano_saude_id: str
    numero_carteirinha: str
    data_validade: Optional[date] = None
    status: Literal['ativa', 'inativa', 'suspensa', 'vencida'] = 'ativa'
    motivo_inativacao: Optional[str] = None
    historico_status: Optional[List[dict]] = None

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            Decimal: lambda v: float(v) if isinstance(v, Decimal) else v
        }
        
        @staticmethod
        def json_dumps(v, *, default):
            return json.dumps(v, cls=DateEncoder)

class CarteirinhaCreate(CarteirinhaBase):
    """Modelo para criação de Carteirinha"""
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "numero_carteirinha": "123456",
                "paciente_id": "user-id-123",
                "plano_saude_id": "plano-id-123",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }

class CarteirinhaUpdate(CarteirinhaBase):
    """Modelo para atualização de Carteirinha"""
    paciente_id: Optional[str] = None
    plano_saude_id: Optional[str] = None
    numero_carteirinha: Optional[str] = None
    data_validade: Optional[date] = None
    status: Optional[Literal['ativa', 'inativa', 'suspensa', 'vencida']] = None
    motivo_inativacao: Optional[str] = None
    historico_status: Optional[List[dict]] = None
    updated_by: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "numero_carteirinha": "123456",
                "paciente_id": "user-id-123",
                "plano_saude_id": "plano-id-123",
                "updated_by": "user-id-123"
            }
        }

class Carteirinha(CarteirinhaBase):
    """Modelo completo de Carteirinha"""
    id: str
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None
    paciente_nome: Optional[str] = None
    plano_saude_nome: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
            Decimal: str
        }