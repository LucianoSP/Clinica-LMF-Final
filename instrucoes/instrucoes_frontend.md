# Instruções do Frontend

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── app/              # Páginas e rotas
│   ├── components/       # Componentes reutilizáveis
│   ├── hooks/           # Hooks personalizados
│   ├── services/        # Serviços e APIs
│   ├── styles/          # Estilos globais
│   └── utils/           # Utilitários
├── public/              # Arquivos estáticos
├── .env.example         # Exemplo de variáveis de ambiente
└── package.json         # Dependências e scripts
```

## Configuração do Ambiente

1. **Instalar Dependências**
   ```bash
   npm install
   ```

2. **Variáveis de Ambiente**
   ```env
   NEXT_PUBLIC_SUPABASE_URL=
   NEXT_PUBLIC_SUPABASE_ANON_KEY=
   NEXT_PUBLIC_API_URL=
   ```

3. **Configuração Next.js**
   ```javascript
   const nextConfig = {
     output: 'standalone',
     images: {
       unoptimized: true,
       domains: ['localhost']
     }
   }
   ```

## Desenvolvimento

### 1. Iniciar Servidor de Desenvolvimento
```bash
npm run dev
```

### 2. Build de Produção
```bash
npm run build
```

### 3. Testar Build
```bash
npm run start
```

## Componentes Principais

### 1. Layout
- `src/components/layout/`
  - Header
  - Sidebar
  - Footer

### 2. Formulários
- `src/components/forms/`
  - Inputs
  - Botões
  - Validações

### 3. Tabelas
- `src/components/tables/`
  - Listagens
  - Paginação
  - Ordenação

## Integração com Backend

### 1. API Client
```typescript
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL
});
```

### 2. Interceptors
```typescript
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Error]', error);
    return Promise.reject(error);
  }
);
```

## Boas Práticas

1. **Componentes**
   - Use TypeScript
   - Implemente PropTypes
   - Siga padrões de design

2. **Estado**
   - Use hooks apropriados
   - Evite prop drilling
   - Implemente contextos

3. **Performance**
   - Otimize imagens
   - Use lazy loading
   - Implemente cache

## Solução de Problemas

1. **Erros de Build**
   - Verificar dependências
   - Limpar cache
   - Verificar tipos

2. **Problemas de API**
   - Verificar URLs
   - Testar endpoints
   - Verificar CORS

3. **Problemas de Renderização**
   - Verificar hooks
   - Testar componentes
   - Verificar estado

# Prompt para Geração de Interface Frontend Completa

Este prompt auxilia na geração de todos os arquivos necessários para implementar uma interface completa para uma nova entidade no sistema, seguindo a estrutura existente do projeto Next.js com TypeScript.

## 1. Tipos (`types/[nome_entidade].ts`)

```typescript
export interface [Nome_Entidade] {
    id: string;
    nome: string;
    // Campos específicos da entidade
    // Exemplo da implementação de Pacientes:
    // cpf?: string;
    // rg?: string;
    // data_nascimento?: string;
    // telefone?: string;
    // email?: string;
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
}

export interface [Nome_Entidade]Create extends Omit<[Nome_Entidade], 
    'id' | 'created_at' | 'updated_at' | 'created_by' | 'updated_by' | 'deleted_at'> {
    // Campos adicionais específicos para criação, se necessário
}

export interface [Nome_Entidade]Update extends Partial<[Nome_Entidade]Create> {
    // Campos adicionais específicos para atualização, se necessário
}

export interface [Nome_Entidade]FormData {
    nome: string;
    // Campos específicos do formulário
    // Exemplo da implementação de Pacientes:
    // cpf?: string;
    // rg?: string;
    // data_nascimento?: string;
    // telefone?: string;
    // email?: string;
}
```

## 2. Serviços (`services/[nome_entidade]Service.ts`)

```typescript
import api from './api';
import { [Nome_Entidade] } from '@/types/[nome_entidade]';
import { StandardResponse, PaginatedResponse } from "@/types/api";
import { [Nome_Entidade]FormData } from '@/components/[nome_entidades]/[Nome_Entidade]Form';
import { supabase } from '@/lib/supabase';

// Interface que estende o FormData para incluir campos de auditoria
interface [Nome_Entidade]Data extends [Nome_Entidade]FormData {
    created_by?: string;
    updated_by?: string;
}

export const [nome_entidade]Service = {
    // Listagem geral
    listar: async (
        page: number = 1,
        limit: number = 10,
        search?: string,
        orderColumn: string = "nome",
        orderDirection: "asc" | "desc" = "asc"
    ): Promise<PaginatedResponse<[Nome_Entidade]>> => {
        const offset = (page - 1) * limit;
        const params = new URLSearchParams({
            offset: String(offset),
            limit: String(limit),
            order_column: orderColumn,
            order_direction: orderDirection
        });

        if (search && search.trim()) {
            params.append("search", search.trim());
        }

        const response = await api.get<PaginatedResponse<[Nome_Entidade]>>(`/api/[nome_entidades]?${params}`);
        return response.data;
    },

    // Listagem por entidade pai (exemplo: listar fichas por paciente)
    listarPorEntidadePai: async (
        entidadePaiId: string,
        page: number = 1,
        limit: number = 10,
        orderColumn: string = "nome",
        orderDirection: "asc" | "desc" = "asc"
    ): Promise<PaginatedResponse<[Nome_Entidade]>> => {
        const offset = (page - 1) * limit;
        const params = new URLSearchParams({
            offset: String(offset),
            limit: String(limit),
            order_column: orderColumn,
            order_direction: orderDirection
        });

        // IMPORTANTE: Usar a rota aninhada correta para relacionamentos
        const response = await api.get<PaginatedResponse<[Nome_Entidade]>>(
            `/api/[entidade_pai]/${entidadePaiId}/[nome_entidades]?${params}`
        );
        return response.data;
    },

    obter: async (id: string): Promise<StandardResponse<[Nome_Entidade]>> => {
        const response = await api.get<StandardResponse<[Nome_Entidade]>>(`/api/[nome_entidades]/${id}`);
        return response.data;
    },

    criar: async (data: [Nome_Entidade]Data): Promise<StandardResponse<[Nome_Entidade]>> => {
        try {
            // Obtém o usuário atual do Supabase
            const { data: { user } } = await supabase.auth.getUser();
            if (!user) throw new Error('Usuário não autenticado');

            const payload = {
                ...data,
                created_by: user.id,
                updated_by: user.id
            };

            console.log('Dados enviados para API:', payload);
            const response = await api.post<StandardResponse<[Nome_Entidade]>>('/api/[nome_entidades]', payload);
            return response.data;
        } catch (error: any) {
            console.error('Erro detalhado:', error.response?.data?.detail);
            throw error;
        }
    },

    atualizar: async (id: string, data: [Nome_Entidade]Data): Promise<StandardResponse<[Nome_Entidade]>> => {
        try {
            // Obtém o usuário atual do Supabase
            const { data: { user } } = await supabase.auth.getUser();
            if (!user) throw new Error('Usuário não autenticado');

            // Remove o created_by se existir e adiciona updated_by
            const { created_by, ...updateData } = data;
            const payload = {
                ...updateData,
                updated_by: user.id
            };

            const response = await api.put<StandardResponse<[Nome_Entidade]>>(`/api/[nome_entidades]/${id}`, payload);
            return response.data;
        } catch (error: any) {
            console.error('Erro ao atualizar [nome_entidade]:', error);
            throw error;
        }
    },

    excluir: async (id: string): Promise<StandardResponse<boolean>> => {
        const response = await api.delete<StandardResponse<boolean>>(`/api/[nome_entidades]/${id}`);
        return response.data;
    }
};
```

## 3. Modal (`components/[nome_entidades]/[Nome_Entidade]Modal.tsx`)

```typescript
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { [Nome_Entidade]Form, [Nome_Entidade]FormData } from "./[Nome_Entidade]Form";
import { [Nome_Entidade] } from "@/types/[nome_entidade]";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { [nome_entidade]Service } from "@/services/[nome_entidade]Service";
import { supabase } from '@/lib/supabase';

interface [Nome_Entidade]ModalProps {
    isOpen: boolean;
    onClose: () => void;
    [nome_entidade]?: [Nome_Entidade];
}

export function [Nome_Entidade]Modal({ isOpen, onClose, [nome_entidade] }: [Nome_Entidade]ModalProps) {
    const queryClient = useQueryClient();

    const handleSubmit = async (formData: [Nome_Entidade]FormData) => {
        try {
            // Verifica autenticação
            const { data: { session } } = await supabase.auth.getSession();
            if (!session) {
                toast.error('Sessão expirada. Por favor, faça login novamente.');
                return;
            }

            if ([nome_entidade]) {
                await [nome_entidade]Service.atualizar([nome_entidade].id, formData);
                toast.success('[Nome_Entidade] atualizado com sucesso');
            } else {
                await [nome_entidade]Service.criar(formData);
                toast.success('[Nome_Entidade] criado com sucesso');
            }

            await queryClient.invalidateQueries({ queryKey: ['[nome_entidades]'] });
            onClose();
        } catch (error: any) {
            console.error('Erro ao salvar [nome_entidade]:', error);
            
            if (error.message?.includes('AuthSessionMissingError')) {
                toast.error('Sessão expirada. Por favor, faça login novamente.');
                return;
            }
            
            const acao = [nome_entidade] ? 'atualizar' : 'criar';
            toast.error(`Erro ao ${acao} [nome_entidade]. Por favor, tente novamente.`);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle>
                        {[nome_entidade] ? "Editar [Nome_Entidade]" : "Novo [Nome_Entidade]"}
                    </DialogTitle>
                </DialogHeader>
                <[Nome_Entidade]Form
                    [nome_entidade]={[nome_entidade]}
                    onSubmit={handleSubmit}
                    onCancel={onClose}
                />
            </DialogContent>
        </Dialog>
    );
}
```

## 4. Componentes de UI Reutilizáveis

### ComboboxField

O ComboboxField é um componente de seleção avançado que suporta busca assíncrona e seleção de itens. É especialmente útil para campos de seleção com muitos dados que precisam ser carregados sob demanda.

```typescript
import { ComboboxField } from "@/components/ui/combobox-field";

interface ExampleProps {
    // ... outros props
}

export function ExampleComponent({ ... }: ExampleProps) {
    // Estado para o item selecionado
    const [selectedItem, setSelectedItem] = useState<Item | null>(null);

    // Função de busca assíncrona
    const handleSearch = async (searchTerm: string) => {
        try {
            const response = await itemService.buscarPorTermo(searchTerm);
            return response.items;
        } catch (error) {
            return [];
        }
    };

    // Função para lidar com a seleção
    const handleSelect = (item: Item | null) => {
        setSelectedItem(item);
        if (item) {
            // Lógica adicional quando um item é selecionado
        }
    };

    return (
        <ComboboxField
            name="item"
            label="Selecione um Item"
            onSearch={handleSearch}
            onSelect={handleSelect}
            getOptionLabel={(item: Item) => item.nome}
            getOptionValue={(item: Item) => item.id}
        />
    );
}
```

#### Props do ComboboxField

| Prop | Tipo | Descrição |
|------|------|-----------|
| name | string | Nome do campo no formulário |
| label | string | Rótulo exibido acima do campo |
| onSearch | (term: string) => Promise<T[]> | Função assíncrona que retorna os resultados da busca |
| onSelect | (item: T \| null) => void | Função chamada quando um item é selecionado ou limpo |
| getOptionLabel | (item: T) => string | Função que retorna o texto a ser exibido para cada item |
| getOptionValue | (item: T) => string | Função que retorna o valor único de cada item |
| placeholder? | string | Texto placeholder opcional |
| disabled? | boolean | Se o campo está desabilitado |

#### Características

- Suporte a busca assíncrona com debounce
- Seleção e limpeza de valores
- Integração com react-hook-form
- Suporte a TypeScript com tipos genéricos
- Acessibilidade com suporte a teclado
- Loading state durante a busca
- Mensagens de erro do formulário

#### Exemplo de Uso com TypeScript

```typescript
interface Paciente {
    id: string;
    nome: string;
    cpf: string;
}

// No componente
<ComboboxField<Paciente>
    name="paciente"
    label="Paciente"
    onSearch={handleSearch}
    onSelect={handleSelect}
    getOptionLabel={(paciente) => `${paciente.nome} - ${paciente.cpf}`}
    getOptionValue={(paciente) => paciente.id}
/>
```

#### Boas Práticas

1. **Tratamento de Erros**
   - Sempre retorne um array vazio em caso de erro na busca
   - Implemente tratamento de erro apropriado no componente pai

2. **Performance**
   - Implemente debounce na função de busca
   - Limite o número de resultados retornados
   - Cache os resultados quando apropriado

3. **UX**
   - Forneça feedback visual durante o carregamento
   - Mantenha mensagens de erro claras
   - Permita navegação por teclado

## 5. Página (`app/cadastros/[nome_entidades]/page.tsx`)

```typescript
"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { [nome_entidade]Service } from "@/services/[nome_entidade]Service";
import { [Nome_Entidade]Modal } from "@/components/[nome_entidades]/[Nome_Entidade]Modal";
import { [Nome_Entidade] } from "@/types/[nome_entidade]";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/ui/data-table";
import { columns } from "./columns";
import { PageHeader } from "@/components/ui/page-header";

export default function [Nome_Entidade]sPage() {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selected[Nome_Entidade], setSelected[Nome_Entidade]] = useState<[Nome_Entidade] | undefined>();

    const { data, isLoading } = useQuery({
        queryKey: ["[nome_entidades]"],
        queryFn: () => [nome_entidade]Service.listar(),
    });

    const handleEdit = ([nome_entidade]: [Nome_Entidade]) => {
        setSelected[Nome_Entidade]([nome_entidade]);
        setIsModalOpen(true);
    };

    const handleCreate = () => {
        setSelected[Nome_Entidade](undefined);
        setIsModalOpen(true);
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setSelected[Nome_Entidade](undefined);
    };

    return (
        <div className="container mx-auto py-10">
            <PageHeader
                title="[Nome_Entidade]s"
                description="Gerencie os [nome_entidade]s do sistema"
                button={
                    <Button onClick={handleCreate}>
                        Novo [Nome_Entidade]
                    </Button>
                }
            />

            <div className="mt-6">
                <DataTable
                    columns={columns}
                    data={data?.items || []}
                    loading={isLoading}
                    onEdit={handleEdit}
                />
            </div>

            <[Nome_Entidade]Modal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                [nome_entidade]={selected[Nome_Entidade]}
            />
        </div>
    );
}
```

## 6. Colunas (`app/cadastros/[nome_entidades]/columns.tsx`)

```typescript
import { ColumnDef } from "@tanstack/react-table";
import { [Nome_Entidade] } from "@/types/[nome_entidade]";
import { formatarData } from "@/lib/utils";
import { TableActions } from "@/components/ui/table-actions";

export const columns: ColumnDef<[Nome_Entidade]>[] = [
    {
        accessorKey: "nome",
        header: "Nome",
    },
    // Colunas específicas da entidade
    // Exemplo da implementação de Pacientes:
    // {
    //     accessorKey: "cpf",
    //     header: "CPF",
    // },
    // {
    //     accessorKey: "data_nascimento",
    //     header: "Data de Nascimento",
    //     cell: ({ row }) => formatarData(row.original.data_nascimento),
    // },
    {
        accessorKey: "created_at",
        header: "Data de Criação",
        cell: ({ row }) => formatarData(row.original.created_at),
    },
    {
        id: "actions",
        cell: ({ row }) => (
            <TableActions
                item={row.original}
                onEdit={(item) => onEdit(item)}
            />
        ),
    },
];
```

## 7. Importante: Manipulação de Datas

Para garantir a correta manipulação de datas entre frontend e backend:

1. Ao enviar datas para o backend:

```typescript
import { formatDateToISO } from "@/lib/utils";

// Antes de enviar para o backend
const dataFormatada = formatDateToISO(data);
```

2. Ao receber datas do backend:

```typescript
import { formatarData } from "@/lib/utils";

// Ao exibir a data
const dataExibicao = formatarData(data);
```

3. Nos tipos TypeScript, sempre declare campos de data como string:

```typescript
export interface [Nome_Entidade] {
    data_nascimento: string;
    created_at: string;
    updated_at: string;
    deleted_at: string | null;
}
```

4. Em formulários com DatePicker:

```typescript
import { DatePicker } from "@/components/ui/date-picker";
import { formatarData, formatDateToISO } from "@/lib/utils";

// No formulário
<DatePicker
    value={data}
    onChange={(newDate) => {
        // Ao salvar, converte para ISO
        const isoDate = formatDateToISO(newDate);
        // ... lógica de salvamento
    }}
/>

// Ao exibir
<span>{formatarData(data)}</span>
```

### Observações Importantes:

1. **Organização dos Serviços**:

   - Cada entidade deve ter seu próprio arquivo de serviço (ex: `pacienteService.ts`, `fichaService.ts`)
   - O arquivo `api.ts` deve conter apenas configurações e funções compartilhadas
   - Use a função `getCurrentUserId()` do `api.ts` para obter o ID do usuário autenticado
2. **Campos de Auditoria**:

   - Crie uma interface que estenda o FormData para incluir os campos de auditoria
   - `created_by`: incluído apenas na criação de novos registros
   - `updated_by`: incluído em todas as operações de criação e atualização
   - Nunca envie `created_by` em operações de atualização
3. **Tratamento de Erros**:

   - Implemente tratamento específico para erros de autenticação
   - Use mensagens de erro específicas para cada operação
   - Mantenha logs detalhados no console para depuração
4. **Boas Práticas**:

   - Use tipagem forte em todas as interfaces e funções
   - Mantenha a lógica de negócios nos serviços
   - Centralize a lógica de autenticação
   - Use mensagens toast para feedback ao usuário
   - Atualize o cache do React Query após operações de sucesso

## 8. Campos Relacionados no Frontend

### 8.1 Tipos com Campos Relacionados

Quando uma entidade possui campos de outras entidades relacionadas, defina os tipos assim:

```typescript
export interface Guia {
    id: string;
    numero_guia: string;
    // ... outros campos da guia ...
    
    // Campos relacionados
    paciente_nome?: string;
    carteirinha_numero?: string;
    
    // Campos de auditoria
    created_at: string;
    updated_at: string;
    created_by?: string;
    updated_by?: string;
    deleted_at?: string;
}
```

### 8.2 Exibição em Tabelas

Para exibir campos relacionados nas tabelas:

```typescript
export const columns: ColumnDef<Guia>[] = [
    {
        accessorKey: "numero_guia",
        header: "Número da Guia",
    },
    {
        accessorKey: "paciente_nome",
        header: "Paciente",
    },
    {
        accessorKey: "carteirinha_numero",
        header: "Carteirinha",
    },
    // ... outras colunas
];
```

### 8.3 Pontos Importantes

1. **Tipagem**:
   - Sempre declare campos relacionados como opcionais (`?`)
   - Mantenha a consistência com os nomes do backend
   - Documente os campos relacionados

2. **Componentes**:
   - Use componentes de exibição apropriados para cada tipo de dado
   - Trate casos onde dados relacionados são nulos
   - Implemente fallbacks adequados

3. **Serviços**:
   - Os serviços devem esperar e tratar campos relacionados
   - Mantenha a tipagem consistente em todas as operações
   - Documente comportamentos especiais

4. **Performance**:
   - Considere o impacto de joins nos tempos de carregamento
   - Implemente paginação quando necessário
   - Use caching apropriadamente
