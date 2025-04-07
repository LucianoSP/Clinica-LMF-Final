# API de Prompts Personalizados

## Visão Geral

O sistema oferece um endpoint de API para listar todos os prompts personalizados disponíveis. Esta API é utilizada pela interface de upload para exibir os prompts na lista suspensa, mas também pode ser usada por outras aplicações ou scripts que precisem conhecer os prompts disponíveis.

## Endpoint para Listar Prompts

### Requisição

```
GET /api/prompts-disponiveis
```

### Resposta

A resposta é um objeto JSON com a seguinte estrutura:

```json
{
  "success": true,
  "prompts": [
    {
      "path": "prompts/unimed/padrao.md",
      "title": "Prompt Padrão para Extração de Fichas da Unimed",
      "description": "Analise este documento PDF de atendimento médico da Unimed e extraia as seguintes informações em JSON válido..."
    },
    {
      "path": "prompts/unimed/especial.md",
      "title": "Prompt para Casos Especiais de Fichas da Unimed",
      "description": "Analise este documento PDF de atendimento médico da Unimed e extraia as seguintes informações em JSON válido..."
    }
  ]
}
```

### Campos da Resposta

- **success**: Booleano indicando se a requisição foi bem-sucedida
- **prompts**: Array de objetos representando os prompts disponíveis
  - **path**: Caminho relativo para o arquivo de prompt
  - **title**: Título do prompt (extraído da primeira linha do arquivo ou do nome do arquivo)
  - **description**: Descrição do prompt (extraída das primeiras linhas do arquivo)

### Exemplo de Uso

```javascript
// Exemplo em JavaScript
async function carregarPrompts() {
  try {
    const response = await fetch('/api/prompts-disponiveis');
    const data = await response.json();
    
    if (data.success) {
      // Processar a lista de prompts
      console.log(`${data.prompts.length} prompts disponíveis`);
      data.prompts.forEach(prompt => {
        console.log(`- ${prompt.title} (${prompt.path})`);
      });
    } else {
      console.error('Erro ao carregar prompts:', data.message);
    }
  } catch (error) {
    console.error('Erro na requisição:', error);
  }
}
```

```python
# Exemplo em Python
import requests

def carregar_prompts():
    try:
        response = requests.get('http://seu-servidor/api/prompts-disponiveis')
        data = response.json()
        
        if data['success']:
            # Processar a lista de prompts
            print(f"{len(data['prompts'])} prompts disponíveis")
            for prompt in data['prompts']:
                print(f"- {prompt['title']} ({prompt['path']})")
        else:
            print(f"Erro ao carregar prompts: {data.get('message')}")
    except Exception as e:
        print(f"Erro na requisição: {str(e)}")
```

## Como o Sistema Identifica Prompts

O endpoint percorre a estrutura de diretórios `prompts/` e identifica arquivos com extensão `.md` ou `.txt`. Para cada arquivo encontrado:

1. O caminho relativo é normalizado para o formato Unix (usando `/` como separador)
2. O título é extraído da primeira linha do arquivo, se começar com `#` (formato Markdown)
3. Se não houver um título no formato Markdown, o nome do arquivo é usado como título
4. Uma descrição é extraída das primeiras linhas do arquivo (ignorando linhas que começam com `#` ou `{`)
5. A descrição é truncada para no máximo 100 caracteres, seguida de "..." se for mais longa

## Implementação no Backend

O endpoint é implementado no arquivo `backend/routes/upload.py` e utiliza o módulo `os.walk` para percorrer a estrutura de diretórios.

## Considerações de Segurança

- O endpoint apenas lista arquivos dentro da pasta `prompts/` e suas subpastas
- Apenas arquivos com extensão `.md` ou `.txt` são considerados
- O conteúdo dos arquivos é lido apenas para extrair o título e descrição
- Erros na leitura de arquivos individuais não interrompem o processamento dos demais

## Solução de Problemas

Se um prompt não aparecer na lista retornada pela API:

1. Verifique se o arquivo está na pasta `prompts/` ou em uma subpasta
2. Confirme que o arquivo tem extensão `.md` ou `.txt`
3. Verifique as permissões do arquivo (o servidor deve ter permissão de leitura)
4. Verifique os logs do servidor para mensagens de erro específicas
5. Certifique-se de que o arquivo está em formato texto (UTF-8 recomendado) 