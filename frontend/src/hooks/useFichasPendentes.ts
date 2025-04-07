import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import fichasPendentesService, { FichaPendente, ProcessarFichaOptions } from "@/services/fichasPendentesService";

export function useFichasPendentes(params: {
  offset?: number;
  limit?: number;
  search?: string;
  processado?: boolean;
  order_column?: string;
  order_direction?: 'asc' | 'desc';
}) {
  return useQuery({
    queryKey: ['fichas-pendentes', params],
    queryFn: () => fichasPendentesService.listar(params),
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useFichaPendente(id: string) {
  return useQuery({
    queryKey: ['ficha-pendente', id],
    queryFn: () => fichasPendentesService.obterPorId(id),
    enabled: !!id,
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useProcessarFichaPendente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, opcoes }: { id: string; opcoes: ProcessarFichaOptions }) => 
      fichasPendentesService.processar(id, opcoes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fichas-pendentes'] });
      queryClient.invalidateQueries({ queryKey: ['fichas'] });
      toast.success('Ficha processada com sucesso!');
    },
    onError: (error: any) => {
      toast.error(error.message || 'Erro ao processar ficha');
    },
  });
}

export function useExcluirFichaPendente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      console.log('Executando mutação de exclusão para ID:', id);
      try {
        const resultado = await fichasPendentesService.excluir(id);
        console.log('Resultado da API de exclusão:', resultado);
        return resultado;
      } catch (error) {
        console.error('Erro na chamada à API de exclusão:', error);
        throw error;
      }
    },
    onSuccess: (data) => {
      console.log('Mutação de exclusão bem-sucedida:', data);
      queryClient.invalidateQueries({ queryKey: ['fichas-pendentes'] });
    },
    onError: (error: any) => {
      console.error('Erro na mutação de exclusão:', error);
      toast.error(error.message || 'Erro ao excluir ficha pendente');
    },
  });
} 