from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..models.plano_saude import PlanoSaudeCreate, PlanoSaudeUpdate, PlanoSaude
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.plano_saude import PlanoSaudeService
from ..repositories.plano_saude import PlanoSaudeRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


def get_plano_saude_repository(db: SupabaseClient = Depends(
    get_supabase_client)) -> PlanoSaudeRepository:
    return PlanoSaudeRepository(db)


def get_plano_saude_service(repo: PlanoSaudeRepository = Depends(
    get_plano_saude_repository)) -> PlanoSaudeService:
    return PlanoSaudeService(repo)


@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de planos de saúde está funcionando"}


@router.get("",
            response_model=PaginatedResponse[PlanoSaude],
            summary="Listar Planos de Saúde",
            description="Retorna uma lista paginada de planos de saúde")
async def list_planos_saude(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    order_column: str = Query("nome", regex="^(nome|created_at)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$"),
    service: PlanoSaudeService = Depends(get_plano_saude_service)):
    
    logger.info(f"Recebida requisição para listar planos de saúde")
    logger.info(f"Parâmetros: limit={limit}, offset={offset}, search={search}, order_column={order_column}, order_direction={order_direction}")
    
    result = await service.list_planos_saude(limit=limit,
                                           offset=offset,
                                           search=search,
                                           order_column=order_column,
                                           order_direction=order_direction)

    logger.info(f"Resultado obtido: {len(result['items'])} itens")
    
    return PaginatedResponse(success=True,
                           items=result["items"],
                           total=result["total"],
                           page=(offset // limit) + 1,
                           total_pages=ceil(result["total"] / limit),
                           has_more=offset + limit < result["total"])


@router.post("",
            response_model=StandardResponse[PlanoSaude],
            status_code=status.HTTP_201_CREATED,
            summary="Criar Plano de Saúde",
            description="Cria um novo plano de saúde")
async def create_plano_saude(
    plano: PlanoSaudeCreate,
    service: PlanoSaudeService = Depends(get_plano_saude_service)
):
    try:
        logger.info(f"Recebendo requisição POST /planos-saude")
        logger.info(f"Payload recebido: {plano.model_dump()}")
        
        result = await service.create_plano_saude(plano)
        return StandardResponse(
            success=True,
            data=result,
            message="Plano de saúde criado com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except Exception as e:
        logger.error(f"Erro ao criar plano de saúde: {str(e)}")
        raise


@router.get("/{id}",
            response_model=StandardResponse[PlanoSaude],
            summary="Buscar Plano de Saúde",
            description="Retorna os dados de um plano de saúde específico")
async def get_plano_saude(
        id: UUID = Path(...),
        service: PlanoSaudeService = Depends(get_plano_saude_service)):
    result = await service.get_plano_saude(id)
    if not result:
        raise HTTPException(status_code=404,
                          detail="Plano de saúde não encontrado")
    return StandardResponse(success=True, data=result)


@router.put("/{id}",
            response_model=StandardResponse[PlanoSaude],
            summary="Atualizar Plano de Saúde",
            description="Atualiza os dados de um plano de saúde")
async def update_plano_saude(
    plano: PlanoSaudeUpdate,
    id: UUID = Path(...),
    service: PlanoSaudeService = Depends(get_plano_saude_service)
):
    try:
        # Usando o mesmo ID fixo do usuário admin
        user_id = "f5ba3137-3ef6-4958-bf07-dfaa12d91db3"
        
        result = await service.update_plano_saude(id, plano, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Plano de saúde não encontrado")
        return StandardResponse(
            success=True,
            data=result,
            message="Plano de saúde atualizado com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar plano de saúde: {str(e)}"
        )


@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Plano de Saúde",
               description="Remove um plano de saúde do sistema")
async def delete_plano_saude(
        id: UUID = Path(...),
        service: PlanoSaudeService = Depends(get_plano_saude_service)):
    result = await service.delete_plano_saude(id)
    if not result:
        raise HTTPException(status_code=404,
                          detail="Plano de saúde não encontrado")
    return StandardResponse(success=True,
                          data=result,
                          message="Plano de saúde removido com sucesso")
