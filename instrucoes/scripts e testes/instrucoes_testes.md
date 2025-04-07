# Instruções de Testes

## Scripts de Teste Disponíveis

O projeto possui três scripts principais para geração de dados de teste:

1. **Script Antigo** (`backend/scripts/gerar_dados_antigo.py`)
   - Mantido para referência histórica
   - Usa a estrutura antiga de imports
   - Execução:
   ```bash
   python -m backend.scripts.gerar_dados_antigo
   ```

2. **Script Novo** (`backend/scripts/gerar_dados_teste.py`)
   - Nova versão com estrutura atualizada
   - Usa imports relativos
   - Execução:
   ```bash
   python -m backend.scripts.gerar_dados_teste
   ```

3. **Script Detalhado** (`backend/scripts/gerar_dados_de_testes.py`)
   - Versão mais completa com mais dados de teste
   - Usa a nova estrutura de imports
   - Execução:
   ```bash
   python -m backend.scripts.gerar_dados_de_testes
   ```

## Estrutura dos Dados de Teste

Os scripts geram os seguintes tipos de dados:

1. **Protocolos**
   - Dados básicos de protocolos
   - Relacionamentos com outras entidades

2. **Guias**
   - Guias de atendimento
   - Status e informações de processamento

3. **Fichas**
   - Fichas de presença
   - Relacionamentos com guias e protocolos

4. **Sessões**
   - Registros de sessões
   - Status e informações de assinatura

5. **Execuções**
   - Registros de execução
   - Status de biometria

6. **Atendimentos de Faturamento**
   - Dados para faturamento
   - Informações de pacientes e profissionais

## Como Usar os Scripts

1. **Preparação**
   - Certifique-se de que o ambiente está configurado
   - Verifique as variáveis de ambiente
   - Instale as dependências necessárias

2. **Execução**
   - Escolha o script apropriado
   - Use o comando com a flag `-m`
   - Monitore a saída para erros

3. **Verificação**
   - Confirme a geração dos dados
   - Verifique os relacionamentos
   - Teste as funcionalidades

## Boas Práticas

1. **Dados de Teste**
   - Mantenha os dados consistentes
   - Use dados realistas
   - Evite dados sensíveis

2. **Execução**
   - Execute em ambiente de desenvolvimento
   - Faça backup antes de executar
   - Documente alterações

3. **Manutenção**
   - Atualize os scripts conforme necessário
   - Mantenha a documentação atualizada
   - Reporte problemas encontrados

## Solução de Problemas

1. **Erros de Importação**
   - Verifique a estrutura de pastas
   - Confirme os imports relativos
   - Verifique os arquivos `__init__.py`

2. **Erros de Dados**
   - Verifique a estrutura do banco
   - Confirme as permissões
   - Valide os dados gerados

3. **Erros de Execução**
   - Verifique logs de erro
   - Confirme dependências
   - Teste em ambiente isolado

# Guia de Testes

Este documento descreve a estrutura e práticas de teste do projeto.

## 1. Estrutura de Testes

### 1.1 Backend (Python/FastAPI)

Os testes do backend são organizados em:

```
backend/
  tests/
    unit/           # Testes unitários
    integration/    # Testes de integração
    fixtures/       # Dados de teste reutilizáveis
```

### 1.2 Frontend (Next.js/React)

Os testes do frontend são organizados em:

```
frontend/
  __tests__/
    components/    # Testes de componentes
    pages/         # Testes de páginas
    hooks/         # Testes de hooks customizados
```

## 2. Testes de Endpoint

Cada endpoint da API deve ter testes básicos que verificam:

```python
@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint está funcionando"}
```

Exemplo de teste de endpoint:

```python
async def test_endpoint_pacientes():
    response = await client.get("/api/pacientes/teste")
    assert response.status_code == 200
    assert response.json() == {"message": "Endpoint de pacientes está funcionando"}
```

## 3. Dados de Teste

### 3.1 Scripts de Geração

Utilizamos scripts para gerar dados de teste:

```python
def gerar_nome_paciente() -> str:
    nomes = ['João', 'Maria', 'José', 'Ana', 'Pedro']
    sobrenomes = ['Silva', 'Santos', 'Oliveira']
    return f"{random.choice(nomes)} {random.choice(sobrenomes)}"

def gerar_divergencias(quantidade: int) -> List[dict]:
    return [gerar_divergencia() for _ in range(quantidade)]
```

### 3.2 Fixtures

Dados de teste comuns são definidos como fixtures:

```python
@pytest.fixture
def paciente_teste():
    return {
        "nome": "Paciente Teste",
        "data_nascimento": "2000-01-01",
        "cpf": "12345678900"
    }
```

## 4. Testes de Conexão

Testes de conexão com serviços externos:

```python
def test_connection():
    if not supabase:
        print("Supabase não configurado")
        return False

    try:
        response = supabase.table("protocolos_excel").select("*").limit(1).execute()
        print("Conexão com Supabase estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao conectar com Supabase: {e}")
        return False
```

## 5. Boas Práticas

1. **Isolamento**: Cada teste deve ser independente e não afetar outros testes.
2. **Limpeza**: Limpar dados de teste após cada execução.
3. **Mocking**: Usar mocks para serviços externos (Supabase, APIs, etc).
4. **Cobertura**: Manter cobertura mínima de 80% para código crítico.
5. **Documentação**: Documentar casos de teste complexos.

## 6. Execução de Testes

### 6.1 Backend

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura
pytest --cov=app

# Executar testes específicos
pytest tests/unit/test_pacientes.py
```

### 6.2 Frontend

```bash
# Executar todos os testes
npm test

# Executar testes com watch mode
npm test -- --watch

# Executar testes com cobertura
npm test -- --coverage
```

## 7. CI/CD

Os testes são executados automaticamente:

1. Em cada pull request
2. Na branch principal antes do deploy
3. Em deploys de produção

## 8. Troubleshooting

1. Verificar configuração do ambiente (.env)
2. Confirmar conexão com Supabase
3. Limpar cache de testes
4. Verificar logs de erro detalhados 