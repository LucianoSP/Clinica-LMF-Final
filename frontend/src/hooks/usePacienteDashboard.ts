import { useQuery } from "@tanstack/react-query";
import {
  PacienteDashboard,
  PacienteSearchResult,
} from "@/types/dashboard-paciente";
import { Paciente } from "@/types/paciente";
import api from "@/services/api";
import { useDebounce } from "./useDebounce";
import { useState } from "react";
import { pacienteService } from "@/services/pacienteService";
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { Ficha } from "@/types/ficha";
import { Carteirinha } from "@/types/carteirinha";
import { Guia, GuiaStatus, TipoGuia } from "@/types/guia";

interface SearchResponse {
  items: Array<{
    id: string;
    nome: string;
    cpf?: string;
    data_nascimento?: string;
    foto?: string;
  }>;
  total: number;
  page: number;
  total_pages: number;
}

interface ApiResponse<T> {
  data: T;
}

interface PacienteResponse {
  success: boolean;
  data: Paciente;
}

interface ListResponse<T> {
  success: boolean;
  items: T[];
  total: number;
  page: number;
  total_pages: number;
}

interface GuiaResponse {
  id: string;
  carteirinha_id: string;
  paciente_id: string;
  procedimento_id: string;
  numero_guia: string;
  data_solicitacao: string;
  tipo: string;
  status: string;
  quantidade_solicitada: number;
  quantidade_autorizada: number;
  quantidade_executada: number;
  motivo_negacao?: string;
  codigo_servico?: string;
  descricao_servico?: string;
  observacoes?: string;
  dados_autorizacao?: {
    autorizador?: string;
    codigo_autorizacao?: string;
    data_autorizacao?: string;
  };
  historico_status: Array<{
    status: string;
    data: string;
    usuario: string;
    observacao?: string;
  }>;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
  deleted_at?: string;
}

export function usePacienteSearch(
  searchTerm: string,
  page: number = 1,
  limit: number = 10
) {
  const debouncedSearch = useDebounce(searchTerm, 300);

  return useQuery<PacienteSearchResult[], Error>({
    queryKey: ["paciente-search", debouncedSearch, page, limit],
    queryFn: async () => {
      if (!debouncedSearch || debouncedSearch.length < 3) return [];

      const response = await pacienteService.buscarPorTermo(debouncedSearch, {
        page,
        limit,
      });
      return response.items.map((item) => ({
        id: item.id,
        nome: item.nome,
        cpf: item.cpf,
        data_nascimento: item.data_nascimento,
        foto: item.foto,
      }));
    },
    enabled: debouncedSearch.length >= 3,
    retry: 2,
  });
}

export function usePacienteDashboard(pacienteId: string | null) {
  const pacienteQuery = useQuery<Paciente, Error>({
    queryKey: ["paciente", pacienteId],
    queryFn: async () => {
      if (!pacienteId) throw new Error("ID do paciente é necessário");
      const response = (await pacienteService.obter(
        pacienteId,
        "id,nome,cpf,data_nascimento,telefone,email,endereco,foto"
      )) as StandardResponse<Paciente>;
      if (!response.data) throw new Error("Paciente não encontrado");
      return response.data;
    },
    enabled: !!pacienteId,
  });

  const carteirinhasQuery = useQuery<Carteirinha[], Error>({
    queryKey: ["paciente-carteirinhas", pacienteId],
    queryFn: async () => {
      if (!pacienteId) throw new Error("ID do paciente é necessário");
      const response = (await pacienteService.obterCarteirinhas(pacienteId, {
        order_column: "data_validade",
        order_direction: "desc",
      })) as PaginatedResponse<Carteirinha>;
      return response.items || [];
    },
    enabled: !!pacienteId,
  });

  const guiasQuery = useQuery<Guia[], Error>({
    queryKey: ["paciente-guias", pacienteId],
    queryFn: async () => {
      if (!pacienteId) throw new Error("ID do paciente é necessário");
      const response = (await pacienteService.obterGuias(pacienteId, {
        order_column: "created_at",
        order_direction: "desc",
      })) as PaginatedResponse<GuiaResponse>;
      return response.items.map((guiaResponse) => ({
        ...guiaResponse,
        tipo: guiaResponse.tipo.toLowerCase() as TipoGuia,
        status: guiaResponse.status.toLowerCase() as GuiaStatus,
        historico_status: guiaResponse.historico_status.map((historico) => ({
          ...historico,
          status: historico.status.toLowerCase() as GuiaStatus,
        })),
      }));
    },
    enabled: !!pacienteId,
  });

  const fichasQuery = useQuery<Ficha[], Error>({
    queryKey: ["paciente-fichas", pacienteId],
    queryFn: async () => {
      if (!pacienteId) throw new Error("ID do paciente é necessário");
      const response = (await pacienteService.obterFichas(pacienteId, {
        order_column: "data_atendimento",
        order_direction: "desc",
      })) as PaginatedResponse<Ficha>;
      console.log("Fichas obtidas:", response.items);
      return response.items || [];
    },
    enabled: !!pacienteId,
  });

  const isLoading =
    pacienteQuery.isLoading ||
    carteirinhasQuery.isLoading ||
    guiasQuery.isLoading ||
    fichasQuery.isLoading;

  const error =
    pacienteQuery.error ||
    carteirinhasQuery.error ||
    guiasQuery.error ||
    fichasQuery.error;

  const data =
    pacienteQuery.data &&
    carteirinhasQuery.data &&
    guiasQuery.data &&
    fichasQuery.data
      ? {
          paciente: pacienteQuery.data,
          carteirinhas: carteirinhasQuery.data,
          guias: guiasQuery.data,
          fichas: fichasQuery.data,
          stats: {
            total_carteirinhas: carteirinhasQuery.data.length,
            total_guias: guiasQuery.data.length,
            total_fichas: fichasQuery.data.length,
            fichas_pendentes: fichasQuery.data.filter(
              (f: Ficha) => f.status === "pendente"
            ).length,
            fichas_conferidas: fichasQuery.data.filter(
              (f: Ficha) => f.status === "conferida"
            ).length,
            fichas_faturadas: fichasQuery.data.filter(
              (f: Ficha) => f.status === "faturada"
            ).length,
            fichas_canceladas: fichasQuery.data.filter(
              (f: Ficha) => f.status === "cancelada"
            ).length,
            sessoes_totais: guiasQuery.data.reduce(
              (acc: number, g: Guia) => acc + (g.quantidade_autorizada || 0),
              0
            ),
            sessoes_realizadas: guiasQuery.data.reduce(
              (acc: number, g: Guia) => {
                console.log(`Guia ${g.numero_guia}: quantidade_executada=${g.quantidade_executada || 0}`);
                return acc + (g.quantidade_executada || 0);
              },
              0
            ),
            sessoes_pendentes: guiasQuery.data.reduce(
              (acc: number, g: Guia) =>
                acc + ((g.quantidade_autorizada || 0) - (g.quantidade_executada || 0)),
              0
            ),
            valor_faturado: guiasQuery.data.reduce(
              (acc: number, g: Guia) => acc + (g.quantidade_executada || 0) * 100, // Valor fictício de R$100 por sessão
              0
            ),
          },
        }
      : null;

  return {
    data,
    isLoading,
    error,
  };
}

export function usePacienteDashboardStore() {
  const [selectedPacienteId, setSelectedPacienteId] = useState<string | null>(
    null
  );
  const [searchTerm, setSearchTerm] = useState("");

  const searchResults = usePacienteSearch(searchTerm);
  const dashboardDataQuery = usePacienteDashboard(selectedPacienteId);

  const dashboardData = {
    data: dashboardDataQuery.data || null,
    isLoading: dashboardDataQuery.isLoading,
    error: dashboardDataQuery.error,
  };

  return {
    searchTerm,
    setSearchTerm,
    searchResults,
    selectedPacienteId,
    setSelectedPacienteId,
    dashboardData,
  };
}
