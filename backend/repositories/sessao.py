from uuid import UUID
from typing import Optional, Dict, List
from backend.repositories.database_supabase import SupabaseClient
import logging
from datetime import datetime
from ..utils.date_utils import format_date_fields, DATE_FIELDS
from ..models.sessao import SessaoCreate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SessaoRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "sessoes"

    async def list(self,
                  offset: int = 0,
                  limit: int = 100,
                  search: Optional[str] = None,
                  order_column: str = "data_sessao",
                  order_direction: str = "desc") -> Dict:
        try:
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if search:
                query = query.or_(f"observacoes.ilike.%{search}%")

            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)

            query = query.range(offset, offset + limit - 1)
            result = query.execute()

            count_result = self.db.from_(self.table).select("id", count="exact").is_("deleted_at", "null").execute()

            items = [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

            return {
                "items": items,
                "total": count_result.count if hasattr(count_result, 'count') else 0,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Erro ao listar sessões: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def get_by_guia(self, guia_id: UUID) -> List[Dict]:
        result = self.db.from_(self.table).select("*")\
            .eq("guia_id", str(guia_id))\
            .is_("deleted_at", "null")\
            .execute()
        return [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

    async def get_by_paciente(self, paciente_id: UUID) -> List[Dict]:
        result = self.db.from_(self.table).select("*")\
            .eq("paciente_id", str(paciente_id))\
            .is_("deleted_at", "null")\
            .execute()
        return [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

    async def create(self, sessao: SessaoCreate):
        try:
            data = sessao.model_dump()
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao criar sessão: {str(e)}")
            raise

    async def update(self, id: UUID, data: Dict, user_id: UUID) -> Optional[Dict]:
        try:
            update_data = {
                **data,
                "updated_by": str(user_id)
            }

            result = self.db.from_(self.table).update(update_data).eq("id", str(id)).is_("deleted_at", "null").execute()

            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar sessão: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table).update({"deleted_at": "now()"}).eq("id", str(id)).is_("deleted_at", "null").execute()
        return bool(result.data)

    async def update_status(self, id: UUID, status: str, user_id: UUID) -> Optional[Dict]:
        try:
            update_data = {
                "status": status,
                "updated_by": str(user_id),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.db.from_(self.table).update(update_data)\
                .eq("id", str(id))\
                .is_("deleted_at", "null")\
                .execute()
            
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar status da sessão: {str(e)}")
            raise

    async def get_by_ficha_presenca(self, ficha_id: UUID) -> List[Dict]:
        """Busca todas as sessões de uma ficha"""
        result = self.db.from_(self.table).select("*")\
            .eq("ficha_id", str(ficha_id))\
            .is_("deleted_at", "null")\
            .order("ordem_execucao", desc=False)\
            .execute()
        return [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

    # Alias para manter compatibilidade com o serviço
    async def list_by_guia(self, guia_id: UUID) -> List[Dict]:
        return await self.get_by_guia(guia_id) 