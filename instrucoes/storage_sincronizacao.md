# Sistema de Armazenamento e Sincronização

## 1. Visão Geral

O sistema de armazenamento é responsável por gerenciar arquivos digitais (PDFs, imagens, documentos) utilizados pela aplicação. Os arquivos são armazenados no Cloudflare R2 (serviço de armazenamento em nuvem) e seus metadados são registrados na tabela `storage` do Supabase.

A sincronização bidirecional garante que:
1. Todos os arquivos presentes no R2 tenham registros correspondentes na tabela `storage`
2. Todos os registros na tabela `storage` correspondam a arquivos realmente existentes no R2

### 1.1 Diagrama de Sincronização

```
┌─────────────────┐                 ┌─────────────────┐
│                 │                 │                 │
│   Cloudflare    │                 │    Supabase     │
│       R2        │◄───────────────►│  Tabela Storage │
│                 │  Sincronização  │                 │
│  (Arquivos)     │  Bidirecional   │  (Metadados)    │
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘
        ▲                                   ▲
        │                                   │
        │                                   │
        │                                   │
        │                                   │
        └───────────────┬───────────────────┘
                        │
                ┌───────────────┐
                │               │
                │  Aplicação    │
                │  ClinicalMF   │
                │               │
                └───────────────┘
```

## 2. Componentes do Sistema

### 2.1 Armazenamento de Arquivos
- **Cloudflare R2**: Serviço de armazenamento em nuvem onde os arquivos são fisicamente armazenados
- **Tabela Storage**: Tabela no Supabase que mantém metadados dos arquivos (nome, tamanho, tipo, URL, etc.)

### 2.2 Estrutura da Tabela Storage
```sql
CREATE TABLE storage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  nome TEXT NOT NULL,
  url TEXT NOT NULL,
  content_type TEXT,
  size INTEGER,
  tipo_referencia TEXT,
  referencia_id UUID,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by UUID REFERENCES usuarios(id),
  updated_by UUID REFERENCES usuarios(id),
  deleted_at TIMESTAMP WITH TIME ZONE
);
```

## 3. Funcionalidade de Sincronização

### 3.1 Visão Geral da Sincronização
A sincronização bidirecional entre o R2 e a tabela `storage` é realizada através do botão "Sincronizar R2" na página de armazenamento. Esta funcionalidade:

1. Adiciona registros na tabela `storage` para arquivos que existem no R2 mas não estão na tabela
2. Remove registros da tabela `storage` (marcando como excluídos) quando os arquivos correspondentes não existem mais no R2

### 3.2 Processo de Sincronização
```python
async def sync_with_r2(self) -> bool:
    """Sincroniza a tabela storage com os arquivos do R2"""
    # 1. Lista todos os arquivos no R2
    r2_files = self.storage_r2.list_files()
    
    # 2. Cria um conjunto com as URLs de todos os arquivos no R2
    r2_urls = {self.storage_r2.get_url(file["key"]) for file in r2_files}
    
    # 3. Obtém todos os registros ativos da tabela storage
    storage_records = await self._get_all_active_storage_records()
    
    # 4. Adiciona novos arquivos que existem no R2 mas não na tabela storage
    for file in r2_files:
        url = self.storage_r2.get_url(file["key"])
        existing = await self.repository.get_by_path(url)
        if not existing:
            # Cria um novo registro
            storage_data = StorageCreate(...)
            await self.repository.create(storage_data)
    
    # 5. Remove registros da tabela storage que não existem mais no R2
    for record in storage_records:
        if record["url"] not in r2_urls:
            # Marca o registro como excluído na tabela storage
            await self.repository.delete(record["id"])
```

## 4. Interface do Usuário

### 4.1 Página de Armazenamento
A página de armazenamento (`/storage`) permite:
- Visualizar todos os arquivos armazenados
- Fazer upload de novos arquivos
- Sincronizar a tabela `storage` com o R2
- Excluir arquivos

### 4.2 Botão de Sincronização
O botão "Sincronizar R2" na página de armazenamento inicia o processo de sincronização bidirecional:
```typescript
const handleSync = async () => {
    try {
        setIsSyncing(true);
        await storageService.syncWithR2();
        toast.success("Sincronização bidirecional concluída com sucesso");
        refetch();
    } catch (error) {
        console.error("Erro ao sincronizar:", error);
        toast.error("Erro ao sincronizar com R2");
    } finally {
        setIsSyncing(false);
    }
};
```

## 5. Casos de Uso

### 5.1 Quando Usar a Sincronização
- Após exclusões manuais de arquivos no R2
- Quando arquivos foram adicionados diretamente ao R2 sem passar pela aplicação
- Periodicamente para garantir a integridade dos dados
- Quando houver suspeita de inconsistências entre o R2 e a tabela `storage`

### 5.2 Benefícios
- Mantém a integridade dos dados
- Evita referências a arquivos inexistentes
- Garante que todos os arquivos no R2 estejam catalogados
- Facilita a auditoria e o gerenciamento de arquivos

## 6. Troubleshooting

### 6.1 Problemas Comuns
- **Erro de permissão**: Verifique se as credenciais do R2 estão configuradas corretamente
- **Timeout**: Para grandes volumes de arquivos, a sincronização pode demorar mais tempo
- **Arquivos não aparecem**: Verifique se o caminho/URL está correto no R2

### 6.2 Logs
A sincronização gera logs detalhados que podem ser consultados para diagnóstico:
- Número de arquivos encontrados no R2
- Número de registros na tabela `storage`
- Registros adicionados e removidos
- Erros específicos durante o processo

### 6.3 Exemplos de Logs

```
2023-07-15 10:15:32 - INFO - Encontrados 156 arquivos no R2
2023-07-15 10:15:33 - INFO - Encontrados 150 registros ativos na tabela storage
2023-07-15 10:15:35 - INFO - Registro removido: relatorio_2022.pdf (URL: https://storage.example.com/fichas/relatorio_2022.pdf)
2023-07-15 10:15:36 - INFO - Registro removido: exame_123.pdf (URL: https://storage.example.com/fichas/exame_123.pdf)
2023-07-15 10:15:40 - INFO - Sincronização concluída: 8 registros adicionados, 2 registros removidos
```

Em caso de erro:
```
2023-07-15 10:15:32 - ERROR - Erro: r2_files não é uma lista: None
2023-07-15 10:15:32 - ERROR - Erro ao sincronizar com R2: Falha na conexão com o serviço R2
```

## 7. Considerações Finais

A sincronização bidirecional entre o R2 e a tabela `storage` é uma funcionalidade essencial para manter a integridade dos dados do sistema. Recomenda-se executar a sincronização periodicamente, especialmente após operações manuais no R2 ou quando houver suspeita de inconsistências.

Para melhorias futuras, pode-se considerar:
- Sincronização automática agendada
- Relatórios detalhados de sincronização
- Opção para sincronizar apenas determinados tipos de arquivos ou pastas 