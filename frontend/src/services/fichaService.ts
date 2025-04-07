import { api } from "./api";
import { PaginatedResponse, StandardResponse } from "@/types/api";
import { Ficha } from "@/types/ficha";
import { getCurrentUserId } from "@/lib/auth";

export interface FichaData {
  paciente_id: string;
  data_atendimento: string;
  status: string;
  created_by?: string;
  updated_by?: string;
}

export interface FichaUpdateData {
  paciente_id?: string;
  data_atendimento?: string;
  status?: string;
  created_by?: string;
  updated_by?: string;
}

export const fichaService = {
  listar: async (
    page: number = 1,
    limit: number = 10,
    search?: string | object,
    orderColumn: string = "data_atendimento",
    orderDirection: "asc" | "desc" = "desc"
  ): Promise<PaginatedResponse<Ficha>> => {
    const params = new URLSearchParams({
      offset: ((page - 1) * limit).toString(),
      limit: limit.toString(),
      order_column: orderColumn,
      order_direction: orderDirection,
    });

    if (search) {
      // Se search for um objeto, converte para string
      const searchTerm =
        typeof search === "string" ? search : JSON.stringify(search);
      params.append("search", searchTerm);
    }

    const response = await api.get<PaginatedResponse<Ficha>>(
      `/api/fichas?${params}`
    );
    return response.data;
  },

  listarPorPaciente: async (
    pacienteId: string,
    page: number = 1,
    limit: number = 10,
    orderColumn: string = "data_atendimento",
    orderDirection: "asc" | "desc" = "desc"
  ): Promise<PaginatedResponse<Ficha>> => {
    const params = new URLSearchParams({
      offset: ((page - 1) * limit).toString(),
      limit: limit.toString(),
      order_column: orderColumn,
      order_direction: orderDirection,
    });

    const response = await api.get<PaginatedResponse<Ficha>>(
      `/api/pacientes/${pacienteId}/fichas?${params}`
    );
    return response.data;
  },

  obter: async (id: string): Promise<StandardResponse<Ficha>> => {
    const response = await api.get<StandardResponse<Ficha>>(
      `/api/fichas/${id}`
    );
    return response.data;
  },

  criar: async (data: FichaData): Promise<StandardResponse<Ficha>> => {
    try {
      // console.log('Dados enviados para API (criar):', data);
      const response = await api.post<StandardResponse<Ficha>>("/api/fichas", data);
      return response.data;
    } catch (error) {
      console.error("Erro ao criar ficha:", error);
      throw error;
    }
  },

  atualizar: async (
    id: string,
    data: FichaUpdateData
  ): Promise<StandardResponse<Ficha>> => {
    try {
      // Remove o created_by se existir, pois não deve ser atualizado
      const { created_by, ...updateData } = data;
      // console.log('Dados enviados para API (atualizar):', updateData);
      const response = await api.put<StandardResponse<Ficha>>(`/api/fichas/${id}`, updateData);
      return response.data;
    } catch (error) {
      console.error("Erro ao atualizar ficha:", error);
      throw error;
    }
  },

  excluir: async (id: string): Promise<StandardResponse<boolean>> => {
    try {
      const response = await api.delete<StandardResponse<boolean>>(
        `/api/fichas/${id}`
      );
      return response.data;
    } catch (error) {
      console.error("Erro ao excluir ficha:", error);
      throw error;
    }
  },
};
