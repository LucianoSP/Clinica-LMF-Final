import api from './api';
import { PlanoSaude } from '@/types/plano_saude';
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { PlanoSaudeFormData } from '@/components/planos_saude/PlanoSaudeForm';
import { getCurrentUserId } from './api';

// Interface que estende PlanoSaudeFormData para incluir campos de auditoria
interface PlanoSaudeData extends PlanoSaudeFormData {
    created_by?: string;
    updated_by?: string;
}

export const planoSaudeService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "nome",
        orderDirection: "asc" | "desc" = "asc"
    ): Promise<PaginatedResponse<PlanoSaude>> => {
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

        const response = await api.get<PaginatedResponse<PlanoSaude>>(`api/planos-saude?${params}`);
        return response.data;
    },

    obter: async (id: string): Promise<StandardResponse<PlanoSaude>> => {
        const response = await api.get<StandardResponse<PlanoSaude>>(`api/planos-saude/${id}`);
        return response.data;
    },

    criar: async (data: PlanoSaudeData): Promise<StandardResponse<PlanoSaude>> => {
        try {
            console.log('Dados enviados para API:', data);
            const response = await api.post<StandardResponse<PlanoSaude>>('api/planos-saude', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },

    atualizar: async (id: string, data: PlanoSaudeData): Promise<StandardResponse<PlanoSaude>> => {
        try {
            // Remove o created_by se existir, pois não deve ser atualizado
            const { created_by, ...updateData } = data;
            const response = await api.put<StandardResponse<PlanoSaude>>(`api/planos-saude/${id}`, updateData);
            return response.data;
        } catch (error: any) {
            console.error('Erro ao atualizar plano de saúde:', error);
            throw error;
        }
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        const response = await api.delete<StandardResponse<boolean>>(`api/planos-saude/${id}`);
        return response.data;
    }
};