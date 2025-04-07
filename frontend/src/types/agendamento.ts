export interface Agendamento {
    id: string;
    id_atendimento?: string;
    unidade?: string;
    carteirinha?: string;
    carteirinha_numero?: string;
    cod_paciente?: string;
    paciente_id: string;
    paciente_nome?: string;
    pagamento?: string;
    plano_saude_nome?: string;
    sala?: string;
    sala_nome?: string;
    id_profissional?: string;
    profissional?: string;
    profissional_nome?: string;
    tipo_atend?: string;
    qtd_sess?: number;
    elegibilidade?: boolean;
    substituicao?: boolean;
    tipo_falta?: string;
    id_pai?: string;
    codigo_faturamento?: string;
    procedimento_id: string;
    procedimento_nome?: string;
    tipo_pagamento_nome?: string;
    data_agendamento: string;
    hora_inicio: string;
    hora_fim: string;
    status: string;
    observacoes?: string;
    created_at?: string;
    updated_at?: string;
    created_by?: string;
    updated_by?: string;
    importado?: boolean;
    id_origem?: string;
    profissao?: string;
    especialidade?: string;
    especialidade_nome?: string;
    plano_saude?: string;
    schedule_codigo_faturamento?: string;
    schedule_parent_id?: number | null;
    schedule_falha_do_profissional?: boolean;
    status_vinculacao?: 'Pendente' | 'Ficha OK' | 'Unimed OK' | 'Completo' | string;
    possui_sessao_vinculada?: boolean;
    possui_execucao_vinculada?: boolean;
    schedule_id?: string;
    schedule_date_start?: string;
    schedule_date_end?: string;
    schedule_pacient_id?: string;
    schedule_pagamento_id?: string;
    schedule_profissional_id?: string;
    schedule_unidade?: string;
    schedule_room_id?: string;
    schedule_qtd_sessions?: number;
    schedule_status?: string;
    schedule_room_rent_value?: number;
    schedule_fixed?: boolean;
    schedule_especialidade_id?: string;
    schedule_local_id?: string;
    schedule_saldo_sessoes?: number;
    schedule_elegibilidade?: boolean;
    schedule_registration_date?: string;
    schedule_lastupdate?: string;
    parent_id?: string;
    sala_id_supabase?: string;
    local_id_supabase?: string;
    especialidade_id_supabase?: string;
    data_registro_origem?: string;
    data_atualizacao_origem?: string;
    local_nome?: string;
}

// Interface para criação de agendamento
export interface AgendamentoCreate {
    paciente_id: string;
    procedimento_id: string;
    data_agendamento: string;
    hora_inicio: string;
    hora_fim: string;
    status: string;
    observacoes?: string;
}

// Interface para atualização de agendamento
export interface AgendamentoUpdate {
    paciente_id?: string;
    procedimento_id?: string;
    data_agendamento?: string;
    hora_inicio?: string;
    hora_fim?: string;
    status?: string;
    observacoes?: string;
}

// Interface para o formulário de agendamento
export interface AgendamentoFormData {
    paciente_id: string;
    procedimento_id: string;
    data_agendamento: string;
    hora_inicio: string;
    hora_fim: string;
    status: string;
    observacoes?: string;
} 