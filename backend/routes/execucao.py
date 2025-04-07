from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..models.execucao import ExecucaoCreate, ExecucaoUpdate, Execucao
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.execucao import ExecucaoService
from ..repositories.execucao import ExecucaoRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_execucao_repository(db: SupabaseClient = Depends(get_supabase_client)) -> ExecucaoRepository:
    return ExecucaoRepository(db)

def get_execucao_service(repo: ExecucaoRepository = Depends(get_execucao_repository)) -> ExecucaoService:
    return ExecucaoService(repo)

@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de execuções está funcionando"}

@router.get("",
            response_model=PaginatedResponse[Execucao],
            summary="Listar Execuções",
            description="Retorna uma lista paginada de execuções")
async def list_execucoes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    numero_guia: Optional[str] = None,
    paciente_id: Optional[UUID] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status_vinculacao: Optional[str] = Query(None, regex="^(vinculada|nao_vinculada)$", description="Filtra por status de vinculação (sessao_id IS NOT NULL ou IS NULL)"),
    link_manual_necessario: Optional[bool] = Query(None, description="Filtra execuções que requerem vinculação manual"),
    order_column: str = Query("data_execucao", regex="^(data_execucao|numero_guia|codigo_ficha|paciente_nome|status|link_manual_necessario)$"),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: ExecucaoService = Depends(get_execucao_service)
):
    try:
        logger.info(f"Listando execuções com parâmetros: limit={limit}, offset={offset}, search={search}, "
                    f"numero_guia={numero_guia}, paciente_id={paciente_id}, data_inicio={data_inicio}, data_fim={data_fim}, "
                    f"status_vinculacao={status_vinculacao}, link_manual_necessario={link_manual_necessario}, "
                    f"order_column={order_column}, order_direction={order_direction}")
        
        is_vinculada = None
        if status_vinculacao == "vinculada":
            is_vinculada = True
        elif status_vinculacao == "nao_vinculada":
            is_vinculada = False

        result = await service.list_execucoes(
            limit=limit,
            offset=offset,
            search=search,
            numero_guia=numero_guia,
            paciente_id=paciente_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            is_vinculada=is_vinculada,
            link_manual_necessario=link_manual_necessario,
            order_column=order_column,
            order_direction=order_direction
        )
        
        # Log para depuração
        if result["items"] and len(result["items"]) > 0:
            logger.debug(f"Primeiro item na resposta: {result['items'][0]}")
        
        response = PaginatedResponse(
            success=True,
            items=result["items"],
            total=result["total"],
            page=(offset // limit) + 1,
            total_pages=ceil(result["total"] / limit),
            has_more=offset + limit < result["total"]
        )
        
        logger.info(f"Resposta gerada com sucesso: {len(result['items'])} itens, total={result['total']}")
        return response
    except Exception as e:
        logger.error(f"Erro ao listar execuções: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar execuções: {str(e)}")

@router.get("/{id}",
            response_model=StandardResponse[Execucao],
            summary="Buscar Execução",
            description="Retorna os dados de uma execução específica")
async def get_execucao(
    id: UUID = Path(...),
    service: ExecucaoService = Depends(get_execucao_service)
):
    result = await service.get_execucao(id)
    if not result:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return StandardResponse(success=True, data=result)

@router.post("",
            response_model=StandardResponse[Execucao],
            status_code=status.HTTP_201_CREATED,
            summary="Criar Execução",
            description="Cria uma nova execução")
async def create_execucao(
    execucao: ExecucaoCreate,
    service: ExecucaoService = Depends(get_execucao_service)
):
    try:
        logger.info(f"Recebendo requisição POST /execucoes")
        logger.info(f"Payload recebido: {execucao.model_dump()}")
        
        result = await service.create_execucao(execucao)
        return StandardResponse(
            success=True,
            data=result,
            message="Execução criada com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except Exception as e:
        logger.error(f"Erro ao criar execução: {str(e)}")
        raise

@router.put("/{id}",
            response_model=StandardResponse[Execucao],
            summary="Atualizar Execução",
            description="Atualiza os dados de uma execução")
async def update_execucao(
    execucao: ExecucaoUpdate,
    id: UUID = Path(...),
    service: ExecucaoService = Depends(get_execucao_service)
):
    result = await service.update_execucao(id, execucao)
    if not result:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Execução atualizada com sucesso"
    )

@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Execução",
               description="Remove uma execução do sistema")
async def delete_execucao(
    id: UUID = Path(...),
    service: ExecucaoService = Depends(get_execucao_service)
):
    result = await service.delete_execucao(id)
    if not result:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Execução removida com sucesso"
    )

@router.get("/guia/{guia_id}",
            response_model=StandardResponse[List[Execucao]],
            summary="Listar Execuções por Guia",
            description="Retorna todas as execuções de uma guia específica")
async def get_execucoes_by_guia(
    guia_id: UUID = Path(...),
    service: ExecucaoService = Depends(get_execucao_service)
):
    result = await service.get_execucoes_by_guia(guia_id)
    return StandardResponse(
        success=True,
        data=result
    )

@router.put("/{id}/biometria",
            response_model=StandardResponse[Execucao],
            summary="Verificar Biometria da Execução",
            description="Atualiza o status de verificação biométrica de uma execução")
async def verificar_biometria_execucao(
    id: UUID = Path(...),
    status_biometria: str = Body(..., embed=True),
    service: ExecucaoService = Depends(get_execucao_service)
):
    result = await service.verificar_biometria_execucao(id, status_biometria)
    return StandardResponse(
        success=True,
        data=result,
        message="Status de biometria da execução atualizado com sucesso"
    )