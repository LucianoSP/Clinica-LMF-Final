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

Regras CRÍTICAS para extração precisa:
1. ATENÇÃO: APENAS linhas que possuem uma DATA DE ATENDIMENTO PREENCHIDA no campo 11 devem ser processadas e incluídas no JSON
2. IGNORE COMPLETAMENTE linhas sem data de atendimento, mesmo que tenham assinatura ou outros campos preenchidos
3. VERIFIQUE CUIDADOSAMENTE cada linha para garantir que a data está realmente preenchida antes de processá-la
4. DATAS: Todas as datas devem ser convertidas para o formato DD/MM/YYYY (com 4 dígitos no ano)
   - Exemplo: Se encontrar "16/01/24", converta para "16/01/2024"
5. ASSINATURAS: Para determinar "possui_assinatura" (boolean):
   - true = SOMENTE se houver uma assinatura real visível (traço, rabisco ou assinatura manuscrita) no campo 15
   - false = Se o campo estiver em branco OU se apenas o quadrado de marcação estiver preenchido sem assinatura real
6. Preserve EXATAMENTE a formatação original dos números (incluindo pontos, hífens e zeros)

Retorne APENAS o JSON sem texto adicional ou explicações.