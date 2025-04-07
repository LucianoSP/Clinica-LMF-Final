import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/services/api";
import { Sessao } from "@/types/sessao";

// Interface para a versão simplificada de Sessao usada internamente
export interface SessaoBasica {
  id: string;
  ficha_id: string;
  guia_id: string;
  data_sessao: string;
  possui_assinatura: boolean;
  procedimento_id: string;
  profissional_executante: string;
  status: string;
  numero_guia: string;
  codigo_ficha: string;
  ordem_execucao: number;
  status_biometria: string;
}

interface ListarSessoesResponse {
  success: boolean;
  data: null;
  items: SessaoBasica[];
  total: number;
  page: number;
  total_pages: number;
  has_more: boolean;
}

interface AtualizarSessaoResponse {
  data: SessaoBasica;
}

interface CriarMultiplasSessoesResponse {
  data: {
    created: number;
    items: SessaoBasica[];
  }
}

interface ListarSessoesParams {
  fichaId: string;
  page?: number;
  limit?: number;
}

interface AtualizarSessaoParams {
  sessaoId: string;
  fichaId: string;
  dados: Partial<SessaoBasica>;
}

// Serviço para manipulação de sessões
export const sessoesService = {
  listar: async ({ fichaId, page = 1, limit = 50 }: ListarSessoesParams) => {
    const response = await api.get<ListarSessoesResponse>(`/api/fichas/${fichaId}/sessoes`, {
      params: {
        page,
        limit
      }
    });
    return response.data;
  },
  
  atualizar: async ({ fichaId, sessaoId, dados }: AtualizarSessaoParams) => {
    const response = await api.put<AtualizarSessaoResponse>(`/api/fichas/${fichaId}/sessoes/${sessaoId}`, dados);
    return response.data;
  },
  
  criarMultiplas: async (fichaId: string, sessoes: Partial<SessaoBasica>[]) => {
    const response = await api.post<CriarMultiplasSessoesResponse>(`/api/fichas/${fichaId}/sessoes/batch`, { sessoes });
    return response.data;
  }
};

// Hook para listar sessões de uma ficha
export function useSessoes(fichaId: string | null) {
  return useQuery({
    queryKey: ["sessoes", fichaId],
    queryFn: async () => {
      if (!fichaId) return { items: [], total: 0 };
      const response = await sessoesService.listar({ fichaId });
      
      // Converter SessaoBasica para Sessao
      const sessoes: Sessao[] = (response.items || []).map(item => ({
        id: item.id,
        guia_id: item.guia_id,
        data_sessao: item.data_sessao,
        paciente_id: "",
        profissional_id: "",
        status: item.status as any,
        tipo_atendimento: "presencial",
        anexos: [],
        created_at: "",
        updated_at: "",
        // Adicionar propriedades específicas de SessaoBasica
        possui_assinatura: item.possui_assinatura,
        ordem_execucao: item.ordem_execucao
      }));
      
      // Adaptar o formato da resposta para o que o componente espera
      return {
        items: sessoes,
        total: response.total || 0
      };
    },
    enabled: !!fichaId
  });
}

// Hook para atualizar uma sessão
export function useAtualizarSessao() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ fichaId, sessaoId, dados }: AtualizarSessaoParams) => {
      const response = await sessoesService.atualizar({ 
        fichaId, 
        sessaoId, 
        dados 
      });
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["sessoes", variables.fichaId] });
      toast.success("Sessão atualizada com sucesso");
    },
    onError: () => {
      toast.error("Erro ao atualizar sessão");
    }
  });
}

// Hook para criar múltiplas sessões
export function useCriarMultiplasSessoes() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ fichaId, sessoes }: { fichaId: string, sessoes: Partial<SessaoBasica>[] }) => {
      const response = await sessoesService.criarMultiplas(fichaId, sessoes);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["sessoes", variables.fichaId] });
      toast.success("Sessões criadas com sucesso");
    },
    onError: () => {
      toast.error("Erro ao criar sessões");
    }
  });
}

// Hook para listar sessões de uma guia
export function useSessoesDaGuia(guiaId: string | null) {
  return useQuery({
    queryKey: ["sessoes-guia", guiaId],
    queryFn: async () => {
      if (!guiaId) return { data: [] };
      try {
        const response = await api.get<ListarSessoesResponse>(`/api/sessoes/guia/${guiaId}`);
        
        // Converter SessaoBasica para Sessao
        const sessoes: Sessao[] = (response.data.items || []).map(item => ({
          id: item.id,
          guia_id: item.guia_id,
          data_sessao: item.data_sessao,
          paciente_id: "",
          profissional_id: "",
          status: item.status as any,
          tipo_atendimento: "presencial",
          anexos: [],
          created_at: "",
          updated_at: "",
          // Adicionar propriedades específicas de SessaoBasica
          possui_assinatura: item.possui_assinatura,
          ordem_execucao: item.ordem_execucao
        }));
        
        return {
          data: sessoes
        };
      } catch (error) {
        console.error("Erro ao buscar sessões da guia:", error);
        return { data: [] };
      }
    },
    enabled: !!guiaId
  });
} 