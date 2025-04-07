import { useQuery } from '@tanstack/react-query';
import { mapeamentoService } from '@/services/mapeamentoService';
import { TipoMapeamento } from '@/types/mapeamentos';

export function useMapeamentos<T>(
  tipo: TipoMapeamento,
  page: number = 1,
  limit: number = 10,
  search: string = '',
  orderColumn: string = 'id_mysql',
  orderDirection: 'asc' | 'desc' = 'asc'
) {
  const queryKey = ['mapeamentos', tipo, page, limit, search, orderColumn, orderDirection];

  return useQuery({
    queryKey,
    queryFn: () => mapeamentoService.listar<T>(
      tipo, 
      page, 
      limit, 
      search, 
      orderColumn, 
      orderDirection
    ),
    staleTime: 5 * 60 * 1000 // 5 minutos
  });
}