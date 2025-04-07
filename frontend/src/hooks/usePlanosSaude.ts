import { useQuery } from "@tanstack/react-query";
import { planoSaudeService } from "@/services/planoSaudeService";

export function usePlanosSaude(
  page: number,
  limit: number,
  search?: string,
  orderColumn: string = "nome",
  orderDirection: "asc" | "desc" = "asc"
) {
  return useQuery({
    queryKey: ["planos_saude", page, limit, search, orderColumn, orderDirection],
    queryFn: () => planoSaudeService.listar(page, limit, search, orderColumn, orderDirection),
    staleTime: 1000 * 60, // 1 minuto
  });
}

export function usePlanoSaude(id: string) {
  return useQuery({
    queryKey: ["plano_saude", id],
    queryFn: () => planoSaudeService.obter(id),
    staleTime: 1000 * 60 * 5, // 5 minutos
    enabled: !!id,
  });
}