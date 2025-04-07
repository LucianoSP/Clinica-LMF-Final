import { useQuery } from '@tanstack/react-query';
import { guiaService } from '@/services/guiaService';
import { Guia } from '@/types/guia';
import { StandardResponse } from '@/types/api';

export function useGuiasDaCarteirinha(pacienteId: string | null, carteirinha: string | null) {
    return useQuery<StandardResponse<Guia[]>>({
        queryKey: ['guias', 'carteirinha', carteirinha],
        queryFn: () => carteirinha ? guiaService.listarPorCarteirinha(carteirinha) : Promise.resolve({ data: [], success: true }),
        enabled: !!carteirinha && !!pacienteId
    });
} 