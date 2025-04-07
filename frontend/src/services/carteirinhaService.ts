import api, { ListParams } from './api';
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { Carteirinha, CarteirinhaFormData } from '@/types/carteirinha';
import { getCurrentUserId } from './api';

// Interface que estende CarteirinhaFormData para incluir campos de auditoria
interface CarteirinhaData extends CarteirinhaFormData {
    created_by?: string;
    updated_by?: string;
    paciente_nome?: string;
    plano_saude_nome?: string;
}

export const carteirinhaService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "numero_carteirinha",
        orderDirection: "asc" | "desc" = "asc"
    ): Promise<PaginatedResponse<Carteirinha>> => {
        const offset = (page - 1) * limit;
        const params = new URLSearchParams({
            offset: String(offset),
            limit: String(limit),
            order_column: orderColumn,
            order_direction: orderDirection
        });

        if (search && search.trim()) {
            params.append("search", search.trim());
        }

        const response = await api.get<PaginatedResponse<Carteirinha>>(`/api/carteirinhas?${params}`);
        return response.data;
    },

    obter: async (id: string): Promise<StandardResponse<Carteirinha>> => {
        const response = await api.get<StandardResponse<Carteirinha>>(`/api/carteirinhas/${id}`);
        return response.data;
    },

    criar: async (data: CarteirinhaData): Promise<StandardResponse<Carteirinha>> => {
        try {
            console.log('Dados enviados para API:', data);
            const response = await api.post<StandardResponse<Carteirinha>>('/api/carteirinhas', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },

    atualizar: async (id: string, data: CarteirinhaData): Promise<StandardResponse<Carteirinha>> => {
        try {
            // Remove campos que não devem ser atualizados
            const { 
                created_by, 
                paciente_nome, 
                plano_saude_nome, 
                ...updateData 
            } = data;
            
            console.log('Dados enviados para API na atualização:', updateData);
            const response = await api.put<StandardResponse<Carteirinha>>(`/api/carteirinhas/${id}`, updateData);
            
            // Se a resposta for bem-sucedida, mas os campos paciente_nome e plano_saude_nome estiverem vazios,
            // restauramos os valores originais
            if (response.data.success && response.data.data) {
                if (!response.data.data.paciente_nome && paciente_nome) {
                    response.data.data.paciente_nome = paciente_nome;
                }
                if (!response.data.data.plano_saude_nome && plano_saude_nome) {
                    response.data.data.plano_saude_nome = plano_saude_nome;
                }
            }
            
            return response.data;
        } catch (error: any) {
            console.error('Erro ao atualizar carteirinha:', error);
            throw error;
        }
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        const response = await api.delete<StandardResponse<boolean>>(`/api/carteirinhas/${id}`);
        return response.data;
    },

    listarPorPaciente: async (pacienteId: string): Promise<StandardResponse<Carteirinha[]>> => {
        const response = await api.get<StandardResponse<Carteirinha[]>>(`/api/carteirinhas/by-paciente/${pacienteId}`);
        return response.data;
    },

    listarComJoins: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "numero_carteirinha",
        orderDirection: "asc" | "desc" = "asc",
        status?: string,
        pacienteId?: string,
        planoSaudeId?: string
    ): Promise<PaginatedResponse<Carteirinha>> => {
        try {
            const offset = (page - 1) * limit;
            
            const response = await api.post<PaginatedResponse<Carteirinha>>('/api/carteirinhas/rpc/listar_carteirinhas_com_detalhes', {
                p_offset: offset,
                p_limit: limit,
                p_search: search || null,
                p_status: status || null,
                p_paciente_id: pacienteId || null,
                p_plano_saude_id: planoSaudeId || null,
                p_order_column: orderColumn,
                p_order_direction: orderDirection
            });
            
            return response.data;
        } catch (error) {
            console.error('Erro ao listar carteirinhas com detalhes:', error);
            throw error;
        }
    },

    migrarDePacientes: async (tamanhoBatch: number = 100): Promise<any> => {
        try {
            const response = await api.post(`/api/carteirinhas/migrar-de-pacientes?tamanho_lote=${tamanhoBatch}`);
            return response.data;
        } catch (error) {
            console.error('Erro ao migrar carteirinhas:', error);
            throw error;
        }
    }
};