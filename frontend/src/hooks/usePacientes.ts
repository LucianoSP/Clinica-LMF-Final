import { useQuery } from "@tanstack/react-query";
import { pacienteService } from "@/services/pacienteService";
import { ListParams } from "@/services/api";

export function usePacientes(
  page: number,
  limit: number,
  search?: string,
  order_column: string = "nome",
  order_direction: "asc" | "desc" = "asc",
  fields: string = "*"
) {
  return useQuery({
    queryKey: ["pacientes", page, limit, search, order_column, order_direction, fields],
    queryFn: () => pacienteService.buscarPorTermo(search || "", {
      page,
      limit,
      order_column,
      order_direction,
      fields,
    }),
  });
}

export function usePaciente(id: string | undefined) {
  return useQuery({
    queryKey: ["paciente", id],
    queryFn: () => pacienteService.obter(id!, "*"),
    enabled: !!id,
  });
}

// nao está sendo usado
export function useUltimaAtualizacaoPacientes() {
  return useQuery({
    queryKey: ["pacientes-ultima-atualizacao"],
    queryFn: () => pacienteService.obterUltimaAtualizacao(),
    // refetchInterval: 60000, // Atualiza a cada minuto
  });
}