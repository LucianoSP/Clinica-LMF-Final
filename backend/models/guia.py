from datetime import datetime, date
from typing import Optional, Union, List
from pydantic import BaseModel, Field
from decimal import Decimal
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


class GuiaBase(BaseModel):
    """Modelo base para Guia"""

    carteirinha_id: str
    paciente_id: str
    procedimento_id: str
    numero_guia: str
    data_solicitacao: Optional[date] = None
    data_autorizacao: Optional[date] = None
    status: str = Field(
        default="pendente",
        description="Status da guia: rascunho, pendente, autorizada, negada, cancelada, executada",
    )
    tipo: str = Field(
        description="Tipo do procedimento: consulta, exame, procedimento, internacao"
    )
    quantidade_autorizada: int = Field(default=1)
    quantidade_executada: int = Field(default=0)
    motivo_negacao: Optional[str] = None
    codigo_servico: Optional[str] = None
    descricao_servico: Optional[str] = None
    quantidade: int = Field(default=1)
    observacoes: Optional[str] = None
    dados_autorizacao: Optional[dict] = Field(default_factory=dict)
    historico_status: List[dict] = Field(default_factory=list)

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v,
        }

        @staticmethod
        def json_dumps(v, *, default):
            return json.dumps(v, cls=DateEncoder)


class GuiaCreate(GuiaBase):
    """Modelo para criação de Guia"""

    created_by: str
    updated_by: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "carteirinha_id": "carteirinha-id-123",
                "paciente_id": "paciente-id-123",
                "procedimento_id": "procedimento-id-123",
                "numero_guia": "G123456",
                "data_solicitacao": "2024-02-20",
                "tipo": "consulta",
                "created_by": "user-id-123",
                "updated_by": "user-id-123",
            }
        }
    }


class GuiaUpdate(GuiaBase):
    """Modelo para atualização de Guia"""

    carteirinha_id: Optional[str] = None
    paciente_id: Optional[str] = None
    procedimento_id: Optional[str] = None
    numero_guia: Optional[str] = None
    data_solicitacao: Optional[date] = None
    data_autorizacao: Optional[date] = None
    status: Optional[str] = None
    tipo: Optional[str] = None
    quantidade_autorizada: Optional[int] = None
    quantidade_executada: Optional[int] = None
    motivo_negacao: Optional[str] = None
    codigo_servico: Optional[str] = None
    descricao_servico: Optional[str] = None
    quantidade: Optional[int] = None
    observacoes: Optional[str] = None
    dados_autorizacao: Optional[dict] = None
    historico_status: Optional[List[dict]] = None
    updated_by: str


class Guia(GuiaBase):
    """Modelo completo de Guia"""

    id: str
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None
    paciente_nome: Optional[str] = None
    carteirinha_numero: Optional[str] = None


# Adicionar ao backend/models/guia.py
class GuiaComDetalhes(Guia):
    paciente_nome: Optional[str]
    carteirinha_numero: Optional[str]

    class Config:
        from_attributes = True
