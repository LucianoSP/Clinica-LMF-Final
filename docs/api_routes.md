# Documentação das Rotas da API

Este documento contém a documentação de todas as rotas da API do sistema ClinicalMF, organizadas por recurso.

## Sumário

1. [Pacientes](#pacientes)
2. [Carteirinhas](#carteirinhas)
3. [Guias](#guias)
4. [Fichas](#fichas)
5. [Procedimentos](#procedimentos)
6. [Sessões](#sessões)
7. [Sessões (Endpoint Principal)](#sessões-endpoint-principal)
8. [Execuções](#execuções)
9. [Divergências](#divergências)
10. [Agendamentos](#agendamentos)
11. [Auditoria](#auditoria)
12. [Auditoria de Execução](#auditoria-de-execução)
13. [Importação](#importação)
14. [Upload](#upload)
15. [Planos de Saúde](#planos-de-saúde)
16. [Storage](#storage)

## Pacientes

Base URL: `/pacientes`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/pacientes` | Listar Pacientes | Retorna uma lista paginada de pacientes | paciente.py | routes |
| POST | `/pacientes` | Criar Paciente | Cria um novo paciente | paciente.py | routes |
| POST | `/pacientes/importar` | Importar Pacientes do MySQL | Importa pacientes de um banco de dados MySQL para o Supabase com controle de datas | paciente.py | routes |
| GET | `/pacientes/ultima-atualizacao` | Obter última atualização | Retorna a data da última atualização na tabela de pacientes | paciente.py | routes |
| GET | `/pacientes/{id}` | Buscar Paciente | Retorna os dados de um paciente específico | paciente.py | routes |
| PUT | `/pacientes/{id}` | Atualizar Paciente | Atualiza os dados de um paciente | paciente.py | routes |
| DELETE | `/pacientes/{id}` | Deletar Paciente | Remove um paciente do sistema | paciente.py | routes |
| GET | `/pacientes/{id}/carteirinhas` | Listar Carteirinhas por Paciente | Retorna uma lista paginada de carteirinhas do paciente | paciente.py | routes |
| GET | `/pacientes/{id}/guias` | Listar Guias por Paciente | Retorna uma lista paginada de guias do paciente | paciente.py | routes |
| GET | `/pacientes/{id}/fichas` | Listar Fichas por Paciente | Retorna uma lista paginada de fichas do paciente | paciente.py | routes |
| GET | `/pacientes/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | paciente.py | routes |

## Carteirinhas

Base URL: `/carteirinhas`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/carteirinhas` | Listar Carteirinhas | Retorna uma lista paginada de carteirinhas | carteirinha.py | routes |
| POST | `/carteirinhas` | Criar Carteirinha | Cria uma nova carteirinha | carteirinha.py | routes |
| GET | `/carteirinhas/{id}` | Buscar Carteirinha | Retorna os dados de uma carteirinha específica | carteirinha.py | routes |
| PUT | `/carteirinhas/{id}` | Atualizar Carteirinha | Atualiza os dados de uma carteirinha | carteirinha.py | routes |
| DELETE | `/carteirinhas/{id}` | Deletar Carteirinha | Remove uma carteirinha do sistema | carteirinha.py | routes |
| GET | `/carteirinhas/by-paciente/{paciente_id}` | Buscar Carteirinhas por Paciente | Retorna todas as carteirinhas de um paciente específico | carteirinha.py | routes |
| POST | `/carteirinhas/rpc/listar_carteirinhas_com_detalhes` | Listar Carteirinhas com Detalhes via RPC | Retorna uma lista paginada de carteirinhas com dados do paciente e plano de saúde via RPC | carteirinha.py | routes |
| POST | `/carteirinhas/migrar-de-pacientes` | Migrar Carteirinhas da Tabela Pacientes | Migra os números de carteirinha da tabela pacientes para a tabela carteirinhas | carteirinha.py | routes |
| GET | `/carteirinhas/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | carteirinha.py | routes |

## Guias

Base URL: `/guias`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/guias` | Listar Guias | Retorna uma lista paginada de guias com opções de filtro | guia.py | routes |
| POST | `/guias` | Criar Guia | Cria uma nova guia | guia.py | routes |
| GET | `/guias/{id}` | Buscar Guia | Retorna uma guia específica pelo ID | guia.py | routes |
| PUT | `/guias/{id}` | Atualizar Guia | Atualiza uma guia existente | guia.py | routes |
| DELETE | `/guias/{id}` | Deletar Guia | Deleta uma guia existente (soft delete) | guia.py | routes |
| POST | `/guias/rpc/listar_guias_com_detalhes` | Listar Guias com Detalhes via RPC | Retorna uma lista paginada de guias com detalhes do paciente e carteirinha via RPC | guia.py | routes |
| GET | `/guias/carteirinha/{carteirinha_id}` | Listar Guias por Carteirinha | Retorna todas as guias de uma carteirinha específica | guia.py | routes |
| PATCH | `/guias/{id}/status` | Atualizar Status da Guia | Atualiza o status de uma guia existente | guia.py | routes |

## Fichas

Base URL: `/fichas`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/fichas` | Listar Fichas | Retorna uma lista paginada de fichas | ficha.py | routes |
| POST | `/fichas` | Criar Ficha | Cria uma nova ficha | ficha.py | routes |
| GET | `/fichas/{id}` | Buscar Ficha | Retorna os dados de uma ficha específica | ficha.py | routes |
| PUT | `/fichas/{id}` | Atualizar Ficha | Atualiza os dados de uma ficha | ficha.py | routes |
| DELETE | `/fichas/{id}` | Deletar Ficha | Remove uma ficha do sistema | ficha.py | routes |
| PATCH | `/fichas/{id}/status` | Atualizar Status da Ficha | Atualiza o status de uma ficha | ficha.py | routes |
| GET | `/fichas/pendentes` | Listar Fichas Pendentes | Lista fichas pendentes com paginação e filtros | ficha.py | routes |
| POST | `/fichas/pendentes/{id}/processar` | Processar Ficha Pendente | Processa uma ficha pendente, criando ou vinculando a uma guia | ficha.py | routes |
| DELETE | `/fichas/pendentes/{id}` | Excluir Ficha Pendente | Exclui uma ficha pendente | ficha.py | routes |
| GET | `/fichas/paciente/{paciente_id}` | Listar Fichas por Paciente | Retorna uma lista paginada de fichas de um paciente específico | ficha.py | routes |
| GET | `/fichas/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | ficha.py | routes |

## Procedimentos

Base URL: `/procedimentos`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/procedimentos` | Listar Procedimentos | Retorna uma lista paginada de procedimentos | procedimento.py | routes |
| POST | `/procedimentos` | Criar Procedimento | Cria um novo procedimento | procedimento.py | routes |
| GET | `/procedimentos/{id}` | Buscar Procedimento | Retorna os dados de um procedimento específico | procedimento.py | routes |
| PUT | `/procedimentos/{id}` | Atualizar Procedimento | Atualiza os dados de um procedimento | procedimento.py | routes |
| DELETE | `/procedimentos/{id}` | Deletar Procedimento | Remove um procedimento do sistema | procedimento.py | routes |
| PATCH | `/procedimentos/{id}/inativar` | Inativar Procedimento | Inativa um procedimento no sistema | procedimento.py | routes |
| GET | `/procedimentos/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | procedimento.py | routes |

## Sessões

Base URL: `/fichas/{ficha_id}/sessoes`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/fichas/{ficha_id}/sessoes` | Listar Sessões por Ficha | Retorna uma lista paginada de sessões de uma ficha específica | ficha.py | routes |
| PUT | `/fichas/{ficha_id}/sessoes/{sessao_id}` | Atualizar Sessão | Atualiza os dados de uma sessão específica | ficha.py | routes |
| POST | `/fichas/{ficha_id}/sessoes` | Criar Múltiplas Sessões | Cria múltiplas sessões para uma ficha específica | ficha.py | routes |
| POST | `/fichas/{ficha_id}/gerar-sessoes` | Gerar Sessões para Ficha | Gera automaticamente sessões para uma ficha com base nas regras de negócio | ficha.py | routes |

## Sessões (Endpoint Principal)

Base URL: `/sessoes`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/sessoes` | Listar Sessões | Retorna uma lista paginada de sessões | sessao.py | routes |
| POST | `/sessoes` | Criar Sessão | Cria uma nova sessão | sessao.py | routes |
| GET | `/sessoes/{id}` | Buscar Sessão | Retorna os dados de uma sessão específica | sessao.py | routes |
| PUT | `/sessoes/{id}` | Atualizar Sessão | Atualiza os dados de uma sessão | sessao.py | routes |
| DELETE | `/sessoes/{id}` | Deletar Sessão | Remove uma sessão do sistema | sessao.py | routes |
| GET | `/sessoes/ficha-presenca/{ficha_presenca_id}` | Listar Sessões por Ficha de Presença | Retorna todas as sessões de uma ficha de presença específica | sessao.py | routes |
| GET | `/sessoes/paciente/{paciente_id}` | Listar Sessões por Paciente | Retorna todas as sessões de um paciente específico | sessao.py | routes |
| GET | `/sessoes/guia/{guia_id}` | Listar Sessões por Guia | Retorna todas as sessões de uma guia específica | sessao.py | routes |
| GET | `/sessoes/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | sessao.py | routes |

## Execuções

Base URL: `/execucoes`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/execucoes` | Listar Execuções | Retorna uma lista paginada de execuções | execucao.py | routes |
| POST | `/execucoes` | Criar Execução | Cria uma nova execução | execucao.py | routes |
| GET | `/execucoes/{id}` | Buscar Execução | Retorna os dados de uma execução específica | execucao.py | routes |
| PUT | `/execucoes/{id}` | Atualizar Execução | Atualiza os dados de uma execução | execucao.py | routes |
| DELETE | `/execucoes/{id}` | Deletar Execução | Remove uma execução do sistema | execucao.py | routes |
| GET | `/execucoes/guia/{guia_id}` | Listar Execuções por Guia | Retorna todas as execuções de uma guia específica | execucao.py | routes |
| PUT | `/execucoes/{id}/biometria` | Verificar Biometria da Execução | Atualiza o status de verificação biométrica de uma execução | execucao.py | routes |
| GET | `/execucoes/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | execucao.py | routes |

## Divergências

Base URL: `/divergencias`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/divergencias` | Listar Divergências | Retorna uma lista paginada de divergências | divergencia.py | routes |
| POST | `/divergencias` | Criar Divergência | Cria uma nova divergência | divergencia.py | routes |
| GET | `/divergencias/{id}` | Buscar Divergência | Retorna os dados de uma divergência específica | divergencia.py | routes |
| PUT | `/divergencias/{id}` | Atualizar Divergência | Atualiza os dados de uma divergência | divergencia.py | routes |
| DELETE | `/divergencias/{id}` | Deletar Divergência | Remove uma divergência do sistema | divergencia.py | routes |
| POST | `/divergencias/{id}/resolver` | Resolver Divergência | Marca uma divergência como resolvida | divergencia.py | routes |
| POST | `/divergencias/{id}/incrementar-tentativas` | Incrementar Tentativas | Incrementa o contador de tentativas de resolução | divergencia.py | routes |
| GET | `/divergencias/guia/{numero_guia}` | Buscar Divergências por Guia | Retorna todas as divergências associadas a um número de guia | divergencia.py | routes |
| GET | `/divergencias/ficha/{codigo_ficha}` | Buscar Divergências por Ficha | Retorna todas as divergências associadas a um código de ficha | divergencia.py | routes |
| GET | `/divergencias/sessao/{sessao_id}` | Buscar Divergências por Sessão | Retorna todas as divergências associadas a uma sessão | divergencia.py | routes |
| POST | `/divergencias/iniciar-auditoria` | Iniciar Auditoria | Inicia o processo de auditoria | divergencia.py | routes |
| PUT | `/divergencias/{divergencia_id}/status` | Atualizar Status da Divergência | Atualiza o status de uma divergência | divergencia.py | routes |
| GET | `/divergencias/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | divergencia.py | routes |

## Agendamentos

Base URL: `/agendamentos`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/agendamentos` | Listar Agendamentos | Retorna uma lista paginada de agendamentos | agendamento.py | routes |
| POST | `/agendamentos` | Criar Agendamento | Cria um novo agendamento | agendamento.py | routes |
| GET | `/agendamentos/{id}` | Buscar Agendamento | Retorna os dados de um agendamento específico | agendamento.py | routes |
| PUT | `/agendamentos/{id}` | Atualizar Agendamento | Atualiza os dados de um agendamento | agendamento.py | routes |
| DELETE | `/agendamentos/{id}` | Deletar Agendamento | Remove um agendamento do sistema | agendamento.py | routes |
| GET | `/agendamentos/verificar-quantidade-agendamentos` | Verificar Quantidade | Verifica a quantidade de agendamentos disponíveis para importação | agendamento.py | routes |
| POST | `/agendamentos/importar-agendamentos-mysql` | Importar Agendamentos | Importa agendamentos do MySQL para o Supabase | agendamento.py | routes |
| POST | `/agendamentos/importar-agendamentos-desde-data` | Importar Agendamentos por Data | Importa agendamentos a partir de uma data específica | agendamento.py | routes |
| GET | `/agendamentos/preencher-mapeamento-pacientes` | Preencher Mapeamento | Popula a tabela de mapeamento de pacientes | agendamento.py | routes |

## Auditoria

Base URL: `/auditoria`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| POST | `/auditoria/iniciar` | Iniciar Auditoria | Inicia uma nova auditoria | auditoria.py | routes |
| POST | `/auditoria/executar` | Executar Auditoria | Executa uma auditoria completa | auditoria.py | routes |
| GET | `/auditoria/divergencias` | Listar Divergências | Lista divergências com paginação e filtros | auditoria.py | routes |
| GET | `/auditoria/divergencias/{divergencia_id}` | Buscar Divergência | Obtém uma divergência pelo ID | auditoria.py | routes |
| PUT | `/auditoria/divergencias/{divergencia_id}` | Atualizar Divergência | Atualiza uma divergência | auditoria.py | routes |
| PUT | `/auditoria/divergencias/{divergencia_id}/status` | Atualizar Status | Atualiza o status de uma divergência | auditoria.py | routes |
| GET | `/auditoria/estatisticas` | Obter Estatísticas | Obtém estatísticas das divergências | auditoria.py | routes |

## Auditoria de Execução

Base URL: `/auditoria-execucao`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/auditoria-execucao/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/ultima` | Buscar Última Auditoria | Retorna os dados da última auditoria de execução realizada | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao` | Listar Auditorias | Retorna uma lista paginada de auditorias de execuções | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/{id}` | Buscar Auditoria | Retorna os dados de uma auditoria de execução específica | auditoria_execucao.py | routes |
| POST | `/auditoria-execucao` | Criar Auditoria | Cria uma nova auditoria de execução | auditoria_execucao.py | routes |
| PUT | `/auditoria-execucao/{id}` | Atualizar Auditoria | Atualiza os dados de uma auditoria de execução | auditoria_execucao.py | routes |
| DELETE | `/auditoria-execucao/{id}` | Deletar Auditoria | Remove uma auditoria de execução do sistema | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/periodo/{data_inicial}/{data_final}` | Buscar por Período | Retorna auditorias em um período específico | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/execucoes` | Listar Execuções | Lista execuções de auditoria com paginação e filtros | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/execucoes/{execucao_id}` | Buscar Execução | Obtém uma execução de auditoria pelo ID | auditoria_execucao.py | routes |
| PUT | `/auditoria-execucao/execucoes/{execucao_id}` | Atualizar Execução | Atualiza uma execução de auditoria | auditoria_execucao.py | routes |
| DELETE | `/auditoria-execucao/execucoes/{execucao_id}` | Deletar Execução | Deleta uma execução de auditoria | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/execucoes/{execucao_id}/divergencias` | Listar Divergências | Lista divergências de uma execução específica | auditoria_execucao.py | routes |
| GET | `/auditoria-execucao/execucoes/{execucao_id}/estatisticas` | Obter Estatísticas | Obtém estatísticas de uma execução específica | auditoria_execucao.py | routes |
| POST | `/auditoria-execucao/iniciar` | Iniciar Auditoria | Inicia uma nova execução de auditoria | auditoria_execucao.py | routes |

## Importação

Base URL: `/importacao`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/importacao/ultima-importacao` | Obter Última Importação | Obtém os dados da última importação registrada | importacao.py | routes |
| GET | `/importacao/limpar-datas-controle` | Limpar Datas de Controle | Limpa datas inválidas nas tabelas de controle de importação | importacao.py | routes |
| GET | `/importacao/preencher-mapeamento-pacientes` | Preencher Mapeamento | Preenche a tabela de mapeamento entre IDs do MySQL e IDs do Supabase | importacao.py | routes |
| GET | `/importacao/corrigir-agendamentos-importados` | Corrigir Agendamentos | Corrige os agendamentos importados, vinculando-os aos pacientes existentes | importacao.py | routes |
| GET | `/importacao/verificar-quantidade-agendamentos` | Verificar Quantidade | Verifica a quantidade de agendamentos disponíveis para importação a partir de uma data | importacao_routes.py | routes |
| GET | `/importacao/importar-agendamentos` | Importar Agendamentos | Importa agendamentos do sistema legado para o sistema atual a partir de uma data específica | importacao_routes.py | routes |

## Upload

Base URL: `/upload`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| POST | `/upload/upload-pdf` | Upload de PDF | Endpoint para upload de PDF e extração de dados | upload.py | routes |
| GET | `/upload/prompts-disponiveis` | Listar Prompts Disponíveis | Lista todos os prompts personalizados disponíveis no sistema | upload.py | routes |

## Planos de Saúde

Base URL: `/planos-saude`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/planos-saude` | Listar Planos de Saúde | Retorna uma lista paginada de planos de saúde | plano_saude.py | routes |
| POST | `/planos-saude` | Criar Plano de Saúde | Cria um novo plano de saúde | plano_saude.py | routes |
| GET | `/planos-saude/{id}` | Buscar Plano de Saúde | Retorna os dados de um plano de saúde específico | plano_saude.py | routes |
| PUT | `/planos-saude/{id}` | Atualizar Plano de Saúde | Atualiza os dados de um plano de saúde | plano_saude.py | routes |
| DELETE | `/planos-saude/{id}` | Deletar Plano de Saúde | Remove um plano de saúde do sistema | plano_saude.py | routes |
| GET | `/planos-saude/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | plano_saude.py | routes |

## Storage

Base URL: `/storage`

| Método | Rota | Summary | Descrição | Arquivo | Caminho |
|--------|------|---------|-----------|---------|---------|
| GET | `/storage` | Listar Arquivos | Retorna uma lista paginada de arquivos armazenados | storage.py | routes |
| POST | `/storage` | Upload de Arquivo | Faz upload de um novo arquivo | storage.py | routes |
| GET | `/storage/{id}` | Buscar Arquivo | Retorna os dados de um arquivo específico | storage.py | routes |
| PUT | `/storage/{id}` | Atualizar Arquivo | Atualiza os dados de um arquivo | storage.py | routes |
| DELETE | `/storage/{id}` | Deletar Arquivo | Remove um arquivo do sistema | storage.py | routes |
| GET | `/storage/reference/{reference_id}/{reference_type}` | Buscar Arquivos por Referência | Retorna todos os arquivos vinculados a uma referência específica | storage.py | routes |
| GET | `/storage/download/all` | Download de Todos os Arquivos | Baixa todos os arquivos em um arquivo ZIP | storage.py | routes |
| POST | `/storage/sync` | Sincronizar com R2 | Sincroniza a tabela storage com os arquivos do Cloudflare R2 | storage.py | routes |
| GET | `/storage/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | storage.py | routes |
