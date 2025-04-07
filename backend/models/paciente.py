from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel, field_validator
import json


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


class PacienteBase(BaseModel):
    """Modelo base para Paciente"""
    nome: str
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    foto: Optional[str] = None
    nome_responsavel: Optional[str] = None
    nome_pai: Optional[str] = None
    nome_mae: Optional[str] = None
    sexo: Optional[str] = None
    cep: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[int] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    cidade_id: Optional[int] = None
    estado: Optional[str] = None
    forma_pagamento: Optional[int] = None
    valor_consulta: Optional[float] = None
    profissional_id: Optional[str] = None  # Alterado de int para str para aceitar UUID
    escola_nome: Optional[str] = None
    escola_ano: Optional[str] = None
    escola_professor: Optional[str] = None
    escola_periodo: Optional[str] = None
    escola_contato: Optional[str] = None
    patologia_id: Optional[int] = None
    tem_supervisor: Optional[bool] = False
    supervisor_id: Optional[str] = None  # Alterado de int para str para aceitar UUID
    tem_avaliacao_luria: Optional[bool] = False
    avaliacao_luria_data_inicio_treinamento: Optional[date] = None
    avaliacao_luria_reforcadores: Optional[str] = None
    avaliacao_luria_obs_comportamento: Optional[str] = None
    numero_carteirinha: Optional[str] = None
    cpf_responsavel: Optional[str] = None
    crm_medico: Optional[str] = None
    nome_medico: Optional[str] = None
    pai_nao_declarado: Optional[bool] = False
    telefone: Optional[str] = None
    email: Optional[str] = None
    observacoes: Optional[str] = None
    importado: Optional[bool] = False
    id_origem: Optional[int] = None
    data_registro_origem: Optional[datetime] = None
    data_atualizacao_origem: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
        }
    }
    
    def model_dump_json(self, **kwargs):
        """Sobrescreve o método model_dump_json para garantir serialização correta de datas"""
        kwargs.setdefault("cls", DateEncoder)
        return super().model_dump_json(**kwargs)


class PacienteCreate(PacienteBase):
    """Modelo para criação de Paciente"""
    created_by: str
    updated_by: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "João da Silva",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }


class PacienteUpdate(PacienteBase):
    nome: Optional[str] = None  # Alterado para opcional
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None
    updated_by: Optional[str] = None


class Paciente(PacienteBase):
    """Modelo para a entidade Paciente"""
    id: str
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None

    model_config = {
        "from_attributes": True
    }
