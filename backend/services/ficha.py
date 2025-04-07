from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime
import logging
import json
from ..models.ficha import FichaCreate, FichaUpdate
from ..repositories.ficha import FichaRepository
from ..utils.date_utils import DateEncoder, format_date_fields, DATE_FIELDS

logger = logging.getLogger(__name__)

class FichaService:
    def __init__(self, repository: FichaRepository):
        self.repository = repository

    async def list_fichas(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "data_atendimento",
        order_direction: str = "desc",
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction,
            )
            
            # Garantir que as datas sejam serializadas corretamente
            if result and "items" in result:
                result["items"] = json.loads(json.dumps(result["items"], cls=DateEncoder))
            
            return {
                "items": result.get("items", []),
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
            }
        except Exception as e:
            logger.error(f"Erro ao listar fichas: {str(e)}")
            raise

    async def get_ficha(self, id: UUID) -> Optional[Dict]:
        try:
            result = await self.repository.get_by_id(id)
            # Garantir que as datas sejam serializadas corretamente
            if result:
                result = json.loads(json.dumps(result, cls=DateEncoder))
            return result
        except Exception as e:
            logger.error(f"Erro ao buscar ficha: {str(e)}")
            raise

    async def get_ficha_by_codigo(self, codigo: str) -> Optional[Dict]:
        try:
            result = await self.repository.get_by_codigo(codigo)
            # Garantir que as datas sejam serializadas corretamente
            if result:
                result = json.loads(json.dumps(result, cls=DateEncoder))
            return result
        except Exception as e:
            logger.error(f"Erro ao buscar ficha por código: {str(e)}")
            raise

    async def create_ficha(self, ficha: FichaCreate) -> Dict:
        try:
            result = await self.repository.create(ficha)
            # Garantir que as datas sejam serializadas corretamente
            if result:
                result = json.loads(json.dumps(result, cls=DateEncoder))
            return result
        except Exception as e:
            logger.error(f"Erro ao criar ficha: {str(e)}")
            raise

    async def update_ficha(self, id: UUID, ficha: FichaUpdate) -> Optional[Dict]:
        try:
            # Obter a ficha atual para verificar se existe
            existing = await self.repository.get_by_id(id)
            if not existing:
                logger.error(f"Ficha não encontrada: {id}")
                return None
            
            result = await self.repository.update(id, ficha)
            # Garantir que as datas sejam serializadas corretamente
            if result:
                # Usar o mesmo padrão que funciona para carteirinhas
                result = json.loads(json.dumps(result, cls=DateEncoder))
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar ficha: {str(e)}")
            raise

    async def delete_ficha(self, id: UUID) -> bool:
        try:
            return await self.repository.delete(id)
        except Exception as e:
            logger.error(f"Erro ao excluir ficha: {str(e)}")
            raise

    async def update_status(self, id: UUID, status: str) -> Optional[Dict]:
        try:
            result = await self.repository.update_status(id, status)
            # Garantir que as datas sejam serializadas corretamente
            if result:
                result = json.loads(json.dumps(result, cls=DateEncoder))
            return result
        except Exception as e:
            logger.error(f"Erro ao atualizar status da ficha: {str(e)}")
            raise

    async def get_fichas_by_paciente(
        self,
        paciente_id: str,
        offset: int = 0,
        limit: int = 100,
        order_column: str = "data_atendimento",
        order_direction: str = "desc",
    ) -> Dict:
        try:
            result = await self.repository.get_by_paciente(
                paciente_id=paciente_id,
                offset=offset,
                limit=limit,
                order_column=order_column,
                order_direction=order_direction,
            )
            
            # Garantir que as datas sejam serializadas corretamente
            if result and "items" in result:
                result["items"] = json.loads(json.dumps(result["items"], cls=DateEncoder))
            
            return result
        except Exception as e:
            logger.error(f"Erro ao listar fichas do paciente: {str(e)}")
            raise