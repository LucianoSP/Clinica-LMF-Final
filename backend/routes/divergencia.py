from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..models.divergencia import DivergenciaCreate, DivergenciaUpdate, Divergencia, TipoDivergencia, StatusDivergencia
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.divergencia import DivergenciaService
from ..repositories.divergencia import DivergenciaRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient
from ..services.auditoria import AuditoriaService
from ..repositories.auditoria_execucao import AuditoriaExecucaoRepository

router = APIRouter(tags=["Divergências"], redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_divergencia_repository(db: SupabaseClient = Depends(get_supabase_client)) -> DivergenciaRepository:
    return DivergenciaRepository(db)

def get_divergencia_service(repo: DivergenciaRepository = Depends(get_divergencia_repository)) -> DivergenciaService:
    return DivergenciaService(repo)

def get_auditoria_service(db: SupabaseClient = Depends(get_supabase_client)) -> AuditoriaService:
    divergencia_repo = DivergenciaRepository(db)
    auditoria_repo = AuditoriaExecucaoRepository(db)
    return AuditoriaService(divergencia_repo, auditoria_repo)

@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de divergências está funcionando"}

@router.get("",
            response_model=PaginatedResponse[Divergencia],
            summary="Listar Divergências",
            description="Retorna uma lista paginada de divergências")
async def list_divergencias(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    prioridade: Optional[str] = None,
    order_column: str = Query("data_identificacao", regex="^(data_identificacao|numero_guia|codigo_ficha|status|tipo|prioridade|created_at)$"),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: AuditoriaService = Depends(get_auditoria_service)
):
    """
    Lista as divergências encontradas na auditoria
    """
    try:
        result = await service.listar_divergencias(
            limit=limit,
            offset=offset,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            tipo=tipo,
            prioridade=prioridade,
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
    except Exception as e:
        logger.error(f"Erro ao listar divergências: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar divergências: {str(e)}"
        )

@router.get("/{id}",
            response_model=StandardResponse[Divergencia],
            summary="Buscar Divergência",
            description="Retorna os dados de uma divergência específica")
async def get_divergencia(
    id: UUID = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.get_divergencia(id)
    if not result:
        raise HTTPException(status_code=404, detail="Divergência não encontrada")
    return StandardResponse(success=True, data=result)

@router.post("",
            response_model=StandardResponse[Divergencia],
            status_code=status.HTTP_201_CREATED,
            summary="Criar Divergência",
            description="Cria uma nova divergência")
async def create_divergencia(
    divergencia: DivergenciaCreate,
    service: DivergenciaService = Depends(get_divergencia_service)
):
    try:
        logger.info(f"Recebendo requisição POST /divergencias")
        logger.info(f"Payload recebido: {divergencia.model_dump()}")
        
        result = await service.create_divergencia(divergencia)
        return StandardResponse(
            success=True,
            data=result,
            message="Divergência criada com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except Exception as e:
        logger.error(f"Erro ao criar divergência: {str(e)}")
        raise

@router.put("/{id}",
            response_model=StandardResponse[Divergencia],
            summary="Atualizar Divergência",
            description="Atualiza os dados de uma divergência")
async def update_divergencia(
    divergencia: DivergenciaUpdate,
    id: UUID = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.update_divergencia(id, divergencia)
    if not result:
        raise HTTPException(status_code=404, detail="Divergência não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Divergência atualizada com sucesso"
    )

@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Divergência",
               description="Remove uma divergência do sistema")
async def delete_divergencia(
    id: UUID = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.delete_divergencia(id)
    if not result:
        raise HTTPException(status_code=404, detail="Divergência não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Divergência removida com sucesso"
    )

@router.post("/{id}/resolver",
             response_model=StandardResponse[Divergencia],
             summary="Resolver Divergência",
             description="Marca uma divergência como resolvida")
async def resolver_divergencia(
    id: UUID = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.resolver_divergencia(id)
    return StandardResponse(
        success=True,
        data=result,
        message="Divergência resolvida com sucesso"
    )

@router.post("/{id}/incrementar-tentativas",
             response_model=StandardResponse[Divergencia],
             summary="Incrementar Tentativas",
             description="Incrementa o contador de tentativas de resolução")
async def incrementar_tentativas(
    id: UUID = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.incrementar_tentativas(id)
    return StandardResponse(
        success=True,
        data=result,
        message="Contador de tentativas incrementado com sucesso"
    )

@router.get("/guia/{numero_guia}",
            response_model=StandardResponse[List[Divergencia]],
            summary="Buscar Divergências por Guia",
            description="Retorna todas as divergências associadas a um número de guia")
async def get_divergencias_by_guia(
    numero_guia: str = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.get_divergencias_by_numero_guia(numero_guia)
    return StandardResponse(
        success=True,
        data=result
    )

@router.get("/ficha/{codigo_ficha}",
            response_model=StandardResponse[List[Divergencia]],
            summary="Buscar Divergências por Ficha",
            description="Retorna todas as divergências associadas a um código de ficha")
async def get_divergencias_by_ficha(
    codigo_ficha: str = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.get_divergencias_by_codigo_ficha(codigo_ficha)
    return StandardResponse(
        success=True,
        data=result
    )

@router.get("/sessao/{sessao_id}",
            response_model=StandardResponse[List[Divergencia]],
            summary="Buscar Divergências por Sessão",
            description="Retorna todas as divergências associadas a uma sessão")
async def get_divergencias_by_sessao(
    sessao_id: UUID = Path(...),
    service: DivergenciaService = Depends(get_divergencia_service)
):
    result = await service.get_divergencias_by_sessao(sessao_id)
    return StandardResponse(
        success=True,
        data=result
    )

@router.post("/iniciar-auditoria")
async def iniciar_auditoria(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    service: AuditoriaService = Depends(get_auditoria_service)
):
    """
    Inicia o processo de auditoria
    """
    try:
        result = await service.realizar_auditoria_completa(data_inicio, data_fim)
        return StandardResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Erro ao iniciar auditoria: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar auditoria: {str(e)}"
        )

@router.put("/{divergencia_id}/status")
async def atualizar_status_divergencia(
    divergencia_id: str,
    novo_status: str,
    usuario_id: Optional[str] = None,
    service: AuditoriaService = Depends(get_auditoria_service)
):
    """
    Atualiza o status de uma divergência
    """
    try:
        result = await service.atualizar_status_divergencia(
            divergencia_id,
            novo_status,
            usuario_id
        )
        return StandardResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Erro ao atualizar status da divergência: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar status da divergência: {str(e)}"
        ) 