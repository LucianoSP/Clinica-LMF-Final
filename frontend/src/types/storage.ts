export type GuiaStatus = 'pendente' | 'autorizada' | 'negada' | 'cancelada' | 'executada';
export type GuiaTipo = 'consulta' | 'exame' | 'procedimento';
export type TipoArquivo = 'arquivo' | 'imagem' | 'documento';

export interface Guia {
    id: string;
    carteirinha_id: string;
    paciente_id: string;
    procedimento_id: string;
    numero_guia: string;
    data_solicitacao: string;
    data_autorizacao?: string;
    data_emissao?: string;
    data_validade?: string;
    senha_autorizacao?: string;
    data_validade_senha?: string;
    status: GuiaStatus;
    tipo: GuiaTipo;
    quantidade_autorizada: number;
    quantidade_executada: number;
    valor_autorizado?: number;
    profissional_solicitante?: string;
    profissional_executante?: string;
    origem?: string;
    motivo_negacao?: string;
    codigo_servico?: string;
    descricao_servico?: string;
    quantidade: number;
    observacoes?: string;
    dados_autorizacao?: any;
    historico_status?: any[];
    created_at: string;
    updated_at: string;
    deleted_at?: string;
    created_by?: string;
    updated_by?: string;
}

export interface GuiaFormData {
    numero: string;
    tipo: GuiaTipo;
    medico: string;
    paciente_id: string;
}

export interface GuiaFilters {
    search?: string;
    paciente_id?: string;
}

export interface Storage {
    id: string;
    nome: string;
    tipo: TipoArquivo;
    mime_type: string;
    tamanho: number;
    caminho: string;
    url: string;  // URL do arquivo no R2
    entidade: string;
    entidade_id: string;
    hash?: string;
    metadados?: any;
    publico: boolean;
    temporario: boolean;
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
}

export interface StorageFormData {
    nome: string;
    tipo: TipoArquivo;
    mime_type: string;
    tamanho: number;
    caminho: string;
    entidade: string;
    entidade_id: string;
    hash?: string;
    metadados?: any;
    publico?: boolean;
    temporario?: boolean;
}