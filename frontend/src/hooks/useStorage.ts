import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { guiaService } from '@/services/guiaService'
import { GuiaFormData, GuiaFilters, Guia } from '@/types/guia'
import { PaginatedResponse } from '@/types/api'
import { toast } from 'sonner'

export function useGuias(
    page: number,
    limit: number,
    search?: string,
    orderColumn?: string,
    orderDirection?: "asc" | "desc",
    carteirinhaId?: string
) {
    return useQuery({
        queryKey: ["guias", page, limit, search, orderColumn, orderDirection, carteirinhaId],
        queryFn: async () => {
            if (carteirinhaId) {
                const response = await guiaService.listarPorCarteirinha(carteirinhaId);
                if (!response.data) {
                    return {
                        items: [],
                        total: 0,
                        page: 1,
                        total_pages: 1,
                        has_more: false,
                        limit,
                        success: true
                    } as PaginatedResponse<Guia>;
                }
                // Converte o array para o formato paginado
                const items = response.data.map(guia => ({
                    ...guia,
                    paciente_nome: ''
                }));
                return {
                    items,
                    total: items.length,
                    page: 1,
                    total_pages: 1,
                    has_more: false,
                    limit,
                    success: true
                } as PaginatedResponse<Guia>;
            }
            return guiaService.listar(page, limit, search && search.trim() !== '' ? { search } : undefined, orderColumn || "numero_guia", orderDirection);
        },
    })
}

export function useGuia(id: string | undefined) {
    return useQuery({
        queryKey: ["guia", id],
        queryFn: () => guiaService.obter(id!),
        enabled: !!id,
    })
}

export function useGuiasPorCarteirinha(carteirinha_id: string) {
    return useQuery({
        queryKey: ['guias', 'carteirinha', carteirinha_id],
        queryFn: () => guiaService.listarPorCarteirinha(carteirinha_id),
        staleTime: 1000 * 60,
    })
}

export function useGuiasPorPaciente(paciente_id: string) {
    return useQuery({
        queryKey: ['guias', 'paciente', paciente_id],
        queryFn: () => guiaService.listarPorPaciente(paciente_id),
        staleTime: 1000 * 60,
    })
}

export function useGuiasPorProcedimento(procedimento_id: string) {
    return useQuery({
        queryKey: ['guias', 'procedimento', procedimento_id],
        queryFn: () => guiaService.listarPorProcedimento(procedimento_id),
        staleTime: 1000 * 60,
    })
}

export function useCriarGuia() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (data: GuiaFormData) => guiaService.criar(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['guias'] })
            toast.success('Guia criada com sucesso!')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.message || 'Erro ao criar guia')
        }
    })
}

export function useAtualizarGuia() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: ({ id, data }: { id: string, data: Partial<GuiaFormData> }) => 
            guiaService.atualizar(id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['guias'] })
            toast.success('Guia atualizada com sucesso!')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.message || 'Erro ao atualizar guia')
        }
    })
}

export function useExcluirGuia() {
    const queryClient = useQueryClient()

    return useMutation({
        mutationFn: (id: string) => guiaService.excluir(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['guias'] })
            toast.success('Guia excluída com sucesso!')
        },
        onError: (error: any) => {
            toast.error(error.response?.data?.message || 'Erro ao excluir guia')
        }
    })
} 