from uuid import UUID
from typing import Optional, Dict, List
from backend.repositories.database_supabase import SupabaseClient
import logging
from datetime import datetime
from decimal import Decimal
from ..utils.date_utils import format_date_fields, DATE_FIELDS
from ..models.procedimento import ProcedimentoCreate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def convert_decimal_to_float(data: Dict) -> Dict:
    """Converte valores Decimal para float no dicionário"""
    decimal_fields = ['valor', 'valor_filme', 'valor_operacional', 'valor_total']
    converted = data.copy()
    
    for field in decimal_fields:
        if field in converted and isinstance(converted[field], Decimal):
            converted[field] = float(converted[field])
    
    return converted

class ProcedimentoRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "procedimentos"

    async def list(self,
                  offset: int = 0,
                  limit: int = 100,
                  search: Optional[str] = None,
                  order_column: str = "nome",
                  order_direction: str = "asc",
                  tipo: Optional[str] = None,
                  ativo: Optional[bool] = None) -> Dict:
        try:
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if search:
                query = query.or_(f"nome.ilike.%{search}%,codigo.ilike.%{search}%")

            if tipo:
                query = query.eq("tipo", tipo)

            if ativo is not None:
                query = query.eq("ativo", ativo)

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
            logger.error(f"Erro ao listar procedimentos: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*")\
            .eq("codigo", codigo)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None

    async def create(self, procedimento: ProcedimentoCreate):
        try:
            data = procedimento.model_dump() if hasattr(procedimento, 'model_dump') else procedimento
            data = convert_decimal_to_float(data)
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao criar procedimento: {str(e)}")
            raise

    async def update(self, id: UUID, data: Dict, user_id: UUID) -> Optional[Dict]:
        try:
            # Converter valores Decimal para float
            update_data = convert_decimal_to_float(data)
            logger.debug(f"Dados convertidos para atualização: {update_data}")
            
            update_data.update({
                "updated_by": str(user_id)
            })
            
            result = self.db.from_(self.table).update(update_data)\
                .eq("id", str(id))\
                .is_("deleted_at", "null")\
                .execute()
            
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar procedimento: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table)\
            .update({"deleted_at": "now()"})\
            .eq("id", str(id))\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data) 