export type BiometriaStatus = 'nao_verificado' | 'verificado' | 'falha';
export type StatusExecucao = 'pendente' | 'realizada' | 'cancelada';
export type TipoExecucao = 'presencial' | 'teleconsulta' | null;

export const STATUS_MAPPING: Record<string, StatusExecucao> = {
    "em_analise": "pendente",
    "aprovada": "realizada",
    "rejeitada": "cancelada"
};

// Interface para procedimentos na execução
export interface ProcedimentoExecucao {
    id?: string;
    procedimento_id: string;
    codigo?: string;
    nome?: string;
    quantidade: number;
    valor_unitario?: number;
    valor_total?: number;
    observacoes?: string;
}

// Interface para anexos na execução
export interface AnexoExecucao {
    id?: string;
    arquivo_id: string;
    nome_arquivo?: string;
    tipo_arquivo?: string;
    url?: string;
    tamanho?: number;
    data_upload?: string;
}

export interface Execucao {
    // Campos de identificação
    id: string;
    sessao_id: string | null;
    guia_id: string;
    numero_guia?: string;
    codigo_ficha?: string;
    codigo_ficha_temp?: boolean;
    ordem_execucao?: number | null;
    
    // Campos de paciente
    paciente_id: string | null;
    paciente_nome?: string;
    paciente_carteirinha?: string;
    
    // Campos de profissional
    profissional_id: string | null;
    profissional_executante?: string;
    usuario_executante?: string | null;
    conselho_profissional?: string | null;
    numero_conselho?: string | null;
    uf_conselho?: string | null;
    codigo_cbo?: string | null;
    
    // Campos de data e hora
    data_execucao: string;
    data_atendimento?: string | null;
    hora_inicio?: string | null;
    hora_fim?: string | null;
    
    // Campos de status e origem
    status: StatusExecucao;
    status_biometria?: BiometriaStatus;
    origem?: string;
    ip_origem?: string | null;
    tipo_execucao: TipoExecucao;
    
    // Campos de conteúdo
    procedimentos: ProcedimentoExecucao[];
    valor_total?: number | null;
    assinatura_paciente?: string | null;
    assinatura_profissional?: string | null;
    observacoes?: string | null;
    anexos: AnexoExecucao[];
    
    // Campos de auditoria
    created_at: string;
    updated_at: string;
    created_by?: string | null;
    updated_by?: string | null;
    deleted_at?: string | null;
}

export interface ExecucaoCreate extends Omit<Execucao,
    'id' | 'created_at' | 'updated_at' | 'created_by' | 'updated_by' | 'deleted_at'> {
    // Campos adicionais específicos para criação, se necessário
}

export interface ExecucaoUpdate extends Partial<ExecucaoCreate> {
    // Campos adicionais específicos para atualização, se necessário
}

export interface ExecucaoFormData {
    sessao_id: string;
    guia_id: string;
    paciente_id: string;
    data_execucao: string;
    hora_inicio?: string;
    hora_fim?: string;
    status?: StatusExecucao;
    tipo_execucao: TipoExecucao;
    procedimentos?: ProcedimentoExecucao[];
    valor_total?: number;
    assinatura_paciente?: string;
    assinatura_profissional?: string;
    observacoes?: string;
    anexos?: AnexoExecucao[];
}

// Funções auxiliares para mapeamento de valores legados
export const mapStatus = (status: string): StatusExecucao => {
    return STATUS_MAPPING[status] || status as StatusExecucao;
};

// Tipo para a resposta paginada de execuções
import { PaginatedResponse } from '@/types/api';
export type ExecucoesResponse = PaginatedResponse<Execucao>;