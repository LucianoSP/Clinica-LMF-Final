import { api } from "./api";
import { StandardResponse } from "@/types/api"; // Pode precisar ajustar o tipo de resposta

// Interface para a resposta detalhada da vinculação batch de agendamentos
interface VinculacaoAgendamentosDetails {
    sessoes_vinculadas_direto: number;
    execucoes_vinculadas_direto: number;
    execucoes_atualizadas_por_propagacao: number;
    sessoes_atualizadas_por_propagacao: number;
    total_vinculado_sessao: number;
    total_vinculado_execucao: number;
}

interface VinculacaoAgendamentosResponse extends StandardResponse<any> { // O tipo de `data` pode ser null ou a interface de detalhes
    details?: VinculacaoAgendamentosDetails;
    message?: string; // Adicionado para capturar a mensagem de retorno da API
}

export const vinculacaoService = {
    /**
     * Chama o endpoint backend para executar a função batch `vincular_agendamentos`.
     */
    vincularAgendamentosBatch: async (): Promise<VinculacaoAgendamentosResponse> => {
        try {
            const response = await api.post<VinculacaoAgendamentosResponse>('api/vinculacoes/agendamentos/batch');
            // Retorna os dados completos da resposta, incluindo a mensagem e os detalhes
            return response.data;
        } catch (error: any) {
            console.error("Erro ao executar vinculação batch de agendamentos:", error);
            // Tenta extrair uma mensagem de erro mais útil
            const errorMessage = error.response?.data?.detail || error.message || "Erro desconhecido ao executar vinculação batch.";
            // Lança um erro para ser capturado no componente que chama o serviço
            throw new Error(errorMessage);
        }
    },

    // Adicionar outras funções de serviço de vinculação aqui, se necessário
    // Ex: vincularManual, vincularSessoesExecucoesBatch, etc.
}; 