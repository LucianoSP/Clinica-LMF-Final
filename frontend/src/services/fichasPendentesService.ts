import api from './api';
import { StandardResponse } from '@/types/api';

export interface FichaPendente {
  id: string;
  storage_id: string;
  dados_extraidos: any;
  status: string;
  arquivo_url: string;
  numero_guia: string;
  paciente_nome: string;
  paciente_carteirinha: string;
  data_atendimento: string;
  total_sessoes: number;
  codigo_ficha: string;
  observacoes: string;
  processado: boolean;
  data_processamento: string | null;
  created_at: string;
  updated_at: string;
}

export interface ListagemFichasPendentes {
  items: FichaPendente[];
  total: number;
  limit: number;
  offset: number;
}

export interface ProcessarFichaOptions {
  criar_guia?: boolean;
  guia_id?: string;
}

export interface ProcessarFichaResult {
  ficha_id: string;
  guia_id: string;
}

export interface Guia {
  id: string;
  numero_guia: string;
  paciente_nome?: string;
  status: string;
}

const fichasPendentesService = {
  /**
   * Lista fichas pendentes com paginação e filtros
   */
  async listar(params: {
    offset?: number;
    limit?: number;
    search?: string;
    processado?: boolean;
    order_column?: string;
    order_direction?: 'asc' | 'desc';
  }): Promise<ListagemFichasPendentes> {
    const response = await api.get<ListagemFichasPendentes>('/api/fichas/pendentes', { params });
    return response.data;
  },

  /**
   * Obtém detalhes de uma ficha pendente específica
   */
  async obterPorId(id: string): Promise<FichaPendente> {
    const response = await api.get<StandardResponse<FichaPendente>>(`/api/fichas/pendentes/${id}`);
    if (!response.data.data) {
      throw new Error('Ficha pendente não encontrada');
    }
    return response.data.data;
  },

  /**
   * Processa uma ficha pendente, criando ou vinculando a uma guia existente
   */
  async processar(id: string, opcoes: ProcessarFichaOptions): Promise<StandardResponse<ProcessarFichaResult>> {
    const response = await api.post<StandardResponse<ProcessarFichaResult>>(`/api/fichas/pendentes/${id}/processar`, opcoes);
    return response.data;
  },

  /**
   * Busca guias disponíveis para vincular a uma ficha pendente
   */
  async buscarGuiasDisponiveis(numeroGuia: string): Promise<Guia[]> {
    const response = await api.get<{ items: Guia[] }>('/api/guias', {
      params: {
        search: numeroGuia,
        limit: 10
      }
    });
    return response.data.items || [];
  },

  /**
   * Exclui uma ficha pendente
   */
  async excluir(id: string): Promise<StandardResponse<boolean>> {
    const response = await api.delete<StandardResponse<boolean>>(`/api/fichas/pendentes/${id}`);
    return response.data;
  }
};

export default fichasPendentesService; 