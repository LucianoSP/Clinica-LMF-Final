import api, { getCurrentUserId } from './api'
import { StandardResponse, PaginatedResponse } from "@/types/api"
import { Guia, GuiaFormData, GuiaFilters } from '@/types/guia'

export const guiaService = {
    listar: async (
        page: number = 1,
        limit: number = 10,
        filters?: GuiaFilters,
        orderColumn: string = "data_solicitacao",
        orderDirection: "asc" | "desc" = "desc"
    ): Promise<PaginatedResponse<Guia>> => {
        const offset = (page - 1) * limit

        try {
            // console.group('Listando guias')
            // console.log('Parâmetros:', {
            //     p_offset: offset,
            //     p_limit: limit,
            //     p_search: filters?.search || '',
            //     p_status: filters?.status || '',
            //     p_carteirinha_id: filters?.carteirinha_id || '',
            //     p_paciente_id: filters?.paciente_id || '',
            //     p_order_column: orderColumn,
            //     p_order_direction: orderDirection
            // })

            const { data } = await api.post<PaginatedResponse<Guia>>('/api/guias/rpc/listar_guias_com_detalhes', {
                p_offset: offset,
                p_limit: limit,
                p_search: filters?.search || '',
                p_status: filters?.status || '',
                p_carteirinha_id: filters?.carteirinha_id || '',
                p_paciente_id: filters?.paciente_id || '',
                p_order_column: orderColumn,
                p_order_direction: orderDirection
            })

            // console.log('Resposta completa:', data)
            // console.log('Dados das guias:', data.items)
            // console.log('Exemplo de guia:', data.items[0])
            // console.groupEnd()
            return data
        } catch (error) {
            console.error('Erro ao listar guias:', error)
            throw error
        }
    },

    obter: async (id: string): Promise<StandardResponse<Guia>> => {
        try {
            // console.group('Obtendo guia')
            // console.log('ID:', id)
            const response = await api.get<StandardResponse<Guia>>(`/api/guias/${id}`)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao obter guia:', error)
            throw error
        }
    },

    criar: async (data: GuiaFormData): Promise<StandardResponse<Guia>> => {
        try {
            // console.group('Criando guia')
            const userId = await getCurrentUserId()
            const payload = {
                ...data,
                created_by: userId,
                updated_by: userId,
                historico_status: [{
                    status: data.status,
                    data: new Date().toISOString(),
                    usuario: userId,
                    observacao: 'Guia criada'
                }]
            }
            // console.log('Payload:', payload)
            const response = await api.post<StandardResponse<Guia>>('/api/guias', payload)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao criar guia:', error)
            throw error
        }
    },

    atualizar: async (id: string, data: Partial<GuiaFormData>): Promise<StandardResponse<Guia>> => {
        try {
            // console.group('Atualizando guia')
            // console.log('ID:', id)
            const userId = await getCurrentUserId()
            const payload = {
                ...data,
                updated_by: userId,
                historico_status: [{
                    status: data.status,
                    data: new Date().toISOString(),
                    usuario: userId,
                    observacao: 'Guia atualizada'
                }]
            }
            // console.log('Payload:', payload)
            const response = await api.put<StandardResponse<Guia>>(`/api/guias/${id}`, payload)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao atualizar guia:', error)
            throw error
        }
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        try {
            // console.group('Excluindo guia')
            // console.log('ID:', id)
            const response = await api.delete<StandardResponse<boolean>>(`/api/guias/${id}`)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao excluir guia:', error)
            throw error
        }
    },

    listarPorCarteirinha: async (carteirinha_id: string): Promise<StandardResponse<Guia[]>> => {
        try {
            // console.group('Listando guias por carteirinha')
            // console.log('ID da carteirinha:', carteirinha_id)
            const response = await api.get<StandardResponse<Guia[]>>(`/api/carteirinhas/${carteirinha_id}/guias`)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao listar guias por carteirinha:', error)
            throw error
        }
    },

    listarPorPaciente: async (paciente_id: string): Promise<PaginatedResponse<Guia>> => {
        try {
            // console.group('Listando guias por paciente')
            // console.log('ID do paciente:', paciente_id)
            const response = await api.get<PaginatedResponse<Guia>>(`/api/pacientes/${paciente_id}/guias`)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao listar guias por paciente:', error)
            throw error
        }
    },

    listarPorProcedimento: async (procedimento_id: string): Promise<StandardResponse<Guia[]>> => {
        try {
            // console.group('Listando guias por procedimento')
            // console.log('ID do procedimento:', procedimento_id)
            const response = await api.get<StandardResponse<Guia[]>>(`/api/procedimentos/${procedimento_id}/guias`)
            // console.log('Resposta:', response.data)
            // console.groupEnd()
            return response.data
        } catch (error) {
            console.error('Erro ao listar guias por procedimento:', error)
            throw error
        }
    }
}