from fastapi import APIRouter, Depends, Query, Request, Response, status, HTTPException
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import pymysql
import os
from dotenv import load_dotenv
from ..utils.date_utils import format_date, format_date_fields, DATE_FIELDS, DateUUIDEncoder
from ..repositories.database_supabase import get_supabase_client, SupabaseClient
import sshtunnel
import logging
from backend.routes.agendamento import mapear_agendamento
import json
from postgrest.exceptions import APIError

logger = logging.getLogger(__name__)


load_dotenv()

# Configurações SSH (CORRIGIDO)
SSH_CONFIG = {
    'host': os.getenv('SSH_HOST'),
    'user': os.getenv('SSH_USER'),
    'password': os.getenv('SSH_PASSWORD'),
    'port': int(os.getenv('SSH_PORT', 22)) # Porta SSH, default 22
}

# Configurações de conexão MySQL (CORRIGIDO - apenas user/pass do .env)
MYSQL_CONFIG = {
    'remote_host': os.getenv('MYSQL_HOST', '127.0.0.1'), # Host MySQL no servidor remoto (geralmente 127.0.0.1)
    'remote_port': int(os.getenv('MYSQL_PORT', 3306)), # Porta MySQL no servidor remoto
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

router = APIRouter(tags=["importacao"])

# Rota de teste
# @router.get("/teste") # Removendo decorador se não for uma rota real
async def rota_de_teste():
    return {"message": "Rota de teste de importação funcionando!"}

# Conexão com MySQL (sistema legado) - ADAPTADA PARA USAR TÚNEL SSH
def get_mysql_connection(database_name):
    """Estabelece conexão com MySQL via túnel SSH."""
    tunnel = None
    local_tunnel_port = 3307 # Porta local para o túnel
    try:
        # Log detalhado das configurações SSH antes de tentar a conexão
        logger.info("--- [DEBUG] Configurações para Túnel SSH ---")
        logger.info(f"SSH Host: {SSH_CONFIG.get('host')}")
        logger.info(f"SSH Port: {SSH_CONFIG.get('port')}")
        logger.info(f"SSH User: {SSH_CONFIG.get('user')}")
        # Nunca logar a senha completa em produção, mas útil para debug extremo localmente
        # logger.info(f"SSH Password: {SSH_CONFIG.get('password')}") # DESCOMENTE COM CUIDADO!
        logger.info(f"SSH Password fornecida: {'Sim' if SSH_CONFIG.get('password') else 'Não'}")
        logger.info(f"MySQL Remoto (dentro do SSH): {MYSQL_CONFIG.get('remote_host')}:{MYSQL_CONFIG.get('remote_port')}")
        logger.info(f"Porta Local do Túnel: {local_tunnel_port}")
        logger.info("--- [DEBUG] Fim Configurações ---")

        # Criar túnel SSH usando SSH_CONFIG correto
        logger.info(f"Tentando túnel SSH para {SSH_CONFIG['host']}:{SSH_CONFIG['port']} como {SSH_CONFIG['user']}")
        tunnel = sshtunnel.SSHTunnelForwarder(
            (SSH_CONFIG['host'], SSH_CONFIG['port']), # <<< Conexão SSH
            ssh_username=SSH_CONFIG['user'],
            ssh_password=SSH_CONFIG['password'],
            remote_bind_address=(MYSQL_CONFIG['remote_host'], MYSQL_CONFIG['remote_port']), # <<< Endereço MySQL no servidor remoto
            local_bind_address=('127.0.0.1', local_tunnel_port)  # <<< Endereço local do túnel
        )
        logger.info("SSHTunnelForwarder object created. Attempting tunnel.start()...")
        tunnel.start()
        logger.info("tunnel.start() completed.")
        logger.info(f"Túnel SSH estabelecido: localhost:{local_tunnel_port} -> {MYSQL_CONFIG['remote_host']}:{MYSQL_CONFIG['remote_port']} via {SSH_CONFIG['host']}")

        # Configuração para conectar ao MySQL localmente através do túnel
        mysql_conn_config = {
            'host': '127.0.0.1',             # <<< Conecta ao host local do túnel
            'port': local_tunnel_port,       # <<< Conecta à porta local do túnel
            'user': MYSQL_CONFIG['user'],
            'password': MYSQL_CONFIG['password'],
            'database': database_name,       # <<< Banco de dados específico
            'charset': MYSQL_CONFIG['charset'],
            'cursorclass': MYSQL_CONFIG['cursorclass']
        }

        logger.info(f"Conectando ao MySQL via túnel em 127.0.0.1:{local_tunnel_port} (banco: {database_name}) ...")
        connection = pymysql.connect(**mysql_conn_config)
        logger.info("Conexão MySQL via túnel estabelecida com sucesso!")

        # Retorna a conexão e o túnel para que possam ser fechados depois
        return connection, tunnel

    except Exception as e:
        logger.error(f"Falha ao estabelecer túnel SSH ou conexão MySQL: {e}", exc_info=True)
        # Fecha o túnel se ele foi iniciado mas a conexão MySQL falhou ou outra exceção ocorreu
        if tunnel and tunnel.is_active:
            try:
                tunnel.stop()
                logger.info("Túnel SSH (parcialmente aberto) fechado devido a erro.")
            except Exception as tunnel_close_error:
                 logger.error(f"Erro ao tentar fechar túnel SSH após falha: {tunnel_close_error}")
        raise # Re-levanta a exceção para ser tratada no endpoint

# Função auxiliar para fechar conexão e túnel
def close_connection_and_tunnel(connection, tunnel):
    """Fecha a conexão MySQL e o túnel SSH de forma segura."""
    if connection:
        try:
            connection.close()
            logger.info("Conexão MySQL fechada.")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão MySQL: {e}", exc_info=True)
    if tunnel and tunnel.is_active:
        try:
            tunnel.stop()
            logger.info("Túnel SSH fechado.")
        except Exception as e:
             logger.error(f"Erro ao fechar túnel SSH: {e}", exc_info=True)

# Rotas de verificação e importação individuais que causam erro
# @router.get("/verificar-quantidade-agendamentos") ...
# @router.get("/importar-agendamentos") ...
# @router.get("/verificar-quantidade-profissoes") ...
# @router.post("/importar-profissoes") ...
# @router.get("/verificar-quantidade-locais") ...
# @router.post("/importar-locais") ...
# @router.get("/verificar-quantidade-salas") ...
# @router.post("/importar-salas") ...
# @router.get("/verificar-quantidade-usuarios-aba") ...
# @router.post("/importar-usuarios-aba") ...
# @router.post("/importar-usuarios-profissoes") ...
# @router.post("/importar-usuarios-especialidades") ...
# @router.post("/importar-agendamentos-profissionais") ...

# Endpoints para importação de profissões (ws_profissoes)
async def verificar_quantidade_profissoes(
    banco_dados: str = Query("abalarissa_db"),
    tabela: str = Query("ws_profissoes"),
    data_inicial: Optional[str] = Query(None)
):
    """
    Verifica a quantidade de profissões disponíveis para importação
    """
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT COUNT(*) as total FROM {banco_dados}.{tabela}
                """
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += f" WHERE registration_date >= %s"
                    cursor.execute(query, (data_inicial_str,))
                else:
                    cursor.execute(query)
                    
                result = cursor.fetchone()
                
                return {
                    "success": True,
                    "message": "Contagem realizada com sucesso",
                    "quantidade": result['total'] if result and 'total' in result else 0
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao verificar quantidade de profissões: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao verificar quantidade: {str(e)}",
            "quantidade": 0
        }

async def importar_profissoes(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient
):
    """
    Importa profissões do sistema Aba para o Supabase
    """
    if not connection:
        raise ValueError("A conexão MySQL deve ser fornecida para esta função.")

    novos_registros = 0
    registros_atualizados = 0

    try:
        with connection.cursor() as cursor:
            query = f"""
            SELECT 
                profissao_id, 
                profissao_name, 
                profissao_status
            FROM {tabela}
            ORDER BY profissao_id
            """
            
            cursor.execute(query)
            profissoes = cursor.fetchall()
            
            for profissao in profissoes:
                try:
                    result = supabase.table("profissoes").select("id").eq("profissao_id", profissao["profissao_id"]).execute()
                    
                    data_to_upsert = {
                        "profissao_name": profissao["profissao_name"],
                        "profissao_status": profissao["profissao_status"],
                        "updated_at": datetime.now().isoformat()
                    }

                    if result.data:
                        supabase.table("profissoes").update(data_to_upsert).eq("profissao_id", profissao["profissao_id"]).execute()
                        registros_atualizados += 1
                    else:
                        data_to_upsert["profissao_id"] = profissao["profissao_id"]
                        data_to_upsert["created_at"] = datetime.now().isoformat()
                        supabase.table("profissoes").insert(data_to_upsert).execute()
                        novos_registros += 1
                except Exception as inner_e:
                    print(f"Erro ao processar profissão ID {profissao.get('profissao_id')}: {inner_e}")
                    continue

        return {
            "success": True,
            "message": "Importação de profissões concluída",
            "novos_registros": novos_registros,
            "registros_atualizados": registros_atualizados,
            "total_processado": novos_registros + registros_atualizados
        }
    except Exception as e:
        print(f"Erro na importação de profissões: {e}")
        raise

# Endpoints para importação de locais (ps_locales)
async def verificar_quantidade_locais(
    banco_dados: str = Query("abalarissa_db"),
    tabela: str = Query("ps_locales"),
    data_inicial: Optional[str] = Query(None)
):
    """
    Verifica a quantidade de locais disponíveis para importação
    """
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT COUNT(*) as total FROM {banco_dados}.{tabela}
                """
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += f" WHERE registration_date >= %s"
                    cursor.execute(query, (data_inicial_str,))
                else:
                    cursor.execute(query)
                    
                result = cursor.fetchone()
                
                return {
                    "success": True,
                    "message": "Contagem realizada com sucesso",
                    "quantidade": result['total'] if result and 'total' in result else 0
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao verificar quantidade de locais: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao verificar quantidade: {str(e)}",
            "quantidade": 0
        }

async def importar_locais(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient,
    data_inicial: Optional[str] = None
):
    """
    Importa locais do sistema Aba para o Supabase
    """
    novos_registros = 0
    registros_atualizados = 0
    try:
        with connection.cursor() as cursor:
            query = f"""
            SELECT 
                local_id, 
                local_nome
            FROM {tabela}
            """
            
            params = []
            
            if data_inicial:
                data_inicial_dt = datetime.fromisoformat(data_inicial)
                data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                query += " WHERE registration_date >= %s"
                params.append(data_inicial_str)
            
            query += " ORDER BY local_id"
            
            cursor.execute(query, params if params else None)
            locais = cursor.fetchall()
            
            for local in locais:
                try:
                    result = supabase.table("locais").select("id").eq("local_id", local["local_id"]).execute()
                    
                    data_to_upsert = {
                        "local_nome": local["local_nome"],
                        "updated_at": datetime.now().isoformat()
                    }
                    if result.data:
                        supabase.table("locais").update(data_to_upsert).eq("local_id", local["local_id"]).execute()
                        registros_atualizados += 1
                    else:
                        data_to_upsert["local_id"] = local["local_id"]
                        data_to_upsert["created_at"] = datetime.now().isoformat()
                        supabase.table("locais").insert(data_to_upsert).execute()
                        novos_registros += 1
                except Exception as inner_e:
                    print(f"Erro ao processar local ID {local.get('local_id')}: {inner_e}")

        return {
            "success": True,
            "message": "Importação de locais concluída",
            "novos_registros": novos_registros,
            "registros_atualizados": registros_atualizados,
            "total_processado": novos_registros + registros_atualizados
        }
    except Exception as e:
        print(f"Erro na importação de locais: {e}")
        raise

# Endpoints para importação de salas (ps_care_rooms)
async def verificar_quantidade_salas(
    banco_dados: str = Query("abalarissa_db"),
    tabela: str = Query("ps_care_rooms"),
    data_inicial: Optional[str] = Query(None)
):
    """
    Verifica a quantidade de salas disponíveis para importação
    """
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT COUNT(*) as total FROM {banco_dados}.{tabela}
                """
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += f" WHERE registration_date >= %s"
                    cursor.execute(query, (data_inicial_str,))
                else:
                    cursor.execute(query)
                    
                result = cursor.fetchone()
                
                return {
                    "success": True,
                    "message": "Contagem realizada com sucesso",
                    "quantidade": result['total'] if result and 'total' in result else 0
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao verificar quantidade de salas: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao verificar quantidade: {str(e)}",
            "quantidade": 0
        }

async def importar_salas(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient,
    data_inicial: Optional[str] = None
):
    """
    Importa salas do sistema Aba (ps_care_rooms) para o Supabase, incluindo mais colunas.
    """
    # A conexão MySQL agora é gerenciada pela função chamadora (importar_tudo_sistema_aba)
    if not connection:
        raise ValueError("A conexão MySQL deve ser fornecida para esta função.")
        
    novos_registros = 0
    registros_atualizados = 0
    erros = 0
    
    try:
        with connection.cursor() as cursor:
            # Seleciona todas as colunas relevantes
            query = f"""SELECT 
                        room_id, 
                        room_local_id, 
                        room_name, 
                        room_description, 
                        room_type, 
                        room_status, 
                        room_registration_date, 
                        room_lastupdate, 
                        multiple, 
                        room_capacidade 
                    FROM {tabela} 
                    ORDER BY room_id"""
            
            cursor.execute(query)
            salas_mysql = cursor.fetchall()
            logger.info(f"Encontradas {len(salas_mysql)} salas no MySQL.")
            
            for sala in salas_mysql:
                try:
                    mysql_room_id = str(sala["room_id"]) # Chave para upsert

                    # --- CORREÇÃO AQUI: Converter datas para ISO string --- 
                    reg_date = sala.get("room_registration_date")
                    last_update = sala.get("room_lastupdate")

                    reg_date_iso = reg_date.isoformat() if isinstance(reg_date, datetime) else reg_date
                    last_update_iso = last_update.isoformat() if isinstance(last_update, datetime) else last_update
                    # --- FIM DA CORREÇÃO ---

                    # Prepara dados para upsert
                    data_to_upsert = {
                        "room_id": mysql_room_id, # Incluir explicitamente para upsert
                        "room_local_id": str(sala.get("room_local_id")) if sala.get("room_local_id") is not None else None,
                        "room_name": sala.get("room_name"),
                        "room_description": sala.get("room_description"),
                        "room_type": sala.get("room_type"),
                        "room_status": sala.get("room_status"),
                        "room_registration_date": reg_date_iso, # Usar valor convertido
                        "room_lastupdate": last_update_iso,    # Usar valor convertido
                        "multiple": bool(sala.get("multiple")) if sala.get("multiple") is not None else None, # Converte tinyint para boolean
                        "room_capacidade": sala.get("room_capacidade"),
                        "updated_at": datetime.now().isoformat()
                    }
                    # Remover Nones explicitamente se necessário (Upsert geralmente lida bem)
                    data_to_upsert = {k: v for k, v in data_to_upsert.items() if v is not None}

                    # Usar upsert para inserir ou atualizar
                    upsert_result = supabase.table("salas").upsert(
                        data_to_upsert, 
                        on_conflict="room_id" # Use room_id como o conflict target
                    ).execute()

                    # Contabilizar baseado no resultado ou assumindo sucesso se não houver erro
                    # A API v2 do Supabase pode não retornar dados claros sobre insert vs update no upsert
                    # Vamos assumir que foi atualização se já existia, senão novo.
                    # Uma forma mais robusta seria fazer um SELECT antes, mas upsert é mais eficiente.
                    # Simplificação: Contamos como sucesso, mas não diferenciamos novo/atualizado aqui
                    # para evitar complexidade extra na contagem pós-upsert.
                    # A contagem será feita comparando o total antes e depois se necessário,
                    # mas para este retorno, focamos no sucesso geral.
                    
                    # Se chegou aqui, o upsert deu certo. Precisamos saber se foi insert ou update.
                    # Solução simples: fazemos um select ANTES do upsert (menos eficiente)
                    # Solução Upsert: Não temos info direta insert/update no V2 do python client.
                    # Assumiremos atualização como padrão e novo se erro específico indicasse não existência?
                    # Melhoria: Lógica de contagem pode ser aprimorada.
                    # Por ora, vamos apenas incrementar um contador geral de sucesso.

                except Exception as inner_e:
                    logger.error(f"Erro ao processar sala ID {mysql_room_id}: {inner_e}")
                    erros += 1

        # Obter contagem final para calcular novos/atualizados (exemplo)
        # final_count = supabase.table("salas").select('id', count='exact').execute().count
        # novos_registros = final_count - initial_count # Se initial_count fosse pego antes
        # registros_atualizados = len(salas_mysql) - erros - novos_registros # Estimativa

        # Simplificação: Retorna apenas o total processado e erros
        total_processado = len(salas_mysql)
        registros_sucesso = total_processado - erros

        return {
            "success": erros == 0,
            "message": f"Importação de salas concluída com {registros_sucesso} sucessos e {erros} erros.",
            # "novos_registros": novos_registros, # Contagem complexa com upsert v2
            # "registros_atualizados": registros_atualizados, # Contagem complexa com upsert v2
            "total_processado": total_processado,
            "registros_importados": registros_sucesso, # Campo esperado pelo controle
            "erros": erros
        }
    except Exception as e:
        logger.error(f"Erro na importação de salas: {e}")
        # Levantar a exceção para ser capturada pelo endpoint
        raise HTTPException(status_code=500, detail=f"Erro interno na importação de salas: {str(e)}")

# Endpoints para importação de usuários (ws_users)
async def verificar_quantidade_usuarios_aba(
    banco_dados: str = Query("abalarissa_db"),
    tabela: str = Query("ws_users"),
    data_inicial: Optional[str] = Query(None)
):
    """
    Verifica a quantidade de usuários do sistema Aba disponíveis para importação
    """
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT COUNT(*) as total FROM {banco_dados}.{tabela}
                """
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += f" WHERE registration_date >= %s"
                    cursor.execute(query, (data_inicial_str,))
                else:
                    cursor.execute(query)
                    
                result = cursor.fetchone()
                
                return {
                    "success": True,
                    "message": "Contagem realizada com sucesso",
                    "quantidade": result['total'] if result and 'total' in result else 0
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao verificar quantidade de usuários Aba: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao verificar quantidade: {str(e)}",
            "quantidade": 0
        }

async def importar_usuarios_aba(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient,
    data_inicial: Optional[str] = None
):
    """
    Importa usuários do sistema Aba para o Supabase
    """
    connection = None
    tunnel = None
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        supabase = get_supabase_client()
        
        novos_registros = 0
        registros_atualizados = 0
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT 
                    user_id, 
                    user_name, 
                    user_lastname
                FROM {banco_dados}.{tabela}
                """
                
                params = []
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += " WHERE registration_date >= %s"
                    params.append(data_inicial_str)
                
                query += " ORDER BY user_id"
                
                cursor.execute(query, params if params else None)
                usuarios = cursor.fetchall()
                
                for usuario in usuarios:
                    # Verificar se já existe
                    result = supabase.table("usuarios_aba").select("*").eq("user_id", usuario["user_id"]).execute()
                    
                    if result.data and len(result.data) > 0:
                        # Atualizar registro existente
                        supabase.table("usuarios_aba").update({
                            "user_name": usuario["user_name"],
                            "user_lastname": usuario["user_lastname"],
                            "updated_at": datetime.now().isoformat()
                        }).eq("user_id", usuario["user_id"]).execute()
                        registros_atualizados += 1
                    else:
                        # Inserir novo registro
                        supabase.table("usuarios_aba").insert({
                            "user_id": usuario["user_id"],
                            "user_name": usuario["user_name"],
                            "user_lastname": usuario["user_lastname"],
                            "created_at": datetime.now().isoformat(),
                            "updated_at": datetime.now().isoformat()
                        }).execute()
                        novos_registros += 1
                
                return {
                    "success": True,
                    "message": "Importação concluída com sucesso",
                    "novos_registros": novos_registros,
                    "registros_atualizados": registros_atualizados,
                    "total_processado": novos_registros + registros_atualizados
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao importar usuários Aba: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao importar usuários Aba: {str(e)}",
            "novos_registros": 0,
            "registros_atualizados": 0,
            "total_processado": 0
        }

# Endpoint para importar relações usuários-profissões
async def importar_usuarios_profissoes(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient,
    data_inicial: Optional[str] = None
):
    """
    Importa relações entre usuários e profissões do sistema Aba
    """
    connection = None
    tunnel = None
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        supabase = get_supabase_client()
        
        novos_registros = 0
        registros_atualizados = 0
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT 
                    user_id, 
                    profissao_id
                FROM {banco_dados}.{tabela}
                """
                
                params = []
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += " WHERE registration_date >= %s"
                    params.append(data_inicial_str)
                
                cursor.execute(query, params if params else None)
                relacoes = cursor.fetchall()
                
                for relacao in relacoes:
                    # Buscar IDs nas tabelas do Supabase
                    usuario_result = supabase.table("usuarios_aba").select("id").eq("user_id", relacao["user_id"]).execute()
                    profissao_result = supabase.table("profissoes").select("id").eq("profissao_id", relacao["profissao_id"]).execute()
                    
                    if usuario_result.data and profissao_result.data:
                        usuario_id = usuario_result.data[0]["id"]
                        profissao_id = profissao_result.data[0]["id"]
                        
                        # Verificar se a relação já existe
                        result = supabase.table("usuarios_profissoes").select("*").eq("usuario_aba_id", usuario_id).eq("profissao_id", profissao_id).execute()
                        
                        if not result.data:
                            # Inserir nova relação
                            supabase.table("usuarios_profissoes").insert({
                                "usuario_aba_id": usuario_id,
                                "profissao_id": profissao_id,
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            }).execute()
                            novos_registros += 1
                
                return {
                    "success": True,
                    "message": "Importação concluída com sucesso",
                    "novos_registros": novos_registros,
                    "total_processado": novos_registros
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao importar relações usuários-profissões: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao importar relações: {str(e)}",
            "novos_registros": 0,
            "total_processado": 0
        }

# Endpoint para importar especialidades (ws_especialidades)
async def importar_especialidades(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient
):
    """
    Importa especialidades do sistema Aba (ws_especialidades) para o Supabase
    """
    if not connection:
        raise ValueError("A conexão MySQL deve ser fornecida para esta função.")

    novos_registros = 0
    registros_atualizados = 0
    erros = 0

    try:
        with connection.cursor() as cursor:
            # Assumindo que a tabela MySQL é ws_especialidades
            query = f"""
            SELECT 
                especialidade_id, 
                especialidade_name
            FROM {tabela} 
            ORDER BY especialidade_id
            """
            
            cursor.execute(query)
            especialidades_mysql = cursor.fetchall()
            logger.info(f"Encontradas {len(especialidades_mysql)} especialidades no MySQL.")
            
            for especialidade in especialidades_mysql:
                try:
                    mysql_id = especialidade.get("especialidade_id")
                    mysql_name = especialidade.get("especialidade_name")
                    
                    if not mysql_id or not mysql_name:
                        logger.warning(f"Registro de especialidade inválido no MySQL: {especialidade}")
                        erros += 1
                        continue

                    # Verificar se já existe no Supabase pelo ID original
                    result = supabase.table("especialidades").select("id").eq("especialidade_id", mysql_id).execute()
                    
                    data_to_upsert = {
                        "nome": mysql_name,
                        "updated_at": datetime.now().isoformat()
                    }

                    if result.data:
                        # Atualiza se existente
                        supabase.table("especialidades").update(data_to_upsert).eq("especialidade_id", mysql_id).execute()
                        registros_atualizados += 1
                    else:
                        # Insere se não existente, incluindo o ID original
                        data_to_upsert["especialidade_id"] = mysql_id # Guarda o ID original
                        data_to_upsert["created_at"] = datetime.now().isoformat()
                        # Poderia adicionar created_by/updated_by se necessário
                        supabase.table("especialidades").insert(data_to_upsert).execute()
                        novos_registros += 1
                except Exception as inner_e:
                    logger.error(f"Erro ao processar especialidade ID {especialidade.get('especialidade_id')}: {inner_e}", exc_info=True)
                    erros += 1
                    continue

        total_processado = novos_registros + registros_atualizados + erros
        logger.info(f"Importação de especialidades: {novos_registros} novas, {registros_atualizados} atualizadas, {erros} erros.")
        return {
            "success": True,
            "message": "Importação de especialidades concluída",
            "novos_registros": novos_registros,
            "registros_atualizados": registros_atualizados,
            "erros": erros,
            "total_processado": total_processado
        }
    except Exception as e:
        logger.error(f"Erro na importação de especialidades: {e}", exc_info=True)
        raise # Re-levanta a exceção para ser capturada pela função principal

# Endpoint para importar relações usuários-especialidades
async def importar_usuarios_especialidades(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient,
    data_inicial: Optional[str] = None
):
    """
    Importa relações entre usuários e especialidades do sistema Aba
    """
    novos_registros = 0
    registros_atualizados = 0
    erros_mapeamento = 0

    try:
        usuarios_map = {u['user_id']: u['id'] for u in supabase.table('usuarios_aba').select('id, user_id').execute().data}
        especialidades_map = {e['especialidade_id']: e['id'] for e in supabase.table('especialidades').select('id, especialidade_id').not_.is_('especialidade_id', None).execute().data}

        with connection.cursor() as cursor:
            query = f"""
            SELECT 
                user_id, 
                especialidade_id
            FROM {tabela}
            """
            params = []

            logger.info(f"Executando consulta para relações usuários-especialidades: {query}")
            cursor.execute(query, params if params else None)
            relacoes_mysql = cursor.fetchall()
            logger.info(f"Encontradas {len(relacoes_mysql)} relações usuário-especialidade no MySQL.")

            for relacao in relacoes_mysql:
                try:
                    mysql_user_id = relacao["user_id"]
                    mysql_especialidade_id = relacao["especialidade_id"]

                    # Convert MySQL IDs to string for dictionary lookup
                    supabase_usuario_id = usuarios_map.get(str(mysql_user_id))
                    supabase_especialidade_id = especialidades_map.get(str(mysql_especialidade_id))

                    if supabase_usuario_id and supabase_especialidade_id:
                        result = supabase.table("usuarios_especialidades").select("id").eq("usuario_aba_id", supabase_usuario_id).eq("especialidade_id", supabase_especialidade_id).execute()

                        update_data = {
                            "updated_at": datetime.now().isoformat()
                        }

                        if result.data:
                            supabase.table("usuarios_especialidades").update(update_data).eq("usuario_aba_id", supabase_usuario_id).eq("especialidade_id", supabase_especialidade_id).execute()
                            registros_atualizados += 1
                        else:
                            insert_data = {
                                "usuario_aba_id": supabase_usuario_id,
                                "especialidade_id": supabase_especialidade_id,
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            }
                            supabase.table("usuarios_especialidades").insert(insert_data).execute()
                            novos_registros += 1
                    else:
                        erros_mapeamento += 1
                        logger.warning(f"Não foi possível mapear IDs para relação user_id={mysql_user_id}, especialidade_id={mysql_especialidade_id}")
                except Exception as inner_e:
                    logger.error(f"Erro ao processar relação user_id={relacao.get('user_id')}, especialidade_id={relacao.get('especialidade_id')}: {inner_e}", exc_info=True)
                    erros_mapeamento += 1

        total_processado = novos_registros + registros_atualizados + erros_mapeamento
        logger.info(f"Importação de relações usuários-especialidades: {novos_registros} novas, {registros_atualizados} atualizadas, {erros_mapeamento} erros.")
        return {
            "success": True,
            "message": "Importação de relações usuários-especialidades concluída",
            "novos_registros": novos_registros,
            "registros_atualizados": registros_atualizados,
            "erros_mapeamento": erros_mapeamento,
            "total_processado": total_processado
        }
    except Exception as e:
        logger.error(f"Erro na importação de relações usuários-especialidades: {e}", exc_info=True)
        raise

# Modificação da importação de agendamentos para incluir relações com profissionais
async def importar_agendamentos_profissionais(
    banco_dados: str,
    tabela: str,
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient,
    data_inicial: Optional[str] = None
):
    """
    Importa relações entre agendamentos e profissionais do sistema Aba
    """
    connection = None
    tunnel = None
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        supabase = get_supabase_client()
        
        novos_registros = 0
        
        try:
            with connection.cursor() as cursor:
                query = f"""
                SELECT 
                    schedule_id, 
                    professional_id
                FROM {banco_dados}.{tabela}
                """
                
                params = []
                
                if data_inicial:
                    data_inicial_dt = datetime.fromisoformat(data_inicial)
                    data_inicial_str = data_inicial_dt.strftime('%Y-%m-%d 00:00:00')
                    query += " WHERE registration_date >= %s"
                    params.append(data_inicial_str)
                
                cursor.execute(query, params if params else None)
                relacoes = cursor.fetchall()
                
                for relacao in relacoes:
                    # Buscar agendamento pelo id_origem
                    agendamento_result = supabase.table("agendamentos").select("id").eq("id_origem", relacao["schedule_id"]).execute()
                    
                    # Buscar profissional pelo id
                    profissional_result = supabase.table("usuarios_aba").select("id").eq("user_id", relacao["professional_id"]).execute()
                    
                    if agendamento_result.data and profissional_result.data:
                        agendamento_id = agendamento_result.data[0]["id"]
                        profissional_id = profissional_result.data[0]["id"]
                        
                        # Verificar se a relação já existe
                        result = supabase.table("agendamentos_profissionais").select("*").eq("schedule_id", agendamento_id).eq("professional_id", profissional_id).execute()
                        
                        if not result.data:
                            # Inserir nova relação
                            supabase.table("agendamentos_profissionais").insert({
                                "schedule_id": agendamento_id,
                                "professional_id": profissional_id,
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            }).execute()
                            novos_registros += 1
                
                return {
                    "success": True,
                    "message": "Importação concluída com sucesso",
                    "novos_registros": novos_registros,
                    "total_processado": novos_registros
                }
        finally:
            close_connection_and_tunnel(connection, tunnel)
            
    except Exception as e:
        print(f"Erro ao importar relações agendamentos-profissionais: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao importar relações: {str(e)}",
            "novos_registros": 0,
            "total_processado": 0
        }
    

# Função para importar tipos de pagamento (ws_pagamentos)


# Função para importar tipos de pagamento (ws_pagamentos)
async def importar_tipos_pagamento(
    banco_dados: str,
    tabela: str,  # Esperado: ws_pagamentos
    connection: pymysql.connections.Connection,
    supabase: SupabaseClient
):
    """
    Importa tipos de pagamento do sistema Aba para a tabela tipo_pagamento.
    """
    if not connection:
        raise ValueError("A conexão MySQL deve ser fornecida para esta função.")

    novos_registros = 0
    registros_atualizados = 0
    erros = 0
    log_erros = []

    try:
        with connection.cursor() as cursor:
            query = f"""
            SELECT 
                pagamento_id, 
                pagamento_name, 
                pagamento_carteirinha_obrigatoria,
                pagamento_status
            FROM {tabela}
            ORDER BY pagamento_id
            """
            cursor.execute(query)
            tipos_pagamento = cursor.fetchall()

            for tipo in tipos_pagamento:
                id_origem = tipo.get('pagamento_id')
                if not id_origem:
                    logger.warning(f"Registro de tipo de pagamento sem pagamento_id encontrado. Ignorando: {tipo}")
                    erros += 1
                    log_erros.append(f"Registro sem pagamento_id: {tipo}")
                    continue

                try:
                    # Mapear campos
                    nome = tipo.get('pagamento_name')
                    carteirinha_obrigatoria_str = tipo.get('pagamento_carteirinha_obrigatoria', 'N')  # Assumir 'N' se nulo
                    carteirinha_obrigatoria = carteirinha_obrigatoria_str.upper() == 'S' if carteirinha_obrigatoria_str else False
                    status_str = tipo.get('pagamento_status', 'I')  # Assumir 'I' (Inativo) se nulo
                    ativo = status_str.upper() == 'A'

                    # DEBUG: Logar detalhes do cliente Supabase antes da consulta
                    try:
                        supabase_url = getattr(supabase, 'supabase_url', 'URL não encontrada')
                        has_key = hasattr(supabase, 'supabase_key') and bool(getattr(supabase, 'supabase_key', None))
                        logger.debug(f"[DEBUG Import Tipo Pagamento ID {id_origem}] Supabase URL: {supabase_url}, Key Presente: {has_key}")
                    except Exception as log_err:
                        logger.error(f"[DEBUG] Erro ao logar config supabase: {log_err}")

                    # Verificar se já existe pelo ID de origem
                    result = None  # Resetar result
                    try:
                        result = supabase.table("tipo_pagamento").select("id").eq("id_origem", id_origem).execute()

                        # Tratamento SUPER robusto para a resposta
                        registro_encontrado = False
                        if result and hasattr(result, 'data') and isinstance(result.data, list):
                            if len(result.data) > 0:
                                registro_encontrado = True
                        elif result:
                            logger.warning(f"Resposta inesperada da consulta para ID {id_origem}. Status: {getattr(result, 'status_code', 'N/A')}, Data: {getattr(result, 'data', 'N/A')}")
                        else:
                            logger.error(f"Consulta para ID {id_origem} retornou None.")
                    except APIError as api_err:
                        logger.error(f"APIError ao consultar tipo_pagamento ID {id_origem}: Code={api_err.code}, Message={api_err.message}. Tentando continuar...")
                        registro_encontrado = False  # Assume que não existe se a consulta falhou
                    except Exception as query_err:
                        logger.error(f"Erro inesperado ao consultar tipo_pagamento ID {id_origem}: {query_err}", exc_info=True)
                        registro_encontrado = False  # Assume que não existe se a consulta falhou

                    # Dados para upsert (preparados independentemente da consulta)
                    data_to_upsert = {
                        "nome": nome,
                        "carteirinha_obrigatoria": carteirinha_obrigatoria,
                        "ativo": ativo,
                        "updated_at": datetime.now(timezone.utc).isoformat()  # Usar UTC
                    }

                    # Agora decide se atualiza ou insere baseado em registro_encontrado
                    if registro_encontrado:
                        # --- ATUALIZAÇÃO ---
                        try:
                            update_response = supabase.table("tipo_pagamento").update(data_to_upsert).eq("id_origem", id_origem).execute()
                            if hasattr(update_response, 'error') and update_response.error:
                                logger.error(f"Erro Supabase ao ATUALIZAR tipo_pagamento ID Origem {id_origem}: {update_response.error}")
                                erros += 1
                                log_erros.append(f"Erro Supabase (Update) ID {id_origem}: {update_response.error}")
                            elif not update_response.data:
                                logger.warning(f"Atualização de tipo_pagamento ID Origem {id_origem} não retornou dados (pode ser normal).")
                                registros_atualizados += 1
                            else:
                                registros_atualizados += 1
                        except Exception as update_err:
                            logger.error(f"Exceção ao ATUALIZAR tipo_pagamento ID Origem {id_origem}: {update_err}", exc_info=True)
                            erros += 1
                            log_erros.append(f"Erro Python (Update) ID {id_origem}: {update_err}")
                    else:
                        # --- INSERÇÃO ---
                        try:
                            data_to_upsert["id_origem"] = id_origem
                            data_to_upsert["created_at"] = datetime.now(timezone.utc).isoformat()  # Usar UTC
                            insert_response = supabase.table("tipo_pagamento").insert(data_to_upsert).execute()
                            if hasattr(insert_response, 'error') and insert_response.error:
                                logger.error(f"Erro Supabase ao INSERIR tipo_pagamento ID Origem {id_origem}: {insert_response.error}")
                                erros += 1
                                log_erros.append(f"Erro Supabase (Insert) ID {id_origem}: {insert_response.error}")
                            elif not insert_response.data:
                                logger.error(f"Falha ao INSERIR tipo_pagamento ID Origem {id_origem}: Insert não retornou dados.")
                                erros += 1
                                log_erros.append(f"Erro Supabase (Insert sem dados) ID {id_origem}")
                            else:
                                novos_registros += 1
                        except Exception as insert_err:
                            logger.error(f"Exceção ao INSERIR tipo_pagamento ID Origem {id_origem}: {insert_err}", exc_info=True)
                            erros += 1
                            log_erros.append(f"Erro Python (Insert) ID {id_origem}: {insert_err}")

                except Exception as inner_e:
                    logger.exception(f"Erro GERAL ao processar tipo_pagamento ID Origem {id_origem}: {inner_e}")
                    erros += 1
                    log_erros.append(f"Erro Python ID {id_origem}: {inner_e}")
                    continue  # Pula para o próximo registro

        return {
            "success": True,
            "message": f"Importação de tipos de pagamento concluída. Novos: {novos_registros}, Atualizados: {registros_atualizados}, Erros: {erros}",
            "novos_registros": novos_registros,
            "registros_atualizados": registros_atualizados,
            "erros": erros,
            "log_erros": log_erros,
            "total_processado": novos_registros + registros_atualizados
        }
    except Exception as e:
        logger.exception(f"Erro GERAL na importação de tipos de pagamento: {e}")
        return {
            "success": False,
            "message": f"Erro fatal na importação de tipos de pagamento: {e}",
            "novos_registros": novos_registros,
            "registros_atualizados": registros_atualizados,
            "erros": erros + 1  # Incrementa erro fatal
        }


# Função para importar/atualizar procedimentos com dados de faturamento (ws_pagamentos_x_codigos_faturamento)
async def importar_codigos_faturamento(banco_dados: str, tabela: str, connection, supabase: SupabaseClient) -> Dict[str, Any]:
    """Importa/Atualiza procedimentos com base na tabela ws_pagamentos_x_codigos_faturamento."""
    logger.info(f"Iniciando importação/atualização de Códigos de Faturamento da tabela {tabela}...")
    registros_criados = 0
    registros_atualizados = 0
    erros = 0
    log_erros = []
    total_origem = 0
    resultado_final = {}

    try:
        with connection.cursor() as cursor:
            query = f"""
            SELECT codigo_faturamento_id, pagamento_id, codigo_faturamento_descricao
            FROM {tabela}
            ORDER BY codigo_faturamento_id
            """
            cursor.execute(query)
            codigos_faturamento = cursor.fetchall()
            total_origem = len(codigos_faturamento)
            logger.info(f"Encontrados {total_origem} registros em {tabela}.")

            for codigo_fat in codigos_faturamento:
                id_origem = codigo_fat.get('codigo_faturamento_id')
                pagamento_id_origem = codigo_fat.get('pagamento_id')
                descricao = codigo_fat.get('codigo_faturamento_descricao')

                if not id_origem:
                    logger.warning(f"Registro sem codigo_faturamento_id: {codigo_fat}. Ignorando.")
                    erros += 1
                    log_erros.append(f"Registro sem ID: {codigo_fat}")
                    continue
                
                if not descricao:
                    logger.warning(f"Registro com CodFat ID {id_origem} não possui descrição. Usando placeholder.")
                    descricao = f"Procedimento {id_origem}"

                try:
                    # Busca procedimento existente
                    proc_result = supabase.table("procedimentos") \
                        .select("id") \
                        .eq("codigo_faturamento_id_origem", id_origem) \
                        .execute()
                    logger.debug(f"Busca Proc CodFat ID {id_origem}: {proc_result}")

                    if hasattr(proc_result, 'error') and proc_result.error:
                        raise Exception(f"Erro API Supabase (Busca): {proc_result.error}")

                    if proc_result and proc_result.data:
                        # --- ATUALIZAÇÃO ---
                        procedimento_id_supabase = proc_result.data[0]["id"]
                        data_to_update = {
                            "nome": descricao,
                            "pagamento_id_origem": pagamento_id_origem,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                        data_to_update = {k: v for k, v in data_to_update.items() if v is not None}
                        
                        update_response = supabase.table("procedimentos") \
                            .update(data_to_update) \
                            .eq("id", procedimento_id_supabase) \
                            .execute()
                        logger.debug(f"Update Proc ID {procedimento_id_supabase} (CodFat ID {id_origem}): {update_response}")
                        
                        if hasattr(update_response, 'error') and update_response.error:
                            raise Exception(f"Erro API Supabase (Update): {update_response.error}")
                        elif not update_response.data:
                            raise Exception("Falha Update Supabase (sem dados)")
                        else:
                            registros_atualizados += 1
                            logger.info(f"Procedimento {procedimento_id_supabase} atualizado com CodFat ID {id_origem}")
                    else:
                        # --- CRIAÇÃO ---
                        logger.info(f"Proc CodFat ID {id_origem} não encontrado. Criando novo...")
                        data_to_insert = {
                            "codigo_faturamento_id_origem": id_origem,
                            "pagamento_id_origem": pagamento_id_origem,
                            "nome": descricao,
                            "codigo": str(id_origem),
                            "tipo": 'consulta',
                            "ativo": True
                        }
                        data_to_insert = {k: v for k, v in data_to_insert.items() if v is not None}
                        
                        insert_response = supabase.table("procedimentos") \
                            .insert(data_to_insert) \
                            .execute()
                        logger.debug(f"Insert Proc CodFat ID {id_origem}: {insert_response}")
                        
                        if hasattr(insert_response, 'error') and insert_response.error:
                            raise Exception(f"Erro API Supabase (Insert): {insert_response.error}")
                        elif not insert_response.data:
                            raise Exception("Falha Insert Supabase (sem dados)")
                        else:
                            registros_criados += 1
                            logger.info(f"Novo procedimento criado para CodFat ID {id_origem} com ID: {insert_response.data[0]['id']}")
                            
                except Exception as inner_e:
                    logger.exception(f"Erro ao processar CodFat ID {id_origem}: {inner_e}")
                    erros += 1
                    log_erros.append(f"Erro CodFat ID {id_origem}: {inner_e}")
                    continue # Pula para o próximo registro
            
            # Fim do Loop - Preparar resultado de sucesso
            resultado_final = {
                "success": True,
                "message": f"Processamento concluído. Criados: {registros_criados}, Atualizados: {registros_atualizados}, Erros: {erros}",
                "registros_criados": registros_criados,
                "registros_atualizados": registros_atualizados,
                "erros": erros,
                "log_erros": log_erros,
                "total_origem": total_origem,
                "total_processado": registros_criados + registros_atualizados + erros
            }

    except Exception as e:
        # Erro geral (conexão, etc.)
        logger.exception(f"Erro GERAL na importação de códigos de faturamento: {e}")
        resultado_final = {
            "success": False,
            "message": f"Erro fatal na importação: {e}",
            "registros_criados": registros_criados,
            "registros_atualizados": registros_atualizados,
            "erros": erros + 1, # Adiciona erro fatal
            "log_erros": log_erros + [f"Erro Fatal: {e}"]
        }
    
    # Retorno unificado
    return resultado_final

# --- Função Auxiliar para Registrar Controle --- 
async def registrar_controle_importacao(tabela_nome: str, resultado: Dict[str, Any], supabase: SupabaseClient):
    """Registra o resultado de uma importação na tabela de controle."""
    try:
        if resultado.get("success", False):
            agora = datetime.now(timezone.utc).isoformat()
            registros = resultado.get("total_processado", 0)
            obs = resultado.get("message", "Importação concluída.")
            
            dados_controle = {
                "nome_tabela": tabela_nome,
                "ultima_importacao": agora,
                "registros_importados": registros,
                "observacoes": obs
            }
            # Upsert para inserir ou atualizar o registro de controle
            supabase.table("controle_importacao_tabelas_auxiliares").upsert(dados_controle).execute()
            logger.info(f"Controle de importação registrado para tabela: {tabela_nome}")
        else:
             logger.warning(f"Importação da tabela {tabela_nome} falhou. Controle não registrado.")
    except Exception as e:
        logger.error(f"Erro ao registrar controle de importação para {tabela_nome}: {e}", exc_info=True)

# --- Endpoints de API Individuais (Modificados para registrar controle) --- 

@router.post("/profissoes")
async def importar_profissoes_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "profissoes"
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela = "ws_profissoes"
        result = await importar_profissoes(banco_dados, tabela, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return result
    except Exception as e:
        logger.error(f"Erro na API /profissoes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/especialidades")
async def importar_especialidades_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "especialidades"
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela = "ws_especialidades"
        result = await importar_especialidades(banco_dados, tabela, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return result
    except Exception as e:
        logger.error(f"Erro na API /especialidades: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/locais")
async def importar_locais_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "locais"
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela = "ps_locales"
        result = await importar_locais(banco_dados, tabela, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return result
    except Exception as e:
        logger.error(f"Erro na API /locais: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/salas")
async def importar_salas_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    resultado_importacao = {}
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        resultado_importacao = await importar_salas(
            banco_dados=banco_dados, 
            tabela="ps_care_rooms", 
            connection=connection, 
            supabase=supabase
        )
        # Registrar no controle APÓS a importação principal ter sucesso (ou falhado e tratado)
        await registrar_controle_importacao("salas", resultado_importacao, supabase)
        # -- CORREÇÃO: Usar encoder no retorno final --
        return json.loads(json.dumps(resultado_importacao, cls=DateUUIDEncoder))
    except HTTPException as http_exc:
            # Re-levantar exceções HTTP para que o FastAPI as trate corretamente
            raise http_exc
    except Exception as e:
        logger.error(f"Erro no endpoint /salas: {e}")
        # Registrar falha no controle se a importação falhou
        await registrar_controle_importacao("salas", {"success": False, "message": str(e)}, supabase)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/usuarios-aba")
async def importar_usuarios_aba_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "usuarios_aba"
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela = "ws_users"
        result = await importar_usuarios_aba(banco_dados, tabela, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return result
    except Exception as e:
        logger.error(f"Erro na API /usuarios-aba: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/usuarios-profissoes")
async def importar_usuarios_profissoes_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "usuarios_profissoes"
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela = "ws_users_profissoes"
        result = await importar_usuarios_profissoes(banco_dados, tabela, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return result
    except Exception as e:
        logger.error(f"Erro na API /usuarios-profissoes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/usuarios-especialidades")
async def importar_usuarios_especialidades_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "usuarios_especialidades"
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela = "ws_users_especialidades"
        result = await importar_usuarios_especialidades(banco_dados, tabela, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return result
    except Exception as e:
        logger.error(f"Erro na API /usuarios-especialidades: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

# --- Endpoints para Tipos de Pagamento e Códigos de Faturamento --- 

@router.post("/tipos-pagamento")
async def importar_tipos_pagamento_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "tipos_pagamento" # Nome para controle
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela_mysql = "ws_pagamentos"
        result = await importar_tipos_pagamento(banco_dados, tabela_mysql, connection, supabase)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return json.loads(json.dumps(result, cls=DateUUIDEncoder))
    except Exception as e:
        logger.error(f"Erro na API /tipos-pagamento: {e}", exc_info=True)
        await registrar_controle_importacao(tabela_nome, {"success": False, "message": str(e)}, supabase)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

@router.post("/codigos-faturamento")
async def importar_codigos_faturamento_endpoint(
    banco_dados: str = Query("abalarissa_db"), 
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    connection = None
    tunnel = None
    result = {}
    tabela_nome = "codigos_faturamento" # Nome para controle
    try:
        connection, tunnel = get_mysql_connection(banco_dados)
        tabela_mysql = "ws_pagamentos_x_codigos_faturamento"
        # Pré-requisito: Procedimentos já devem ter sido importados e ter codigo_faturamento_id_origem
        # Idealmente, garantir que a importação de procedimentos esteja completa antes de chamar isso.
        result = await importar_codigos_faturamento(banco_dados, tabela_mysql, connection, supabase)
        # Registrar controle (mesmo que seja apenas atualização)
        await registrar_controle_importacao(tabela_nome, result, supabase)
        return json.loads(json.dumps(result, cls=DateUUIDEncoder))
    except Exception as e:
        logger.error(f"Erro na API /codigos-faturamento: {e}", exc_info=True)
        await registrar_controle_importacao(tabela_nome, {"success": False, "message": str(e)}, supabase)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_connection_and_tunnel(connection, tunnel)

# --- Endpoint Original para Importar Tudo (Modificado para registrar controle) --- 
@router.post("/importar-tudo-sistema-aba")
async def importar_tudo_sistema_aba(
    banco_dados: str = Query("abalarissa_db"),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    resultados = {}
    connection = None
    tunnel = None
    success = False
    message = "Falha na importação geral."
    try:
        logger.info(f"Iniciando importação completa do sistema Aba (banco: {banco_dados})")
        connection, tunnel = get_mysql_connection(banco_dados)
        
        import_steps = [
            ("profissoes", importar_profissoes, {"banco_dados": banco_dados, "tabela": "ws_profissoes"}),
            ("especialidades", importar_especialidades, {"banco_dados": banco_dados, "tabela": "ws_especialidades"}),
            ("locais", importar_locais, {"banco_dados": banco_dados, "tabela": "ps_locales"}),
            ("salas", importar_salas, {"banco_dados": banco_dados, "tabela": "ps_care_rooms"}),
            ("usuarios_aba", importar_usuarios_aba, {"banco_dados": banco_dados, "tabela": "ws_users"}),
            # Adicionar importação de tipos de pagamento antes das relações
            ("tipos_pagamento", importar_tipos_pagamento, {"banco_dados": banco_dados, "tabela": "ws_pagamentos"}),
            # Adicionar atualização de códigos de faturamento (idealmente após procedimentos terem ID de origem)
            ("codigos_faturamento", importar_codigos_faturamento, {"banco_dados": banco_dados, "tabela": "ws_pagamentos_x_codigos_faturamento"}),
            ("usuarios_profissoes", importar_usuarios_profissoes, {"banco_dados": banco_dados, "tabela": "ws_users_profissoes"}),
            ("usuarios_especialidades", importar_usuarios_especialidades, {"banco_dados": banco_dados, "tabela": "ws_users_especialidades"}),
        ]

        for name, func, params in import_steps:
            logger.info(f"--- Iniciando importação: {name} ---")
            step_result = {}
            try:
                step_result = await func(**params, connection=connection, supabase=supabase)
                resultados[name] = step_result
                await registrar_controle_importacao(name, step_result, supabase) # Registra controle após cada passo
                if not step_result.get("success", False):
                    logger.warning(f"Importação de {name} falhou parcialmente ou totalmente: {step_result.get('message')}")
                logger.info(f"--- Concluída importação: {name} ---")
            except Exception as step_e:
                logger.error(f"Erro crítico na etapa de importação '{name}': {step_e}", exc_info=True)
                step_result = {"success": False, "message": f"Erro crítico: {str(step_e)}"}
                resultados[name] = step_result
                await registrar_controle_importacao(name, step_result, supabase) # Registra falha no controle
                # Decide se quer parar ou continuar em caso de erro
                # raise Exception(f"Erro crítico na etapa {name}: {step_e}") # Descomente para parar
                continue # Comentado: continua para o próximo passo mesmo com erro

        # Verifica se todos os passos foram bem-sucedidos
        all_success = all(res.get("success", False) for res in resultados.values())
        if all_success:
            success = True
            message = "Importação completa concluída com sucesso."
        else:
            success = False
            message = "Importação completa concluída com uma ou mais falhas."

    except Exception as e:
        logger.error(f"Erro GERAL durante a importação completa: {e}", exc_info=True)
        success = False
        message = f"Erro GERAL durante a importação: {str(e)}"

    finally:
        logger.info("Fechando conexão MySQL e túnel SSH...")
        close_connection_and_tunnel(connection, tunnel)
        
    return {
        "success": success,
        "message": message,
        "resultados": resultados
    }

# --- Endpoint GET para buscar controle ---
@router.get("/controle-importacao")
async def obter_controle_importacao(
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """Obtém todos os registros da tabela de controle de importação."""
    try:
        result = supabase.table("controle_importacao_tabelas_auxiliares").select("*").order("nome_tabela").execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        logger.error(f"Erro ao obter controle de importação: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# NOVO ENDPOINT PARA CORRIGIR AGENDAMENTOS IMPORTADOS SEM PACIENTE
@router.get(
    "/corrigir-agendamentos-importados", # A rota relativa ao prefixo /api/importacao
    summary="Corrigir Agendamentos Importados Sem Paciente",
    description="Busca agendamentos importados sem paciente_id e tenta vinculá-los usando o id_origem do paciente.",
    tags=["Importação"] # Mantém a tag
)
async def corrigir_agendamentos_importados(
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    logger.info("Iniciando processo de correção de agendamentos sem paciente vinculado.")
    agendamentos_atualizados = 0
    agendamentos_verificados = 0
    erros_busca_paciente = []

    try:
        # 1. Buscar agendamentos importados sem paciente_id
        response_orfãos = supabase.table("agendamentos") \
            .select("id, id_origem, schedule_pacient_id, paciente_id") \
            .eq("importado", True) \
            .is_("paciente_id", None) \
            .execute()
        
        agendamentos_orfãos = response_orfãos.data
        agendamentos_sem_paciente_antes = len(agendamentos_orfãos)
        logger.info(f"Encontrados {agendamentos_sem_paciente_antes} agendamentos importados sem paciente_id.")

        if not agendamentos_orfãos:
            return {
                "status": "success",
                "agendamentos_sem_paciente_antes": 0,
                "agendamentos_atualizados": 0,
                "agendamentos_sem_paciente_depois": 0,
                "message": "Nenhum agendamento importado sem vínculo de paciente encontrado para corrigir."
            }

        # 2. Buscar todos os pacientes importados e criar um mapa id_origem -> id (UUID)
        response_pacientes = supabase.table("pacientes") \
            .select("id, id_origem") \
            .eq("importado", True) \
            .execute()
        
        paciente_map = {}
        for p in response_pacientes.data:
            if p.get("id_origem"):
                paciente_map[str(p["id_origem"])] = p["id"]
        
        logger.info(f"Criado mapa com {len(paciente_map)} pacientes importados.")

        # 3. Iterar sobre os agendamentos órfãos e tentar encontrar o paciente
        updates_to_perform = [] # Lista para acumular atualizações
        for agendamento in agendamentos_orfãos:
            agendamentos_verificados += 1
            id_agendamento_supabase = agendamento.get("id")
            # Precisamos garantir que temos o ID do paciente legado do agendamento
            # Vamos assumir que ele está no campo id_origem do agendamento se não tiver sido mapeado antes?
            # Ou usamos um campo específico como schedule_pacient_id se ele existir na tabela agendamentos?
            # Vou usar schedule_pacient_id conforme código anterior.
            id_paciente_legado = agendamento.get("schedule_pacient_id") 
            
            if not id_paciente_legado:
                logger.warning(f"Agendamento {id_agendamento_supabase} não possui ID de paciente legado (schedule_pacient_id). Impossível vincular.")
                continue
            
            # Tentar encontrar o UUID do paciente no mapa
            paciente_uuid_encontrado = paciente_map.get(str(id_paciente_legado))
            
            if paciente_uuid_encontrado:
                updates_to_perform.append({
                    "id": id_agendamento_supabase,
                    "paciente_id": paciente_uuid_encontrado
                })
                logger.info(f"Paciente encontrado para agendamento {id_agendamento_supabase} (ID legado: {id_paciente_legado}). Preparando para vincular com UUID: {paciente_uuid_encontrado}")
            else:
                logger.warning(f"Paciente com id_origem {id_paciente_legado} não encontrado no mapa para agendamento {id_agendamento_supabase}.")
        
        # 4. Executar atualizações em lote, se houver
        if updates_to_perform:
            logger.info(f"Tentando atualizar {len(updates_to_perform)} agendamentos...")
            try:
                # Iterar e atualizar individualmente
                for update_data in updates_to_perform:
                     update_response = supabase.table("agendamentos") \
                        .update({"paciente_id": update_data["paciente_id"]}) \
                        .eq("id", update_data["id"]) \
                        .execute()
                     
                     if hasattr(update_response, 'error') and update_response.error is not None:
                         error_msg = f"Erro ao atualizar agendamento {update_data['id']}: {update_response.error}"
                         logger.error(error_msg)
                         erros_busca_paciente.append(error_msg)
                     else:
                         agendamentos_atualizados += 1
                
                logger.info(f"{agendamentos_atualizados} agendamentos atualizados com sucesso (de {len(updates_to_perform)} tentativas).")

            except Exception as batch_update_e:
                error_msg = f"Erro durante a atualização dos agendamentos: {str(batch_update_e)}"
                logger.exception(error_msg)
                erros_busca_paciente.append(f"Erro geral durante atualização: {str(batch_update_e)}")
        
        # Cálculo final e mensagem
        agendamentos_sem_paciente_depois = agendamentos_sem_paciente_antes - agendamentos_atualizados
        message = f"Correção concluída. {agendamentos_atualizados} agendamentos foram vinculados a pacientes. {agendamentos_sem_paciente_depois} agendamentos permanecem sem vínculo."
        if erros_busca_paciente:
            message += f" Ocorreram {len(erros_busca_paciente)} erros durante a atualização (ver logs)."
        
        logger.info(message)
        return {
            "status": "success",
            "agendamentos_sem_paciente_antes": agendamentos_sem_paciente_antes,
            "agendamentos_atualizados": agendamentos_atualizados,
            "agendamentos_sem_paciente_depois": agendamentos_sem_paciente_depois,
            "message": message
        }

    except Exception as e:
        logger.exception(f"Erro geral no processo de correção de agendamentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao corrigir agendamentos: {str(e)}"
        )
# FIM NOVO ENDPOINT

def mapear_tipo_pagamento(item, usuario_id):
    """Mapeia os dados de um tipo de pagamento do MySQL para o formato Supabase."""
    # Garante que id_origem seja string
    id_origem = str(item.get('id')) if item.get('id') is not None else None

    mapped_data = {
        'id_origem': id_origem,
        'nome': item.get('pagamento_name'),  # <-- CORRIGIDO AQUI
        'carteirinha_obrigatoria': item.get('pagamento_carteirinha_obrigatoria') == 1, #MySQL usa 1 para true?
        'ativo': item.get('pagamento_status') == 1, # MySQL usa 1 para ativo?
        'created_by': usuario_id,
        'updated_by': usuario_id,
        'importado': True,
        # Adicione outros mapeamentos se necessário
    }
    
    # Remove chaves com valor None para evitar problemas no Supabase
    return {k: v for k, v in mapped_data.items() if v is not None}