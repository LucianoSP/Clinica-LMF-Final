# Documentação da Funcionalidade de Upload de PDF e Extração de Dados

## Visão Geral

A funcionalidade de upload de PDF e extração de dados permite que os usuários enviem arquivos PDF contendo fichas de pacientes para o sistema. O processo automatiza a extração de informações relevantes dos documentos, armazena os arquivos no Cloudflare R2 e registra os dados extraídos no banco de dados Supabase.

O sistema utiliza um fluxo inteligente para processamento das fichas:
- Se a guia referenciada no documento existir no sistema, a ficha é criada na tabela `fichas`
- Se a guia não existir, a ficha é salva na tabela `fichas_pendentes` para processamento posterior

Além disso, o sistema permite a escolha entre diferentes modelos de IA para extração de dados:
1. **Claude (Anthropic)** - O modelo padrão, com excelente processamento de documentos
2. **Gemini (Google)** - Alternativa da Google para processamento de PDFs
3. **Mistral** - Alternativa open-source com bom desempenho em extração de dados

## Fluxo de Processamento

### Fluxo Unificado

1. **Recebimento do Arquivo**: O sistema recebe um ou mais arquivos PDF através do endpoint `/api/upload-pdf-unificado`.
2. **Seleção do Modelo de IA**: O usuário escolhe qual modelo de IA usar para o processamento (Claude, Gemini ou Mistral).
3. **Escolha de Prompt Personalizado** (Opcional): O usuário pode especificar um arquivo de prompt personalizado para a extração.
4. **Armazenamento Temporário**: Cada arquivo é temporariamente salvo no servidor para processamento.
5. **Extração de Dados**: O sistema utiliza o modelo de IA selecionado para extrair informações estruturadas do PDF.
6. **Validação dos Dados**: Os dados extraídos são validados para garantir que estão no formato esperado.
7. **Verificação de Guia**: O sistema verifica se a guia referenciada existe no banco de dados.
8. **Processamento Automático**:
   - Se a guia existir, o sistema salva o registro diretamente na tabela `fichas`
   - Se a guia não existir, o sistema salva o registro na tabela `fichas_pendentes` para processamento posterior
9. **Conversão de Datas**: As datas são convertidas do formato brasileiro (DD/MM/YYYY) para o formato ISO (YYYY-MM-DD).
10. **Renomeação do Arquivo**: O arquivo é renomeado seguindo o padrão "codigo_ficha - nome_paciente - data_envio.pdf".
11. **Upload para Cloudflare R2**: O arquivo renomeado é enviado para o armazenamento R2, em pastas específicas dependendo do destino (fichas/ ou fichas_pendentes/).
12. **Registro no Banco de Dados**: Os dados extraídos e a URL do arquivo são registrados nas tabelas correspondentes.

## Componentes Principais

### 1. Endpoint de Upload

```python
@router.post("/upload-pdf")
async def upload_pdf(
    files: List[UploadFile] = File(...),
    modelo_ia: str = Form("claude"),
    prompt_path: Optional[str] = Form(None)
)
```

Este endpoint recebe arquivos PDF e parâmetros adicionais como o modelo de IA a ser usado e o caminho do prompt personalizado. A resposta inclui informações sobre o resultado do processamento para cada arquivo.

### 2. Processador de PDF

```python
async def process_pdf(file: UploadFile, modelo_ia: str, prompt_path: Optional[str]) -> Dict
```

Esta função processa cada arquivo PDF individualmente. Ela é responsável por extrair dados do PDF, verificar a existência da guia e salvar o registro na tabela apropriada.

### 3. Extrator de Informações

```python
async def extract_info_from_pdf(pdf_path: str, api_key: str, modelo: str, prompt_path: str)
```

Esta função gerencia a extração de informações do PDF utilizando a IA escolhida. Três modelos são suportados:

- `extract_with_claude`: Utiliza a API Claude da Anthropic
- `extract_with_gemini`: Utiliza a API Gemini Pro Vision do Google
- `extract_with_mistral`: Utiliza o modelo Mistral para OCR e processamento

### 4. Interface de Upload de Arquivos

O componente React `FileUpload` na interface do usuário permite:
- Selecionar arquivos PDF
- Escolher o modelo de IA para o processamento
- Selecionar ou especificar um prompt personalizado
- Visualizar o progresso do upload

## Fluxo de Fichas Pendentes

As fichas que são registradas como pendentes (quando a guia não existe) podem ser posteriormente processadas através da interface de "Fichas Pendentes". O usuário pode:

1. Visualizar todas as fichas pendentes
2. Ver os dados extraídos de cada ficha
3. Associá-las a guias existentes
4. Criar novas guias e vincular as fichas
5. Processar as fichas manualmente

## Tratamento de Erros e Logs

O sistema inclui tratamento abrangente de erros e logs detalhados para rastrear o processamento de arquivos:

- Logs de validação de dados
- Registro de tempos de processamento
- Detalhes de erros na extração
- Informações sobre o armazenamento de arquivos
- Status de criação de registros no banco de dados

## Considerações de Segurança

- Os arquivos são armazenados em um ambiente seguro (Cloudflare R2)
- Os metadados dos arquivos são registrados no Supabase
- As chaves de API para os modelos de IA são armazenadas como variáveis de ambiente

## Armazenamento de Dados

### 1. Cloudflare R2

Os arquivos PDF são armazenados no Cloudflare R2 em dois caminhos:
- Modo Normal: `fichas/{codigo_ficha} - {nome_paciente} - {data_envio}.pdf`
- Modo Alternativo: `fichas_pendentes/{codigo_ficha}_{nome_paciente}_{timestamp}.pdf`

### 2. Banco de Dados Supabase

Os dados são armazenados em três tabelas:

#### Tabela "storage"
- Contém metadados dos arquivos armazenados no R2
- Inclui campos como nome, URL, tamanho e tipo de conteúdo

#### Tabela "fichas"
- Armazena dados de fichas quando o modo normal é bem-sucedido
- Inclui a referência à guia existente ou criada automaticamente

#### Tabela "fichas_pendentes"
- Armazena dados de fichas quando o modo alternativo é usado
- Contém os mesmos dados da ficha mais um campo `dados_extraidos` em formato JSON
- Inclui campos de controle como `processado` e `data_processamento`
- Pode ser processada posteriormente para criar fichas regulares

## Configuração do Ambiente

Para configurar os modelos de IA, adicione as seguintes variáveis ao arquivo `.env`:

```
# Chaves API para os modelos de IA
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui  # Para o Claude
GEMINI_API_KEY=sua_chave_gemini_aqui        # Para o Gemini
MISTRAL_API_KEY=sua_chave_mistral_aqui      # Para o Mistral
```

Para o Gemini, certifique-se de que sua chave de API tenha acesso ao modelo `gemini-1.5-pro`, que oferece melhor suporte para processamento de documentos.

## Comparação dos Modelos de IA

| Modelo    | Fornecedor | Pontos Fortes                   | Considerações                       |
|-----------|------------|--------------------------------|-------------------------------------|
| Claude    | Anthropic  | Excelente interpretação de PDFs, fiel aos layouts dos documentos | Maior custo, requer API key comercial |
| Gemini    | Google     | Boa relação custo-benefício, bom em tabelas | Menor precisão em layouts complexos |
| Mistral   | Mistral AI | API OCR dedicada, preservação de layout, reconhecimento de tabelas | Requer plano com acesso a OCR |

## Tratamento de Erros

O sistema registra logs detalhados e inclui tratamento para:
- Falha na extração de dados do PDF
- Guia inexistente no sistema
- Falha ao criar guia automaticamente
- Paciente ou carteirinha não encontrados
- Chave de API não configurada ou inválida
- Outros erros de banco de dados ou processamento

## Processamento Manual de Fichas Pendentes

As fichas armazenadas na tabela `fichas_pendentes` podem ser:
1. Revisadas na interface de administração
2. Processadas manualmente após a criação das guias necessárias
3. Excluídas manualmente se não forem necessárias

Quando uma ficha pendente é processada com sucesso, ela é automaticamente excluída da tabela `fichas_pendentes` e uma nova ficha é criada na tabela `fichas`. Isso mantém a tabela de fichas pendentes limpa, contendo apenas fichas que realmente precisam de atenção.

O processamento manual pode ser realizado através da interface de usuário na aba "Fichas Pendentes" da página de Fichas, onde o usuário tem as seguintes opções:
- Visualizar o PDF original
- Examinar os dados extraídos
- Processar a ficha (criar nova guia ou vincular a existente)
- Excluir a ficha pendente

## Considerações de Segurança

- A função SQL `inserir_ficha_bypass_fk` deve ser usada com cautela para evitar inconsistências no banco de dados
- O modo alternativo deve ser usado apenas quando necessário, sendo o modo normal preferido
- As chaves de API dos modelos de IA devem ser mantidas seguras e nunca expostas no código-fonte
- Todos os processos são completamente registrados em logs para auditoria

## Exemplo de Uso

### Modo Normal com Seleção de Modelo de IA e Prompt Personalizado
1. Selecione "Modo Normal" na interface de upload
2. Escolha o modelo de IA desejado (Claude, Gemini ou Mistral)
3. Opcionalmente, informe o caminho para um arquivo de prompt personalizado
4. Envie um ou mais arquivos PDF para processamento
5. O sistema tentará processar os arquivos usando o modelo selecionado e as instruções do prompt

### Modo Alternativo com Seleção de Modelo de IA e Prompt Personalizado
1. Selecione "Modo Alternativo" na interface de upload
2. Escolha o modelo de IA desejado (Claude, Gemini ou Mistral)
3. Opcionalmente, informe o caminho para um arquivo de prompt personalizado
4. Envie um ou mais arquivos PDF para processamento
5. O sistema salvará os dados extraídos como pendentes para processamento posterior

## Customização do Processamento

### Prompts Personalizados para Extração
O sistema suporta o uso de prompts personalizados para otimizar a extração de dados de diferentes tipos de documentos. Os prompts são organizados em uma estrutura de pastas dedicada:

```
prompts/
├── unimed/         # Prompts específicos para documentos da Unimed
│   ├── padrao.md   # Prompt padrão para fichas da Unimed
│   └── especial.md # Prompt para casos especiais da Unimed
├── outros/         # Prompts para outros convênios ou tipos de documentos
└── README.md       # Documentação sobre os prompts disponíveis
```

Para usar um prompt personalizado, especifique o caminho relativo no campo "Arquivo de Prompt Personalizado" na interface de upload ou no parâmetro `prompt_path` da API.

Para mais detalhes sobre criação e uso de prompts personalizados, consulte a documentação específica em `instrucoes/prompts_personalizados.md`.

## Solução de Problemas Comuns

### Erro "Chave API não configurada"
Este erro ocorre quando a chave API do modelo selecionado não foi configurada:
1. Verifique se o modelo selecionado está disponível para sua conta
2. Configure a chave API correspondente no arquivo `.env`
3. Reinicie o servidor após adicionar a chave

### Erro "Modelo de IA inválido"
Ocorre quando o modelo especificado não é suportado:
1. Use apenas os modelos oficialmente suportados: claude, gemini ou mistral
2. Verifique a grafia correta do nome do modelo

### Erro "Guia não encontrada"
Este erro ocorre quando o sistema não consegue encontrar ou criar automaticamente a guia referenciada:
1. Verifique se o número da guia está correto no PDF
2. Verifique se o paciente e a carteirinha existem no sistema
3. Use o modo alternativo se precisar fazer o upload antes de criar as guias

### Erro específico do Gemini: "Quota exceeded" ou "API key not valid"
Ocorre quando há problemas com a chave de API do Gemini:
1. Verifique se a chave API foi copiada corretamente
2. Verifique se você não excedeu o limite de solicitações gratuitas
3. Consulte a documentação específica em `instrucoes/configuracao_gemini.md` para mais detalhes

### Erro específico do Mistral: "OCR processing failed"
Ocorre quando há problemas no processamento do documento:
1. Verifique se o PDF está em um formato padrão
2. Verifique se o tamanho do arquivo não excede o limite permitido (geralmente 25MB)
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

### Erro específico do Mistral: "API key not authorized for OCR"
Ocorre quando sua chave de API não tem permissão para usar o recurso de OCR:
1. Verifique seu plano e permissões no console da Mistral AI
2. Certifique-se de que sua conta tem acesso ao modelo `mistral-ocr-latest`
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

### Erro específico do Mistral: "Validation errors for Unmarshaller"
Ocorre quando há problemas com o formato dos dados enviados para a API:
1. Este erro foi corrigido na versão atual do sistema, que agora usa a API OCR corretamente
2. Se o erro persistir, verifique se você está usando a versão mais recente do código
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

### Erro específico do Mistral: "'OCRResponse' object has no attribute 'id'"
Este erro não é mais relevante com a nova implementação:
1. A implementação atual usa a API OCR corretamente
2. Se você encontrar este erro, verifique se está usando a versão mais recente do código
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

### Erro específico do Mistral: "Document content must be a URL (starting with 'https')"
Ocorre quando há problemas com o formato da URL do documento:
1. Este erro foi corrigido na versão atual do sistema, que agora usa URLs assinadas geradas pelo serviço de arquivos do Mistral
2. Se o erro persistir, verifique se você está usando a versão mais recente do código
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

### Erro específico do Mistral: "Input should be 'fine-tune', 'batch', 'ocr' or 'code_interpreter'"
Ocorre quando há problemas com o valor do parâmetro `purpose` no upload de arquivos:
1. Este erro foi corrigido na versão atual do sistema, que agora usa `purpose="ocr"` para o upload de PDFs
2. Se o erro persistir, verifique se você está usando a versão mais recente do código
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

### Erro específico do Mistral: "Input tag 'file_id' found does not match any of the expected tags"
Este erro não é mais relevante com a nova implementação:
1. A implementação atual não usa mais tags de conteúdo complexas
2. Se você encontrar este erro, verifique se está usando a versão mais recente do código
3. Consulte a documentação específica em `instrucoes/configuracao_mistral.md` para mais detalhes

## Como Usar a Interface de Upload

### Seleção de Modelo de IA e Prompt Personalizado

1. Acesse a interface de upload de PDF clicando no botão "Upload de PDF" na página de fichas
2. Escolha o modo de upload desejado:
   - **Modo Normal**: Para processar fichas quando as guias já existem no sistema
   - **Modo Alternativo**: Para processar fichas mesmo quando as guias não existem
3. Selecione o modelo de IA a ser usado para processamento:
   - **Claude (Anthropic)**: Recomendado para a maioria dos casos
   - **Gemini (Google)**: Alternativa com bom custo-benefício
   - **Mistral**: Opção adicional para processamento
4. Escolha um prompt personalizado (opcional):
   - **Modo Seleção**: Escolha um prompt da lista suspensa de prompts disponíveis
   - **Modo Manual**: Digite manualmente o caminho para um arquivo de prompt
   - Deixe em branco para usar o prompt padrão do sistema
5. Arraste e solte os arquivos PDF ou clique para selecioná-los
6. Clique em "Processar" para iniciar o processamento

![Interface de Upload](../assets/images/interface_upload.png)

### Detalhes da Interface de Seleção de Prompts

A interface oferece duas maneiras de selecionar um prompt personalizado:

1. **Modo Seleção** (recomendado):
   - Exibe uma lista suspensa com todos os prompts disponíveis no sistema
   - Os prompts são carregados automaticamente da pasta `prompts/`
   - Mostra o título e descrição do prompt selecionado
   - Facilita a escolha sem precisar digitar o caminho completo

2. **Modo Manual**:
   - Permite digitar manualmente o caminho para um arquivo de prompt
   - Útil para testar novos prompts que ainda não estão na lista
   - Formato esperado: `prompts/categoria/nome_do_prompt.md`
