# Funções Auxiliares (Utils)

Este documento descreve as principais funções auxiliares utilizadas no projeto, tanto no frontend quanto no backend.

## 1. Frontend Utils

### 1.1 Formatação de Data e Hora

```typescript
// Função principal para formatar datas
formatarData(data: string | Date | undefined | null, incluirHora: boolean = false): string

// Função para converter data para formato ISO
formatDateToISO(dateStr: string): string

// Formatação de data e hora completa
formatDateTime(date: string | Date | null | undefined): string

// Formatação de data e hora com locale
formatarDataHora(data: string | Date | null): string
```

### 1.2 Formatação de Dados Pessoais

```typescript
// Formatação de CPF
formatarCPF(cpf: string | null | undefined): string

// Formatação de telefone
formatarTelefone(telefone: string | null | undefined): string
```

## 2. Backend Utils

### 2.1 Manipulação de Datas

```python
# Formata uma data para o padrão DD/MM/YYYY
formatar_data(data: Any) -> str

# Converte date ou datetime para string ISO
format_date(value: Any) -> Any

# Formata campos de data em um dicionário para string ISO
format_date_fields(data: Dict[str, Any], fields: list[str]) -> Dict[str, Any]

# Converte datetime para string ISO format
format_datetime(dt: Union[datetime, str, None]) -> Union[str, None]

# Formata todos os campos de data em um dicionário de modelo
format_model_dates(data: Dict[str, Any]) -> Dict[str, Any]
```

### 2.2 Serialização JSON

**Importante:** Toda a lógica de serialização JSON para datas e UUIDs está centralizada no arquivo `backend/utils/date_utils.py`.

```python
# Serializa datas para JSON (em date_utils.py)
class DateEncoder(json.JSONEncoder):
    # ... implementação ...

# Serializa UUIDs e datas para JSON (em date_utils.py)
class DateUUIDEncoder(json.JSONEncoder):
    # ... implementação ...
```

## 3. Campos de Data Padrão

Os seguintes campos são tratados como datas em toda a aplicação:

```python
DATE_FIELDS = [
    'data_nascimento',
    'avaliacao_luria_data_inicio_treinamento',
    'created_at',
    'updated_at',
    'deleted_at',
    'data_validade',
    'data_inicio',
    'data_fim'
]
```

## 4. Boas Práticas

1. Sempre use as funções de formatação apropriadas para garantir consistência na exibição de dados.
2. Para datas no frontend, prefira usar `formatarData()` que já lida com timezone e locale.
3. No backend, use os encoders JSON apropriados (`DateEncoder`, `DateUUIDEncoder` de `date_utils`) ao serializar respostas.
4. Para novos campos de data, adicione-os à lista `DATE_FIELDS` para garantir tratamento consistente.
5. Ao lidar com datas vindas de APIs externas ou entrada do usuário, use `formatar_data()` que tenta interpretar vários formatos. 

## 5. Tratamento de Erros Comuns com Datas

### 5.1 Erro "Object of type date is not JSON serializable"

Este erro ocorre quando tentamos serializar objetos `date` ou `datetime` diretamente para JSON. Para resolver:

1. **No serviço**:
   - Sempre use o `DateEncoder` ou `DateUUIDEncoder` (se houver UUIDs) ao serializar respostas que contêm datas:
   ```python
   from backend.utils.date_utils import DateEncoder, DateUUIDEncoder

   # Garantir que as datas e UUIDs sejam serializadas corretamente
   if result:
       result = json.loads(json.dumps(result, cls=DateUUIDEncoder)) # Ou DateEncoder se não houver UUIDs
   ```
   - Aplique isso em todos os métodos que retornam dados com datas/UUIDs (get, list, create, update)

2. **No repositório**:
   - Use `format_date_fields` antes de enviar dados para o banco:
   ```python
   formatted_data = format_date_fields(data, DATE_FIELDS)
   ```
   - Use `format_date_fields` ao receber dados do banco:
   ```python
   return format_date_fields(result.data[0], DATE_FIELDS)
   ```
   - Certifique-se de que o campo de data esteja na lista `DATE_FIELDS`

3. **Nos modelos**:
   - Configure corretamente os encoders JSON nos modelos Pydantic:
   ```python
   class Config:
       json_encoders = {
           date: lambda v: v.isoformat() if isinstance(v, date) else v,
           datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
       }
   ```

### 5.2 Erro "object APIResponse[~_ReturnT] can't be used in 'await' expression"

Este erro ocorre quando tentamos usar `await` com um objeto que não é awaitable. Para resolver:

1. **No repositório**:
   - Use `from_` em vez de `table` com `await`:
   ```python
   # Incorreto
   result = await self.db.table(self.table).update(data).eq("id", str(id)).execute()
   
   # Correto
   result = self.db.from_(self.table).update(data).eq("id", str(id)).execute()
   ```

2. **Consistência**:
   - Mantenha o mesmo padrão em todos os métodos do repositório
   - Verifique todos os métodos que usam `table` e substitua por `from_` se necessário

## 6. Checklist para Implementação de Novas Entidades

Ao implementar uma nova entidade que contém campos de data:

1. **Adicione os campos de data à lista `DATE_FIELDS`**:
   ```python
   DATE_FIELDS = [
       # ... campos existentes ...
       'data_nova_entidade'  # Adicione o novo campo aqui
   ]
   ```

2. **Implemente a serialização JSON em todos os métodos do serviço**:
   - get, list, create, update, e quaisquer métodos personalizados

3. **Use `format_date_fields` em todos os métodos do repositório**:
   - Antes de enviar para o banco
   - Ao receber do banco

4. **Verifique a consistência dos métodos**:
   - Use `from_` em vez de `table` com `await`
   - Mantenha o mesmo padrão em todos os métodos

5. **Teste a serialização**:
   - Verifique se as datas são serializadas corretamente em todas as operações
   - Teste especialmente as operações de atualização que podem causar o erro "not JSON serializable" 

# Instruções de Utilitários

## Scripts Disponíveis

### Scripts de Geração de Dados

1. **Gerar Dados Antigo** (`backend/scripts/gerar_dados_antigo.py`)
   - Gera dados de teste básicos
   - Usa estrutura antiga de imports
   - Execução:
   ```bash
   python -m backend.scripts.gerar_dados_antigo
   ```

2. **Gerar Dados Teste** (`backend/scripts/gerar_dados_teste.py`)
   - Nova versão com estrutura atualizada
   - Usa imports relativos
   - Execução:
   ```bash
   python -m backend.scripts.gerar_dados_teste
   ```

3. **Gerar Dados de Testes** (`backend/scripts/gerar_dados_de_testes.py`)
   - Versão mais completa
   - Gera mais dados e relacionamentos
   - Execução:
   ```bash
   python -m backend.scripts.gerar_dados_de_testes
   ```

## Utilitários de Banco de Dados

### Conexão com Supabase

O cliente Supabase está configurado em `backend/config/config.py`:

```python
from ..config.config import supabase
```

### Funções de Teste

1. **Testar Conexão**
   ```python
   from ..config.config import test_connection
   
   if test_connection():
       print("Conexão estabelecida com sucesso!")
   ```

2. **Consultas Básicas**
   ```python
   # Exemplo de consulta
   response = supabase.table("tabela").select("*").execute()
   ```

## Utilitários de Desenvolvimento

### Estrutura de Imports

1. **Imports Relativos**
   ```python
   from ..config.config import supabase
   from ..repositories.database_supabase import get_supabase_client
   ```

2. **Imports Absolutos**
   ```python
   from backend.config.config import supabase
   from backend.repositories.database_supabase import get_supabase_client
   ```

### Boas Práticas

1. **Organização de Código**
   - Use imports relativos para módulos internos
   - Mantenha imports organizados
   - Evite imports circulares

2. **Configurações**
   - Use variáveis de ambiente
   - Centralize configurações
   - Documente alterações

3. **Testes**
   - Use scripts apropriados
   - Mantenha dados consistentes
   - Documente casos de teste

## Solução de Problemas

1. **Erros de Importação**
   - Verifique estrutura de pastas
   - Confirme `__init__.py`
   - Use imports corretos

2. **Erros de Conexão**
   - Verifique variáveis de ambiente
   - Teste conexão
   - Verifique logs

3. **Erros de Execução**
   - Use flag `-m`
   - Verifique dependências
   - Teste em ambiente isolado

## 7. Boas Práticas para Importação de Dados

### 7.1 Segurança em Consultas SQL

1. **Parametrização de Consultas**:
   - Sempre parametrize consultas SQL para evitar injeção SQL
   ```python
   # Correto - Parametrização
   query = "SELECT * FROM tabela WHERE data >= %s"
   cursor.execute(query, (data_inicial,))
   
   # Incorreto - Vulnerável a injeção SQL
   query = f"SELECT * FROM tabela WHERE data >= '{data_inicial}'"
   cursor.execute(query)
   ```

2. **Validação de Entradas**:
   - Valide tipos e formatos de dados antes de usá-los em consultas
   - Converta strings de data para objetos datetime antes de formatá-las para SQL

### 7.2 Importação de Grandes Volumes

1. **Verificação Prévia**:
   - Sempre verifique a quantidade de registros antes de iniciar importações
   - Use limites e paginação para processar grandes volumes de dados

2. **Processamento em Lotes**:
   ```python
   # Exemplo de importação em lotes
   offset = 0
   limit = 1000
   while True:
       query = f"SELECT * FROM tabela LIMIT {limit} OFFSET {offset}"
       # Processar lote
       if registros_processados < limit:
           break
       offset += limit
   ```

3. **Feedback ao Usuário**:
   - Forneça informações sobre progresso para importações longas
   - Use contagens preliminares para estimar tempos de processamento

### 7.3 Filtragem por Data

1. **Formato Correto**:
   - Para MySQL, use o formato 'YYYY-MM-DD HH:MM:SS'
   - Sempre inclua a parte de tempo para evitar ambiguidades

2. **Comparação de Datas**:
   ```python
   # Para capturar registros do dia inteiro
   data_inicial = '2023-01-01 00:00:00'  # Início do dia
   data_final = '2023-01-01 23:59:59'    # Fim do dia
   
   query = "SELECT * FROM tabela WHERE data_registro BETWEEN %s AND %s"
   cursor.execute(query, (data_inicial, data_final))
   ```

3. **Fusos Horários**:
   - Considere diferenças de fuso horário entre sistemas
   - Documente qual fuso está sendo usado (UTC, local, etc.)

### 7.4 Debugging de Consultas SQL

1. **Log de Consultas**:
   ```python
   import logging
   
   # Configure seu logger
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)
   
   # Log da consulta antes da execução
   query = "SELECT * FROM tabela WHERE data >= %s"
   params = (data_inicial,)
   logger.debug(f"Executando consulta: {query} com parâmetros: {params}")
   
   cursor.execute(query, params)
   ```

2. **Validação de Resultados**:
   - Verifique a contagem de registros retornados
   - Compare com resultados esperados ou históricos anteriores

3. **Resolução de Problemas Comuns**:
   - Erro de sintaxe SQL: Verifique aspas, parênteses e vírgulas
   - Zero registros: Verifique filtros de data e formatos
   - Erro "Invalid datetime format": Certifique-se que as datas estão no formato 'YYYY-MM-DD HH:MM:SS'

## 8. Checklist para Importação de Dados Legados

1. **Preparação**:
   - [ ] Defina os campos a serem importados e seus mapeamentos
   - [ ] Identifique campos de chave primária para deduplicação
   - [ ] Determine estratégia para lidar com dados duplicados

2. **Segurança**:
   - [ ] Use credenciais com permissões mínimas necessárias
   - [ ] Parametrize todas as consultas SQL
   - [ ] Não exponha credenciais em código ou logs

3. **Execução**:
   - [ ] Verifique a quantidade de registros antes da importação
   - [ ] Use transações para garantir integridade de dados
   - [ ] Implemente processamento em lotes para grandes volumes

4. **Validação**:
   - [ ] Compare contagens antes e depois da importação
   - [ ] Verifique amostra de registros para garantir integridade
   - [ ] Documente discrepâncias e suas justificativas