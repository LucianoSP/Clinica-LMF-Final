import api from './api';
import { Execucao, ExecucaoCreate, ExecucaoUpdate, ExecucaoFormData } from '@/types/execucao';
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { getCurrentUserId } from './api';

// Interface que estende o FormData para incluir campos de auditoria
interface ExecucaoData extends ExecucaoFormData {
    created_by?: string;
    updated_by?: string;
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

export const execucaoService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "data_execucao",
        orderDirection: "asc" | "desc" = "desc"
    ): Promise<PaginatedResponse<Execucao>> => {
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

        console.log('Parâmetros da requisição:', params.toString());
        
        try {
            const response = await api.get<PaginatedResponse<Execucao>>(`api/execucoes?${params}`);
            console.log('Resposta bruta da API:', response);
            
            // Verificar se a resposta está no formato esperado
            const data = response.data;
            
            // Se não houver items na resposta, criar um array vazio
            if (!data.items) {
                console.warn('Resposta da API não contém o campo "items"');
                data.items = [];
            }
            
            // Verificar os dados brutos recebidos
            if (data.items && data.items.length > 0) {
                console.log('Dados brutos do primeiro item:', JSON.stringify(data.items[0]));
                
                // Verificar campos importantes antes do mapeamento
                const camposImportantes = [
                    'id', 'paciente_nome', 'paciente_carteirinha', 'numero_guia', 
                    'codigo_ficha', 'status_biometria', 'origem', 'profissional_executante'
                ];
                
                const primeiroItemBruto = data.items[0];
                console.log('Campos importantes presentes no item bruto:', 
                    camposImportantes.filter(campo => 
                        primeiroItemBruto[campo as keyof typeof primeiroItemBruto]
                    )
                );
            }
            
            // Garantir que todos os campos necessários estejam presentes em cada item
            if (data.items && data.items.length > 0) {
                data.items = data.items.map(item => {
                    // Extrair o ID curto para usar como código de ficha alternativo
                    const idCurto = item.id ? item.id.substring(0, 8) : 'SEMID';
                    
                    // Mapear campos do banco de dados para o modelo do frontend
                    return {
                        // Campos de identificação
                        id: item.id,
                        sessao_id: item.sessao_id,
                        guia_id: item.guia_id,
                        numero_guia: item.numero_guia || `GUIA-${item.guia_id?.substring(0, 6) || idCurto}`,
                        codigo_ficha: item.codigo_ficha || `FICHA-${idCurto}`,
                        codigo_ficha_temp: item.codigo_ficha_temp || false,
                        ordem_execucao: item.ordem_execucao || null,
                        
                        // Campos de paciente
                        paciente_id: item.paciente_id || null,
                        paciente_nome: item.paciente_nome || `Paciente ${idCurto}`,
                        paciente_carteirinha: item.paciente_carteirinha || `CART-${idCurto}`,
                        
                        // Campos de profissional
                        profissional_id: item.profissional_id || null,
                        profissional_executante: item.profissional_executante || 'Não informado',
                        usuario_executante: item.usuario_executante || null,
                        conselho_profissional: item.conselho_profissional || null,
                        numero_conselho: item.numero_conselho || null,
                        uf_conselho: item.uf_conselho || null,
                        codigo_cbo: item.codigo_cbo || null,
                        
                        // Campos de data e hora
                        data_execucao: item.data_execucao,
                        data_atendimento: item.data_atendimento || null,
                        hora_inicio: item.hora_inicio || null,
                        hora_fim: item.hora_fim || null,
                        
                        // Campos de status e origem
                        status: item.status || 'pendente',
                        status_biometria: item.status_biometria || 'nao_verificado',
                        origem: item.origem || 'Sistema',
                        ip_origem: item.ip_origem || null,
                        tipo_execucao: item.tipo_execucao || 'presencial',
                        
                        // Campos de conteúdo
                        procedimentos: item.procedimentos || [],
                        valor_total: item.valor_total || null,
                        assinatura_paciente: item.assinatura_paciente || null,
                        assinatura_profissional: item.assinatura_profissional || null,
                        observacoes: item.observacoes || null,
                        anexos: item.anexos || [],
                        
                        // Campos de auditoria
                        created_at: item.created_at,
                        updated_at: item.updated_at,
                        created_by: item.created_by || null,
                        updated_by: item.updated_by || null,
                        deleted_at: item.deleted_at || null
                    };
                });
                
                // Verificar o primeiro item após o mapeamento
                if (data.items.length > 0) {
                    console.log('Primeiro item após mapeamento:', data.items[0]);
                }
            }
            
            return data;
        } catch (error) {
            console.error('Erro ao listar execuções:', error);
            throw error;
        }
    },

    obter: async (id: string): Promise<StandardResponse<Execucao>> => {
        const response = await api.get<StandardResponse<Execucao>>(`/api/execucoes/${id}`);
        return response.data;
    },

    criar: async (data: ExecucaoData): Promise<StandardResponse<Execucao>> => {
        try {
            const userId = await getCurrentUserId();
            const payload = {
                ...data,
                created_by: userId,
                updated_by: userId
            };
            
            const response = await api.post<StandardResponse<Execucao>>('api/execucoes', payload);
            return response.data;
        } catch (error: unknown) {
            console.error('Erro ao criar execução:', error);
            
            const apiError = error as ApiError;
            if (apiError.message?.includes('AuthSessionMissingError')) {
                throw new Error('Sessão expirada. Por favor, faça login novamente.');
            }
            
            throw error;
        }
    },

    atualizar: async (id: string, data: ExecucaoData): Promise<StandardResponse<Execucao>> => {
        try {
            const userId = await getCurrentUserId();
            
            // Remove o created_by se existir, pois não deve ser atualizado
            const { created_by, ...updateData } = data;
            const payload = {
                ...updateData,
                updated_by: userId
            };
            
            const response = await api.put<StandardResponse<Execucao>>(`/api/execucoes/${id}`, payload);
            return response.data;
        } catch (error: unknown) {
            console.error('Erro ao atualizar execução:', error);
            
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
            const response = await api.delete<StandardResponse<boolean>>(`/api/execucoes/${id}`, {
                params: { updated_by: userId }
            });
            return response.data;
        } catch (error: unknown) {
            console.error('Erro ao excluir execução:', error);
            
            const apiError = error as ApiError;
            if (apiError.message?.includes('AuthSessionMissingError')) {
                throw new Error('Sessão expirada. Por favor, faça login novamente.');
            }
            
            throw error;
        }
    }
};