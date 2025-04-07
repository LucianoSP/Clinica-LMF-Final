import api, { ListParams } from './api';
import { Paciente } from '@/types/paciente';
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { PacienteFormData } from '@/components/pacientes/PacienteForm';
import { getCurrentUserId } from './api';

// Interface que estende PacienteFormData para incluir campos de auditoria
interface PacienteData extends PacienteFormData {
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
    erros: Array<string | { paciente: string, erro: string }>;
    success: boolean;
    connection_status: {
        success: boolean;
        message: string;
    };
    ultima_data_registro?: string;
    ultima_data_atualizacao?: string;
    atualizados?: number;
}

export const pacienteService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "nome",
        orderDirection: "asc" | "desc" = "asc"
    ): Promise<PaginatedResponse<Paciente>> => {
        try {
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

            const response = await api.get<PaginatedResponse<Paciente>>(`/api/pacientes?${params}`);
            return response.data;
        } catch (error) {
            console.error('Erro ao listar pacientes:', error);
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao listar pacientes',
                data: [],
                items: [],
                total: 0,
                page,
                total_pages: 0,
                has_more: false
            };
        }
    },

    obter: async (id: string, fields?: string): Promise<StandardResponse<Paciente>> => {
        try {
            const params = fields ? `?fields=${fields}` : '';
            const response = await api.get<StandardResponse<Paciente>>(`/api/pacientes/${id}${params}`);
            return response.data;
        } catch (error) {
            console.error(`Erro ao obter paciente ${id}:`, error);
            return {
                data: undefined,
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao obter paciente'
            };
        }
    },

    criar: async (data: PacienteData): Promise<StandardResponse<Paciente>> => {
        try {
            // console.log('Dados enviados para API:', data);
            const response = await api.post<StandardResponse<Paciente>>('/api/pacientes', data);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            return {
                success: false,
                message: error.response?.data?.detail || error.message || 'Erro ao criar paciente',
                data: undefined
            };
        }
    },

    atualizar: async (id: string, data: PacienteData): Promise<StandardResponse<Paciente>> => {
        try {
            console.log('pacienteService.atualizar - Iniciando atualização do paciente:', id);
            console.log('pacienteService.atualizar - Dados enviados:', data);
            
            // Remove o created_by se existir, pois não deve ser atualizado
            const { created_by, ...updateData } = data;
            
            // Garantir que id_origem seja uma string válida
            if (updateData.id_origem === undefined) {
                updateData.id_origem = "";
            }
            
            console.log('pacienteService.atualizar - Dados após processamento:', updateData);
            
            const response = await api.put<StandardResponse<Paciente>>(`/api/pacientes/${id}`, updateData);
            
            console.log('pacienteService.atualizar - Resposta da API:', response.data);
            return response.data;
        } catch (error: any) {
            console.error('pacienteService.atualizar - Erro ao atualizar paciente:', error);
            return {
                success: false,
                message: error.response?.data?.detail || error.message || 'Erro ao atualizar paciente',
                data: undefined
            };
        }
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        try {
            const response = await api.delete<StandardResponse<boolean>>(`/api/pacientes/${id}`);
            return response.data;
        } catch (error) {
            console.error(`Erro ao excluir paciente ${id}:`, error);
            return {
                data: false,
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao excluir paciente'
            };
        }
    },
    
    importarPacientes: async (
        database: string, 
        tabela: string, 
        limit?: number
    ): Promise<ImportResponse> => {
        try {
            // Usar a rota correta com body parameters
            const response = await api.post<ImportResponse>(`/api/pacientes/importar`, {
                database,
                tabela,
                limit
            });
            return response.data;
        } catch (error) {
            console.error("Erro ao importar pacientes:", error);
            throw error;
        }
    },

    // Métodos específicos para pacientes
    buscarPorTermo: async (term: string, params?: ListParams): Promise<PaginatedResponse<Paciente>> => {
        try {
            const searchParams = new URLSearchParams({
                search: term,
                offset: String(((params?.page || 1) - 1) * (params?.limit || 10)),
                limit: String(params?.limit || 10),
                order_column: params?.order_column || 'nome',
                order_direction: params?.order_direction || 'asc'
            });

            // Adicionar campos se especificados
            if (params?.fields) {
                searchParams.append('fields', params.fields);
            }
            
            // console.log('Parâmetros da API:', searchParams.toString());
            const response = await api.get<PaginatedResponse<Paciente>>(`/api/pacientes?${searchParams}`);
            // console.log('Resposta da API:', response.data);
            return response.data;
        } catch (error) {
            console.error('Erro ao buscar pacientes por termo:', error);
            // Retorna uma resposta padrão vazia em caso de erro
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao buscar pacientes',
                data: [], // data deve ser um array vazio de Paciente
                items: [], // items deve estar no nível principal
                total: 0,
                page: params?.page || 1,
                total_pages: 0,
                has_more: false
            };
        }
    },

    // Método otimizado para busca de pacientes no combobox
    buscarParaCombobox: async (term: string): Promise<StandardResponse<Paciente[]>> => {
        // Aumenta o limite para 100 para garantir que mais resultados sejam encontrados
        const searchParams = new URLSearchParams({
            search: term,
            limit: '100', // Aumentado para 100 para garantir que encontre mais resultados
            fields: 'id,nome,cpf', // Solicita apenas os campos necessários
            order_column: 'nome',
            order_direction: 'asc'
        });

        try {
            // console.log(`Buscando pacientes para combobox com termo: "${term}"`);
            const response = await api.get<PaginatedResponse<Paciente>>(`/api/pacientes?${searchParams}`);
            // console.log(`Encontrados ${response.data.items?.length || 0} pacientes para o termo "${term}"`);
            
            // Se não encontrou resultados e o termo é curto, tenta uma busca mais ampla
            if ((!response.data.items || response.data.items.length === 0) && term.length <= 3) {
                // console.log(`Tentando busca mais ampla para o termo curto: "${term}"`);
                // Adiciona um caractere curinga ao final do termo para buscar nomes que começam com o termo
                const wildcardParams = new URLSearchParams({
                    search: `${term}%`, // Adiciona % ao final para buscar nomes que começam com o termo
                    limit: '100',
                    fields: 'id,nome,cpf',
                    order_column: 'nome',
                    order_direction: 'asc'
                });
                
                const wildcardResponse = await api.get<PaginatedResponse<Paciente>>(`/api/pacientes?${wildcardParams}`);
                // console.log(`Encontrados ${wildcardResponse.data.items?.length || 0} pacientes na busca ampla`);
                return {
                    success: true,
                    data: wildcardResponse.data.items || [],
                    message: 'Pacientes encontrados com sucesso'
                };
            }
            
            return {
                success: true,
                data: response.data.items || [],
                message: 'Pacientes encontrados com sucesso'
            };
        } catch (error) {
            console.error('Erro na busca de pacientes para combobox:', error);
            return {
                success: false,
                data: [],
                message: error instanceof Error ? error.message : 'Erro ao buscar pacientes para combobox'
            };
        }
    },

    obterCarteirinhas: async (id: string, params?: ListParams) => {
        try {
            const response = await api.get(`/api/pacientes/${id}/carteirinhas`, { params });
            return response.data;
        } catch (error) {
            console.error(`Erro ao obter carteirinhas do paciente ${id}:`, error);
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao obter carteirinhas do paciente',
                data: {
                    items: [],
                    total: 0,
                    page: 1,
                    total_pages: 0,
                    has_more: false,
                    success: false
                }
            };
        }
    },

    obterGuias: async (id: string, params?: ListParams) => {
        try {
            const response = await api.get(`/api/pacientes/${id}/guias`, { params });
            return response.data;
        } catch (error) {
            console.error(`Erro ao obter guias do paciente ${id}:`, error);
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao obter guias do paciente',
                data: []
            };
        }
    },

    obterFichas: async (id: string, params?: ListParams) => {
        try {
            const response = await api.get(`/api/pacientes/${id}/fichas`, { params });
            return response.data;
        } catch (error) {
            console.error(`Erro ao obter fichas do paciente ${id}:`, error);
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao obter fichas do paciente',
                data: {
                    items: [],
                    total: 0,
                    page: 1,
                    total_pages: 0,
                    has_more: false,
                    success: false
                }
            };
        }
    },

    obterFoto: async (id: string) => {
        try {
            const response = await api.get(`/api/pacientes/${id}/foto`);
            return response.data;
        } catch (error) {
            console.error(`Erro ao obter foto do paciente ${id}:`, error);
            return {
                data: undefined,
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao obter foto do paciente'
            };
        }
    },

    testarConexao: async (database: string): Promise<{ success: boolean; message: string }> => {
        try {
            const response = await api.post<{ success: boolean; message: string }>(`/api/pacientes/test-connection`, {
                database
            });
            return response.data;
        } catch (error) {
            console.error("Erro ao testar conexão:", error);
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao testar conexão'
            };
        }
    },

    obterUltimaAtualizacao: async (): Promise<StandardResponse<{ultima_criacao: string, ultima_atualizacao: string, total_pacientes: number}>> => {
        try {
            const response = await api.get<StandardResponse<{ultima_criacao: string, ultima_atualizacao: string, total_pacientes: number}>>('/api/pacientes/ultima-atualizacao');
            return response.data;
        } catch (error) {
            console.error('Erro ao obter última atualização:', error);
            return {
                success: false,
                message: error instanceof Error ? error.message : 'Erro ao obter última atualização',
                data: undefined
            };
        }
    }
};