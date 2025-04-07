# Documentação de Chamadas à API no Frontend

Este documento mapeia todas as chamadas à API realizadas no frontend, mostrando em quais componentes, páginas, hooks ou serviços cada endpoint é utilizado.

## Índice

1. [Pacientes](#pacientes)
2. [Guias](#guias)
3. [Fichas](#fichas)
4. [Agendamentos](#agendamentos)
5. [Carteirinhas](#carteirinhas)
6. [Procedimentos](#procedimentos)
7. [Planos de Saúde](#planos-de-saude)
8. [Execuções](#execucoes)
9. [Sessões](#sessoes)
10. [Importação](#importacao)
11. [Storage](#storage)
12. [Divergências](#divergencias)

## Pacientes

### Listar Pacientes
- **Endpoint:** `GET /api/pacientes`
- **Serviço:** `pacienteService.listar()`
- **Usado em:**
  - `src/app/(auth)/cadastros/pacientes/page.tsx` - Página de listagem de pacientes
  - `src/components/carteirinhas/CarteirinhaForm.tsx` - Formulário de carteirinhas para selecionar pacientes
  - `src/hooks/usePacientes.ts` - Hook para gerenciar pacientes

### Obter Paciente
- **Endpoint:** `GET /api/pacientes/{id}`
- **Serviço:** `pacienteService.obter()`
- **Usado em:**
  - `src/components/guias/GuiaForm.tsx` - Para carregar dados do paciente ao criar/editar guias
  - `src/components/fichas/FichaForm.tsx` - Para carregar dados do paciente ao criar/editar fichas
  - `src/hooks/usePacientes.ts` - Hook para gerenciar pacientes

### Criar Paciente
- **Endpoint:** `POST /api/pacientes`
- **Serviço:** `pacienteService.criar()`
- **Usado em:**
  - `src/components/pacientes/PacienteModal.tsx` - Modal para criação de pacientes
  - `src/hooks/usePacientes.ts` - Hook para gerenciar pacientes

### Atualizar Paciente
- **Endpoint:** `PUT /api/pacientes/{id}`
- **Serviço:** `pacienteService.atualizar()`
- **Usado em:**
  - `src/components/pacientes/PacienteModal.tsx` - Modal para edição de pacientes
  - `src/hooks/usePacientes.ts` - Hook para gerenciar pacientes

### Excluir Paciente
- **Endpoint:** `DELETE /api/pacientes/{id}`
- **Serviço:** `pacienteService.excluir()`
- **Usado em:**
  - `src/app/(auth)/cadastros/pacientes/page.tsx` - Página de listagem de pacientes (ação de exclusão)
  - `src/hooks/usePacientes.ts` - Hook para gerenciar pacientes

### Buscar Pacientes por Termo
- **Endpoint:** `GET /api/pacientes/buscar`
- **Serviço:** `pacienteService.buscarPorTermo()`
- **Usado em:**
  - `src/app/(auth)/fichas-presenca/page.tsx` - Busca de pacientes para fichas de presença
  - `src/components/guias/GuiaForm.tsx` - Busca de pacientes no formulário de guias
  - `src/components/fichas/FichaForm.tsx` - Busca de pacientes no formulário de fichas

### Buscar Pacientes para Combobox
- **Endpoint:** `GET /api/pacientes/combobox`
- **Serviço:** `pacienteService.buscarParaCombobox()`
- **Usado em:**
  - `src/components/fichas/FichaForm.tsx` - Combobox de seleção de pacientes

### Importar Pacientes
- **Endpoint:** `POST /api/pacientes/importar`
- **Serviço:** `pacienteService.importarPacientes()`
- **Usado em:**
  - `src/app/(auth)/cadastros/pacientes/page.tsx` - Funcionalidade de importação de pacientes

### Obter Carteirinhas do Paciente
- **Endpoint:** `GET /api/pacientes/{id}/carteirinhas`
- **Serviço:** `pacienteService.obterCarteirinhas()`
- **Usado em:**
  - Não identificado uso direto nos componentes analisados

### Obter Guias do Paciente
- **Endpoint:** `GET /api/pacientes/{id}/guias`
- **Serviço:** `pacienteService.obterGuias()`
- **Usado em:**
  - Não identificado uso direto nos componentes analisados

### Obter Fichas do Paciente
- **Endpoint:** `GET /api/pacientes/{id}/fichas`
- **Serviço:** `pacienteService.obterFichas()`
- **Usado em:**
  - Não identificado uso direto nos componentes analisados

## Guias

### Listar Guias
- **Endpoint:** `GET /api/guias`
- **Serviço:** `guiaService.listar()`
- **Usado em:**
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

### Obter Guia
- **Endpoint:** `GET /api/guias/{id}`
- **Serviço:** `guiaService.obter()`
- **Usado em:**
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

### Criar Guia
- **Endpoint:** `POST /api/guias`
- **Serviço:** `guiaService.criar()`
- **Usado em:**
  - `src/components/storage/GuiaModal.tsx` - Modal para criação de guias
  - `src/components/guias/GuiaForm.tsx` - Formulário de guias
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

### Atualizar Guia
- **Endpoint:** `PUT /api/guias/{id}`
- **Serviço:** `guiaService.atualizar()`
- **Usado em:**
  - `src/components/storage/GuiaModal.tsx` - Modal para edição de guias
  - `src/components/guias/GuiaForm.tsx` - Formulário de guias
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

### Excluir Guia
- **Endpoint:** `DELETE /api/guias/{id}`
- **Serviço:** `guiaService.excluir()`
- **Usado em:**
  - `src/components/guias/guia-row-actions.tsx` - Ações de linha na tabela de guias
  - `src/app/(auth)/cadastros/guias/page.tsx` - Página de listagem de guias (ação de exclusão)
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

### Listar Guias por Carteirinha
- **Endpoint:** `GET /api/guias/carteirinha/{carteirinha_id}`
- **Serviço:** `guiaService.listarPorCarteirinha()`
- **Usado em:**
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage
  - `src/hooks/useGuiasDaCarteirinha.ts` - Hook específico para guias de uma carteirinha

### Listar Guias por Paciente
- **Endpoint:** `GET /api/guias/paciente/{paciente_id}`
- **Serviço:** `guiaService.listarPorPaciente()`
- **Usado em:**
  - `src/components/fichas/FichaForm.tsx` - Formulário de fichas
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

### Listar Guias por Procedimento
- **Endpoint:** `GET /api/guias/procedimento/{procedimento_id}`
- **Serviço:** `guiaService.listarPorProcedimento()`
- **Usado em:**
  - `src/hooks/useGuias.ts` - Hook para gerenciar guias
  - `src/hooks/useStorage.ts` - Hook para gerenciar storage

## Fichas

### Listar Fichas
- **Endpoint:** `GET /api/fichas`
- **Serviço:** `apiFichas.listar()`
- **Usado em:**
  - `src/services/api.ts` - Definição do serviço

### Conferir Sessão
- **Endpoint:** `POST /api/fichas/{fichaId}/sessoes/{sessaoId}/conferir`
- **Serviço:** `apiFichas.conferirSessao()`
- **Usado em:**
  - `src/services/api.ts` - Definição do serviço

### Atualizar Sessão
- **Endpoint:** `PUT /api/fichas/{fichaId}/sessoes/{sessaoId}`
- **Serviço:** `apiFichas.atualizarSessao()`
- **Usado em:**
  - `src/services/api.ts` - Definição do serviço

### Excluir Sessão
- **Endpoint:** `DELETE /api/fichas/{fichaId}/sessoes/{sessaoId}`
- **Serviço:** `apiFichas.excluirSessao()`
- **Usado em:**
  - `src/services/api.ts` - Definição do serviço

### Excluir Ficha
- **Endpoint:** `DELETE /api/fichas/{fichaId}`
- **Serviço:** `apiFichas.excluir()`
- **Usado em:**
  - `src/services/api.ts` - Definição do serviço

## Agendamentos

### Listar Agendamentos
- **Endpoint:** `GET /api/agendamentos`
- **Serviço:** `agendamentoService.listar()`
- **Usado em:**
  - `src/hooks/useAgendamentos.ts` - Hook para gerenciar agendamentos

### Obter Agendamento
- **Endpoint:** `GET /api/agendamentos/{id}`
- **Serviço:** `agendamentoService.obter()`
- **Usado em:**
  - `src/hooks/useAgendamentos.ts` - Hook para gerenciar agendamentos

### Excluir Agendamento
- **Endpoint:** `DELETE /api/agendamentos/{id}`
- **Serviço:** `agendamentoService.excluir()`
- **Usado em:**
  - `src/app/agendamentos/page.tsx` - Página de agendamentos
  - `src/app/(auth)/agendamento/page.tsx` - Página de agendamento autenticada

### Verificar Quantidade de Agendamentos
- **Endpoint:** `GET /api/agendamentos/verificar-quantidade`
- **Serviço:** `agendamentoService.verificarQuantidadeAgendamentos()`
- **Usado em:**
  - `src/app/(auth)/agendamento/page.tsx` - Página de agendamento autenticada

### Importar Agendamentos Desde Data
- **Endpoint:** `POST /api/agendamentos/importar-desde-data`
- **Serviço:** `agendamentoService.importarAgendamentosDesdeData()`
- **Usado em:**
  - `src/app/(auth)/agendamento/page.tsx` - Página de agendamento autenticada

## Importação

### Preencher Mapeamento de Pacientes
- **Endpoint:** `GET /api/importacao/preencher-mapeamento-pacientes`
- **Serviço:** Não identificado uso direto nos componentes analisados

## Upload

### Upload de PDF
- **Endpoint:** `POST /api/upload/upload-pdf`
- **Serviço:** Não identificado uso direto nos componentes analisados

## Observações

Este documento mapeia as chamadas à API do frontend para o backend, mostrando onde cada endpoint é utilizado. Algumas chamadas podem estar sendo utilizadas em componentes ou hooks que não foram identificados na análise atual.

Para uma visão completa das rotas disponíveis no backend, consulte o arquivo `api_routes.md`.
