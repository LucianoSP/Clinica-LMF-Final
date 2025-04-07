from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

class PacienteBase(BaseModel):
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
    

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(PacienteBase):
    nome: Optional[str] = None
    data_nascimento: Optional[date] = None
    cpf: Optional[str] = None

class Paciente(PacienteBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
