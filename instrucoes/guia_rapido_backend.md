# Guia Rápido - Backend

## 1. Configuração Inicial

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais
```

## 2. Estrutura Básica

```python
# routes/[entidade].py
from fastapi import APIRouter, HTTPException
from typing import Optional
from ..models.[entidade] import [Entidade]Create, [Entidade]Update
from ..services.[entidade]_service import [Entidade]Service

router = APIRouter()
service = [Entidade]Service()

@router.get("/")
async def list_[entidades]():
    return await service.list_[entidades]()

@router.post("/")
async def create_[entidade](data: [Entidade]Create):
    return await service.create_[entidade](data)
```

## 3. Modelos

```python
# models/[entidade].py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class [Entidade]Base(BaseModel):
    nome: str = Field(..., min_length=2)
    ativo: bool = True
    
class [Entidade]Create([Entidade]Base):
    pass

class [Entidade]Update([Entidade]Base):
    nome: Optional[str] = None
    ativo: Optional[bool] = None
```

## 4. Serviços

```python
# services/[entidade]_service.py
from typing import Dict, List
from fastapi import HTTPException
from ..models.[entidade] import [Entidade]Create, [Entidade]Update
from ..repositories.[entidade]_repository import [Entidade]Repository

class [Entidade]Service:
    def __init__(self):
        self.repository = [Entidade]Repository()

    async def list_[entidades](self) -> List[Dict]:
        try:
            return await self.repository.list_[entidades]()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
```

## 5. Repositórios

```python
# repositories/[entidade]_repository.py
from typing import Dict, List
from ..database_supabase import get_supabase_client

class [Entidade]Repository:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def list_[entidades](self) -> List[Dict]:
        try:
            result = self.supabase.table("[entidades]").select("*").execute()
            return result.data
        except Exception as e:
            raise Exception(f"Erro ao listar [entidades]: {str(e)}")
```

## 6. Comandos Úteis

```bash
# Executar servidor
uvicorn app:app --reload

# Executar testes
pytest

# Gerar dados de teste
python -m backend.scripts.gerar_dados_teste
```

## 7. Endpoints Padrão

- `GET /api/[entidade]s/`: Listar
- `POST /api/[entidade]s/`: Criar
- `GET /api/[entidade]s/{id}/`: Detalhar
- `PUT /api/[entidade]s/{id}/`: Atualizar
- `DELETE /api/[entidade]s/{id}/`: Remover

## 8. Validações Comuns

```python
from pydantic import Field, validator

# Campo obrigatório
nome: str = Field(..., min_length=2)

# Campo opcional
descricao: Optional[str] = None

# Validador customizado
@validator("cpf")
def validar_cpf(cls, v):
    if not v.isdigit() or len(v) != 11:
        raise ValueError("CPF inválido")
    return v
```

## 9. Tratamento de Erros

```python
try:
    result = await service.operation()
    return StandardResponse(success=True, data=result)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

## 10. Autenticação

```python
from fastapi import Depends
from ..utils.auth import get_current_user

@router.get("/", dependencies=[Depends(get_current_user)])
async def protected_route():
    return {"message": "Rota protegida"}
```

## 11. Logs

```python
import logging

logger = logging.getLogger(__name__)

try:
    logger.info("Iniciando operação")
    result = await operation()
    logger.info(f"Operação concluída: {result}")
except Exception as e:
    logger.error(f"Erro: {str(e)}")
    raise
```

## 12. Serialização de Datas

```python
# 1. Importe as utilidades de data
from ..utils.date_utils import DateEncoder, format_date_fields, DATE_FIELDS

# 2. No serviço, serialize datas para JSON
async def update_entity(self, id: UUID, entity: EntityUpdate):
    try:
        result = await self.repository.update(id, entity)
        # Serializa datas para JSON
        if result:
            result = json.loads(json.dumps(result, cls=DateEncoder))
        return result
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise

# 3. No repositório, formate datas antes de enviar para o banco
async def update(self, id: UUID, entity: EntityUpdate):
    try:
        data = entity.model_dump(exclude_unset=True)
        # Formata datas para ISO
        formatted_data = format_date_fields(data, DATE_FIELDS)
        result = self.db.from_(self.table).update(formatted_data).eq("id", str(id)).execute()
        if result.data:
            # Formata datas na resposta
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise

# 4. Adicione campos de data à lista DATE_FIELDS
# Em utils/date_utils.py
DATE_FIELDS = [
    'data_nascimento',
    'created_at',
    'updated_at',
    'deleted_at',
    'data_nova_entidade'  # Adicione seu campo aqui
]
```

## 13. Dicas Rápidas

1. Use tipos explícitos sempre que possível
2. Documente funções complexas
3. Mantenha endpoints RESTful
4. Valide dados na entrada
5. Use async/await consistentemente
6. Mantenha logs informativos
7. Trate exceções adequadamente
8. Siga o padrão de projeto existente 