export type GuiaStatus = 'rascunho' | 'pendente' | 'autorizada' | 'negada' | 'cancelada' | 'executada';
export type TipoGuia = 'consulta' | 'exame' | 'procedimento' | 'internacao';

export type DadosAutorizacao = {
    autorizador?: string;
    codigo_autorizacao?: string;
    data_autorizacao?: string;
};

export type HistoricoStatus = {
    status: GuiaStatus;
    data: string;
    usuario: string;
    observacao?: string;
};

export interface Guia {
    id: string;
    carteirinha_id: string;
    paciente_id: string;
    procedimento_id: string;
    numero_guia: string;
    data_solicitacao: string;
    tipo: TipoGuia;
    status: GuiaStatus;
    quantidade_solicitada: number;
    quantidade_autorizada: number;
    quantidade_executada: number;
    motivo_negacao?: string;
    codigo_servico?: string;
    descricao_servico?: string;
    observacoes?: string;
    dados_autorizacao?: DadosAutorizacao;
    historico_status: HistoricoStatus[];
    created_at: string;
    updated_at: string;
    created_by: string;
    updated_by: string;
    deleted_at?: string;
    // Campos adicionais para exibição
    paciente_nome?: string;
    carteirinha_numero?: string;
}

export interface GuiaFormData {
    carteirinha_id: string;
    paciente_id: string;
    procedimento_id: string;
    numero_guia: string;
    data_solicitacao: string;
    tipo: TipoGuia;
    status: GuiaStatus;
    quantidade_solicitada: number;
    quantidade_autorizada?: number;
    quantidade_executada?: number;
    motivo_negacao?: string;
    codigo_servico?: string;
    descricao_servico?: string;
    observacoes?: string;
    dados_autorizacao?: DadosAutorizacao;
    created_by?: string;
    updated_by?: string;
}

export interface GuiaFilters {
    search?: string;
    paciente_id?: string;
    carteirinha_id?: string;
    procedimento_id?: string;
    status?: GuiaStatus;
    tipo?: TipoGuia;
    data_inicio?: string;
    data_fim?: string;
}