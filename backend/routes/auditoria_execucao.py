from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, Dict
import logging
from ..repositories.auditoria_execucao import AuditoriaExecucaoRepository
from ..repositories.divergencia_auditoria import DivergenciaAuditoriaRepository
from ..services.auditoria_execucao import AuditoriaExecucaoService
from ..services.divergencia_auditoria import DivergenciaAuditoriaService
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient
from ..schemas.responses import StandardResponse
from ..models.auditoria_execucao import AuditoriaExecucao
from ..utils.date_utils import formatar_data
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(redirect_slashes=False, tags=["Auditoria Execução"])


def get_auditoria_execucao_repository(
    db: SupabaseClient = Depends(get_supabase_client),
) -> AuditoriaExecucaoRepository:
    return AuditoriaExecucaoRepository(db)


def get_divergencia_auditoria_repository(
    db: SupabaseClient = Depends(get_supabase_client),
) -> DivergenciaAuditoriaRepository:
    return DivergenciaAuditoriaRepository(db)


def get_auditoria_execucao_service(
    repository: AuditoriaExecucaoRepository = Depends(
        get_auditoria_execucao_repository
    ),
) -> AuditoriaExecucaoService:
    return AuditoriaExecucaoService(repository)


def get_divergencia_auditoria_service(
    repository: DivergenciaAuditoriaRepository = Depends(
        get_divergencia_auditoria_repository
    ),
) -> DivergenciaAuditoriaService:
    return DivergenciaAuditoriaService(repository)


@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de auditoria de execuções está funcionando"}


@router.get(
    "/ultima",
    response_model=StandardResponse[AuditoriaExecucao],
    summary="Buscar Última Auditoria",
    description="Retorna os dados da última auditoria de execução realizada",
)
async def get_ultima_auditoria(
    service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service),
):
    """
    Obtém os dados da última auditoria realizada
    """
    try:
        result = await service.get_ultima_auditoria()
        if not result:
            # Criando um objeto com valores padrão válidos que satisfazem o schema
            return StandardResponse(
                success=True,
                data={
                    "id": "00000000-0000-0000-0000-000000000000",  # UUID vazio como valor padrão
                    "data_execucao": datetime.now().date(),  # Data atual como valor padrão
                    "total_protocolos": 0,
                    "total_divergencias": 0,
                    "divergencias_por_tipo": {},
                    "total_fichas": 0,
                    "total_execucoes": 0,
                    "total_guias": 0,
                    "total_resolvidas": 0,
                    "status": "sem_dados",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                },
            )
        return StandardResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Erro ao obter última auditoria: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao obter última auditoria: {str(e)}"
        )


@router.get(
    "",
    response_model=StandardResponse[AuditoriaExecucao],
    summary="Listar Auditorias de Execuções",
    description="Retorna uma lista paginada de auditorias de execuções",
)
async def list_auditoria_execucoes(
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    order_column: str = "data_execucao",
    order_direction: str = "desc",
    service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service),
):
    try:
        result = await service.list_auditoria_execucoes(
            offset=offset,
            limit=limit,
            search=search,
            order_column=order_column,
            order_direction=order_direction,
        )
        return StandardResponse(success=True, data=result)
    except Exception as e:
        logger.error(f"Erro ao listar auditorias: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar auditorias: {str(e)}"
        )


@router.get(
    "/{id}",
    response_model=StandardResponse[AuditoriaExecucao],
    summary="Buscar Auditoria de Execução",
    description="Retorna os dados de uma auditoria de execução específica",
)
async def get_auditoria_execucao(
    id: str, service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service)
):
    result = await service.get_by_id(id)
    if not result:
        raise HTTPException(
            status_code=404, detail="Auditoria de execução não encontrada"
        )
    return StandardResponse(success=True, data=result)


@router.post(
    "",
    response_model=StandardResponse[AuditoriaExecucao],
    status_code=201,
    summary="Criar Auditoria de Execução",
    description="Cria uma nova auditoria de execução",
)
async def create_auditoria_execucao(
    data: Dict,
    service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service),
):
    try:
        result = await service.registrar_execucao(**data)
        return StandardResponse(
            success=True,
            data=result,
            message="Auditoria de execução criada com sucesso",
        )
    except Exception as e:
        logger.error(f"Erro ao criar auditoria de execução: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar auditoria de execução: {str(e)}"
        )


@router.put(
    "/{id}",
    response_model=StandardResponse[AuditoriaExecucao],
    summary="Atualizar Auditoria de Execução",
    description="Atualiza os dados de uma auditoria de execução",
)
async def update_auditoria_execucao(
    data: Dict,
    id: str,
    service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service),
):
    result = await service.update_auditoria_execucao(id, **data)
    if not result:
        raise HTTPException(
            status_code=404, detail="Auditoria de execução não encontrada"
        )
    return StandardResponse(
        success=True,
        data=result,
        message="Auditoria de execução atualizada com sucesso",
    )


@router.delete(
    "/{id}",
    response_model=StandardResponse[bool],
    summary="Deletar Auditoria de Execução",
    description="Remove uma auditoria de execução do sistema",
)
async def delete_auditoria_execucao(
    id: str, service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service)
):
    result = await service.delete_auditoria_execucao(id)
    if not result:
        raise HTTPException(
            status_code=404, detail="Auditoria de execução não encontrada"
        )
    return StandardResponse(
        success=True, data=result, message="Auditoria de execução removida com sucesso"
    )


@router.get(
    "/periodo/{data_inicial}/{data_final}",
    response_model=StandardResponse[AuditoriaExecucao],
    summary="Buscar Auditoria por Período",
    description="Retorna a auditoria de execução para um período específico",
)
async def get_auditoria_por_periodo(
    data_inicial: str,
    data_final: str,
    service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service),
):
    result = await service.get_auditoria_por_periodo(data_inicial, data_final)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma auditoria encontrada para o período especificado",
        )
    return StandardResponse(success=True, data=result)


@router.get("")
async def listar_execucoes(
    page: int = 1,
    per_page: int = 10,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: Optional[str] = None,
    db=Depends(get_supabase_client),
) -> Dict:
    """Lista execuções de auditoria com paginação e filtros"""
    try:
        repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaExecucaoService(repository)

        return await service.listar_execucoes(
            page=page,
            per_page=per_page,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execucao_id}")
async def obter_execucao(execucao_id: str, db=Depends(get_supabase_client)) -> Dict:
    """Obtém uma execução de auditoria pelo ID"""
    try:
        repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaExecucaoService(repository)

        execucao = await service.obter_execucao(execucao_id)
        if not execucao:
            raise HTTPException(status_code=404, detail="Execução não encontrada")

        return execucao
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{execucao_id}")
async def atualizar_execucao(
    execucao_id: str, data: Dict, db=Depends(get_supabase_client)
) -> Dict:
    """Atualiza uma execução de auditoria"""
    try:
        repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaExecucaoService(repository)

        execucao_atualizada = await service.atualizar_execucao(execucao_id, **data)
        if not execucao_atualizada:
            raise HTTPException(status_code=404, detail="Execução não encontrada")

        return execucao_atualizada
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{execucao_id}")
async def deletar_execucao(execucao_id: str, db=Depends(get_supabase_client)) -> Dict:
    """Deleta uma execução de auditoria"""
    try:
        repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaExecucaoService(repository)

        success = await service.deletar_execucao(execucao_id)
        if not success:
            raise HTTPException(status_code=404, detail="Execução não encontrada")

        return {"message": "Execução deletada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execucao_id}/divergencias")
async def listar_divergencias_execucao(
    execucao_id: str,
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    prioridade: Optional[str] = None,
    db=Depends(get_supabase_client),
) -> Dict:
    """Lista divergências de uma execução específica"""
    try:
        repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaExecucaoService(repository)

        return await service.listar_divergencias_execucao(
            execucao_id=execucao_id,
            page=page,
            per_page=per_page,
            status=status,
            tipo=tipo,
            prioridade=prioridade,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execucao_id}/estatisticas")
async def obter_estatisticas_execucao(
    execucao_id: str, db=Depends(get_supabase_client)
) -> Dict:
    """Obtém estatísticas de uma execução específica"""
    try:
        repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaExecucaoService(repository)

        stats = await service.obter_estatisticas_execucao(execucao_id)
        if not stats:
            raise HTTPException(status_code=404, detail="Execução não encontrada")

        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/iniciar",
    response_model=StandardResponse[AuditoriaExecucao],
    status_code=201,
    summary="Iniciar Nova Auditoria",
    description="Inicia uma nova execução de auditoria no sistema",
)
async def iniciar_auditoria(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    service: AuditoriaExecucaoService = Depends(get_auditoria_execucao_service),
    divergencia_service: DivergenciaAuditoriaService = Depends(get_divergencia_auditoria_service),
):
    """
    Inicia uma nova execução de auditoria
    """
    try:
        # Criando uma nova auditoria com data atual
        data = {
            "data_execucao": datetime.now(),
            "data_inicial": data_inicio,
            "data_final": data_fim,
            "status": "em_andamento"
        }
        result = await service.registrar_execucao(**data)
        
        # Importando aqui para evitar circular imports
        from ..services.auditoria import realizar_auditoria_fichas_execucoes
        
        # Iniciar o processo de auditoria em background usando asyncio.create_task
        import asyncio
        
        async def executar_auditoria_background():
            try:
                # Chamar o processo de auditoria
                await realizar_auditoria_fichas_execucoes(data_inicio, data_fim)
                
                # Atualizar o status da auditoria para concluído
                try:
                    await service.update_auditoria_execucao(
                        result.id, 
                        status="concluido",
                        updated_at=datetime.now().isoformat()
                    )
                    logger.info(f"Auditoria {result.id} concluída com sucesso")
                except Exception as update_error:
                    logger.error(f"Erro ao atualizar status da auditoria: {update_error}")
            except Exception as audit_error:
                logger.error(f"Erro ao executar auditoria: {audit_error}")
                # Atualizar o status da auditoria para erro
                try:
                    await service.update_auditoria_execucao(
                        result.id, 
                        status="erro",
                        updated_at=datetime.now().isoformat()
                    )
                except Exception as update_error:
                    logger.error(f"Erro ao atualizar status da auditoria para erro: {update_error}")
        
        # Iniciar a tarefa em background
        asyncio.create_task(executar_auditoria_background())
        
        # Retornar imediatamente com o status "em_andamento"
        return StandardResponse(
            success=True,
            data=result,
            message="Auditoria iniciada com sucesso. O processo está sendo executado em segundo plano.",
        )
    except Exception as e:
        logger.error(f"Erro ao iniciar auditoria: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao iniciar auditoria: {str(e)}"
        )
