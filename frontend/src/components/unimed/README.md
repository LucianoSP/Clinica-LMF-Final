# Componentes de Monitoramento da Unimed

Este diretório contém os componentes utilizados na página de monitoramento da Unimed, responsáveis por exibir o status do processamento de guias, estatísticas e gerenciamento das sessões capturadas.

## Melhorias Implementadas

### Adaptação para Tabela Intermediária

O sistema foi adaptado para trabalhar com a tabela intermediária `unimed_sessoes_capturadas`, permitindo um melhor controle do processamento e recuperação de erros.

### Dashboard

- **Status Cards**: Exibição visual do status atual das sessões (processadas, pendentes, com erro)
- **Indicador de Processamento Ativo**: Animação indicando quando existe uma captura em andamento
- **Gráficos Aprimorados**:
  - Gráfico de linha mostrando a atividade nas últimas 24h
  - Gráfico de barras mostrando o desempenho por dia
  - Gráfico de pizza com a distribuição de status das sessões
- **Histórico de Execuções**: Tabela com dados detalhados das últimas tarefas executadas
- **Atualização Automática**: Contador de atualização e inscrição em eventos do banco de dados

### Gestão de Sessões

- **Filtros por Status**: Botões para filtrar sessões por status (processado, pendente, erro)
- **Reprocessamento em Lote**: Possibilidade de reprocessar todas as sessões com erro de uma vez
- **Detalhes da Sessão**: Modal com logs detalhados de processamento de cada sessão
- **Mensagens de Erro**: Visualização clara dos erros ocorridos durante o processamento
- **Paginação Avançada**: Sistema de paginação para navegar entre grandes conjuntos de sessões
- **Busca Aprimorada**: Campo de busca com feedback visual e limpar filtros

### Nova Captura

- **Seleção de Datas**: Interface aprimorada para seleção das datas inicial e final
- **Limite de Guias**: Controle deslizante para definir o número máximo de guias a serem processadas
- **Validações**: Verificações antes de iniciar uma nova captura
- **Resumo da Captura**: Painel informativo com detalhes da captura a ser iniciada
- **Histórico de Execuções**: Tabela com histórico das últimas execuções realizadas

### Visualização de Logs

- **LogViewer Aprimorado**: Componente para visualização de logs com cores distintas por tipo
- **Exportação de Logs**: Funcionalidades para copiar e baixar logs
- **Visualização Detalhada**: Tabela com informações detalhadas de cada log
- **Estatísticas de Logs**: Resumo visual com contagem de logs por tipo

## Componentes Principais

- **Dashboard.tsx**: Modernizado com tabs para melhor organização, gráficos interativos, e visualização em tempo real. Melhorado o layout geral para garantir espaçamento adequado entre componentes e melhor visualização em diferentes tamanhos de tela.
- **StatusCard.tsx**: Redesenhado para exibir informações de status de forma mais clara e visualmente atraente, com indicadores de cores e ícones.
- **SessoesTable.tsx**: Implementado com recursos avançados de filtragem e paginação, melhorando a usabilidade.
- **SessaoDetalhes.tsx**: Aprimorado para exibir logs e detalhes de sessão de forma organizada e fácil de ler.
- **ExecutionStats.tsx**: Adicionado para mostrar estatísticas de execução em tempo real.
- **RealTimeMonitor.tsx**: Criado para exibir informações em tempo real sobre o processamento atual, com indicadores visuais de progresso.
- **LogViewer.tsx**: Implementado para exibir logs em tempo real com formatação adequada por tipo de log, com recursos de rolagem automática, cópia e download de logs.

## Integração com Backend

O sistema se comunica com o backend através de APIs para:
- Iniciar novas capturas
- Reprocessar sessões com erro
- Obter dados atualizados do banco de dados

Além disso, utiliza os canais de realtime do Supabase para receber atualizações em tempo real das tabelas:
- `processing_status`
- `unimed_sessoes_capturadas`
- `unimed_log_processamento`

## Melhorias Visuais

- **Design Responsivo**: Adaptação para diferentes tamanhos de tela
- **Animações Suaves**: Transições e animações para melhorar a experiência do usuário
- **Feedback Visual**: Indicadores claros de status e progresso
- **Tooltips Informativos**: Dicas contextuais para ajudar na navegação
- **Cores Semânticas**: Uso consistente de cores para indicar diferentes estados
- **Sombras e Efeitos**: Elementos visuais para destacar componentes importantes
- **Implementação de cards com sombras suaves e efeitos hover para melhor feedback visual**
- **Uso de badges coloridos para indicar status (sucesso, erro, pendente)**
- **Gráficos interativos para visualização de dados (linha, pizza)**
- **Tabelas responsivas com cabeçalhos fixos para melhor navegação**
- **Espaçamento adequado entre componentes para melhor legibilidade**
- **Layout responsivo que se adapta a diferentes tamanhos de tela**
- **Indicadores visuais de progresso para tarefas em andamento**

## Melhorias de Usabilidade

- **Interface de captura de guias mais intuitiva com seleção de datas e limite de guias**
- **Filtros rápidos para visualização de sessões por status**
- **Detalhamento de logs com opções de cópia e download**
- **Monitoramento em tempo real de tarefas em execução**
- **Resumo visual do status atual do sistema**
- **Melhor organização de conteúdo usando tabs**
- **Feedback visual para ações do usuário**

### Integração com Backend

- **Implementação de chamadas API para buscar dados em tempo real**
- **Atualização automática de status de processamento**
- **Funcionalidade de reprocessamento de sessões com erro**
- **Exibição de logs detalhados para diagnóstico de problemas**

Todas as melhorias foram implementadas utilizando componentes shadcn onde possível, garantindo consistência visual e aderência às melhores práticas de design. 