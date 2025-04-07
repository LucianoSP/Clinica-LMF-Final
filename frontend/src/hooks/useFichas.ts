import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fichaService, FichaData } from "@/services/fichaService";
import { Ficha } from "@/types/ficha";
import { toast } from "sonner";
import { PaginatedResponse, StandardResponse } from "@/types/api";
import { api, getCurrentUserId } from "@/services/api";

export function useFichas(
  page: number,
  limit: number,
  search?: string,
  orderColumn?: string,
  orderDirection?: "asc" | "desc"
) {
  return useQuery<PaginatedResponse<Ficha>>({
    queryKey: ["fichas", page, limit, search, orderColumn, orderDirection],
    queryFn: () =>
      fichaService.listar(page, limit, search, orderColumn, orderDirection),
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useFicha(id: string | undefined) {
  return useQuery<StandardResponse<Ficha>>({
    queryKey: ["ficha", id],
    queryFn: () => fichaService.obter(id!),
    enabled: !!id,
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useFichasPorProfissional(profissional_id: string) {
  return useQuery<PaginatedResponse<Ficha>>({
    queryKey: ["fichas", "profissional", profissional_id],
    queryFn: () => fichaService.listar(1, 100, profissional_id),
    staleTime: 1000 * 60,
  });
}

export function useFichasPorPaciente(
  pacienteId: string | null,
  page: number,
  limit: number
) {
  return useQuery<PaginatedResponse<Ficha>>({
    queryKey: ["fichas", "paciente", pacienteId, page, limit],
    queryFn: async () => {
      if (!pacienteId) {
        return {
          success: true,
          items: [],
          total: 0,
          page: 1,
          total_pages: 0,
          has_more: false,
        };
      }

      try {
        return await fichaService.listarPorPaciente(
          pacienteId,
          page,
          limit,
          "data_atendimento",
          "desc"
        );
      } catch (error: any) {
        toast.error(error.message || "Erro ao buscar fichas do paciente");
        throw error;
      }
    },
    enabled: !!pacienteId,
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useFichasPorGuia(guiaId: string | null) {
  return useQuery<PaginatedResponse<Ficha>>({
    queryKey: ["fichas", "guia", guiaId],
    queryFn: () => {
      if (!guiaId)
        return Promise.resolve<PaginatedResponse<Ficha>>({
          success: true,
          items: [],
          total: 0,
          page: 1,
          total_pages: 0,
          has_more: false,
        });

      return fichaService.listar(
        1, // página inicial
        100, // limite de itens
        { guia_id: guiaId }, // filtro por guia
        "data_atendimento", // ordenar por data
        "desc" // ordem decrescente
      );
    },
    enabled: !!guiaId,
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useCriarFicha() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: FichaData) => {
      const userId = await getCurrentUserId();
      return fichaService.criar({
        ...data,
        created_by: userId,
        updated_by: userId,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas"] });
      toast.success("Ficha criada com sucesso!");
    },
    onError: (error: any) => {
      toast.error(error.message || "Erro ao criar ficha");
    },
  });
}

export function useAtualizarFicha() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: string;
      data: Partial<FichaData>;
    }) => {
      const userId = await getCurrentUserId();
      return fichaService.atualizar(id, { ...data, updated_by: userId });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas"] });
      toast.success("Ficha atualizada com sucesso!");
    },
    onError: (error: any) => {
      toast.error(error.message || "Erro ao atualizar ficha");
    },
  });
}

export function useExcluirFicha() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => fichaService.excluir(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["fichas"] });
      toast.success("Ficha excluída com sucesso!");
    },
    onError: (error: any) => {
      toast.error(error.message || "Erro ao excluir ficha");
    },
  });
}
