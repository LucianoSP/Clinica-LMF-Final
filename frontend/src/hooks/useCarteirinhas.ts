import { useQuery } from "@tanstack/react-query";
import { carteirinhaService } from "@/services/carteirinhaService";
import { PaginatedResponse, StandardResponse } from "@/types/api";
import { Carteirinha } from "@/types/carteirinha";

interface CarteirinhaResponse {
  id: string;
  numero_carteirinha: string;
  paciente_id: string;
  plano_saude_id: string;
  data_validade: string;
  status: string;
  motivo_inativacao?: string;
  paciente?: {
    id: string;
    nome: string;
  };
  historico_status?: Array<{
    data: string;
    motivo: string;
    status: string;
  }>;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export function useCarteirinhas(
  page: number,
  limit: number,
  search?: string,
  orderColumn?: string,
  orderDirection?: "asc" | "desc",
  pacienteId?: string
) {
  return useQuery({
    queryKey: ["carteirinhas", page, limit, search, orderColumn, orderDirection, pacienteId],
    queryFn: async () => {
      if (pacienteId) {
        const response = await carteirinhaService.listarPorPaciente(pacienteId);
        const carteirinhas = response.data as unknown as CarteirinhaResponse[];

        return {
          items: carteirinhas.map(carteirinha => ({
            id: carteirinha.id,
            numero_carteirinha: carteirinha.numero_carteirinha,
            data_validade: carteirinha.data_validade,
            status: carteirinha.status,
            paciente_id: carteirinha.paciente_id,
            plano_saude_id: carteirinha.plano_saude_id,
            titular: true,
            paciente: {
              id: carteirinha.paciente_id,
              nome: carteirinha.paciente?.nome || ''
            },
            created_at: carteirinha.created_at,
            updated_at: carteirinha.updated_at,
            created_by: carteirinha.created_by,
            updated_by: carteirinha.updated_by
          })),
          total: carteirinhas.length,
          page: 1,
          total_pages: 1,
          has_more: false,
          limit,
          success: true
        } as PaginatedResponse<Carteirinha>;
      }
      return carteirinhaService.listar(page, limit, search, orderColumn || "numero_carteirinha", orderDirection);
    },
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function useCarteirinha(id: string | undefined) {
  return useQuery({
    queryKey: ["carteirinha", id],
    queryFn: () => carteirinhaService.obter(id!),
    enabled: !!id,
  });
}

export function useCarteirinhasDoPaciente(pacienteId: string | null) {
  return useQuery({
    queryKey: ["carteirinhas", "paciente", pacienteId],
    queryFn: async () => {
      if (!pacienteId) throw new Error("ID do paciente é obrigatório");
      const response = await carteirinhaService.listarPorPaciente(pacienteId);
      const carteirinhas = response.data as unknown as CarteirinhaResponse[];

      return {
        items: carteirinhas,
        total: carteirinhas.length,
        page: 1,
        total_pages: 1,
        has_more: false,
        limit: carteirinhas.length,
        success: true
      } as PaginatedResponse<CarteirinhaResponse>;
    },
    enabled: !!pacienteId,
    staleTime: 1000 * 60 // 1 minuto
  });
}