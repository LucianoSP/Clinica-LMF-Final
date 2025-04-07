export type TipoDivergencia = 'valor' | 'procedimento' | 'quantidade' | 'data';
export type StatusDivergencia = 'pendente' | 'resolvida' | 'cancelada';

export interface Divergencia {
    id: string;
    guia_id: string;
    tipo: TipoDivergencia;
    tipo_divergencia?: TipoDivergencia;
    descricao: string;
    valor_cobrado?: number;
    valor_correto?: number;
    status: StatusDivergencia;
    data_identificacao: string;
    data_resolucao?: string;
    motivo_divergencia?: string;
    solucao?: string;
    documentos: any[];
    observacoes?: string;
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
}

export interface DivergenciaFormData {
    guia_id: string;
    tipo: TipoDivergencia;
    tipo_divergencia?: TipoDivergencia;
    descricao: string;
    valor_cobrado?: number;
    valor_correto?: number;
    status?: StatusDivergencia;
    data_identificacao: string;
    data_resolucao?: string;
    motivo_divergencia?: string;
    solucao?: string;
    documentos?: any[];
    observacoes?: string;
} 