# Guia Rápido - Frontend

## 1. Configuração Inicial

```bash
# Instalar dependências
npm install

# Configurar .env.local
cp .env.example .env.local
# Editar .env.local com suas credenciais

# Executar em desenvolvimento
npm run dev
```

## 2. Estrutura do Projeto

```
frontend/
├── src/
│   ├── app/              # Páginas e rotas
│   ├── components/       # Componentes reutilizáveis
│   ├── hooks/            # Hooks personalizados
│   ├── services/         # Serviços e APIs
│   ├── styles/           # Estilos globais
│   └── utils/            # Utilitários
├── public/               # Arquivos estáticos
└── middleware.ts         # Proteção de rotas e CORS
```

## 3. Padrões de Desenvolvimento

### 3.1 Componentes
- Use componentes pequenos e reutilizáveis
- Siga o padrão de composição
- Implemente TypeScript para tipagem forte
- Documente props e comportamentos complexos

### 3.2 Serviços
- Um arquivo service por entidade
- Implemente tratamento de erros consistente
- Use o proxy Supabase para evitar CORS
- Adicione headers de autenticação apropriados

### 3.3 Formulários
- Use React Hook Form para gerenciamento
- Valide campos com Zod
- Implemente feedback visual de validação
- Mantenha validações consistentes

## 4. Autenticação e Segurança

### 4.1 Hook de Autenticação
```typescript
// Uso básico do hook de autenticação
const { isAuthenticated, user, loading, isOffline, login, logout } = useAuth()
```

### 4.2 Proxy para Supabase
- Use a rota `/api/supabase` para requisições ao Supabase
- Envie o token de autenticação em todas as requisições
- Suporta todos os métodos HTTP (GET, POST, PUT, PATCH, DELETE)

### 4.3 Tratamento Offline
- Detecte automaticamente o estado de conexão
- Forneça feedback ao usuário sobre estado offline
- Armazene operações para execução posterior quando reconectar

## 5. Boas Práticas

### 5.1 Tipagem
- Use interfaces para definir tipos de dados
- Declare campos relacionados como opcionais
- Mantenha consistência com o backend
- Documente comportamentos especiais

### 5.2 Performance
- Otimize componentes pesados com memoização
- Implemente estratégias de cache
- Use loading states para feedback ao usuário
- Otimize imagens e assets

### 5.3 Tratamento de Erros
- Implemente tratamento específico para erros de autenticação
- Use mensagens de erro contextuais
- Mantenha logs detalhados no console para depuração
- Implemente fallbacks quando recursos falham

### 5.4 Manipulação de Datas
- Ao enviar para o backend: use formato ISO
- Ao exibir ao usuário: use formatos localizados
- Use funções utilitárias de formatação consistentes

## 6. Integração com Backend

- Use interceptors para logging e tratamento de erros
- Implemente retry automático para falhas de rede
- Mantenha campos de auditoria (created_by, updated_by)
- Implemente invalidação de cache após operações

## 7. Campos Relacionados

- Defina tipos com campos relacionados conforme necessário
- Use componentes de seleção apropriados (ComboboxField)
- Implemente lazy loading para dados relacionados grandes
- Trate casos onde dados relacionados são nulos

## 8. Comandos Úteis

```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# Lint
npm run lint

# Testes
npm test
```

## 9. Configuração CORS

- Configure allowedOrigins no middleware e next.config.js
- Implemente tratamento de preflight OPTIONS
- Inclua todos os métodos HTTP necessários
- Adicione headers para credentials e métodos permitidos

## 10. Componentes UI Reutilizáveis

- **DataTable**: Tabela com paginação, ordenação e filtragem
- **Modal**: Janela modal com suporte a fechamento e transições
- **FormField**: Campo de formulário com validação e feedback
- **ComboboxField**: Campo de seleção avançado com busca
- **DatePicker**: Seletor de data com suporte a localização

## 11. Acessibilidade

- Implemente atributos ARIA corretamente
- Mantenha contraste e tamanho de texto adequados
- Permita navegação por teclado
- Teste com leitores de tela 