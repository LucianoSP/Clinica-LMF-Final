import { useQuery } from '@tanstack/react-query';
import { divergenciaService } from '@/services/divergenciaService';
import { Divergencia } from '@/types/auditoria';
import { PaginatedResponse } from '@/types/api';

export function useDivergencias(
    page: number = 1,
    limit: number = 10,
    dataInicio?: string,
    dataFim?: string,
    status?: string,
    tipo?: string,
    prioridade?: string,
    orderColumn: string = "data_identificacao",
    orderDirection: "asc" | "desc" = "desc"
) {
    const offset = (page - 1) * limit;
    
    return useQuery<PaginatedResponse<Divergencia>>({
        queryKey: ['divergencias', offset, limit, dataInicio, dataFim, status, tipo, prioridade, orderColumn, orderDirection],
        queryFn: () => divergenciaService.listar(
            offset,
            limit,
            dataInicio,
            dataFim,
            status,
            tipo,
            prioridade,
            orderColumn,
            orderDirection
        ),
        placeholderData: (previousData) => previousData
    });
} 