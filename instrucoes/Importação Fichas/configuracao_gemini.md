# Configuração e Uso da API Gemini para Processamento de PDFs

## Visão Geral
Este documento detalha como configurar e utilizar a API Gemini (Google) para processamento de documentos PDF em nosso sistema. A implementação utiliza a biblioteca oficial `google-genai` para processar PDFs e extrair informações estruturadas.

## Requisitos
Para utilizar a API Gemini, você precisará:

1. Uma conta no Google AI Studio ou Google Cloud Platform
2. Uma chave de API válida para o modelo Gemini 1.5 Pro
3. A biblioteca `google-genai` instalada:
   ```
   pip install -q -U google-genai
   ```

## Obtendo a Chave de API

### Opção 1: Google AI Studio (mais simples)
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key" (Criar Chave de API)
4. Copie a chave gerada para uso no sistema

### Opção 2: Google Cloud Platform (mais completo)
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a API Vertex AI ou Gemini API para seu projeto
4. Navegue até "APIs & Services" > "Credentials"
5. Clique em "Create Credentials" > "API Key"
6. Recomendamos restringir a chave apenas para a API Gemini/Vertex AI
7. Copie a chave gerada para uso no sistema

## Configuração da Chave API
1. Adicione sua chave API ao arquivo `.env` na raiz do projeto:
   ```
   GEMINI_API_KEY=sua_chave_api_aqui
   ```
2. Certifique-se de que sua chave tenha acesso ao modelo `gemini-1.5-pro` para melhor processamento de documentos

## Como Funciona a Implementação
Nossa implementação utiliza o modelo Gemini 1.5 Pro para processar PDFs e extrair informações estruturadas. Veja como funciona:

1. **Inicialização do Cliente**:
   ```python
   import google.genai as genai
   
   # Configuração do cliente
   genai.configure(api_key=api_key)
   
   # Criação do modelo com instruções de sistema
   model = genai.GenerativeModel(
       model_name="gemini-1.5-pro",
       system_instruction="Você é um assistente especializado em extrair informações de documentos PDF..."
   )
   ```

2. **Envio do PDF para Processamento**:
   ```python
   # Configuração da geração
   generation_config = {
       "temperature": 0.1,  # Baixa temperatura para respostas determinísticas
       "top_p": 0.95,
       "top_k": 40,
       "max_output_tokens": 8192,
   }
   
   # Envio do PDF como objeto Blob
   response = model.generate_content(
       [pdf_content],
       generation_config=generation_config
   )
   ```

3. **Processamento da Resposta**:
   ```python
   # Extração do texto da resposta
   extracted_text = response.text
   
   # Processamento adicional conforme necessário
   # ...
   ```

## Vantagens do Modelo Gemini
- **Instruções de Sistema**: Permite contextualizar o modelo para tarefas específicas
- **Temperatura Baixa**: Configuração com temperatura 0.1 para respostas mais determinísticas
- **Processamento Multimodal**: Capacidade de processar texto e imagens simultaneamente
- **Extração Estruturada**: Otimizado para extrair dados em formato estruturado

## Solução de Problemas Comuns

### Erro: "API key not valid"
- Verifique se a chave API foi copiada corretamente
- Confirme se a chave não expirou
- Certifique-se de que a chave tem permissões para acessar a API Gemini

### Erro: "Quota exceeded"
- Verifique os limites de uso da sua conta
- Considere atualizar para um plano com maior cota
- Implemente lógica de retry com backoff exponencial

### Erro: "Model not available"
- Confirme se o modelo `gemini-1.5-pro` está disponível na sua região
- Verifique se sua conta tem acesso ao modelo solicitado

### Erro: "Content filtered"
- O conteúdo pode ter sido bloqueado pelos filtros de segurança do Google
- Revise o conteúdo do PDF para garantir que não viole as políticas de uso

## Dicas para Otimizar Resultados
1. **Ajuste de Temperatura**: Use valores baixos (0.1-0.3) para extração de dados estruturados
2. **Instruções Claras**: Forneça instruções específicas no prompt para melhorar a precisão
3. **Limite de Tokens**: Esteja ciente dos limites de tokens do modelo
4. **Qualidade do Documento**: PDFs bem formatados produzem melhores resultados

## Recursos Adicionais
- [Documentação Oficial do Google Gemini](https://ai.google.dev/docs)
- [Guia de Melhores Práticas para Prompts](https://ai.google.dev/docs/prompting-guide)
- [Limites e Cotas da API](https://ai.google.dev/docs/quotas_and_limits) 