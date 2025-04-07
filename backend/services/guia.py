from datetime import datetime, UTC, date
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException
from ..models.guia import GuiaCreate, GuiaUpdate, Guia
from ..repositories.guia import GuiaRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GuiaService:
    def __init__(self, repository: GuiaRepository):
        self.repository = repository

    async def list_guias(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        carteirinha_id: Optional[str] = None,
        paciente_id: Optional[str] = None,
        order_column: str = "data_solicitacao",
        order_direction: str = "desc",
    ) -> Dict:
        """Lista guias com opções de filtro e paginação"""
        try:
            return await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                status=status,
                carteirinha_id=carteirinha_id,
                paciente_id=paciente_id,
                order_column=order_column,
                order_direction=order_direction,
            )
        except Exception as e:
            logger.error(f"Erro ao listar guias: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao listar guias: {str(e)}"
            )

    async def get_guia(self, id: UUID) -> Optional[Guia]:
        """Busca uma guia por ID"""
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Guia não encontrada")
            return Guia(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Erro ao buscar guia: {str(e)}"
            )

    async def get_guias_by_carteirinha(
        self, carteirinha_id: UUID, status: Optional[str] = None
    ) -> List[Guia]:
        """Busca guias por carteirinha com opção de filtro por status"""
        try:
            result = await self.repository.get_by_carteirinha(carteirinha_id, status)
            return [Guia(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar guias da carteirinha: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao buscar guias da carteirinha: {str(e)}"
            )

    async def create_guia(self, guia: GuiaCreate) -> Guia:
        """Cria uma nova guia"""
        try:
            logger.info(f"Dados recebidos no serviço: {guia.model_dump()}")

            # Verifica se já existe uma guia com o mesmo número para a carteirinha
            existing = await self.repository.get_by_numero_and_carteirinha(
                guia.numero_guia, guia.carteirinha_id
            )
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="Já existe uma guia com este número para esta carteirinha",
                )

            result = await self.repository.create(guia)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao criar guia")
            return Guia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar guia: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar guia: {str(e)}")

    async def update_guia(self, id: UUID, guia: GuiaUpdate) -> Optional[Guia]:
        """Atualiza uma guia existente"""
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Guia não encontrada")

            result = await self.repository.update(id, guia)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao atualizar guia")
            return Guia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar guia: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao atualizar guia: {str(e)}"
            )

    async def delete_guia(self, id: UUID) -> bool:
        """Deleta uma guia (soft delete)"""
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Guia não encontrada")

            result = await self.repository.soft_delete(id)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao deletar guia")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao deletar guia: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao deletar guia: {str(e)}"
            )

    async def update_guia_status(
        self, id: UUID, novo_status: str, motivo: Optional[str] = None
    ) -> Optional[Guia]:
        """Atualiza o status de uma guia"""
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Guia não encontrada")

            # Prepara os dados de atualização
            update_data = {
                "status": novo_status,
                "updated_at": datetime.now(UTC).isoformat(),
            }

            if motivo:
                update_data[
                    "motivo_negacao" if novo_status == "negada" else "observacoes"
                ] = motivo

            # Atualiza o histórico de status
            historico = existing.get("historico_status", [])
            historico.append(
                {
                    "status": novo_status,
                    "data": datetime.now(UTC).isoformat(),
                    "observacao": motivo,
                }
            )
            update_data["historico_status"] = historico

            result = await self.repository.update(id, GuiaUpdate(**update_data))
            if not result:
                raise HTTPException(
                    status_code=500, detail="Erro ao atualizar status da guia"
                )
            return Guia(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar status da guia: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao atualizar status da guia: {str(e)}"
            )
