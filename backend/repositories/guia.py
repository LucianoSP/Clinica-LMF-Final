import asyncio
from uuid import UUID
from typing import Optional, Dict, List
from backend.repositories.database_supabase import SupabaseClient
import logging
from datetime import datetime, date
from ..utils.date_utils import format_date_fields, DATE_FIELDS
from ..models.guia import GuiaCreate, GuiaUpdate, DateEncoder
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GuiaRepository:

    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "guias"

    def _format_data(self, data: Dict) -> Dict:
        """Formata os dados para enviar ao banco, incluindo datas"""
        return json.loads(json.dumps(data, cls=DateEncoder))

    async def list(
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
        try:
            params = {
                "p_offset": offset,
                "p_limit": limit,
                "p_search": search if search and search.strip() != "" else None,
                "p_status": status if status and status.strip() != "" else None,
                "p_carteirinha_id": str(carteirinha_id) if carteirinha_id else None,
                "p_paciente_id": str(paciente_id) if paciente_id else None,
                "p_order_column": order_column,
                "p_order_direction": order_direction,
            }

            logger.info("Chamando RPC listar_guias_com_detalhes com parâmetros:")
            logger.info(str(params))

            result = await asyncio.to_thread(
                lambda: self.db.rpc("listar_guias_com_detalhes", params).execute()
            )
            logger.info("Resultado da RPC:")
            logger.info(str(result.data))

            # Tratar valores nulos antes de formatar as datas
            items = []
            for item in (result.data or []):
                # Garantir que dados_autorizacao seja sempre um dicionário
                if item.get("dados_autorizacao") is None:
                    item["dados_autorizacao"] = {}
                
                # Garantir que data_solicitacao seja sempre uma data válida
                if item.get("data_solicitacao") is None:
                    # Usar a data de criação como fallback ou uma data padrão
                    item["data_solicitacao"] = item.get("created_at") or datetime.now().isoformat()
                
                # Garantir que data_autorizacao seja sempre uma data válida ou None
                if item.get("data_autorizacao") is None and item.get("status") == "autorizada":
                    # Se o status é autorizada mas não tem data, usar a data de atualização
                    item["data_autorizacao"] = item.get("updated_at") or datetime.now().isoformat()
                
                items.append(format_date_fields(item, DATE_FIELDS))
            
            response = {
                "items": items,
                "total": len(items),
                "limit": limit,
                "offset": offset,
            }

            logger.info("Resposta final:")
            logger.info(str(response))
            return response
        except Exception as e:
            logger.error(f"Erro ao listar guias: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        try:
            params = {"p_guia_id": str(id)}
            result = await asyncio.to_thread(
                lambda: self.db.rpc("obter_guia_com_detalhes", params).execute()
            )
            if result.data and len(result.data) > 0:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar guia por ID: {str(e)}")
            raise

    async def get_by_carteirinha(
        self, carteirinha_id: UUID, status: Optional[str] = None
    ) -> List[Dict]:
        try:
            query = (
                self.db.from_(self.table)
                .select("*")
                .eq("carteirinha_id", str(carteirinha_id))
                .is_("deleted_at", None)
            )

            if status:
                query = query.eq("status", status)

            result = await asyncio.to_thread(query.execute)
            return [
                format_date_fields(item, DATE_FIELDS) for item in (result.data or [])
            ]
        except Exception as e:
            logger.error(f"Erro ao buscar guias por carteirinha: {str(e)}")
            raise

    async def get_by_numero_and_carteirinha(
        self, numero: str, carteirinha_id: UUID
    ) -> Optional[Dict]:
        try:
            result = await asyncio.to_thread(
                lambda: self.db.from_(self.table)
                .select("*")
                .eq("numero_guia", numero)
                .eq("carteirinha_id", str(carteirinha_id))
                .is_("deleted_at", None)
                .execute()
            )
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar guia por número e carteirinha: {str(e)}")
            raise

    async def create(self, guia: GuiaCreate) -> Optional[Dict]:
        try:
            data = guia.model_dump()
            formatted_data = self._format_data(data)
            result = await asyncio.to_thread(
                lambda: self.db.from_(self.table).insert(formatted_data).execute()
            )
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao criar guia: {str(e)}")
            raise

    async def update(self, id: UUID, guia: GuiaUpdate) -> Optional[Dict]:
        try:
            data = guia.model_dump(exclude_unset=True)
            formatted_data = self._format_data(data)
            result = await asyncio.to_thread(
                lambda: self.db.from_(self.table)
                .update(formatted_data)
                .eq("id", str(id))
                .execute()
            )
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao atualizar guia: {str(e)}")
            raise

    async def soft_delete(self, id: UUID) -> bool:
        try:
            delete_data = {"deleted_at": datetime.now().isoformat()}
            result = await asyncio.to_thread(
                lambda: self.db.from_(self.table)
                .update(delete_data)
                .eq("id", str(id))
                .is_("deleted_at", None)
                .execute()
            )
            return bool(result.data)
        except Exception as e:
            logger.error(f"Erro no repositório ao deletar guia: {str(e)}")
            raise
