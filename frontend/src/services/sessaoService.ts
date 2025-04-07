import api from './api';
import { Sessao } from '@/types/sessao';
import { StandardResponse, PaginatedResponse } from "@/types/api";

export const sessaoService = {
    criar: async (data: any): Promise<StandardResponse<Sessao>> => {
        try {
            const response = await api.post<StandardResponse<Sessao>>('api/sessoes', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },
    listarPorGuia: async (guiaId: string) => {
        const response = await api.get<PaginatedResponse<Sessao>>(`/api/sessoes/guia/${guiaId}`);
        return response.data;
    }
}; 