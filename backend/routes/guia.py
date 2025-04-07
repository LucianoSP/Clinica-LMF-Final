from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..models.guia import GuiaCreate, GuiaUpdate, Guia
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.guia import GuiaService
from ..repositories.guia import GuiaRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


def get_guia_repository(
    db: SupabaseClient = Depends(get_supabase_client),
) -> GuiaRepository:
    return GuiaRepository(db)


def get_guia_service(
    repo: GuiaRepository = Depends(get_guia_repository),
) -> GuiaService:
    return GuiaService(repo)


@router.post(
    "",
    response_model=StandardResponse[Guia],
    status_code=status.HTTP_201_CREATED,
    summary="Criar Guia",
    description="Cria uma nova guia",
)
async def create_guia(
    guia: GuiaCreate, service: GuiaService = Depends(get_guia_service)
):
    try:
        logger.info(f"Recebendo requisição POST /guias")
        logger.info(f"Payload recebido: {guia.model_dump()}")

        result = await service.create_guia(guia)
        return StandardResponse(
            success=True, data=result, message="Guia criada com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar guia: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar guia: {str(e)}")


@router.get(
    "",
    response_model=PaginatedResponse[Guia],
    summary="Listar Guias",
    description="Retorna uma lista paginada de guias com opções de filtro",
)
async def list_guias(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    status: Optional[str] = Query(
        None, regex="^(rascunho|pendente|autorizada|negada|cancelada|executada)$"
    ),
    carteirinha_id: Optional[str] = None,
    paciente_id: Optional[str] = None,
    order_column: str = Query(
        "data_solicitacao",
        regex="^(numero_guia|data_solicitacao|data_autorizacao|status|created_at)$",
    ),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: GuiaService = Depends(get_guia_service),
):
    try:
        result = await service.list_guias(
            limit=limit,
            offset=offset,
            search=search,
            status=status,
            carteirinha_id=carteirinha_id,
            paciente_id=paciente_id,
            order_column=order_column,
            order_direction=order_direction,
        )

        return PaginatedResponse(
            success=True,
            items=result["items"],
            total=result["total"],
            page=(offset // limit) + 1,
            total_pages=ceil(result["total"] / limit),
            has_more=offset + limit < result["total"],
        )
    except Exception as e:
        logger.error(f"Erro ao listar guias: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar guias: {str(e)}")


@router.post(
    "/rpc/listar_guias_com_detalhes",
    response_model=PaginatedResponse[Guia],
    summary="Listar Guias com Detalhes via RPC",
    description="Retorna uma lista paginada de guias com detalhes do paciente e carteirinha via RPC",
)
async def list_guias_rpc(
    p_offset: int = Body(...),
    p_limit: int = Body(...),
    p_search: Optional[str] = Body(None),
    p_status: Optional[str] = Body(None),
    p_carteirinha_id: Optional[str] = Body(None),
    p_paciente_id: Optional[str] = Body(None),
    p_order_column: str = Body("data_solicitacao"),
    p_order_direction: str = Body("desc"),
    service: GuiaService = Depends(get_guia_service),
):
    try:
        result = await service.list_guias(
            offset=p_offset,
            limit=p_limit,
            search=p_search,
            status=p_status,
            carteirinha_id=p_carteirinha_id,
            paciente_id=p_paciente_id,
            order_column=p_order_column,
            order_direction=p_order_direction,
        )

        return PaginatedResponse(
            success=True,
            items=result["items"],
            total=result["total"],
            page=(p_offset // p_limit) + 1,
            total_pages=ceil(result["total"] / p_limit),
            has_more=p_offset + p_limit < result["total"],
        )
    except Exception as e:
        logger.error(f"Erro ao listar guias via RPC: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar guias via RPC: {str(e)}")


@router.get(
    "/{id}",
    response_model=StandardResponse[Guia],
    summary="Buscar Guia",
    description="Retorna uma guia específica pelo ID",
)
async def get_guia(
    id: UUID = Path(...), service: GuiaService = Depends(get_guia_service)
):
    try:
        result = await service.get_guia(id)
        return StandardResponse(success=True, data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar guia: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar guia: {str(e)}")


@router.put(
    "/{id}",
    response_model=StandardResponse[Guia],
    summary="Atualizar Guia",
    description="Atualiza uma guia existente",
)
async def update_guia(
    guia: GuiaUpdate = Body(...),
    id: UUID = Path(...),
    service: GuiaService = Depends(get_guia_service),
):
    try:
        result = await service.update_guia(id, guia)
        return StandardResponse(
            success=True, data=result, message="Guia atualizada com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar guia: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar guia: {str(e)}")


@router.delete(
    "/{id}",
    response_model=StandardResponse[bool],
    summary="Deletar Guia",
    description="Deleta uma guia existente (soft delete)",
)
async def delete_guia(
    id: UUID = Path(...), service: GuiaService = Depends(get_guia_service)
):
    try:
        result = await service.delete_guia(id)
        return StandardResponse(
            success=True, data=result, message="Guia deletada com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar guia: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao deletar guia: {str(e)}")


@router.get(
    "/carteirinha/{carteirinha_id}",
    response_model=StandardResponse[List[Guia]],
    summary="Buscar Guias por Carteirinha",
    description="Retorna todas as guias de uma carteirinha específica",
)
async def get_guias_by_carteirinha(
    carteirinha_id: UUID = Path(...),
    status: Optional[str] = Query(
        None, regex="^(rascunho|pendente|autorizada|negada|cancelada|executada)$"
    ),
    service: GuiaService = Depends(get_guia_service),
):
    try:
        result = await service.get_guias_by_carteirinha(carteirinha_id, status)
        return StandardResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Erro ao buscar guias da carteirinha: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar guias da carteirinha: {str(e)}"
        )


@router.patch(
    "/{id}/status",
    response_model=StandardResponse[Guia],
    summary="Atualizar Status da Guia",
    description="Atualiza o status de uma guia existente",
)
async def update_guia_status(
    id: UUID = Path(...),
    novo_status: str = Query(
        ..., regex="^(rascunho|pendente|autorizada|negada|cancelada|executada)$"
    ),
    motivo: Optional[str] = Query(None),
    service: GuiaService = Depends(get_guia_service),
):
    try:
        result = await service.update_guia_status(id, novo_status, motivo)
        return StandardResponse(
            success=True,
            data=result,
            message=f"Status da guia atualizado para {novo_status}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar status da guia: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar status da guia: {str(e)}"
        )
