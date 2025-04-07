from uuid import UUID
from typing import Optional, Dict, List, Tuple
from backend.repositories.database_supabase import SupabaseClient
import logging
from ..models.plano_saude import PlanoSaudeCreate
from ..utils.date_utils import format_date_fields, DATE_FIELDS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PlanoSaudeRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "planos_saude"

    async def list(self,
                  offset: int = 0,
                  limit: int = 100,
                  search: Optional[str] = None,
                  order_column: str = "nome",
                  order_direction: str = "asc") -> Dict:
        try:
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if search:
                query = query.or_(f"nome.ilike.%{search}%")

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
            logger.error(f"Erro ao listar planos de saúde: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
        return result.data[0] if result.data else None

    async def get_by_registro_ans(self, registro_ans: str) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("registro_ans", registro_ans).is_("deleted_at", "null").execute()
        return result.data[0] if result.data else None

    async def create(self, plano: PlanoSaudeCreate):
        try:
            data = plano.model_dump()
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao criar plano de saúde: {str(e)}")
            raise

    async def update(self, id: UUID, data: Dict, user_id: UUID) -> Optional[Dict]:
        try:
            update_data = {
                **data,
                "updated_by": str(user_id)
            }
            
            result = self.db.from_(self.table).update(update_data).eq("id", str(id)).is_("deleted_at", "null").execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao atualizar plano de saúde: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table).update({"deleted_at": "now()"}).eq("id", str(id)).is_("deleted_at", "null").execute()
        return bool(result.data)