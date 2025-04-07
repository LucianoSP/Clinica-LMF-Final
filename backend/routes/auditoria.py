from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, List
from datetime import datetime, date
from ..services.auditoria import AuditoriaService
from ..repositories.divergencia import DivergenciaRepository
from ..repositories.auditoria_execucao import AuditoriaExecucaoRepository
from ..models.divergencia import DivergenciaCreate, DivergenciaUpdate, TipoDivergencia, StatusDivergencia
from ..utils.date_utils import formatar_data
from backend.repositories.database_supabase import get_supabase_client
from uuid import UUID

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])

@router.post("/iniciar")
async def iniciar_auditoria(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db = Depends(get_supabase_client)
) -> Dict:
    """Inicia uma nova auditoria"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        auditoria_repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaService(divergencia_repository, auditoria_repository)
        
        return await service.iniciar_auditoria(data_inicio, data_fim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/executar")
async def executar_auditoria(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db = Depends(get_supabase_client)
) -> Dict:
    """Executa uma auditoria completa"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        auditoria_repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaService(divergencia_repository, auditoria_repository)
        
        return await service.realizar_auditoria_completa(data_inicio, data_fim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/divergencias")
async def listar_divergencias(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    prioridade: Optional[str] = None,
    db = Depends(get_supabase_client)
) -> Dict:
    """Lista divergências com paginação e filtros"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        auditoria_repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaService(divergencia_repository, auditoria_repository)
        
        return await service.listar_divergencias(
            page=page,
            per_page=per_page,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            tipo=tipo,
            prioridade=prioridade
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/divergencias/{divergencia_id}")
async def obter_divergencia(
    divergencia_id: str,
    db = Depends(get_supabase_client)
) -> Dict:
    """Obtém uma divergência pelo ID"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        return await divergencia_repository.get(divergencia_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/divergencias/{divergencia_id}")
async def atualizar_divergencia(
    divergencia_id: str,
    divergencia: DivergenciaUpdate,
    db = Depends(get_supabase_client)
) -> Dict:
    """Atualiza uma divergência"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        return await divergencia_repository.update(divergencia_id, divergencia)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/divergencias/{divergencia_id}/status")
async def atualizar_status_divergencia(
    divergencia_id: str,
    novo_status: str,
    usuario_id: Optional[str] = None,
    db = Depends(get_supabase_client)
) -> Dict:
    """Atualiza o status de uma divergência"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        auditoria_repository = AuditoriaExecucaoRepository(db)
        service = AuditoriaService(divergencia_repository, auditoria_repository)
        
        success = await service.atualizar_status_divergencia(
            divergencia_id,
            novo_status,
            usuario_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Divergência não encontrada")
            
        return {"message": "Status atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estatisticas")
async def obter_estatisticas(
    db = Depends(get_supabase_client)
) -> Dict:
    """Obtém estatísticas das divergências"""
    try:
        divergencia_repository = DivergenciaRepository(db)
        return await divergencia_repository.get_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 