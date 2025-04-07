import { useQuery } from '@tanstack/react-query';
import { agendamentoService } from '@/services/agendamentoService';
import { Agendamento } from '@/types/agendamento';
import { PaginatedResponse } from '@/types/api';

export const useAgendamentos = (
    page: number,
    limit: number,
    search?: string,
    orderColumn?: string,
    orderDirection?: 'asc' | 'desc',
    statusVinculacaoFilter?: string // Novo parâmetro
) => {
    return useQuery<PaginatedResponse<Agendamento>, Error>({
        queryKey: [
            'agendamentos', 
            page, 
            limit, 
            search, 
            orderColumn, 
            orderDirection,
            statusVinculacaoFilter // Adicionar aos queryKey para re-fetch automático
        ],
        queryFn: () => agendamentoService.listar(
            page,
            limit,
            search,
            orderColumn,
            orderDirection,
            statusVinculacaoFilter === "all" ? undefined : statusVinculacaoFilter 
        ),
        // keepPreviousData: true, // Manter dados anteriores enquanto carrega novos pode ser útil
        // staleTime: 1000 * 60 * 5, // Cache por 5 minutos
    });
};

export function useAgendamento(id: string) {
    return useQuery({
        queryKey: ['agendamento', id],
        queryFn: () => agendamentoService.obter(id),
        enabled: !!id,
        staleTime: 1000 * 60 * 5, // 5 minutos
    });
} 