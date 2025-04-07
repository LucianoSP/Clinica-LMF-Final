# Módulo de Scraping Unimed

Este módulo implementa um sistema automatizado para extração de dados de sessões executadas no portal da Unimed, com integração ao banco de dados existente.

## Estrutura do Projeto

```
Unimed_Scraping/
├── documentacao/
│   ├── scraping-diagram.md         # Diagrama geral do sistema
│   ├── fluxo-unimed.md             # Diagrama do fluxo original
│   └── unimed_scraping_fluxo.md    # Diagrama do fluxo de scraping Unimed
├── sql/
│   ├── schema_fila_processamento.sql  # Schema original
│   ├── nova_integracao/              # Arquivos da nova integração
│   │   └── unimed_scraping_schema.sql # Schema das novas tabelas
│   └── schema_completo.sql           # Schema unificado 
├── todas_as_fases_windows_final_com_execucoes.py  # Script original
├── adaptacoes_unimed_sessoes.py      # Adaptações para o script original
├── aplicar_adaptacoes.py             # Script para aplicar as adaptações
└── exemplo_integracao_unimed.py      # Exemplo conceitual de implementação
```

## Tabelas do Banco de Dados

O sistema utiliza as seguintes tabelas:

1. **processing_status**: Controle geral das tarefas de processamento
2. **guias_queue**: Fila de guias para processamento
3. **unimed_sessoes_capturadas**: Armazena os dados brutos capturados do site da Unimed
4. **unimed_log_processamento**: Logs detalhados do processamento das sessões
5. **execucoes**: Tabela final onde os dados processados são inseridos

## Fluxo de Funcionamento

O processo de scraping da Unimed segue as etapas:

1. **Inicialização**: Configuração do ambiente, conexões e criação do registro da tarefa
2. **Autenticação**: Login no sistema da Unimed
3. **Captura de Sessões**: Navegação e extração dos dados das sessões executadas
4. **Processamento**: Conversão das sessões capturadas em registros na tabela de execuções
5. **Relatório Final**: Geração de estatísticas e atualização do status da tarefa

## Como Implementar

### Pré-requisitos

- Python 3.8+
- Selenium WebDriver
- Driver Chrome instalado
- Acesso ao banco de dados Supabase

### Configuração

1. Execute o script SQL para criar as tabelas necessárias:

```bash
psql -U seu_usuario -d seu_banco -f Unimed_Scraping/sql/schema_completo.sql
```

2. Configure as variáveis de ambiente:

```bash
export SUPABASE_URL="sua_url_supabase"
export SUPABASE_KEY="sua_chave_supabase"
export UNIMED_USERNAME="seu_usuario_unimed"
export UNIMED_PASSWORD="sua_senha_unimed"
export UNIMED_URL="url_portal_unimed"
```

### Adaptando o Script Original

Para adaptar o script original para usar a tabela intermediária:

1. Coloque todos os arquivos na mesma pasta:
   - `todas_as_fases_windows_final_com_execucoes.py` (script original)
   - `adaptacoes_unimed_sessoes.py` (contém as adaptações)
   - `aplicar_adaptacoes.py` (script que aplica as adaptações)

2. Execute o script para aplicar as adaptações:

```bash
python aplicar_adaptacoes.py
```

Este script irá:
- Fazer um backup do script original
- Aplicar as adaptações necessárias
- Gerar um novo arquivo `todas_as_fases_adaptado.py`

3. Execute o script adaptado:

```bash
python todas_as_fases_adaptado.py
```

### Mudanças Implementadas

As adaptações modificam o script original para:

1. Salvar os dados capturados na tabela intermediária `unimed_sessoes_capturadas`
2. Usar a função de banco de dados `inserir_execucao_unimed` para processar e inserir os dados na tabela `execucoes`
3. Adicionar um método para verificar o status do processamento e gerar estatísticas
4. Atualizar o status da tarefa no final do processamento

## Integração com o Sistema Existente

O módulo foi projetado para:

1. Usar a tabela `processing_status` existente para controlar o progresso
2. Capturar dados brutos e armazená-los na tabela `unimed_sessoes_capturadas`
3. Processar os dados e inseri-los na tabela `execucoes` existente
4. Manter logs detalhados na tabela `unimed_log_processamento`

Esta abordagem permite:
- Rastreabilidade completa do processo
- Reprocessamento em caso de falhas
- Auditoria dos dados capturados
- Separação clara entre captura e processamento

## Solução de Problemas

Se encontrar problemas com a adaptação:

1. Restaure o backup original:
```bash
copy todas_as_fases_windows_final_com_execucoes.py.bak_TIMESTAMP todas_as_fases_windows_final_com_execucoes.py
```

2. Verifique se as tabelas foram criadas corretamente:
```sql
SELECT * FROM information_schema.tables WHERE table_name LIKE 'unimed%';
```

3. Teste a função de processamento diretamente:
```sql
SELECT inserir_execucao_unimed('id-da-sessao-aqui');
``` 