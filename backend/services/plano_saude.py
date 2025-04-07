from datetime import datetime, UTC
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException
from ..models.paciente import PacienteCreate, PacienteUpdate, Paciente
from ..repositories.paciente import PacienteRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS
from ..models.plano_saude import PlanoSaudeCreate, PlanoSaudeUpdate, PlanoSaude
from ..repositories.plano_saude import PlanoSaudeRepository
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlanoSaudeService:

    def __init__(self, repository: PlanoSaudeRepository):
        self.repository = repository

    async def list_planos_saude(self,
                                offset: int = 0,
                                limit: int = 100,
                                search: Optional[str] = None,
                                order_column: str = "nome",
                                order_direction: str = "asc") -> Dict:
        try:
            return await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction
            )
        except Exception as e:
            logger.error(f"Erro ao listar planos de saúde: {str(e)}")
            raise

    async def get_plano_saude(self, id: UUID) -> Optional[PlanoSaude]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404,
                                    detail="Plano de saúde não encontrado")
            return PlanoSaude(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar plano de saúde: {str(e)}")

    async def create_plano_saude(self, plano: PlanoSaudeCreate):
        try:
            logger.info(f"Dados recebidos no serviço: {plano.model_dump()}")
            return await self.repository.create(plano)
        except Exception as e:
            logger.error(f"Erro ao criar plano de saúde: {str(e)}")
            raise

    async def update_plano_saude(self, id: UUID,
                                  plano_saude: PlanoSaudeUpdate,
                                  user_id: UUID) -> Optional[PlanoSaude]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404,
                                    detail="Plano de saúde não encontrado")

            # Convertemos o modelo Pydantic para dict
            data = plano_saude.model_dump(exclude_unset=True)

            # Adiciona updated_at e updated_by
            data["updated_at"] = datetime.now(UTC).isoformat()
            data["updated_by"] = str(user_id)

            result = await self.repository.update(id, data, user_id)
            if not result:
                raise HTTPException(status_code=404,
                                    detail="Plano de saúde não encontrado")
            return PlanoSaude(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar plano de saúde: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar plano de saúde: {str(e)}")

    async def delete_plano_saude(self, id: UUID) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404,
                                    detail="Plano de saúde não encontrado")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar plano de saúde: {str(e)}")
