# Documentação de Autenticação e Segurança

## Visão Geral

O sistema utiliza o Supabase como provedor de autenticação, com mecanismos de proxy para evitar problemas de CORS e suporte para operações offline.

## Arquitetura de Segurança

### 1. Frontend (Next.js)

#### 1.1 Proteção de Rotas
- Route groups no Next.js com pasta `(auth)` para rotas protegidas
- Middleware de autenticação
- Redirecionamento automático para login quando não autenticado

#### 1.2 Autenticação com Supabase
- Context API para gerenciamento do estado de autenticação
- Hook `useAuth` para acesso ao contexto
- Detecção de estado offline automática

#### 1.3 Proxy para Supabase
- API route no Next.js para evitar problemas de CORS
- Encaminhamento seguro de tokens de autenticação
- Suporte a todos os métodos HTTP necessários

#### 1.4 Tratamento de Estado Offline
- Detecção automática da conectividade
- Fila de operações para execução quando reconectar
- Cache de dados essenciais para funcionamento offline

### 2. Backend (Supabase)

#### 2.1 Segurança via Postgres
- RLS (Row Level Security) para controle de acesso
- Políticas por operação (SELECT, INSERT, UPDATE, DELETE)
- Autenticação via JWT tokens

#### 2.2 Auditoria
- Campos automáticos de auditoria (`created_by`, `updated_by`)
- Soft delete com `deleted_at`
- Registro de acessos e operações

## Fluxos de Autenticação

### 1. Login
- Formulário de login > Supabase Auth > Gestão de Sessão > Redirecionamento
- Atualização automática de último acesso
- Armazenamento seguro de tokens

### 2. Proteção de Rotas
- Verificação de sessão ativa
- Middleware para validação de tokens
- Redirecionamento quando necessário

### 3. Logout
- Invalidação de sessão no Supabase
- Limpeza de dados locais
- Redirecionamento para login

### 4. Recuperação Após Offline
- Detecção de reconexão
- Execução de operações pendentes
- Sincronização de dados

## Boas Práticas Implementadas

### 1. Segurança
- CORS configurado apropriadamente
- Headers de segurança
- Sanitização de inputs
- Validação em múltiplas camadas

### 2. Tratamento de Erros
- Respostas padronizadas
- Logs seguros (sem dados sensíveis)
- Retry com backoff exponencial

### 3. Prevenção de Ataques
- Proteção contra XSS via headers e sanitização
- Proteção contra CSRF
- Proteção contra SQL Injection via parametrização

## Configuração

### Variáveis de Ambiente
```env
NEXT_PUBLIC_SUPABASE_URL=sua_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=sua_chave_anon
NEXT_PUBLIC_URL=url_frontend
```

## Políticas de Segurança (RLS)

- Políticas SELECT: Controle de visibilidade de dados
- Políticas INSERT/UPDATE: Verificação de autenticação
- Políticas DELETE: Soft delete preferencial

## Recomendações

### 1. Manutenção
- Revisão periódica das políticas de segurança
- Monitoramento de logs de acesso
- Atualização regular de dependências

### 2. Dados Sensíveis
- Criptografia quando necessário
- Adesão à LGPD
- Evitar armazenamento offline de dados sensíveis

### 3. Operações Offline
- Priorização de operações críticas
- Resolução de conflitos
- Feedback claro ao usuário
