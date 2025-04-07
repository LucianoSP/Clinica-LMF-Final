from uuid import UUID
from typing import Optional, Dict, List
from fastapi import HTTPException
from backend.repositories.database_supabase import SupabaseClient
import logging
from datetime import datetime, date
from ..utils.date_utils import format_date_fields, DATE_FIELDS
from ..models.execucao import ExecucaoCreate, ExecucaoUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ExecucaoRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "execucoes"

    async def create(self, execucao: ExecucaoCreate):
        try:
            logger.info(f"Criando execução pelo usuário: {execucao.created_by}")
            data = execucao.model_dump()
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                logger.info(f"Execução criada com sucesso. ID: {result.data[0]['id']}")
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao criar execução. Usuário: {execucao.created_by}. Erro: {str(e)}")
            raise

    async def update(self, id: UUID, execucao: Dict):
        try:
            # Note: A assinatura foi alterada para receber um Dict genérico
            # para evitar conflito com o tipo ExecucaoUpdate importado.
            # O user_id agora deve ser passado dentro do dict 'execucao'.
            user_id = execucao.get('updated_by')
            logger.info(f"Atualizando execução {id} pelo usuário: {user_id}")
            # Verifica se o registro existe e não está deletado
            existing = await self.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Execução não encontrada")

            # Não permite alterar campos de auditoria anteriores
            data = execucao.copy() # Usar uma cópia
            data.pop("created_by", None)  # Não permite alterar created_by
            data.pop("created_at", None)  # Não permite alterar created_at

            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            result = self.db.from_(self.table).update(formatted_data).eq('id', str(id)).execute()
            if result.data:
                # Formata as datas na resposta
                logger.info(f"Execução {id} atualizada com sucesso")
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar execução {id}. Usuário: {user_id}. Erro: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        try:
            result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar execução por ID {id}: {str(e)}")
            raise

    async def list(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        numero_guia: Optional[str] = None,
        paciente_id: Optional[UUID] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
        is_vinculada: Optional[bool] = None,
        link_manual_necessario: Optional[bool] = None,
        order_column: str = "data_execucao",
        order_direction: str = "desc"
    ) -> Dict:
        try:
            logger.info("Listando execuções com novos filtros")
            query = self.db.from_(self.table).select("*", count="exact").is_("deleted_at", "null")

            if search:
                query = query.or_(
                    f"paciente_nome.ilike.%{search}%,"
                    f"paciente_carteirinha.ilike.%{search}%,"
                    f"numero_guia.ilike.%{search}%,"
                    f"codigo_ficha.ilike.%{search}%,"
                    f"profissional_executante.ilike.%{search}%,"
                    f"observacoes.ilike.%{search}%"
                )
            if numero_guia:
                query = query.eq("numero_guia", numero_guia)
            if paciente_id:
                pass
            if data_inicio:
                query = query.gte("data_execucao", data_inicio.isoformat())
            if data_fim:
                query = query.lte("data_execucao", data_fim.isoformat())
            if is_vinculada is not None:
                if is_vinculada:
                    query = query.not_.is_("sessao_id", "null")
                else:
                    query = query.is_("sessao_id", "null")
            if link_manual_necessario is not None:
                query = query.eq("link_manual_necessario", link_manual_necessario)

            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)

            query = query.range(offset, offset + limit - 1)
            result = query.execute()

            items = [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]
            
            if items and len(items) > 0:
                logger.debug(f"Primeiro item retornado: {items[0]}")

            total_count = result.count if hasattr(result, 'count') else 0

            return {
                "items": items,
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.exception(f"Erro ao listar execuções no repositório: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro interno no repositório ao listar execuções: {str(e)}")

    async def get_by_guia(self, guia_id: UUID) -> List[Dict]:
        try:
            result = self.db.from_(self.table).select("*")\
                .eq("guia_id", str(guia_id))\
                .is_("deleted_at", "null")\
                .execute()
            return [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]
        except Exception as e:
            logger.error(f"Erro ao buscar execuções por guia {guia_id}: {str(e)}")
            raise

    async def get_by_sessao(self, sessao_id: UUID) -> List[Dict]:
        try:
            result = self.db.from_(self.table).select("*")\
                .eq("sessao_id", str(sessao_id))\
                .is_("deleted_at", "null")\
                .execute()
            return [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]
        except Exception as e:
            logger.error(f"Erro ao buscar execuções por sessão {sessao_id}: {str(e)}")
            raise

    async def delete(self, id: UUID, user_id: str) -> bool:
        try:
            logger.info(f"Deletando execução {id} pelo usuário {user_id}")
            result = self.db.from_(self.table)\
                .update({
                    "deleted_at": datetime.now().isoformat(),
                    "updated_by": user_id
                })\
                .eq("id", str(id))\
                .is_("deleted_at", "null")\
                .execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Erro ao deletar execução {id}: {str(e)}")
            raise

    async def update_status(self, id: UUID, status: str, user_id: str) -> Optional[Dict]:
        try:
            logger.info(f"Atualizando status da execução {id} para {status} pelo usuário {user_id}")
            update_data = {
                "status": status,
                "updated_by": user_id,
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
            logger.error(f"Erro ao atualizar status da execução {id}: {str(e)}")
            raise