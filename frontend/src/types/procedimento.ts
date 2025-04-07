export type TipoProcedimento = 'consulta' | 'exame' | 'procedimento' | 'internacao';

export interface Procedimento {
    id: string;
    nome: string;
    codigo: string;
    descricao?: string;
    valor?: number | string;
    valor_filme?: number | string;
    valor_operacional?: number | string;
    valor_total?: number | string;
    tempo_medio_execucao?: string;
    requer_autorizacao?: boolean;
    ativo: boolean;
    tipo?: string;
    especialidade?: string;
    duracao_minutos?: number;
    observacoes?: string;
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
}

export interface ProcedimentoFormData {
    nome: string;
    codigo: string;
    descricao?: string;
    valor?: number;
    ativo?: boolean;
    tipo?: string;
    especialidade?: string;
    duracao_minutos?: number;
    observacoes?: string;
}

export interface ProcedimentoCreate extends Omit<Procedimento, 'id' | 'created_at' | 'updated_at' | 'created_by' | 'updated_by' | 'deleted_at'> {
    tempo_medio_execucao?: string;
    valor?: string | number;
    valor_filme?: string | number;
    valor_operacional?: string | number;
    valor_total?: string | number;
}

export interface ProcedimentoUpdate extends Partial<ProcedimentoCreate> {
} 