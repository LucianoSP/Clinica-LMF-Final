import { supabase } from '@/lib/supabase';
import { 
  TipoMapeamento
} from '@/types/mapeamentos';
import { PaginatedResponse, StandardResponse } from '@/types/api';

interface DatabaseError extends Error {
  code?: string;
}

const getTabelaMapeamento = (tipo: TipoMapeamento): string => {
  switch (tipo) {
    case 'pacientes':
      return 'mapeamento_ids_pacientes';
    case 'salas':
      return 'mapeamento_ids_salas';
    case 'especialidades':
      return 'mapeamento_ids_especialidades';
    case 'locais':
      return 'mapeamento_ids_locais';
    case 'pagamentos':
      return 'mapeamento_ids_pagamentos';
    default:
      throw new Error(`Tipo de mapeamento inválido: ${tipo}`);
  }
};

export const mapeamentoService = {
  // Método genérico que retorna itens com paginação
  async listar<T>(
    tipo: TipoMapeamento,
    page = 1,
    limit = 10,
    search = '',
    orderColumn = 'id_mysql',
    orderDirection: 'asc' | 'desc' = 'asc'
  ): Promise<PaginatedResponse<T>> {
    try {
      const tabela = getTabelaMapeamento(tipo);
      
      // Calcular o intervalo para paginação
      const from = (page - 1) * limit;
      const to = from + limit - 1;
      
      // Construir a consulta
      let query = supabase
        .from(tabela)
        .select('*', { count: 'exact' });
      
      // Adicionar busca se houver um termo
      if (search) {
        // Como os campos são numéricos, precisamos converter o termo de busca para número se possível
        const isNumeric = !isNaN(Number(search));
        if (isNumeric) {
          query = query.eq('id_mysql', Number(search));
        }
      }
      
      // Ordenação
      query = query.order(orderColumn, { ascending: orderDirection === 'asc' });
      
      // Paginação
      query = query.range(from, to);
      
      // Executar a consulta
      const { data, error, count } = await query;
      
      if (error) throw error;
      
      return {
        success: true,
        items: data as T[],
        total: count || 0,
        page,
        total_pages: count ? Math.ceil(count / limit) : 0,
        has_more: from + limit < (count || 0)
      };
    } catch (error) {
      console.error(`Erro ao listar mapeamentos de ${tipo}:`, error);
      return { 
        success: false,
        items: [], 
        total: 0, 
        page, 
        total_pages: 0,
        has_more: false
      };
    }
  },

  // Criar um novo mapeamento
  async criar<T>(
    tipo: TipoMapeamento,
    dados: T
  ): Promise<StandardResponse<T>> {
    try {
      const tabela = getTabelaMapeamento(tipo);
      
      const { data, error } = await supabase
        .from(tabela)
        .insert(dados)
        .select()
        .single();
      
      if (error) throw error;
      
      return {
        success: true,
        data: data as T,
        message: 'Mapeamento criado com sucesso'
      };
    } catch (error) {
      console.error(`Erro ao criar mapeamento de ${tipo}:`, error);
      
      // Tratar erro de violação de chave única
      const dbError = error as DatabaseError;
      if (dbError.code === '23505') {
        return {
          success: false,
          data: undefined,
          message: 'Já existe um mapeamento com este ID MySQL'
        };
      }
      
      return {
        success: false,
        data: undefined,
        message: `Erro ao criar mapeamento: ${dbError.message || 'Erro desconhecido'}`
      };
    }
  },

  // Atualizar um mapeamento existente
  async atualizar<T>(
    tipo: TipoMapeamento,
    id_mysql: number,
    dados: Partial<T>
  ): Promise<StandardResponse<T>> {
    try {
      const tabela = getTabelaMapeamento(tipo);
      
      const { data, error } = await supabase
        .from(tabela)
        .update(dados)
        .eq('id_mysql', id_mysql)
        .select()
        .single();
      
      if (error) throw error;
      
      return {
        success: true,
        data: data as T,
        message: 'Mapeamento atualizado com sucesso'
      };
    } catch (error) {
      const dbError = error as DatabaseError;
      console.error(`Erro ao atualizar mapeamento de ${tipo}:`, error);
      return {
        success: false,
        data: undefined,
        message: `Erro ao atualizar mapeamento: ${dbError.message || 'Erro desconhecido'}`
      };
    }
  },

  // Excluir um mapeamento
  async excluir(
    tipo: TipoMapeamento,
    id_mysql: number
  ): Promise<StandardResponse<null>> {
    try {
      const tabela = getTabelaMapeamento(tipo);
      
      const { error } = await supabase
        .from(tabela)
        .delete()
        .eq('id_mysql', id_mysql);
      
      if (error) throw error;
      
      return {
        success: true,
        data: null,
        message: 'Mapeamento excluído com sucesso'
      };
    } catch (error) {
      const dbError = error as DatabaseError;
      console.error(`Erro ao excluir mapeamento de ${tipo}:`, error);
      return {
        success: false,
        data: null,
        message: `Erro ao excluir mapeamento: ${dbError.message || 'Erro desconhecido'}`
      };
    }
  },

  // Obter um mapeamento específico por ID MySQL
  async obterPorId<T>(
    tipo: TipoMapeamento,
    id_mysql: number
  ): Promise<StandardResponse<T>> {
    try {
      const tabela = getTabelaMapeamento(tipo);
      
      const { data, error } = await supabase
        .from(tabela)
        .select('*')
        .eq('id_mysql', id_mysql)
        .single();
      
      if (error) {
        if (error.code === 'PGRST116') { // Não encontrado
          return {
            success: false,
            data: undefined,
            message: 'Mapeamento não encontrado'
          };
        }
        throw error;
      }
      
      return {
        success: true,
        data: data as T,
        message: 'Mapeamento encontrado com sucesso'
      };
    } catch (error) {
      const dbError = error as DatabaseError;
      console.error(`Erro ao buscar mapeamento de ${tipo}:`, error);
      return {
        success: false,
        data: undefined,
        message: `Erro ao buscar mapeamento: ${dbError.message || 'Erro desconhecido'}`
      };
    }
  }
};