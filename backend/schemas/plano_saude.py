
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, field_validator

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

class PlanoSaudeCreate(PlanoSaudeBase):
    @field_validator('codigo_operadora')
    @classmethod
    def validate_codigo_operadora(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 20:
            raise ValueError("Código da operadora deve ter no máximo 20 caracteres")
        return v

class PlanoSaudeUpdate(PlanoSaudeBase):
    nome: Optional[str] = None
    codigo_operadora: Optional[str] = None
    registro_ans: Optional[str] = None
    tipo_plano: Optional[str] = None
    abrangencia: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None
    dados_contrato: Optional[dict] = None

class PlanoSaude(PlanoSaudeBase):
    """Modelo para a entidade Plano de Saúde"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
