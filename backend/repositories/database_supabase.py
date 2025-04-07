# database_supabase.py
from typing import Dict, List, Optional, Any
from supabase import Client, create_client
from fastapi import Depends
import os
from dotenv import load_dotenv
from functools import lru_cache
from datetime import datetime, UTC
from backend.utils.date_utils import format_date_fields

load_dotenv()


def get_supabase_client() -> Client:
    """
    Cria e retorna uma instância do cliente Supabase.
    """
    load_dotenv()  # Garante que o .env foi carregado
    supabase_url = os.getenv('SUPABASE_URL')
    print(f"Tentando conectar a: {supabase_url}")  # Debug
    supabase_key = os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError(
            "SUPABASE_URL e SUPABASE_KEY devem estar definidos nas variáveis de ambiente"
        )

    return create_client(supabase_url, supabase_key)


# Tipo alias para melhor legibilidade
SupabaseClient = Client


async def list_pacientes(
    supabase: SupabaseClient = Depends(get_supabase_client),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None,
    order_column: str = "nome",
    order_direction: str = "asc"
):
    query = supabase.table('pacientes').select('*').eq('deleted_at', None)

    if search:
        query = query.or_(f"nome.ilike.%{search}%,cpf.ilike.%{search}%")

    # Ordenação
    if order_direction == "desc":
        query = query.order(order_column, desc=True)
    else:
        query = query.order(order_column)

    # Total de registros
    total = len(await query.execute())

    # Paginação
    query = query.range(offset, offset + limit - 1)
    response = await query.execute()

    return {
        'items': format_response_list(response.data),
        'total': total,
        'limit': limit,
        'offset': offset
    }


async def get_paciente(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        result = await supabase.table('pacientes').select(
            '*').eq('id', id).eq('deleted_at', None).single().execute()
        return format_response(result.data)
    except Exception as e:
        raise Exception(f"Erro ao buscar paciente: {str(e)}")


async def create_paciente(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        result = await supabase.table('pacientes').insert(data).execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao criar paciente: {str(e)}")


async def update_paciente(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        result = await supabase.table('pacientes').update(data).eq('id', id).execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao atualizar paciente: {str(e)}")


async def delete_paciente(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove um paciente (soft delete)"""
    try:
        result = await supabase.table("pacientes").update({"deleted_at": "now()"}).eq("id", id).is_("deleted_at", "null").execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar paciente: {str(e)}")


# Funções para Planos de Saúde
async def list_planos_saude(supabase: SupabaseClient = Depends(
    get_supabase_client),
                            limit: int = 10,
                            offset: int = 0,
                            search: Optional[str] = None,
                            order_column: str = "nome",
                            order_direction: str = "asc") -> Dict[str, Any]:
    """Lista planos de saúde com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("planos_saude")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(
                f"nome.ilike.%{search}%,codigo_operadora.ilike.%{search}%,registro_ans.ilike.%{search}%"
            )

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar planos de saúde: {str(e)}")


async def get_plano_saude(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca um plano de saúde pelo ID"""
    try:
        result = supabase.table("planos_saude")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar plano de saúde: {str(e)}")


async def get_plano_saude_by_codigo(
    codigo: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca um plano de saúde pelo código da operadora"""
    try:
        result = supabase.table("planos_saude")\
            .select("*")\
            .eq("codigo_operadora", codigo)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar plano de saúde pelo código: {str(e)}")


async def create_plano_saude(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria um novo plano de saúde"""
    try:
        result = supabase.table("planos_saude").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar plano de saúde: {str(e)}")


async def update_plano_saude(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza um plano de saúde existente"""
    try:
        result = supabase.table("planos_saude")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar plano de saúde: {str(e)}")


async def delete_plano_saude(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove um plano de saúde (soft delete)"""
    try:
        result = supabase.table("planos_saude")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar plano de saúde: {str(e)}")


# Funções para Carteirinhas
async def list_carteirinhas(supabase: SupabaseClient = Depends(
    get_supabase_client),
                            limit: int = 10,
                            offset: int = 0,
                            search: Optional[str] = None,
                            order_column: str = "numero_carteirinha",
                            order_direction: str = "asc") -> Dict[str, Any]:
    """Lista carteirinhas com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("carteirinhas")\
            .select("*", count="exact")

        if search:
            query = query.or_(f"numero_carteirinha.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar carteirinhas: {str(e)}")


async def get_carteirinha(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma carteirinha pelo ID"""
    try:
        result = supabase.table("carteirinhas")\
            .select("*")\
            .eq("id", id)\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar carteirinha: {str(e)}")


async def get_carteirinhas_by_paciente(paciente_id: str,
                                       supabase: SupabaseClient,
                                       limit: int = 10,
                                       offset: int = 0) -> Dict[str, Any]:
    """Busca todas as carteirinhas de um paciente"""
    try:
        query = supabase.from_("carteirinhas")\
            .select("*, planos_saude(nome)", count="exact")\
            .eq("paciente_id", paciente_id)\
            .is_("deleted_at", "null")

        result = query.range(offset, offset + limit - 1).execute()
        
        # Processar os resultados para incluir o nome do plano de saúde diretamente no objeto
        items = []
        for item in result.data:
            if item.get('planos_saude') and item['planos_saude'].get('nome'):
                item['plano_saude_nome'] = item['planos_saude']['nome']
            else:
                item['plano_saude_nome'] = 'N/A'
            items.append(item)

        return {
            "items": items,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao buscar carteirinhas do paciente: {str(e)}")


async def get_carteirinha_by_numero_and_plano(
    numero: str,
    plano_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma carteirinha pelo número e plano de saúde"""
    try:
        result = supabase.table("carteirinhas")\
            .select("*")\
            .eq("numero_carteirinha", numero)\
            .eq("plano_saude_id", plano_id)\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(
            f"Erro ao buscar carteirinha por número e plano: {str(e)}")


async def create_carteirinha(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova carteirinha"""
    try:
        result = supabase.table("carteirinhas").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar carteirinha: {str(e)}")


async def update_carteirinha(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma carteirinha existente"""
    try:
        result = supabase.table("carteirinhas")\
            .update(data)\
            .eq("id", id)\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar carteirinha: {str(e)}")


async def delete_carteirinha(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma carteirinha"""
    try:
        result = supabase.table("carteirinhas")\
            .delete()\
            .eq("id", id)\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar carteirinha: {str(e)}")


# Funções para Guias
async def list_guias(supabase: SupabaseClient = Depends(get_supabase_client),
                     limit: int = 10,
                     offset: int = 0,
                     search: Optional[str] = None,
                     order_column: str = "numero_guia",
                     order_direction: str = "asc") -> Dict[str, Any]:
    """Lista guias com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("guias")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(f"numero_guia.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar guias: {str(e)}")


async def get_guia(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma guia pelo ID"""
    try:
        result = supabase.table("guias")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar guia: {str(e)}")


async def get_guias_by_carteirinha(
    carteirinha_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[Dict]:
    """Busca todas as guias de uma carteirinha"""
    try:
        result = supabase.table("guias")\
            .select("*")\
            .eq("carteirinha_id", carteirinha_id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data
    except Exception as e:
        raise Exception(f"Erro ao buscar guias da carteirinha: {str(e)}")


async def get_guia_by_numero_and_carteirinha(
    numero: str,
    carteirinha_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma guia pelo número e carteirinha"""
    try:
        result = supabase.table("guias")\
            .select("*")\
            .eq("numero_guia", numero)\
            .eq("carteirinha_id", carteirinha_id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(
            f"Erro ao buscar guia por número e carteirinha: {str(e)}")


async def create_guia(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova guia"""
    try:
        result = supabase.table("guias").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar guia: {str(e)}")


async def update_guia(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma guia existente"""
    try:
        result = supabase.table("guias")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar guia: {str(e)}")


async def delete_guia(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma guia (soft delete)"""
    try:
        result = supabase.table("guias")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar guia: {str(e)}")


# Funções para Auditoria de Execuções
async def list_auditoria_execucoes(
        supabase: SupabaseClient = Depends(get_supabase_client),
        limit: int = 10,
        offset: int = 0,
        search: Optional[str] = None,
        order_column: str = "data_execucao",
        order_direction: str = "desc") -> Dict[str, Any]:
    """Lista auditorias de execuções com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("auditoria_execucoes")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(f"status.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar auditorias de execuções: {str(e)}")


async def get_auditoria_execucao(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma auditoria de execução pelo ID"""
    try:
        result = supabase.table("auditoria_execucoes")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar auditoria de execução: {str(e)}")


async def get_auditoria_execucao_por_periodo(
    data_inicial: datetime,
    data_final: datetime,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma auditoria de execução por período"""
    try:
        result = supabase.table("auditoria_execucoes")\
            .select("*")\
            .gte("data_execucao", data_inicial.isoformat())\
            .lte("data_execucao", data_final.isoformat())\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(
            f"Erro ao buscar auditoria de execução por período: {str(e)}")


async def create_auditoria_execucao(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova auditoria de execução"""
    try:
        result = supabase.table("auditoria_execucoes").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar auditoria de execução: {str(e)}")


async def update_auditoria_execucao(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma auditoria de execução existente"""
    try:
        result = supabase.table("auditoria_execucoes")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar auditoria de execução: {str(e)}")


async def delete_auditoria_execucao(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma auditoria de execução (soft delete)"""
    try:
        result = supabase.table("auditoria_execucoes")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar auditoria de execução: {str(e)}")


# Funções para Divergências
async def list_divergencias(supabase: SupabaseClient = Depends(
    get_supabase_client),
                            limit: int = 10,
                            offset: int = 0,
                            search: Optional[str] = None,
                            order_column: str = "data_identificacao",
                            order_direction: str = "desc",
                            status: Optional[str] = None,
                            tipo: Optional[str] = None) -> Dict[str, Any]:
    """Lista divergências com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("divergencias")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(
                f"descricao.ilike.%{search}%,tipo.ilike.%{search}%")

        if status:
            query = query.eq("status", status)

        if tipo:
            query = query.eq("tipo", tipo)

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar divergências: {str(e)}")


async def get_divergencia(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma divergência pelo ID"""
    try:
        result = supabase.table("divergencias")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar divergência: {str(e)}")


async def create_divergencia(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova divergência"""
    try:
        result = supabase.table("divergencias").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar divergência: {str(e)}")


async def update_divergencia(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma divergência existente"""
    try:
        result = supabase.table("divergencias")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar divergência: {str(e)}")


async def delete_divergencia(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma divergência (soft delete)"""
    try:
        result = supabase.table("divergencias")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar divergência: {str(e)}")


async def resolver_divergencia(
    id: str,
    user_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Marca uma divergência como resolvida"""
    try:
        data = {
            "status": "resolvida",
            "data_resolucao": datetime.now(UTC).isoformat(),
            "resolvido_por": user_id,
            "updated_at": datetime.now(UTC).isoformat(),
            "updated_by": user_id
        }
        result = supabase.table("divergencias")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao resolver divergência: {str(e)}")


async def incrementar_tentativas_divergencia(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Incrementa o contador de tentativas de resolução"""
    try:
        result = supabase.table("divergencias")\
            .rpc("incrementar_tentativas", {"divergencia_id": id})\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao incrementar tentativas: {str(e)}")


# Funções para Fichas
async def list_fichas(supabase: SupabaseClient = Depends(get_supabase_client),
                      limit: int = 10,
                      offset: int = 0,
                      search: Optional[str] = None,
                      order_column: str = "data_atendimento",
                      order_direction: str = "desc") -> Dict[str, Any]:
    """Lista fichas com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("fichas")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(f"codigo_ficha.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar fichas: {str(e)}")


async def get_ficha(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma ficha pelo ID"""
    try:
        result = supabase.table("fichas")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar ficha: {str(e)}")


async def get_ficha_by_codigo(
    codigo: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma ficha pelo código"""
    try:
        result = supabase.table("fichas")\
            .select("*")\
            .eq("codigo_ficha", codigo)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar ficha por código: {str(e)}")


async def create_ficha(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova ficha"""
    try:
        result = supabase.table("fichas").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar ficha: {str(e)}")


async def update_ficha(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma ficha existente"""
    try:
        result = supabase.table("fichas")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar ficha: {str(e)}")


async def delete_ficha(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma ficha (soft delete)"""
    try:
        result = supabase.table("fichas")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar ficha: {str(e)}")


# Funções para Sessões
async def list_sessoes(
    supabase: SupabaseClient = Depends(get_supabase_client),
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None,
    order_column: str = "data_sessao",
    order_direction: str = "asc") -> Dict[str, Any]:
    """Lista sessões com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("sessoes")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(f"observacoes.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": format_response_list(result.data),
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar sessões: {str(e)}")


async def get_sessao(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma sessão pelo ID"""
    try:
        result = supabase.table("sessoes")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao buscar sessão: {str(e)}")


async def get_sessoes_by_ficha_presenca(
    ficha_presenca_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[Dict]:
    """Busca todas as sessões de uma ficha de presença"""
    try:
        result = supabase.table("sessoes")\
            .select("*")\
            .eq("ficha_id", ficha_presenca_id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response_list(result.data)
    except Exception as e:
        raise Exception(
            f"Erro ao buscar sessões da ficha de presença: {str(e)}")


async def create_sessao(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova sessão"""
    try:
        result = await supabase.table('sessoes').insert(data).execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao criar sessão: {str(e)}")


async def update_sessao(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma sessão existente"""
    try:
        result = await supabase.table('sessoes').update(data).eq('id', id).execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao atualizar sessão: {str(e)}")


async def delete_sessao(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma sessão (soft delete)"""
    try:
        result = supabase.table("sessoes")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar sessão: {str(e)}")


async def get_sessoes_by_paciente(
    paciente_id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[Dict]:
    """Busca todas as sessões de um paciente"""
    try:
        result = supabase.table("sessoes")\
            .select("*")\
            .eq("paciente_id", paciente_id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response_list(result.data)
    except Exception as e:
        raise Exception(f"Erro ao buscar sessões do paciente: {str(e)}")


# Funções para Procedimentos
async def list_procedimentos(supabase: SupabaseClient = Depends(
    get_supabase_client),
                             limit: int = 10,
                             offset: int = 0,
                             search: Optional[str] = None,
                             order_column: str = "nome",
                             order_direction: str = "asc",
                             tipo: Optional[str] = None,
                             ativo: Optional[bool] = None) -> Dict[str, Any]:
    """Lista procedimentos com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("procedimentos")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(
                f"nome.ilike.%{search}%,codigo.ilike.%{search}%,descricao.ilike.%{search}%"
            )

        if tipo:
            query = query.eq("tipo", tipo)

        if ativo is not None:
            query = query.eq("ativo", ativo)

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": format_response_list(result.data),
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar procedimentos: {str(e)}")


async def get_procedimento(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca um procedimento pelo ID"""
    try:
        result = supabase.table("procedimentos")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao buscar procedimento: {str(e)}")


async def get_procedimento_by_codigo(
    codigo: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca um procedimento pelo código"""
    try:
        result = supabase.table("procedimentos")\
            .select("*")\
            .eq("codigo", codigo)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao buscar procedimento por código: {str(e)}")


async def create_procedimento(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria um novo procedimento"""
    try:
        # Calcula o valor total se não fornecido
        if "valor_total" not in data:
            valor_total = 0
            if data.get("valor"):
                valor_total += float(data["valor"])
            if data.get("valor_filme"):
                valor_total += float(data["valor_filme"])
            if data.get("valor_operacional"):
                valor_total += float(data["valor_operacional"])
            data["valor_total"] = valor_total

        result = await supabase.table('procedimentos').insert(data).execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao criar procedimento: {str(e)}")


async def update_procedimento(
    id: str,
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza um procedimento existente"""
    try:
        # Recalcula o valor total se algum valor foi alterado
        if any(key in data
               for key in ["valor", "valor_filme", "valor_operacional"]):
            existing = await get_procedimento(id)
            if existing:
                valor_total = 0
                valor = data.get("valor", existing.get("valor", 0))
                valor_filme = data.get("valor_filme",
                                       existing.get("valor_filme", 0))
                valor_operacional = data.get(
                    "valor_operacional", existing.get("valor_operacional", 0))

                if valor:
                    valor_total += float(valor)
                if valor_filme:
                    valor_total += float(valor_filme)
                if valor_operacional:
                    valor_total += float(valor_operacional)

                data["valor_total"] = valor_total

        result = await supabase.table('procedimentos').update(data).eq('id', id).execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao atualizar procedimento: {str(e)}")


async def delete_procedimento(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove um procedimento (soft delete)"""
    try:
        result = supabase.table("procedimentos")\
            .update({"deleted_at": "now()"})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar procedimento: {str(e)}")


async def inativar_procedimento(
    id: str,
    user_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Inativa um procedimento"""
    try:
        data = {
            "ativo": False,
            "updated_at": datetime.now(UTC).isoformat(),
            "updated_by": user_id
        }
        result = supabase.table("procedimentos")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao inativar procedimento: {str(e)}")


async def get_procedimentos_by_tipo(
    tipo: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[Dict]:
    """Busca procedimentos por tipo"""
    try:
        result = supabase.table("procedimentos")\
            .select("*")\
            .eq("tipo", tipo)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response_list(result.data)
    except Exception as e:
        raise Exception(f"Erro ao buscar procedimentos por tipo: {str(e)}")


async def get_procedimentos_ativos(supabase: SupabaseClient = Depends(
    get_supabase_client)) -> List[Dict]:
    """Busca todos os procedimentos ativos"""
    try:
        result = supabase.table("procedimentos")\
            .select("*")\
            .eq("ativo", True)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response_list(result.data)
    except Exception as e:
        raise Exception(f"Erro ao buscar procedimentos ativos: {str(e)}")


# Funções para Execuções
async def list_execucoes(supabase: SupabaseClient = Depends(
    get_supabase_client),
                         limit: int = 10,
                         offset: int = 0,
                         search: Optional[str] = None,
                         order_column: str = "data_execucao",
                         order_direction: str = "desc") -> Dict[str, Any]:
    """Lista execuções com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("execucoes")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(f"paciente_nome.ilike.%{search}%,"
                              f"paciente_carteirinha.ilike.%{search}%," 
                              f"numero_guia.ilike.%{search}%," 
                              f"codigo_ficha.ilike.%{search}%," 
                              f"profissional_executante.ilike.%{search}%," 
                              f"conselho_profissional.ilike.%{search}%," 
                              f"numero_conselho.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": format_response_list(result.data),
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar execuções: {str(e)}")


async def get_execucao(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Busca uma execução pelo ID"""
    try:
        result = supabase.table("execucoes")\
            .select("*")\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao buscar execução: {str(e)}")


async def get_execucoes_by_guia(
    guia_id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[Dict]:
    """Busca todas as execuções de uma guia"""
    try:
        result = supabase.table("execucoes")\
            .select("*")\
            .eq("guia_id", guia_id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response_list(result.data)
    except Exception as e:
        raise Exception(f"Erro ao buscar execuções da guia: {str(e)}")


async def get_execucoes_by_sessao(
    sessao_id: str, supabase: SupabaseClient = Depends(get_supabase_client)
) -> List[Dict]:
    """Busca todas as execuções de uma sessão"""
    try:
        result = supabase.table("execucoes")\
            .select("*")\
            .eq("sessao_id", sessao_id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response_list(result.data)
    except Exception as e:
        raise Exception(f"Erro ao buscar execuções da sessão: {str(e)}")


async def create_execucao(
    data: Dict,
    supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria uma nova execução"""
    try:
        result = supabase.table("execucoes").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise Exception(f"Erro ao criar execução: {str(e)}")


async def update_execucao(
    id: str,
    data: Dict,
    user_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza uma execução existente"""
    try:
        data["updated_at"] = datetime.now(UTC).isoformat()
        data["updated_by"] = user_id

        result = supabase.table("execucoes")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao atualizar execução: {str(e)}")


async def delete_execucao(
    id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove uma execução (soft delete)"""
    try:
        result = supabase.table("execucoes")\
            .update({"deleted_at": datetime.now(UTC).isoformat()})\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao deletar execução: {str(e)}")


async def verificar_biometria_execucao(
    id: str,
    status_biometria: str,
    user_id: str,
    supabase: SupabaseClient = Depends(get_supabase_client)
) -> Optional[Dict]:
    """Atualiza o status de verificação biométrica de uma execução"""
    try:
        data = {
            "status_biometria": status_biometria,
            "updated_at": datetime.now(UTC).isoformat(),
            "updated_by": user_id
        }
        result = supabase.table("execucoes")\
            .update(data)\
            .eq("id", id)\
            .is_("deleted_at", "null")\
            .execute()
        return format_response(result.data[0])
    except Exception as e:
        raise Exception(f"Erro ao verificar biometria da execução: {str(e)}")


async def get_guias_by_paciente(paciente_id: str,
                                supabase: SupabaseClient,
                                limit: int = 10,
                                offset: int = 0) -> Dict[str, Any]:
    """Busca todas as guias de um paciente"""
    try:
        query = supabase.from_("guias")\
            .select("*", count="exact")\
            .eq("paciente_id", paciente_id)\
            .is_("deleted_at", "null")

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao buscar guias do paciente: {str(e)}")


async def get_fichas_by_paciente(carteirinha: str,
                                 limit: int = 10,
                                 offset: int = 0,
                                 order_column: str = "data_atendimento",
                                 order_direction: str = "desc",
                                 supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    try:
        query = supabase.from_("fichas")\
            .select("*, guias!fichas_guia_id_fkey(*)")\
            .eq("paciente_carteirinha", carteirinha)\
            .is_("deleted_at", "null")

        if order_direction.lower() == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        query = query.range(offset, offset + limit - 1)
        result = query.execute()
        count_result = supabase.from_("fichas").select("id", count="exact").is_("deleted_at", "null").execute()
        
        # Formata os dados antes de retornar
        items = []
        for item in (result.data or []):
            formatted_item = format_date_fields(item, DATE_FIELDS)
            # Garante que os campos obrigatórios existam
            formatted_item.update({
                "profissional_id": str(formatted_item.get("profissional_id")),
                "tipo_ficha": formatted_item.get("tipo_ficha", "evolucao"),
                "data_atendimento": formatted_item.get("data_atendimento"),
                "status": formatted_item.get("status", "pendente"),
                "anexos": formatted_item.get("anexos", [])
            })
            items.append(formatted_item)

        return {
            "items": items,
            "total": count_result.count if hasattr(count_result, 'count') else 0,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Erro ao buscar fichas do paciente: {str(e)}")
        raise


async def list_storage(supabase: SupabaseClient = Depends(get_supabase_client),
                      limit: int = 10,
                      offset: int = 0,
                      search: Optional[str] = None,
                      order_column: str = "nome",
                      order_direction: str = "asc") -> Dict[str, Any]:
    """Lista arquivos com suporte a paginação, busca e ordenação"""
    try:
        query = supabase.table("storage")\
            .select("*", count="exact")\
            .is_("deleted_at", "null")

        if search:
            query = query.or_(f"nome.ilike.%{search}%")

        if order_direction == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)

        result = query.range(offset, offset + limit - 1).execute()

        return {
            "items": result.data,
            "total": result.count,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise Exception(f"Erro ao listar arquivos: {str(e)}")

async def get_storage(id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> Optional[Dict]:
    """Busca um arquivo pelo ID"""
    try:
        result = supabase.table("storage").select("*").eq("id", id).is_("deleted_at", "null").execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao buscar arquivo: {str(e)}")

async def get_storage_by_reference(reference_id: str, reference_type: str, 
                                 supabase: SupabaseClient = Depends(get_supabase_client)) -> List[Dict]:
    """Busca arquivos por referência"""
    try:
        result = supabase.table("storage").select("*")\
            .eq("referencia_id", reference_id)\
            .eq("tipo_referencia", reference_type)\
            .is_("deleted_at", "null").execute()
        return result.data
    except Exception as e:
        raise Exception(f"Erro ao buscar arquivos por referência: {str(e)}")

async def create_storage(data: Dict, supabase: SupabaseClient = Depends(get_supabase_client)) -> Dict:
    """Cria um novo registro de storage"""
    try:
        result = supabase.table("storage").insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao criar registro de storage: {str(e)}")

async def update_storage(id: str, data: Dict, supabase: SupabaseClient = Depends(get_supabase_client)) -> Optional[Dict]:
    """Atualiza um registro de storage existente"""
    try:
        result = supabase.table("storage").update(data).eq("id", id).is_("deleted_at", "null").execute()
        return result.data[0] if result.data else None
    except Exception as e:
        raise Exception(f"Erro ao atualizar registro de storage: {str(e)}")

async def delete_storage(id: str, supabase: SupabaseClient = Depends(get_supabase_client)) -> bool:
    """Remove um registro de storage (soft delete)"""
    try:
        result = supabase.table("storage").update({"deleted_at": "now()"}).eq("id", id).is_("deleted_at", "null").execute()
        return bool(result.data)
    except Exception as e:
        raise Exception(f"Erro ao remover registro de storage: {str(e)}")


# Lista de campos que são datas em toda a aplicação
DATE_FIELDS = [
    'data_nascimento',
    'data_atendimento',
    'data_execucao',
    'data_identificacao',
    'data_resolucao',
    'data_sessao',
    'data_inicio',
    'data_fim',
    'data_cadastro',
    'data_atualizacao',
    'data_inativacao',
    'created_at',
    'updated_at',
    'deleted_at'
]

def format_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formata os campos de data em um dicionário de resposta.
    
    Args:
        data: Dicionário com os dados a serem formatados
        
    Returns:
        Dict com os campos de data formatados
    """
    if not data:
        return data
    return format_date_fields(data, DATE_FIELDS)

def format_response_list(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Formata os campos de data em uma lista de dicionários.
    
    Args:
        data_list: Lista de dicionários com os dados a serem formatados
        
    Returns:
        Lista de dicionários com os campos de data formatados
    """
    if not data_list:
        return data_list
    return [format_response(item) for item in data_list]
