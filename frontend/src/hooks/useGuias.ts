import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { guiaService } from '@/services/guiaService'
import { GuiaFormData, GuiaFilters, Guia } from '@/types/guia'
import { PaginatedResponse } from '@/types/api'
import { toast } from 'sonner'

export function useGuias(
    page: number = 1,
    limit: number = 10,
    filters?: GuiaFilters,
    orderColumn: string = "data_solicitacao",
    orderDirection: "asc" | "desc" = "desc"
) {
    const queryClient = useQueryClient();

    return useQuery({
        queryKey: ['guias', page, limit, filters, orderColumn, orderDirection],
        queryFn: () => guiaService.listar(page, limit, filters, orderColumn, orderDirection),
        placeholderData: (previousData) => previousData
    });
}

export function useGuia(id: string) {
    return useQuery({
        queryKey: ['guia', id],
        queryFn: () => guiaService.obter(id),
        enabled: !!id
    })
}

export function useGuiasPorCarteirinha(carteirinha_id: string) {
    return useQuery({
        queryKey: ['guias', 'carteirinha', carteirinha_id],
        queryFn: () => guiaService.listarPorCarteirinha(carteirinha_id),
        enabled: !!carteirinha_id
    })
}

export function useGuiasPorPaciente(paciente_id: string) {
    return useQuery({
        queryKey: ['guias', 'paciente', paciente_id],
        queryFn: () => guiaService.listarPorPaciente(paciente_id),
        enabled: !!paciente_id
    })
}

export function useGuiasPorProcedimento(procedimento_id: string) {
    return useQuery({
        queryKey: ['guias', 'procedimento', procedimento_id],
        queryFn: () => guiaService.listarPorProcedimento(procedimento_id),
        enabled: !!procedimento_id
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