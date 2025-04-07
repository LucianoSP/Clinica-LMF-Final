from datetime import datetime, UTC, date
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from fastapi import HTTPException
from ..models.carteirinha import CarteirinhaCreate, CarteirinhaUpdate, Carteirinha
from ..repositories.carteirinha import CarteirinhaRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CarteirinhaService:
    def __init__(self, repository: CarteirinhaRepository):
        self.repository = repository

    async def list_carteirinhas(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        paciente_id: Optional[str] = None,
        plano_saude_id: Optional[str] = None,
        order_column: str = "numero_carteirinha",
        order_direction: str = "asc"
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                status=status,
                paciente_id=paciente_id,
                plano_saude_id=plano_saude_id,
                order_column=order_column,
                order_direction=order_direction
            )
            
            return {
                "items": [Carteirinha.model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar carteirinhas: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar carteirinhas: {str(e)}"
            )

    async def get_carteirinha(self, id: UUID) -> Optional[Carteirinha]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Carteirinha não encontrada")
            return Carteirinha(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar carteirinha: {str(e)}")

    async def get_carteirinhas_by_paciente(self, paciente_id: UUID) -> List[Carteirinha]:
        try:
            result = await self.repository.get_by_paciente(paciente_id)
            return [Carteirinha(**item) for item in result]
        except Exception as e:
            logger.error(f"Erro ao buscar carteirinhas do paciente: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar carteirinhas do paciente: {str(e)}"
            )

    async def create_carteirinha(self, carteirinha: CarteirinhaCreate) -> Optional[Carteirinha]:
        try:
            # Verificar duplicidade
            existing = await self.repository.get_by_numero_and_plano(
                carteirinha.numero_carteirinha,
                carteirinha.plano_saude_id
            )
            
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe uma carteirinha com este número para este plano de saúde"
                )

            result = await self.repository.create(carteirinha)
            if result:
                return Carteirinha(**result)
            raise HTTPException(status_code=500, detail="Erro ao criar carteirinha")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar carteirinha: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar carteirinha: {str(e)}")

    async def update_carteirinha(self, id: UUID, carteirinha: CarteirinhaUpdate) -> Optional[Carteirinha]:
        try:
            # Verificar duplicidade
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Carteirinha não encontrada")

            # Guardar os nomes do paciente e do plano de saúde
            paciente_nome = existing.get("paciente_nome", "")
            plano_saude_nome = existing.get("plano_saude_nome", "")

            if carteirinha.numero_carteirinha and carteirinha.plano_saude_id:
                if carteirinha.numero_carteirinha != existing["numero_carteirinha"] or \
                   carteirinha.plano_saude_id != existing["plano_saude_id"]:
                    
                    existing_with_numero = await self.repository.get_by_numero_and_plano(
                        carteirinha.numero_carteirinha,
                        carteirinha.plano_saude_id
                    )
                    
                    if existing_with_numero and existing_with_numero["id"] != str(id):
                        raise HTTPException(
                            status_code=400,
                            detail="Já existe uma carteirinha com este número para este plano de saúde"
                        )

            # Atualizar a carteirinha
            result = await self.repository.update(id, carteirinha)
            if not result:
                raise HTTPException(status_code=404, detail="Carteirinha não encontrada")
            
            # Restaurar os nomes do paciente e do plano de saúde se estiverem vazios
            if not result.get("paciente_nome") and paciente_nome:
                result["paciente_nome"] = paciente_nome
            if not result.get("plano_saude_nome") and plano_saude_nome:
                result["plano_saude_nome"] = plano_saude_nome
                
            return Carteirinha(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar carteirinha: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar carteirinha: {str(e)}")

    async def delete_carteirinha(self, id: UUID) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Carteirinha não encontrada")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar carteirinha: {str(e)}")
