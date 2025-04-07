# Uso de Prompts Personalizados para Extração de Dados

## Visão Geral

O sistema agora permite a utilização de prompts personalizados para extração de dados de PDFs. Isso oferece maior flexibilidade e precisão ao processar diferentes tipos de documentos, permitindo adaptar as instruções para cada caso específico.

## Como Funcionam os Prompts Personalizados

Os prompts são instruções detalhadas fornecidas aos modelos de IA (Claude, Gemini ou Mistral) que especificam exatamente quais dados extrair e como formatá-los. Ao usar prompts personalizados, você pode:

- Focar em campos específicos do documento
- Definir regras de formatação personalizadas
- Ajustar o processamento para diferentes layouts de documentos
- Otimizar a extração para casos específicos

## Estrutura de um Arquivo de Prompt

Um arquivo de prompt deve conter instruções claras sobre:

1. O formato do JSON esperado como saída
2. A descrição de cada campo a ser extraído
3. Regras específicas para validação e formatação dos dados
4. Instruções sobre como lidar com casos especiais

## Repositório de Prompts

O sistema mantém uma biblioteca organizada de prompts personalizados na pasta `prompts/` na raiz do projeto:

```
prompts/
├── unimed/         # Prompts específicos para documentos da Unimed
│   ├── padrao.md   # Prompt padrão para fichas da Unimed
│   └── especial.md # Prompt para casos especiais da Unimed
├── outros/         # Prompts para outros convênios ou tipos de documentos
└── README.md       # Documentação sobre os prompts disponíveis
```

### Prompts Disponíveis

- **`prompts/unimed/padrao.md`**: Prompt padrão otimizado para fichas da Unimed
- **`prompts/unimed/especial.md`**: Prompt para casos especiais ou exceções da Unimed
- **`prompts/outros/`**: Pasta para prompts de outros convênios ou tipos de documentos

## Interface de Seleção de Prompts

A interface de upload de PDFs agora inclui uma funcionalidade para selecionar prompts personalizados de duas maneiras:

### Modo Seleção (Recomendado)

![Seleção de Prompt](../assets/images/selecao_prompt.png)

1. Na interface de upload, o modo "Selecionar" está ativo por padrão
2. Clique no menu suspenso para ver todos os prompts disponíveis
3. Os prompts são listados com seus títulos extraídos do conteúdo do arquivo
4. Ao selecionar um prompt, sua descrição é exibida abaixo do seletor
5. O sistema carrega automaticamente todos os prompts da pasta `prompts/`

### Modo Manual

1. Clique no botão "Manual" na interface de upload
2. Digite o caminho completo para o arquivo de prompt
3. Exemplo: `prompts/unimed/padrao.md`
4. Este modo é útil para testar novos prompts que ainda não estão na lista

## Criando Seu Próprio Prompt Personalizado

Para criar um prompt personalizado:

1. Crie um arquivo de texto (preferencialmente com extensão `.md` ou `.txt`)
2. Defina claramente o formato JSON desejado como saída
3. Especifique cada campo que deve ser extraído e sua localização no documento
4. Adicione regras específicas de processamento e validação
5. Salve o arquivo na pasta apropriada dentro de `prompts/`

**Importante**: O formato de saída JSON deve ser compatível com a estrutura esperada pelo sistema, especialmente os campos:
- `codigo_ficha` (string)
- `registros` (array de objetos)
- Em cada registro: `data_atendimento`, `paciente_carteirinha`, `paciente_nome`, `guia_id` e `possui_assinatura`

### Exemplo de Estrutura de Prompt

```markdown
# Prompt para Extração de Fichas da Unimed
# Versão: 1.0
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
1. ATENÇÃO: APENAS linhas que possuem uma DATA DE ATENDIMENTO PREENCHIDA no campo 11 devem ser processadas
2. IGNORE COMPLETAMENTE linhas sem data de atendimento
...
```

## Como o Sistema Carrega os Prompts

O sistema utiliza um endpoint dedicado (`/api/prompts-disponiveis`) que:

1. Percorre a estrutura de diretórios `prompts/`
2. Identifica arquivos `.md` e `.txt`
3. Extrai o título da primeira linha (se começar com `#`) ou do nome do arquivo
4. Busca uma descrição nas primeiras linhas do arquivo
5. Retorna uma lista formatada com caminho, título e descrição para a interface

## Usando a API Diretamente

Para usar a API diretamente, adicione o parâmetro `prompt_path` nas suas requisições:

```python
import requests

url = "http://seu-servidor/api/upload-pdf"
files = {"files": open("documento.pdf", "rb")}
data = {
    "modelo_ia": "claude",
    "prompt_path": "prompts/unimed/padrao.md"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Dicas para Prompts Eficientes

1. **Seja Específico**: Descreva exatamente onde encontrar cada informação no documento
2. **Defina Regras Claras**: Indique claramente como lidar com casos especiais
3. **Forneça Exemplos**: Exemplos de saída esperada podem melhorar a precisão
4. **Formatação**: Especifique o formato exato para datas, números e outros campos
5. **Considere Padrões**: Explique padrões recorrentes no documento que podem ajudar na extração
6. **Versione seus Prompts**: Inclua número de versão e data de atualização no cabeçalho do prompt
7. **Documente Alterações**: Mantenha um histórico de alterações para cada prompt importante

## Boas Práticas para Gerenciamento de Prompts

1. **Nomenclatura Padronizada**: Use nomes descritivos e consistentes (ex: `convenio_tipo_versao.md`)
2. **Documentação Interna**: Cada prompt deve incluir cabeçalho com propósito, versão e data
3. **Testes Regulares**: Valide periodicamente os prompts com novos documentos
4. **Backup**: Mantenha backups dos prompts que funcionam bem
5. **Iteração Gradual**: Faça pequenas melhorias incrementais em vez de grandes mudanças

## Resolução de Problemas

Se o prompt personalizado não estiver funcionando como esperado:

1. **Verifique o Caminho**: Certifique-se de que o caminho para o arquivo está correto
2. **Formato do Arquivo**: Confirme que o arquivo está em formato texto (UTF-8 recomendado)
3. **Compatibilidade**: Verifique se a estrutura JSON solicitada é compatível com o sistema
4. **Modelo de IA**: Diferentes modelos podem responder de forma distinta ao mesmo prompt
5. **Logs**: Verifique os logs do sistema para mensagens de erro específicas
6. **Interface de Seleção**: Se o prompt não aparecer na lista suspensa, verifique:
   - Se o arquivo está na pasta `prompts/` ou em uma subpasta
   - Se o arquivo tem extensão `.md` ou `.txt`
   - Se o arquivo pode ser lido pelo sistema (permissões)

## Limitações

- O modelo de IA pode não seguir exatamente todas as instruções do prompt
- Documentos muito complexos ou de baixa qualidade podem afetar a precisão
- O processamento com prompts muito detalhados pode ser mais lento
- Os campos extraídos precisam seguir a estrutura esperada pelo sistema
