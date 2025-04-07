from datetime import datetime, UTC, date
from typing import Dict, List, Optional
from uuid import UUID
import json
from fastapi import HTTPException
from ..models.auditoria_execucao import AuditoriaExecucaoCreate, AuditoriaExecucaoUpdate, AuditoriaExecucao
from ..repositories.auditoria_execucao import AuditoriaExecucaoRepository
from ..utils.date_utils import format_date_fields, DATE_FIELDS, DateEncoder
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AuditoriaExecucaoService:
    def __init__(self, repository: AuditoriaExecucaoRepository):
        self.repository = repository

    async def list_auditoria_execucoes(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "data_execucao",
        order_direction: str = "desc"
    ) -> Dict:
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction
            )
            
            return {
                "items": [AuditoriaExecucao.model_validate(item) for item in result.get("items", [])],
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset)
            }
        except Exception as e:
            logger.error(f"Erro ao listar auditorias de execuções: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar auditorias de execuções: {str(e)}"
            )

    async def get_auditoria_execucao(self, id: str) -> Optional[AuditoriaExecucao]:
        try:
            result = await self.repository.get_by_id(id)
            if not result:
                raise HTTPException(status_code=404, detail="Auditoria de execução não encontrada")
            return AuditoriaExecucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar auditoria de execução: {str(e)}")

    async def create_auditoria_execucao(self, auditoria: AuditoriaExecucaoCreate) -> Optional[AuditoriaExecucao]:
        try:
            # Validações específicas da entidade
            if auditoria.data_inicial and auditoria.data_final and auditoria.data_inicial > auditoria.data_final:
                raise HTTPException(
                    status_code=400,
                    detail="Data inicial não pode ser maior que a data final"
                )

            result = await self.repository.create(auditoria)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao criar auditoria de execução")
            
            return AuditoriaExecucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar auditoria de execução: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar auditoria de execução: {str(e)}")

    async def update_auditoria_execucao(self, id: UUID, **kwargs) -> Optional[AuditoriaExecucao]:
        try:
            # Validações específicas da entidade
            if 'data_inicial' in kwargs and 'data_final' in kwargs:
                data_inicial = kwargs['data_inicial']
                data_final = kwargs['data_final']
                if data_inicial and data_final and data_inicial > data_final:
                    raise HTTPException(
                        status_code=400,
                        detail="Data inicial não pode ser maior que a data final"
                    )

            # Atualizar o campo updated_at se não foi fornecido
            if 'updated_at' not in kwargs:
                kwargs['updated_at'] = datetime.now().isoformat()

            # Converter objetos datetime para string ISO
            for key, value in kwargs.items():
                if isinstance(value, (datetime, date)):
                    kwargs[key] = value.isoformat()

            # Chamar o método update do repositório
            result = await self.repository.update(id, kwargs)
            if not result:
                raise HTTPException(status_code=404, detail="Auditoria de execução não encontrada")

            return AuditoriaExecucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao atualizar auditoria de execução: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao atualizar auditoria de execução: {str(e)}")

    async def delete_auditoria_execucao(self, id: UUID) -> bool:
        try:
            existing = await self.repository.get_by_id(id)
            if not existing:
                raise HTTPException(status_code=404, detail="Auditoria de execução não encontrada")

            await self.repository.delete(id)
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar auditoria de execução: {str(e)}")

    async def get_ultima_auditoria(self) -> Optional[AuditoriaExecucao]:
        try:
            result = await self.repository.get_ultima_auditoria()
            if not result:
                return None
            return AuditoriaExecucao(**result)
        except Exception as e:
            logger.error(f"Erro ao buscar última auditoria: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao buscar última auditoria: {str(e)}")
            
    async def registrar_execucao(self, **dados) -> Optional[AuditoriaExecucao]:
        """
        Registra uma nova execução de auditoria.
        """
        try:
            # Lidar com objetos datetime antes de enviar para o repositório
            if "data_execucao" in dados and isinstance(dados["data_execucao"], (datetime, date)):
                dados["data_execucao"] = dados["data_execucao"].isoformat()
                
            # Garante que data_execucao nunca seja nula
            if "data_execucao" not in dados or not dados["data_execucao"]:
                dados["data_execucao"] = datetime.now().isoformat()
                
            # Extrair apenas os campos que o repositório espera
            data = {
                "data_inicial": dados.get("data_inicial"),
                "data_final": dados.get("data_final"),
                "total_protocolos": dados.get("total_protocolos", 0),
                "total_divergencias": dados.get("total_divergencias", 0),
                "divergencias_por_tipo": dados.get("divergencias_por_tipo", {}),
                "total_fichas": dados.get("total_fichas", 0),
                "total_execucoes": dados.get("total_execucoes", 0),
                "total_resolvidas": dados.get("total_resolvidas", 0),
                "data_execucao": dados["data_execucao"]  # Garantir que data_execucao esteja presente
            }
                
            # Serializar para garantir que não há objetos datetime
            data = json.loads(json.dumps(data, cls=DateEncoder))
                
            # Definir o status aqui para garantir que seja enviado junto no INSERT inicial
            # ao invés de tentar fazer um UPDATE depois
            status = dados.get("status", "concluido")
            data["status"] = status
                
            # Registrar a execução
            result = await self.repository.registrar_execucao(**data)
            if not result:
                raise HTTPException(status_code=500, detail="Erro ao registrar execução de auditoria")
                
            # Garantir que o resultado também seja serializável
            result = json.loads(json.dumps(result, cls=DateEncoder))
            
            return AuditoriaExecucao(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao registrar execução de auditoria: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao registrar execução de auditoria: {str(e)}")

    async def get_by_id(self, id: str) -> Optional[AuditoriaExecucao]:
        """
        Obtém uma auditoria de execução pelo ID.
        Alias para get_auditoria_execucao para manter consistência com outros serviços.
        """
        return await self.get_auditoria_execucao(id)
        
    async def listar_divergencias_execucao(
        self,
        execucao_id: str,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
        tipo: Optional[str] = None,
        prioridade: Optional[str] = None
    ) -> Dict:
        """
        Lista divergências de uma execução específica
        """
        try:
            # Importar aqui para evitar circular imports
            from ..repositories.auditoria_repository import buscar_divergencias_view
            
            # Buscar divergências relacionadas a esta execução
            result = buscar_divergencias_view(
                page=page,
                per_page=per_page,
                status=status,
                tipo=tipo,
                prioridade=prioridade,
                execucao_id=execucao_id
            )
            
            return {
                "success": True,
                "items": result.get("items", []),
                "total": result.get("total", 0),
                "page": page,
                "total_pages": (result.get("total", 0) + per_page - 1) // per_page,
                "has_more": page * per_page < result.get("total", 0)
            }
        except Exception as e:
            logger.error(f"Erro ao listar divergências da execução {execucao_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao listar divergências da execução: {str(e)}"
            )