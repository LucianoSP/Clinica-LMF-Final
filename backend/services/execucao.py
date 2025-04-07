from datetime import datetime, UTC, date
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException
from ..models.execucao import ExecucaoCreate, ExecucaoUpdate, Execucao
from ..repositories.execucao import ExecucaoRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ExecucaoService:
    def __init__(self, repository: ExecucaoRepository):
        self.repository = repository

    async def list_execucoes(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        numero_guia: Optional[str] = None,
        paciente_id: Optional[UUID] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        is_vinculada: Optional[bool] = None,
        link_manual_necessario: Optional[bool] = None,
        order_column: str = "data_execucao",
        order_direction: str = "desc"
    ) -> Dict:
        try:
            data_inicio_dt: Optional[date] = None
            if data_inicio:
                try:
                    data_inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d").date()
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de data_inicio inválido. Use YYYY-MM-DD.")
            
            data_fim_dt: Optional[date] = None
            if data_fim:
                try:
                    data_fim_dt = datetime.strptime(data_fim, "%Y-%m-%d").date()
                except ValueError:
                    raise HTTPException(status_code=400, detail="Formato de data_fim inválido. Use YYYY-MM-DD.")

            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                numero_guia=numero_guia,
                paciente_id=paciente_id,
                data_inicio=data_inicio_dt,
                data_fim=data_fim_dt,
                is_vinculada=is_vinculada,
                link_manual_necessario=link_manual_necessario,
                order_column=order_column,
                order_direction=order_direction
            )
            
            items = []
            for item in result.get("items", []):
                try:
                    execucao = Execucao.model_validate(item)
                    items.append(execucao)
                except Exception as e:
                    logger.error(f"Erro ao validar execução: {str(e)}")
                    logger.error(f"Item com erro: {item}")
                    items.append(item)
            
            if items and len(items) > 0:
                logger.debug(f"Primeiro item após validação: {items[0]}")
            
            return {
                "items": items,
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.exception(f"Erro ao listar execuções no serviço: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao listar execuções: {str(e)}"
            )

    async def get_execucao(self, id: str) -> Optional[Execucao]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Execução não encontrada")
            return Execucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar execução: {str(e)}")

    async def get_execucoes_by_guia(self, guia_id: UUID) -> List[Execucao]:
        try:
            result = await self.repository.get_by_guia(guia_id)
            return [Execucao(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar execuções da guia: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar execuções da guia: {str(e)}"
            )

    async def get_execucoes_by_sessao(self, sessao_id: UUID) -> List[Execucao]:
        try:
            result = await self.repository.get_by_sessao(sessao_id)
            return [Execucao(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar execuções da sessão: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar execuções da sessão: {str(e)}"
            )

    async def create_execucao(self, execucao: ExecucaoCreate) -> Optional[Execucao]:
        try:
            logger.info(f"Dados recebidos no serviço: {execucao.model_dump()}")
            result = await self.repository.create(execucao)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao criar execução")
            return Execucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar execução: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar execução: {str(e)}")

    async def update_execucao(self, id: UUID, execucao: ExecucaoUpdate, user_id: UUID) -> Optional[Execucao]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Execução não encontrada")

            update_data = execucao.model_dump(exclude_unset=True)
            result = await self.repository.update(id, update_data, user_id)
            
            if not result:
                raise HTTPException(status_code=404, detail="Execução não encontrada")
            return Execucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar execução: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar execução: {str(e)}")

    async def delete_execucao(self, id: UUID) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Execução não encontrada")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar execução: {str(e)}")

    async def update_status_execucao(self, id: str, status: str, user_id: str) -> Optional[Execucao]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Execução não encontrada")

            result = await self.repository.update_status(id, status, user_id)
            if not result:
                raise HTTPException(status_code=404, detail="Execução não encontrada")
            return Execucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar status da execução: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar status da execução: {str(e)}")

    async def verificar_biometria(self, id: UUID, status_biometria: str, user_id: UUID) -> Optional[Execucao]:
        try:
            data = {
                "status_biometria": status_biometria,
                "updated_at": datetime.now(UTC).isoformat(),
                "updated_by": str(user_id)
            }
            result = await self.repository.update(str(id), data, str(user_id))
            if not result:
                raise HTTPException(status_code=404, detail="Execução não encontrada")
            return Execucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar biometria: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao verificar biometria: {str(e)}")