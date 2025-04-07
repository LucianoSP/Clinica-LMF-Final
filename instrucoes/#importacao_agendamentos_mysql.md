# Implementação da Importação de Agendamentos

Este documento descreve a implementação da funcionalidade de importação de agendamentos do sistema legado MySQL para o Supabase.

## 1. Estrutura de Dados

A tabela de agendamentos no Supabase inclui os seguintes campos para controlar a importação:

```sql
ALTER TABLE agendamentos 
ADD COLUMN IF NOT EXISTS importado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS id_origem VARCHAR(255),
ADD COLUMN IF NOT EXISTS data_registro_origem TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS data_atualizacao_origem TIMESTAMPTZ;

-- Índices para otimizar consultas
CREATE INDEX IF NOT EXISTS idx_agendamentos_id_origem ON agendamentos(id_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_registro_origem ON agendamentos(data_registro_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_atualizacao_origem ON agendamentos(data_atualizacao_origem);
```

## 2. Tabela de Controle de Importação

Uma tabela específica para controlar o processo de importação:

```sql
CREATE TABLE IF NOT EXISTS controle_importacao_agendamentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timestamp_importacao TIMESTAMPTZ DEFAULT NOW(),
  ultima_data_registro_importada TIMESTAMPTZ,
  ultima_data_atualizacao_importada TIMESTAMPTZ,
  quantidade_registros_importados INTEGER DEFAULT 0,
  quantidade_registros_atualizados INTEGER DEFAULT 0,
  usuario_id UUID REFERENCES usuarios(id),
  observacoes TEXT
);

-- Índices para otimização
CREATE INDEX IF NOT EXISTS idx_controle_importacao_agendamentos_datas 
    ON controle_importacao_agendamentos(ultima_data_registro_importada, ultima_data_atualizacao_importada);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_agendamentos_timestamp 
    ON controle_importacao_agendamentos(timestamp_importacao);
```

## 3. View para Acesso aos Dados Completos

Para facilitar o acesso aos dados relacionados, foi criada uma view:

```sql
CREATE OR REPLACE VIEW vw_agendamentos_completos AS
SELECT 
    a.*,
    p.nome AS paciente_nome,
    c.numero_carteirinha AS carteirinha,
    proc.nome AS procedimento_nome
FROM 
    agendamentos a
LEFT JOIN 
    pacientes p ON a.paciente_id = p.id
LEFT JOIN 
    carteirinhas c ON p.id = c.paciente_id
LEFT JOIN 
    procedimentos proc ON a.procedimento_id = proc.id;
```

## 4. Abordagem de Relação Direta

A implementação atual utiliza uma abordagem de relação direta entre os sistemas:

1. **Campo `id_origem`**: Este campo armazena o ID original do registro no MySQL
2. **Busca Direta**: Os registros são relacionados diretamente através deste identificador único
3. **Simplificação**: Sem a necessidade de tabelas de mapeamento intermediárias, o que simplifica o processo

## 5. Implementação no Backend

A funcionalidade está implementada principalmente nos seguintes endpoints:

### 5.1 Verificar Quantidade de Agendamentos

```
GET /importacao/verificar-quantidade-agendamentos
```

Este endpoint permite verificar quantos agendamentos estão disponíveis para importação antes de iniciar o processo.

### 5.2 Importar Agendamentos por Data Específica

```
POST /agendamentos/importar-desde-data
```

Este endpoint permite importar agendamentos a partir de uma data específica, com os seguintes parâmetros:

- `database`: Nome do banco de dados MySQL (padrão: "abalarissa_db")
- `tabela`: Nome da tabela de agendamentos (padrão: "ps_schedule")
- `data_inicial`: Data inicial para importar agendamentos (formato YYYY-MM-DD)
- `data_final`: Data final para importar agendamentos (opcional)

### 5.3 Importar Agendamentos

```
POST /agendamentos/importar
```

Este endpoint importa agendamentos usando uma abordagem baseada em períodos e datas de registro/atualização.

## 6. Processo de Importação

O processo de importação segue estes passos:

1. **Verificação de Conexão**: Testa a conexão com o banco MySQL
2. **Busca de Agendamentos**: Consulta os agendamentos disponíveis no MySQL
3. **Verificação de Existência**: Para cada agendamento, verifica se já existe no Supabase pelo `id_origem`
4. **Mapeamento de Dados**: Converte o formato de dados do MySQL para o formato do Supabase
5. **Inserção ou Atualização**: Insere novos agendamentos ou atualiza existentes
6. **Registro de Controle**: Mantém registros da importação na tabela de controle

## 7. Função de Mapeamento

A função `mapear_agendamento` é responsável por converter os dados do formato MySQL para o formato Supabase. Ela faz:

1. Conversão de tipos de dados (string para int, float, boolean)
2. Tratamento de datas e timestamps
3. Remoção de campos não existentes na tabela de destino
4. Mapeamento direto de identificadores usando o campo `id_origem`

## 8. Considerações sobre Chaves Estrangeiras

Importante observar que:

1. **Referências a Usuários**: Todas as tabelas usam `usuarios(id)` como referência para os campos `created_by` e `updated_by`, não `auth.users(id)`.

2. **Usuário Sistema**: O sistema utiliza um usuário com ID `00000000-0000-0000-0000-000000000000` na tabela `usuarios` para operações automáticas.

## 9. Passos para Executar a Importação

1. **Preparação do Ambiente**:
   - Verifique as configurações de conexão no arquivo `.env`
   - Certifique-se de que as tabelas necessárias estão criadas no Supabase

2. **Importação de Pacientes**:
   - Garanta que os pacientes já foram importados corretamente
   - Os pacientes devem ter seus campos `id_origem` corretamente preenchidos

3. **Importação de Agendamentos**:
   - Use o endpoint `/agendamentos/importar-desde-data` para importações por data
   - Monitore os logs para identificar problemas

## 10. Interface Frontend

A aplicação frontend inclui interfaces para:

1. **Verificação de Agendamentos**: Permite verificar quantos agendamentos estão disponíveis
2. **Importação por Data**: Permite especificar um intervalo de datas para importação
3. **Visualização de Resultados**: Exibe estatísticas e logs da importação

## 11. Observações Importantes

1. **Tabela MySQL**: O nome padrão da tabela MySQL para agendamentos é `ps_schedule`

2. **Campo `id_origem`**: O identificador único `id_origem` é usado para relacionar registros entre o MySQL e o Supabase

3. **Backup**: Sempre faça um backup do banco de dados Supabase antes de importações em massa

4. **Acesso aos Dados Completos**: Use a view `vw_agendamentos_completos` para acessar informações relacionadas aos agendamentos

5. **Modelo de Dados Simplificado**: A tabela `agendamentos` contém apenas dados essenciais, com relacionamentos para outras tabelas em vez de duplicação de dados

## 12. Importação de Tabelas Adicionais do Sistema Aba

Além da tabela de agendamentos (`ps_schedule`), foram adicionados endpoints para importar outras tabelas do sistema Aba que contêm informações relacionadas:

### 12.1 Tabelas do Sistema Aba

As seguintes tabelas foram adicionadas ao sistema:

1. **profissoes** (ws_profissoes): Armazena profissões dos usuários
2. **locais** (ps_locales): Armazena locais de atendimento
3. **salas** (ps_care_rooms): Armazena salas de atendimento
4. **usuarios_aba** (ws_users): Armazena dados dos usuários do sistema Aba
5. **usuarios_profissoes** (ws_users_profissoes): Relaciona usuários e profissões
6. **usuarios_especialidades** (ws_users_especialidades): Relaciona usuários e especialidades
7. **agendamentos_profissionais** (ps_schedule_professionals): Relaciona agendamentos e profissionais

### 12.2 Endpoints para Importação das Tabelas do Sistema Aba

Os seguintes endpoints foram implementados para importar as tabelas adicionais:

```
GET /importacao/verificar-quantidade-profissoes
POST /importacao/importar-profissoes

GET /importacao/verificar-quantidade-locais
POST /importacao/importar-locais

GET /importacao/verificar-quantidade-salas
POST /importacao/importar-salas

GET /importacao/verificar-quantidade-usuarios-aba
POST /importacao/importar-usuarios-aba

POST /importacao/importar-usuarios-profissoes
POST /importacao/importar-usuarios-especialidades
POST /importacao/importar-agendamentos-profissionais

POST /importacao/atualizar-especialidades-ids
POST /importacao/relacionar-agendamentos-com-tabelas-aba
```

### 12.3 Importação de Todos os Dados de Uma Vez

Para facilitar o processo de importação, foi implementado um endpoint que importa todos os dados relacionados do sistema Aba em uma ordem adequada:

```
POST /importacao/importar-tudo-sistema-aba
```

Este endpoint executa as seguintes etapas:

1. Importa profissões
2. Atualiza IDs de especialidades
3. Importa locais
4. Importa salas
5. Importa usuários
6. Importa relações usuários-profissões
7. Importa relações usuários-especialidades
8. Importa relações agendamentos-profissionais

### 12.4 Relacionamento com Agendamentos Existentes

Após importar os dados, é possível relacionar os agendamentos existentes com as tabelas do sistema Aba usando o endpoint:

```
POST /importacao/relacionar-agendamentos-com-tabelas-aba
```

Este endpoint cria relações entre os agendamentos existentes e:
- Salas (`room_local_id` → `salas`)
- Locais (`schedule_local_id` → `locais`)
- Especialidades (`schedule_especialidade_id` → `especialidades`)

### 12.5 Processo de Importação das Tabelas do Sistema Aba

Para importar as tabelas do sistema Aba, siga estes passos:

1. **Verifique a quantidade de registros disponíveis** usando os endpoints de verificação de quantidade
2. **Importe os dados** usando o endpoint `/importacao/importar-tudo-sistema-aba` ou os endpoints individuais
3. **Relacione os agendamentos** com as tabelas do sistema Aba usando o endpoint `/importacao/relacionar-agendamentos-com-tabelas-aba`

### 12.6 Observações sobre a Importação das Tabelas do Sistema Aba

1. **Sem Tabelas de Controle**: Para simplificar, não são utilizadas tabelas de controle para as importações das tabelas do sistema Aba devido ao volume relativamente pequeno de dados
2. **Importação Completa**: Cada vez que uma importação é executada, todos os registros são verificados e atualizados conforme necessário
3. **Relações Diretas**: As relações são estabelecidas usando os IDs originais do sistema Aba
4. **Campos de ID Original**: Os campos `room_local_id`, `local_id`, `especialidade_id`, etc. são usados para estabelecer as relações entre as tabelas
