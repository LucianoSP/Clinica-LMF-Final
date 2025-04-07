import { useQuery } from '@tanstack/react-query'
import { procedimentoService } from '@/services/procedimentoService'

export function useProcedimentos(
    page: number,
    limit: number,
    search?: string,
    orderColumn?: string,
    orderDirection?: "asc" | "desc"
) {
    return useQuery({
        queryKey: ['procedimentos', page, limit, search, orderColumn, orderDirection],
        queryFn: () => procedimentoService.listar(page, limit, search, orderColumn, orderDirection),
        staleTime: 1000 * 60, // 1 minuto
    })
}

export function useProcedimento(id: string) {
    return useQuery({
        queryKey: ['procedimentos', id],
        queryFn: () => procedimentoService.obterPorId(id),
        staleTime: 1000 * 60,
        enabled: !!id
    })
}