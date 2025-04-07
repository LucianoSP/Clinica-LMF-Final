from uuid import UUID
from typing import Optional, Dict, List, Any
from backend.repositories.database_supabase import SupabaseClient
from ..models.divergencia import DivergenciaCreate, DivergenciaUpdate, TipoDivergencia, StatusDivergencia
import logging
from datetime import datetime, timezone, date
from ..utils.date_utils import format_date_fields, DATE_FIELDS, formatar_data
import traceback
from math import ceil
from fastapi import HTTPException

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DivergenciaRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "divergencias"

    async def list(self,
                  limit: int = 10,
                  offset: int = 0,
                  data_inicio: Optional[str] = None,
                  data_fim: Optional[str] = None,
                  status: Optional[str] = None,
                  tipo: Optional[str] = None,
                  prioridade: Optional[str] = None,
                  order_column: str = "data_identificacao",
                  order_direction: str = "desc") -> Dict[str, Any]:
        """
        Lista divergências com paginação e filtros
        """
        try:
            # Inicia a query base
            query = self.db.from_(self.table).select("*")
            
            # Aplicar filtros
            if data_inicio:
                data_inicial = datetime.strptime(formatar_data(data_inicio), '%d/%m/%Y').date()
                query = query.gte("data_atendimento", data_inicial)
            
            if data_fim:
                data_final = datetime.strptime(formatar_data(data_fim), '%d/%m/%Y').date()
                query = query.lte("data_atendimento", data_final)
            
            if status:
                query = query.eq("status", status)
            
            if tipo:
                # Usar apenas a coluna 'tipo'
                query = query.eq("tipo", tipo)
            
            if prioridade:
                query = query.eq("prioridade", prioridade)
            
            # Aplicar ordenação
            if order_direction.lower() == "desc":
                query = query.order(order_column, desc=True)
            else:
                query = query.order(order_column)
            
            # Calcular total de registros
            count_query = self.db.from_(self.table).select("*", count="exact")
            
            # Aplicar os mesmos filtros na query de contagem
            if data_inicio:
                count_query = count_query.gte("data_atendimento", data_inicial)
            if data_fim:
                count_query = count_query.lte("data_atendimento", data_final)
            if status:
                count_query = count_query.eq("status", status)
            if tipo:
                count_query = count_query.eq("tipo", tipo)
            if prioridade:
                count_query = count_query.eq("prioridade", prioridade)
            
            # Executar query de contagem
            count_result = count_query.execute()
            total = count_result.count if hasattr(count_result, 'count') else 0
            
            # Aplicar paginação na query principal
            query = query.range(offset, offset + limit - 1)
            
            # Executar query principal
            result = query.execute()
            items = result.data if result.data else []
            
            # Formatar datas e ajustar campos nos itens
            formatted_items = []
            for item in items:
                # Mapear tipo_divergencia para tipo se necessário
                if "tipo_divergencia" in item and "tipo" not in item:
                    item["tipo"] = item["tipo_divergencia"]
                
                # Ajustar status inválidos
                if item.get("status") not in ["pendente", "em_analise", "resolvida", "ignorada"]:
                    item["status"] = "pendente"
                
                # Formatar datas
                if item.get("data_identificacao"):
                    try:
                        dt = datetime.fromisoformat(item["data_identificacao"].replace("Z", "+00:00"))
                        item["data_identificacao"] = dt.date().isoformat()
                    except (ValueError, AttributeError):
                        logger.warning(f"Data inválida em data_identificacao: {item['data_identificacao']}")
                
                for field in ["data_atendimento", "data_execucao", "data_resolucao"]:
                    if item.get(field):
                        try:
                            dt = datetime.fromisoformat(str(item[field]).replace("Z", "+00:00"))
                            item[field] = dt.date().isoformat()
                        except (ValueError, AttributeError):
                            logger.warning(f"Data inválida em {field}: {item[field]}")
                
                formatted_items.append(item)
            
            return {
                "items": formatted_items,
                "total": total,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            logger.error(f"Erro ao listar divergências: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar divergências: {str(e)}"
            )

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

    async def create(self, divergencia: DivergenciaCreate) -> Dict:
        """
        Cria uma nova divergência
        """
        try:
            # Converte o modelo para dicionário e ajusta a data_identificacao
            dados = divergencia.model_dump()
            
            # Garante que data_identificacao seja apenas a data, sem componente de tempo
            dados["data_identificacao"] = date.today().isoformat()
            
            result = self.db.from_(self.table).insert(dados).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao criar divergência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao criar divergência: {str(e)}"
            )

    async def update(self, divergencia_id: str, divergencia: DivergenciaUpdate) -> Dict:
        """Atualiza uma divergência"""
        try:
            result = self.db.from_(self.table).update(divergencia.model_dump()).eq("id", divergencia_id).execute()
            if not result.data:
                raise HTTPException(status_code=404, detail="Divergência não encontrada")
            return result.data[0]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar divergência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar divergência: {str(e)}"
            )

    async def delete(self, divergencia_id: str) -> bool:
        """Deleta uma divergência"""
        try:
            result = self.db.from_(self.table).delete().eq("id", divergencia_id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Erro ao deletar divergência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao deletar divergência: {str(e)}"
            )

    async def resolver_divergencia(self, id: UUID, user_id: UUID) -> Optional[Dict]:
        try:
            update_data = {
                "status": "resolvida",
                "data_resolucao": datetime.now().isoformat(),
                "resolvido_por": str(user_id),
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
            logger.error(f"Erro ao resolver divergencia: {str(e)}")
            raise

    async def incrementar_tentativas(self, id: UUID) -> Optional[Dict]:
        try:
            result = self.db.rpc(
                "increment_divergencia_tentativas",
                {"divergencia_id": str(id)}
            ).execute()
            
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao incrementar tentativas de resolução: {str(e)}")
            raise

    async def update_status(self, divergencia_id: str, novo_status: str, usuario_id: Optional[str] = None) -> bool:
        """
        Atualiza o status de uma divergência
        """
        try:
            dados = {
                "status": novo_status,
                "data_atualizacao": datetime.now(timezone.utc),
                "usuario_atualizacao_id": usuario_id
            }
            
            result = self.db.from_(self.table).update(dados).eq("id", divergencia_id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Erro ao atualizar status da divergência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar status da divergência: {str(e)}"
            )

    async def delete_all(self) -> bool:
        """
        Limpa todas as divergências
        """
        try:
            result = self.db.from_(self.table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar divergências: {str(e)}")
            raise

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas das divergências.
        
        Returns:
            Dict: Estatísticas das divergências
        """
        try:
            # Buscar contagem total
            total_result = self.db.from_(self.table).select("id", count="exact").execute()
            total = total_result.count if hasattr(total_result, 'count') else len(total_result.data)
            
            # Buscar contagem por tipo
            tipos_result = self.db.from_(self.table).select("tipo, count(*)").group("tipo").execute()
            por_tipo = {
                item["tipo"]: item["count"]
                for item in tipos_result.data
            } if tipos_result.data else {}
            
            # Buscar contagem por status
            status_result = self.db.from_(self.table).select("status, count(*)").group("status").execute()
            por_status = {
                item["status"]: item["count"]
                for item in status_result.data
            } if status_result.data else {}
            
            # Buscar contagem por prioridade
            prioridade_result = self.db.from_(self.table).select("prioridade, count(*)").group("prioridade").execute()
            por_prioridade = {
                item["prioridade"]: item["count"]
                for item in prioridade_result.data
            } if prioridade_result.data else {}
            
            return {
                "total": total,
                "por_tipo": por_tipo,
                "por_status": por_status,
                "por_prioridade": por_prioridade
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {
                "total": 0,
                "por_tipo": {},
                "por_status": {},
                "por_prioridade": {}
            } 