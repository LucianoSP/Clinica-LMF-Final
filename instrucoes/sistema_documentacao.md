# Sistema de Documentação Integrado

## Visão Geral

O Sistema de Documentação Integrado permite acessar toda a documentação do projeto diretamente através da interface do aplicativo, sem necessidade de acessar os arquivos markdown manualmente. Esta funcionalidade facilita a consulta à documentação por todos os membros da equipe, garantindo que as informações estejam sempre acessíveis e atualizadas.

## Funcionalidades

- **Navegação por Índice**: Utiliza o arquivo `indice_geral.md` como ponto de entrada e índice principal
- **Listagem de Arquivos**: Exibe todos os arquivos de documentação disponíveis na pasta `instrucoes`
- **Busca de Documentos**: Permite filtrar documentos por nome para encontrar rapidamente o conteúdo desejado
- **Navegação por Links**: Suporta navegação através de links entre documentos markdown
- **Interface Responsiva**: Layout adaptável para diferentes tamanhos de tela
- **Visualização Formatada**: Renderização de markdown com sintaxe destacada para código

## Arquitetura

### Backend

O backend expõe dois endpoints principais para servir a documentação:

1. **Listar Arquivos**: `/docs/instrucoes` - Retorna uma lista de todos os arquivos markdown disponíveis
2. **Obter Conteúdo**: `/docs/instrucoes/{nome_arquivo}` - Retorna o conteúdo de um arquivo específico

Implementação no arquivo `app.py`:

```python
@app.get("/docs/instrucoes", tags=["Documentação"])
async def listar_arquivos_documentacao():
    """Lista todos os arquivos de documentação disponíveis na pasta instrucoes"""
    try:
        # Lista arquivos na pasta instrucoes
        arquivos = os.listdir("instrucoes")
        # Filtra apenas arquivos markdown
        arquivos_md = [arquivo for arquivo in arquivos if arquivo.endswith(".md")]
        return arquivos_md
    except Exception as e:
        logger.error(f"Erro ao listar arquivos de documentação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar arquivos de documentação"
        )

@app.get("/docs/instrucoes/{nome_arquivo}", tags=["Documentação"])
async def obter_arquivo_documentacao(nome_arquivo: str):
    """Obtém o conteúdo de um arquivo de documentação específico da pasta instrucoes"""
    try:
        # Verifica se o arquivo solicitado existe
        caminho_arquivo = os.path.join("instrucoes", nome_arquivo)
        if not os.path.exists(caminho_arquivo):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo '{nome_arquivo}' não encontrado"
            )
        
        # Verifica se o arquivo solicitado é um markdown
        if not nome_arquivo.endswith(".md"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos markdown (.md) são permitidos"
            )
        
        # Lê o conteúdo do arquivo
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            conteudo = file.read()
        
        return PlainTextResponse(conteudo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de documentação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao ler arquivo de documentação"
        )
```

### Frontend

O frontend implementa um serviço para comunicação com o backend e uma interface de usuário para visualização dos documentos:

1. **Serviço de Documentação**: Responsável por buscar a lista de arquivos e o conteúdo de cada documento
2. **Componente de Visualização**: Renderiza o conteúdo markdown com formatação adequada
3. **Página de Documentação**: Interface principal com navegação lateral e área de conteúdo

#### Serviço de Documentação

```typescript
// documentacaoService.ts
export const documentacaoService = {
  async obterArquivo(nomeArquivo: string): Promise<DocumentacaoResponse> {
    try {
      const response = await api.get(`/docs/instrucoes/${nomeArquivo}`);
      return {
        success: true,
        data: response.data as string
      };
    } catch (error) {
      console.error("Erro ao obter arquivo de documentação:", error);
      return {
        success: false,
        message: "Não foi possível carregar o arquivo de documentação"
      };
    }
  },

  async listarArquivos(): Promise<{ success: boolean; items?: string[]; message?: string }> {
    try {
      const response = await api.get('/docs/instrucoes');
      return {
        success: true,
        items: response.data as string[]
      };
    } catch (error) {
      console.error("Erro ao listar arquivos de documentação:", error);
      return {
        success: false,
        message: "Não foi possível listar os arquivos de documentação"
      };
    }
  }
};
```

#### Componente de Visualização Markdown

O componente `MarkdownViewer` utiliza a biblioteca `react-markdown` para renderizar o conteúdo markdown com formatação adequada, incluindo:

- Títulos hierárquicos
- Listas ordenadas e não-ordenadas
- Blocos de código com destaque de sintaxe
- Tabelas formatadas
- Links clicáveis (incluindo navegação entre documentos)

## Como Usar

1. Acesse a página de documentação através do menu lateral, clicando em "Documentação"
2. O índice geral será exibido por padrão
3. Navegue pelos documentos usando:
   - A barra lateral com a lista de arquivos disponíveis
   - Os links dentro do conteúdo dos documentos
   - A caixa de busca para filtrar documentos por nome

## Manutenção da Documentação

Para adicionar ou atualizar a documentação:

1. Crie ou edite arquivos markdown na pasta `instrucoes/`
2. Atualize o `indice_geral.md` se necessário para incluir links para os novos documentos
3. Os arquivos serão automaticamente disponibilizados na interface de documentação

## Benefícios

- **Centralização**: Toda a documentação acessível em um único local
- **Facilidade de Acesso**: Não é necessário navegar pelo sistema de arquivos
- **Navegação Intuitiva**: Interface amigável com busca e navegação por links
- **Consistência Visual**: Formatação padronizada para todos os documentos
- **Integração**: Documentação integrada ao próprio aplicativo

## Considerações Técnicas

- A documentação é carregada sob demanda, minimizando o impacto no desempenho
- Os arquivos markdown são servidos como texto puro e renderizados no cliente
- A navegação entre documentos é gerenciada no frontend, sem necessidade de recarregar a página
- O sistema suporta a adição de novos documentos sem necessidade de alterações no código 