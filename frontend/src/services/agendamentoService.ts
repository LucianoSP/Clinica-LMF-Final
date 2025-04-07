import { StandardResponse, PaginatedResponse } from "@/types/api";
import { getCurrentUserId } from './api';
import { Agendamento, AgendamentoCreate, AgendamentoUpdate } from "@/types/agendamento";
import { api } from "./api"; // Mover importação da API para cá

// Interface para os dados do formulário
interface AgendamentoFormData {
    paciente_id: string;
    procedimento_id: string;
    data_agendamento: string;
    hora_inicio: string;
    hora_fim: string;
    status: string;
    observacoes?: string;
    // Adicione outros campos conforme necessário
}

// Interface que estende o FormData para incluir campos de auditoria
interface AgendamentoData extends AgendamentoFormData {
    created_by?: string;
    updated_by?: string;
}

// Interface para a resposta da importação
interface ImportResponse {
    message: string;
    importados: number;
    total: number;
    total_atualizados?: number;
    total_erros?: number;
    erros: Array<string | { agendamento: string, erro: string }>;
    success: boolean;
    connection_status: {
        success: boolean;
        message: string;
    };
    ultima_data_registro?: string;
    ultima_data_atualizacao?: string;
    atualizados?: number;
    periodo_semanas?: number;
    data_inicial?: string;
}

// Interface para a resposta de verificação de quantidade
interface QuantidadeResponse {
    success: boolean;
    message: string;
    quantidade: number;
    data_inicial?: string;
    data_final?: string;
}

// Interface para erros da API
interface ApiError extends Error {
    response?: {
        data?: {
            message?: string;
            error?: string;
        };
        status?: number;
    };
    message: string;
}

export const agendamentoService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "data_agendamento",
        orderDirection: "asc" | "desc" = "desc",
        statusVinculacaoFilter?: string
    ): Promise<PaginatedResponse<Agendamento>> => {
        const offset = (page - 1) * limit;
        const params = new URLSearchParams({
            offset: String(offset),
            limit: String(limit),
            order_column: orderColumn,
            order_direction: orderDirection
        });

        if (search) {
            params.append("search", search);
        }

        if (statusVinculacaoFilter) {
            params.append("status_vinculacao", statusVinculacaoFilter);
        }

        const response = await api.get<PaginatedResponse<Agendamento>>(`api/agendamentos?${params}`);
        return response.data;
    },

    obter: async (id: string): Promise<StandardResponse<Agendamento>> => {
        const response = await api.get<StandardResponse<Agendamento>>(`/api/agendamentos/${id}`);
        return response.data;
    },

    criar: async (data: AgendamentoData): Promise<StandardResponse<Agendamento>> => {
        try {
            const userId = await getCurrentUserId();
            const payload = {
                ...data,
                created_by: userId,
                updated_by: userId
            };
            
            const response = await api.post<StandardResponse<Agendamento>>('api/agendamentos', payload);
            return response.data;
        } catch (error: unknown) {
            console.error('Erro ao criar agendamento:', error);
            
            const apiError = error as ApiError;
            if (apiError.message?.includes('AuthSessionMissingError')) {
                throw new Error('Sessão expirada. Por favor, faça login novamente.');
            }
            
            throw error;
        }
    },

    atualizar: async (id: string, data: AgendamentoData): Promise<StandardResponse<Agendamento>> => {
        try {
            const userId = await getCurrentUserId();
            
            // Remove o created_by se existir, pois não deve ser atualizado
            const { created_by, ...updateData } = data;
            const payload = {
                ...updateData,
                updated_by: userId
            };
            
            const response = await api.put<StandardResponse<Agendamento>>(`/api/agendamentos/${id}`, payload);
            return response.data;
        } catch (error: unknown) {
            console.error('Erro ao atualizar agendamento:', error);
            
            const apiError = error as ApiError;
            if (apiError.message?.includes('AuthSessionMissingError')) {
                throw new Error('Sessão expirada. Por favor, faça login novamente.');
            }
            
            throw error;
        }
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        try {
            const userId = await getCurrentUserId();
            const response = await api.delete<StandardResponse<boolean>>(`/api/agendamentos/${id}`, {
                params: { updated_by: userId }
            });
            return response.data;
        } catch (error: unknown) {
            console.error('Erro ao excluir agendamento:', error);
            
            const apiError = error as ApiError;
            if (apiError.message?.includes('AuthSessionMissingError')) {
                throw new Error('Sessão expirada. Por favor, faça login novamente.');
            }
            
            throw error;
        }
    },
    
    importarAgendamentos: async (
        database: string, 
        tabela: string, 
        limit?: number,
        periodoSemanas?: number
    ): Promise<ImportResponse> => {
        try {
            // Usar a rota correta com body parameters
            const response = await api.post<ImportResponse>(`/api/agendamentos/importar`, {
                database,
                tabela,
                limit,
                periodo_semanas: periodoSemanas
            });
            return response.data;
        } catch (error) {
            console.error("Erro ao importar agendamentos:", error);
            throw error;
        }
    },

    // Função unificada para verificar a quantidade de registros antes de importar
    verificarQuantidadeAgendamentos: async (
        database: string, 
        tabela: string, 
        dataInicial: string,
        dataFinal?: string
    ): Promise<QuantidadeResponse> => {
        try {
            // Usar o novo endpoint para verificar a quantidade antes de importar
            const response = await api.post<QuantidadeResponse>(`/api/agendamentos/verificar-quantidade`, {
                database,
                tabela,
                data_inicial: dataInicial,
                data_final: dataFinal
            });
            return response.data;
        } catch (error) {
            console.error("Erro ao verificar quantidade de agendamentos:", error);
            return {
                success: false,
                message: "Erro ao verificar quantidade de agendamentos",
                quantidade: 0,
                data_inicial: dataInicial,
                data_final: dataFinal
            };
        }
    },

    // Novo método para importar agendamentos a partir de uma data específica
    importarAgendamentosDesdeData: async (
        database: string, 
        tabela: string, 
        dataInicial: string,
        dataFinal?: string
    ): Promise<ImportResponse> => {
        try {
            // Usar a rota adaptada para data específica
            const response = await api.post<ImportResponse>(`/api/agendamentos/importar-desde-data`, {
                database,
                tabela,
                data_inicial: dataInicial,
                data_final: dataFinal
            });
            return response.data;
        } catch (error) {
            console.error("Erro ao importar agendamentos desde data:", error);
            throw error;
        }
    },
}