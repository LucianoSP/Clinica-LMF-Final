from uuid import UUID
from typing import Optional, Dict, List, Tuple
from backend.repositories.database_supabase import SupabaseClient
from ..models.ficha import FichaCreate, FichaUpdate
import logging
from datetime import datetime
from ..utils.date_utils import format_date_fields, DATE_FIELDS

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FichaRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "fichas"

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "data_atendimento",
        order_direction: str = "desc",
    ) -> Dict:
        try:
            # Query paginada com todos os campos
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if search:
                search = str(search)  # Garante que search seja uma string
                query = query.or_(
                    f"codigo_ficha.ilike.%{search}%,numero_guia.ilike.%{search}%,paciente_nome.ilike.%{search}%"
                )

            # Adiciona ordenação
            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)

            # Aplica paginação
            query = query.range(offset, offset + limit - 1)

            # Executa a query
            result = query.execute()

            # Contagem total
            count_result = (
                self.db.from_(self.table)
                .select("id", count="exact")
                .is_("deleted_at", "null")
                .execute()
            )

            # Formata as datas
            items = [
                format_date_fields(item, DATE_FIELDS) for item in (result.data or [])
            ]

            return {"items": items, "total": count_result.count, "limit": limit}
        except Exception as e:
            logger.error(f"Erro ao listar fichas: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = (
            self.db.from_(self.table)
            .select("*")
            .eq("id", str(id))
            .is_("deleted_at", "null")
            .execute()
        )
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def get_by_codigo(self, codigo: str) -> Optional[Dict]:
        result = (
            self.db.from_(self.table)
            .select("*")
            .eq("codigo_ficha", codigo)
            .is_("deleted_at", "null")
            .execute()
        )
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def create(self, ficha: FichaCreate) -> Dict:
        try:
            data = ficha.model_dump()
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao criar ficha: {str(e)}")
            raise

    async def update(self, id: UUID, ficha: FichaUpdate) -> Optional[Dict]:
        try:
            data = ficha.model_dump(exclude_unset=True)
            
            # Atualiza o timestamp
            data["updated_at"] = datetime.now().isoformat()
            
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            
            result = (
                self.db.from_(self.table)
                .update(formatted_data)
                .eq("id", str(id))
                .execute()
            )
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar ficha: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = (
            self.db.from_(self.table)
            .update({"deleted_at": "now()"})
            .eq("id", str(id))
            .is_("deleted_at", "null")
            .execute()
        )
        return bool(result.data)

    async def update_status(self, id: UUID, status: str) -> Optional[Dict]:
        try:
            data = {"status": status, "updated_at": datetime.now().isoformat()}
            result = (
                self.db.from_(self.table)
                .update(data)
                .eq("id", str(id))
                .execute()
            )
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar status da ficha: {str(e)}")
            raise

    async def get_by_paciente(
        self,
        paciente_id: str,
        offset: int = 0,
        limit: int = 100,
        order_column: str = "data_atendimento",
        order_direction: str = "desc",
    ) -> Dict:
        try:
            # Primeiro busca as guias do paciente
            guias_query = (
                self.db.from_("guias")
                .select("id")
                .eq("paciente_id", paciente_id)
                .is_("deleted_at", "null")
                .execute()
            )

            if not guias_query.data:
                return {"items": [], "total": 0, "limit": limit}

            guias = [item["id"] for item in guias_query.data]

            # Query base para fichas
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            # Adiciona filtro de guias
            if guias:
                query = query.in_("guia_id", guias)

            # Adiciona ordenação
            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)

            # Aplica paginação e executa
            query = query.range(offset, offset + limit - 1)
            result = query.execute()

            # Query para contagem total
            count_result = (
                self.db.from_(self.table)
                .select("id", count="exact")
                .is_("deleted_at", "null")
                .in_("guia_id", guias)
                .execute()
            )

            # Formata as datas
            items = [
                format_date_fields(item, DATE_FIELDS) for item in (result.data or [])
            ]

            return {
                "items": items,
                "total": count_result.count if hasattr(count_result, "count") else 0,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            logger.error(f"Erro ao listar fichas por paciente: {str(e)}")
            raise
