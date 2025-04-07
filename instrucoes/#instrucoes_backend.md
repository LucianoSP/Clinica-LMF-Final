# Prompt para Geração de Backend FastAPI

## 1. Modelo Base (`models/[nome_entidade].py`)

```python
from datetime import datetime, date
from typing import Optional, Union
from pydantic import BaseModel, field_validator
import json

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class [Nome_Entidade]Base(BaseModel):
    """Modelo base para [Nome_Entidade]"""
    nome: str
    # Campos específicos da entidade
    # Exemplo da implementação de Pacientes:
    # cpf: Optional[str] = None
    # rg: Optional[str] = None
    # data_nascimento: Optional[date] = None
    # telefone: Optional[str] = None
    # email: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            date: lambda v: v.isoformat() if isinstance(v, date) else v,
            datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
        }
    }
    
    def model_dump_json(self, **kwargs):
        """Sobrescreve o método model_dump_json para garantir serialização correta de datas"""
        kwargs.setdefault("cls", DateEncoder)
        return super().model_dump_json(**kwargs)

class [Nome_Entidade]Create([Nome_Entidade]Base):
    """Modelo para criação de [Nome_Entidade]"""
    created_by: str
    updated_by: str

    @field_validator("created_by", "updated_by")
    def validate_user_id(cls, v: str) -> str:
        if not v:
            raise ValueError("ID do usuário é obrigatório")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "nome": "Exemplo",
                "created_by": "user-id-123",
                "updated_by": "user-id-123"
            }
        }
    }

class [Nome_Entidade]Update([Nome_Entidade]Base):
    """Modelo para atualização de [Nome_Entidade]"""
    updated_by: str

    @field_validator("updated_by")
    def validate_updated_by(cls, v: str) -> str:
        if not v:
            raise ValueError("ID do usuário que está atualizando é obrigatório")
        return v

class [Nome_Entidade]([Nome_Entidade]Base):
    """Modelo completo de [Nome_Entidade]"""
    id: str
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None

    model_config = {
        "from_attributes": True
    }
```

# Guia Detalhado de Serialização de Datas no Sistema

## Problema Comum: "Object of type datetime is not JSON serializable"

Este erro ocorre frequentemente quando objetos `datetime` ou `date` não são serializados corretamente antes de enviar para o Supabase ou converter para JSON. Ao contrário de tipos primitivos como `str` ou `int`, objetos `datetime` não podem ser convertidos diretamente para JSON.

### Sintomas comuns:

1. Erro ao enviar dados para o Supabase: `TypeError: Object of type datetime is not JSON serializable`
2. Erros de API ao retornar respostas com datas
3. Falhas na importação de dados entre sistemas
4. Quebra na exibição de datas no frontend

## Solução Abrangente para Serialização de Datas

Para garantir que todas as datas sejam sempre serializadas corretamente, aplicamos uma estratégia em múltiplas camadas:

### 1. Classe DateEncoder

Implementada em `utils/date_utils.py`, esta classe estende o `json.JSONEncoder` para lidar corretamente com objetos de data:

```python
class DateEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)
```

### 2. Formatação Explícita de Campos de Data

Usamos as funções auxiliares:

```python
def format_date(value: Union[date, datetime, T]) -> Union[str, T]:
    """Converte date ou datetime para string ISO se necessário"""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return cast(T, value)

def format_date_fields(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Formata campos de data em um dicionário para string ISO"""
    result = dict(data)
    for field in fields:
        if field in result:
            result[field] = format_date(result[field])
    return result
```

### 3. Modelos Pydantic com Configuração para Datas

Todos os modelos Pydantic devem implementar:

```python
model_config = {
    "from_attributes": True,
    "json_encoders": {
        date: lambda v: v.isoformat() if isinstance(v, date) else v,
        datetime: lambda v: v.isoformat() if isinstance(v, datetime) else v
    }
}

def model_dump_json(self, **kwargs):
    """Sobrescreve o método model_dump_json para garantir serialização correta de datas"""
    kwargs.setdefault("cls", DateEncoder)
    return super().model_dump_json(**kwargs)
```

### 4. Verificação Explícita de Serialização nos Repositórios

Em todos os métodos de repositório que enviam dados para o Supabase, fazer uma verificação explícita:

```python
# Verificar serialização antes de enviar ao banco
try:
    # Testar serialização
    json.dumps(formatted_data)
except TypeError:
    # Se falhar, usar o DateEncoder para serializar
    formatted_data = json.loads(json.dumps(formatted_data, cls=DateEncoder))
```

### 5. Lista Centralizada de Campos de Data

Mantemos uma lista centralizada em `utils/date_utils.py`:

```python
DATE_FIELDS = [
    'data_nascimento',
    'avaliacao_luria_data_inicio_treinamento',
    'created_at',
    'updated_at',
    'deleted_at',
    'data_validade',
    'data_inicio',
    'data_fim',
    'data_atendimento'
]
```

**IMPORTANTE**: Sempre atualize esta lista quando criar novos campos de data em qualquer entidade!

## Onde Aplicar o Tratamento de Datas

### 1. Repositórios

Em TODOS os métodos que enviam dados para o Supabase:

```python
async def create(self, entity: EntityCreate):
    try:
        data = entity.model_dump()
        # Formata as datas
        formatted_data = format_date_fields(data, DATE_FIELDS)
        
        # Verifica a serialização
        try:
            json.dumps(formatted_data)
        except TypeError:
            formatted_data = json.loads(json.dumps(formatted_data, cls=DateEncoder))
        
        result = self.db.from_(self.table).insert(formatted_data).execute()
        # ...
```

### 2. Serviços

Adicione verificação de serialização na camada de serviço para operações complexas:

```python
async def create_entity(self, entity: EntityCreate):
    try:
        # Verifica serialização
        try:
            json.dumps(entity.model_dump())
        except TypeError:
            # Recria o objeto através da serialização/desserialização
            entity_dict = json.loads(json.dumps(entity.model_dump(), cls=DateEncoder))
            entity = EntityCreate.model_validate(entity_dict)
            
        return await self.repository.create(entity)
    except Exception as e:
        # ...
```

### 3. Importação de Dados

Casos especiais, como importação de dados externos, requerem cuidado extra:

```python
# Garantir que não há objetos datetime diretos
try:
    # Testar serialização
    json.dumps(data)
except TypeError:
    # Se falhar, usar o DateEncoder para serializar
    data = json.loads(json.dumps(data, cls=DateEncoder))
```

## Checklist para Evitar Erros de Serialização

✅ Todos os modelos Pydantic têm configuração `json_encoders` para datas  
✅ Repositórios usam `format_date_fields` em todos os métodos CRUD  
✅ Verificação explícita de serialização antes de enviar dados para o Supabase  
✅ Lista `DATE_FIELDS` atualizada com todos os campos de data  
✅ Método `model_dump_json` sobrescrito nos modelos base  
✅ Importação e operação em lote fazem verificação de serialização  

## Como Depurar Problemas de Serialização

1. **Identifique o objeto problemático**: O erro geralmente indica qual tipo de objeto não pode ser serializado
2. **Verifique se o campo está em DATE_FIELDS**: Se não estiver, adicione-o
3. **Teste a serialização explicitamente**:

```python
try:
    json.dumps(seu_objeto)
    print("Objeto serializável")
except TypeError as e:
    print(f"Erro de serialização: {str(e)}")
    # Use DateEncoder para verificar
    result = json.loads(json.dumps(seu_objeto, cls=DateEncoder))
    print("Objeto serializado:", result)
```

4. **Inspecione entradas de log**: Procure por erros que mencionem "JSONEncoder" ou "serializable"

## Abordagem para Imports e Migrações

Em operações de importação em massa ou migração de dados:

1. **Pré-processamento**: Converta todas as datas para strings ISO antes de enviar
2. **Rastreamento de campos de data**: Crie uma lista específica para campos de data do sistema externo
3. **Testes incrementais**: Teste a importação com poucos registros antes de processar tudo
4. **Validação de saída**: Verifique se o resultado final contém apenas strings ISO para datas

Seguindo este guia, você garantirá que a aplicação não sofra com problemas de serialização de datas, evitando erros comuns e garantindo a consistência dos dados.

## 2. Repositório (`repositories/[nome_entidade].py`)

```python
from uuid import UUID
from typing import Optional, Dict
from database_supabase import SupabaseClient
from ..models.[nome_entidade] import [Nome_Entidade]Create, [Nome_Entidade]Update
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import logging

logger = logging.getLogger(__name__)

class [Nome_Entidade]Repository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "[nome_entidade]s"

    async def list(self,
                  offset: int = 0,
                  limit: int = 100,
                  search: Optional[str] = None,
                  order_column: str = "nome",
                  order_direction: str = "asc") -> Dict:
        try:
            # Query base
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            # Adiciona busca se fornecida
            if search:
                query = query.or_(f"nome.ilike.%{search}%")

            # Adiciona ordenação
            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)

            # Aplica paginação
            query = query.range(offset, offset + limit - 1)
            result = query.execute()

            # Query para contagem total (IMPORTANTE: usar count="exact" para Supabase)
            count_result = (
                self.db.from_(self.table)
                .select("id", count="exact")
                .is_("deleted_at", "null")
                .execute()
            )

            # Formata as datas
            items = [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

            return {
                "items": items,
                "total": count_result.count if hasattr(count_result, 'count') else 0,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Erro ao listar {self.table}: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def create(self, [nome_entidade]: [Nome_Entidade]Create):
        try:
            logger.info(f"Criando [nome_entidade] pelo usuário: {[nome_entidade].created_by}")
            data = [nome_entidade].model_dump()
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                logger.info(f"[Nome_Entidade] criado com sucesso. ID: {result.data[0]['id']}")
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao criar [nome_entidade]. Usuário: {[nome_entidade].created_by}. Erro: {str(e)}")
            raise

    async def update(self, id: UUID, [nome_entidade]: [Nome_Entidade]Update):
        try:
            logger.info(f"Atualizando [nome_entidade] {id} pelo usuário: {[nome_entidade].updated_by}")
            # Verifica se o registro existe e não está deletado
            existing = await self.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="[Nome_Entidade] não encontrado")
            
            # Não permite alterar campos de auditoria anteriores
            data = [nome_entidade].model_dump(exclude_unset=True)
            data.pop("created_by", None)  # Não permite alterar created_by
            data.pop("created_at", None)  # Não permite alterar created_at
            
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = await self.db.table(self.table).update(formatted_data).eq('id', str(id)).execute()
            if result.data:
                # Formata as datas na resposta
                logger.info(f"[Nome_Entidade] {id} atualizado com sucesso")
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar [nome_entidade] {id}. Usuário: {[nome_entidade].updated_by}. Erro: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table).update({"deleted_at": "now()"}).eq("id", str(id)).is_("deleted_at", "null").execute()
        return bool(result.data)
```

## 3. Serviço (`services/[nome_entidade].py`)

```python
from datetime import datetime, UTC
from typing import Dict, Optional
from uuid import UUID
from fastapi import HTTPException
from ..models.[nome_entidade] import [Nome_Entidade]Create, [Nome_Entidade]Update, [Nome_Entidade]
from ..repositories.[nome_entidade] import [Nome_Entidade]Repository
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import logging

logger = logging.getLogger(__name__)

class [Nome_Entidade]Service:
    def __init__(self, repository: [Nome_Entidade]Repository):
        self.repository = repository

    async def list_[nome_entidade]s(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "nome",
        order_direction: str = "asc"
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction
            )
            
            return {
                "items": [[Nome_Entidade].model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar [nome_entidade]s: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar [nome_entidade]s: {str(e)}"
            )

    async def get_[nome_entidade](self, id: UUID) -> Optional[[Nome_Entidade]]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="[Nome_Entidade] não encontrado")
            return [Nome_Entidade].model_validate(result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar [nome_entidade]: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar [nome_entidade]: {str(e)}"
            )

    async def create_[nome_entidade](self, [nome_entidade]: [Nome_Entidade]Create) -> [Nome_Entidade]:
        try:
            result = await self.repository.create([nome_entidade])
            if not result:
                raise HTTPException(
                    status_code=500,
                    detail="Erro ao criar [nome_entidade]"
                )
            return [Nome_Entidade].model_validate(result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar [nome_entidade]: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar [nome_entidade]: {str(e)}"
            )

    async def update_[nome_entidade](self, id: UUID, [nome_entidade]: [Nome_Entidade]Update) -> [Nome_Entidade]:
        try:
            result = await self.repository.update(id, [nome_entidade])
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="[Nome_Entidade] não encontrado"
                )
            return [Nome_Entidade].model_validate(result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar [nome_entidade]: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar [nome_entidade]: {str(e)}"
            )

    async def delete_[nome_entidade](self, id: UUID) -> bool:
        try:
            return await self.repository.delete(id)
        except Exception as e:
            logger.error(f"Erro ao deletar [nome_entidade]: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar [nome_entidade]: {str(e)}"
            )
```

## 4. Rotas (`routes/[nome_entidade].py`)

```python
from fastapi import APIRouter, HTTPException, Query, Path, status, Depends
from typing import Optional
import logging
from uuid import UUID
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..models.[nome_entidade] import [Nome_Entidade], [Nome_Entidade]Create, [Nome_Entidade]Update
from ..services.[nome_entidade] import [Nome_Entidade]Service
from ..repositories.[nome_entidade] import [Nome_Entidade]Repository
from database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_[nome_entidade]_repository(
    db: SupabaseClient = Depends(get_supabase_client),
) -> [Nome_Entidade]Repository:
    return [Nome_Entidade]Repository(db)

def get_[nome_entidade]_service(
    repository: [Nome_Entidade]Repository = Depends(get_[nome_entidade]_repository),
) -> [Nome_Entidade]Service:
    return [Nome_Entidade]Service(repository)

@router.get("",
            response_model=PaginatedResponse[[Nome_Entidade]],
            summary="Listar [Nome_Entidade]s",
            description="Retorna uma lista paginada de [nome_entidade]s")
async def list_[nome_entidade]s(
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    order_column: str = Query("nome", description="Coluna para ordenação"),
    order_direction: str = Query("asc", description="Direção da ordenação (asc ou desc)"),
    service: [Nome_Entidade]Service = Depends(get_[nome_entidade]_service)
):
    try:
        logger.info(f"Recebendo requisição GET /[nome_entidade]s")
        logger.debug(f"Parâmetros: offset={offset}, limit={limit}, search={search}, order_column={order_column}, order_direction={order_direction}")
        
        result = await service.list_[nome_entidade]s(
            offset=offset,
            limit=limit,
            search=search,
            order_column=order_column,
            order_direction=order_direction
        )
        
        return PaginatedResponse(
            success=True,
            message="[Nome_Entidade]s listados com sucesso",
            **result
        )
    except Exception as e:
        logger.error(f"Erro ao listar [nome_entidade]s: {str(e)}")
        raise

@router.get("/{id}",
            response_model=StandardResponse[[Nome_Entidade]],
            summary="Obter [Nome_Entidade]",
            description="Retorna um [nome_entidade] específico pelo ID")
async def get_[nome_entidade](
    id: UUID = Path(..., description="ID do [nome_entidade]"),
    service: [Nome_Entidade]Service = Depends(get_[nome_entidade]_service)
):
    try:
        logger.info(f"Recebendo requisição GET /[nome_entidade]s/{id}")
        result = await service.get_[nome_entidade](id)
        return StandardResponse(
            success=True,
            data=result,
            message="[Nome_Entidade] encontrado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao buscar [nome_entidade]: {str(e)}")
        raise

@router.post("",
            response_model=StandardResponse[[Nome_Entidade]],
            status_code=status.HTTP_201_CREATED,
            summary="Criar [Nome_Entidade]",
            description="Cria um novo [nome_entidade]")
async def create_[nome_entidade](
    [nome_entidade]: [Nome_Entidade]Create,
    service: [Nome_Entidade]Service = Depends(get_[nome_entidade]_service)
):
    try:
        logger.info(f"Recebendo requisição POST /[nome_entidade]s")
        logger.debug(f"Payload recebido: {[nome_entidade].model_dump()}")
        
        result = await service.create_[nome_entidade]([nome_entidade])
        return StandardResponse(
            success=True,
            data=result,
            message="[Nome_Entidade] criado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao criar [nome_entidade]: {str(e)}")
        raise

@router.put("/{id}",
            response_model=StandardResponse[[Nome_Entidade]],
            summary="Atualizar [Nome_Entidade]",
            description="Atualiza um [nome_entidade] existente")
async def update_[nome_entidade](
    id: UUID = Path(..., description="ID do [nome_entidade]"),
    [nome_entidade]: [Nome_Entidade]Update,
    service: [Nome_Entidade]Service = Depends(get_[nome_entidade]_service)
):
    try:
        logger.info(f"Recebendo requisição PUT /[nome_entidade]s/{id}")
        logger.debug(f"Payload recebido: {[nome_entidade].model_dump()}")
        
        result = await service.update_[nome_entidade](id, [nome_entidade])
        return StandardResponse(
            success=True,
            data=result,
            message="[Nome_Entidade] atualizado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar [nome_entidade]: {str(e)}")
        raise

@router.delete("/{id}",
            response_model=StandardResponse[bool],
            summary="Deletar [Nome_Entidade]",
            description="Deleta (soft delete) um [nome_entidade] existente")
async def delete_[nome_entidade](
    id: UUID = Path(..., description="ID do [nome_entidade]"),
    service: [Nome_Entidade]Service = Depends(get_[nome_entidade]_service)
):
    try:
        logger.info(f"Recebendo requisição DELETE /[nome_entidade]s/{id}")
        result = await service.delete_[nome_entidade](id)
        return StandardResponse(
            success=True,
            data=result,
            message="[Nome_Entidade] deletado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao deletar [nome_entidade]: {str(e)}")
        raise
```

## 5. Funções RPC no Supabase

### 5.1 Criando Funções RPC

Para criar funções RPC no Supabase que retornam dados com joins ou lógica complexa:

```sql
CREATE OR REPLACE FUNCTION nome_funcao(
    -- Parâmetros de entrada
    p_offset int,
    p_limit int,
    p_search text,
    -- Outros parâmetros...
)
RETURNS TABLE (
    -- Definição das colunas retornadas
    id uuid,
    nome text,
    -- Colunas relacionadas
    paciente_nome text,
    carteirinha_numero text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.*,  -- Colunas da tabela principal
        r.campo as campo_relacionado  -- Campos de outras tabelas
    FROM tabela_principal t
    LEFT JOIN tabela_relacionada r ON t.id = r.tabela_principal_id
    WHERE t.deleted_at IS NULL
        AND (p_search IS NULL OR t.nome ILIKE '%' || p_search || '%')
    ORDER BY t.created_at DESC
    OFFSET p_offset
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

### 5.2 Usando Funções RPC no Repository

Para chamar funções RPC no repository:

```python
async def list(self,
              offset: int = 0,
              limit: int = 100,
              search: Optional[str] = None) -> Dict:
    try:
        # Prepara os parâmetros para a função RPC
        params = {
            'p_offset': offset,
            'p_limit': limit,
            'p_search': search
        }

        # Executa a função RPC
        result = self.db.rpc('nome_funcao', params).execute()

        items = [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

        return {
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Erro ao listar itens: {str(e)}")
        raise
```

### 5.3 Boas Práticas

1. **Nomenclatura**:
   - Use prefixo `p_` para parâmetros de entrada
   - Use nomes descritivos para as funções
   - Mantenha consistência com o nome das tabelas

2. **Segurança**:
   - Sempre inclua `deleted_at IS NULL` nos filtros
   - Faça validação de tipos nos parâmetros
   - Use prepared statements (o Supabase faz isso automaticamente)

3. **Performance**:
   - Adicione índices para campos usados em JOINs e WHERE
   - Use EXPLAIN ANALYZE para otimizar queries
   - Limite o número de registros retornados

4. **Manutenção**:
   - Documente o propósito de cada função
   - Mantenha as funções em arquivos SQL separados
   - Versione as alterações no controle de código

### 5.4 Exemplo Real: Guias com Detalhes

```sql
-- Função para listar guias com detalhes do paciente e carteirinha
CREATE OR REPLACE FUNCTION listar_guias_com_detalhes(
    p_offset int,
    p_limit int,
    p_search text,
    p_status text,
    p_carteirinha_id text,
    p_paciente_id text
)
RETURNS TABLE (
    -- Colunas da guia
    id uuid,
    numero_guia text,
    status text,
    -- Colunas relacionadas
    paciente_nome text,
    carteirinha_numero text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.*,
        p.nome as paciente_nome,
        c.numero_carteirinha
    FROM guias g
    LEFT JOIN pacientes p ON g.paciente_id = p.id
    LEFT JOIN carteirinhas c ON g.carteirinha_id = c.id
    WHERE g.deleted_at IS NULL
        AND (p_search IS NULL OR 
             g.numero_guia ILIKE '%' || p_search || '%')
        AND (p_status IS NULL OR g.status = p_status)
        AND (p_carteirinha_id IS NULL OR 
             g.carteirinha_id::text = p_carteirinha_id)
        AND (p_paciente_id IS NULL OR 
             g.paciente_id::text = p_paciente_id);
END;
$$ LANGUAGE plpgsql;
```

## 6. Rotas com Autenticação (`routes/[nome_entidade].py`)

```python
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies.auth import get_current_user
from ..models.[nome_entidade] import [Nome_Entidade], [Nome_Entidade]Create, [Nome_Entidade]Update
from ..repositories.[nome_entidade] import [Nome_Entidade]Repository
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(redirect_slashes=False)

@router.post("/api/[nome_entidades]", response_model=StandardResponse[[Nome_Entidade]])
async def criar_[nome_entidade](
    [nome_entidade]: [Nome_Entidade]Create,
    current_user: str = Depends(get_current_user),
    db = Depends(get_db)
) -> StandardResponse[[Nome_Entidade]]:
    """
    Cria um novo [nome_entidade].
    Requer autenticação.
    """
    try:
        repository = [Nome_Entidade]Repository(db)
        # current_user já contém o ID do usuário autenticado
        [nome_entidade].created_by = current_user
        [nome_entidade].updated_by = current_user
        result = await repository.create([nome_entidade])
        return StandardResponse(
            success=True,
            message="[Nome_Entidade] criado com sucesso",
            data=result
        )
    except Exception as e:
        logger.error(f"Erro ao criar [nome_entidade]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/[nome_entidades]/{id}", response_model=StandardResponse[[Nome_Entidade]])
async def atualizar_[nome_entidade](
    id: str,
    [nome_entidade]: [Nome_Entidade]Update,
    current_user: str = Depends(get_current_user),
    db = Depends(get_db)
) -> StandardResponse[[Nome_Entidade]]:
    """
    Atualiza um [nome_entidade] existente.
    Requer autenticação.
    """
    try:
        repository = [Nome_Entidade]Repository(db)
        # Atualiza o campo updated_by com o ID do usuário atual
        [nome_entidade].updated_by = current_user
        result = await repository.update(id, [nome_entidade])
        return StandardResponse(
            success=True,
            message="[Nome_Entidade] atualizado com sucesso",
            data=result
        )
    except Exception as e:
        logger.error(f"Erro ao atualizar [nome_entidade]: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 7. Autenticação com Supabase

A autenticação é gerenciada diretamente pelo Supabase Auth. Não há manipulação manual de tokens JWT no backend.

```python
# O Supabase gerencia automaticamente:
# - Autenticação de usuários
# - Refresh de tokens
# - Sessões
# - Políticas de acesso ao banco de dados
```

### Proteção de Rotas

As rotas são protegidas através das políticas de segurança do Supabase:

```sql
-- Exemplo de política de segurança no Supabase
CREATE POLICY "Usuários autenticados podem ler" ON public.pacientes
    FOR SELECT
    TO authenticated
    USING (true);
```

### Campos de Auditoria

Os campos de auditoria são preenchidos automaticamente usando o ID do usuário do Supabase:

```python
class [Nome_Entidade]Create([Nome_Entidade]Base):
    created_by: str  # ID do usuário do Supabase
    updated_by: str  # ID do usuário do Supabase

    @field_validator("created_by", "updated_by")
    def validate_user_id(cls, v: str) -> str:
        if not v:
            raise ValueError("ID do usuário é obrigatório")
        return v
```

### Boas Práticas de Segurança

1. **Autenticação**:
   - Use o cliente Supabase para todas as operações de autenticação
   - Nunca implemente sua própria lógica de autenticação
   - Mantenha as políticas de segurança do Supabase atualizadas

2. **Auditoria**:
   - Sempre inclua `created_by` e `updated_by` nas operações
   - Use o ID do usuário do Supabase para rastreamento
   - Mantenha logs detalhados de todas as operações

3. **Segurança**:
   - Configure corretamente as políticas RLS no Supabase
   - Use HTTPS para todas as comunicações
   - Implemente validações adequadas nos modelos

## Pontos Importantes:

1. **Tratamento de Datas**:

   - Usar `format_date_fields` para formatar datas
   - Manter lista atualizada de `DATE_FIELDS`
   - Usar ISO format para datas
2. **Logs**:

   - Implementar logs em todos os níveis
   - Incluir dados relevantes nos logs
   - Usar try/except com logs de erro
3. **Validação**:

   - Usar Pydantic para validação
   - Tratar ValidationError separadamente
   - Retornar erros detalhados
4. **Campos de Auditoria**:

   - `created_by` e `updated_by` obrigatórios
   - Validar presença dos campos
   - Manter exemplo no schema
5. **Respostas Padronizadas**:

   - Usar StandardResponse
   - Usar PaginatedResponse para listas
   - Incluir mensagens claras
6. **Boas Práticas**:

   - Separar responsabilidades
   - Usar injeção de dependências
   - Documentar endpoints
   - Manter logs consistentes

## Serialização de Modelos Pydantic

Para garantir a correta serialização dos modelos Pydantic em toda a aplicação:

1. **Fluxo de Dados**:

   - Frontend envia dados para o serviço
   - Serviço recebe como modelo Pydantic (Create ou Update)
   - Serviço passa o modelo Pydantic para o repositório
   - Repositório converte o modelo para dicionário usando `model_dump()`
   - Banco de dados recebe um dicionário puro
2. **Regras Importantes**:

   - NUNCA converta o modelo para dicionário no serviço
   - SEMPRE use `model_dump()` no repositório antes de enviar para o banco
   - NUNCA passe dicionários puros entre camadas, use os modelos Pydantic
   - SEMPRE use a função `format_date_fields` após receber dados do banco
   - SEMPRE use o `DateEncoder` ao serializar respostas que contêm datas
   
3. **Tratamento de Datas**:

   - Adicione todos os campos de data à lista `DATE_FIELDS` em `utils/date_utils.py`
   - No serviço, use `json.loads(json.dumps(result, cls=DateEncoder))` para serializar datas
   - No repositório, use `format_date_fields(data, DATE_FIELDS)` antes de enviar para o banco
   - No repositório, use `format_date_fields(result.data[0], DATE_FIELDS)` ao receber do banco
   - Nos modelos Pydantic, configure `json_encoders` para serializar datas corretamente

4. **Erros Comuns e Soluções**:

   - Erro "Object of type date is not JSON serializable": Use `DateEncoder` no serviço
   - Erro "object APIResponse can't be used in 'await' expression": Use `from_` em vez de `table` com `await`
   - Inconsistência na formatação de datas: Verifique se o campo está na lista `DATE_FIELDS`

5. **Exemplo de Fluxo Correto**:

```python
# Service
async def update_entity(self, id: UUID, entity: EntityUpdate) -> Optional[Dict]:
    try:
        result = await self.repository.update(id, entity)
        # Garantir que as datas sejam serializadas corretamente
        if result:
            result = json.loads(json.dumps(result, cls=DateEncoder))
        return result
    except Exception as e:
        logger.error(f"Erro ao atualizar entidade: {str(e)}")
        raise

# Repository
async def update(self, id: UUID, entity: EntityUpdate) -> Optional[Dict]:
    try:
        data = entity.model_dump(exclude_unset=True)
        
        # Atualiza o timestamp
        data["updated_at"] = datetime.now().isoformat()
        
        # Formata as datas antes de enviar para o banco
        formatted_data = format_date_fields(data, DATE_FIELDS)
        
        result = (
            self.db.from_(self.table)
            .update(formatted_data)
            .eq("id", str(id))
            .execute()
        )
        if result.data:
            # Formata as datas na resposta
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None
    except Exception as e:
        logger.error(f"Erro ao atualizar entidade: {str(e)}")
        raise
```

6. **Checklist para Implementação**:

   - [ ] Adicionar campos de data à lista `DATE_FIELDS`
   - [ ] Implementar serialização JSON em todos os métodos do serviço
   - [ ] Usar `format_date_fields` em todos os métodos do repositório
   - [ ] Verificar consistência dos métodos (usar `from_` em vez de `table` com `await`)
   - [ ] Testar a serialização em todas as operações

## Instruções para Criação do Backend

### Estrutura do Projeto

O backend é construído usando FastAPI e Supabase, seguindo uma estrutura organizada em módulos:

```
backend/
├── routes/          # Rotas da API
├── schemas/         # Modelos Pydantic
└── utils/          # Utilitários
```

### Padrões de Código

#### 1. Formatação de Datas

Todas as datas na API são tratadas de forma padronizada:

- Datas são armazenadas no banco em formato UTC
- Datas são serializadas em formato ISO 8601 usando o `DateEncoder` global
- O arquivo `date_utils.py` contém funções utilitárias para manipulação de datas
- A função `format_date_fields` é usada para formatar campos de data em respostas JSON

Campos de data comuns na aplicação:

```python
DATE_FIELDS = [
    'data_nascimento',
    'data_atendimento',
    'data_execucao',
    'data_identificacao',
    'data_resolucao',
    'data_sessao',
    'data_inicio',
    'data_fim',
    'data_cadastro',
    'data_atualizacao',
    'data_inativacao',
    'created_at',
    'updated_at',
    'deleted_at'
]
```

#### 2. Campos de Auditoria

Todas as tabelas devem incluir os seguintes campos de auditoria:

```python
created_at: datetime      # Data de criação (automático)
updated_at: datetime      # Data de atualização (automático)
deleted_at: datetime      # Data de exclusão (soft delete)
created_by: str          # ID do usuário que criou
updated_by: str          # ID do usuário que atualizou
```

Regras para campos de auditoria:

- `created_by` é obrigatório na criação de registros
- `updated_by` é obrigatório na atualização de registros
- Nunca use IDs de usuário fixos ou hardcoded
- Os campos de data são atualizados automaticamente pelo Supabase

#### 3. Respostas da API

Todas as respostas seguem o padrão `StandardResponse`:

```python
{
    "success": bool,
    "message": str,
    "data": Any
}
```

O `DateEncoder` é aplicado globalmente para garantir que todas as datas sejam serializadas corretamente.

#### 4. Funções do Database

Funções de acesso ao banco devem seguir este padrão:

```python
async def list_items(
    supabase: SupabaseClient = Depends(get_supabase_client),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None,
    order_column: str = "created_at",
    order_direction: str = "desc"
):
    query = supabase.table('items').select('*').eq('deleted_at', None)
  
    # ... lógica de filtros ...
  
    return {
        'items': format_response_list(response.data),
        'total': total,
        'limit': limit,
        'offset': offset
    }

async def get_item(id: str, supabase: SupabaseClient = Depends(get_supabase_client)):
    result = await supabase.table('items').select('*').eq('id', id).single().execute()
    return format_response(result.data)

async def create_item(data: Dict, supabase: SupabaseClient = Depends(get_supabase_client)):
    result = await supabase.table('items').insert(data).execute()
    return format_response(result.data[0])

async def update_item(id: str, data: Dict, supabase: SupabaseClient = Depends(get_supabase_client)):
    result = await supabase.table('items').update(data).eq('id', id).execute()
    return format_response(result.data[0])
```

#### 5. Tratamento de Erros

Use try/except em todas as funções do database:

```python
try:
    result = await supabase.table('items').select('*').execute()
    return format_response_list(result.data)
except Exception as e:
    raise Exception(f"Erro ao buscar items: {str(e)}")
```

## 8. Requisitos Importantes para Joins e Detalhes

### 8.1 Modelos Pydantic com Campos Relacionados

Quando uma entidade precisa incluir dados de entidades relacionadas (ex: nome do paciente, número da carteirinha), é necessário:

1. Adicionar os campos relacionados ao modelo principal:

```python
class Guia(GuiaBase):
    """Modelo completo de Guia"""
    id: str
    created_at: Union[datetime, str]
    updated_at: Union[datetime, str]
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[Union[datetime, str]] = None
    # Campos de entidades relacionadas
    paciente_nome: Optional[str] = None
    carteirinha_numero: Optional[str] = None
```

### 8.2 Funções RPC para Joins

Para obter dados relacionados de forma eficiente, use funções RPC no Supabase:

```sql
CREATE OR REPLACE FUNCTION listar_entidade_com_detalhes(
    p_offset int,
    p_limit int,
    p_search text
)
RETURNS TABLE (
    -- Campos da entidade principal
    id uuid,
    nome text,
    -- Campos das entidades relacionadas
    entidade_relacionada_campo text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.*,  -- Campos da entidade principal
        er.campo as entidade_relacionada_campo  -- Campos relacionados
    FROM entidade e
    LEFT JOIN entidade_relacionada er ON e.entidade_relacionada_id = er.id
    WHERE e.deleted_at IS NULL
        AND (p_search IS NULL OR e.nome ILIKE '%' || p_search || '%');
END;
$$ LANGUAGE plpgsql;
```

### 8.3 Repositório com Suporte a Joins

O repositório deve chamar a função RPC e formatar os resultados:

```python
async def list(self, offset: int = 0, limit: int = 100, search: Optional[str] = None) -> Dict:
    try:
        params = {
            "p_offset": offset,
            "p_limit": limit,
            "p_search": search
        }
        
        result = await asyncio.to_thread(
            lambda: self.db.rpc("listar_entidade_com_detalhes", params).execute()
        )
        
        items = [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]
        
        return {
            "items": items,
            "total": len(items),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Erro ao listar entidades: {str(e)}")
        raise
```

### 8.4 Pontos Importantes

1. **Modelos Pydantic**:
   - Sempre declare campos opcionais para dados relacionados
   - Use tipos apropriados (geralmente `Optional[str]`)
   - Mantenha a documentação dos campos atualizada

2. **Funções RPC**:
   - Use LEFT JOIN para evitar perder registros principais
   - Inclua filtro de `deleted_at IS NULL` em todas as tabelas
   - Nomeie campos relacionados de forma clara (ex: `paciente_nome`)

3. **Repositório**:
   - Use `asyncio.to_thread` para chamadas RPC
   - Formate datas corretamente com `format_date_fields`
   - Trate erros adequadamente e mantenha logs

4. **Serviço e Rotas**:
   - Os modelos de resposta devem incluir os campos relacionados
   - A documentação da API deve refletir os campos adicionais
   - Mantenha a consistência na nomenclatura dos campos

# Instruções do Backend

## Estrutura do Projeto

```
backend/
├── config/                 # Configurações do projeto
│   ├── __init__.py
│   └── config.py          # Configurações globais e cliente Supabase
├── repositories/          # Camada de acesso a dados
│   ├── __init__.py
│   ├── database_supabase.py
│   ├── auditoria_repository.py
│   └── ...
├── services/             # Lógica de negócios
│   ├── __init__.py
│   ├── auditoria_service.py
│   └── ...
├── scripts/              # Scripts utilitários
│   ├── __init__.py
│   ├── gerar_dados_antigo.py
│   ├── gerar_dados_teste.py
│   └── gerar_dados_de_testes.py
└── app.py               # Aplicação FastAPI principal
```

## Configuração do Ambiente

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente no arquivo `.env`:
```
SUPABASE_URL=sua_url
SUPABASE_KEY=sua_chave
ANTHROPIC_API_KEY=sua_chave
```

## Executando o Projeto

1. Inicie o servidor FastAPI:
```bash
python -m backend.app
```

2. Acesse a documentação da API:
```
http://localhost:8000/docs
```

## Scripts de Teste

Para gerar dados de teste, você pode usar os seguintes comandos:

```bash
# Usando o script antigo
python -m backend.scripts.gerar_dados_antigo

# Usando o novo script
python -m backend.scripts.gerar_dados_teste

# Usando o script de testes detalhado
python -m backend.scripts.gerar_dados_de_testes
```

## Estrutura de Código

### Configurações (`config/`)
- `config.py`: Configurações globais usando Pydantic Settings
- Gerencia conexão com Supabase e variáveis de ambiente

### Repositórios (`repositories/`)
- Camada de acesso a dados
- Implementa operações CRUD com o Supabase
- Separa lógica de banco de dados da lógica de negócios

### Serviços (`services/`)
- Implementa a lógica de negócios
- Utiliza os repositórios para operações de dados
- Processa regras de negócio e validações

### Scripts (`scripts/`)
- Scripts utilitários para testes e desenvolvimento
- Geração de dados de teste
- Ferramentas de manutenção

## Boas Práticas

1. **Organização de Código**
   - Mantenha os arquivos organizados em suas respectivas pastas
   - Use imports relativos para referências internas
   - Siga o padrão de nomenclatura estabelecido

2. **Configurações**
   - Use variáveis de ambiente para configurações sensíveis
   - Mantenha as configurações centralizadas em `config.py`
   - Não hardcode valores sensíveis no código

3. **Acesso a Dados**
   - Use os repositórios para operações de banco de dados
   - Implemente tratamento de erros adequado
   - Mantenha queries SQL organizadas e documentadas

4. **Testes**
   - Use os scripts de teste para gerar dados de desenvolvimento
   - Mantenha os dados de teste consistentes
   - Documente casos de teste importantes

## Solução de Problemas

1. **Erros de Conexão**
   - Verifique as variáveis de ambiente
   - Teste a conexão com o Supabase
   - Verifique logs de erro

2. **Problemas com Scripts**
   - Execute com flag `-m` para imports relativos
   - Verifique dependências instaladas
   - Consulte logs de execução

3. **Erros de Banco de Dados**
   - Verifique permissões do Supabase
   - Confirme estrutura das tabelas
   - Valide dados de entrada

```

```

```
