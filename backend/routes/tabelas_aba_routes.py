from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import List, Any, Dict, Optional
import logging
from math import ceil

# Corrigido: Usar a função get síncrona
from ..config.config import get_supabase_client
# Importar modelo de resposta paginada (ajuste o caminho se necessário)
from ..schemas.responses import PaginatedResponse 

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/profissoes", response_model=PaginatedResponse[Dict[str, Any]])
def get_profissoes(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("profissao_name", regex="^(profissao_name|profissao_id)$"), # Adicionado regex básico
    order_direction: str = Query("asc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("profissoes").select("*", count="exact")
        
        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)
            
        result = query.range(offset, offset + limit - 1).execute()
        
        total_count = result.count if result.count is not None else 0
        total_pages = ceil(total_count / limit)
        current_page = (offset // limit) + 1
        
        return PaginatedResponse(
            success=True,
            items=result.data,
            total=total_count,
            page=current_page,
            total_pages=total_pages,
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar profissões: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar profissões: {str(e)}")

@router.get("/especialidades", response_model=PaginatedResponse[Dict[str, Any]])
def get_especialidades(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("nome", regex="^(nome|especialidade_id)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("especialidades").select("*", count="exact")
        
        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)
            
        result = query.range(offset, offset + limit - 1).execute()
        
        total_count = result.count if result.count is not None else 0
        total_pages = ceil(total_count / limit)
        current_page = (offset // limit) + 1
        
        return PaginatedResponse(
            success=True,
            items=result.data,
            total=total_count,
            page=current_page,
            total_pages=total_pages,
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar especialidades: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar especialidades: {str(e)}")

@router.get("/locais", response_model=PaginatedResponse[Dict[str, Any]])
def get_locais(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("local_nome", regex="^(local_nome|local_id)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("locais").select("*", count="exact")
        if order_direction == "desc": query = query.order(order_column, desc=True)
        else: query = query.order(order_column)
        result = query.range(offset, offset + limit - 1).execute()
        total_count = result.count if result.count is not None else 0
        return PaginatedResponse(
            success=True, items=result.data, total=total_count,
            page=(offset // limit) + 1, total_pages=ceil(total_count / limit),
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar locais: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar locais: {str(e)}")

@router.get("/salas", response_model=PaginatedResponse[Dict[str, Any]])
def get_salas(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("room_name", regex="^(room_name|room_id|room_local_id)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("salas").select("*", count="exact")
        if order_direction == "desc": query = query.order(order_column, desc=True)
        else: query = query.order(order_column)
        result = query.range(offset, offset + limit - 1).execute()
        total_count = result.count if result.count is not None else 0
        return PaginatedResponse(
            success=True, items=result.data, total=total_count,
            page=(offset // limit) + 1, total_pages=ceil(total_count / limit),
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar salas: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar salas: {str(e)}")

@router.get("/usuarios", response_model=PaginatedResponse[Dict[str, Any]])
def get_usuarios_aba(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("user_name", regex="^(user_name|user_id)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("usuarios_aba").select("*", count="exact")
        if order_direction == "desc": query = query.order(order_column, desc=True)
        else: query = query.order(order_column)
        result = query.range(offset, offset + limit - 1).execute()
        total_count = result.count if result.count is not None else 0
        return PaginatedResponse(
            success=True, items=result.data, total=total_count,
            page=(offset // limit) + 1, total_pages=ceil(total_count / limit),
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar usuários ABA: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar usuários ABA: {str(e)}")

@router.get("/usuarios-profissoes", response_model=PaginatedResponse[Dict[str, Any]])
def get_usuarios_profissoes(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("created_at", regex="^(usuario_aba_id|profissao_id|created_at)$"), # Exemplo: ordenar por data criação
    order_direction: str = Query("desc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("usuarios_profissoes").select("*", count="exact")
        if order_direction == "desc": query = query.order(order_column, desc=True)
        else: query = query.order(order_column)
        result = query.range(offset, offset + limit - 1).execute()
        total_count = result.count if result.count is not None else 0
        return PaginatedResponse(
            success=True, items=result.data, total=total_count,
            page=(offset // limit) + 1, total_pages=ceil(total_count / limit),
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar relações usuários-profissões: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar relações usuários-profissões: {str(e)}")

@router.get("/usuarios-especialidades", response_model=PaginatedResponse[Dict[str, Any]])
def get_usuarios_especialidades(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("created_at", regex="^(usuario_aba_id|especialidade_id|created_at)$"),
    order_direction: str = Query("desc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("usuarios_especialidades").select("*", count="exact")
        if order_direction == "desc": query = query.order(order_column, desc=True)
        else: query = query.order(order_column)
        result = query.range(offset, offset + limit - 1).execute()
        total_count = result.count if result.count is not None else 0
        return PaginatedResponse(
            success=True, items=result.data, total=total_count,
            page=(offset // limit) + 1, total_pages=ceil(total_count / limit),
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar relações usuários-especialidades: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar relações usuários-especialidades: {str(e)}")

@router.get("/agendamentos-profissionais", response_model=PaginatedResponse[Dict[str, Any]])
def get_agendamentos_profissionais(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("created_at", regex="^(schedule_id|professional_id|created_at)$"),
    order_direction: str = Query("desc", regex="^(asc|desc)$")
):
    try:
        query = supabase.table("agendamentos_profissionais").select("*", count="exact")
        if order_direction == "desc": query = query.order(order_column, desc=True)
        else: query = query.order(order_column)
        result = query.range(offset, offset + limit - 1).execute()
        total_count = result.count if result.count is not None else 0
        return PaginatedResponse(
            success=True, items=result.data, total=total_count,
            page=(offset // limit) + 1, total_pages=ceil(total_count / limit),
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar relações agendamentos-profissionais: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar relações agendamentos-profissionais: {str(e)}")

# NOVO ENDPOINT PARA TIPOS DE PAGAMENTO
@router.get("/tipos-pagamento", response_model=PaginatedResponse[Dict[str, Any]])
def get_tipos_pagamento(
    supabase: Client = Depends(get_supabase_client),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("nome", regex="^(nome|id_origem|created_at|ativo)$"), # Colunas permitidas para ordenar
    order_direction: str = Query("asc", regex="^(asc|desc)$")
):
    """Busca dados paginados da tabela tipo_pagamento."""
    try:
        query = supabase.table("tipo_pagamento").select("*", count="exact")
        
        # Aplicar ordenação
        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)
            
        # Aplicar paginação
        result = query.range(offset, offset + limit - 1).execute()
        
        # Calcular totais e páginas
        total_count = result.count if result.count is not None else 0
        total_pages = ceil(total_count / limit)
        current_page = (offset // limit) + 1
        
        # Retornar resposta paginada
        return PaginatedResponse(
            success=True,
            items=result.data,
            total=total_count,
            page=current_page,
            total_pages=total_pages,
            has_more=(offset + limit < total_count)
        )
    except Exception as e:
        logger.error(f"Erro ao buscar tipos de pagamento: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro ao buscar tipos de pagamento: {str(e)}") 