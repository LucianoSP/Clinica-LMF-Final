from typing import Dict, List, Optional
from datetime import datetime
import logging
from ..repositories.divergencia_auditoria import DivergenciaAuditoriaRepository
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class DivergenciaAuditoriaService:
    def __init__(self, repository: DivergenciaAuditoriaRepository):
        self.repository = repository

    async def list_divergencias(self,
                              page: int = 1,
                              per_page: int = 10,
                              data_inicio: Optional[str] = None,
                              data_fim: Optional[str] = None,
                              status: Optional[str] = None,
                              tipo: Optional[str] = None,
                              prioridade: Optional[str] = None) -> Dict:
        try:
            return await self.repository.list(
                page=page,
                per_page=per_page,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status,
                tipo=tipo,
                prioridade=prioridade
            )
        except Exception as e:
            logger.error(f"Erro ao listar divergências: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar divergências: {str(e)}"
            )

    async def create_divergencia(self, divergencia: Dict) -> Dict:
        try:
            return await self.repository.create(divergencia)
        except Exception as e:
            logger.error(f"Erro ao criar divergência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar divergência: {str(e)}"
            )

    async def update_status(self, id: str, status: str, user_id: Optional[str] = None) -> Dict:
        try:
            return await self.repository.update_status(id, status, user_id)
        except Exception as e:
            logger.error(f"Erro ao atualizar status da divergência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar status da divergência: {str(e)}"
            )

    async def delete_all(self) -> bool:
        try:
            return await self.repository.delete_all()
        except Exception as e:
            logger.error(f"Erro ao limpar divergências: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao limpar divergências: {str(e)}"
            )

    async def update_ficha_ids(self, divergencias: List[Dict]) -> bool:
        try:
            return await self.repository.update_ficha_ids(divergencias)
        except Exception as e:
            logger.error(f"Erro ao atualizar ficha_ids: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar ficha_ids: {str(e)}"
            )

    async def get_statistics(self) -> Dict:
        try:
            return await self.repository.get_statistics()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter estatísticas: {str(e)}"
            )
