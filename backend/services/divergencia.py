from datetime import datetime, UTC
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException
from ..models.divergencia import DivergenciaCreate, DivergenciaUpdate, Divergencia
from ..repositories.divergencia import DivergenciaRepository
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DivergenciaService:
    def __init__(self, repository: DivergenciaRepository):
        self.repository = repository

    async def list_divergencias(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "data_identificacao",
        order_direction: str = "desc",
        status: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction,
                status=status,
                tipo=tipo
            )
            
            return {
                "items": [Divergencia.model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar divergencias: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar divergencias: {str(e)}"
            )

    async def get_divergencia(self, id: str) -> Optional[Divergencia]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")
            return Divergencia(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar divergência: {str(e)}")

    async def create_divergencia(self, divergencia: DivergenciaCreate, user_id: str) -> Optional[Divergencia]:
        try:
            logger.info(f"Dados recebidos no serviço: {divergencia.model_dump()}")
            # Converter para dict e processar
            data = divergencia.model_dump(
                exclude_unset=True,
                exclude_none=True
            )
            
            # Adiciona timestamps e user_id
            now = datetime.now(UTC).isoformat()
            data.update({
                "created_at": now,
                "updated_at": now,
                "created_by": str(user_id),
                "updated_by": str(user_id),
                "data_identificacao": now
            })

            result = await self.repository.create(data)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao criar divergência")
            
            return Divergencia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar divergência: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar divergência: {str(e)}")

    async def update_divergencia(self, id: str, divergencia: DivergenciaUpdate, user_id: str) -> Optional[Divergencia]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")

            # Converter para dict e processar
            update_data = divergencia.model_dump(
                exclude_unset=True,
                exclude_none=True
            )
            
            # Se estiver alterando o status para resolvida, adiciona data_resolucao e resolvido_por
            if update_data.get("status") == "resolvida":
                update_data.update({
                    "data_resolucao": datetime.now(UTC).isoformat(),
                    "resolvido_por": str(user_id)
                })
            
            # Adicionar campos de auditoria
            update_data.update({
                "updated_at": datetime.now(UTC).isoformat(),
                "updated_by": str(user_id)
            })

            result = await self.repository.update(id, update_data, user_id)
            if not result:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")
            return Divergencia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar divergência: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar divergência: {str(e)}")

    async def delete_divergencia(self, id: str) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar divergência: {str(e)}")

    async def resolver_divergencia(self, id: str, user_id: str) -> Optional[Divergencia]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")

            if existing["status"] == "resolvida":
                raise HTTPException(status_code=400, detail="Divergência já está resolvida")

            result = await self.repository.resolver_divergencia(id, user_id)
            if not result:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")
            return Divergencia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao resolver divergência: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao resolver divergência: {str(e)}")

    async def incrementar_tentativas(self, id: str) -> Optional[Divergencia]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")

            result = await self.repository.incrementar_tentativas(id)
            if not result:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")
            return Divergencia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao incrementar tentativas de resolução: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao incrementar tentativas de resolução: {str(e)}")

    async def get_divergencias_by_numero_guia(self, numero_guia: str) -> List[Divergencia]:
        try:
            result = await self.repository.get_by_numero_guia(numero_guia)
            return [Divergencia(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar divergências por número de guia: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar divergências por número de guia: {str(e)}"
            )

    async def get_divergencias_by_codigo_ficha(self, codigo_ficha: str) -> List[Divergencia]:
        try:
            result = await self.repository.get_by_codigo_ficha(codigo_ficha)
            return [Divergencia(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar divergências por código de ficha: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar divergências por código de ficha: {str(e)}"
            )

    async def get_divergencias_by_sessao(self, sessao_id: str) -> List[Divergencia]:
        try:
            result = await self.repository.get_by_sessao(sessao_id)
            return [Divergencia(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar divergências por sessão: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar divergências por sessão: {str(e)}"
            )

    async def get_divergencias_by_guia(self, guia_id: UUID) -> List[Divergencia]:
        try:
            result = await self.repository.get_by_guia(guia_id)
            return [Divergencia(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar divergências da guia: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar divergências da guia: {str(e)}"
            ) 