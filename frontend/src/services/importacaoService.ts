// import axios from 'axios'; // Não importar mais axios diretamente
import { apiClient } from '@/lib/api'; // Importar a instância configurada
import { toast } from 'sonner';

// Interface base para o resultado da API (ajuste conforme necessário)
interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T; // Dados específicos retornados pela API
  [key: string]: any; // Para outros campos como 'resultados'
}

// Interface específica para o resultado da importação geral
interface PassoResultado {
  success: boolean;
  message: string;
  novos_registros?: number;
  registros_atualizados?: number;
  registros_existentes?: number;
  erros_mapeamento?: number;
  total_processado?: number;
  registros_nao_encontrados?: number;
}

interface ImportacaoGeralResult extends ApiResponse {
  resultados?: Record<string, PassoResultado>;
}

interface ResultadoRelacionamento {
  success: boolean;
  message: string;
  salas_relacionadas?: number;
  locais_relacionados?: number;
  especialidades_relacionadas?: number;
  total_agendamentos_verificados?: number;
}

interface ResultadoCorrecaoAgendamentos {
  status: string; // "success" ou "error"
  agendamentos_sem_paciente: number;
  agendamentos_atualizados: number;
  message: string;
}

// Exportar a interface para que possa ser importada
export interface ControleImportacaoItem {
  nome_tabela: string;
  ultima_importacao: string; // ISO Date string
  registros_importados?: number;
  observacoes?: string;
}

const importacaoService = {
  /**
   * Inicia a importação completa das tabelas do sistema Aba.
   * @param banco_dados O nome do banco de dados de origem (ex: 'abalarissa_db')
   * @returns Promise<ImportacaoGeralResult>
   */
  async importarTudoSistemaAba(banco_dados: string): Promise<ImportacaoGeralResult> {
    // REMOVIDA: Verificação do API_URL

    const relativePath = '/api/importacao/importar-tudo-sistema-aba'; // Usar caminho relativo
    console.log("[importacaoService] Chamando endpoint:", relativePath, "com banco:", banco_dados);

    try {
      // Usar apiClient importado
      const response = await apiClient.post<ImportacaoGeralResult>(
        relativePath,
        null, // Sem corpo
        { params: { banco_dados } } // Envia como query parameter
      );
      console.log("[importacaoService] Resposta recebida:", response.data);
      return response.data;
    } catch (error: any) {
      // O interceptor do apiClient já loga o erro
      console.error("[importacaoService] Erro na chamada API (pego no service):", error);
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        "Erro desconhecido ao comunicar com a API";
      // Mostrar toast aqui continua útil
      toast.error(`Erro na importação: ${errorMessage}`);
      throw new Error(errorMessage);
    }
  },

  /**
   * Inicia o processo de relacionar agendamentos existentes com tabelas importadas.
   * @returns Promise<ApiResponse>
   */
  async relacionarAgendamentos(): Promise<ResultadoRelacionamento> {
    // REMOVIDA: Verificação do API_URL

    const relativePath = '/api/importacao/relacionar-agendamentos-com-tabelas-aba'; // Usar caminho relativo
    console.log("[importacaoService] Chamando endpoint:", relativePath);

    try {
      // Usar apiClient importado
       const response = await apiClient.post<ResultadoRelacionamento>(relativePath);
       console.log("[importacaoService] Resposta recebida:", response.data);
       return response.data;
    } catch (error: any) {
      // O interceptor do apiClient já loga o erro
       console.error("[importacaoService] Erro na chamada API (pego no service):", error);
       const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        "Erro desconhecido ao comunicar com a API";
      // Mostrar toast aqui continua útil
      toast.error(`Erro ao relacionar agendamentos: ${errorMessage}`);
      throw new Error(errorMessage);
    }
  },

  /**
   * Corrige agendamentos importados que não foram vinculados a pacientes.
   * A URL foi revertida para o prefixo /api/importacao/ após mover a rota no backend.
   */
  async corrigirAgendamentosImportados(): Promise<ResultadoCorrecaoAgendamentos> {
    const response = await apiClient.get<ResultadoCorrecaoAgendamentos>('/importacao/corrigir-agendamentos-importados');
    return response.data;
  },

  // --- Funções para Importação Individual ---

  /** Importa apenas a tabela de profissões (ws_profissoes). */
  async importarProfissoes(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/profissoes', null, { params: { banco_dados } });
    return response.data;
  },

  /** Importa apenas a tabela de especialidades (ws_especialidades). */
  async importarEspecialidades(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/especialidades', null, { params: { banco_dados } });
    return response.data;
  },

  /** Importa apenas a tabela de locais (ps_locales). */
  async importarLocais(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/locais', null, { params: { banco_dados } });
    return response.data;
  },

  /** Importa apenas a tabela de salas (ps_care_rooms). */
  async importarSalas(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/salas', null, { params: { banco_dados } });
    return response.data;
  },

  /** Importa apenas a tabela de usuários ABA (ws_users). */
  async importarUsuariosAba(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/usuarios-aba', null, { params: { banco_dados } });
    return response.data;
  },

  /** Importa apenas a tabela de relações usuários-profissões (ws_users_profissoes). */
  async importarUsuariosProfissoes(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/usuarios-profissoes', null, { params: { banco_dados } });
    return response.data;
  },

  /** Importa apenas a tabela de relações usuários-especialidades (ws_users_especialidades). */
  async importarUsuariosEspecialidades(banco_dados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/usuarios-especialidades', null, { params: { banco_dados } });
    return response.data;
  },

  /**
   * Importa/Atualiza Tipos de Pagamento.
   */
  async importarTiposPagamento(bancoDados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/tipos-pagamento', null, { params: { banco_dados: bancoDados } });
    return response.data;
  },

  /**
   * Atualiza Procedimentos com Códigos de Faturamento.
   */
  async importarCodigosFaturamento(bancoDados: string): Promise<PassoResultado> {
    const response = await apiClient.post<PassoResultado>('/api/importacao/codigos-faturamento', null, { params: { banco_dados: bancoDados } });
    return response.data;
  },

  /** Busca os dados da tabela de controle de importação das tabelas auxiliares. */
  async getControleImportacao(): Promise<{success: boolean, data: ControleImportacaoItem[]}> {
      const response = await apiClient.get<{success: boolean, data: ControleImportacaoItem[]}>('/api/importacao/controle-importacao');
      return response.data;
  }

};

export default importacaoService; 