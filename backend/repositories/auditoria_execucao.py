from uuid import UUID
from typing import Optional, Dict, List
from backend.repositories.database_supabase import SupabaseClient
from ..models.auditoria_execucao import AuditoriaExecucaoCreate, AuditoriaExecucaoUpdate
import logging
from datetime import datetime, date
from ..utils.date_utils import format_date_fields, DATE_FIELDS, formatar_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Adiciona campos específicos de data da auditoria
AUDITORIA_DATE_FIELDS = DATE_FIELDS + ['data_execucao', 'data_inicial', 'data_final']

class AuditoriaExecucaoRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "auditoria_execucoes"

    async def list(self,
                   offset: int = 0,
                   limit: int = 100,
                   search: Optional[str] = None,
                   order_column: str = "data_execucao",
                   order_direction: str = "desc") -> Dict:
        try:
            query = self.db.from_(self.table).select("*").is_("deleted_at", "null")

            if search:
                query = query.or_(f"status.ilike.%{search}%")

            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)

            query = query.range(offset, offset + limit - 1)
            result = query.execute()
            count_result = self.db.from_(self.table).select("id", count="exact").is_("deleted_at", "null").execute()
            items = [format_date_fields(item, AUDITORIA_DATE_FIELDS) for item in (result.data or [])]

            return {
                "items": items,
                "total": count_result.count if hasattr(count_result, 'count') else 0,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Erro ao listar auditorias de execuções: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], AUDITORIA_DATE_FIELDS)
        return None

    async def create(self, auditoria: AuditoriaExecucaoCreate) -> Optional[Dict]:
        try:
            # Converte o modelo para dicionário
            data = auditoria.model_dump()
            
            # Adiciona timestamps
            now = datetime.now()
            data.update({
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            })
            
            # Formata as datas usando formatar_data
            if data.get('data_execucao'):
                data['data_execucao'] = data['data_execucao'].isoformat()
            if data.get('data_inicial'):
                data['data_inicial'] = data['data_inicial'].isoformat()
            if data.get('data_final'):
                data['data_final'] = data['data_final'].isoformat()
            
            result = self.db.from_(self.table).insert(data).execute()
            if result.data:
                return format_date_fields(result.data[0], AUDITORIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao criar auditoria de execução: {str(e)}")
            raise

    async def update(self, id: UUID, data: Dict) -> Optional[Dict]:
        try:
            # Se data for um modelo Pydantic, converte para dicionário
            if hasattr(data, 'model_dump'):
                data = data.model_dump()
            
            # Adiciona timestamp de atualização se não foi fornecido
            if "updated_at" not in data:
                data["updated_at"] = datetime.now().isoformat()
            
            # Formata as datas
            for field in ['data_execucao', 'data_inicial', 'data_final']:
                if field in data and data[field] is not None:
                    if isinstance(data[field], (datetime, date)):
                        data[field] = data[field].isoformat()
            
            result = self.db.from_(self.table).update(data)\
                .eq("id", str(id))\
                .is_("deleted_at", "null")\
                .execute()
            
            if result.data:
                return format_date_fields(result.data[0], AUDITORIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar auditoria de execução: {str(e)}")
            raise

    async def get_ultima_auditoria(self) -> Optional[Dict]:
        """Obtém o resultado da última auditoria realizada"""
        try:
            result = self.db.from_(self.table)\
                .select("*")\
                .is_("deleted_at", "null")\
                .order("data_execucao", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return format_date_fields(result.data[0], AUDITORIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar última auditoria: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table)\
            .update({"deleted_at": datetime.now().isoformat()})\
            .eq("id", str(id))\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)

    async def registrar_execucao(self,
                               data_inicial: Optional[str] = None,
                               data_final: Optional[str] = None,
                               total_protocolos: int = 0,
                               total_divergencias: int = 0,
                               divergencias_por_tipo: Dict = None,
                               total_fichas: int = 0,
                               total_execucoes: int = 0,
                               total_resolvidas: int = 0,
                               data_execucao: Optional[str] = None,
                               status: str = "concluido") -> Dict:
        """Registra uma nova execução de auditoria com seus metadados"""
        try:
            # Garantir que todos os tipos de divergência existam no dicionário
            tipos_base = {
                "execucao_sem_sessao": 0,
                "sessao_sem_execucao": 0,
                "data_divergente": 0,
                "sessao_sem_assinatura": 0,
                "guia_vencida": 0,
                "quantidade_excedida": 0,
                "duplicidade": 0
            }
            
            # Mesclar com os valores recebidos
            if divergencias_por_tipo:
                tipos_base.update(divergencias_por_tipo)

            # Garantir que data_execucao nunca seja nulo (CRUCIAL para atender à restrição NOT NULL do banco)
            if not data_execucao:
                data_execucao = datetime.now().isoformat()

            # Criar os dados completos para inserção
            data = {
                "data_inicial": data_inicial,
                "data_final": data_final,
                "total_protocolos": total_protocolos,
                "total_divergencias": total_divergencias,
                "divergencias_por_tipo": tipos_base,
                "total_fichas": total_fichas,
                "total_execucoes": total_execucoes,
                "total_resolvidas": total_resolvidas,
                "data_execucao": data_execucao,  # Campo obrigatório
                "status": status,  # Usa o valor recebido ou o padrão "concluido"
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            result = self.db.from_(self.table).insert(data).execute()
            if result.data:
                return format_date_fields(result.data[0], AUDITORIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao registrar execução de auditoria: {str(e)}")
            raise

    async def get_by_periodo(self,
                           data_inicial: datetime,
                           data_final: datetime) -> List[Dict]:
        """Obtém auditorias em um período específico"""
        try:
            result = self.db.from_(self.table)\
                .select("*")\
                .gte("data_execucao", data_inicial.isoformat())\
                .lte("data_execucao", data_final.isoformat())\
                .is_("deleted_at", "null")\
                .execute()
            
            return [format_date_fields(item, AUDITORIA_DATE_FIELDS) for item in (result.data or [])]
        except Exception as e:
            logger.error(f"Erro ao buscar auditorias por período: {str(e)}")
            raise

    async def get_by_id(self, id: str) -> Optional[Dict]:
        """Obtém uma auditoria pelo ID"""
        try:
            result = self.db.from_(self.table)\
                .select("*")\
                .eq("id", id)\
                .is_("deleted_at", "null")\
                .execute()
            
            if result.data and len(result.data) > 0:
                return format_date_fields(result.data[0], AUDITORIA_DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar auditoria: {str(e)}")
            raise