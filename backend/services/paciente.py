from datetime import datetime, UTC, date
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException
from ..models.paciente import PacienteCreate, PacienteUpdate, Paciente
from ..repositories.paciente import PacienteRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS, DateEncoder
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PacienteService:
    def __init__(self, repository: PacienteRepository):
        self.repository = repository

    async def list_pacientes(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        fields: str = "*",
        order_column: str = "nome",
        order_direction: str = "asc"
    ) -> Dict:
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
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                fields=fields,
                order_column=order_column,
                order_direction=order_direction
            )
            
            return {
                "items": [Paciente.model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar pacientes: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar pacientes: {str(e)}"
            )

    async def get_paciente(self, id: UUID, fields: str = "*") -> Optional[Paciente]:
        """
        Busca um paciente pelo ID.
        
        Args:
            id: ID do paciente
            fields: Campos a serem retornados (ex: "id,nome,cpf"). Por padrão, retorna todos os campos.
        
        Returns:
            Objeto Paciente ou None se não encontrado
        """
        try:
            result = await self.repository.get_by_id(id, fields)
            if not result:
                raise HTTPException(status_code=404, detail="Paciente não encontrado")
            return Paciente(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar paciente: {str(e)}")

    async def create_paciente(self, paciente: PacienteCreate):
        try:
            logger.debug(f"Dados recebidos no serviço: {paciente.model_dump()}")
            
            # Verificar se precisa serializar os dados antes de passar ao repositório
            try:
                # Testar serialização - isso vai lançar erro se algum campo não for serializável
                paciente_json = json.dumps(paciente.model_dump())
                logger.debug("Paciente serializado com sucesso.")
            except TypeError as e:
                # Há campos de data que precisam ser serializados
                logger.warning(f"Erro de serialização: {str(e)}. Aplicando DateEncoder.")
                # Usar DateEncoder para garantir que datas sejam serializadas corretamente
                paciente_dict = json.loads(json.dumps(paciente.model_dump(), cls=DateEncoder))
                # Recriar o objeto PacienteCreate
                paciente = PacienteCreate.model_validate(paciente_dict)
                
            return await self.repository.create(paciente)
        except Exception as e:
            logger.error(f"Erro ao criar paciente: {str(e)}")
            raise

    async def update_paciente(self, id: UUID, paciente: PacienteUpdate):
        try:
            # Verificar se updated_by está presente
            paciente_dict = paciente.model_dump(exclude_unset=True)
            if 'updated_by' not in paciente_dict or not paciente_dict['updated_by']:
                # Se não estiver presente ou for vazio, usar um valor padrão
                logger.warning("Campo updated_by não fornecido, usando valor padrão")
                paciente_dict['updated_by'] = "sistema"
            
            # O user_id já vem nos dados do paciente (updated_by)
            result = await self.repository.update(id, paciente_dict)
            if result:
                # Formatar campos de data usando a função padrão
                return format_date_fields(result, DATE_FIELDS)
            return None
        except Exception as e:
            logger.error(f"Erro ao atualizar paciente: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao atualizar paciente: {str(e)}"
            )

    async def delete_paciente(self, id: UUID) -> bool:
        try:
            return await self.repository.delete(id)
        except Exception as e:
            logger.error(f"Erro ao excluir paciente: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao excluir paciente: {str(e)}"
            )

    async def get_last_update(self) -> dict:
        """
        Obtém a data da última atualização na tabela de pacientes.
        
        Returns:
            dict: Um dicionário com a data da última criação e última atualização
        """
        try:
            result = await self.repository.get_last_update()
            return result
        except Exception as e:
            logger.error(f"Erro ao obter última atualização: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter última atualização: {str(e)}"
            )
