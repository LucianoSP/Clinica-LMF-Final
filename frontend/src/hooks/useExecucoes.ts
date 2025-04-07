import { useQuery } from '@tanstack/react-query';
import { execucaoService } from '@/services/execucaoService';
import { ExecucoesResponse } from '@/types/execucao';

export function useExecucoes(
    page: number,
    limit: number,
    search: string,
    orderColumn: string,
    orderDirection: "asc" | "desc"
) {
    return useQuery<ExecucoesResponse>({
        queryKey: ['execucoes', page, limit, search, orderColumn, orderDirection],
        queryFn: async () => {
            console.log('Iniciando requisição para listar execuções...');
            console.log('Parâmetros:', { page, limit, search, orderColumn, orderDirection });
            
            try {
                const response = await execucaoService.listar(page, limit, search, orderColumn, orderDirection);
                console.log('Resposta da API de execuções:', response);
                
                // Verificar se a resposta contém os campos esperados
                if (!response.items) {
                    console.error('Resposta não contém o campo "items"');
                } else if (response.items.length === 0) {
                    console.warn('Resposta contém um array "items" vazio');
                } else {
                    const primeiroItem = response.items[0];
                    console.log('Primeiro item após processamento:', primeiroItem);
                    
                    // Verificar campos importantes
                    const camposImportantes = [
                        'paciente_nome', 'paciente_carteirinha', 'numero_guia', 
                        'codigo_ficha', 'status_biometria', 'origem', 'profissional_executante'
                    ];
                    
                    console.log('Campos importantes presentes:', 
                        camposImportantes.filter(campo => 
                            primeiroItem[campo as keyof typeof primeiroItem]
                        )
                    );
                }
                
                return response;
            } catch (error) {
                console.error('Erro ao listar execuções:', error);
                throw error;
            }
        },
        staleTime: 1000 * 60 * 5, // 5 minutos
    });
}