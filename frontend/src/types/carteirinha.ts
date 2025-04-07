export type CarteirinhaStatus = "ativa" | "inativa" | "suspensa" | "vencida";

export interface Carteirinha {
    id: string;
    paciente_id: string;
    paciente_nome?: string;
    plano_saude_id: string;
    plano_saude_nome?: string;
    numero_carteirinha: string;
    data_validade?: string;
    status: CarteirinhaStatus;
    motivo_inativacao?: string;
    historico_status?: any[];
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
}

export interface CarteirinhaFormData {
    paciente_id: string;
    plano_saude_id: string;
    numero_carteirinha: string;
    data_validade?: string;
    status: CarteirinhaStatus;
    motivo_inativacao?: string;
    historico_status?: any[];
}

export interface CarteirinhaFilters {
    search?: string;
    paciente_id?: string;
}