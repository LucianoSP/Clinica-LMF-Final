export type TipoFicha = 'evolucao';
export type StatusFicha = "pendente" | "conferida" | "faturada" | "cancelada";

export interface Ficha {
    id: string;
    codigo_ficha: string;
    guia_id: string;
    numero_guia: string;
    paciente_nome: string;
    paciente_carteirinha: string;
    paciente_id?: string;
    carteirinha_id?: string;
    arquivo_digitalizado?: string;
    storage_id?: string;
    status: StatusFicha;
    data_atendimento: string;
    total_sessoes: number;
    sessoes_conferidas: number;
    created_at: string;
    updated_at: string;
    deleted_at?: string;
    created_by?: string;
    updated_by?: string;
}

export interface FichaData {
    paciente_id: string;
    codigo_ficha: string;
    guia_id: string;
    numero_guia: string;
    paciente_nome: string;
    paciente_carteirinha: string;
    arquivo_digitalizado?: string;
    storage_id?: string;
    status: StatusFicha;
    data_atendimento: string;
    total_sessoes: number;
    sessoes_conferidas: number;
    created_by?: string;
    updated_by?: string;
}

export interface FichaFilters {
    search?: string;
    status?: StatusFicha;
    data_inicio?: string;
    data_fim?: string;
}

export interface FichaFormData {
    paciente_id: string;
    codigo_ficha: string;
    guia_id: string;
    numero_guia: string;
    paciente_nome: string;
    paciente_carteirinha: string;
    arquivo_digitalizado?: string;
    storage_id?: string;
    status: StatusFicha;
    data_atendimento: string;
    total_sessoes: number;
    sessoes_conferidas?: number;
}