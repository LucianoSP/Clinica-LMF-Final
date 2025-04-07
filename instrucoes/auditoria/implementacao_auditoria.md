# Plano de Implementação do Sistema de Auditoria de Divergências

Este documento contém as recomendações e o plano de acompanhamento passo a passo para a implementação completa do sistema de auditoria de divergências no ClinicalMF.

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Preparação](#2-preparação)
3. [Desenvolvimento do Backend](#3-desenvolvimento-do-backend)
4. [Desenvolvimento do Frontend](#4-desenvolvimento-do-frontend)
5. [Testes e Validação](#5-testes-e-validação)
6. [Implantação](#6-implantação)
7. [Documentação e Treinamento](#7-documentação-e-treinamento)
8. [Melhorias Futuras](#8-melhorias-futuras)

## 1. Visão Geral

O sistema de auditoria de divergências visa identificar e gerenciar discrepâncias entre fichas físicas de atendimento e execuções registradas no sistema. Este plano detalha os passos necessários para implementar completamente esta funcionalidade.

### 1.1 Objetivo

- [ ] Implementar um sistema robusto de auditoria de divergências
- [ ] Garantir a integridade dos dados entre execuções e fichas
- [ ] Fornecer ferramentas para identificação e resolução de problemas
- [ ] Melhorar a qualidade dos dados para faturamento

### 1.2 Componentes Principais

- [ ] Módulo de verificação de divergências (Backend)
- [ ] API para gerenciamento de divergências (Backend)
- [ ] Dashboard de auditoria (Frontend)
- [ ] Interface de listagem e resolução de divergências (Frontend)
- [ ] Sistema de relatórios e estatísticas (Frontend/Backend)

## 2. Preparação

### 2.1 Análise de Requisitos

- [ ] Revisar e confirmar os tipos de divergências a serem detectados
- [ ] Definir prioridades para cada tipo de divergência
- [ ] Estabelecer fluxos de trabalho para resolução de divergências
- [ ] Identificar integrações necessárias com outros módulos

### 2.2 Preparação do Ambiente

- [ ] Configurar ambiente de desenvolvimento para testes isolados
- [ ] Criar branch específica para o desenvolvimento da funcionalidade
- [x] Padronizar a nomenclatura dos campos (tipo vs tipo_divergencia)
- [x] Padronizar a estrutura da resposta da API (usar "items" consistentemente)
- [x] Adicionar logs detalhados para facilitar depuração
- [ ] Executar o script `backend/scripts/gerar_dados_teste.py` para gerar dados de teste
- [ ] Verificar a estrutura do banco de dados (Supabase) e ajustar se necessário

### 2.3 Estrutura do Banco de Dados

- [ ] Revisar a estrutura da tabela `divergencias`
- [ ] Revisar a estrutura da tabela `auditoria_execucoes`
- [ ] Criar índices para otimizar consultas de auditoria
- [ ] Implementar triggers ou regras para manter integridade referencial

## 3. Desenvolvimento do Backend

### 3.1 Implementação das Funções de Verificação

- [ ] Revisar e otimizar a função `verificar_datas()`
  - [ ] Padronizar o formato de data em todo o sistema
  - [ ] Adicionar tratamento de exceção para formatos de data inválidos

- [ ] Revisar e otimizar a função `verificar_assinatura_ficha()`
  - [ ] Padronizar a terminologia (ficha_sem_assinatura vs sessao_sem_assinatura)
  - [ ] Melhorar a validação da assinatura

- [ ] Revisar e otimizar a função `verificar_duplicidade_execucoes()`
  - [ ] Adicionar critérios adicionais de verificação de duplicidade
  - [ ] Otimizar o algoritmo para melhor performance

- [ ] Revisar e otimizar a função `verificar_quantidade_execucaos()`
  - [ ] Corrigir o nome da função para `verificar_quantidade_execucoes()`
  - [ ] Melhorar a estrutura condicional

- [ ] Revisar e otimizar a função `verificar_validade_guia()`
  - [ ] Adicionar validação de formato de data
  - [ ] Implementar cache para guias já verificadas

### 3.2 Implementação da Auditoria Principal

- [ ] Otimizar a função `realizar_auditoria_fichas_execucoes()`
  - [ ] Implementar processamento em lotes para grandes volumes de dados
  - [ ] Adicionar log detalhado de operações
  - [ ] Implementar mecanismo de retentativas para operações falhas

- [ ] Melhorar a função `limpar_divergencias_db()`
  - [ ] Adicionar opção para preservar divergências históricas
  - [ ] Implementar soft delete em vez de exclusão permanente

### 3.3 Implementação do Repositório

- [ ] Otimizar a função `registrar_divergencia_detalhada()`
  - [ ] Adicionar validação de campos obrigatórios
  - [ ] Implementar transações para garantir atomicidade

- [ ] Melhorar a função `atualizar_status_divergencia()`
  - [ ] Adicionar validação de transições de status válidas
  - [ ] Registrar histórico completo de alterações de status

- [ ] Otimizar a função `buscar_divergencias_view()`
  - [ ] Implementar cache para consultas frequentes
  - [ ] Otimizar consultas SQL para melhor performance

- [ ] Expandir a função `calcular_estatisticas_divergencias()`
  - [ ] Adicionar estatísticas por período
  - [ ] Incluir tendências e comparativos

### 3.4 Endpoints da API

- [ ] Implementar endpoint `GET /divergencias`
  - [ ] Adicionar filtros avançados
  - [ ] Melhorar a paginação

- [ ] Implementar endpoint `POST /auditoria/executar`
  - [ ] Adicionar opção para auditoria parcial/incremental
  - [ ] Implementar execução assíncrona para grandes volumes

- [ ] Implementar endpoint `PUT /divergencias/{id}/status`
  - [ ] Adicionar validação de permissões
  - [ ] Implementar histórico de alterações

- [ ] Implementar endpoint `GET /auditoria/estatisticas`
  - [ ] Expandir para incluir mais métricas
  - [ ] Adicionar filtros por período

- [ ] Implementar endpoint `GET /auditoria/ultima`
  - [ ] Melhorar detalhamento dos resultados
  - [ ] Adicionar métricas de performance

- [x] Padronizar prefixos das rotas 
  - [x] Usar "/api/divergencias" como padrão no backend
  - [x] Garantir consistência entre routers

- [ ] Novos endpoints adicionais
  - [ ] `POST /divergencias/resolucao-em-lote` para resolução em massa
  - [ ] `GET /divergencias/export` para exportação em CSV/Excel
  - [ ] `GET /auditoria/historico` para histórico de auditorias

## 4. Desenvolvimento do Frontend

### 4.1 Dashboard de Auditoria

- [ ] Implementar componente `DashboardAuditoria`
  - [ ] Criar cards resumo para estatísticas principais
  - [ ] Implementar gráficos de distribuição de divergências
  - [ ] Adicionar filtro por período

- [ ] Implementar componente `CardsDivergencia`
  - [ ] Criar cards para cada tipo de divergência
  - [ ] Adicionar indicadores visuais de prioridade
  - [ ] Implementar links diretos para filtros específicos

- [ ] Implementar componente `GraficoDivergencias`
  - [ ] Criar gráfico de barras por tipo de divergência
  - [ ] Criar gráfico de pizza por status
  - [ ] Implementar gráfico de linha para tendências temporais

### 4.2 Lista de Divergências

- [ ] Implementar componente `ListaDivergencias`
  - [ ] Criar tabela paginada de divergências
  - [ ] Implementar ordenação por múltiplos critérios
  - [ ] Adicionar destaques visuais por prioridade

- [ ] Implementar componente `FiltrosDivergencia`
  - [ ] Criar formulário com filtros avançados
  - [ ] Implementar busca por texto (paciente, guia, etc.)
  - [ ] Adicionar salvamento de filtros favoritos

- [ ] Implementar componente `TabelaDivergencias`
  - [ ] Criar células com formatação condicional
  - [ ] Implementar ações rápidas em linha
  - [ ] Adicionar expansão de detalhes

### 4.3 Detalhes e Resolução

- [ ] Implementar componente `DetalhesDivergencia`
  - [ ] Criar visualização detalhada de divergência
  - [ ] Implementar visualização de documentos relacionados
  - [ ] Adicionar histórico de alterações

- [x] Corrigir problemas de tipos no componente `DetalheDivergencia`
  - [x] Adicionar valor padrão para o tipo no DivergenciaBadge
  - [x] Garantir compatibilidade entre tipo e tipo_divergencia

- [ ] Implementar componente `FormularioResolucao`
  - [ ] Criar formulário para atualização de status
  - [ ] Implementar upload de documentos de suporte
  - [ ] Adicionar campo de observações

- [ ] Implementar componente `HistoricoResolucao`
  - [ ] Criar linha do tempo de alterações
  - [ ] Mostrar detalhes de cada alteração
  - [ ] Incluir informações do usuário responsável

### 4.4 Relatórios

- [ ] Implementar componente `RelatorioAuditoria`
  - [ ] Criar visualização resumida dos resultados
  - [ ] Implementar gráficos comparativos
  - [ ] Adicionar exportação em vários formatos

- [ ] Implementar componente `FiltrosPeriodo`
  - [ ] Criar seletor de intervalo de datas
  - [ ] Implementar presets comuns (último mês, trimestre, etc.)
  - [ ] Adicionar comparação entre períodos

- [ ] Implementar componente `IndicadoresDesempenho`
  - [ ] Criar visualização de KPIs
  - [ ] Implementar comparação com metas
  - [ ] Adicionar tendências e projeções

## 5. Testes e Validação

### 5.1 Testes Unitários

- [ ] Implementar testes para `verificar_datas()`
  - [ ] Teste com datas iguais
  - [ ] Teste com datas diferentes
  - [ ] Teste com datas inválidas
  - [ ] Teste com datas nulas

- [ ] Implementar testes para `verificar_assinatura_ficha()`
  - [ ] Teste com ficha assinada
  - [ ] Teste com ficha não assinada
  - [ ] Teste com ficha sem arquivo
  - [ ] Teste com ficha sem informação de assinatura

- [ ] Implementar testes para `verificar_duplicidade_execucoes()`
  - [ ] Teste sem duplicidade
  - [ ] Teste com uma duplicidade
  - [ ] Teste com várias duplicidades

- [ ] Implementar testes para `verificar_quantidade_execucaos()`
  - [ ] Teste com quantidade correta
  - [ ] Teste com quantidade menor
  - [ ] Teste com quantidade maior
  - [ ] Teste com quantidade nula

- [ ] Implementar testes para `verificar_validade_guia()`
  - [ ] Teste com guia válida
  - [ ] Teste com guia vencida
  - [ ] Teste com guia sem data de validade

### 5.2 Testes de Integração

- [ ] Implementar testes para `registrar_divergencia_detalhada()`
  - [ ] Teste com dados válidos
  - [ ] Teste com dados inválidos
  - [ ] Teste com campos opcionais nulos

- [ ] Implementar testes para `atualizar_status_divergencia()`
  - [ ] Teste de alteração para "em_analise"
  - [ ] Teste de alteração para "resolvida"
  - [ ] Teste com status inválido

- [ ] Implementar testes para `buscar_divergencias_view()`
  - [ ] Teste sem filtros
  - [ ] Teste com filtros específicos
  - [ ] Teste de paginação

- [ ] Implementar testes para `calcular_estatisticas_divergencias()`
  - [ ] Teste com diversos tipos de divergências
  - [ ] Teste com diferentes status
  - [ ] Teste com diferentes prioridades

### 5.3 Testes de Sistema

- [ ] Implementar teste para execução completa da auditoria
  - [ ] Teste com dados normais (sem divergências)
  - [ ] Teste com dados contendo divergências variadas
  - [ ] Teste de performance com grande volume de dados

- [ ] Implementar teste para detecção de divergências específicas
  - [ ] Teste para data divergente
  - [ ] Teste para sessão sem assinatura
  - [ ] Teste para execução sem ficha
  - [ ] Teste para ficha sem execução
  - [ ] Teste para guia vencida
  - [ ] Teste para quantidade excedida
  - [ ] Teste para duplicidade

### 5.4 Testes de Interface

- [ ] Testar Dashboard de Auditoria
  - [ ] Verificar exibição correta de estatísticas
  - [ ] Testar interatividade dos gráficos
  - [ ] Validar responsividade em diferentes resoluções

- [ ] Testar Lista de Divergências
  - [ ] Verificar filtros e ordenação
  - [ ] Testar paginação
  - [ ] Validar ações em linha

- [ ] Testar Detalhes e Resolução
  - [ ] Verificar exibição completa de informações
  - [ ] Testar formulário de resolução
  - [ ] Validar histórico de alterações

- [ ] Testar Relatórios
  - [ ] Verificar geração correta de relatórios
  - [ ] Testar exportação em diferentes formatos
  - [ ] Validar filtros e opções de configuração

## 6. Implantação

### 6.1 Preparação

- [ ] Realizar revisão de código final
  - [ ] Verificar padrões de codificação
  - [ ] Eliminar código comentado ou não utilizado
  - [ ] Garantir tratamento adequado de erros

- [ ] Preparar script de migração de banco de dados
  - [ ] Criar índices necessários
  - [ ] Adicionar constraints de integridade
  - [ ] Verificar compatibilidade com dados existentes

- [ ] Criar documentação de implantação
  - [ ] Listar dependências e pré-requisitos
  - [ ] Detalhar passos para implantação
  - [ ] Incluir procedimentos de rollback

### 6.2 Implantação em Staging

- [ ] Implantar backend em ambiente de staging
  - [ ] Verificar configuração de variáveis de ambiente
  - [ ] Validar conexão com banco de dados
  - [ ] Testar endpoints da API

- [ ] Implantar frontend em ambiente de staging
  - [ ] Verificar configuração de URLs da API
  - [ ] Validar assets e recursos estáticos
  - [ ] Testar funcionalidades em diferentes navegadores

- [ ] Executar testes de aceitação em staging
  - [ ] Verificar funcionalidades end-to-end
  - [ ] Validar performance e tempos de resposta
  - [ ] Testar em diferentes dispositivos e resoluções

### 6.3 Implantação em Produção

- [ ] Criar plano de implantação em produção
  - [ ] Definir janela de manutenção (se necessário)
  - [ ] Preparar comunicado para usuários
  - [ ] Estabelecer pontos de verificação

- [ ] Executar implantação em produção
  - [ ] Realizar backup completo antes da implantação
  - [ ] Seguir procedimento documentado
  - [ ] Verificar todos os pontos de checagem

- [ ] Realizar validação pós-implantação
  - [ ] Executar testes de sanidade
  - [ ] Verificar logs em busca de erros
  - [ ] Monitorar métricas de performance

## 7. Documentação e Treinamento

### 7.1 Documentação Técnica

- [ ] Atualizar documentação da API
  - [ ] Documentar novos endpoints
  - [ ] Incluir exemplos de requisição e resposta
  - [ ] Detalhar códigos de erro

- [ ] Criar documentação de arquitetura
  - [ ] Detalhar fluxo de dados
  - [ ] Explicar interações entre componentes
  - [ ] Incluir diagramas explicativos

- [ ] Documentar estrutura do banco de dados
  - [ ] Detalhar schema das tabelas
  - [ ] Explicar relacionamentos
  - [ ] Documentar índices e otimizações

### 7.2 Documentação para Usuários

- [ ] Criar manual do usuário
  - [ ] Explicar conceito de divergências
  - [ ] Detalhar fluxo de resolução
  - [ ] Incluir capturas de tela explicativas

- [ ] Preparar guias rápidos
  - [ ] Guia para execução de auditoria
  - [ ] Guia para resolução de divergências
  - [ ] Guia para interpretação de relatórios

- [ ] Desenvolver FAQ
  - [ ] Listar perguntas comuns
  - [ ] Fornecer respostas claras
  - [ ] Incluir exemplos práticos

### 7.3 Treinamento

- [ ] Preparar material de treinamento
  - [ ] Criar apresentações
  - [ ] Desenvolver exercícios práticos
  - [ ] Preparar cenários de exemplo

- [ ] Realizar sessões de treinamento
  - [ ] Treinar administradores do sistema
  - [ ] Treinar usuários finais
  - [ ] Realizar sessões de dúvidas

- [ ] Implementar suporte pós-treinamento
  - [ ] Designar pessoa(s) para suporte
  - [ ] Estabelecer canal para dúvidas
  - [ ] Planejar sessões de reforço

## 8. Melhorias Futuras

### 8.1 Otimizações Técnicas

- [ ] Implementar cache para consultas frequentes
  - [ ] Cache de estatísticas
  - [ ] Cache de resultados de auditoria recentes
  - [ ] Cache de configurações

- [ ] Melhorar performance de auditoria
  - [ ] Implementar processamento paralelo
  - [ ] Otimizar consultas SQL
  - [ ] Implementar indexação avançada

- [ ] Desenvolver API GraphQL
  - [ ] Criar schema GraphQL
  - [ ] Implementar resolvers
  - [ ] Oferecer queries e mutations flexíveis

### 8.2 Novas Funcionalidades

- [ ] Implementar auditoria automática agendada
  - [ ] Configurar periodicidade
  - [ ] Implementar notificações de resultados
  - [ ] Criar histórico de execuções

- [ ] Desenvolver sistema de alertas
  - [ ] Configurar limites e gatilhos
  - [ ] Implementar notificações por email/sistema
  - [ ] Criar dashboard de alertas

- [ ] Implementar inteligência artificial
  - [ ] Desenvolver algoritmo de detecção de padrões
  - [ ] Implementar sugestões automáticas de resolução
  - [ ] Criar previsão de tendências

### 8.3 Integração com Outros Sistemas

- [ ] Integrar com sistema de faturamento
  - [ ] Criar validação pré-faturamento
  - [ ] Implementar bloqueio de faturamento com divergências críticas
  - [ ] Desenvolver relatórios específicos para faturamento

- [ ] Integrar com sistema de gestão documental
  - [ ] Vincular documentos relevantes a divergências
  - [ ] Implementar digitalização/OCR de documentos físicos
  - [ ] Criar validação automática de documentos

- [ ] Integrar com sistema de BI
  - [ ] Exportar dados para ferramentas de BI
  - [ ] Criar modelos de análise avançada
  - [ ] Desenvolver dashboards executivos 