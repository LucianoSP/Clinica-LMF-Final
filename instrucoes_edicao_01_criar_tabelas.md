# Instruções para atualizar o arquivo 01_criar_tabelas.sql

## Passo a passo

1. Abra o arquivo `sql/01_criar_tabelas.sql` em um editor de texto.

2. **Adicione o código para funções e views após os índices da tabela agendamentos**:
   - Localize a definição da tabela agendamentos e seus índices (aproximadamente linhas 376-438).
   - Logo após o último índice `CREATE INDEX IF NOT EXISTS idx_agendamentos_data_atualizacao_origem`, adicione o código contido no arquivo `alteracoes_para_01_criar_tabelas.sql`.

3. **Remova as funções duplicadas no final do arquivo**:
   - Localize as funções duplicadas no final do arquivo (aproximadamente linhas 1035-1110).
   - Remova todo o trecho listado no arquivo `remover_duplicados_01_criar_tabelas.sql`.

## Observações importantes

- A tabela `agendamentos` em si não precisa ser modificada, pois já está corretamente definida.
- Estamos adicionando funções e views que complementam a tabela para permitir o uso do modelo relacional.
- Essas funções permitem que o frontend continue funcionando normalmente, mesmo com as alterações na estrutura interna.

## Verificação

Após fazer as alterações, verifique:

1. Se as funções e a view estão definidas logo após os índices da tabela agendamentos
2. Se as funções duplicadas no final do arquivo foram removidas
3. Se não há erros de sintaxe no SQL

## Próximos passos após a edição

Depois de editar o arquivo:

1. Execute o SQL no banco de dados Supabase para aplicar as alterações
2. Teste a importação de agendamentos para verificar se o erro "Could not find the 'carteirinha' column" não ocorre mais
3. Verifique se a interface do sistema consegue visualizar os agendamentos corretamente 