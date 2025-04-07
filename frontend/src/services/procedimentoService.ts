import api from './api';
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { Procedimento, ProcedimentoCreate, ProcedimentoUpdate } from '@/types/procedimento';

export const procedimentoService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "nome",
        orderDirection: "asc" | "desc" = "asc"
    ): Promise<PaginatedResponse<Procedimento>> => {
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

        const response = await api.get<PaginatedResponse<Procedimento>>(`api/procedimentos?${params}`);
        return response.data;
    },

    obterPorId: async (id: string): Promise<StandardResponse<Procedimento>> => {
        const response = await api.get<StandardResponse<Procedimento>>(`/api/procedimentos/${id}`);
        return response.data;
    },

    criar: async (data: any): Promise<StandardResponse<Procedimento>> => {
        try {
            const response = await api.post<StandardResponse<Procedimento>>('api/procedimentos', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },

    atualizar: async (id: string, procedimento: ProcedimentoUpdate): Promise<StandardResponse<Procedimento>> => {
        const response = await api.put<StandardResponse<Procedimento>>(`/api/procedimentos/${id}`, procedimento);
        return response.data;
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        const response = await api.delete<StandardResponse<boolean>>(`/api/procedimentos/${id}`);
        return response.data;
    }
}; 