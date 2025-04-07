from uuid import UUID
from typing import Optional, Dict, List, Tuple
from backend.repositories.database_supabase import SupabaseClient
from ..models.carteirinha import CarteirinhaCreate, CarteirinhaUpdate
import logging
from datetime import datetime
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import asyncio

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CarteirinhaRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "carteirinhas"

    async def list(self,
                   offset: int = 0,
                   limit: int = 100,
                   search: Optional[str] = None,
                   status: Optional[str] = None,
                   paciente_id: Optional[str] = None,
                   plano_saude_id: Optional[str] = None,
                   order_column: str = "numero_carteirinha",
                   order_direction: str = "asc") -> Dict:
        """Lista carteirinhas com suporte a paginação, busca e ordenação"""
        try:
            # Validar ordem
            valid_columns = ["numero_carteirinha", "data_validade", "created_at", "status"]
            if order_column not in valid_columns:
                raise ValueError(f"Coluna de ordenação inválida. Valores permitidos: {', '.join(valid_columns)}")

            # Preparar parâmetros para a função RPC
            params = {
                "p_offset": offset,
                "p_limit": limit,
                "p_search": search if search and search.strip() != "" else None,
                "p_status": status if status and status.strip() != "" else None,
                "p_paciente_id": str(paciente_id) if paciente_id else None,
                "p_plano_saude_id": str(plano_saude_id) if plano_saude_id else None,
                "p_order_column": order_column,
                "p_order_direction": order_direction,
            }

            logger.info("Chamando RPC listar_carteirinhas_com_detalhes com parâmetros:")
            logger.info(str(params))

            # Chamar a função RPC
            result = await asyncio.to_thread(
                lambda: self.db.rpc("listar_carteirinhas_com_detalhes", params).execute()
            )
            
            logger.info("Resultado da RPC:")
            logger.info(str(result.data))

            # Obter contagem total
            count_result = self.db.from_(self.table).select("id", count="exact").is_("deleted_at", "null").execute()
            total = count_result.count if hasattr(count_result, 'count') else 0

            # Formatar datas e garantir que created_by e updated_by não sejam nulos
            items = []
            for item in (result.data or []):
                # Garantir que created_by e updated_by não sejam nulos
                if item.get("created_by") is None:
                    item["created_by"] = ""
                if item.get("updated_by") is None:
                    item["updated_by"] = ""
                
                items.append(format_date_fields(item, DATE_FIELDS))

            return {
                "items": items,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Erro ao listar carteirinhas: {str(e)}")
            raise

    async def get_by_id(self, id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select(
            f"{self.table}.*, pacientes.nome as paciente_nome, planos_saude.nome as plano_saude_nome"
        ).join(
            "pacientes", f"{self.table}.paciente_id=pacientes.id"
        ).join(
            "planos_saude", f"{self.table}.plano_saude_id=planos_saude.id"
        ).eq("carteirinhas.id", str(id)).is_("carteirinhas.deleted_at", "null").execute()
        
        if result.data:
            item = result.data[0]
            # Garantir que created_by e updated_by não sejam nulos
            if item.get("created_by") is None:
                item["created_by"] = ""
            if item.get("updated_by") is None:
                item["updated_by"] = ""
            
            return format_date_fields(item, DATE_FIELDS)
        return None

    async def get_by_numero_and_plano(self, numero: str, plano_id: UUID) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*")\
            .eq("numero_carteirinha", numero)\
            .eq("plano_saude_id", str(plano_id))\
            .is_("deleted_at", "null")\
            .execute()
        
        if result.data:
            item = result.data[0]
            # Garantir que created_by e updated_by não sejam nulos
            if item.get("created_by") is None:
                item["created_by"] = ""
            if item.get("updated_by") is None:
                item["updated_by"] = ""
            
            return format_date_fields(item, DATE_FIELDS)
        
        return None

    async def get_by_paciente(self, paciente_id: UUID) -> List[Dict]:
        try:
            # Usar a sintaxe correta para selects no Supabase
            result = self.db.from_(self.table).select(
                "*,planos_saude(id,nome)"
            ).eq("paciente_id", str(paciente_id)).is_("deleted_at", "null").execute()
            
            items = []
            for item in (result.data or []):
                # Extrair o nome do plano de saúde do objeto aninhado
                if item.get("planos_saude"):
                    item["plano_saude_nome"] = item["planos_saude"].get("nome")
                
                # Garantir que created_by e updated_by não sejam nulos
                if item.get("created_by") is None:
                    item["created_by"] = ""
                if item.get("updated_by") is None:
                    item["updated_by"] = ""
                
                items.append(format_date_fields(item, DATE_FIELDS))
            
            return items
        except Exception as e:
            logger.error(f"Erro ao buscar carteirinhas por paciente: {str(e)}")
            raise

    async def create(self, carteirinha: CarteirinhaCreate) -> Optional[Dict]:
        try:
            # Converte o modelo para dicionário
            data = carteirinha.model_dump()
            
            # Adiciona timestamps
            now = datetime.now().isoformat()
            data.update({
                "created_at": now,
                "updated_at": now
            })
            
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao criar carteirinha: {str(e)}")
            raise

    async def update(self, id: UUID, carteirinha: CarteirinhaUpdate) -> Optional[Dict]:
        try:
            # Converte o modelo para dicionário
            data = carteirinha.model_dump(exclude_unset=True)
            
            # Log para depuração
            logger.info(f"Dados recebidos para atualização: {data}")
            
            # Atualiza o timestamp
            data["updated_at"] = datetime.now().isoformat()
            
            # Remover campos que não fazem parte da tabela carteirinhas
            # Esses campos podem vir do frontend ou do modelo Carteirinha
            campos_para_remover = ["paciente_nome", "plano_saude_nome"]
            for campo in campos_para_remover:
                if campo in data:
                    logger.info(f"Removendo campo {campo} dos dados de atualização")
                    del data[campo]
            
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            
            logger.info(f"Dados formatados para atualização: {formatted_data}")
            
            # Atualizar a carteirinha
            result = self.db.from_(self.table).update(formatted_data).eq("id", str(id)).is_("deleted_at", "null").execute()
            
            if not result.data:
                return None
            
            # Buscar os dados atualizados com uma consulta simples
            get_result = self.db.from_(self.table).select("*").eq("id", str(id)).is_("deleted_at", "null").execute()
            
            if not get_result.data:
                return None
                
            # Obter o item atualizado
            updated_item = get_result.data[0]
            
            # Garantir que created_by e updated_by não sejam nulos
            if updated_item.get("created_by") is None:
                updated_item["created_by"] = ""
            if updated_item.get("updated_by") is None:
                updated_item["updated_by"] = ""
            
            # Adicionar campos paciente_nome e plano_saude_nome vazios
            # Esses campos serão preenchidos pelo frontend se necessário
            updated_item["paciente_nome"] = ""
            updated_item["plano_saude_nome"] = ""
            
            return format_date_fields(updated_item, DATE_FIELDS)
        except Exception as e:
            logger.error(f"Erro ao atualizar carteirinha: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table)\
            .update({"deleted_at": "now()"})\
            .eq("id", str(id))\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
