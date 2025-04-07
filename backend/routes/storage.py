from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends, UploadFile, File
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
import os
import tempfile
from pydantic import ValidationError

from ..schemas.responses import StandardResponse, PaginatedResponse
from ..models.storage import StorageCreate, StorageUpdate, Storage
from ..services.storage import StorageService
from ..repositories.storage import StorageRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_storage_repository(db: SupabaseClient = Depends(get_supabase_client)) -> StorageRepository:
    return StorageRepository(db)

def get_storage_service(repo: StorageRepository = Depends(get_storage_repository)) -> StorageService:
    return StorageService(repo)

@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de storage está funcionando"}

@router.get("",
            response_model=PaginatedResponse[Storage],
            summary="Listar Arquivos",
            description="Retorna uma lista paginada de arquivos armazenados")
async def list_files(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    order_column: str = Query("nome", regex="^(nome|created_at|size)$"),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: StorageService = Depends(get_storage_service)
):
    result = await service.list_files(
        limit=limit,
        offset=offset,
        search=search,
        order_column=order_column,
        order_direction=order_direction
    )
    
    return PaginatedResponse(
        success=True,
        items=result["items"],
        total=result["total"],
        page=(offset // limit) + 1,
        total_pages=ceil(result["total"] / limit),
        has_more=offset + limit < result["total"]
    )

@router.get("/{id}",
            response_model=StandardResponse[Storage],
            summary="Buscar Arquivo",
            description="Retorna os dados de um arquivo específico")
async def get_file(
    id: UUID = Path(...),
    service: StorageService = Depends(get_storage_service)
):
    result = await service.get_file(id)
    return StandardResponse(success=True, data=result)

@router.post("",
            response_model=StandardResponse[Storage],
            status_code=status.HTTP_201_CREATED,
            summary="Upload de Arquivo",
            description="Faz upload de um novo arquivo")
async def upload_file(
    file: UploadFile = File(...),
    entidade: str = Query(..., description="Tipo da entidade (paciente, guia, etc)"),
    entidade_id: str = Query(..., description="ID da entidade"),
    service: StorageService = Depends(get_storage_service)
):
    try:
        logger.info(f"Recebendo requisição POST /storage")
        logger.info(f"Arquivo: {file.filename}, Entidade: {entidade}, ID: {entidade_id}")
        
        result = await service.upload_file(file, entidade, entidade_id)
        return StandardResponse(
            success=True,
            data=result,
            message="Arquivo enviado com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except Exception as e:
        logger.error(f"Erro ao fazer upload do arquivo: {str(e)}")
        raise

@router.put("/{id}",
            response_model=StandardResponse[Storage],
            summary="Atualizar Arquivo",
            description="Atualiza os dados de um arquivo")
async def update_file(
    file_data: StorageUpdate,
    id: UUID = Path(...),
    service: StorageService = Depends(get_storage_service)
):
    result = await service.update_file(id, file_data)
    return StandardResponse(
        success=True,
        data=result,
        message="Arquivo atualizado com sucesso"
    )

@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Arquivo",
               description="Remove um arquivo do sistema")
async def delete_file(
    id: UUID = Path(...),
    service: StorageService = Depends(get_storage_service)
):
    result = await service.delete_file(id)
    return StandardResponse(
        success=True,
        data=result,
        message="Arquivo removido com sucesso"
    )

@router.get("/reference/{reference_id}/{reference_type}",
            response_model=StandardResponse[List[Storage]],
            summary="Buscar Arquivos por Referência",
            description="Retorna todos os arquivos vinculados a uma referência específica")
async def get_files_by_reference(
    reference_id: UUID = Path(...),
    reference_type: str = Path(...),
    service: StorageService = Depends(get_storage_service)
):
    result = await service.get_files_by_reference(reference_id, reference_type)
    return StandardResponse(success=True, data=result)

@router.get("/download/all",
            summary="Download de Todos os Arquivos",
            description="Baixa todos os arquivos em um arquivo ZIP")
async def download_all_files(
    service: StorageService = Depends(get_storage_service)
):
    zip_content = await service.download_all_files()
    if not zip_content:
        raise HTTPException(status_code=500, detail="Erro ao gerar arquivo ZIP")

@router.post("/sync",
            response_model=StandardResponse[bool],
            summary="Sincronizar com R2",
            description="Sincroniza a tabela storage com os arquivos do Cloudflare R2")
async def sync_with_r2(
    service: StorageService = Depends(get_storage_service)
):
    try:
        result = await service.sync_with_r2()
        return StandardResponse(
            success=True,
            data=result,
            message="Sincronização bidirecional concluída com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao sincronizar com R2: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar com R2: {str(e)}"
        )
