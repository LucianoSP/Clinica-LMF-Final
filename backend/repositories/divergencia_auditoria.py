from uuid import UUID
from typing import Optional, Dict, List
from backend.repositories.database_supabase import SupabaseClient
import logging
from datetime import datetime
from ..utils.date_utils import format_date_fields, DATE_FIELDS, formatar_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Adiciona campos específicos de data da divergência
DIVERGENCIA_DATE_FIELDS = DATE_FIELDS + ['data_execucao', 'data_atendimento']

class DivergenciaAuditoriaRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "divergencias"

    async def list(self,
                  page: int = 1,
                  per_page: int = 10,
                  data_inicio: Optional[str] = None,
                  data_fim: Optional[str] = None,
                  status: Optional[str] = None,
                  tipo: Optional[str] = None,
                  prioridade: Optional[str] = None) -> Dict:
        """Lista divergências com paginação e filtros"""
        try:
            offset = (page - 1) * per_page
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if status:
                query = query.eq("status", status)
            if tipo:
                query = query.eq("tipo", tipo)
            if prioridade:
                query = query.eq("prioridade", prioridade)
            if data_inicio:
                query = query.gte("data_execucao", data_inicio)
            if data_fim:
                query = query.lte("data_execucao", data_fim)

            # Primeiro faz a contagem
            count_result = query.execute()
            total = len(count_result.data) if count_result.data else 0

            # Depois aplica a paginação
            query = query.range(offset, offset + per_page - 1)
            result = query.execute()

            items = [format_date_fields(item, DIVERGENCIA_DATE_FIELDS) for item in (result.data or [])]

            return {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
        except Exception as e:
            logger.error(f"Erro ao listar divergências: {str(e)}")
            raise

    async def create(self, divergencia: Dict) -> Dict:
        """Registra uma nova divergência"""
        try:
            result = self.db.from_(self.table).insert(divergencia).execute()
            if result.data:
                return format_date_fields(result.data[0], DIVERGENCIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao registrar divergência: {str(e)}")
            raise

    async def update_status(self, id: str, status: str, user_id: Optional[str] = None) -> Dict:
        """Atualiza o status de uma divergência"""
        try:
            data = {
                "status": status,
                "updated_at": datetime.now().isoformat(),
                "updated_by": user_id
            }
            result = self.db.from_(self.table)\
                .update(data)\
                .eq("id", id)\
                .execute()
            
            if result.data:
                return format_date_fields(result.data[0], DIVERGENCIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar status da divergência: {str(e)}")
            raise

    async def delete_all(self) -> bool:
        """Limpa a tabela de divergências"""
        try:
            result = self.db.from_(self.table)\
                .update({"deleted_at": datetime.now().isoformat()})\
                .is_("deleted_at", "null")\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar divergências: {str(e)}")
            raise

    async def update_ficha_ids(self, divergencias: List[Dict]) -> bool:
        """Atualiza os ficha_ids nas divergências"""
        try:
            for divergencia in divergencias:
                if divergencia.get("ficha_id"):
                    self.db.from_(self.table)\
                        .update({
                            "ficha_id": divergencia["ficha_id"],
                            "data_atendimento": divergencia.get("data_atendimento")
                        })\
                        .eq("id", divergencia["id"])\
                        .execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar ficha_ids: {str(e)}")
            raise

    async def get_statistics(self) -> Dict:
        """Obtém estatísticas das divergências"""
        try:
            # Buscar contagem por tipo e status
            result = self.db.from_(self.table)\
                .select("tipo, status, count")\
                .group("tipo, status")\
                .execute()
            
            # Inicializar contadores
            por_tipo = {}
            por_status = {"pendente": 0, "em_analise": 0, "resolvida": 0, "cancelada": 0}
            
            # Processar resultados
            for row in result.data:
                tipo = row.get("tipo")
                status = row.get("status", "pendente")
                count = row.get("count", 0)
                
                # Contagem por tipo
                if tipo:
                    por_tipo[tipo] = por_tipo.get(tipo, 0) + int(count)
                
                # Contagem por status
                if status in por_status:
                    por_status[status] += int(count)
            
            # Buscar contagem total
            total_result = self.db.from_(self.table)\
                .select("id", count="exact")\
                .execute()
            
            total = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
            
            return {
                "total": total,
                "por_tipo": por_tipo,
                "por_status": por_status
            }
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {str(e)}")
            raise
