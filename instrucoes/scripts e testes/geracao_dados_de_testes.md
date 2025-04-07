# Documentação: Script de Geração de Dados para Testes

## Índice
1. [Visão Geral](#1-visão-geral)
2. [Requisitos e Configuração](#2-requisitos-e-configuração)
3. [Estrutura do Script](#3-estrutura-do-script)
4. [Cenários de Teste e Divergências](#4-cenários-de-teste-e-divergências)
5. [Detalhamento dos Métodos](#5-detalhamento-dos-métodos)
6. [Fluxo de Execução](#6-fluxo-de-execução)
7. [Como Executar o Script](#7-como-executar-o-script)
8. [Solução de Problemas](#8-solução-de-problemas)

## 1. Visão Geral

O script `gerar_dados_de_testes.py` foi desenvolvido para facilitar o teste do sistema de auditoria de divergências, gerando automaticamente um conjunto de dados que simula diversos cenários de uso e problemas comuns. O script popula todas as tabelas relevantes com dados coerentes e interconectados, criando especificamente cenários que demonstram os oito tipos de divergências documentados no sistema.

### 1.1 Objetivo Principal

Criar um ambiente de dados controlado que permite:
- Testar a funcionalidade de auditoria de divergências
- Validar o fluxo completo do processamento de fichas
- Simular diversos cenários de erro para verificar a robustez do sistema
- Facilitar o desenvolvimento e testes de novas funcionalidades

### 1.2 Melhorias Implementadas

O script atual inclui as seguintes melhorias:

1. **Agendamentos mais realistas**:
   - Gera 5 agendamentos por paciente (distribuídos entre passado e futuro)
   - Distribui agendamentos ao longo de 60 dias (30 no passado, 30 no futuro)
   - Implementa distribuição estatística de status:
     - 70% realizados (agendamentos passados)
     - 15% faltou (agendamentos passados)
     - 15% cancelados (agendamentos passados)
   - Diversidade de planos de saúde, unidades e códigos de faturamento

2. **Vinculação Melhorada**:
   - Agendamentos são vinculados corretamente às fichas
   - Fichas são vinculadas às sessões
   - Execuções são criadas com base nas sessões

## 2. Requisitos e Configuração

### 2.1 Dependências

O script requer as seguintes bibliotecas Python:
- `supabase-py`: Para interação com o banco de dados Supabase
- `dotenv`: Para carregar variáveis de ambiente
- `faker`: Para geração de dados fictícios realistas
- `datetime`: Para manipulação de datas e horas
- `logging`: Para registro de logs durante a execução
- `uuid`: Para geração de identificadores únicos

### 2.2 Configuração do Ambiente

O script utiliza a configuração de banco de dados da aplicação principal através do módulo `backend.config.config`. Isso garante consistência nas credenciais e conexões utilizadas.

### 2.3 Permissões Necessárias

O usuário configurado na chave do Supabase deve ter permissões para:
- Ler todas as tabelas do banco de dados
- Inserir registros em todas as tabelas
- Excluir registros de todas as tabelas
- Atualizar registros em todas as tabelas

Ao ser executado, o script realiza uma verificação automática de permissões, tentando inserir e excluir um registro de teste na tabela `especialidades`.

## 3. Estrutura do Script

### 3.1 Classe Principal: DatabasePopulator

O script é organizado em torno da classe `DatabasePopulator`, que contém métodos para popular cada uma das tabelas do sistema. Esta classe recebe as seguintes configurações iniciais:

- `supabase`: Cliente Supabase inicializado
- `admin_id`: ID do usuário administrador a ser usado como criador dos registros
- `preserve_users`: Flag para preservar usuários existentes (padrão: True)
- `generate_divergences`: Flag para gerar cenários de divergência (padrão: True)

### 3.2 Principais Métodos

A classe `DatabasePopulator` contém os seguintes métodos principais:

1. **Métodos de população por tabela:**
   - `populate_especialidades()`: Cria especialidades médicas básicas
   - `populate_procedimentos()`: Cria procedimentos médicos padrão
   - `populate_planos_saude()`: Cria planos de saúde de exemplo
   - `populate_pacientes()`: Cria pacientes fictícios
   - `populate_carteirinhas()`: Cria carteirinhas vinculadas aos pacientes
   - `populate_guias()`: Cria guias de autorização para procedimentos
   - `populate_agendamentos()`: Cria agendamentos para atendimentos
   - `populate_fichas()`: Cria fichas de presença vinculadas às guias
   - `populate_storage()`: Cria registros de armazenamento para PDFs de fichas
   - `populate_sessoes()`: Cria sessões para cada ficha
   - `populate_execucoes()`: Cria execuções, incluindo casos com divergências
   - `populate_atendimentos_faturamento()`: Cria registros na tabela de faturamento
   - `populate_divergencias_manual()`: Documentação dos cenários de divergência criados

2. **Métodos de controle:**
   - `verificar_permissoes()`: Verifica se o usuário tem permissões adequadas
   - `limpar_dados_antigos()`: Limpa dados existentes nas tabelas
   - `populate_all()`: Método principal que chama todos os outros na ordem correta

## 4. Cenários de Teste e Divergências

O script cria automaticamente os seguintes cenários de divergência, cada um associado a uma guia específica:

| Tipo de Divergência | Guia | Descrição |
|---------------------|------|-----------|
| `ficha_sem_execucao` | G2024003 | Fichas registradas sem execução correspondente |
| `execucao_sem_ficha` | G2024006 | Execuções registradas sem ficha correspondente |
| `data_divergente` | G2024003 | Data da execução diferente da data da sessão |
| `sessao_sem_assinatura` | G2024004 | Sessões sem assinatura do paciente |
| `guia_vencida` | G2024005 | Guia com data de validade expirada |
| `quantidade_excedida` | G2024002 | Quantidade de execuções maior que autorizado |
| `falta_data_execucao` | G2024007 | Execução sem data registrada |
| `duplicidade` | G2024006 | Execução registrada em duplicidade |

### 4.1 Detalhamento dos Cenários

#### 4.1.1 ficha_sem_execucao (G2024003)
- Paciente: Ana Oliveira
- A partir da 5ª sessão da ficha, o status é definido como "pendente"
- Não são criadas execuções para estas sessões
- Resultado: Existe ficha e sessão, mas não há execução correspondente

#### 4.1.2 execucao_sem_ficha (G2024006)
- Paciente: Lucia Mendes
- São criadas execuções com código de ficha temporário (código_ficha_temp = true)
- Estas execuções não estão associadas a nenhuma sessão existente (sessao_id = null)
- Resultado: Existe execução, mas não há ficha/sessão correspondente

#### 4.1.3 data_divergente (G2024003)
- Paciente: Ana Oliveira
- Para as primeiras 3 sessões, a data de execução é igual à data da sessão
- A partir da 4ª sessão, a data de execução é definida como um dia após a data da sessão
- Resultado: A data da execução não corresponde à data da sessão

#### 4.1.4 sessao_sem_assinatura (G2024004)
- Paciente: Pedro Costa Junior
- A cada 2 sessões, o campo `possui_assinatura` é definido como `False`
- Resultado: Existem sessões sem assinatura do paciente

#### 4.1.5 guia_vencida (G2024005)
- Paciente: Carlos Ferreira
- A carteirinha é criada com data de validade no passado (2023-12-31)
- Resultado: A guia está vencida, mas existem execuções para ela

#### 4.1.6 quantidade_excedida (G2024002)
- Paciente: João Santos
- A guia autoriza apenas 5 sessões
- São criadas 8 execuções (3 a mais que o autorizado)
- Resultado: O número de execuções excede o limite autorizado pela guia

#### 4.1.7 falta_data_execucao (G2024007)
- Paciente: Roberto Almeida
- Para as primeiras 3 sessões, o campo `data_execucao` é definido como `NULL`
- Resultado: Existem execuções sem data de execução registrada

#### 4.1.8 duplicidade (G2024006)
- Paciente: Lucia Mendes
- Para as primeiras 3 sessões, são criadas execuções duplicadas com exatamente os mesmos dados
- Resultado: Existem execuções duplicadas para a mesma sessão

## 5. Detalhamento dos Métodos

### 5.1 `populate_especialidades()`
- Cria 6 especialidades médicas: Fisioterapia, Clínica Geral, Ortopedia, Neurologia, Pediatria e Cardiologia
- Vincula o usuário administrador a essas especialidades
- Define Fisioterapia como especialidade principal do administrador

### 5.2 `populate_procedimentos()`
- Cria 5 procedimentos básicos para diferentes tipos de atendimento
- Define valores, tipos e códigos para cada procedimento
- Configura procedimentos ativos por padrão

### 5.3 `populate_planos_saude()`
- Cria 4 planos de saúde: Unimed Nacional, Bradesco Saúde, SulAmérica e Amil
- Define informações como registro ANS, código de operadora e abrangência
- Configura dados de contrato em formato JSON

### 5.4 `populate_pacientes()`
- Cria 7 pacientes fictícios com dados completos para cada cenário de divergência
- Cada paciente recebe um código ABA único para vinculação com agendamentos
- Inclui dados como nome, CPF, data de nascimento, telefone e email

### 5.5 `populate_carteirinhas()`
- Cria uma carteirinha para cada paciente, vinculada a um plano de saúde
- Define datas de validade (uma intencionalmente vencida para simular guia_vencida)
- Configura status da carteirinha (ativa, suspensa, vencida)

### 5.6 `populate_guias()`
- Cria 7 guias de autorização, uma para cada cenário de divergência
- Cada guia tem um número específico (G2024001 a G2024007) para facilitar identificação
- Configura quantidade autorizada, tipo de procedimento e datas de autorização

### 5.7 `populate_agendamentos()`
- Cria 5 agendamentos para cada paciente
- Distribui agendamentos ao longo de 60 dias (30 no passado, 30 no futuro)
- Define status de forma estatística: 70% realizados, 15% faltou, 15% cancelados (passados)
- Inclui códigos de faturamento para integração com o sistema de faturamento

### 5.8 `populate_fichas()`
- Cria uma ficha para cada guia com as informações necessárias
- Associa a ficha ao agendamento correspondente do paciente
- Define código de ficha, data de atendimento e total de sessões

### 5.9 `populate_storage()`
- Cria um registro para cada ficha, simulando o armazenamento do PDF
- Define URL fictícia no Cloudflare R2 e metadados do arquivo
- Atualiza as fichas com o ID do storage para manter a referência

### 5.10 `populate_sessoes()`
- Cria múltiplas sessões para cada ficha
- Define diferentes configurações de assinatura e status conforme o cenário de teste
- Implementa os campos novos como número_guia, código_ficha, profissional_executante e status_biometria

### 5.11 `populate_execucoes()`
- Cria execuções para as sessões conforme os cenários de divergência
- Implementa os novos campos como data_atendimento, paciente_nome, paciente_carteirinha, código_ficha_temp
- Inclui informações do profissional como conselho_profissional, numero_conselho, uf_conselho e código_cbo

### 5.12 `populate_atendimentos_faturamento()`
- Identifica agendamentos com status 'realizado'
- Gera registros na tabela de faturamento com carteirinha, profissional e código de faturamento
- Formata datas e horas conforme exigido pelo banco de dados

### 5.13 `populate_divergencias_manual()`
- Este método não insere divergências diretamente no banco
- Explica que as divergências são geradas pelo sistema de auditoria
- Lista os cenários de divergência criados para facilitar os testes

### 5.14 `limpar_dados_antigos()`
- Remove registros existentes em todas as tabelas, preservando usuários se configurado
- Executa a limpeza na ordem correta para evitar problemas de integridade referencial
- Trata exceções individualmente para cada tabela

### 5.15 `populate_all()`
- Método principal que coordena a execução de todos os outros métodos
- Garante que as tabelas sejam populadas na ordem correta respeitando as dependências
- Registra o progresso da execução e captura exceções para melhor diagnóstico

## 6. Fluxo de Execução

O fluxo de execução do script segue a seguinte ordem:

1. **Inicialização**
   - Carrega configurações
   - Configura logging
   - Verifica permissões do usuário

2. **Limpeza** (opcional, controlada pelo parâmetro `preserve_users`)
   - Remove dados existentes nas tabelas para garantir um ambiente limpo

3. **População de Tabelas Base**
   - Cria especialidades e procedimentos
   - Cria planos de saúde
   - Cria pacientes

4. **População de Relacionamentos**
   - Cria carteirinhas vinculadas aos pacientes e planos
   - Cria guias vinculadas às carteirinhas e procedimentos
   - Cria agendamentos para os pacientes

5. **População de Documentos**
   - Cria fichas vinculadas às guias e agendamentos
   - Cria registros de storage para os PDFs das fichas
   - Cria sessões vinculadas às fichas

6. **População de Execuções**
   - Cria execuções normais
   - Cria execuções com divergências específicas
   - Cria execuções duplicadas
   - Cria execuções sem ficha
   - Cria execuções sem data

7. **População de Tabelas de Suporte**
   - Cria registros na tabela de atendimentos para faturamento

8. **Documentação**
   - Exibe informações sobre os cenários de divergência criados

## 7. Como Executar o Script

### 7.1 Preparação do Ambiente

1. Certifique-se de que as bibliotecas necessárias estão instaladas:
   ```bash
   pip install supabase python-dotenv faker
   ```

2. Verifique que o arquivo `.env` está configurado com as credenciais do Supabase

### 7.2 Execução

Execute o script a partir da raiz do projeto com o seguinte comando:

```bash
python -m backend.scripts.gerar_dados_de_testes
```

### 7.3 Parâmetros Configuráveis

Os principais parâmetros de configuração estão no método `main()`:

- `preserve_users`: Define se os usuários existentes devem ser preservados (True) ou removidos (False)
- `generate_divergences`: Define se os cenários de divergência devem ser criados (True) ou não (False)
- `admin_id`: ID do usuário administrador usado para criar os registros

Para modificar estes parâmetros, edite o script antes de executá-lo:

```python
# Parâmetros de configuração
preserve_users = True  # Altere para False se deseja remover usuários existentes
generate_divergences = True  # Altere para False se não deseja cenários de divergência
```

## 8. Solução de Problemas

### 8.1 Erros Comuns

#### 8.1.1 Erro de Conexão com Supabase
```
Erro: Credenciais do Supabase não encontradas
```
**Solução**: Verifique se o arquivo `.env` existe e contém as variáveis `SUPABASE_URL` e `SUPABASE_KEY` corretas.

#### 8.1.2 Erro de Permissão
```
Erro ao inserir registro de teste: Permission denied
```
**Solução**: O usuário configutado não tem permissões suficientes. Execute os scripts de configuração de segurança recomendados no log.

#### 8.1.3 Erro de Inserção em Lote
```
Erro ao inserir lote X: PostgreSQL Error
```
**Solução**: O script tentará inserir os registros um a um quando falhar em lote. Verifique os logs para identificar qual registro específico está causando o problema.

#### 8.1.4 Erro de Tabela Não Existente
```
Tabela atendimentos_faturamento não existe ou não está acessível
```
**Solução**: Certifique-se de executar o script de criação de tabelas antes de gerar os dados.

### 8.2 Dicas para Testes

1. **Teste em Ambiente Isolado**: Use uma instância de Supabase dedicada para testes.
2. **Backup Prévio**: Faça um backup do banco antes de executar o script.
3. **Verificação Pós-Execução**: Após executar o script, verifique se todos os cenários de divergência foram criados corretamente executando uma auditoria no sistema.
4. **Execução da Auditoria**: Para gerar os registros de divergência, execute o processo de auditoria no sistema após a geração dos dados.
5. **Logs Detalhados**: O script gera logs detalhados que podem ajudar a identificar problemas durante a execução.