Analise este documento PDF de atendimento médico da Unimed e extraia as seguintes informações em JSON válido:

{
    "codigo_ficha": string,  // Campo no canto superior direito, formato XX-XXXXXXXX
    "registros": [
        {
            "data_atendimento": string,     // Campo 11 - Data do atendimento no formato DD/MM/YYYY
            "paciente_carteirinha": string,  // Campo 12 - Número da carteira
            "paciente_nome": string,         // Campo 13 - Nome/Nome Social do Beneficiário
            "guia_id": string,               // Campo 14 - Número da Guia Principal
            "possui_assinatura": boolean     // Campo 15 - Indica se há assinatura real na linha
        }
    ]
}

Regras críticas para extração precisa:
1. LINHAS: Processe APENAS as linhas que têm data de atendimento preenchida no campo 11 (primeira coluna)
2. DATAS: Todas as datas devem ser convertidas para o formato DD/MM/YYYY (com 4 dígitos no ano)
   - Exemplo: Se encontrar "13/01/24", converta para "13/01/2024"
3. ASSINATURAS: Para determinar "possui_assinatura" (boolean):
   - true = SOMENTE se houver uma assinatura real visível (traço, rabisco ou assinatura manuscrita) no campo 15
   - false = Se o campo estiver em branco OU se apenas o quadrado de marcação estiver preenchido sem assinatura real
   - IMPORTANTE: O quadrado marcado com X é apenas uma instrução para assinar, mas não confirma que a assinatura foi feita
4. Preserve EXATAMENTE a formatação original dos números (incluindo pontos, hífens e zeros)
5. Verifique que a data extraída é válida (não existe 30/02/2024, por exemplo)
6. CRÍTICO: NÃO use valores de exemplo como "João da Silva" ou "123.456.789-0". Extraia APENAS os dados reais do documento.
7. Se não conseguir extrair um valor com certeza, use "" (string vazia) para campos de texto ou null para outros tipos.

Retorne APENAS o JSON sem texto adicional ou explicações.