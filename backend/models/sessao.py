from datetime import datetime, date
from typing import Optional, Union, List
from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
import json

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class SessaoBase(BaseModel):
    """Modelo base para Sessão - Ajustado para refletir tabela sessoes"""
    # Campos que existem na tabela sessoes
    ficha_id: Optional[UUID] = None # FK para fichas
    guia_id: Optional[UUID] = None # FK para guias
    numero_guia: Optional[str] = None
    data_sessao: date
    hora_inicio: Optional[str] = None # Pydantic pode validar formato de hora se necessário
    hora_fim: Optional[str] = None
    profissional_id: Optional[UUID] = None # FK para usuarios, pode ser NULL
    assinatura_paciente: Optional[str] = None # Armazenado como texto/base64?
    assinatura_profissional: Optional[str] = None
    status: Optional[str] = 'pendente' # Usar o ENUM status_sessao aqui seria melhor
    observacoes: Optional[str] = None
    codigo_ficha: Optional[str] = None
    codigo_ficha_temp: Optional[bool] = True
    ordem_execucao: Optional[int] = None

    # Campos removidos que não existem na tabela sessoes:
    # paciente_id: str -> Não existe diretamente em sessoes
    # tipo_atendimento: str -> Não existe em sessoes
    # evolucao: Optional[str] = None -> Não existe em sessoes (talvez em observacoes?)
    # anexos: List[dict] = [] -> Não existe em sessoes

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

class SessaoCreate(SessaoBase):
    """Modelo para criação de Sessão"""
    # Manter guia_id ou ficha_id como obrigatórios na criação?
    # data_sessao é obrigatório pela base
    created_by: UUID
    updated_by: Optional[UUID] = None # Pode ser o mesmo que created_by inicialmente

    model_config = {
        "json_schema_extra": {
            "example": {
                "guia_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "profissional_id": "b2c3d4e5-f6a7-8901-2345-67890abcdef0",
                "data_sessao": "2024-03-20",
                "status": "pendente",
                "ordem_execucao": 1,
                "created_by": "c3d4e5f6-a7b8-9012-3456-7890abcdef01",
            }
        }
    }

class SessaoUpdate(BaseModel): # Não herdar de SessaoBase para permitir atualização parcial
    """Modelo para atualização de Sessão"""
    ficha_id: Optional[UUID] = None
    guia_id: Optional[UUID] = None
    numero_guia: Optional[str] = None
    data_sessao: Optional[date] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    profissional_id: Optional[UUID] = None
    assinatura_paciente: Optional[str] = None
    assinatura_profissional: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None
    codigo_ficha: Optional[str] = None
    codigo_ficha_temp: Optional[bool] = None
    ordem_execucao: Optional[int] = None
    updated_by: UUID # Obrigatório na atualização

class Sessao(SessaoBase):
    """Modelo completo de Sessão para resposta da API"""
    id: UUID # Alterado para UUID
    created_at: Optional[datetime] = None # Usar datetime diretamente
    updated_at: Optional[datetime] = None
    created_by: Optional[UUID] = None # Alterado para UUID
    updated_by: Optional[UUID] = None # Alterado para UUID
    deleted_at: Optional[datetime] = None

    # Adicionar campos relacionais se necessário para exibição
    # paciente: Optional[Paciente] = None
    # profissional: Optional[Usuario] = None
    # guia: Optional[Guia] = None
    # ficha: Optional[Ficha] = None
