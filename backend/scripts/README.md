# Importação de Pacientes MySQL para Supabase

Este diretório contém scripts para importar dados de pacientes de um banco de dados MySQL para o Supabase.

## Requisitos

Certifique-se de ter as seguintes dependências instaladas:

```bash
pip install pymysql supabase python-dotenv
```

## Configuração

Os scripts utilizam as configurações definidas no arquivo `.env` na raiz do projeto para se conectar ao Supabase.

Para a conexão com o MySQL, as credenciais já estão configuradas nos scripts:

- Host: 64.23.227.147
- Porta: 3306
- Usuário: root
- Senha: 591#2n4AO1Qp

## Scripts Disponíveis

### 1. Importação Interativa (`import_pacientes.py`)

Este script permite importar pacientes de forma interativa, guiando o usuário através de um processo passo a passo.

**Uso:**
```bash
python backend/scripts/import_pacientes.py
```

O script irá:
1. Listar todos os bancos de dados disponíveis no servidor MySQL
2. Solicitar que você selecione um banco de dados
3. Listar todas as tabelas no banco de dados selecionado
4. Solicitar que você selecione a tabela que contém os dados dos pacientes
5. Mostrar a estrutura da tabela selecionada
6. Confirmar se deseja iniciar a importação
7. Realizar a importação e mostrar o progresso

### 2. Importação em Lote (`batch_import_pacientes.py`)

Este script permite importar pacientes de forma automatizada, sem interação do usuário, ideal para processamento em lote ou uso em scripts.

**Uso:**
```bash
python backend/scripts/batch_import_pacientes.py --database NOME_DO_BANCO --tabela NOME_DA_TABELA [opções]
```

**Parâmetros:**
- `--database`, `-d`: Nome do banco de dados MySQL (obrigatório)
- `--tabela`, `-t`: Nome da tabela que contém os pacientes (obrigatório)
- `--modo`, `-m`: Modo de importação ('pular' ou 'substituir', padrão: 'pular')
- `--limite`, `-l`: Número máximo de registros a importar
- `--offset`, `-o`: Número de registros a pular (útil para paginação)

**Exemplos:**

Importar todos os pacientes da tabela 'clientes' do banco 'clinica':
```bash
python backend/scripts/batch_import_pacientes.py --database clinica --tabela clientes
```

Importar os primeiros 100 pacientes, substituindo registros existentes:
```bash
python backend/scripts/batch_import_pacientes.py --database clinica --tabela clientes --modo substituir --limite 100
```

Importar do registro 101 ao 200:
```bash
python backend/scripts/batch_import_pacientes.py --database clinica --tabela clientes --limite 100 --offset 100
```

## Mapeamento de Campos

O script mapeia os campos do MySQL para o Supabase de acordo com o seguinte padrão:

| Campo Supabase | Campos MySQL procurados |
|----------------|-------------------------|
| id | (gerado como UUID) |
| nome | nome, Nome |
| codigo_aba | codigo, id |
| cpf | cpf, CPF |
| data_nascimento | data_nascimento, DataNascimento |
| nome_responsavel | nome_responsavel, Responsavel |
| nome_mae | nome_mae, Mae |
| nome_pai | nome_pai, Pai |
| sexo | sexo, Sexo |
| endereco | endereco, Endereco |
| bairro | bairro, Bairro |
| cidade | cidade, Cidade |
| estado | estado, Estado |
| telefone | telefone, Telefone |
| email | email, Email |
| observacoes | observacoes, Observacoes |

Se a estrutura da sua tabela MySQL for diferente, você precisará ajustar a função `mapear_paciente()` nos scripts.

## Logs

A versão em lote do script gera logs detalhados em um arquivo na pasta `logs/` na raiz do projeto. Os logs contêm informações sobre o processo de importação, incluindo conexões, número de registros processados, erros, etc.

## Solução de Problemas

### Erro de Conexão ao MySQL

Se você encontrar erros de conexão ao MySQL, verifique:
- Se o servidor MySQL está acessível a partir da sua máquina
- Se as credenciais estão corretas
- Se o banco de dados existe
- Se o firewall permite conexões na porta 3306

### Erro ao Inserir no Supabase

Se você encontrar erros ao inserir registros no Supabase, verifique:
- Se as credenciais do Supabase no arquivo `.env` estão corretas
- Se a tabela 'pacientes' existe no Supabase
- Se a estrutura da tabela 'pacientes' corresponde aos campos que você está tentando inserir 