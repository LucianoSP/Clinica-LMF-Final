from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..models.procedimento import ProcedimentoCreate, ProcedimentoUpdate, Procedimento
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.procedimento import ProcedimentoService
from ..repositories.procedimento import ProcedimentoRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_procedimento_repository(db: SupabaseClient = Depends(get_supabase_client)) -> ProcedimentoRepository:
    return ProcedimentoRepository(db)

def get_procedimento_service(repo: ProcedimentoRepository = Depends(get_procedimento_repository)) -> ProcedimentoService:
    return ProcedimentoService(repo)

@router.get("",
            response_model=PaginatedResponse[Procedimento],
            summary="Listar Procedimentos",
            description="Retorna uma lista paginada de procedimentos")
async def list_procedimentos(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    order_column: str = Query("nome", regex="^(nome|codigo|tipo|valor_total|created_at)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$"),
    tipo: Optional[str] = None,
    ativo: Optional[bool] = None,
    service: ProcedimentoService = Depends(get_procedimento_service)
):
    result = await service.list_procedimentos(
        limit=limit,
        offset=offset,
        search=search,
        order_column=order_column,
        order_direction=order_direction,
        tipo=tipo,
        ativo=ativo
    )
    
    return PaginatedResponse(
        success=True,
        items=result["items"],
        total=result["total"],
        page=(offset // limit) + 1,
        total_pages=ceil(result["total"] / limit),
        has_more=offset + limit < result["total"]
    )

@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de procedimentos está funcionando"}

@router.get("/{id}",
            response_model=StandardResponse[Procedimento],
            summary="Buscar Procedimento",
            description="Retorna os dados de um procedimento específico")
async def get_procedimento(
    id: UUID = Path(...),
    service: ProcedimentoService = Depends(get_procedimento_service)
):
    result = await service.get_procedimento(id)
    if not result:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    return StandardResponse(success=True, data=result)

@router.post("",
            response_model=StandardResponse[Procedimento],
            status_code=status.HTTP_201_CREATED,
            summary="Criar Procedimento",
            description="Cria um novo procedimento")
async def create_procedimento(
    procedimento: ProcedimentoCreate,
    service: ProcedimentoService = Depends(get_procedimento_service)
):
    print("Recebendo requisição POST /procedimentos")
    print(f"Payload recebido: {procedimento.model_dump()}")
    
    try:
        user_id = procedimento.created_by if hasattr(procedimento, 'created_by') and procedimento.created_by else "system"
        
        result = await service.create_procedimento(procedimento, user_id)
        return StandardResponse(
            success=True,
            data=result,
            message="Procedimento criado com sucesso"
        )
    except ValidationError as e:
        print(f"Erro de validação: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        raise

@router.put("/{id}",
            response_model=StandardResponse[Procedimento],
            summary="Atualizar Procedimento",
            description="Atualiza os dados de um procedimento")
async def update_procedimento(
    procedimento: ProcedimentoUpdate,
    id: UUID = Path(...),
    service: ProcedimentoService = Depends(get_procedimento_service)
):
    # Obter o user_id do campo updated_by do procedimento
    user_id = procedimento.updated_by if hasattr(procedimento, 'updated_by') and procedimento.updated_by else "system"
    
    result = await service.update_procedimento(id, procedimento, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    return StandardResponse(
        success=True,
        data=result,
        message="Procedimento atualizado com sucesso"
    )

@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Procedimento",
               description="Remove um procedimento do sistema")
async def delete_procedimento(
    id: UUID = Path(...),
    service: ProcedimentoService = Depends(get_procedimento_service)
):
    result = await service.delete_procedimento(id)
    if not result:
        raise HTTPException(status_code=404, detail="Procedimento não encontrado")
    return StandardResponse(
        success=True,
        data=result,
        message="Procedimento removido com sucesso"
    )

@router.patch("/{id}/inativar",
              response_model=StandardResponse[Procedimento],
              summary="Inativar Procedimento",
              description="Inativa um procedimento no sistema")
async def inativar_procedimento(
    id: UUID = Path(...),
    service: ProcedimentoService = Depends(get_procedimento_service)
):
    # Usar "system" como user_id padrão para inativação
    user_id = "system"
    
    result = await service.inativar_procedimento(id, user_id)
    return StandardResponse(
        success=True,
        data=result,
        message="Procedimento inativado com sucesso"
    ) 