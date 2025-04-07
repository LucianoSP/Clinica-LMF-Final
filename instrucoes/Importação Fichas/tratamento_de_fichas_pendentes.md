<think>O usuário está informando que o modo alternativo de upload de PDF funcionou e os registros foram salvos corretamente na tabela fichas_pendentes. Agora, ele está perguntando como devemos tratar esses registros.

Vou propor algumas opções para processar os registros da tabela fichas_pendentes, que é uma tabela temporária com dados que não puderam ser inseridos diretamente na tabela de fichas por questões de integridade referencial (como guias inexistentes).</think>Ótimo! É muito bom saber que o modo alternativo está funcionando corretamente e os dados estão sendo salvos na tabela `fichas_pendentes`. Vamos discutir a melhor estratégia para tratar esses registros.

# Implementação do Tratamento de Fichas Pendentes

## Visão Geral

O sistema agora possui uma funcionalidade completa para gerenciar fichas pendentes que foram enviadas através do método alternativo de upload. A implementação inclui tanto o backend quanto o frontend, permitindo que os usuários visualizem, filtrem e processem as fichas pendentes de forma intuitiva.

## Implementação Backend

### 1. Endpoints para Fichas Pendentes

Foram implementados dois novos endpoints na API para gerenciar as fichas pendentes:

```python
@router.get("/pendentes")
async def listar_fichas_pendentes(
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    processado: Optional[bool] = None,
    order_column: str = "created_at",
    order_direction: str = "desc",
    db = Depends(get_supabase_client)
) -> Dict:
    """Lista fichas pendentes com paginação e filtros"""
    # Implementação...
```

Este endpoint retorna uma lista paginada de fichas pendentes, com suporte para busca, filtros por status de processamento e ordenação.

```python
@router.post("/pendentes/{id}/processar")
async def processar_ficha_pendente(
    id: str,
    opcoes: Dict,
    db = Depends(get_supabase_client)
) -> Dict:
    """Processa uma ficha pendente, criando ou vinculando a uma guia"""
    # Implementação...
```

Este endpoint processa uma ficha pendente específica, com opções para criar uma nova guia automaticamente ou vincular a uma guia existente.

### 2. Lógica de Processamento

A lógica de processamento de fichas pendentes inclui:

- Verificação se a ficha já foi processada anteriormente
- Opção para criar uma nova guia automaticamente com base nos dados extraídos
- Opção para vincular a ficha a uma guia existente
- Criação da ficha regular no sistema após o processamento
- **Exclusão automática da ficha pendente** após o processamento bem-sucedido

> **Importante**: Quando uma ficha pendente é processada com sucesso, ela é **automaticamente excluída** da tabela `fichas_pendentes`. Isso mantém a tabela limpa, contendo apenas fichas que realmente precisam de atenção.

## Implementação Frontend

### 1. Serviço de Fichas Pendentes

Foi criado um novo serviço `fichasPendentesService.ts` para interagir com os endpoints da API:

```typescript
export interface FichaPendente {
  id: string;
  storage_id: string;
  dados_extraidos: any;
  status: string;
  arquivo_url: string;
  numero_guia: string;
  paciente_nome: string;
  paciente_carteirinha: string;
  data_atendimento: string;
  total_sessoes: number;
  codigo_ficha: string;
  observacoes: string;
  processado: boolean;
  data_processamento: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProcessarFichaOptions {
  criar_guia?: boolean;
  guia_id?: string;
}

// Métodos implementados:
// - listar(params): Lista fichas pendentes com paginação e filtros
// - obterPorId(id): Obtém uma ficha pendente específica
// - processar(id, opcoes): Processa uma ficha pendente
// - buscarGuiasDisponiveis(numeroGuia): Busca guias disponíveis para vinculação
// - excluir(id): Exclui uma ficha pendente
```

### 2. Componente de Fichas Pendentes

Foi desenvolvido um novo componente `FichasPendentesTab.tsx` que implementa a interface para gerenciar fichas pendentes:

- Tabela de listagem de fichas pendentes usando o componente `SortableTable`
- Filtros para busca por código, guia ou paciente
- Filtro por status de processamento (processado/não processado)
- Ordenação por diferentes campos
- Paginação completa
- Menu de ações para cada ficha (visualizar PDF, visualizar dados, processar, excluir)
- Modal para visualização detalhada dos dados extraídos
- Modal para processamento de fichas com opções para criar guia ou vincular a existente

### 3. Integração na Página de Fichas

O componente de fichas pendentes foi integrado à página de fichas existente usando um sistema de abas:

```tsx
<Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
    <TabsList className="mb-4">
        <TabsTrigger value="fichas">Fichas</TabsTrigger>
        <TabsTrigger value="fichas_pendentes">Fichas Pendentes</TabsTrigger>
    </TabsList>
    
    <TabsContent value="fichas">
        {/* Conteúdo original da página de fichas */}
    </TabsContent>
    
    <TabsContent value="fichas_pendentes">
        <FichasPendentesTab />
    </TabsContent>
</Tabs>
```

## Funcionalidades Implementadas

### 1. Listagem de Fichas Pendentes

- Visualização em tabela com colunas para status, código, guia, paciente, data de atendimento e data de upload
- Indicador visual de status usando badges com cores pasteis
- Contagem total de fichas pendentes
- Ordenação por qualquer coluna (ascendente/descendente)

### 2. Filtros e Busca

- Campo de busca para filtrar por código, número de guia ou nome do paciente
- Filtro por status de processamento
- Botão para atualizar a listagem

### 3. Visualização de Detalhes

- Modal para visualização do PDF original
- Modal para visualização dos dados extraídos em formato JSON
- Exibição formatada dos dados básicos (código, guia, paciente, carteirinha, data, sessões)

### 4. Processamento de Fichas

- Opção para criar uma nova guia automaticamente com os dados extraídos
- Opção para vincular a uma guia existente
- Busca de guias disponíveis pelo número da guia
- Feedback visual sobre o resultado do processamento
- **Remoção automática** da ficha pendente após processamento bem-sucedido

### 5. Exclusão Manual de Fichas

- Opção para excluir manualmente fichas pendentes que não serão processadas
- Confirmação antes da exclusão para evitar operações acidentais
- Atualização automática da lista após a exclusão

## Fluxo de Trabalho

1. O usuário acessa a página de Fichas e seleciona a aba "Fichas Pendentes"
2. O sistema exibe a lista de fichas pendentes com indicadores visuais de status
3. O usuário pode filtrar, buscar ou ordenar a lista conforme necessário
4. Para cada ficha, o usuário pode:
   - Visualizar o PDF original
   - Examinar os dados extraídos
   - Processar a ficha escolhendo entre criar uma nova guia ou vincular a uma existente
   - Excluir a ficha se não for necessária
5. Após o processamento, a ficha é **automaticamente excluída** da lista de pendentes e aparece na lista regular de fichas

## Benefícios da Implementação

- Interface intuitiva integrada ao fluxo existente de gerenciamento de fichas
- Processamento flexível com opções para diferentes cenários
- Feedback visual claro sobre o status de cada ficha
- Rastreabilidade completa do processo de upload alternativo até a conversão em ficha regular
- **Tabela de fichas pendentes sempre limpa**, contendo apenas fichas que realmente precisam de atenção

## Próximos Passos e Melhorias Futuras

Algumas melhorias que podem ser consideradas para futuras versões:

1. **Processamento em Lote**: Permitir selecionar múltiplas fichas pendentes e processá-las em lote
2. **Automação**: Implementar processamento automático para fichas que atendem a determinados critérios
3. **Relatórios**: Adicionar relatórios sobre fichas pendentes e taxas de processamento
4. **Notificações**: Alertar usuários sobre novas fichas pendentes que precisam de atenção

Esta implementação permite que os usuários gerenciem eficientemente as fichas enviadas pelo método alternativo, mantendo a consistência com o restante da aplicação e proporcionando uma experiência de usuário intuitiva.
