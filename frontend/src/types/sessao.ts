export type StatusSessao = 'agendada' | 'realizada' | 'cancelada' | 'faltou';
export type TipoAtendimento = 'presencial' | 'teleconsulta';

export interface Sessao {
    id: string;
    guia_id: string;
    paciente_id: string;
    profissional_id: string;
    data_sessao: string;
    hora_inicio?: string;
    hora_fim?: string;
    status: StatusSessao;
    tipo_atendimento: TipoAtendimento;
    evolucao?: string;
    assinatura_paciente?: string;
    assinatura_profissional?: string;
    observacoes?: string;
    anexos: any[];
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
    possui_assinatura?: boolean;
    ordem_execucao?: number;
}

export interface SessaoFormData {
    guia_id: string;
    paciente_id: string;
    profissional_id: string;
    data_sessao: string;
    hora_inicio?: string;
    hora_fim?: string;
    status?: StatusSessao;
    tipo_atendimento: TipoAtendimento;
    evolucao?: string;
    assinatura_paciente?: string;
    assinatura_profissional?: string;
    observacoes?: string;
    anexos?: any[];
} 