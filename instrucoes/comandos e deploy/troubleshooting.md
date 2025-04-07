# Guia de Troubleshooting

## 1. Problemas de Autenticação

### 1.1 Erro de Login
**Problema**: Não consegue fazer login na aplicação.
**Solução**:
1. Verificar credenciais do Supabase no `.env`
2. Limpar cookies do navegador
3. Verificar se o usuário existe no Supabase
4. Verificar logs do console para erros específicos

### 1.2 Sessão Expirada
**Problema**: Sessão expira frequentemente.
**Solução**:
1. Verificar configuração de tempo de sessão no Supabase
2. Implementar refresh token automático
3. Verificar timezone do servidor

## 2. Problemas de API

### 2.1 Erro 500
**Problema**: Servidor retorna erro interno.
**Solução**:
1. Verificar logs do servidor
2. Validar payload da requisição
3. Verificar conexão com Supabase
4. Verificar tratamento de exceções

### 2.2 CORS
**Problema**: Erro de CORS no frontend.
**Solução**:
1. Verificar configuração de CORS no backend:
```python
origins = [
    "http://localhost:3000",
    "https://clinicalmf-producao.vercel.app"
]
```
2. Verificar URL da API no frontend
3. Usar credenciais corretas

## 3. Problemas de Banco de Dados

### 3.1 Erro de Conexão
**Problema**: Não consegue conectar ao Supabase.
**Solução**:
1. Verificar variáveis de ambiente:
```env
SUPABASE_URL=
SUPABASE_KEY=
```
2. Testar conexão:
```python
def test_connection():
    try:
        response = supabase.table("protocolos_excel").select("*").limit(1).execute()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False
```

### 3.2 Erro de Permissão
**Problema**: Erro de permissão ao acessar tabelas.
**Solução**:
1. Verificar RLS policies
2. Confirmar que usuário está autenticado
3. Verificar roles e permissões

## 4. Problemas de Build

### 4.1 Frontend
**Problema**: Erro no build do Next.js.
**Solução**:
1. Limpar cache:
```bash
rm -rf .next
npm run build
```
2. Verificar dependências:
```bash
npm install
npm audit fix
```
3. Verificar tipos TypeScript

### 4.2 Backend
**Problema**: Erro ao iniciar servidor FastAPI.
**Solução**:
1. Verificar ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Verificar imports e dependências
3. Verificar configurações do uvicorn

## 5. Problemas de Performance

### 5.1 Frontend Lento
**Problema**: Interface lenta ou travando.
**Solução**:
1. Implementar virtualização em listas grandes
2. Otimizar re-renders com useMemo/useCallback
3. Lazy loading de componentes pesados
4. Otimizar imagens e assets

### 5.2 Backend Lento
**Problema**: Requisições demorando muito.
**Solução**:
1. Implementar caching
2. Otimizar queries do Supabase
3. Usar paginação adequadamente
4. Monitorar tempos de resposta

## 6. Problemas de Upload

### 6.1 Erro no Upload
**Problema**: Falha ao fazer upload de arquivos.
**Solução**:
1. Verificar configuração do R2:
```env
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
```
2. Verificar tamanho máximo permitido
3. Validar tipos de arquivo aceitos

### 6.2 Arquivos Corrompidos
**Problema**: Arquivos corrompidos após upload.
**Solução**:
1. Verificar encoding
2. Implementar verificação de integridade
3. Validar processo de upload

## 7. Logs e Debugging

### 7.1 Frontend
```typescript
// Interceptor de API
api.interceptors.response.use(
  (response) => {
    console.log('[API Response]', response);
    return response;
  },
  (error) => {
    console.error('[API Error]', error);
    return Promise.reject(error);
  }
);
```

### 7.2 Backend
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    # operação
    logger.info("Sucesso")
except Exception as e:
    logger.error(f"Erro: {str(e)}")
```

## 8. Checklist de Verificação

1. **Ambiente**
   - [ ] Variáveis de ambiente configuradas
   - [ ] Dependências instaladas
   - [ ] Serviços externos acessíveis

2. **Autenticação**
   - [ ] Tokens válidos
   - [ ] Sessão ativa
   - [ ] Permissões corretas

3. **Dados**
   - [ ] Banco conectado
   - [ ] Queries funcionando
   - [ ] Cache limpo

4. **Rede**
   - [ ] CORS configurado
   - [ ] URLs corretas
   - [ ] Certificados válidos

## 9. Contatos de Suporte

1. **Desenvolvimento**
   - Frontend: [responsável]
   - Backend: [responsável]
   - DevOps: [responsável]

2. **Infraestrutura**
   - Supabase: [contato]
   - Vercel: [contato]
   - R2: [contato]