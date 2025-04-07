from uuid import UUID
from typing import Optional, Dict, List, Tuple, Any
from backend.repositories.database_supabase import SupabaseClient, get_supabase_client
from backend.models.paciente import PacienteCreate, PacienteUpdate
import logging
from datetime import datetime
from ..utils.date_utils import format_date_fields, DATE_FIELDS, DateEncoder
import json
from fastapi import HTTPException
from ..config.config import supabase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PacienteRepository:
    def __init__(self, db: SupabaseClient):
        self.db = db
        self.table = "pacientes"

    async def list(self,
                  offset: int = 0,
                  limit: int = 100,
                  search: Optional[str] = None,
                  fields: str = "*",
                  order_column: str = "nome",
                  order_direction: str = "asc") -> Dict:
        """
        Lista pacientes com paginação, busca e ordenação.
        
        Args:
            offset: Offset para paginação
            limit: Limite de resultados por página
            search: Termo de busca
            fields: Campos a serem retornados (ex: "id,nome,cpf"). Por padrão, retorna todos os campos.
            order_column: Coluna para ordenação
            order_direction: Direção da ordenação (asc ou desc)
            
        Returns:
            Dicionário com os resultados paginados
        """
        try:
            # Query paginada com os campos especificados
            query = self.db.from_(self.table).select(fields).is_("deleted_at", "null")

            if search:
                query = query.or_(f"nome.ilike.%{search}%,cpf.ilike.%{search}%")

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
            count_query = self.db.from_(self.table).select("id", count="exact").is_("deleted_at", "null")
            
            # Aplica o mesmo filtro de busca na contagem total
            if search:
                count_query = count_query.or_(f"nome.ilike.%{search}%,cpf.ilike.%{search}%")
                
            count_result = count_query.execute()

            # Formata as datas
            items = [format_date_fields(item, DATE_FIELDS) for item in (result.data or [])]

            return {
                "items": items,
                "total": count_result.count if hasattr(count_result, 'count') else 0,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Erro ao listar pacientes: {str(e)}")
            raise

    async def get_by_id(self, id: UUID, fields: str = "*") -> Optional[Dict]:
        """
        Busca um paciente pelo ID.
        
        Args:
            id: ID do paciente
            fields: Campos a serem retornados (ex: "id,nome,cpf"). Por padrão, retorna todos os campos.
        
        Returns:
            Dicionário com os dados do paciente ou None se não encontrado
        """
        result = self.db.from_(self.table).select(fields).eq("id", str(id)).is_("deleted_at", "null").execute()
        if result.data:
            return format_date_fields(result.data[0], DATE_FIELDS)
        return None

    async def create(self, paciente: PacienteCreate):
        try:
            data = paciente.model_dump()
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            
            # Verificar serialização antes de enviar ao banco
            try:
                # Testar serialização
                json.dumps(formatted_data)
            except TypeError:
                # Se falhar, usar o DateEncoder para serializar
                formatted_data = json.loads(json.dumps(formatted_data, cls=DateEncoder))
            
            result = self.db.from_(self.table).insert(formatted_data).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao criar paciente: {str(e)}")
            raise

    async def update(self, id: UUID, paciente):
        try:
            # Verifica se é um dicionário ou um objeto PacienteUpdate
            if hasattr(paciente, 'model_dump'):
                data = paciente.model_dump()
            else:
                data = dict(paciente)  # Faz uma cópia para não alterar o original
            
            # Importante: Primeiro, buscar o paciente atual para verificar campos com restrição NOT NULL
            current_paciente = await self.get_by_id(id)
            if not current_paciente:
                raise Exception(f"Paciente com ID {id} não encontrado")
                
            # Se o paciente atual tem id_origem, o valor NÃO deve ser alterado para NULL
            if current_paciente.get('id_origem') and (data.get('id_origem') is None or data.get('id_origem') == 0):
                # Manter o valor original de id_origem
                data['id_origem'] = current_paciente['id_origem']
                logger.info(f"Preservando id_origem original: {data['id_origem']}")
            
            # O mesmo para importado (se for NOT NULL no banco)
            if current_paciente.get('importado') is not None and data.get('importado') is None:
                data['importado'] = current_paciente['importado']
            
            # Garantir que updated_by não seja nulo
            if data.get('updated_by') is None:
                data['updated_by'] = current_paciente.get('updated_by') or 'sistema'
                logger.info(f"Definindo updated_by para: {data['updated_by']}")
            
            # Formata as datas antes de enviar para o banco
            formatted_data = format_date_fields(data, DATE_FIELDS)
            
            # Verificar serialização antes de enviar ao banco
            try:
                # Testar serialização
                json.dumps(formatted_data)
            except TypeError:
                # Se falhar, usar o DateEncoder para serializar
                formatted_data = json.loads(json.dumps(formatted_data, cls=DateEncoder))
            
            result = self.db.from_(self.table).update(formatted_data).eq('id', str(id)).execute()
            if result.data:
                # Formata as datas na resposta
                return format_date_fields(result.data[0], DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro no repositório ao atualizar paciente: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        result = self.db.from_(self.table).update({"deleted_at": "now()"}).eq("id", str(id)).is_("deleted_at", "null").execute()
        return bool(result.data)

    async def get_by_cpf(self, cpf: str) -> Optional[Dict]:
        result = self.db.from_(self.table).select("*").eq("cpf", cpf).is_("deleted_at", "null").execute()
        return result.data[0] if result.data else None

    async def get_by_id_origem(self, id_origem: int) -> Optional[Dict]:
        """Busca um paciente pelo ID de origem."""
        try:
            result = self.db.from_(self.table).select("*").eq("id_origem", id_origem).is_("deleted_at", "null").execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erro ao buscar paciente por id_origem: {str(e)}")
            return None

    async def get_last_update(self) -> Dict:
        """
        Obtém a data da última atualização e criação na tabela de pacientes.
        
        Returns:
            Dict: Um dicionário com as datas de última criação e atualização
        """
        try:
            # Abordagem mais direta para evitar problemas com await
            # Buscamos todos os dados em uma única consulta
            result = self.db.from_(self.table).select("created_at, updated_at").is_("deleted_at", "null").execute()
            
            # Processamos os resultados em memória
            created_dates = []
            updated_dates = []
            
            if result.data:
                for row in result.data:
                    if row.get('created_at'):
                        created_dates.append(row['created_at'])
                    if row.get('updated_at'):
                        updated_dates.append(row['updated_at'])
            
            # Ordenamos as datas e pegamos a mais recente
            ultima_criacao = max(created_dates) if created_dates else None
            ultima_atualizacao = max(updated_dates) if updated_dates else None
            
            # Formatamos as datas
            if ultima_criacao:
                ultima_criacao_dict = {'created_at': ultima_criacao}
                ultima_criacao = format_date_fields(ultima_criacao_dict, ['created_at'])['created_at']
            
            if ultima_atualizacao:
                ultima_atualizacao_dict = {'updated_at': ultima_atualizacao}
                ultima_atualizacao = format_date_fields(ultima_atualizacao_dict, ['updated_at'])['updated_at']
            
            # Contamos os pacientes ativos
            count_result = self.db.from_(self.table).select("*", count="exact").is_("deleted_at", "null").execute()
            
            return {
                "ultima_criacao": ultima_criacao,
                "ultima_atualizacao": ultima_atualizacao,
                "total_pacientes": count_result.count
            }
        except Exception as e:
            logger.error(f"Erro ao obter última atualização: {str(e)}")
            # Re-lançar exceção para ser tratada na camada de serviço
            raise
