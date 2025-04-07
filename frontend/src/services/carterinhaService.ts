import api from './api';
import { Carteirinha } from '@/types/carteirinha';
import { StandardResponse, PaginatedResponse } from "@/types/api";

export const carterinhaService = {
    criar: async (data: any): Promise<StandardResponse<Carteirinha>> => {
        try {
            const response = await api.post<StandardResponse<Carteirinha>>('api/carteirinhas', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },
    // ... outros métodos
}; 