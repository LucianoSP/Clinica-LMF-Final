from datetime import datetime, date
from typing import Optional, List, Literal, Dict
from uuid import UUID
from pydantic import BaseModel

StatusGuia = Literal["pendente", "autorizada", "negada", "cancelada", "em_analise"]


class GuiaBase(BaseModel):
    """Modelo base para Guia"""

    carteirinha_id: UUID
    paciente_id: UUID
    procedimento_id: UUID
    numero_guia: str
    data_solicitacao: date
    data_autorizacao: Optional[date] = None
    status: str
    tipo: str  # Garantir que é 'tipo', não 'tipo_guia'
    quantidade_autorizada: int
    quantidade_executada: int = 0
    motivo_negacao: Optional[str] = None
    codigo_servico: Optional[str] = None
    descricao_servico: Optional[str] = None
    quantidade: int
    observacoes: Optional[str] = None
    dados_autorizacao: Dict = {}
    historico_status: List = []


class GuiaCreate(GuiaBase):
    pass


class GuiaUpdate(GuiaBase):
    carteirinha_id: Optional[UUID] = None
    numero_guia: Optional[str] = None
    data_solicitacao: Optional[date] = None
    data_autorizacao: Optional[date] = None
    status: Optional[StatusGuia] = None
    motivo_negacao: Optional[str] = None
    codigo_servico: Optional[str] = None
    descricao_servico: Optional[str] = None
    quantidade: Optional[int] = None
    observacoes: Optional[str] = None
    dados_autorizacao: Optional[dict] = None
    historico_status: Optional[List[dict]] = None


class Guia(GuiaBase):
    """Modelo para a entidade Guia"""

    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None
    # Campos adicionais para exibição
    paciente_nome: Optional[str] = None
    carteirinha_numero: Optional[str] = None

    class Config:
        from_attributes = True
