import { api } from "./api";

interface DocumentacaoResponse {
  success: boolean;
  data?: string;
  message?: string;
}

/**
 * Serviço para acessar a documentação do sistema
 */
export const documentacaoService = {
  /**
   * Obtém o conteúdo de um arquivo markdown da pasta 'instrucoes'
   * @param nomeArquivo Nome do arquivo (com extensão .md)
   * @returns O conteúdo do arquivo em formato string
   */
  async obterArquivo(nomeArquivo: string): Promise<DocumentacaoResponse> {
    try {
      const response = await api.get(`/docs/instrucoes/${nomeArquivo}`);
      return {
        success: true,
        data: response.data as string
      };
    } catch (error) {
      console.error("Erro ao obter arquivo de documentação:", error);
      return {
        success: false,
        message: "Não foi possível carregar o arquivo de documentação"
      };
    }
  },

  /**
   * Lista todos os arquivos disponíveis na pasta 'instrucoes'
   * @returns Lista de nomes de arquivos
   */
  async listarArquivos(): Promise<{ success: boolean; items?: string[]; message?: string }> {
    try {
      const response = await api.get('/docs/instrucoes');
      return {
        success: true,
        items: response.data as string[]
      };
    } catch (error) {
      console.error("Erro ao listar arquivos de documentação:", error);
      return {
        success: false,
        message: "Não foi possível listar os arquivos de documentação"
      };
    }
  }
}; 