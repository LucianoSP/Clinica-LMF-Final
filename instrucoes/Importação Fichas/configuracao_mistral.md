# Configuração e Uso da API Mistral para Processamento de PDFs

## Visão Geral

O Mistral AI oferece recursos avançados de processamento de documentos através de sua API OCR dedicada. Nossa implementação utiliza a biblioteca oficial `mistralai` para processar PDFs em duas etapas: primeiro extraindo o texto com a API OCR e depois analisando esse texto com um modelo de linguagem.

## Requisitos

Para utilizar o processamento do Mistral, você precisa:

1. Uma conta na [Plataforma Mistral AI](https://console.mistral.ai/)
2. Uma chave de API válida com acesso aos recursos de OCR, chat e upload de arquivos
3. Instalação da biblioteca oficial: `pip install mistralai==0.0.9`

## Configuração

### 1. Obtenção da Chave de API

1. Acesse [console.mistral.ai](https://console.mistral.ai/)
2. Faça login ou crie uma conta
3. Navegue até "API Keys" 
4. Clique em "Create API Key"
5. Dê um nome para sua chave (ex: "pdf-processor")
6. Copie a chave gerada (você não poderá vê-la novamente)

### 2. Configuração no Arquivo .env

Adicione sua chave de API ao arquivo `.env` na raiz do projeto:

```
MISTRAL_API_KEY=sua_chave_aqui
```

### 3. Verificação de Acesso

O acesso aos recursos de upload de arquivos, OCR e chat pode estar sujeito a limitações dependendo do seu plano. Verifique no console do Mistral AI se você tem acesso ao modelo `mistral-ocr-latest` e à API de arquivos.

## Como Funciona a Implementação

Nossa implementação do processamento de PDFs com o Mistral segue estas etapas:

```python
# Fazer upload do arquivo PDF para o Mistral
with open(pdf_path, "rb") as pdf_file:
    uploaded_file = client.files.upload(
        file={
            "file_name": os.path.basename(pdf_path),
            "content": pdf_file,
        },
        purpose="ocr"
    )

# Obter URL assinada para o arquivo
signed_url = client.files.get_signed_url(file_id=uploaded_file.id)

# Processar o documento com OCR
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": signed_url.url
    }
)

# Extrair o texto do documento processado
document_text = "\n\n".join([f"### Página {i+1}\n{ocr_response.pages[i].markdown}" for i in range(len(ocr_response.pages))])

# System prompt para melhorar os resultados
system_prompt = """
Você é um assistente especializado em extrair informações estruturadas de documentos PDF.
Sua tarefa é analisar documentos de fichas médicas e extrair dados específicos no formato JSON.

Siga rigorosamente as regras de extração fornecidas e retorne apenas o JSON solicitado.
"""

# Enviar o texto extraído para o modelo de chat com o prompt do usuário
messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": f"{prompt}\n\nConteúdo do documento:\n\n{document_text}"
    }
]

# Obter a resposta do chat
chat_response = client.chat.complete(
    model="mistral-large-latest",
    messages=messages,
    temperature=0.0,
    max_tokens=4096
)
```

Esta implementação utiliza a API OCR dedicada do Mistral para extrair o texto do documento, e depois envia esse texto para um modelo de linguagem para análise estruturada.

## Vantagens do Processamento de Documentos do Mistral

1. **OCR Especializado**: O modelo `mistral-ocr-latest` é otimizado para reconhecimento de texto em documentos
2. **Processamento em Duas Etapas**: Separação clara entre extração de texto e análise estruturada
3. **Preservação de Layout**: O OCR preserva a estrutura do documento, facilitando a extração de dados
4. **Temperatura Zero**: Usamos temperatura 0.0 para obter respostas determinísticas e consistentes
5. **Alta Precisão**: A API OCR dedicada oferece reconhecimento preciso de texto em documentos complexos

## Solução de Problemas

### Erro: "Document processing failed"

- **Causa possível**: Formato de documento não suportado ou documento muito grande
- **Solução**: Verifique se o PDF está em um formato padrão e não excede os limites de tamanho

### Erro: "API key not authorized for OCR"

- **Causa possível**: Sua chave de API não tem permissão para usar o recurso de OCR
- **Solução**: Verifique seu plano e permissões no console da Mistral AI

### Erro: "Rate limit exceeded"

- **Causa possível**: Você excedeu o número de solicitações permitidas em seu plano
- **Solução**: Aguarde um pouco antes de tentar novamente ou considere fazer upgrade do seu plano

### Erro: "Validation errors for Unmarshaller"

- **Causa possível**: Formato incorreto dos dados enviados para a API
- **Solução**: Certifique-se de que está usando o formato correto para enviar documentos

### Erro: "Document content must be a URL (starting with 'https')"

- **Causa possível**: Tentativa de enviar documento como URL de dados (data:application/pdf;base64,...)
- **Solução**: Use a API de upload de arquivos do Mistral e depois a API OCR, como implementado na versão atual

### Erro: "Input should be 'fine-tune', 'batch', 'ocr' or 'code_interpreter'"

- **Causa possível**: Valor incorreto para o parâmetro `purpose` no upload de arquivos
- **Solução**: Use apenas os valores permitidos: `'fine-tune'`, `'batch'`, `'ocr'` ou `'code_interpreter'`. Para processamento de PDFs, use `purpose="ocr"`

## Comparação com Outros Modelos

A abordagem de processamento de documentos do Mistral oferece vantagens específicas para certos casos de uso:

| Recurso | Mistral | Claude | Gemini |
|---------|---------|--------|--------|
| API OCR Dedicada | ✅ | ❌ | ❌ |
| Preservação de layout | Muito boa | Excelente | Boa |
| Reconhecimento de tabelas | Muito bom | Excelente | Muito bom |
| Custo | Médio | Alto | Médio-Baixo |
| Tamanho máximo | 25MB | 10MB | 20MB |

## Recursos Adicionais

- [Documentação oficial da API Mistral](https://docs.mistral.ai/)
- [Guia de processamento de documentos do Mistral](https://docs.mistral.ai/capabilities/document/)
- [Documentação da API de OCR do Mistral](https://docs.mistral.ai/api/ocr/)
- [Documentação da API de arquivos do Mistral](https://docs.mistral.ai/api/files/)
- [Exemplos de Uso](https://github.com/mistralai/client-python) 