from datetime import datetime, UTC
from typing import Dict, List, Optional
from uuid import UUID
import logging
from ..repositories.storage import StorageRepository
from ..models.storage import StorageCreate, StorageUpdate, Storage
from backend.services.storage_r2 import storage as storage_r2_client
from fastapi import HTTPException
import os

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self, repository: StorageRepository):
        self.repository = repository
        self.storage_r2 = storage_r2_client

    async def list_files(
        self,
        offset: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_column: str = "created_at",
        order_direction: str = "desc",
    ) -> Dict:
        """Lista arquivos com paginação e busca"""
        try:
            result = await self.repository.list(
                offset=offset,
                limit=limit,
                search=search,
                order_column=order_column,
                order_direction=order_direction,
            )

            # Validar cada item individualmente
            validated_items = []
            for item in result.get("items", []):
                try:
                    validated_item = Storage.model_validate(item)
                    validated_items.append(validated_item)
                except Exception as e:
                    logger.error(f"Erro ao validar item: {str(e)}")
                    continue

            return {
                "items": validated_items,
                "total": result.get("total", 0),
                "limit": result.get("limit", limit),
                "offset": result.get("offset", offset),
                "total_pages": (
                    (result.get("total", 0) + limit - 1) // limit
                    if result.get("total", 0) > 0
                    else 0
                ),
                "has_more": result.get("total", 0) > offset + limit,
            }
        except Exception as e:
            logger.error(f"Erro ao listar arquivos: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao listar arquivos: {str(e)}"
            )

    async def get_file(self, id: str):
        """Obtém um arquivo pelo ID"""
        try:
            return await self.repository.get_by_id(id)
        except Exception as e:
            logger.error(f"Erro ao obter arquivo: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao obter arquivo: {str(e)}"
            )

    async def get_files_by_reference(self, reference_id: UUID, reference_type: str):
        """Obtém arquivos por referência"""
        try:
            return await self.repository.get_by_reference(reference_id, reference_type)
        except Exception as e:
            logger.error(f"Erro ao obter arquivos por referência: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter arquivos por referência: {str(e)}",
            )

    async def create_file(self, storage: StorageCreate):
        """Cria um novo registro de arquivo"""
        try:
            return await self.repository.create(storage)
        except Exception as e:
            logger.error(f"Erro ao criar arquivo: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao criar arquivo: {str(e)}"
            )

    async def update_file(self, id: UUID, storage: StorageUpdate, user_id: UUID):
        """Atualiza um arquivo existente"""
        try:
            return await self.repository.update(id, storage, user_id)
        except Exception as e:
            logger.error(f"Erro ao atualizar arquivo: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao atualizar arquivo: {str(e)}"
            )

    async def delete_file(self, id: UUID):
        """Remove um arquivo"""
        try:
            return await self.repository.delete(id)
        except Exception as e:
            logger.error(f"Erro ao excluir arquivo: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao excluir arquivo: {str(e)}"
            )

    async def upload_file(
        self,
        file_path: str,
        dest_name: str,
        reference_id: Optional[UUID] = None,
        reference_type: Optional[str] = None,
        user_id: UUID = None,
    ):
        """Faz upload de um arquivo para o R2"""
        try:
            result = await self.storage_r2.upload_file(file_path, dest_name)
            if result:
                return result
            raise Exception("Falha ao fazer upload do arquivo")
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao fazer upload do arquivo: {str(e)}"
            )

    async def download_all_files(self):
        """Download de todos os arquivos em um ZIP"""
        try:
            return await self.storage_r2.download_all_files()
        except Exception as e:
            logger.error(f"Erro ao baixar arquivos: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao baixar arquivos: {str(e)}"
            )

    async def get_files_by_entidade(self, entidade: str, entidade_id: str):
        """Obtém arquivos por entidade"""
        try:
            return await self.repository.get_by_entidade(entidade, entidade_id)
        except Exception as e:
            logger.error(f"Erro ao buscar arquivos da entidade: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao buscar arquivos da entidade: {str(e)}"
            )

    async def sync_with_r2(self) -> bool:
        """Sincroniza a tabela storage com os arquivos do R2"""
        try:
            # Lista todos os arquivos no R2
            r2_files = self.storage_r2.list_files()

            # Verifica se r2_files é uma lista
            if not isinstance(r2_files, list):
                logger.error(f"Erro: r2_files não é uma lista: {r2_files}")
                return False

            # Obtém o usuário do sistema (admin)
            admin_user_id = await self._get_or_create_admin_user()
            if not admin_user_id:
                logger.error("Não foi possível obter ou criar o usuário admin")
                return False

            # Cria um conjunto com as URLs de todos os arquivos no R2
            r2_urls = {self.storage_r2.get_url(file["key"]) for file in r2_files if isinstance(file, dict) and "key" in file}
            logger.info(f"Encontrados {len(r2_urls)} arquivos no R2")

            # Obtém todos os registros ativos da tabela storage
            storage_records = await self._get_all_active_storage_records()
            logger.info(f"Encontrados {len(storage_records)} registros ativos na tabela storage")

            # Adiciona novos arquivos que existem no R2 mas não na tabela storage
            added_count = 0
            for file in r2_files:
                try:
                    # Verifica se o arquivo tem a chave necessária
                    if not isinstance(file, dict) or "key" not in file:
                        logger.error(f"Arquivo inválido: {file}")
                        continue

                    # Gera a URL do arquivo
                    url = self.storage_r2.get_url(file["key"])

                    # Verifica se o arquivo já existe no banco
                    existing = await self.repository.get_by_path(url)

                    if not existing:
                        # Cria um novo registro
                        storage_data = StorageCreate(
                            nome=os.path.basename(file["key"]),
                            content_type=file.get("content_type", "application/pdf"),
                            size=file.get("size", 0),
                            url=url,
                            created_by=admin_user_id,  # UUID do admin como string
                            updated_by=admin_user_id,  # UUID do admin como string
                        )
                        await self.repository.create(storage_data)
                        added_count += 1
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo {file}: {str(e)}")
                    continue

            # Remove registros da tabela storage que não existem mais no R2
            removed_count = 0
            for record in storage_records:
                if record["url"] not in r2_urls:
                    try:
                        # Marca o registro como excluído na tabela storage
                        await self.repository.delete(record["id"])
                        removed_count += 1
                        logger.info(f"Registro removido: {record['nome']} (URL: {record['url']})")
                    except Exception as e:
                        logger.error(f"Erro ao remover registro {record['id']}: {str(e)}")

            logger.info(f"Sincronização concluída: {added_count} registros adicionados, {removed_count} registros removidos")
            return True

        except Exception as e:
            logger.error(f"Erro ao sincronizar com R2: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Erro ao sincronizar com R2: {str(e)}"
            )

    async def _get_or_create_admin_user(self) -> Optional[str]:
        """Obtém ou cria um usuário admin para operações do sistema"""
        try:
            # Busca um usuário admin existente
            result = (
                self.repository.db.from_("usuarios")
                .select("id")
                .eq("tipo_usuario", "admin")
                .eq("ativo", True)
                .limit(1)
                .execute()
            )
            if result.data and len(result.data) > 0:
                return str(result.data[0]["id"])

            # Se não encontrou, cria um novo usuário admin
            result = (
                self.repository.db.from_("usuarios")
                .insert(
                    {
                        "nome": "System Admin",
                        "email": "system@clinicalmf.com",
                        "tipo_usuario": "admin",
                        "ativo": True,
                        "permissoes": {"admin": True},
                    }
                )
                .execute()
            )

            if result.data and len(result.data) > 0:
                return str(result.data[0]["id"])

            return None
        except Exception as e:
            logger.error(f"Erro ao obter/criar usuário admin: {str(e)}")
            return None

    def _get_file_type(self, path: str) -> str:
        """Determina o tipo do arquivo baseado no caminho"""
        if "/fichas/" in path:
            return "ficha"
        elif "/documentos/" in path:
            return "documento"
        else:
            return "arquivo"

    def _get_entity_from_path(self, path: str) -> str:
        """Extrai a entidade do caminho do arquivo"""
        if "/fichas/" in path:
            return "ficha"
        elif "/pacientes/" in path:
            return "paciente"
        else:
            return "outro"

    def _get_entity_id_from_path(self, path: str) -> str:
        """Extrai o ID da entidade do caminho do arquivo"""
        try:
            parts = path.split("/")
            if len(parts) >= 3:
                # Assume que o ID está no formato: entidade/ID/arquivo
                return parts[-2]
            return "unknown"
        except:
            return "unknown"

    async def _get_all_active_storage_records(self) -> List[Dict]:
        """Obtém todos os registros ativos da tabela storage"""
        try:
            result = self.repository.db.from_("storage").select("*").is_("deleted_at", "null").execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Erro ao obter registros da tabela storage: {str(e)}")
            return []
