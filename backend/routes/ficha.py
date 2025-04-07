from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, status
from typing import Dict, List, Optional
from uuid import UUID
from pydantic import ValidationError
from datetime import datetime, timedelta
import logging
import json

from ..models.ficha import FichaCreate, FichaUpdate, Ficha
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.ficha import FichaService
from ..repositories.ficha import FichaRepository
from ..utils.date_utils import DateEncoder
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

# Importações para sessões
from ..schemas.sessao import Sessao, SessaoUpdate
from ..services.sessao import SessaoService
from ..repositories.sessao import SessaoRepository

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


def get_ficha_repository(
    db: SupabaseClient = Depends(get_supabase_client),
) -> FichaRepository:
    return FichaRepository(db)


def get_ficha_service(
    repo: FichaRepository = Depends(get_ficha_repository),
) -> FichaService:
    return FichaService(repo)


@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de fichas está funcionando"}


@router.get(
    "",
    response_model=PaginatedResponse[Ficha],
    summary="Listar Fichas",
    description="Retorna uma lista paginada de fichas",
)
async def list_fichas(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    order_column: str = Query(
        "data_atendimento",
        regex="^(data_atendimento|codigo_ficha|numero_guia|paciente_nome|status)$",
    ),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: FichaService = Depends(get_ficha_service),
):
    try:
        result = await service.list_fichas(
            offset=offset,
            limit=limit,
            search=search,
            order_column=order_column,
            order_direction=order_direction,
        )

        items = [Ficha.model_validate(item) for item in result.get("items", [])]
        total = result.get("total", 0)
        page = (offset // limit) + 1
        total_pages = (total + limit - 1) // limit
        has_more = page < total_pages

        return PaginatedResponse(
            success=True,
            items=items,
            total=total,
            page=page,
            total_pages=total_pages,
            has_more=has_more
        )
    except Exception as e:
        logger.error(f"Erro ao listar fichas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/pendentes")
async def listar_fichas_pendentes(
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    processado: Optional[bool] = None,
    order_column: str = "created_at",
    order_direction: str = "desc",
    db = Depends(get_supabase_client)
) -> Dict:
    """Lista fichas pendentes com paginação e filtros"""
    try:
        # Construir a query base
        query = db.from_("fichas_pendentes").select("*", count="exact")
        
        # Aplicar filtros
        if search:
            query = query.or_(
                f"codigo_ficha.ilike.%{search}%,numero_guia.ilike.%{search}%,paciente_nome.ilike.%{search}%"
            )
        
        if processado is not None:
            query = query.eq("processado", processado)
        
        # Aplicar ordenação
        if order_direction.lower() == "desc":
            query = query.order(order_column, desc=True)
        else:
            query = query.order(order_column)
        
        # Aplicar paginação
        query = query.range(offset, offset + limit - 1)
        
        # Executar a query
        result = query.execute()
        
        # Formatar as datas nos resultados
        items = []
        for item in result.data or []:
            # Converter campos de data para formato ISO
            for field in ["data_atendimento", "data_processamento", "created_at", "updated_at"]:
                if item.get(field):
                    if isinstance(item[field], str):
                        try:
                            # Tentar converter para objeto datetime e depois para string ISO
                            dt = datetime.fromisoformat(item[field].replace("Z", "+00:00"))
                            item[field] = dt.isoformat()
                        except ValueError:
                            pass
            items.append(item)
        
        return {
            "items": items,
            "total": result.count if hasattr(result, "count") else len(items),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Erro ao listar fichas pendentes: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar fichas pendentes: {str(e)}"
        )


@router.post("/pendentes/{id}/processar")
async def processar_ficha_pendente(
    id: str,
    opcoes: Dict,
    db = Depends(get_supabase_client)
) -> Dict:
    """Processa uma ficha pendente, criando ou vinculando a uma guia"""
    try:
        # Buscar a ficha pendente
        ficha_pendente = db.from_("fichas_pendentes").select("*").eq("id", id).execute()
        
        if not ficha_pendente.data:
            raise HTTPException(status_code=404, detail="Ficha pendente não encontrada")
        
        ficha_data = ficha_pendente.data[0]
        
        # Verificar se já foi processada
        if ficha_data.get("processado"):
            return {
                "success": False,
                "message": "Esta ficha já foi processada anteriormente",
                "data": ficha_data
            }
        
        # Opções de processamento
        criar_guia = opcoes.get("criar_guia", False)
        guia_id = opcoes.get("guia_id")
        
        # Se for para criar guia
        if criar_guia:
            # Buscar carteirinha pelo número
            carteirinha_numero = ficha_data.get("paciente_carteirinha", "").strip()
            logger.info(f"Buscando carteirinha com número: '{carteirinha_numero}'")
            
            # Primeiro tenta buscar com o formato exato
            carteirinha_query = db.from_("carteirinhas").select("*").eq("numero_carteirinha", carteirinha_numero).execute()
            
            # Se não encontrar, tenta buscar removendo pontos e hífens
            if not carteirinha_query.data:
                carteirinha_numero_limpo = carteirinha_numero.replace(".", "").replace("-", "").strip()
                logger.info(f"Carteirinha não encontrada com formato exato. Tentando com número limpo: '{carteirinha_numero_limpo}'")
                carteirinha_query = db.from_("carteirinhas").select("*").ilike("numero_carteirinha", f"%{carteirinha_numero_limpo}%").execute()
            
            if not carteirinha_query.data:
                logger.warning(f"Carteirinha não encontrada para o número: '{carteirinha_numero}'")
                return {
                    "success": False,
                    "message": f"Não foi possível encontrar a carteirinha com número '{carteirinha_numero}'. Verifique se a carteirinha está cadastrada no sistema.",
                    "data": ficha_data
                }
            
            logger.info(f"Carteirinha encontrada: {carteirinha_query.data[0].get('id')}")
            carteirinha = carteirinha_query.data[0]
            carteirinha_id = carteirinha.get("id")
            paciente_id = carteirinha.get("paciente_id")
            
            # Verificar se já existe uma guia com o mesmo número
            numero_guia = ficha_data.get("numero_guia")
            logger.info(f"Verificando se já existe uma guia com o número: '{numero_guia}'")
            guia_existente = db.from_("guias").select("*").eq("numero_guia", numero_guia).execute()
            
            if guia_existente.data:
                logger.info(f"Guia já existe. Usando guia existente com ID: {guia_existente.data[0].get('id')}")
                guia_id = guia_existente.data[0].get("id")
            else:
                # Buscar procedimento (usando um padrão)
                logger.info("Buscando procedimento do tipo 'procedimento'...")
                procedimento_query = db.from_("procedimentos").select("*").eq("tipo", "procedimento").limit(1).execute()
                
                if not procedimento_query.data:
                    logger.info("Nenhum procedimento do tipo 'procedimento' encontrado. Buscando qualquer tipo...")
                    # Se não encontrar, busca qualquer tipo
                    procedimento_query = db.from_("procedimentos").select("*").limit(1).execute()
                    
                if not procedimento_query.data:
                    logger.warning("Nenhum procedimento encontrado no sistema.")
                    return {
                        "success": False,
                        "message": "Não foi possível encontrar um procedimento para a guia",
                        "data": ficha_data
                    }
                
                procedimento_id = procedimento_query.data[0].get("id")
                logger.info(f"Procedimento encontrado: {procedimento_id} - {procedimento_query.data[0].get('nome')} (tipo: {procedimento_query.data[0].get('tipo')})")
                
                # Criar a guia
                guia_data = {
                    "carteirinha_id": carteirinha_id,
                    "paciente_id": paciente_id,
                    "procedimento_id": procedimento_id,
                    "numero_guia": numero_guia,
                    "data_solicitacao": ficha_data.get("data_atendimento"),
                    "data_autorizacao": ficha_data.get("data_atendimento"),
                    "status": "autorizada",
                    "tipo": "procedimento",
                    "quantidade_autorizada": ficha_data.get("total_sessoes", 1),
                    "quantidade_executada": 0
                }
                
                logger.info(f"Criando guia com dados: {guia_data}")
                
                guia_result = db.from_("guias").insert(guia_data).execute()
                
                if not guia_result.data:
                    logger.error("Erro ao criar guia: nenhum dado retornado")
                    return {
                        "success": False,
                        "message": "Erro ao criar guia",
                        "data": ficha_data
                    }
                
                guia_id = guia_result.data[0].get("id")
                logger.info(f"Guia criada com sucesso. ID: {guia_id}")
        
        # Se não tiver guia_id, não pode prosseguir
        if not guia_id:
            return {
                "success": False,
                "message": "É necessário fornecer um ID de guia ou criar uma nova",
                "data": ficha_data
            }
        
        # Criar a ficha
        codigo_ficha = ficha_data.get("codigo_ficha")
        
        # Verificar se já existe uma ficha com o mesmo código
        logger.info(f"Verificando se já existe uma ficha com o código: '{codigo_ficha}'")
        ficha_existente = db.from_("fichas").select("*").eq("codigo_ficha", codigo_ficha).execute()
        
        if ficha_existente.data:
            logger.warning(f"Ficha com código '{codigo_ficha}' já existe. ID: {ficha_existente.data[0].get('id')}")
            return {
                "success": False,
                "message": f"Já existe uma ficha com o código '{codigo_ficha}'",
                "data": ficha_data
            }
        
        ficha_insert = {
            "storage_id": ficha_data.get("storage_id"),
            "codigo_ficha": codigo_ficha,
            "numero_guia": ficha_data.get("numero_guia"),
            "guia_id": guia_id,
            "paciente_nome": ficha_data.get("paciente_nome"),
            "paciente_carteirinha": ficha_data.get("paciente_carteirinha"),
            "arquivo_digitalizado": ficha_data.get("arquivo_url"),
            "status": "pendente",
            "data_atendimento": ficha_data.get("data_atendimento"),
            "total_sessoes": ficha_data.get("total_sessoes")
        }
        
        logger.info(f"Criando ficha com dados: {ficha_insert}")
        ficha_result = db.from_("fichas").insert(ficha_insert).execute()
        
        if not ficha_result.data:
            logger.error("Erro ao criar ficha: nenhum dado retornado")
            return {
                "success": False,
                "message": "Erro ao criar ficha",
                "data": ficha_data
            }
        
        logger.info(f"Ficha criada com sucesso. ID: {ficha_result.data[0].get('id')}")
        
        # Excluir a ficha pendente após processamento bem-sucedido
        logger.info(f"Excluindo ficha pendente após processamento bem-sucedido. ID: {id}")
        db.from_("fichas_pendentes").delete().eq("id", id).execute()
        
        return {
            "success": True,
            "message": "Ficha processada com sucesso",
            "data": {
                "ficha_id": ficha_result.data[0].get("id"),
                "guia_id": guia_id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar ficha pendente: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao processar ficha pendente: {str(e)}"
        )


@router.delete("/pendentes/{id}", response_model=StandardResponse[bool])
async def excluir_ficha_pendente(
    id: str,
    db = Depends(get_supabase_client)
) -> Dict:
    """Exclui uma ficha pendente"""
    try:
        # Verificar se a ficha pendente existe
        ficha_pendente = db.from_("fichas_pendentes").select("*").eq("id", id).execute()
        
        if not ficha_pendente.data:
            raise HTTPException(status_code=404, detail="Ficha pendente não encontrada")
        
        # Obter o storage_id para excluir o arquivo também
        storage_id = ficha_pendente.data[0].get("storage_id")
        
        # Excluir a ficha pendente
        result = db.from_("fichas_pendentes").delete().eq("id", id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao excluir ficha pendente")
        
        # Tentar excluir o arquivo do storage (se existir)
        if storage_id:
            try:
                db.from_("storage").delete().eq("id", storage_id).execute()
            except Exception as e:
                logger.warning(f"Não foi possível excluir o arquivo do storage: {str(e)}")
        
        return {
            "success": True,
            "message": "Ficha pendente excluída com sucesso",
            "data": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir ficha pendente: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao excluir ficha pendente: {str(e)}"
        )


@router.get(
    "/{id}",
    response_model=StandardResponse[Ficha],
    summary="Buscar Ficha",
    description="Retorna os dados de uma ficha específica",
)
async def get_ficha(
    id: UUID = Path(...), service: FichaService = Depends(get_ficha_service)
):
    try:
        result = await service.get_ficha(id)
        if not result:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        return StandardResponse(success=True, data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ficha: {str(e)}")


@router.post(
    "",
    response_model=StandardResponse[Ficha],
    status_code=status.HTTP_201_CREATED,
    summary="Criar Ficha",
    description="Cria uma nova ficha",
)
async def create_ficha(
    ficha: FichaCreate, service: FichaService = Depends(get_ficha_service)
):
    try:
        logger.info(f"Recebendo requisição POST /fichas")
        logger.debug(f"Dados recebidos: {ficha}")

        # Validar código da ficha se fornecido
        if ficha.codigo_ficha:
            existing = await service.get_ficha_by_codigo(ficha.codigo_ficha)
            if existing:
                raise HTTPException(
                    status_code=409, detail="Já existe uma ficha com este código"
                )

        result = await service.create_ficha(ficha)

        return StandardResponse(
            success=True, data=result, message="Ficha criada com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        logger.error(f"Erro ao criar ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar ficha: {str(e)}")


@router.put(
    "/{id}",
    response_model=StandardResponse[Ficha],
    summary="Atualizar Ficha",
    description="Atualiza os dados de uma ficha",
)
async def update_ficha(
    id: UUID = Path(...),
    ficha: FichaUpdate = Body(...),
    service: FichaService = Depends(get_ficha_service),
):
    try:
        result = await service.update_ficha(id, ficha)
        if not result:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        # Serializa o resultado usando DateEncoder para garantir que dates sejam convertidos corretamente
        serialized = json.loads(json.dumps(result, cls=DateEncoder))
        return StandardResponse(success=True, data=serialized)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar ficha: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar ficha: {str(e)}"
        )


@router.delete(
    "/{id}",
    response_model=StandardResponse[bool],
    summary="Excluir Ficha",
    description="Exclui uma ficha",
)
async def delete_ficha(
    id: UUID = Path(...),
    service: FichaService = Depends(get_ficha_service),
):
    try:
        result = await service.delete_ficha(id)
        if not result:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        return StandardResponse(success=True, data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir ficha: {str(e)}")


@router.put(
    "/{id}/status",
    response_model=StandardResponse[Ficha],
    summary="Atualizar Status da Ficha",
    description="Atualiza o status de uma ficha",
)
async def update_status_ficha(
    id: UUID = Path(...),
    status: str = Body(..., embed=True),
    service: FichaService = Depends(get_ficha_service),
):
    try:
        result = await service.update_status(id, status)
        if not result:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        return StandardResponse(success=True, data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar status da ficha: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar status da ficha: {str(e)}"
        )


@router.get(
    "/pacientes/{paciente_id}/fichas",
    response_model=PaginatedResponse[Ficha],
    summary="Listar Fichas por Paciente",
    description="Retorna todas as fichas de um paciente específico",
)
async def get_fichas_by_paciente(
    paciente_id: str = Path(...),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    order_column: str = Query(
        "data_atendimento",
        regex="^(data_atendimento|codigo_ficha|numero_guia|paciente_nome|status)$",
    ),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: FichaService = Depends(get_ficha_service),
):
    try:
        result = await service.get_fichas_by_paciente(
            paciente_id=paciente_id,
            offset=offset,
            limit=limit,
            order_column=order_column,
            order_direction=order_direction,
        )
        return PaginatedResponse(
            success=True,
            items=result["items"],
            total=result["total"],
            page=(offset // limit) + 1,
            total_pages=(result["total"] + limit - 1) // limit,
            has_more=offset + limit < result["total"],
        )
    except Exception as e:
        logger.error(f"Erro ao listar fichas do paciente: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar fichas do paciente: {str(e)}"
        )

# Endpoints para gerenciar sessões de uma ficha específica
@router.get(
    "/{ficha_id}/sessoes",
    response_model=PaginatedResponse[Sessao],
    summary="Listar Sessões de uma Ficha",
    description="Retorna uma lista paginada de sessões de uma ficha específica"
)
async def list_sessoes_by_ficha(
    ficha_id: UUID = Path(..., description="ID da ficha"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    db: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Verificar se a ficha existe
        ficha_repo = FichaRepository(db)
        ficha = await ficha_repo.get_by_id(ficha_id)
        if not ficha:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        
        # Buscar sessões da ficha
        sessao_repo = SessaoRepository(db)
        offset = (page - 1) * limit
        
        # Consulta personalizada para buscar sessões por ficha_id
        query = db.from_("sessoes").select("*")\
            .eq("ficha_id", str(ficha_id))\
            .is_("deleted_at", "null")\
            .order("ordem_execucao", desc=False)\
            .range(offset, offset + limit - 1)
        
        result = query.execute()
        
        # Contar total de registros
        count_query = db.from_("sessoes").select("id", count="exact")\
            .eq("ficha_id", str(ficha_id))\
            .is_("deleted_at", "null")
        
        count_result = count_query.execute()
        total = count_result.count if hasattr(count_result, 'count') else 0
        
        # Se não houver sessões, retornar lista vazia
        if not result.data:
            return PaginatedResponse(
                success=True,
                items=[],
                total=0,
                page=page,
                total_pages=0,
                has_more=False
            )
        
        # Formatar datas e validar dados
        items = []
        for item in result.data:
            # Garantir que todos os campos necessários estejam presentes
            if 'data_sessao' in item and item['data_sessao']:
                if isinstance(item['data_sessao'], str):
                    try:
                        item['data_sessao'] = datetime.fromisoformat(item['data_sessao'].replace('Z', '+00:00')).date()
                    except ValueError:
                        # Se não conseguir converter, manter como está
                        pass
            
            # Garantir que campos obrigatórios estejam presentes
            if 'ficha_id' not in item or not item['ficha_id']:
                item['ficha_id'] = str(ficha_id)
                
            # Converter campos de data para o formato correto
            if 'created_at' in item and isinstance(item['created_at'], str):
                try:
                    item['created_at'] = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                except ValueError:
                    # Se não conseguir converter, usar data atual
                    item['created_at'] = datetime.now()
            
            if 'updated_at' in item and isinstance(item['updated_at'], str):
                try:
                    item['updated_at'] = datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00'))
                except ValueError:
                    # Se não conseguir converter, usar data atual
                    item['updated_at'] = datetime.now()
            
            # Garantir que possui_assinatura seja booleano
            if 'possui_assinatura' in item:
                if not isinstance(item['possui_assinatura'], bool):
                    item['possui_assinatura'] = bool(item['possui_assinatura'])
            else:
                item['possui_assinatura'] = False
            
            # Garantir que status tenha um valor padrão
            if 'status' not in item or not item['status']:
                item['status'] = "pendente"
            
            try:
                # Tentar validar o modelo
                sessao = Sessao.model_validate(item)
                items.append(sessao)
            except Exception as e:
                logger.error(f"Erro ao validar sessão {item.get('id')}: {str(e)}")
                # Continuar com a próxima sessão
        
        return PaginatedResponse(
            success=True,
            items=items,
            total=total,
            page=page,
            total_pages=(total + limit - 1) // limit if total > 0 else 0,
            has_more=offset + limit < total
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar sessões da ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar sessões da ficha: {str(e)}")

@router.put(
    "/{ficha_id}/sessoes/{sessao_id}",
    response_model=StandardResponse[Sessao],
    summary="Atualizar Sessão de uma Ficha",
    description="Atualiza os dados de uma sessão específica de uma ficha"
)
async def update_sessao_by_ficha(
    ficha_id: UUID = Path(..., description="ID da ficha"),
    sessao_id: UUID = Path(..., description="ID da sessão"),
    dados: SessaoUpdate = Body(..., description="Dados da sessão a serem atualizados"),
    db: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Verificar se a ficha existe
        ficha_repo = FichaRepository(db)
        ficha = await ficha_repo.get_by_id(ficha_id)
        if not ficha:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        
        # Verificar se a sessão existe e pertence à ficha
        sessao_repo = SessaoRepository(db)
        sessao = await sessao_repo.get_by_id(sessao_id)
        
        if not sessao:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        if str(sessao.get('ficha_id')) != str(ficha_id):
            raise HTTPException(status_code=400, detail="A sessão não pertence à ficha especificada")
        
        # Atualizar a sessão
        sessao_service = SessaoService(sessao_repo)
        
        # Usar um ID de usuário padrão para atualização (pode ser substituído pelo ID real do usuário autenticado)
        user_id = "00000000-0000-0000-0000-000000000000"
        
        update_data = dados.model_dump(exclude_unset=True)
        result = await sessao_repo.update(sessao_id, update_data, user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Erro ao atualizar sessão")
        
        return StandardResponse(
            success=True,
            data=Sessao.model_validate(result),
            message="Sessão atualizada com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar sessão da ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar sessão da ficha: {str(e)}")

@router.post(
    "/{ficha_id}/sessoes/batch",
    response_model=StandardResponse[Dict],
    summary="Criar Múltiplas Sessões para uma Ficha",
    description="Cria múltiplas sessões para uma ficha específica"
)
async def create_multiple_sessoes(
    ficha_id: UUID = Path(..., description="ID da ficha"),
    dados: Dict = Body(..., description="Dados das sessões a serem criadas"),
    db: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Verificar se a ficha existe
        ficha_repo = FichaRepository(db)
        ficha = await ficha_repo.get_by_id(ficha_id)
        if not ficha:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        
        sessoes = dados.get("sessoes", [])
        if not sessoes:
            raise HTTPException(status_code=400, detail="Nenhuma sessão fornecida para criação")
        
        # Criar sessões
        created_items = []
        user_id = "00000000-0000-0000-0000-000000000000"  # ID padrão para criação
        
        for i, sessao_data in enumerate(sessoes):
            # Garantir que a sessão esteja vinculada à ficha correta
            sessao_data["ficha_id"] = str(ficha_id)
            sessao_data["ordem_execucao"] = i + 1
            
            # Adicionar campos de auditoria
            sessao_data["created_by"] = user_id
            sessao_data["updated_by"] = user_id
            
            # Inserir no banco
            result = db.from_("sessoes").insert(sessao_data).execute()
            
            if result.data:
                created_items.append(result.data[0])
        
        return StandardResponse(
            success=True,
            data={
                "created": len(created_items),
                "items": created_items
            },
            message=f"{len(created_items)} sessões criadas com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar sessões para a ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar sessões para a ficha: {str(e)}")

@router.post(
    "/{ficha_id}/gerar-sessoes",
    response_model=StandardResponse[Dict],
    summary="Gerar Sessões para uma Ficha",
    description="Gera sessões para uma ficha existente baseado no total_sessoes"
)
async def gerar_sessoes_para_ficha(
    ficha_id: UUID = Path(..., description="ID da ficha"),
    db: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Verificar se a ficha existe
        ficha_repo = FichaRepository(db)
        ficha = await ficha_repo.get_by_id(ficha_id)
        if not ficha:
            raise HTTPException(status_code=404, detail="Ficha não encontrada")
        
        # Verificar se já existem sessões para esta ficha
        sessoes_existentes = db.from_("sessoes").select("*").eq("ficha_id", str(ficha_id)).is_("deleted_at", "null").execute()
        
        if sessoes_existentes.data and len(sessoes_existentes.data) > 0:
            return StandardResponse(
                success=True,
                data={
                    "message": f"Já existem {len(sessoes_existentes.data)} sessões para esta ficha",
                    "sessoes": sessoes_existentes.data
                }
            )
        
        # Obter o total de sessões da ficha
        total_sessoes = ficha.get("total_sessoes", 0)
        if total_sessoes <= 0:
            return StandardResponse(
                success=False,
                data=None,
                message="A ficha não possui um total de sessões definido"
            )
        
        # Data base para as sessões (data da ficha)
        data_base = datetime.fromisoformat(ficha.get("data_atendimento").replace("Z", "+00:00"))
        
        # Gerar sessões
        sessoes = []
        for i in range(total_sessoes):
            data_sessao = data_base + timedelta(days=i * 7)  # Uma sessão por semana
            
            sessao = {
                "ficha_id": str(ficha_id),
                "guia_id": ficha.get("guia_id"),
                "data_sessao": data_sessao.date().isoformat(),
                "possui_assinatura": False,
                "procedimento_id": str(uuid.uuid4()),  # Placeholder
                "profissional_executante": "",
                "status": "pendente",
                "numero_guia": ficha.get("numero_guia"),
                "codigo_ficha": ficha.get("codigo_ficha"),
                "ordem_execucao": i + 1,
                "status_biometria": "nao_verificado",
                "created_by": "00000000-0000-0000-0000-000000000000",
                "updated_by": "00000000-0000-0000-0000-000000000000"
            }
            
            sessoes.append(sessao)
        
        # Inserir sessões no banco
        result = db.from_("sessoes").insert(sessoes).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Erro ao criar sessões")
        
        return StandardResponse(
            success=True,
            data={
                "created": len(result.data),
                "items": result.data
            },
            message=f"{len(result.data)} sessões criadas com sucesso"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar sessões para a ficha: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar sessões para a ficha: {str(e)}")
