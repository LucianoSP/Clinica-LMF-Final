from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..schemas.sessao import SessaoCreate, SessaoUpdate, Sessao
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.sessao import SessaoService
from ..repositories.sessao import SessaoRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_sessao_repository(db: SupabaseClient = Depends(get_supabase_client)) -> SessaoRepository:
    return SessaoRepository(db)

def get_sessao_service(repo: SessaoRepository = Depends(get_sessao_repository)) -> SessaoService:
    return SessaoService(repo)

@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de sessões está funcionando"}

@router.get("",
            response_model=PaginatedResponse[Sessao],
            summary="Listar Sessões",
            description="Retorna uma lista paginada de sessões")
async def list_sessoes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    order_column: str = Query("data_sessao", regex="^(data_sessao|status|valor_sessao|created_at)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$"),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.list_sessoes(
        limit=limit,
        offset=offset,
        search=search,
        order_column=order_column,
        order_direction=order_direction
    )
    
    return PaginatedResponse(
        success=True,
        items=result["items"],
        total=result["total"],
        page=(offset // limit) + 1,
        total_pages=ceil(result["total"] / limit),
        has_more=offset + limit < result["total"]
    )

@router.get("/{id}",
            response_model=StandardResponse[Sessao],
            summary="Buscar Sessão",
            description="Retorna os dados de uma sessão específica")
async def get_sessao(
    id: UUID = Path(...),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.get_sessao(id)
    if not result:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return StandardResponse(success=True, data=result)

@router.post("",
            response_model=StandardResponse[Sessao],
            status_code=status.HTTP_201_CREATED,
            summary="Criar Sessão",
            description="Cria uma nova sessão")
async def create_sessao(
    sessao: SessaoCreate,
    service: SessaoService = Depends(get_sessao_service)
):
    try:
        logger.info(f"Recebendo requisição POST /sessoes")
        logger.info(f"Payload recebido: {sessao.model_dump()}")
        
        result = await service.create_sessao(sessao)
        return StandardResponse(
            success=True,
            data=result,
            message="Sessão criada com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {str(e)}")
        raise

@router.put("/{id}",
            response_model=StandardResponse[Sessao],
            summary="Atualizar Sessão",
            description="Atualiza os dados de uma sessão")
async def update_sessao(
    sessao: SessaoUpdate,
    id: UUID = Path(...),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.update_sessao(id, sessao)
    if not result:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Sessão atualizada com sucesso"
    )

@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Sessão",
               description="Remove uma sessão do sistema")
async def delete_sessao(
    id: UUID = Path(...),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.delete_sessao(id)
    if not result:
        raise HTTPException(status_code=404, detail="Sessão não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Sessão removida com sucesso"
    )

@router.get("/ficha-presenca/{ficha_presenca_id}",
            response_model=StandardResponse[List[Sessao]],
            summary="Listar Sessões por Ficha de Presença",
            description="Retorna todas as sessões de uma ficha de presença específica")
async def get_sessoes_by_ficha_presenca(
    ficha_presenca_id: UUID = Path(...),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.get_sessoes_by_ficha_presenca(ficha_presenca_id)
    return StandardResponse(
        success=True,
        data=result
    )

@router.get("/paciente/{paciente_id}",
            response_model=StandardResponse[List[Sessao]],
            summary="Listar Sessões por Paciente",
            description="Retorna todas as sessões de um paciente específico")
async def get_sessoes_by_paciente(
    paciente_id: UUID = Path(...),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.get_sessoes_by_paciente(paciente_id)
    return StandardResponse(
        success=True,
        data=result
    )

@router.get("/guia/{guia_id}",
            response_model=PaginatedResponse[Sessao],
            summary="Listar Sessões por Guia",
            description="Retorna todas as sessões de uma guia específica")
async def list_sessoes_by_guia(
    guia_id: UUID = Path(...),
    service: SessaoService = Depends(get_sessao_service)
):
    result = await service.list_sessoes_by_guia(guia_id)
    return PaginatedResponse(
        success=True,
        items=result,
        total=len(result),
        page=1,
        total_pages=1,
        has_more=False
    ) 