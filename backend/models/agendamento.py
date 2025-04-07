from typing import Optional
from pydantic import BaseModel

class AgendamentoResponse(BaseModel):
    id: int
    data_agendamento: str
    hora_inicio: str
    hora_fim: str
    paciente_id: Optional[int]
    procedimento_id: Optional[int]
    local_id_supabase: Optional[int]
    sala_id_supabase: Optional[int]
    schedule_profissional_id: Optional[int]
    status: Optional[str]
    observacoes: Optional[str]
    pagamento: Optional[str]
    id_atendimento: Optional[str]
    cod_paciente: Optional[str]
    qtd_sess: Optional[int]
    elegibilidade: Optional[bool]
    substituicao: Optional[bool]
    tipo_falta: Optional[str]
    id_pai: Optional[int]
    codigo_faturamento: Optional[str]
    
    # Dados relacionados
    paciente_nome: Optional[str]
    carteirinha: Optional[str]
    plano_saude: Optional[str]
    procedimento_nome: Optional[str]
    local_nome: Optional[str]
    sala_nome: Optional[str]
    profissional_nome: Optional[str]
    profissional: Optional[str]
    profissao: Optional[str]
    profissional_id: Optional[int]

    class Config:
        from_attributes = True 