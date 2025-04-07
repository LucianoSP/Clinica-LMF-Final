import { api } from "@/services/api";
import { PaginatedResponse, StandardResponse } from "@/types/api";
import { Storage } from "@/types/storage";
import { Guia, GuiaFormData, GuiaFilters } from "@/types/guia";

export const guiaService = {
  listar: async (
    page: number = 1,
    limit: number = 10,
    search?: string,
    orderColumn: string = "numero_guia",
    orderDirection: "asc" | "desc" = "asc"
  ): Promise<PaginatedResponse<Guia>> => {
    const offset = (page - 1) * limit;
    const params = new URLSearchParams({
      offset: String(offset),
      limit: String(limit),
      order_column: orderColumn,
      order_direction: orderDirection,
    });

    if (search) params.append("search", search);

    const response = await api.get<PaginatedResponse<Guia>>(
      `/api/guias?${params}`
    );
    return response.data;
  },

  obter: async (id: string): Promise<StandardResponse<Guia>> => {
    const response = await api.get<StandardResponse<Guia>>(`/api/guias/${id}`);
    return response.data;
  },

  criar: async (guia: GuiaFormData): Promise<StandardResponse<Guia>> => {
    const response = await api.post<StandardResponse<Guia>>("/api/guias", guia);
    return response.data;
  },

  atualizar: async (
    id: string,
    guia: Partial<GuiaFormData>
  ): Promise<StandardResponse<Guia>> => {
    const response = await api.put<StandardResponse<Guia>>(
      `/api/guias/${id}`,
      guia
    );
    return response.data;
  },

  excluir: async (id: string): Promise<StandardResponse<boolean>> => {
    const response = await api.delete<StandardResponse<boolean>>(
      `/api/guias/${id}`
    );
    return response.data;
  },

  listarPorCarteirinha: async (
    carteirinha_id: string
  ): Promise<StandardResponse<Guia[]>> => {
    const response = await api.get<StandardResponse<Guia[]>>(
      `/api/guias/by-carteirinha/${carteirinha_id}`
    );
    return response.data;
  },

  listarPorPaciente: async (
    paciente_id: string
  ): Promise<StandardResponse<Guia[]>> => {
    const response = await api.get<StandardResponse<Guia[]>>(
      `/api/guias/by-paciente/${paciente_id}`
    );
    return response.data;
  },

  listarPorProcedimento: async (
    procedimento_id: string
  ): Promise<StandardResponse<Guia[]>> => {
    const response = await api.get<StandardResponse<Guia[]>>(
      `/api/guias/by-procedimento/${procedimento_id}`
    );
    return response.data;
  },
};

export interface StorageListParams {
  page?: number;
  limit?: number;
  search?: string;
  order_column?: string;
  order_direction?: "asc" | "desc";
}

class StorageService {
  async listar({
    page = 1,
    limit = 10,
    search,
    order_column = "nome",
    order_direction = "desc",
  }: StorageListParams = {}) {
    const params = new URLSearchParams({
      offset: ((page - 1) * limit).toString(),
      limit: limit.toString(),
      order_column,
      order_direction,
    });

    if (search) params.append("search", search);

    const response = await api.get<PaginatedResponse<Storage>>(
      `/api/storage?${params}`
    );
    return response.data;
  }

  async buscar(id: string) {
    const response = await api.get<StandardResponse<Storage>>(
      `/api/storage/${id}`
    );
    return response.data;
  }

  async criar(formData: FormData) {
    const response = await api.post<StandardResponse<Storage>>(
      "/api/storage",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  }

  async atualizar(id: string, data: FormData) {
    const response = await api.put<StandardResponse<Storage>>(
      `/api/storage/${id}`,
      data
    );
    return response.data;
  }

  async excluir(id: string) {
    const response = await api.delete<StandardResponse<boolean>>(
      `/api/storage/${id}`
    );
    return response.data;
  }

  async buscarPorReferencia(referenceId: string, referenceType: string) {
    const response = await api.get<StandardResponse<Storage[]>>(
      `/api/storage/reference/${referenceId}/${referenceType}`
    );
    return response.data;
  }

  async upload(
    file: File,
    entidade: string,
    entidade_id: string
  ): Promise<StandardResponse<Storage>> {
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("entidade", entidade);
      formData.append("entidade_id", entidade_id);

      const response = await api.post<StandardResponse<Storage>>(
        "api/storage",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      return response.data;
    } catch (error: any) {
      console.error("Erro detalhado:", error.response?.data?.detail);
      throw error;
    }
  }

  async uploadFiles(files: FileList): Promise<StandardResponse<boolean>> {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }
    const response = await api.post<StandardResponse<boolean>>(
      "/api/storage/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  }

  async syncWithR2(): Promise<StandardResponse<boolean>> {
    const response = await api.post<StandardResponse<boolean>>(
      "/api/storage/sync"
    );
    return response.data;
  }
}

export const storageService = new StorageService();
