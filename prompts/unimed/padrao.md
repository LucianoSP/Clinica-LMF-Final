# Prompt Padrão para Extração de Fichas da Unimed
# Versão: 1.1
# Data: 14/03/2024
# Autor: Equipe ClinicalMF

Analise este documento PDF de atendimento médico da Unimed e extraia as seguintes informações em JSON válido:

{
    "codigo_ficha": string,  // Campo no canto superior direito, formato XX-XXXXXXXX
    "registros": [
        {
            "data_atendimento": string,     // Campo 11 - Data do atendimento no formato DD/MM/YYYY
            "paciente_carteirinha": string,  // Campo 12 - Número da carteira
            "paciente_nome": string,         // Campo 13 - Nome/Nome Social do Beneficiário
            "guia_id": string,               // Campo 14 - Número da Guia Principal
            "possui_assinatura": boolean     // Campo 15 - Indica se tem assinatura na linha
        }
    ]
}

Regras de extração:
1. Cada linha numerada (1-, 2-, 3-, etc) representa uma sessão diferente do mesmo paciente
2. Inclua TODAS as linhas que têm data de atendimento preenchida, mesmo que não tenham assinatura
3. IMPORTANTE: Todas as datas DEVEM estar no formato DD/MM/YYYY (com 4 dígitos no ano)
4. Todas as datas devem ser válidas (30/02/2024 seria uma data inválida)
5. Mantenha o número da carteirinha EXATAMENTE como está no documento, incluindo pontos e hífens
6. Para determinar "possui_assinatura" (boolean):
   - true = Se houver uma assinatura visível na linha
   - false = Se o campo estiver em branco
7. CRÍTICO: NÃO use valores de exemplo como "João da Silva" ou "123.456.789-0". Extraia APENAS os dados reais do documento.
8. Se não conseguir extrair um valor com certeza, use "" (string vazia) para campos de texto ou null para outros tipos.
9. Retorne APENAS o JSON, sem texto adicional

Histórico de alterações:
- 14/03/2024: Versão inicial do prompt
- 14/03/2024: Adicionada instrução para não usar valores de exemplo 