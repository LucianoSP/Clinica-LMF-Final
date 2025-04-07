from fastapi import APIRouter, HTTPException, Query, Path, Body, status, Depends
from typing import List, Optional
import logging
from math import ceil
from uuid import UUID

from pydantic import ValidationError

from ..models.paciente import PacienteCreate, PacienteUpdate, Paciente
from ..schemas.responses import StandardResponse, PaginatedResponse
from ..services.paciente import PacienteService
from ..repositories.paciente import PacienteRepository
from ..services.ficha import FichaService
from ..repositories.ficha import FichaRepository
from backend.repositories.database_supabase import (
    get_supabase_client,
    SupabaseClient,
    get_carteirinhas_by_paciente,
    get_guias_by_paciente,
)
import pymysql
import uuid
import datetime
import sshtunnel
from ..config.config import settings
from fastapi.responses import JSONResponse

router = APIRouter(redirect_slashes=False)
logger = logging.getLogger(__name__)


def get_paciente_repository(
    db: SupabaseClient = Depends(get_supabase_client),
) -> PacienteRepository:
    return PacienteRepository(db)


def get_paciente_service(
    repo: PacienteRepository = Depends(get_paciente_repository),
) -> PacienteService:
    return PacienteService(repo)


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
    return {"message": "Endpoint de pacientes está funcionando"}


@router.get(
    "",
    response_model=PaginatedResponse[Paciente],
    summary="Listar Pacientes",
    description="Retorna uma lista paginada de pacientes",
)
async def list_pacientes(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    fields: str = Query("*", description="Campos a serem retornados (ex: 'id,nome,cpf'). Por padrão, retorna todos os campos."),
    order_column: str = Query("nome", regex="^(nome|nome_responsavel|cpf|rg|data_nascimento|telefone|email|cidade|data_registro_origem)$"),
    order_direction: str = Query("asc", regex="^(asc|desc)$"),
    service: PacienteService = Depends(get_paciente_service),
):
    result = await service.list_pacientes(
        limit=limit,
        offset=offset,
        search=search,
        fields=fields,
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


@router.post(
    "",
    response_model=StandardResponse[Paciente],
    status_code=status.HTTP_201_CREATED,
    summary="Criar Paciente",
    description="Cria um novo paciente",
)
async def create_paciente(
    paciente: PacienteCreate, service: PacienteService = Depends(get_paciente_service)
):
    print("Recebendo requisição POST /pacientes")  # Usando print para debug
    print(f"Payload recebido: {paciente.model_dump()}")  # Usando print para debug

    try:
        result = await service.create_paciente(paciente)
        return StandardResponse(
            success=True, data=result, message="Paciente criado com sucesso"
        )
    except ValidationError as e:
        print(f"Erro de validação: {e.errors()}")  # Usando print para debug
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        print(f"Erro geral: {str(e)}")  # Usando print para debug
        raise


@router.get(
    "/ultima-atualizacao",
    response_model=StandardResponse,
    summary="Obter última atualização",
    description="Retorna a data da última atualização na tabela de pacientes"
)
async def get_last_update(
    service: PacienteService = Depends(get_paciente_service),
):
    """
    Retorna a data da última atualização na tabela de pacientes.
    
    Esta informação é útil para mostrar quando foi a última vez que um paciente foi adicionado 
    ou modificado no sistema.
    """
    try:
        result = await service.get_last_update()
        return StandardResponse(
            success=True,
            data=result,
            message="Data da última atualização obtida com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao obter última atualização: {str(e)}")
        # Garantir uma resposta no formato esperado pelo frontend
        return StandardResponse(
            success=False,
            data=None,
            message=f"Erro ao obter última atualização: {str(e)}"
        )


@router.get(
    "/{id}",
    response_model=StandardResponse[Paciente],
    summary="Buscar Paciente",
    description="Retorna os dados de um paciente específico",
)
async def get_paciente(
    id: UUID = Path(...), 
    fields: str = Query("*", description="Campos a serem retornados (ex: 'id,nome,cpf'). Por padrão, retorna todos os campos."),
    service: PacienteService = Depends(get_paciente_service)
):
    result = await service.get_paciente(id, fields)
    if not result:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return StandardResponse(success=True, data=result)


@router.put(
    "/{id}",
    response_model=StandardResponse[Paciente],
    summary="Atualizar Paciente",
    description="Atualiza os dados de um paciente",
)
async def update_paciente(
    paciente: PacienteUpdate,
    id: UUID = Path(...),
    service: PacienteService = Depends(get_paciente_service),
):
    result = await service.update_paciente(id, paciente)
    if not result:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return StandardResponse(
        success=True, data=result, message="Paciente atualizado com sucesso"
    )


@router.delete(
    "/{id}",
    response_model=StandardResponse[bool],
    summary="Deletar Paciente",
    description="Remove um paciente do sistema",
)
async def delete_paciente(
    id: UUID = Path(...), service: PacienteService = Depends(get_paciente_service)
):
    result = await service.delete_paciente(id)
    if not result:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return StandardResponse(
        success=True, data=result, message="Paciente removido com sucesso"
    )


@router.get(
    "/{id}/carteirinhas",
    response_model=PaginatedResponse,
    summary="Listar Carteirinhas do Paciente",
    description="Retorna uma lista paginada de carteirinhas do paciente",
)
async def list_carteirinhas_by_paciente(
    id: UUID = Path(...),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: SupabaseClient = Depends(get_supabase_client),
):
    try:
        result = await get_carteirinhas_by_paciente(
            str(id), db, limit=limit, offset=offset
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
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar carteirinhas do paciente: {str(e)}"
        )


@router.get(
    "/{id}/guias",
    response_model=PaginatedResponse,
    summary="Listar Guias do Paciente",
    description="Retorna uma lista paginada de guias do paciente",
)
async def list_guias_by_paciente(
    id: UUID = Path(...),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: SupabaseClient = Depends(get_supabase_client),
):
    try:
        result = await get_guias_by_paciente(str(id), db, limit=limit, offset=offset)

        return PaginatedResponse(
            success=True,
            items=result["items"],
            total=result["total"],
            page=(offset // limit) + 1,
            total_pages=(result["total"] + limit - 1) // limit,
            has_more=offset + limit < result["total"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar guias do paciente: {str(e)}"
        )


@router.get(
    "/{id}/fichas",
    response_model=PaginatedResponse,
    summary="Listar Fichas do Paciente",
    description="Retorna uma lista paginada de fichas do paciente",
)
async def list_fichas_by_paciente(
    id: UUID = Path(...),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_column: str = Query("data_atendimento", regex="^(data_atendimento|codigo_ficha|numero_guia|created_at)$"),
    order_direction: str = Query("desc", regex="^(asc|desc)$"),
    service: FichaService = Depends(get_ficha_service)
):
    try:
        result = await service.get_fichas_by_paciente(
            paciente_id=id,
            limit=limit, 
            offset=offset,
            order_column=order_column,
            order_direction=order_direction
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

# Configurações de conexão MySQL
MYSQL_CONFIG = {
    'host': '127.0.0.1',  # localhost após o túnel SSH
    'port': 3306,
    'user': 'luciano_pacheco',
    'password': '0&)9qB37W1uK',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Configurações SSH 
SSH_CONFIG = {
    'host': '64.23.227.147',
    'user': 'root',
    'password': '591#2n4AO1Qp',
    'port': 22  # Porta SSH padrão
}

async def testar_conexao_mysql(database):
    """Testa a conexão com o banco de dados MySQL via túnel SSH."""
    tunnel = None
    try:
        # Configuração com o banco selecionado
        config = MYSQL_CONFIG.copy()
        config['database'] = database
        
        logger.info(f"Abrindo túnel SSH para {SSH_CONFIG['host']}...")
        try:
            # Criar túnel SSH
            tunnel = sshtunnel.SSHTunnelForwarder(
                (SSH_CONFIG['host'], SSH_CONFIG['port']),
                ssh_username=SSH_CONFIG['user'],
                ssh_password=SSH_CONFIG['password'],
                remote_bind_address=('127.0.0.1', 3306),
                local_bind_address=('127.0.0.1', 3307)  # Use uma porta diferente localmente
            )
            tunnel.start()
            logger.info("Túnel SSH estabelecido com sucesso!")
            
            # Atualizar a configuração MySQL para usar a porta do túnel
            config['host'] = '127.0.0.1'
            config['port'] = 3307  # Porta local do túnel
            
        except Exception as e:
            logger.error(f"Erro ao abrir túnel SSH: {str(e)}")
            return False, f"Erro ao abrir túnel SSH: {str(e)}"
        
        # Conectar ao MySQL através do túnel
        logger.info(f"Conectando ao MySQL em {config['host']}:{config['port']} (banco: {database})...")
        try:
            # Usar a configuração que já inclui DictCursor
            conexao = pymysql.connect(**config)
            logger.info("Conexão estabelecida com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao conectar ao MySQL: {str(e)}")
            raise Exception(f"Erro ao conectar ao banco de dados MySQL: {str(e)}")
        
        # Testar uma consulta simples
        cursor = conexao.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conexao.close()
        
        return True, "Conexão estabelecida com sucesso!"
    except Exception as e:
        logger.error(f"Erro ao testar conexão com MySQL: {str(e)}")
        return False, f"Erro ao conectar: {str(e)}"
    finally:
        # Fechar o túnel SSH se estiver aberto
        if tunnel and tunnel.is_active:
            tunnel.close()

@router.post("/test-connection", summary="Testar Conexão MySQL")
async def testar_conexao(dados: dict):
    """Testa a conexão com o banco de dados MySQL."""
    database = dados.get("database")
    
    if not database:
        return {
            "success": False,
            "message": "Parâmetro 'database' é obrigatório"
        }
    
    logger.info(f"Testando conexão com o banco {database}")
    
    sucesso, mensagem = await testar_conexao_mysql(database)
    
    return {
        "success": sucesso,
        "message": mensagem
    }

async def buscar_pacientes_mysql(database, tabela, limite=None, ultima_data_registro=None, ultima_data_atualizacao=None):
    """Busca pacientes no banco de dados MySQL via túnel SSH."""
    tunnel = None
    try:
        # Configuração com o banco selecionado
        config = MYSQL_CONFIG.copy()
        config['database'] = database
        
        logger.info(f"Abrindo túnel SSH para {SSH_CONFIG['host']}...")
        try:
            # Criar túnel SSH
            tunnel = sshtunnel.SSHTunnelForwarder(
                (SSH_CONFIG['host'], SSH_CONFIG['port']),
                ssh_username=SSH_CONFIG['user'],
                ssh_password=SSH_CONFIG['password'],
                remote_bind_address=('127.0.0.1', 3306),
                local_bind_address=('127.0.0.1', 3307)  # Use uma porta diferente localmente
            )
            tunnel.start()
            logger.info("Túnel SSH estabelecido com sucesso!")
            
            # Atualizar a configuração MySQL para usar a porta do túnel
            config['host'] = '127.0.0.1'
            config['port'] = 3307  # Porta local do túnel
            
        except Exception as e:
            logger.error(f"Erro ao abrir túnel SSH: {str(e)}")
            raise Exception(f"Erro ao abrir túnel SSH: {str(e)}")
        
        # Conectar ao MySQL através do túnel
        logger.info(f"Conectando ao MySQL em {config['host']}:{config['port']} (banco: {database})...")
        try:
            # Usar a configuração que já inclui DictCursor
            conexao = pymysql.connect(**config)
            logger.info("Conexão estabelecida com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao conectar ao MySQL: {str(e)}")
            raise Exception(f"Erro ao conectar ao banco de dados MySQL: {str(e)}")
        
        # Buscar dados
        cursor = conexao.cursor()
        
        # Construir a consulta base
        query = f"SELECT * FROM {tabela}"
        params = []
        
        # Adicionar filtro de datas somente se ambas estiverem definidas E não for a primeira importação
        if ultima_data_registro is not None and ultima_data_atualizacao is not None:
            logger.info(f"Filtrando por datas: registro > {ultima_data_registro} OU atualização > {ultima_data_atualizacao}")
            
            # Verificamos se existem colunas client_registration_date e client_update_date
            try:
                # Primeiro, consultamos as colunas da tabela para evitar erros
                cursor.execute(f"SHOW COLUMNS FROM {tabela}")
                colunas = cursor.fetchall()
                nomes_colunas = [col['Field'] for col in colunas]
                
                tem_coluna_registro = 'client_registration_date' in nomes_colunas
                tem_coluna_atualizacao = 'client_update_date' in nomes_colunas
                
                if tem_coluna_registro and tem_coluna_atualizacao:
                    # Usamos IFNULL para tratar valores nulos como uma data antiga
                    # e IS NULL para incluir registros sem data quando necessário
                    where_conditions = []
                    
                    # where_conditions.append("(IFNULL(client_registration_date, '1900-01-01') > %s OR client_registration_date IS NULL OR "
                    #                        "IFNULL(client_update_date, '1900-01-01') > %s OR client_update_date IS NULL)")
                    # params.extend([ultima_data_registro, ultima_data_atualizacao])

                    where_conditions.append("(IFNULL(client_update_date, '1900-01-01') > %s OR client_update_date IS NULL)")
                    params.extend([ultima_data_atualizacao])

                    query += " WHERE " + " AND ".join(where_conditions) + " ORDER BY client_update_date"
                else:
                    logger.warning("Colunas de data não encontradas na tabela. Importando todos os registros.")
                    # Se não temos as colunas de data, importamos todos os registros
            except Exception as e:
                logger.error(f"Erro ao verificar colunas: {str(e)}. Importando todos os registros.")
                # Se houver erro, importamos todos para não bloquear o processo
        else:
            logger.info("Primeira importação ou datas não definidas. Importando todos os registros.")
        
        # Adicionar limite se especificado
        if limite:
            query += f" LIMIT {limite}"
            
        logger.info(f"Executando consulta: {query}")
        logger.info(f"Parâmetros: {params}")
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            pacientes = cursor.fetchall()
            logger.info(f"Consulta executada com sucesso. Encontrados {len(pacientes)} registros.")
        except Exception as e:
            logger.error(f"Erro ao executar consulta SQL: {str(e)}")
            cursor.close()
            conexao.close()
            raise Exception(f"Erro ao executar consulta SQL: {str(e)}")
        
        cursor.close()
        conexao.close()
        
        # Verificar se temos dados
        if not pacientes:
            logger.warning("Nenhum paciente encontrado na consulta.")
        else:
            # Mostrar exemplo de campos disponíveis
            exemplo = pacientes[0]
            logger.info(f"Campos disponíveis no primeiro registro: {', '.join(exemplo.keys())}")
        
        return pacientes
    except Exception as e:
        logger.error(f"Erro ao buscar pacientes: {str(e)}")
        raise Exception(f"Erro ao buscar pacientes no MySQL: {str(e)}")
    finally:
        # Fechar o túnel SSH se estiver aberto
        if tunnel and tunnel.is_active:
            tunnel.close()

def mapear_paciente(paciente_mysql, usuario_id):
    """Mapeia um paciente do MySQL para o formato do Supabase."""
    
    # Converter campos booleanos (podem vir como int, string ou None)
    def converter_para_bool(valor):
        if valor is None:
            return False
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, int):
            return valor != 0
        if isinstance(valor, str):
            return valor.lower() in ('1', 'true', 'sim', 'yes', 't', 'y', 's')
        return False
    
    # Converter campos numéricos (podem vir como string ou None)
    def converter_para_int(valor):
        if valor is None:
            return None
        if isinstance(valor, int):
            return valor
        if isinstance(valor, str) and valor.strip():
            try:
                return int(valor)
            except (ValueError, TypeError):
                return None
        return None
    
    # Converter para float com segurança
    def converter_para_float(valor):
        if valor is None:
            return None
        if isinstance(valor, float):
            return valor
        if isinstance(valor, int):
            return float(valor)
        if isinstance(valor, str) and valor.strip():
            try:
                return float(valor.replace(',', '.'))
            except (ValueError, TypeError):
                return None
        return None
    
    # Verificar se um valor é um UUID válido
    def eh_uuid_valido(valor):
        if valor is None:
            return False
        try:
            # Tentar converter para UUID
            UUID(str(valor))
            return True
        except (ValueError, TypeError, AttributeError):
            return False
    
    # Processar o número com segurança
    numero = None
    if 'client_numero' in paciente_mysql:
        try:
            client_numero = paciente_mysql.get('client_numero')
            if isinstance(client_numero, int):
                numero = client_numero
            elif isinstance(client_numero, str) and client_numero.strip() and client_numero.strip().isdigit():
                numero = int(client_numero)
        except (ValueError, TypeError, AttributeError):
            pass  # Em caso de erro, mantém como None
    
    # Converter datas para ISO string
    def converter_data(valor):
        if valor is None:
            return None
        if isinstance(valor, (datetime.date, datetime.datetime)):
            return valor.isoformat()
        return valor
    
    # Verificar o supervisor_id - se for um código numérico como '999', retorna None
    supervisor_id = paciente_mysql.get('client_supervisor_id')
    supervisor_id_final = None
    if supervisor_id is not None:
        # Se for um UUID válido, usar o valor
        if eh_uuid_valido(supervisor_id):
            supervisor_id_final = str(supervisor_id)
        # Se não for UUID válido, deixar como None
    
    # Mapeamento dos campos
    paciente_supabase = {
        'nome': paciente_mysql.get('client_nome', ''),
        'id_origem': converter_para_int(paciente_mysql.get('client_id', '')),
        'cpf': paciente_mysql.get('client_cpf', ''),
        'rg': paciente_mysql.get('client_rg', ''),
        'data_nascimento': converter_data(paciente_mysql.get('client_data_nascimento')),
        'foto': paciente_mysql.get('client_thumb', ''),
        'nome_responsavel': paciente_mysql.get('client_nome_responsavel', ''),
        'nome_pai': paciente_mysql.get('client_nome_pai', ''),
        'nome_mae': paciente_mysql.get('client_nome_mae', ''),
        'sexo': paciente_mysql.get('client_sexo', '')[0:1] if paciente_mysql.get('client_sexo') else '',
        'cep': paciente_mysql.get('client_cep', ''),
        'endereco': paciente_mysql.get('client_endereco', ''),
        'numero': numero,
        'complemento': paciente_mysql.get('client_complemento', ''),
        'bairro': paciente_mysql.get('client_bairro', ''),
        'cidade': paciente_mysql.get('client_cidade_nome', ''),
        'estado': paciente_mysql.get('client_state', '')[0:2].upper() if paciente_mysql.get('client_state') else '',
        'forma_pagamento': converter_para_int(paciente_mysql.get('client_payment')),
        'valor_consulta': converter_para_float(paciente_mysql.get('consult_value')),
        'telefone': paciente_mysql.get('client_telefone', ''),
        'email': paciente_mysql.get('client_email', ''),
        'created_by': usuario_id,
        'updated_by': usuario_id,
        
        # Campos adicionais
        'patologia_id': converter_para_int(paciente_mysql.get('client_patalogia_id')),
        'tem_supervisor': converter_para_bool(paciente_mysql.get('client_tem_supervisor')),
        'supervisor_id': supervisor_id_final,  # Usar o valor processado, que será None se não for UUID válido
        'tem_avaliacao_luria': converter_para_bool(paciente_mysql.get('client_tem_avaliacao_luria')),
        'avaliacao_luria_data_inicio_treinamento': converter_data(paciente_mysql.get('client_avaliacao_luria_data_inicio_treinamento')),
        'avaliacao_luria_reforcadores': paciente_mysql.get('client_avaliacao_luria_reforcadores', ''),
        'avaliacao_luria_obs_comportamento': paciente_mysql.get('client_avaliacao_luria_obs_comportamento', ''),
        'numero_carteirinha': paciente_mysql.get('client_numero_carteirinha', ''),
        'cpf_responsavel': paciente_mysql.get('client_cpf_cli', ''),
        'crm_medico': paciente_mysql.get('client_crm_medico', ''),
        'nome_medico': paciente_mysql.get('client_nome_medico', ''),
        'pai_nao_declarado': converter_para_bool(paciente_mysql.get('client_pai_nao_declarado')),
        
        # Campos para rastreamento de importação
        'importado': True,
        'data_registro_origem': converter_data(paciente_mysql.get('client_registration_date')),
        'data_atualizacao_origem': converter_data(paciente_mysql.get('client_update_date'))
    }
    
    return paciente_supabase

def safe_str(obj):
    """Converte qualquer objeto para string, tratando datas corretamente"""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj)

@router.post(
    "/importar",
    summary="Importar Pacientes do MySQL",
    description="Importa pacientes de um banco de dados MySQL para o Supabase com controle de datas"
)

async def importar_pacientes_mysql(
    dados: dict,
):
    """
    Importa pacientes do banco de dados MySQL para o Supabase.
    
    - database: Nome do banco de dados MySQL
    - tabela: Nome da tabela que contém os pacientes
    - limit: Número máximo de registros a importar (opcional)
    - usuario_id: ID do usuário que está executando a importação (opcional)
    
    O sistema agora controla datas de importação para evitar duplicação:
    - Apenas importa registros novos ou atualizados desde a última importação
    - Rastreia as datas de criação e atualização dos registros originais
    """
    try:
        # Extrair os parâmetros do corpo da requisição
        database = dados.get("database")
        tabela = dados.get("tabela")
        limit = dados.get("limit")
        
        # Extrair o ID do usuário que está executando a importação, se fornecido
        usuario_id = dados.get("usuario_id", "sistema")
        logger.info(f"Importação sendo executada pelo usuário: {usuario_id}")
        
        # Se o usuário for "sistema", vamos verificar se o UUID correspondente existe
        if usuario_id == "sistema":
            db = get_supabase_client()
            sistema_uuid = "00000000-0000-0000-0000-000000000000"
            
            # Verificar se o usuário sistema já existe
            result = db.from_("usuarios").select("*").eq("id", sistema_uuid).execute()
            
            if not result.data:
                logger.info("Usuário sistema não encontrado, criando-o agora")
                try:
                    # Criar usuário sistema se não existir
                    db.from_("usuarios").insert({
                        "id": sistema_uuid,
                        "nome": "Sistema",
                        "email": "sistema@sistema.com",
                        "tipo_usuario": "sistema",
                        "created_at": datetime.datetime.now().isoformat(),
                        "updated_at": datetime.datetime.now().isoformat()
                    }).execute()
                    
                    usuario_id = sistema_uuid
                except Exception as e:
                    logger.error(f"Erro ao criar usuário sistema: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Erro ao criar usuário sistema: {str(e)}")
            else:
                usuario_id = sistema_uuid
        
        # Validações dos parâmetros
        if not database:
            raise HTTPException(status_code=400, detail="Nome do banco de dados é obrigatório")
            
        if not tabela:
            raise HTTPException(status_code=400, detail="Nome da tabela é obrigatório")
            
        # Buscar a última importação para controle de datas
        # Utilizamos a tabela controle_importacao_pacientes
        db = get_supabase_client()
        ultima_importacao_result = db.from_("controle_importacao_pacientes") \
            .select("*") \
            .order("timestamp_importacao", desc=True) \
            .limit(1) \
            .execute()
            
        # Extrair datas da última importação
        ultima_data_registro = None
        ultima_data_atualizacao = None
        
        if ultima_importacao_result.data and len(ultima_importacao_result.data) > 0:
            ultima_importacao = ultima_importacao_result.data[0]
            ultima_data_registro = ultima_importacao.get("ultima_data_registro_importada")
            ultima_data_atualizacao = ultima_importacao.get("ultima_data_atualizacao_importada")
            logger.info(f"Última importação encontrada: registro={ultima_data_registro}, atualização={ultima_data_atualizacao}")
            
        # Verificar conexão com MySQL
        sucesso, mensagem = await testar_conexao_mysql(database)
        if not sucesso:
            return {
                "success": False,
                "message": f"Erro na conexão com MySQL: {mensagem}",
                "importados": 0,
                "total": 0,
                "erros": [mensagem],
                "connection_status": {
                    "success": False,
                    "message": mensagem
                }
            }
        
        # Buscar pacientes no MySQL com filtro de data
        pacientes_mysql = await buscar_pacientes_mysql(
            database, 
            tabela, 
            limite=limit,
            ultima_data_registro=ultima_data_registro,
            ultima_data_atualizacao=ultima_data_atualizacao
        )
        
        if not pacientes_mysql:
            return {
                "success": True,
                "message": "Nenhum paciente novo encontrado para importação",
                "importados": 0,
                "total": 0,
                "erros": [],
                "connection_status": {
                    "success": True,
                    "message": mensagem
                }
            }
        
        # Importar pacientes para o Supabase
        repository = PacienteRepository(get_supabase_client())
        total_importados = 0
        total_atualizados = 0
        erros = []
        
        # Importar DateEncoder para tratamento global de datas
        from ..utils.date_utils import DateEncoder
        import json
        
        # Rastrear datas máximas nesta importação
        data_registro_max = None
        data_atualizacao_max = None
        
        # Testar conexão e obter cursor
        connection, cursor = await testar_conexao_mysql(database)
        if not connection or not cursor:
            return {
                "success": False,
                "message": f"Erro ao estabelecer conexão com o banco de dados MySQL {database}",
                "importados": 0,
                "total": 0,
                "erros": []
            }
        
        # Consultar o ID do plano Unimed uma única vez antes de iniciar a importação
        plano_unimed_id = None
        try:
            # Buscar especificamente o plano Unimed, já que é o único importado atualmente
            plano_saude_result = db.from_("planos_saude").select("id").ilike("nome", "%unimed%").is_("deleted_at", "null").execute()
            
            if plano_saude_result.data and len(plano_saude_result.data) > 0:
                plano_unimed_id = plano_saude_result.data[0]["id"]
                logger.info(f"Plano Unimed encontrado, ID: {plano_unimed_id}")
            else:
                logger.error("Plano Unimed não encontrado. Abortando importação de pacientes.")
                return {
                    "success": False,
                    "message": "Plano Unimed não encontrado. A importação foi abortada pois os pacientes precisam ser vinculados a este plano.",
                    "importados": 0,
                    "total": len(pacientes_mysql),
                    "total_erros": 0,
                    "total_atualizados": 0,
                    "erros": [{
                        "paciente": "Todos",
                        "erro": "Plano Unimed não encontrado no sistema. Cadastre o plano antes de iniciar a importação."
                    }],
                    "connection_status": {
                        "success": True,
                        "message": "Conexão estabelecida, mas importação abortada por falta do plano Unimed."
                    }
                }
        except Exception as e:
            logger.error(f"Erro ao buscar plano Unimed: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao buscar plano Unimed: {str(e)}. A importação foi abortada.",
                "importados": 0,
                "total": len(pacientes_mysql),
                "total_erros": 1,
                "total_atualizados": 0,
                "erros": [{
                    "paciente": "Todos",
                    "erro": f"Erro ao buscar plano Unimed: {str(e)}"
                }],
                "connection_status": {
                    "success": True,
                    "message": "Conexão estabelecida, mas importação abortada por erro ao buscar plano Unimed."
                }
            }
        
        # +++ Log Adicionado: Confirmar plano_unimed_id ANTES do loop +++
        logger.info(f"DEBUG: Valor de plano_unimed_id ANTES do loop: {plano_unimed_id}")
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        for paciente_mysql in pacientes_mysql:
            try:
                # Verificar se tem o campo obrigatório nome
                client_nome = paciente_mysql.get('client_nome', '')
                
                # Pular paciente se não tiver nome
                if not client_nome or client_nome.strip() == '':
                    erro = {
                        "paciente": paciente_mysql.get('client_nome', 'Nome não disponível'),
                        "erro": "Paciente sem nome - registro ignorado"
                    }
                    erros.append(erro)
                    logger.warning(f"Pulando paciente sem nome: {paciente_mysql.get('client_nome', 'Nome não disponível')}")
                    continue
                
                # Extrair as datas do registro original (se disponíveis)
                data_registro_origem = None
                data_atualizacao_origem = None
                
                try:
                    if 'client_registration_date' in paciente_mysql and paciente_mysql['client_registration_date']:
                        data_registro_origem = paciente_mysql['client_registration_date']
                        # Atualizar a data máxima de registro vista nesta importação
                        if data_registro_max is None or data_registro_origem > data_registro_max:
                            data_registro_max = data_registro_origem
                except Exception as e:
                    logger.warning(f"Erro ao processar data_registro_origem: {str(e)}")
                
                try:
                    if 'client_update_date' in paciente_mysql and paciente_mysql['client_update_date']:
                        data_atualizacao_origem = paciente_mysql['client_update_date']
                        # Atualizar a data máxima de atualização vista nesta importação
                        if data_atualizacao_max is None or data_atualizacao_origem > data_atualizacao_max:
                            data_atualizacao_max = data_atualizacao_origem
                except Exception as e:
                    logger.warning(f"Erro ao processar data_atualizacao_origem: {str(e)}")
                
                # Mapear dados do MySQL para o formato do Supabase
                try:
                    paciente_dict = mapear_paciente(paciente_mysql, usuario_id)
                    
                    # Serializar todas as datas logo após o mapeamento, antes de qualquer operação
                    paciente_dict = json.loads(json.dumps(paciente_dict, cls=DateEncoder))
                except Exception as e:
                    logger.error(f"Erro ao mapear paciente {paciente_mysql.get('client_nome', 'Nome não disponível')}: {str(e)}")
                    erro = {
                        "paciente": paciente_mysql.get('client_nome', 'Nome não disponível'),
                        "erro": f"Erro no mapeamento: {str(e)}"
                    }
                    erros.append(erro)
                    continue
                
                # Log para verificar o valor de id_origem antes de criar o objeto
                logger.info(f"Valor de id_origem antes de criar PacienteCreate: {paciente_dict.get('id_origem')}")
                
                # Garantir que id_origem não seja nulo antes de criar o objeto
                if not paciente_dict.get('id_origem') or str(paciente_dict.get('id_origem')).strip() == '':
                    paciente_dict['id_origem'] = f"ORIGEM-{str(uuid.uuid4())[-8:]}"
                    logger.info(f"FINAL: Definindo ID de origem de emergência: {paciente_dict['id_origem']}")
                
                # Verificar se já existe um paciente com este id_origem
                try:
                    id_origem = paciente_dict.get('id_origem')
                    paciente_existente = await repository.get_by_id_origem(id_origem)
                except Exception as e:
                    logger.error(f"Erro ao verificar existência do paciente {paciente_dict.get('nome')}: {str(e)}")
                    erro = {
                        "paciente": paciente_dict.get('nome', 'Nome não disponível'),
                        "erro": f"Erro ao verificar existência: {str(e)}"
                    }
                    erros.append(erro)
                    continue
                
                paciente_obj_para_carteirinha = None # Resetar para cada paciente

                try:
                    if paciente_existente:
                        # O paciente já existe, atualizar em vez de criar
                        logger.info(f"Paciente com id_origem {id_origem} já existe. Atualizando dados.")

                        # Preservar o ID original e atualizar os outros campos
                        id_existente = paciente_existente.get('id')
                        paciente_dict['updated_at'] = datetime.datetime.now().isoformat()  # Já serializar a data

                        # Remover id do dict pois não podemos alterar o id
                        if 'id' in paciente_dict:
                            del paciente_dict['id']

                        # Serializar as datas antes de criar o objeto para evitar erro de serialização
                        paciente_dict = json.loads(json.dumps(paciente_dict, cls=DateEncoder))

                        # Atualizar usando o dicionário diretamente
                        update_response = await repository.update(UUID(id_existente), paciente_dict)
                        logger.info(f"DEBUG Update Response - ID Origem: {id_origem}, Tipo: {type(update_response).__name__}, Resposta: {update_response!r}")

                        # --- Correção Final: Usar o dicionário retornado diretamente ---
                        paciente_dict_atualizado = update_response if isinstance(update_response, dict) else None
                        paciente_obj_para_carteirinha = paciente_dict_atualizado
                        # --- Fim Correção Final ---
                        
                        if paciente_dict_atualizado:
                            total_importados += 1 # Conta como processado
                            total_atualizados += 1
                            logger.info(f"Paciente atualizado com sucesso: {paciente_dict_atualizado.get('nome', 'N/A')} (ID: {id_existente})")
                        else:
                            logger.error(f"Falha ao obter/processar dicionário do paciente atualizado {paciente_dict.get('nome')} após PATCH. Resposta: {update_response!r}")
                            erro = {
                                "paciente": paciente_dict.get('nome', 'Nome não disponível'),
                                "erro": "Falha ao processar resposta da atualização."
                            }
                            erros.append(erro)
                            paciente_obj_para_carteirinha = None # Evita processar carteirinha
                    else:
                        # O paciente não existe, criar um novo
                        try:
                            # Serializar as datas antes de criar o objeto
                            paciente_dict = json.loads(json.dumps(paciente_dict, cls=DateEncoder))
                            paciente_create = PacienteCreate(**paciente_dict)
                            logger.info(f"Objeto PacienteCreate criado com id_origem: {paciente_create.id_origem if hasattr(paciente_create, 'id_origem') else 'NÃO POSSUI'}")

                            # +++ Log Adicionado: Inspecionar resposta do create +++
                            create_response = await repository.create(paciente_create)
                            logger.info(f"DEBUG Create Response - ID Origem: {paciente_create.id_origem}, Tipo: {type(create_response).__name__}, Resposta: {create_response!r}")
                            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++

                            # --- Correção Final: Usar o dicionário retornado diretamente ---
                            created_paciente_dict = create_response if isinstance(create_response, dict) else None
                            paciente_obj_para_carteirinha = created_paciente_dict
                            # --- Fim Correção Final ---
                            
                            if created_paciente_dict:
                                total_importados += 1
                                logger.info(f"Paciente importado com sucesso: {created_paciente_dict.get('nome','N/A')} (ID: {created_paciente_dict.get('id')})")
                            else:
                                logger.error(f"Falha ao obter/processar dicionário do paciente criado {paciente_dict.get('nome')} após POST. Resposta: {create_response!r}")
                                erro = {
                                    "paciente": paciente_dict.get('nome', 'Nome não disponível'),
                                    "erro": "Falha ao processar resposta da criação."
                                }
                                erros.append(erro)
                                paciente_obj_para_carteirinha = None # Evita processar carteirinha
                                continue # Pula para o próximo paciente

                        except Exception as e:
                            # Make this log super clear
                            error_type = type(e).__name__
                            error_repr = repr(e)
                            # Tenta obter o nome do paciente do dict original se possível
                            paciente_nome_inner_exc = 'Nome Indisponível'
                            if 'paciente_dict' in locals() and isinstance(paciente_dict, dict):
                                paciente_nome_inner_exc = paciente_dict.get('nome', 'Nome Indisponível no Inner Except')
                            elif 'paciente_create' in locals() and hasattr(paciente_create, 'nome'):
                                paciente_nome_inner_exc = paciente_create.nome
                            
                            logger.error(f"Erro ao criar paciente {paciente_nome_inner_exc}: Tipo={error_type}, Repr={error_repr}")
                            erro = {
                                "paciente": paciente_nome_inner_exc,
                                "erro": f"Erro ao criar: {error_repr}"
                            }
                            erros.append(erro)
                            # Pula para o próximo paciente
                            paciente_obj_para_carteirinha = None # Garante que não tentará criar carteirinha
                            continue # Pula para o próximo paciente

                    # Log que estava faltando (deve funcionar agora)
                    if paciente_obj_para_carteirinha:
                        num_cart = paciente_obj_para_carteirinha.get('numero_carteirinha')
                        pac_id = paciente_obj_para_carteirinha.get('id')
                        logger.info(f"DEBUG Carteirinha Check - Paciente ID: {pac_id}, "
                                    f"Numero Carteirinha: '{num_cart}' (Tipo: {type(num_cart).__name__}), "
                                    f"Plano Unimed ID: {plano_unimed_id}")
                    else:
                        logger.info("DEBUG Carteirinha Check - paciente_obj_para_carteirinha é None, pulando carteirinha.")
                    
                    # ----- Lógica da Carteirinha (Unificada) -----
                    # Usa paciente_obj_para_carteirinha que agora é um DICIONÁRIO
                    if paciente_obj_para_carteirinha and paciente_obj_para_carteirinha.get('numero_carteirinha') and plano_unimed_id:
                        # Usa .get() para segurança e ['id'] para acesso
                        numero_carteirinha = paciente_obj_para_carteirinha.get('numero_carteirinha', '').strip()
                        paciente_id_atual = paciente_obj_para_carteirinha['id'] # Extrai o ID do dicionário
                        paciente_nome_atual = paciente_obj_para_carteirinha.get('nome', 'Nome Indisponível')
                        
                        if numero_carteirinha:
                            try:
                                # Verificar se o paciente já tem alguma carteirinha com este número para o plano Unimed
                                carteirinhas_existentes = db.from_("carteirinhas")\
                                    .select("id,numero_carteirinha,plano_saude_id")\
                                    .eq("paciente_id", paciente_id_atual)\
                                    .eq("plano_saude_id", plano_unimed_id)\
                                    .is_("deleted_at", "null")\
                                    .execute()

                                carteirinha_existente_com_numero = None
                                if carteirinhas_existentes.data:
                                    for c in carteirinhas_existentes.data:
                                        if c.get("numero_carteirinha") == numero_carteirinha:
                                            carteirinha_existente_com_numero = c
                                            break

                                if not carteirinha_existente_com_numero:
                                    # Criar nova carteirinha
                                    nova_carteirinha = {
                                        "paciente_id": paciente_id_atual, # Usa o ID extraído do dicionário
                                        "plano_saude_id": plano_unimed_id,
                                        "numero_carteirinha": numero_carteirinha,
                                        "status": "ativa",
                                        "created_by": usuario_id,
                                        "updated_by": usuario_id
                                    }
                                    carteirinha_result = db.from_("carteirinhas").insert(nova_carteirinha).execute()
                                    if carteirinha_result.data:
                                        logger.info(f"Carteirinha criada automaticamente para {paciente_nome_atual}, número: {numero_carteirinha}")
                                    else:
                                        logger.warning(f"Falha ao criar carteirinha para {paciente_nome_atual}: {carteirinha_result.error}")
                                else:
                                    logger.info(f"Paciente {paciente_nome_atual} já possui carteirinha {numero_carteirinha} para o plano Unimed")
                            except Exception as e:
                                logger.error(f"Erro ao processar carteirinha para {paciente_nome_atual}: {str(e)}")
                                # Não falhar a importação só porque a carteirinha falhou
                    elif paciente_obj_para_carteirinha and not paciente_obj_para_carteirinha.get('numero_carteirinha'):
                        # +++ Log Adicionado: Caso onde numero_carteirinha é 'falsy' +++
                        logger.info(f"DEBUG Carteirinha Skip - Paciente {paciente_obj_para_carteirinha.get('nome', 'N/A')} não possui numero_carteirinha.")
                        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    elif not plano_unimed_id:
                        # +++ Log Adicionado: Caso onde plano_unimed_id é None (não deveria acontecer aqui, mas por segurança) +++
                        logger.warning("DEBUG Carteirinha Skip - plano_unimed_id é None dentro do loop.")
                        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

                    # ----- Fim Lógica da Carteirinha -----
                except Exception as e:
                    error_type = type(e).__name__
                    error_repr = repr(e)
                    logger.error(f"Erro interno ao processar o paciente {paciente_dict.get('nome', 'Nome Indisponível')}: Tipo={error_type}, Repr={error_repr}")
                    erro = {
                        "paciente": paciente_dict.get('nome', 'Nome Indisponível'),
                        "erro": f"Erro interno: {error_repr}"
                    }
                    erros.append(erro)
                    continue
            except Exception as e:
                # Registrar erro para este paciente (loop principal)
                error_type = type(e).__name__
                error_repr = repr(e)
                error_str = str(e)
                logger.error(f"Erro CRÍTICO ao importar paciente {paciente_mysql.get('client_nome', 'Nome não disponível')}: Tipo={error_type}, Repr={error_repr}, Str={error_str}")
                erro = {
                    "paciente": paciente_mysql.get('client_nome', 'Nome não disponível'),
                    "erro": f"Erro CRÍTICO - Tipo: {error_type}, Detalhes: {error_repr}" # Usar repr
                }
                erros.append(erro)
        
        # Registrar a importação no controle de importação
        if total_importados > 0 or total_atualizados > 0:
            try:
                # Garantir que as datas estão em formato ISO para evitar problemas
                data_registro_iso = data_registro_max.isoformat() if data_registro_max else None
                data_atualizacao_iso = data_atualizacao_max.isoformat() if data_atualizacao_max else None
                
                # Logar para debug
                logger.info(f"Registrando importação com datas máximas - Registro: {data_registro_iso}, Atualização: {data_atualizacao_iso}")
                
                # Preparar os dados para inserção
                import_data = {
                    "ultima_data_registro_importada": data_registro_iso,
                    "ultima_data_atualizacao_importada": data_atualizacao_iso,
                    "quantidade_registros_importados": total_importados - total_atualizados,
                    "quantidade_registros_atualizados": total_atualizados,
                    "usuario_id": usuario_id,
                    "timestamp_importacao": datetime.datetime.now().isoformat(),
                    "observacoes": f"Importação: {total_importados} importados, {total_atualizados} atualizados, {len(erros)} erros"
                }
                
                # Serializar novamente para garantir que não há objetos datetime
                import_data = json.loads(json.dumps(import_data, cls=DateEncoder))
                
                db.from_("controle_importacao_pacientes").insert(import_data).execute()
                logger.info("Registro de importação salvo com sucesso")
            except Exception as e:
                logger.error(f"Erro ao registrar importação: {str(e)}")
                # Não deixar falhar a importação só porque o registro falhou
        
        # Resultado da importação
        return {
            "success": True,
            "message": f"Importação concluída. {total_importados} pacientes importados, {total_atualizados} atualizados com sucesso.",
            "importados": total_importados,
            "total": len(pacientes_mysql),
            "total_erros": len(erros),
            "total_atualizados": total_atualizados,
            "erros": erros,
            "connection_status": {
                "success": True,
                "message": mensagem
            },
            "ultima_data_registro": data_registro_max.isoformat() if data_registro_max else None,
            "ultima_data_atualizacao": data_atualizacao_max.isoformat() if data_atualizacao_max else None
        }
        
    except Exception as e:
        logger.error(f"Erro na importação de pacientes: {str(e)}")
        return {
            "success": False,
            "message": f"Erro durante a importação: {str(e)}",
            "importados": 0,
            "total": 0,
            "erros": [str(e)],
            "connection_status": {
                "success": True,
                "message": "Conexão estabelecida, mas houve erro na importação"
            }
        }