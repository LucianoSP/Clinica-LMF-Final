from datetime import datetime, UTC, date
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException
from ..models.sessao import SessaoCreate, SessaoUpdate, Sessao
from ..repositories.sessao import SessaoRepository
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SessaoService:
    def __init__(self, repository: SessaoRepository):
        self.repository = repository

    async def list_sessoes(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "data_sessao",
        order_direction: str = "desc"
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction
            )
            
            return {
                "items": [Sessao.model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar sessões: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar sessões: {str(e)}"
            )

    async def get_sessao(self, id: str) -> Optional[Sessao]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Sessão não encontrada")
            return Sessao(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar sessão: {str(e)}")

    async def create_sessao(self, sessao: SessaoCreate) -> Optional[Sessao]:
        try:
            logger.info(f"Dados recebidos no serviço: {sessao.model_dump()}")
            result = await self.repository.create(sessao)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao criar sessão")
            return Sessao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar sessão: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar sessão: {str(e)}")

    async def update_sessao(self, id: UUID, sessao: SessaoUpdate, user_id: UUID) -> Optional[Sessao]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Sessão não encontrada")

            update_data = sessao.model_dump(exclude_unset=True)
            result = await self.repository.update(id, update_data, user_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="Sessão não encontrada")
            return Sessao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar sessão: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar sessão: {str(e)}")

    async def delete_sessao(self, id: UUID) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Sessão não encontrada")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar sessão: {str(e)}")

    async def update_status_sessao(self, id: str, status: str, user_id: str) -> Optional[Sessao]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Sessão não encontrada")

            result = await self.repository.update_status(id, status, user_id)
            if not result:
                raise HTTPException(status_code=404, detail="Sessão não encontrada")
            return Sessao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar status da sessão: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar status da sessão: {str(e)}")

    async def get_sessoes_by_guia(self, guia_id: UUID) -> List[Sessao]:
        try:
            result = await self.repository.get_by_guia(guia_id)
            return [Sessao(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar sessões da guia: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar sessões da guia: {str(e)}"
            )

    async def get_sessoes_by_paciente(self, paciente_id: UUID) -> List[Sessao]:
        try:
            result = await self.repository.get_by_paciente(paciente_id)
            return [Sessao(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar sessões do paciente: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar sessões do paciente: {str(e)}"
            )

    async def get_sessoes_by_ficha_presenca(self, ficha_presenca_id: str) -> List[Sessao]:
        try:
            result = await self.repository.get_by_ficha_presenca(ficha_presenca_id)
            return [Sessao(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar sessões da ficha de presença: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar sessões da ficha de presença: {str(e)}"
            )

    async def list_sessoes_by_guia(self, guia_id: UUID) -> List[Dict]:
        """Lista todas as sessões de uma guia específica"""
        return await self.repository.list_by_guia(guia_id) 