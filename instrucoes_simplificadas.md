# Instruções Simplificadas para Atualizar o Modelo de Agendamentos

Em vez de tentar editar manualmente o arquivo `01_criar_tabelas.sql`, uma solução mais simples é executar o arquivo SQL que criamos diretamente no banco de dados Supabase.

## Opção 1: Console do Supabase

1. Acesse o painel do Supabase (`https://app.supabase.io`)
2. Vá para a seção "SQL Editor"
3. Clique em "New Query" 
4. Copie e cole todo o conteúdo do arquivo `agendamentos_atualizar_modelo.sql`
5. Execute o script

## Opção 2: Cliente SQL

Se preferir usar um cliente SQL (como pgAdmin, DBeaver, etc.):

1. Conecte-se ao seu banco de dados Supabase
2. Abra uma nova consulta SQL
3. Copie e cole o conteúdo do arquivo `agendamentos_atualizar_modelo.sql`
4. Execute o script

## Resultado Esperado

Depois de executar o script, você terá:

1. Uma função `proc_agendamento_enriquecer_dados()` para adicionar dinamicamente dados de pacientes
2. Uma função `fn_limpar_dados_importacao_agendamentos()` para limpar dados de importação
3. Uma view `vw_agendamentos_completos` que mostra os agendamentos com os dados completos de pacientes

## Testando a Solução

Para verificar se a solução funcionou:

1. Execute a seguinte consulta no Supabase:
   ```sql
   SELECT * FROM vw_agendamentos_completos LIMIT 10;
   ```

2. Tente importar agendamentos novamente - o erro "Could not find the 'carteirinha' column" não deve mais ocorrer.

Não é necessário modificar o arquivo `01_criar_tabelas.sql` original, já que todas as alterações foram aplicadas diretamente no banco de dados. 