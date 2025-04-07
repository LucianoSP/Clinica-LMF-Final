import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFichas } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

interface FichaPresencaResponse {
  items: any[];
  total: number;
  page: number;
  pages: number;
}

export function useFichasPresenca(params: {
  page: number;
  perPage: number;
  search?: string;
  status?: string;
}) {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const fichasQuery = useQuery({
    queryKey: ["fichas-presenca", params],
    queryFn: async () => {
      const response = await apiFichas.listar(params);
      return response.data as FichaPresencaResponse;
    },
  });

  const conferirSessaoMutation = useMutation({
    mutationFn: async ({
      fichaId,
      sessaoId,
    }: {
      fichaId: string;
      sessaoId: string;
    }) => {
      const response = await apiFichas.conferirSessao(fichaId, sessaoId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas-presenca"] });
      toast({
        title: "Sucesso",
        description: "Sessão conferida com sucesso",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Não foi possível conferir a sessão",
        variant: "destructive",
      });
    },
  });

  const atualizarSessaoMutation = useMutation({
    mutationFn: async ({
      fichaId,
      sessaoId,
      data,
    }: {
      fichaId: string;
      sessaoId: string;
      data: any;
    }) => {
      const response = await apiFichas.atualizarSessao(
        fichaId,
        sessaoId,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas-presenca"] });
      toast({
        title: "Sucesso",
        description: "Sessão atualizada com sucesso",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Não foi possível atualizar a sessão",
        variant: "destructive",
      });
    },
  });

  const excluirSessaoMutation = useMutation({
    mutationFn: async ({
      fichaId,
      sessaoId,
    }: {
      fichaId: string;
      sessaoId: string;
    }) => {
      const response = await apiFichas.excluirSessao(fichaId, sessaoId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas-presenca"] });
      toast({
        title: "Sucesso",
        description: "Sessão excluída com sucesso",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Não foi possível excluir a sessão",
        variant: "destructive",
      });
    },
  });

  const excluirFichaMutation = useMutation({
    mutationFn: async (fichaId: string) => {
      const response = await apiFichas.excluir(fichaId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas-presenca"] });
      toast({
        title: "Sucesso",
        description: "Ficha excluída com sucesso",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Não foi possível excluir a ficha",
        variant: "destructive",
      });
    },
  });

  return {
    data: fichasQuery.data,
    isLoading: fichasQuery.isLoading,
    error: fichasQuery.error,
    conferirSessao: conferirSessaoMutation.mutate,
    atualizarSessao: atualizarSessaoMutation.mutate,
    excluirSessao: excluirSessaoMutation.mutate,
    excluirFicha: excluirFichaMutation.mutate,
  };
}
