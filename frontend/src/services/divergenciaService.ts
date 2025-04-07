import api from './api';
import { Divergencia as DivergenciaBase } from '@/types/divergencia';
import { Divergencia } from '@/types/auditoria';
import { StandardResponse, PaginatedResponse } from "@/types/api";

export const divergenciaService = {
    criar: async (data: any): Promise<StandardResponse<DivergenciaBase>> => {
        try {
            const response = await api.post<StandardResponse<DivergenciaBase>>('api/divergencias', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },
    
    listar: async (
        offset: number = 0,
        limit: number = 10,
        dataInicio?: string,
        dataFim?: string,
        status?: string,
        tipo?: string,
        prioridade?: string,
        orderColumn: string = "data_identificacao",
        orderDirection: "asc" | "desc" = "desc"
    ): Promise<PaginatedResponse<Divergencia>> => {
        try {
            console.log('Parâmetros da chamada:', {
                offset, limit, dataInicio, dataFim, status, tipo, prioridade, orderColumn, orderDirection
            });
            
            const params = {
                offset,
                limit,
                ...(dataInicio && { data_inicio: dataInicio }),
                ...(dataFim && { data_fim: dataFim }),
                ...(status && status !== 'todos' && { status }),
                ...(tipo && tipo !== 'todos' && { tipo }),
                ...(prioridade && prioridade !== 'todas' && { prioridade }),
                order_column: orderColumn,
                order_direction: orderDirection
            };
            
            console.log('Parâmetros enviados:', params);
            
            const response = await api.get<PaginatedResponse<Divergencia>>('/api/divergencias', { params });
            console.log('Resposta da API:', response.data);
            return response.data;
        } catch (error: any) {
            console.error('Erro ao listar divergências:', error);
            throw error;
        }
    },
    
    obter: async (id: string): Promise<StandardResponse<DivergenciaBase>> => {
        try {
            const response = await api.get<StandardResponse<DivergenciaBase>>(`/api/divergencias/${id}`);
            return response.data;
        } catch (error: any) {
            console.error('Erro ao obter divergência:', error);
            throw error;
        }
    },
    
    atualizar: async (id: string, data: Partial<DivergenciaBase>): Promise<StandardResponse<DivergenciaBase>> => {
        try {
            const response = await api.put<StandardResponse<DivergenciaBase>>(`/api/divergencias/${id}`, data);
            return response.data;
        } catch (error: any) {
            console.error('Erro ao atualizar divergência:', error);
            throw error;
        }
    },
    
    resolver: async (id: string): Promise<StandardResponse<DivergenciaBase>> => {
        try {
            const response = await api.post<StandardResponse<DivergenciaBase>>(`/api/divergencias/${id}/resolver`, {});
            return response.data;
        } catch (error: any) {
            console.error('Erro ao resolver divergência:', error);
            throw error;
        }
    }
}; 