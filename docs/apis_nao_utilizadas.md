# APIs do Backend Não Utilizadas no Frontend

Este documento lista todas as rotas da API disponíveis no backend que não foram identificadas como sendo chamadas diretamente pelo frontend. Essas APIs podem representar funcionalidades não implementadas na interface ou endpoints que são utilizados apenas por outros sistemas ou scripts.

## Índice

1. [Pacientes](#pacientes)
2. [Carteirinhas](#carteirinhas)
3. [Guias](#guias)
4. [Fichas](#fichas)
5. [Procedimentos](#procedimentos)
6. [Sessões](#sessoes)
7. [Execuções](#execucoes)
8. [Divergências](#divergencias)
9. [Agendamentos](#agendamentos)
10. [Auditoria](#auditoria)
11. [Auditoria de Execução](#auditoria-de-execucao)
12. [Importação](#importacao)
13. [Upload](#upload)
14. [Planos de Saúde](#planos-de-saude)
15. [Storage](#storage)

## Pacientes

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/pacientes/ultima-atualizacao` | Obter última atualização | Retorna a data da última atualização na tabela de pacientes | paciente.py |
| GET | `/pacientes/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | paciente.py |

## Carteirinhas

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/carteirinhas/by-paciente/{paciente_id}` | Buscar Carteirinhas por Paciente | Retorna todas as carteirinhas de um paciente específico | carteirinha.py |
| POST | `/carteirinhas/rpc/listar_carteirinhas_com_detalhes` | Listar Carteirinhas com Detalhes via RPC | Retorna uma lista paginada de carteirinhas com dados do paciente e plano de saúde via RPC | carteirinha.py |
| POST | `/carteirinhas/migrar-de-pacientes` | Migrar Carteirinhas da Tabela Pacientes | Migra os números de carteirinha da tabela pacientes para a tabela carteirinhas | carteirinha.py |
| GET | `/carteirinhas/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | carteirinha.py |

## Guias

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| POST | `/guias/rpc/listar_guias_com_detalhes` | Listar Guias com Detalhes via RPC | Retorna uma lista paginada de guias com detalhes do paciente e carteirinha via RPC | guia.py |
| PATCH | `/guias/{id}/status` | Atualizar Status da Guia | Atualiza o status de uma guia existente | guia.py |

## Fichas

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| POST | `/fichas` | Criar Ficha | Cria uma nova ficha | ficha.py |
| GET | `/fichas/{id}` | Buscar Ficha | Retorna os dados de uma ficha específica | ficha.py |
| PUT | `/fichas/{id}` | Atualizar Ficha | Atualiza os dados de uma ficha | ficha.py |
| PATCH | `/fichas/{id}/status` | Atualizar Status da Ficha | Atualiza o status de uma ficha | ficha.py |
| GET | `/fichas/pendentes` | Listar Fichas Pendentes | Lista fichas pendentes com paginação e filtros | ficha.py |
| POST | `/fichas/pendentes/{id}/processar` | Processar Ficha Pendente | Processa uma ficha pendente, criando ou vinculando a uma guia | ficha.py |
| DELETE | `/fichas/pendentes/{id}` | Excluir Ficha Pendente | Exclui uma ficha pendente | ficha.py |
| GET | `/fichas/paciente/{paciente_id}` | Listar Fichas por Paciente | Retorna uma lista paginada de fichas de um paciente específico | ficha.py |
| GET | `/fichas/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | ficha.py |
| POST | `/fichas/{ficha_id}/sessoes` | Criar Múltiplas Sessões | Cria múltiplas sessões para uma ficha específica | ficha.py |
| POST | `/fichas/{ficha_id}/gerar-sessoes` | Gerar Sessões para Ficha | Gera automaticamente sessões para uma ficha com base nas regras de negócio | ficha.py |
| GET | `/fichas/{ficha_id}/sessoes` | Listar Sessões por Ficha | Retorna uma lista paginada de sessões de uma ficha específica | ficha.py |

## Procedimentos

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/procedimentos` | Listar Procedimentos | Retorna uma lista paginada de procedimentos | procedimento.py |
| POST | `/procedimentos` | Criar Procedimento | Cria um novo procedimento | procedimento.py |
| GET | `/procedimentos/{id}` | Buscar Procedimento | Retorna os dados de um procedimento específico | procedimento.py |
| PUT | `/procedimentos/{id}` | Atualizar Procedimento | Atualiza os dados de um procedimento | procedimento.py |
| DELETE | `/procedimentos/{id}` | Deletar Procedimento | Remove um procedimento do sistema | procedimento.py |
| PATCH | `/procedimentos/{id}/inativar` | Inativar Procedimento | Inativa um procedimento no sistema | procedimento.py |
| GET | `/procedimentos/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | procedimento.py |

## Sessões

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/sessoes` | Listar Sessões | Retorna uma lista paginada de sessões | sessao.py |
| POST | `/sessoes` | Criar Sessão | Cria uma nova sessão | sessao.py |
| GET | `/sessoes/{id}` | Buscar Sessão | Retorna os dados de uma sessão específica | sessao.py |
| PUT | `/sessoes/{id}` | Atualizar Sessão | Atualiza os dados de uma sessão | sessao.py |
| DELETE | `/sessoes/{id}` | Deletar Sessão | Remove uma sessão do sistema | sessao.py |
| GET | `/sessoes/ficha-presenca/{ficha_presenca_id}` | Listar Sessões por Ficha de Presença | Retorna todas as sessões de uma ficha de presença específica | sessao.py |
| GET | `/sessoes/paciente/{paciente_id}` | Listar Sessões por Paciente | Retorna todas as sessões de um paciente específico | sessao.py |
| GET | `/sessoes/guia/{guia_id}` | Listar Sessões por Guia | Retorna todas as sessões de uma guia específica | sessao.py |
| GET | `/sessoes/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | sessao.py |

## Execuções

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/execucoes` | Listar Execuções | Retorna uma lista paginada de execuções | execucao.py |
| POST | `/execucoes` | Criar Execução | Cria uma nova execução | execucao.py |
| GET | `/execucoes/{id}` | Buscar Execução | Retorna os dados de uma execução específica | execucao.py |
| PUT | `/execucoes/{id}` | Atualizar Execução | Atualiza os dados de uma execução | execucao.py |
| DELETE | `/execucoes/{id}` | Deletar Execução | Remove uma execução do sistema | execucao.py |
| GET | `/execucoes/guia/{guia_id}` | Listar Execuções por Guia | Retorna todas as execuções de uma guia específica | execucao.py |
| PUT | `/execucoes/{id}/biometria` | Verificar Biometria da Execução | Atualiza o status de verificação biométrica de uma execução | execucao.py |
| GET | `/execucoes/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | execucao.py |

## Divergências

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/divergencias` | Listar Divergências | Retorna uma lista paginada de divergências | divergencia.py |
| POST | `/divergencias` | Criar Divergência | Cria uma nova divergência | divergencia.py |
| GET | `/divergencias/{id}` | Buscar Divergência | Retorna os dados de uma divergência específica | divergencia.py |
| PUT | `/divergencias/{id}` | Atualizar Divergência | Atualiza os dados de uma divergência | divergencia.py |
| DELETE | `/divergencias/{id}` | Deletar Divergência | Remove uma divergência do sistema | divergencia.py |
| POST | `/divergencias/{id}/resolver` | Resolver Divergência | Marca uma divergência como resolvida | divergencia.py |
| GET | `/divergencias/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | divergencia.py |

## Agendamentos

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| POST | `/agendamentos` | Criar Agendamento | Cria um novo agendamento | agendamento.py |
| PUT | `/agendamentos/{id}` | Atualizar Agendamento | Atualiza um agendamento existente | agendamento.py |
| GET | `/agendamentos/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | agendamento.py |

## Auditoria

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| POST | `/auditoria/iniciar` | Iniciar Auditoria | Inicia uma nova auditoria | auditoria.py |
| POST | `/auditoria/executar` | Executar Auditoria | Executa uma auditoria completa | auditoria.py |
| GET | `/auditoria/divergencias` | Listar Divergências | Lista divergências com paginação e filtros | auditoria.py |
| GET | `/auditoria/divergencias/{divergencia_id}` | Obter Divergência | Obtém uma divergência pelo ID | auditoria.py |
| PUT | `/auditoria/divergencias/{divergencia_id}` | Atualizar Divergência | Atualiza uma divergência | auditoria.py |
| PUT | `/auditoria/divergencias/{divergencia_id}/status` | Atualizar Status | Atualiza o status de uma divergência | auditoria.py |
| GET | `/auditoria/estatisticas` | Obter Estatísticas | Obtém estatísticas das divergências | auditoria.py |

## Auditoria de Execução

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/auditoria-execucao/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | auditoria_execucao.py |
| GET | `/auditoria-execucao/ultima` | Buscar Última Auditoria | Retorna os dados da última auditoria de execução realizada | auditoria_execucao.py |
| GET | `/auditoria-execucao` | Listar Auditorias | Retorna uma lista paginada de auditorias de execuções | auditoria_execucao.py |
| GET | `/auditoria-execucao/{id}` | Buscar Auditoria | Retorna os dados de uma auditoria de execução específica | auditoria_execucao.py |
| POST | `/auditoria-execucao` | Criar Auditoria | Cria uma nova auditoria de execução | auditoria_execucao.py |
| PUT | `/auditoria-execucao/{id}` | Atualizar Auditoria | Atualiza os dados de uma auditoria de execução | auditoria_execucao.py |
| DELETE | `/auditoria-execucao/{id}` | Deletar Auditoria | Remove uma auditoria de execução do sistema | auditoria_execucao.py |
| GET | `/auditoria-execucao/periodo/{data_inicial}/{data_final}` | Buscar por Período | Retorna auditorias em um período específico | auditoria_execucao.py |
| GET | `/auditoria-execucao/execucoes` | Listar Execuções | Lista execuções de auditoria com paginação e filtros | auditoria_execucao.py |
| GET | `/auditoria-execucao/execucoes/{execucao_id}` | Buscar Execução | Obtém uma execução de auditoria pelo ID | auditoria_execucao.py |
| PUT | `/auditoria-execucao/execucoes/{execucao_id}` | Atualizar Execução | Atualiza uma execução de auditoria | auditoria_execucao.py |
| DELETE | `/auditoria-execucao/execucoes/{execucao_id}` | Deletar Execução | Deleta uma execução de auditoria | auditoria_execucao.py |
| GET | `/auditoria-execucao/execucoes/{execucao_id}/divergencias` | Listar Divergências | Lista divergências de uma execução específica | auditoria_execucao.py |
| GET | `/auditoria-execucao/execucoes/{execucao_id}/estatisticas` | Obter Estatísticas | Obtém estatísticas de uma execução específica | auditoria_execucao.py |
| POST | `/auditoria-execucao/iniciar` | Iniciar Auditoria | Inicia uma nova execução de auditoria | auditoria_execucao.py |

## Importação

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/importacao/ultima-importacao` | Obter Última Importação | Obtém os dados da última importação registrada | importacao.py |
| GET | `/importacao/limpar-datas-controle` | Limpar Datas de Controle | Limpa datas inválidas nas tabelas de controle de importação | importacao.py |
| GET | `/importacao/corrigir-agendamentos-importados` | Corrigir Agendamentos | Corrige os agendamentos importados | importacao.py |
| GET | `/importacao/verificar-quantidade-agendamentos` | Verificar Quantidade | Verifica a quantidade de agendamentos disponíveis para importação | importacao_routes.py |
| GET | `/importacao/importar-agendamentos` | Importar Agendamentos | Importa agendamentos do sistema legado para o sistema atual | importacao_routes.py |

## Upload

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/upload/prompts` | Listar Prompts | Lista todos os prompts personalizados disponíveis no sistema | upload.py |

## Planos de Saúde

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/planos-saude` | Listar Planos de Saúde | Retorna uma lista paginada de planos de saúde | plano_saude.py |
| POST | `/planos-saude` | Criar Plano de Saúde | Cria um novo plano de saúde | plano_saude.py |
| GET | `/planos-saude/{id}` | Buscar Plano de Saúde | Retorna os dados de um plano de saúde específico | plano_saude.py |
| PUT | `/planos-saude/{id}` | Atualizar Plano de Saúde | Atualiza os dados de um plano de saúde | plano_saude.py |
| DELETE | `/planos-saude/{id}` | Deletar Plano de Saúde | Remove um plano de saúde do sistema | plano_saude.py |
| GET | `/planos-saude/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | plano_saude.py |

## Storage

| Método | Rota | Summary | Descrição | Arquivo |
|--------|------|---------|-----------|---------|
| GET | `/storage` | Listar Arquivos | Retorna uma lista paginada de arquivos armazenados | storage.py |
| POST | `/storage` | Upload de Arquivo | Faz upload de um novo arquivo | storage.py |
| GET | `/storage/{id}` | Buscar Arquivo | Retorna os dados de um arquivo específico | storage.py |
| PUT | `/storage/{id}` | Atualizar Arquivo | Atualiza os dados de um arquivo | storage.py |
| DELETE | `/storage/{id}` | Deletar Arquivo | Remove um arquivo do sistema | storage.py |
| GET | `/storage/reference/{reference_id}/{reference_type}` | Buscar Arquivos por Referência | Retorna todos os arquivos vinculados a uma referência específica | storage.py |
| GET | `/storage/download/all` | Download de Todos os Arquivos | Baixa todos os arquivos em um arquivo ZIP | storage.py |
| POST | `/storage/sync` | Sincronizar com R2 | Sincroniza a tabela storage com os arquivos do Cloudflare R2 | storage.py |
| GET | `/storage/teste` | Teste | Endpoint de teste para verificar se o serviço está funcionando | storage.py |

## Observações

Este documento identifica as APIs disponíveis no backend que não estão sendo utilizadas diretamente pelo frontend. Algumas possíveis razões para estas APIs não serem chamadas:

1. **APIs de Teste**: Endpoints com `/teste` são geralmente utilizados apenas para verificar se o serviço está funcionando.
2. **Funcionalidades Não Implementadas**: Algumas APIs podem corresponder a funcionalidades que ainda não foram implementadas na interface do usuário.
3. **APIs Internas**: Alguns endpoints podem ser utilizados apenas internamente pelo backend ou por scripts de administração.
4. **APIs Legadas**: Algumas APIs podem ter sido substituídas por novas implementações, mas mantidas para compatibilidade.

Recomenda-se revisar estas APIs não utilizadas para determinar se:
- Devem ser implementadas no frontend
- Podem ser removidas do backend se não forem mais necessárias
- Devem ser mantidas para uso futuro ou para outros sistemas
