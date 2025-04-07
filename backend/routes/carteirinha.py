from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID
from pydantic import ValidationError

from ..models.carteirinha import CarteirinhaCreate, CarteirinhaUpdate, Carteirinha
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.carteirinha import CarteirinhaService
from ..repositories.carteirinha import CarteirinhaRepository
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient
from ..utils.date_utils import format_date_fields, DATE_FIELDS

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)

def get_carteirinha_repository(db: SupabaseClient = Depends(get_supabase_client)) -> CarteirinhaRepository:
    return CarteirinhaRepository(db)

def get_carteirinha_service(repo: CarteirinhaRepository = Depends(get_carteirinha_repository)) -> CarteirinhaService:
    return CarteirinhaService(repo)

@router.get("/teste")
async def test_endpoint():
    return {"message": "Endpoint de carteirinhas está funcionando"}

@router.get("",
            response_model=PaginatedResponse[Carteirinha],
            summary="Listar Carteirinhas",
            description="Retorna uma lista paginada de carteirinhas")
async def list_carteirinhas(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    order_column: str = Query("numero_carteirinha", regex="^(numero_carteirinha|data_validade|created_at|status)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$"),
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    result = await service.list_carteirinhas(
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

@router.get("/by-paciente/{paciente_id}",
            response_model=StandardResponse[List[Carteirinha]],
            summary="Buscar Carteirinhas por Paciente",
            description="Retorna todas as carteirinhas de um paciente específico")
async def get_carteirinhas_by_paciente(
    paciente_id: UUID = Path(...),
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    result = await service.get_carteirinhas_by_paciente(paciente_id)
    return StandardResponse(success=True, data=result)

@router.post("/rpc/listar_carteirinhas_com_detalhes",
            response_model=PaginatedResponse[Carteirinha],
            summary="Listar Carteirinhas com Detalhes via RPC",
            description="Retorna uma lista paginada de carteirinhas com dados do paciente e plano de saúde via RPC")
async def list_carteirinhas_rpc(
    p_offset: int = Body(...),
    p_limit: int = Body(...),
    p_search: Optional[str] = Body(None),
    p_status: Optional[str] = Body(None),
    p_paciente_id: Optional[str] = Body(None),
    p_plano_saude_id: Optional[str] = Body(None),
    p_order_column: str = Body("numero_carteirinha"),
    p_order_direction: str = Body("asc"),
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    try:
        result = await service.list_carteirinhas(
            offset=p_offset,
            limit=p_limit,
            search=p_search,
            status=p_status,
            paciente_id=p_paciente_id,
            plano_saude_id=p_plano_saude_id,
            order_column=p_order_column,
            order_direction=p_order_direction,
        )

        return PaginatedResponse(
            success=True,
            items=result["items"],
            total=result["total"],
            page=(p_offset // p_limit) + 1,
            total_pages=ceil(result["total"] / p_limit),
            has_more=p_offset + p_limit < result["total"]
        )
    except Exception as e:
        logger.error(f"Erro ao listar carteirinhas via RPC: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar carteirinhas via RPC: {str(e)}"
        )

@router.post("",
            response_model=StandardResponse[Carteirinha],
            status_code=status.HTTP_201_CREATED,
            summary="Criar Carteirinha",
            description="Cria uma nova carteirinha")
async def create_carteirinha(
    carteirinha: CarteirinhaCreate,
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    try:
        logger.info(f"Recebendo requisição POST /carteirinhas")
        logger.info(f"Payload recebido: {carteirinha.model_dump()}")
        
        result = await service.create_carteirinha(carteirinha)
        return StandardResponse(
            success=True,
            data=result,
            message="Carteirinha criada com sucesso"
        )
    except ValidationError as e:
        logger.error(f"Erro de validação: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except Exception as e:
        logger.error(f"Erro ao criar carteirinha: {str(e)}")
        raise

@router.get("/{id}",
            response_model=StandardResponse[Carteirinha],
            summary="Buscar Carteirinha",
            description="Retorna os dados de uma carteirinha específica")
async def get_carteirinha(
    id: UUID = Path(...),
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    result = await service.get_carteirinha(id)
    if not result:
        raise HTTPException(status_code=404, detail="Carteirinha não encontrada")
    return StandardResponse(success=True, data=result)

@router.put("/{id}",
            response_model=StandardResponse[Carteirinha],
            summary="Atualizar Carteirinha",
            description="Atualiza os dados de uma carteirinha")
async def update_carteirinha(
    carteirinha: CarteirinhaUpdate,
    id: UUID = Path(...),
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    result = await service.update_carteirinha(id, carteirinha)
    if not result:
        raise HTTPException(status_code=404, detail="Carteirinha não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Carteirinha atualizada com sucesso"
    )

@router.delete("/{id}",
               response_model=StandardResponse[bool],
               summary="Deletar Carteirinha",
               description="Remove uma carteirinha do sistema")
async def delete_carteirinha(
    id: UUID = Path(...),
    service: CarteirinhaService = Depends(get_carteirinha_service)
):
    result = await service.delete_carteirinha(id)
    if not result:
        raise HTTPException(status_code=404, detail="Carteirinha não encontrada")
    return StandardResponse(
        success=True,
        data=result,
        message="Carteirinha removida com sucesso"
    )

@router.post(
    "/migrar-de-pacientes",
    summary="Migrar Carteirinhas da Tabela Pacientes",
    description="Migra os números de carteirinha da tabela pacientes para a tabela carteirinhas"
)
async def migrar_carteirinhas_de_pacientes(
    tamanho_lote: int = Query(100, description="Tamanho do lote para processamento"),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Migra os números de carteirinha com prefixo "0064" da tabela pacientes para a tabela carteirinhas,
    associando-as ao plano UNIMED. Carteirinhas com outros prefixos serão ignoradas.
    
    Esta operação:
    1. Identifica pacientes com número de carteirinha começando com "0064"
    2. Cria registros correspondentes na tabela carteirinhas
    3. Associa ao plano UNIMED
    
    Parâmetros:
    - tamanho_lote: Número de registros a processar por vez (padrão: 100)
    
    Retorna:
    - Resumo da operação com contadores e detalhes dos erros
    """
    try:
        # Obter ID do plano UNIMED
        plano_result = supabase.table("planos_saude").select("id, nome").ilike("nome", "%UNIMED%").limit(1).execute()
        
        if not plano_result.data:
            return {
                "success": False,
                "message": "Plano UNIMED não encontrado",
                "details": [],
                "errors": [{
                    "paciente_id": "",
                    "nome_paciente": "Erro de Sistema",
                    "numero_carteirinha": "",
                    "erro": "Plano UNIMED não encontrado no sistema"
                }]
            }
        
        plano_unimed = plano_result.data[0]
        plano_unimed_id = plano_unimed["id"]
        plano_unimed_nome = plano_unimed["nome"]
        
        # Usar o ID do sistema para operações automáticas
        usuario_sistema_id = "00000000-0000-0000-0000-000000000000"  # ID padrão do sistema
        
        # Buscar pacientes com carteirinhas começando com "0064" que ainda não foram migradas
        pacientes_result = supabase.rpc(
            "buscar_pacientes_para_migracao_carteirinhas",
            {"p_prefixo": "0064", "p_limite": tamanho_lote}
        ).execute()
        
        if not pacientes_result.data:
            return {
                "success": True,
                "message": "Nenhuma carteirinha encontrada para migração",
                "details": [],
                "errors": []
            }
        
        pacientes = pacientes_result.data
        
        # Contadores para o resumo
        total_pacientes = len(pacientes)
        contador_criados = 0
        contador_erros = 0
        
        # Listas para armazenar resultados
        detalhes = []
        erros = []
        
        # Processar cada paciente
        for paciente in pacientes:
            try:
                paciente_id = paciente["id"]
                nome_paciente = paciente["nome"]
                numero_carteirinha = paciente["numero_carteirinha"]
                
                # Verificar se o número de carteirinha já existe para outro paciente
                carteirinha_existente = supabase.table("carteirinhas") \
                    .select("*") \
                    .eq("numero_carteirinha", numero_carteirinha) \
                    .neq("paciente_id", paciente_id) \
                    .limit(1) \
                    .execute()
                
                if carteirinha_existente.data:
                    erro_msg = "ERRO: Carteirinha já existe para outro paciente"
                    erros.append({
                        "paciente_id": paciente_id,
                        "nome_paciente": nome_paciente,
                        "numero_carteirinha": numero_carteirinha,
                        "erro": erro_msg
                    })
                    contador_erros += 1
                    continue
                
                # Verificar se já existe uma carteirinha com o mesmo número para o mesmo plano
                carteirinha_mesmo_plano = supabase.table("carteirinhas") \
                    .select("*") \
                    .eq("numero_carteirinha", numero_carteirinha) \
                    .eq("plano_saude_id", plano_unimed_id) \
                    .limit(1) \
                    .execute()
                
                if carteirinha_mesmo_plano.data:
                    erro_msg = "ERRO: Já existe uma carteirinha com este número para este plano"
                    erros.append({
                        "paciente_id": paciente_id,
                        "nome_paciente": nome_paciente,
                        "numero_carteirinha": numero_carteirinha,
                        "erro": erro_msg
                    })
                    contador_erros += 1
                    continue
                
                # Inserir a carteirinha
                nova_carteirinha = {
                    "paciente_id": paciente_id,
                    "plano_saude_id": plano_unimed_id,
                    "numero_carteirinha": numero_carteirinha,
                    "status": "ativa",
                    "created_by": usuario_sistema_id,
                    "updated_by": usuario_sistema_id
                }
                
                resultado_insercao = supabase.table("carteirinhas").insert(nova_carteirinha).execute()
                
                if resultado_insercao.data:
                    detalhes.append({
                        "paciente_id": paciente_id,
                        "nome_paciente": nome_paciente,
                        "numero_carteirinha": numero_carteirinha,
                        "resultado": "Carteirinha criada com sucesso"
                    })
                    contador_criados += 1
                else:
                    erro_msg = "ERRO: Falha ao inserir carteirinha"
                    erros.append({
                        "paciente_id": paciente_id,
                        "nome_paciente": nome_paciente,
                        "numero_carteirinha": numero_carteirinha,
                        "erro": erro_msg
                    })
                    contador_erros += 1
            
            except Exception as e:
                erro_msg = f"ERRO: {str(e)}"
                erros.append({
                    "paciente_id": paciente.get("id", ""),
                    "nome_paciente": paciente.get("nome", "Desconhecido"),
                    "numero_carteirinha": paciente.get("numero_carteirinha", ""),
                    "erro": erro_msg
                })
                contador_erros += 1
        
        # Preparar mensagem de resumo
        resumo = f"Migração concluída. Total de carteirinhas com prefixo '0064': {total_pacientes}, Criadas: {contador_criados}, Erros: {contador_erros}"
        
        return {
            "success": True,
            "message": resumo,
            "details": detalhes,
            "errors": erros
        }
        
    except Exception as e:
        logger.error(f"Erro ao migrar carteirinhas: {str(e)}")
        return {
            "success": False,
            "message": "Erro ao migrar carteirinhas",
            "details": [],
            "errors": [{
                "paciente_id": "",
                "nome_paciente": "Erro de Sistema",
                "numero_carteirinha": "",
                "erro": str(e)
            }]
        }