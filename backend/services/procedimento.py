from datetime import datetime, UTC
from typing import Dict, List, Optional
from uuid import UUID
from fastapi import HTTPException
from decimal import Decimal
from ..models.procedimento import ProcedimentoCreate, ProcedimentoUpdate, Procedimento
from ..repositories.procedimento import ProcedimentoRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def log_dict_with_types(prefix: str, data: dict):
    """Função auxiliar para logar dicionários com tipos de dados"""
    type_info = {k: f"{v} ({type(v).__name__})" for k, v in data.items()}
    logger.debug(f"{prefix}: {json.dumps(type_info, indent=2, default=str)}")

class ProcedimentoService:
    def __init__(self, repository: ProcedimentoRepository):
        self.repository = repository

    async def list_procedimentos(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "nome",
        order_direction: str = "asc",
        tipo: Optional[str] = None,
        ativo: Optional[bool] = None
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction,
                tipo=tipo,
                ativo=ativo
            )
            
            return {
                "items": [Procedimento.model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar procedimentos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar procedimentos: {str(e)}"
            )

    async def get_procedimento(self, id: str) -> Optional[Procedimento]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Procedimento não encontrado")
            return Procedimento(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao buscar procedimento: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao buscar procedimento: {str(e)}")

    async def create_procedimento(self, procedimento: ProcedimentoCreate, user_id: str) -> Optional[Procedimento]:
        try:
            logger.info(f"Dados recebidos no serviço: {procedimento.model_dump()}")
            # Validar se já existe procedimento com o mesmo código
            existing = await self.repository.get_by_codigo(procedimento.codigo)
            if existing:
                raise HTTPException(status_code=409, detail="Já existe um procedimento com este código")

            # Calcular valor total se não fornecido
            data = procedimento.model_dump(
                exclude_unset=True,
                exclude_none=True
            )
            
            logger.debug("Dados recebidos para criação:")
            log_dict_with_types("Dados do procedimento", data)
            
            if "valor_total" not in data:
                valor_total = Decimal('0')
                if data.get("valor"):
                    valor_total += data["valor"]
                if data.get("valor_filme"):
                    valor_total += data["valor_filme"]
                if data.get("valor_operacional"):
                    valor_total += data["valor_operacional"]
                data["valor_total"] = valor_total
                logger.debug(f"Valor total calculado: {valor_total} (tipo: {type(valor_total)})")

            data = format_date_fields(data, DATE_FIELDS)
            
            # Adiciona timestamps e user_id
            now = datetime.now(UTC).isoformat()
            data.update({
                "created_at": now,
                "updated_at": now,
                "created_by": str(user_id),
                "updated_by": str(user_id)
            })

            logger.debug("Dados após processamento:")
            log_dict_with_types("Dados finais", data)

            result = await self.repository.create(data)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao criar procedimento")
            
            return Procedimento(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar procedimento: {str(e)}")
            logger.error(f"Detalhes do erro: {type(e).__name__} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar procedimento: {str(e)}")

    async def update_procedimento(self, id: str, procedimento: ProcedimentoUpdate, user_id: str) -> Optional[Procedimento]:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Procedimento não encontrado")

            logger.debug("Dados existentes:")
            log_dict_with_types("Procedimento existente", existing)

            # Validar se o código já existe (se estiver sendo alterado)
            if procedimento.codigo and procedimento.codigo != existing["codigo"]:
                existing_with_codigo = await self.repository.get_by_codigo(procedimento.codigo)
                if existing_with_codigo and existing_with_codigo["id"] != id:
                    raise HTTPException(status_code=409, detail="Já existe um procedimento com este código")

            # Converter para dict e processar
            update_data = procedimento.model_dump(
                exclude_unset=True,
                exclude_none=True
            )
            
            logger.debug("Dados recebidos para atualização:")
            log_dict_with_types("Dados de atualização", update_data)
            
            # Recalcular valor total se algum valor foi alterado
            if any(key in update_data for key in ["valor", "valor_filme", "valor_operacional"]):
                valor_total = Decimal('0')
                valor = update_data.get("valor", existing.get("valor", Decimal('0')))
                valor_filme = update_data.get("valor_filme", existing.get("valor_filme", Decimal('0')))
                valor_operacional = update_data.get("valor_operacional", existing.get("valor_operacional", Decimal('0')))
                
                logger.debug(f"Valores para cálculo:")
                logger.debug(f"- valor: {valor} (tipo: {type(valor)})")
                logger.debug(f"- valor_filme: {valor_filme} (tipo: {type(valor_filme)})")
                logger.debug(f"- valor_operacional: {valor_operacional} (tipo: {type(valor_operacional)})")
                
                if valor:
                    valor_total += Decimal(str(valor))
                if valor_filme:
                    valor_total += Decimal(str(valor_filme))
                if valor_operacional:
                    valor_total += Decimal(str(valor_operacional))
                
                update_data["valor_total"] = valor_total
                logger.debug(f"Valor total calculado: {valor_total} (tipo: {type(valor_total)})")
            
            update_data = format_date_fields(update_data, DATE_FIELDS)
            
            # Adicionar campos de auditoria
            update_data.update({
                "updated_at": datetime.now(UTC).isoformat(),
                "updated_by": str(user_id)
            })

            logger.debug("Dados após processamento:")
            log_dict_with_types("Dados finais", update_data)

            result = await self.repository.update(id, update_data, user_id)
            if not result:
                raise HTTPException(status_code=404, detail="Procedimento não encontrado")
            return Procedimento(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar procedimento: {str(e)}")
            logger.error(f"Detalhes do erro: {type(e).__name__} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar procedimento: {str(e)}")

    async def delete_procedimento(self, id: str) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Procedimento não encontrado")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao deletar procedimento: {str(e)}")
            logger.error(f"Detalhes do erro: {type(e).__name__} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao deletar procedimento: {str(e)}")

    async def inativar_procedimento(self, id: str, user_id: str) -> Procedimento:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Procedimento não encontrado")

            update_data = {
                "ativo": False,
                "updated_at": datetime.now(UTC).isoformat(),
                "updated_by": str(user_id)
            }

            result = await self.repository.update(id, update_data, user_id)
            if not result:
                raise HTTPException(status_code=404, detail="Procedimento não encontrado")
            return Procedimento(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao inativar procedimento: {str(e)}")
            logger.error(f"Detalhes do erro: {type(e).__name__} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao inativar procedimento: {str(e)}") 