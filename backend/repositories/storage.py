from uuid import UUID
from typing import Optional, Dict, List
from backend.repositories.database_supabase import SupabaseClient
import logging
from datetime import datetime
from ..utils.date_utils import format_date_fields, DATE_FIELDS
from ..models.storage import StorageCreate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class StorageRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "storage"

    async def list(self,
                  offset: int = 0,
                  limit: int = 100,
                  search: Optional[str] = None,
                  order_column: str = "created_at",
                  order_direction: str = "desc") -> Dict:
        try:
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if search:
                query = query.or_(f"nome.ilike.%{search}%,url.ilike.%{search}%")

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
            logger.error(f"Erro ao listar arquivos: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def get_by_entidade(self, entidade: str, entidade_id: str) -> List[Dict]:
        result = self.db.from_(self.table).select("*")\
            .eq("entidade", entidade)\
            .eq("entidade_id", entidade_id)\
            .is_("deleted_at", "null")\
            .execute()
        return [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

    async def get_by_path(self, path: str) -> Optional[Dict]:
        """Busca um arquivo pela URL no R2"""
        result = self.db.from_(self.table).select("*").eq("url", path).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def create(self, storage: StorageCreate):
        try:
            # Usa mode='json' para garantir que UUIDs sejam serializados corretamente
            data = storage.model_dump(mode='json')
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao criar arquivo: {str(e)}")
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
            logger.error(f"Erro ao atualizar arquivo: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table).update({"deleted_at": "now()"}).eq("id", str(id)).is_("deleted_at", "null").execute()
        return bool(result.data)
