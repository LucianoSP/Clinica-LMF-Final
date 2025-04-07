import json
import os
import uuid
import datetime
import logging
import asyncio # Adicionar import asyncio
from typing import Dict, List, Any, Optional
from uuid import UUID
import pymysql
import sshtunnel
from fastapi import APIRouter, HTTPException, Query, Path, status, Depends
from pydantic import BaseModel
from pymysql.cursors import DictCursor
from dateutil import parser

from ..config.config import Settings
from ..utils.date_utils import DateEncoder, format_date_fields, DATE_FIELDS, ensure_serializable, format_time
from ..utils.agendamento_utils import limpar_campos_invalidos, adicionar_dados_relacionados
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do .env

# Definir as configurações de SSH e MySQL para a importação
# Configurações SSH (CORRIGIDO - usa variáveis SSH_*)
ssh_port_str = os.getenv('SSH_PORT') # Usar SSH_PORT
ssh_port = int(ssh_port_str) if ssh_port_str and ssh_port_str.isdigit() else 22 # Converte para int, padrão 22
SSH_CONFIG = {
    'host': os.getenv('SSH_HOST'), # Usar SSH_HOST
    'user': os.getenv('SSH_USER'), # Usar SSH_USER
    'password': os.getenv('SSH_PASSWORD'), # Usar SSH_PASSWORD
    'port': ssh_port # Usa a porta SSH convertida para inteiro
}

# Configurações de conexão MySQL (usado para remote_bind_address e conexão final)
# Assegurar que a porta MySQL seja lida como inteiro
mysql_port_str = os.getenv('MYSQL_PORT')
mysql_port = int(mysql_port_str) if mysql_port_str and mysql_port_str.isdigit() else 3306
MYSQL_CONFIG = {
    'remote_host': os.getenv('MYSQL_HOST', '127.0.0.1'), # Host MySQL no servidor remoto
    'remote_port': mysql_port, # Porta MySQL no servidor remoto (convertida)
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

router = APIRouter(tags=["Agendamentos"])

# Configurar logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def testar_conexao_mysql(database):
    """Testa a conexão com o banco de dados MySQL via túnel SSH."""
    tunnel = None
    try:
        # Configuração MySQL para conexão *final* (via túnel)
        config_final = {
            'host': '127.0.0.1', # Conecta ao túnel local
            'port': 3307,        # Porta local do túnel
            'user': MYSQL_CONFIG['user'],
            'password': MYSQL_CONFIG['password'],
            'database': database,
            'charset': MYSQL_CONFIG['charset'],
            'cursorclass': MYSQL_CONFIG['cursorclass']
        }

        logger.info(f"Abrindo túnel SSH para {SSH_CONFIG['host']}:{SSH_CONFIG['port']}...")
        try:
            # Criar túnel SSH (CORRIGIDO - usa remote_bind_address do MYSQL_CONFIG)
            tunnel = sshtunnel.SSHTunnelForwarder(
                (SSH_CONFIG['host'], SSH_CONFIG['port']),
                ssh_username=SSH_CONFIG['user'],
                ssh_password=SSH_CONFIG['password'],
                remote_bind_address=(MYSQL_CONFIG['remote_host'], MYSQL_CONFIG['remote_port']), # Usa host/porta MySQL remotos
                local_bind_address=('127.0.0.1', 3307)
            )
            tunnel.start()
            logger.info("Túnel SSH estabelecido com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao abrir túnel SSH: {str(e)}")
            return False, f"Erro ao abrir túnel SSH: {str(e)}"

        # Conectar ao MySQL através do túnel (usando config_final)
        logger.info(f"Conectando ao MySQL em {config_final['host']}:{config_final['port']} (banco: {database})...")
        try:
            conexao = pymysql.connect(**config_final)
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


async def buscar_agendamentos_mysql(database, tabela, limite=None, ultima_data_registro=None, ultima_data_atualizacao=None, periodo_semanas=None):
    """
    Busca agendamentos no banco de dados MySQL, incluindo o ID do profissional.
    
    Args:
        database: Nome do banco de dados MySQL
        tabela: Nome da tabela de agendamentos no MySQL
        limite: Limite de registros a serem retornados
        ultima_data_registro: Data de registro da última importação
        ultima_data_atualizacao: Data de atualização da última importação
        periodo_semanas: Número de semanas para filtrar agendamentos (opcional)
        
    Returns:
        list: Lista de agendamentos encontrados
    """
    tunnel = None
    try:
        # Configuração MySQL para conexão *final* (via túnel)
        config_final = {
            'host': '127.0.0.1',
            'port': 3307,
            'user': MYSQL_CONFIG['user'],
            'password': MYSQL_CONFIG['password'],
            'database': database,
            'charset': MYSQL_CONFIG['charset'],
            'cursorclass': MYSQL_CONFIG['cursorclass']
        }

        logger.info(f"Abrindo túnel SSH para {SSH_CONFIG['host']}:{SSH_CONFIG['port']}...")
        # Criar túnel SSH (CORRIGIDO - usa remote_bind_address do MYSQL_CONFIG)
        tunnel = sshtunnel.SSHTunnelForwarder(
            (SSH_CONFIG['host'], SSH_CONFIG['port']),
            ssh_username=SSH_CONFIG['user'],
            ssh_password=SSH_CONFIG['password'],
            remote_bind_address=(MYSQL_CONFIG['remote_host'], MYSQL_CONFIG['remote_port']), # Usa host/porta MySQL remotos
            local_bind_address=('127.0.0.1', 3307)
        )
        tunnel.start()

        # Conectar ao MySQL (usando config_final)
        conexao = pymysql.connect(**config_final)
        
        # Construir a consulta SQL com JOIN
        sql = f"""SELECT s.*, sp.professional_id 
                 FROM {tabela} s 
                 LEFT JOIN ps_schedule_professionals sp ON s.schedule_id = sp.schedule_id 
                 WHERE 1=1"""
        params = []
        
        # Filtrar por período em semanas se fornecido
        if periodo_semanas:
            sql += f" AND s.schedule_date_start >= DATE_SUB(NOW(), INTERVAL %s WEEK)" # Alias s.
            params.append(periodo_semanas)
            logger.info(f"Filtrando agendamentos das últimas {periodo_semanas} semanas")
        
        # Filtrar por datas se fornecidas (usando alias s.)
        if ultima_data_registro or ultima_data_atualizacao:
            registro_campo = "s.schedule_registration_date"
            atualizacao_campo = "s.schedule_lastupdate"
            
            sql += " AND (" # Iniciar grupo OR
            first_condition = True
            if ultima_data_registro:
                sql += f" IFNULL({registro_campo}, '1900-01-01') > %s"
                params.append(ultima_data_registro)
                first_condition = False
                
            if ultima_data_atualizacao:
                if not first_condition:
                    sql += " OR"
                sql += f" IFNULL({atualizacao_campo}, '1900-01-01') > %s"
                params.append(ultima_data_atualizacao)
            sql += ")" # Fechar grupo OR

        # Ordenar por data de agendamento (usando alias s.)
        sql += " ORDER BY s.schedule_date_start DESC"
        
        # Adicionar limite se fornecido
        if limite:
            sql += " LIMIT %s"
            params.append(int(limite))
        
        # Executar a consulta
        with conexao.cursor() as cursor:
            cursor.execute(sql, params)
            agendamentos = cursor.fetchall()
            
            logger.info(f"Encontrados {len(agendamentos)} agendamentos para importação")
            return agendamentos
    
    except Exception as e:
        logger.error(f"Erro ao buscar agendamentos no MySQL: {str(e)}")
        raise
    
    finally:
        # Fechar conexão e túnel
        if 'conexao' in locals() and conexao:
            conexao.close()
        if tunnel and tunnel.is_active:
            tunnel.close()

async def buscar_agendamentos_mysql_desde_data(database, tabela, data_inicial, data_final=None):
    """
    Busca agendamentos do MySQL a partir de uma data específica até uma data final, incluindo ID do profissional.
    
    Parâmetros:
    - database: Nome do banco de dados MySQL
    - tabela: Nome da tabela de agendamentos
    - data_inicial: Data inicial para buscar agendamentos (formato YYYY-MM-DD)
    - data_final: Data final para buscar agendamentos (formato YYYY-MM-DD)
    """
    tunnel = None
    try:
        # Configuração MySQL para conexão *final* (via túnel)
        config_final = {
             'host': '127.0.0.1',
             'port': 3307,
             'user': MYSQL_CONFIG['user'],
             'password': MYSQL_CONFIG['password'],
             'database': database,
             'charset': MYSQL_CONFIG['charset'],
             'cursorclass': MYSQL_CONFIG['cursorclass']
         }

        logger.info(f"Abrindo túnel SSH para {SSH_CONFIG['host']}:{SSH_CONFIG['port']}...")
        # Criar túnel SSH (CORRIGIDO - usa remote_bind_address do MYSQL_CONFIG)
        tunnel = sshtunnel.SSHTunnelForwarder(
            (SSH_CONFIG['host'], SSH_CONFIG['port']),
            ssh_username=SSH_CONFIG['user'],
            ssh_password=SSH_CONFIG['password'],
            remote_bind_address=(MYSQL_CONFIG['remote_host'], MYSQL_CONFIG['remote_port']), # Usa host/porta MySQL remotos
            local_bind_address=('127.0.0.1', 3307)
        )
        tunnel.start()

        # Conectar ao MySQL (usando config_final)
        conexao = pymysql.connect(**config_final)
        
        # Construir a consulta SQL com JOIN
        sql = f"""SELECT s.*, sp.professional_id 
                 FROM {tabela} s 
                 LEFT JOIN ps_schedule_professionals sp ON s.schedule_id = sp.schedule_id 
                 WHERE s.schedule_date_start >= %s""" # Alias s.
        params = [data_inicial]

        if data_final:
             sql += " AND s.schedule_date_start <= %s" # Alias s.
             params.append(data_final)
        
        sql += " ORDER BY s.schedule_date_start ASC" # Alias s.
        
        # Log completo da consulta para debug
        logger.debug(f"Consulta SQL: {sql} - Parâmetros: {params}")
        
        # Executar a consulta
        with conexao.cursor() as cursor:
            cursor.execute(sql, params)
            resultado = cursor.fetchall()
            
        logger.info(f"Encontrados {len(resultado)} agendamentos para importação de {data_inicial} até {data_final if data_final else 'hoje'}")
        
        return resultado
    
    except Exception as e:
        logger.error(f"Erro ao buscar agendamentos do MySQL: {str(e)}")
        return []
    
    finally:
        # Fechar conexão e túnel
        if 'conexao' in locals() and conexao:
            conexao.close()
        if tunnel and tunnel.is_active:
            tunnel.close()

# Função auxiliar para dividir uma lista em lotes
def chunks(lst, n):
    """Divide a lista em lotes de tamanho n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def mapear_agendamento(agendamento_mysql, usuario_id, supabase_client=None):
    """Mapeia os dados de um agendamento MySQL para o formato do Supabase."""
    
    # Funções auxiliares de conversão
    def converter_para_bool(valor):
        if valor is None:
            return None
        if isinstance(valor, (int, float)):
            return valor != 0
        if isinstance(valor, str):
            return valor.lower() in ('1', 'true', 'sim', 's', 'yes', 'y', 't')
        return bool(valor)
    
    def converter_para_int(valor):
        if valor is None:
            return None
        try:
            return int(float(valor))
        except (ValueError, TypeError):
            return None
    
    def converter_para_float(valor):
        if valor is None:
            return None
        try:
            # Converter para string primeiro para lidar com casos onde o valor é '10,5'
            valor_str = str(valor).replace(',', '.')
            return float(valor_str)
        except (ValueError, TypeError):
            return None
    
    def eh_uuid_valido(valor):
        """Verifica se o valor é um UUID válido."""
        if valor is None:
            return False
        try:
            # Alguns valores numéricos como '40' não são UUIDs válidos
            if isinstance(valor, (int, float)) or (isinstance(valor, str) and valor.isdigit()):
                return False
            UUID(str(valor))
            return True
        except (ValueError, TypeError, AttributeError):
            return False
    
    def converter_sim_nao_para_boolean(valor):
        return None if valor is None else valor.lower() == 's'
    
    def converter_data(valor, campo_nome):
        """Converte para datetime ou retorna None, com logging."""
        if not valor:
            logger.debug(f"Campo '{campo_nome}': Valor de entrada vazio ou None.")
            return None
        try:
            logger.debug(f"Campo '{campo_nome}': Tentando converter valor '{valor}' (Tipo: {type(valor)})")
            if isinstance(valor, (datetime.date, datetime.datetime)):
                logger.debug(f"Campo '{campo_nome}': Valor já é datetime. Retornando diretamente.")
                return valor
            # Tentar parsear a string - esta etapa pode ser o problema
            dt_obj = parser.parse(str(valor))
            logger.debug(f"Campo '{campo_nome}': Valor convertido para datetime: {dt_obj}")
            return dt_obj
        except (ValueError, TypeError, parser.ParserError) as e:
            logger.warning(f"Campo '{campo_nome}': Falha ao converter valor '{valor}'. Erro: {e}. Retornando None.")
            return None

    # Extrair o ID do paciente do agendamento
    paciente_id = None
    id_paciente_origem = agendamento_mysql.get('schedule_pacient_id')
    
    # Tenta mapear o paciente usando diretamente a tabela de pacientes (em vez da tabela de mapeamento)
    if id_paciente_origem and supabase_client:
        try:
            # Limpa o ID para garantir que é um número
            if isinstance(id_paciente_origem, str) and id_paciente_origem.isdigit():
                id_paciente_origem = int(id_paciente_origem)
            
            if isinstance(id_paciente_origem, (int, float)):
                # Buscar paciente pelo campo id_origem diretamente na tabela de pacientes
                response = supabase_client.table("pacientes") \
                    .select("id") \
                    .eq("id_origem", str(id_paciente_origem)) \
                    .execute()
                
                if response.data and len(response.data) > 0:
                    paciente_id = response.data[0]["id"]
                    logger.info(f"Paciente encontrado pelo id_origem: {id_paciente_origem} -> {paciente_id}")
                else:
                    logger.warning(f"ID de paciente não encontrado na tabela de pacientes: {id_paciente_origem}")
        except Exception as e:
            logger.error(f"Erro ao mapear ID do paciente: {str(e)}")
    
    # Tenta encontrar um procedimento adequado (simplificado por enquanto)
    procedimento_id = None
    try:
        if supabase_client:
            # Buscar um procedimento padrão
            response = supabase_client.table("procedimentos") \
                .select("id") \
                .limit(1) \
                .execute()
            
            if response.data and len(response.data) > 0:
                procedimento_id = response.data[0]["id"]
                logger.info(f"Usando procedimento padrão: {procedimento_id}")
    except Exception as e:
        logger.error(f"Erro ao buscar procedimento padrão: {str(e)}")
    
    # --- Mapeamento de Profissional (MySQL INT -> Supabase UUID) ---
    profissional_supabase_id = None
    id_profissional_origem = agendamento_mysql.get('professional_id') # Usar o alias da query com JOIN
    
    if id_profissional_origem and supabase_client:
        try:
            # Tenta converter para INT, pois pode vir como string do DB
            try:
                id_profissional_int = int(id_profissional_origem)
            except (ValueError, TypeError):
                logger.warning(f"ID de profissional da origem não é um inteiro válido: {id_profissional_origem}")
                id_profissional_int = None

            if id_profissional_int is not None:
                # Buscar usuário na tabela usuarios_aba pelo user_id (INT)
                response = supabase_client.table("usuarios_aba") \
                    .select("id") \
                    .eq("user_id", id_profissional_int) \
                    .execute()
                
                if response.data and len(response.data) > 0:
                    profissional_supabase_id = response.data[0]["id"]
                    logger.info(f"Profissional mapeado: {id_profissional_int} -> {profissional_supabase_id}")
                else:
                    logger.warning(f"ID de profissional (user_id) não encontrado na tabela usuarios_aba: {id_profissional_int}")
        except Exception as e:
            logger.error(f"Erro ao mapear ID do profissional: {str(e)}")
    # --- Fim Mapeamento Profissional ---

    # --- Mapeamento de Sala (MySQL INT -> Supabase UUID) ---
    sala_supabase_id = None
    id_sala_origem = converter_para_int(agendamento_mysql.get('schedule_room_id'))
    if id_sala_origem and supabase_client:
        try:
            response = supabase_client.table("salas") \
                .select("id") \
                .eq("room_id", str(id_sala_origem)) \
                .limit(1) \
                .execute()
            if response.data and len(response.data) > 0:
                sala_supabase_id = response.data[0]["id"]
                logger.info(f"Sala mapeada: {id_sala_origem} -> {sala_supabase_id}")
            else:
                logger.warning(f"ID de Sala (room_id) não encontrado na tabela salas: {id_sala_origem}")
        except Exception as e:
            logger.error(f"Erro ao mapear ID da Sala: {str(e)}")
    # --- Fim Mapeamento Sala ---

    # --- Mapeamento de Local (MySQL INT -> Supabase UUID) ---
    local_supabase_id = None
    id_local_origem = converter_para_int(agendamento_mysql.get('schedule_local_id'))
    if id_local_origem and supabase_client:
        try:
            response = supabase_client.table("locais") \
                .select("id") \
                .eq("local_id", str(id_local_origem)) \
                .limit(1) \
                .execute()
            if response.data and len(response.data) > 0:
                local_supabase_id = response.data[0]["id"]
                logger.info(f"Local mapeado: {id_local_origem} -> {local_supabase_id}")
            else:
                logger.warning(f"ID de Local (local_id) não encontrado na tabela locais: {id_local_origem}")
        except Exception as e:
            logger.error(f"Erro ao mapear ID do Local: {str(e)}")
    # --- Fim Mapeamento Local ---

    # --- Mapeamento de Especialidade (MySQL INT -> Supabase UUID) ---
    especialidade_supabase_id = None
    id_especialidade_origem = converter_para_int(agendamento_mysql.get('schedule_especialidade_id'))
    if id_especialidade_origem and supabase_client:
        try:
            response = supabase_client.table("especialidades") \
                .select("id") \
                .eq("especialidade_id", str(id_especialidade_origem)) \
                .limit(1) \
                .execute()
            if response.data and len(response.data) > 0:
                especialidade_supabase_id = response.data[0]["id"]
                logger.info(f"Especialidade mapeada: {id_especialidade_origem} -> {especialidade_supabase_id}")
            else:
                logger.warning(f"ID de Especialidade (especialidade_id) não encontrado na tabela especialidades: {id_especialidade_origem}")
        except Exception as e:
            logger.error(f"Erro ao mapear ID da Especialidade: {str(e)}")
    # --- Fim Mapeamento Especialidade ---

    # Mapear o pagamento (nome descritivo)
    pagamento = None
    pagamento_id = agendamento_mysql.get('schedule_pagamento_id')
    if pagamento_id == "15":
        pagamento = "Plano de Saúde"
    elif pagamento_id == "3":
        pagamento = "Particular"
    
    # Obter valores para os campos do agendamento e logar
    schedule_date_start_raw = agendamento_mysql.get('schedule_date_start')
    data_agendamento = converter_data(schedule_date_start_raw, 'schedule_date_start')
    # Convertido para ISO para 'data_agendamento' e agora também para 'schedule_date_start'
    data_agendamento_iso = data_agendamento.isoformat() if data_agendamento else None
    logger.debug(f"schedule_date_start: Raw='{schedule_date_start_raw}', Convertido='{data_agendamento}', ISO='{data_agendamento_iso}'")

    schedule_date_end_raw = agendamento_mysql.get('schedule_date_end')
    data_fim_obj = converter_data(schedule_date_end_raw, 'schedule_date_end')
    # Convertido para ISO para 'schedule_date_end'
    data_fim_iso = data_fim_obj.isoformat() if data_fim_obj else None
    logger.debug(f"schedule_date_end: Raw='{schedule_date_end_raw}', Convertido='{data_fim_obj}', ISO='{data_fim_iso}'")

    schedule_registration_date_raw = agendamento_mysql.get('schedule_registration_date')
    schedule_registration_date = converter_data(schedule_registration_date_raw, 'schedule_registration_date')
    schedule_registration_date_iso = schedule_registration_date.isoformat() if schedule_registration_date else None
    logger.debug(f"schedule_registration_date: Raw='{schedule_registration_date_raw}', Convertido='{schedule_registration_date}', ISO='{schedule_registration_date_iso}'")

    schedule_lastupdate_raw = agendamento_mysql.get('schedule_lastupdate')
    schedule_lastupdate = converter_data(schedule_lastupdate_raw, 'schedule_lastupdate')
    schedule_lastupdate_iso = schedule_lastupdate.isoformat() if schedule_lastupdate else None
    logger.debug(f"schedule_lastupdate: Raw='{schedule_lastupdate_raw}', Convertido='{schedule_lastupdate}', ISO='{schedule_lastupdate_iso}'")

    # Processar hora_inicio (usa 'data_agendamento' convertido)
    hora_inicio = None
    if data_agendamento:
        try:
            hora_inicio = format_time(data_agendamento)
        except Exception as e:
            logger.error(f"Erro ao extrair hora_inicio de '{data_agendamento}': {str(e)}")
            hora_inicio = None
    logger.debug(f"hora_inicio: Calculado='{hora_inicio}'")

    # Processar hora_fim (usa 'data_fim_obj' convertido)
    hora_fim = None
    if data_fim_obj:
        try:
            hora_fim = format_time(data_fim_obj)
        except Exception as e:
            logger.error(f"Erro ao extrair hora_fim de '{data_fim_obj}': {str(e)}")
            hora_fim = None
    logger.debug(f"hora_fim: Calculado='{hora_fim}'")

    # Mapear o status (mais descritivo)
    status_map = {
        "0": "Agendado",
        "1": "Confirmado",
        "9": "Cancelado"
    }
    status_original = agendamento_mysql.get('schedule_status')
    status = status_map.get(str(status_original), status_original)
    
    # --- IDs Relacionais (obter e validar/atribuir) ---
    # Store original MySQL Parent ID (INT) - Assuming this is correct structure
    schedule_parent_id = converter_para_int(agendamento_mysql.get('schedule_parent_id'))
    
    # O ID do profissional mapeado (UUID) vai para schedule_profissional_id
    schedule_profissional_id = profissional_supabase_id if eh_uuid_valido(profissional_supabase_id) else None 
    # Use the newly mapped Supabase IDs
    sala_id_supabase = sala_supabase_id if eh_uuid_valido(sala_supabase_id) else None 
    local_id_supabase = local_supabase_id if eh_uuid_valido(local_supabase_id) else None 
    especialidade_id_supabase = especialidade_supabase_id if eh_uuid_valido(especialidade_supabase_id) else None 
    # --- Fim IDs Relacionais ---
    
    agendamento = {
        # Campos principais obrigatórios para agendamento
        'paciente_id': paciente_id if eh_uuid_valido(paciente_id) else None,
        'procedimento_id': procedimento_id if eh_uuid_valido(procedimento_id) else None,
        'data_agendamento': data_agendamento_iso,
        'hora_inicio': hora_inicio,
        'hora_fim': hora_fim,
        'status': status,
        'observacoes': agendamento_mysql.get('schedule_observations'), # Verificar se nome da coluna está correto
        
        # IDs Relacionais Supabase (UUIDs)
        'sala_id_supabase': sala_id_supabase,
        'local_id_supabase': local_id_supabase,
        'especialidade_id_supabase': especialidade_id_supabase,
        'schedule_profissional_id': schedule_profissional_id, 

        # Original MySQL Parent ID (INT) - Assuming this is correct structure
        'schedule_parent_id': schedule_parent_id, 

        # Campos de importação e informações adicionais
        'importado': True,
        'id_origem': str(agendamento_mysql.get('schedule_id', '')), # ID Original do agendamento
        'schedule_codigo_faturamento': agendamento_mysql.get('schedule_codigo_faturamento'),
        
        # Campos de data/hora originais do MySQL (convertidos para ISO)
        'schedule_date_start': data_agendamento_iso,
        'schedule_date_end': data_fim_iso,
        'schedule_registration_date': schedule_registration_date_iso,
        'schedule_lastupdate': schedule_lastupdate_iso,
        
        # Campos de auditoria
        'created_by': usuario_id if eh_uuid_valido(usuario_id) else None,
        'updated_by': usuario_id if eh_uuid_valido(usuario_id) else None
    }

    # Log antes de remover Nones
    logger.debug(f"Dicionário agendamento ANTES de remover None: {agendamento}")

    # Remover valores None para evitar conflitos
    agendamento_limpo = {k: v for k, v in agendamento.items() if v is not None}

    # Fazer log dos campos que estamos enviando para debug
    logger.debug(f"Dicionário agendamento DEPOIS de remover None (enviado ao Supabase): {agendamento_limpo}")

    return agendamento_limpo

def safe_str(obj):
    """Converte qualquer objeto para string de forma segura."""
    if obj is None:
        return "None"
    return str(obj)


@router.post(
    "/importar",
    summary="Importar Agendamentos do MySQL",
    description="Importa agendamentos de um banco de dados MySQL para o Supabase com controle de datas"
)
async def importar_agendamentos_mysql(
    dados: dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Importa agendamentos do MySQL para o Supabase com controle de datas e pré-processamento.
    
    Parâmetros:
    - database: Nome do banco de dados MySQL
    - tabela: Nome da tabela de agendamentos (default: 'ps_schedule')
    - limite: Limite de registros a importar (default: 50)
    - ultima_data_registro: Data da última importação (formato ISO)
    - ultima_data_atualizacao: Data da última atualização (formato ISO)
    - id_usuario: ID do usuário que está realizando a importação
    - periodo_semanas: Número de semanas para filtrar agendamentos (opcional)
    """
    try:
        # Extrair os parâmetros do corpo da requisição
        database = dados.get("database")
        tabela = dados.get("tabela", "ps_schedule")  # Usar ps_schedule como padrão
        limit = dados.get("limit")
        periodo_semanas = dados.get("periodo_semanas", 4)  # Padrão: 4 semanas
        
        # Extrair o ID do usuário que está executando a importação, se fornecido
        usuario_id = dados.get("usuario_id", "sistema")
        logger.info(f"Importação sendo executada pelo usuário: {usuario_id}")
        
        # Se o usuário for "sistema", vamos verificar se o UUID correspondente existe
        if usuario_id == "sistema":
            db = get_supabase_client()
            sistema_uuid = "00000000-0000-0000-0000-000000000000"
            
            # Verificar se o usuário sistema já existe
            result = db.table("usuarios").select("*").eq("id", sistema_uuid).execute()
            
            if not result.data:
                logger.info("Usuário sistema não encontrado, criando-o agora")
                try:
                    # Criar usuário sistema se não existir
                    db.table("usuarios").insert({
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
            
        # A tabela agora tem um valor padrão, então não precisamos mais verificar se ela é nula
        logger.info(f"Importando agendamentos do banco '{database}', tabela '{tabela}'")
        
        # Buscar a última importação para controle de datas
        # Utilizamos a tabela controle_importacao_agendamentos
        db = get_supabase_client()
        ultima_importacao_result = db.table("controle_importacao_agendamentos") \
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
                },
                "periodo_semanas": periodo_semanas
            }
        
        # Comentado: A tabela mapeamento_ids_pacientes não existe e o mapeamento é feito direto
        # mapeamento_result, mapeamento_msg, qtd_mapeada = await preencher_mapeamento_pacientes(supabase)
        # if not mapeamento_result:
        #     logger.warning(f"Atenção: {mapeamento_msg}")
        # else:
        #     logger.info(f"Mapeamento de pacientes: {mapeamento_msg}")
        
        # Buscar os agendamentos do MySQL
        agendamentos_mysql = await buscar_agendamentos_mysql(
            database, 
            tabela, 
            limit, 
            ultima_data_registro, 
            ultima_data_atualizacao,
            periodo_semanas
        )
        
        if not agendamentos_mysql:
            return {"message": "Nenhum agendamento encontrado para importação", "quantidade": 0}
        
        logger.info(f"Iniciando importação de {len(agendamentos_mysql)} agendamentos")
        
        # Contadores para o relatório
        contador_importados = 0
        contador_atualizados = 0
        contador_erros = 0
        
        # Processar os agendamentos
        for agendamento_mysql in agendamentos_mysql:
            try:
                # Obter o ID de origem do agendamento
                id_origem = str(agendamento_mysql.get('schedule_id', ''))
                
                if not id_origem:
                    logger.warning(f"Agendamento sem ID de origem: {agendamento_mysql}")
                    contador_erros += 1
                    continue
                
                # Verificar se o agendamento já existe no Supabase
                response = supabase.table('agendamentos') \
                    .select('*') \
                    .eq('id_origem', id_origem) \
                    .execute()
                
                agendamento_existente = response.data[0] if response.data else None
                
                # Mapear o agendamento do formato MySQL para o formato Supabase
                agendamento_dados = mapear_agendamento(agendamento_mysql, usuario_id, supabase)
                
                # Serializar objetos datetime antes de qualquer operação
                agendamento_dados = ensure_serializable(agendamento_dados)
                
                if agendamento_existente:
                    # Atualizar o agendamento existente
                    response = supabase.table('agendamentos') \
                        .update(agendamento_dados) \
                        .eq('id', agendamento_existente['id']) \
                        .execute()
                    
                    if response.data:
                        logger.info(f"Agendamento atualizado com sucesso: {id_origem}")
                        contador_atualizados += 1
                    else:
                        logger.error(f"Erro ao atualizar agendamento: {id_origem}")
                        contador_erros += 1
                else:
                    # Criar um novo agendamento
                    response = supabase.table('agendamentos') \
                        .insert(agendamento_dados) \
                        .execute()
                    
                    if response.data:
                        logger.info(f"Agendamento importado com sucesso: {id_origem}")
                        contador_importados += 1
                    else:
                        logger.error(f"Erro ao importar agendamento: {id_origem}")
                        contador_erros += 1
            
            except Exception as e:
                logger.error(f"Erro ao processar agendamento: {str(e)}")
                contador_erros += 1
        
        # Preparar variáveis de data para uso em todo o escopo da função
        # Verificar se as variáveis são objetos datetime ou strings
        if ultima_data_registro:
            data_registro_iso = ultima_data_registro.isoformat() if hasattr(ultima_data_registro, 'isoformat') else ultima_data_registro
        else:
            data_registro_iso = None
            
        if ultima_data_atualizacao:
            data_atualizacao_iso = ultima_data_atualizacao.isoformat() if hasattr(ultima_data_atualizacao, 'isoformat') else ultima_data_atualizacao
        else:
            data_atualizacao_iso = None
        
        # Registrar a importação no controle de importação
        if contador_importados > 0 or contador_atualizados > 0:
            try:
                # Preparar os dados para inserção e garantir formato de data correto
                try:
                    # Formatar as datas em formato ISO
                    data_inicial_iso = data_registro_iso
                    if data_registro_iso and not 'T' in data_registro_iso:
                        # Adicionar a parte da hora se for apenas data (YYYY-MM-DD)
                        data_inicial_iso = f"{data_registro_iso}T00:00:00"
                    
                    data_final_iso = data_atualizacao_iso
                    if data_atualizacao_iso and not 'T' in data_atualizacao_iso:
                        # Adicionar a parte da hora se for apenas data (YYYY-MM-DD)
                        data_final_iso = f"{data_atualizacao_iso}T23:59:59"
                    elif not data_atualizacao_iso:
                        # Se não tiver data final, usar a data atual
                        data_final_iso = datetime.datetime.now().isoformat()
                    
                    import_data = {
                        "ultima_data_registro_importada": data_inicial_iso,
                        "ultima_data_atualizacao_importada": data_final_iso,
                        "quantidade_registros_importados": contador_importados,
                        "quantidade_registros_atualizados": contador_atualizados,
                        "usuario_id": usuario_id,
                        "timestamp_importacao": datetime.datetime.now().isoformat(),
                        "observacoes": f"Importação desde {data_inicial_iso}: {contador_importados} novos, {contador_atualizados} atualizados, {contador_erros} erros"
                    }
                    
                    # Serializar novamente para garantir que não há objetos datetime
                    import_data = json.loads(json.dumps(import_data, cls=DateEncoder))
                except Exception as e:
                    logger.error(f"Erro ao formatar datas para registro de importação: {str(e)}")
                    # Fallback para caso de erro na formatação
                    import_data = {
                        "quantidade_registros_importados": contador_importados,
                        "quantidade_registros_atualizados": contador_atualizados,
                        "usuario_id": usuario_id,
                        "timestamp_importacao": datetime.datetime.now().isoformat(),
                        "observacoes": f"Importação desde {data_registro_iso}: {contador_importados} novos, {contador_atualizados} atualizados, {contador_erros} erros"
                    }
                
                # Inserir na tabela de controle
                logger.info(f"Registrando na tabela controle_importacao_agendamentos: {import_data}")
                db.table("controle_importacao_agendamentos").insert(import_data).execute()
                logger.info("Registro de importação salvo com sucesso")
            except Exception as e:
                logger.error(f"Erro ao registrar importação: {str(e)}")
                # Não deixar falhar a importação só porque o registro falhou
        
        # Resultado da importação
        return {
            "success": True,
            "message": f"Importação concluída. {contador_importados} agendamentos importados das últimas {periodo_semanas} semanas, {contador_atualizados} atualizados com sucesso.",
            "importados": contador_importados,
            "total": len(agendamentos_mysql),
            "total_erros": contador_erros,
            "total_atualizados": contador_atualizados,
            "erros": [],
            "connection_status": {
                "success": True,
                "message": mensagem
            },
            "ultima_data_registro": data_registro_iso if data_registro_iso else None,
            "ultima_data_atualizacao": data_atualizacao_iso if data_atualizacao_iso else None,
            "periodo_semanas": periodo_semanas
        }
        
    except Exception as e:
        logger.error(f"Erro na importação de agendamentos: {str(e)}")
        return {
            "success": False,
            "message": f"Erro na importação de agendamentos: {str(e)}",
            "importados": 0,
            "total": 0,
            "erros": [safe_str(e)],
            "connection_status": {
                "success": False,
                "message": "Erro interno na importação"
            },
            "data_inicial": dados.get("data_inicial"),
            "data_final": dados.get("data_final")
        }

@router.post(
    "/importar-desde-data",
    summary="Importar agendamentos a partir de uma data específica",
    description="Importa agendamentos do MySQL para o Supabase a partir de uma data específica até uma data final"
)
async def importar_agendamentos_desde_data(
    dados: dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Importa agendamentos do MySQL para o Supabase a partir de uma data específica até uma data final.
    
    Parâmetros:
    - database: Nome do banco de dados MySQL
    - tabela: Nome da tabela de agendamentos
    - data_inicial: Data inicial para importar agendamentos (formato YYYY-MM-DD)
    - data_final: Data final para importar agendamentos (formato YYYY-MM-DD)
    """
    tunnel = None
    try:
        # Extrair os parâmetros do corpo da requisição
        database = dados.get("database", "abalarissa_db")  # Valor padrão
        tabela = dados.get("tabela", "ps_schedule")  # Valor padrão
        data_inicial = dados.get("data_inicial")
        data_final = dados.get("data_final")
        
        if not data_inicial:
            return {
                "success": False,
                "message": "Data inicial é obrigatória",
                "importados": 0,
                "total": 0,
                "erros": ["Data inicial não fornecida"],
                "connection_status": {
                    "success": False,
                    "message": "Data inicial não fornecida"
                }
            }
        
        # Extrair o ID do usuário que está executando a importação, se fornecido
        usuario_id = dados.get("usuario_id", "sistema")
        logger.info(f"Importação sendo executada pelo usuário: {usuario_id}")
        
        # Se o usuário for "sistema", vamos verificar se o UUID correspondente existe
        if usuario_id == "sistema":
            db = get_supabase_client()
            sistema_uuid = "00000000-0000-0000-0000-000000000000"
            
            # Verificar se o usuário sistema já existe
            result = db.table("usuarios").select("*").eq("id", sistema_uuid).execute()
            
            if not result.data:
                logger.info("Usuário sistema não encontrado, criando-o agora")
                try:
                    # Criar usuário sistema se não existir
                    db.table("usuarios").insert({
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
                },
                "data_inicial": data_inicial
            }
        
        # Comentado: A tabela mapeamento_ids_pacientes não existe e o mapeamento é feito direto
        # mapeamento_result, mapeamento_msg, qtd_mapeada = await preencher_mapeamento_pacientes(supabase)
        # if not mapeamento_result:
        #     logger.warning(f"Atenção: {mapeamento_msg}")
        # else:
        #     logger.info(f"Mapeamento de pacientes: {mapeamento_msg}")
        
        # Buscar os agendamentos do MySQL desde a data específica
        agendamentos_mysql = await buscar_agendamentos_mysql_desde_data(
            database, 
            tabela, 
            data_inicial,
            data_final
        )
        
        if not agendamentos_mysql:
            return {
                "success": True,
                "message": f"Nenhum agendamento encontrado a partir de {data_inicial}",
                "importados": 0,
                "total": 0,
                "erros": [],
                "connection_status": {
                    "success": True,
                    "message": "Conexão bem-sucedida, mas nenhum agendamento para importar"
                },
                "data_inicial": data_inicial
            }
        
        logger.info(f"Iniciando importação de {len(agendamentos_mysql)} agendamentos a partir de {data_inicial}")
        
        # Contadores para o relatório
        contador_importados = 0
        contador_atualizados = 0
        contador_erros = 0
        erros = []
        
        # Processar os agendamentos
        for agendamento_mysql in agendamentos_mysql:
            try:
                # Obter o ID de origem do agendamento
                id_origem = str(agendamento_mysql.get('schedule_id', ''))
                
                if not id_origem:
                    logger.warning(f"Agendamento sem ID de origem: {agendamento_mysql}")
                    erro = f"Agendamento sem ID de origem"
                    erros.append(erro)
                    contador_erros += 1
                    continue
                
                # Verificar se o agendamento já existe no Supabase
                response = supabase.table('agendamentos') \
                    .select('*') \
                    .eq('id_origem', id_origem) \
                    .execute()
                
                agendamento_existente = response.data[0] if response.data else None
                
                # Mapear o agendamento do formato MySQL para o formato Supabase
                agendamento_dados = mapear_agendamento(agendamento_mysql, usuario_id, supabase)
                
                # Serializar objetos datetime e decimais antes de qualquer operação
                agendamento_dados = ensure_serializable(agendamento_dados)
                
                if agendamento_existente:
                    # Atualizar o agendamento existente
                    response = supabase.table('agendamentos') \
                        .update(agendamento_dados) \
                        .eq('id', agendamento_existente['id']) \
                        .execute()
                    
                    if response.data:
                        logger.info(f"Agendamento atualizado com sucesso: {id_origem}")
                        contador_atualizados += 1
                    else:
                        erro = f"Erro ao atualizar agendamento: {id_origem}"
                        logger.error(erro)
                        erros.append(erro)
                        contador_erros += 1
                else:
                    # Criar um novo agendamento
                    response = supabase.table('agendamentos') \
                        .insert(agendamento_dados) \
                        .execute()
                    
                    if response.data:
                        logger.info(f"Agendamento importado com sucesso: {id_origem}")
                        contador_importados += 1
                    else:
                        erro = f"Erro ao importar agendamento: {id_origem}"
                        logger.error(erro)
                        erros.append(erro)
                        contador_erros += 1
            
            except Exception as e:
                erro = f"Erro ao processar agendamento: {safe_str(e)}"
                logger.error(erro)
                erros.append(erro)
                contador_erros += 1
        
        # Registrar a importação no controle de importação
        if contador_importados > 0 or contador_atualizados > 0:
            try:
                # Preparar os dados para inserção e garantir formato de data correto
                try:
                    # Formatar as datas em formato ISO
                    data_inicial_iso = data_inicial
                    if data_inicial and not 'T' in data_inicial:
                        # Adicionar a parte da hora se for apenas data (YYYY-MM-DD)
                        data_inicial_iso = f"{data_inicial}T00:00:00"
                    
                    data_final_iso = data_final
                    if data_final and not 'T' in data_final:
                        # Adicionar a parte da hora se for apenas data (YYYY-MM-DD)
                        data_final_iso = f"{data_final}T23:59:59"
                    elif not data_final:
                        # Se não tiver data final, usar a data atual
                        data_final_iso = datetime.datetime.now().isoformat()
                    
                    import_data = {
                        "ultima_data_registro_importada": data_inicial_iso,
                        "ultima_data_atualizacao_importada": data_final_iso,
                        "quantidade_registros_importados": contador_importados,
                        "quantidade_registros_atualizados": contador_atualizados,
                        "usuario_id": usuario_id,
                        "timestamp_importacao": datetime.datetime.now().isoformat(),
                        "observacoes": f"Importação desde {data_inicial_iso}: {contador_importados} novos, {contador_atualizados} atualizados, {contador_erros} erros"
                    }
                    
                    # Serializar novamente para garantir que não há objetos datetime
                    import_data = json.loads(json.dumps(import_data, cls=DateEncoder))
                except Exception as e:
                    logger.error(f"Erro ao formatar datas para registro de importação: {str(e)}")
                    # Fallback para caso de erro na formatação
                    import_data = {
                        "quantidade_registros_importados": contador_importados,
                        "quantidade_registros_atualizados": contador_atualizados,
                        "usuario_id": usuario_id,
                        "timestamp_importacao": datetime.datetime.now().isoformat(),
                        "observacoes": f"Importação desde {data_inicial}: {contador_importados} novos, {contador_atualizados} atualizados, {contador_erros} erros"
                    }
                
                # Inserir na tabela de controle
                logger.info(f"Registrando na tabela controle_importacao_agendamentos: {import_data}")
                db.table("controle_importacao_agendamentos").insert(import_data).execute()
                logger.info("Registro de importação salvo com sucesso")
            except Exception as e:
                logger.error(f"Erro ao registrar importação: {str(e)}")
                # Não deixar falhar a importação só porque o registro falhou
        
        # Limitar número de erros retornados
        if len(erros) > 10:
            erros = erros[:10] + [f"... e mais {len(erros) - 10} erros (veja os logs para detalhes)"]
        
        # Resultado da importação
        return {
            "success": True,
            "message": f"Importação concluída. {contador_importados} novos agendamentos importados a partir de {data_inicial}, {contador_atualizados} atualizados.",
            "importados": contador_importados + contador_atualizados,
            "total": len(agendamentos_mysql),
            "total_erros": contador_erros,
            "total_atualizados": contador_atualizados,
            "erros": erros,
            "connection_status": {
                "success": True,
                "message": mensagem
            },
            "data_inicial": data_inicial,
            "data_final": data_final
        }
        
    except Exception as e:
        logger.error(f"Erro na importação de agendamentos: {str(e)}")
        return {
            "success": False,
            "message": f"Erro na importação de agendamentos: {str(e)}",
            "importados": 0,
            "total": 0,
            "erros": [safe_str(e)],
            "connection_status": {
                "success": False,
                "message": "Erro interno na importação"
            },
            "data_inicial": dados.get("data_inicial"),
            "data_final": dados.get("data_final")
        }

@router.post(
    "/verificar-quantidade",
    summary="Verificar quantidade de agendamentos disponíveis para importação",
    description="Retorna a quantidade de agendamentos disponíveis para importação a partir de uma data específica"
)
async def verificar_quantidade_agendamentos(
    dados: dict,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Verifica a quantidade de agendamentos disponíveis para importação sem realizar a importação.
    
    Parâmetros:
    - database: Nome do banco de dados MySQL
    - tabela: Nome da tabela de agendamentos
    - data_inicial: Data inicial para verificar agendamentos (formato YYYY-MM-DD)
    """
    tunnel = None
    try:
        # Extrair os parâmetros do corpo da requisição
        database = dados.get("database", "abalarissa_db")  # Valor padrão
        tabela = dados.get("tabela", "ps_schedule")  # Valor padrão
        data_inicial = dados.get("data_inicial")
        
        if not data_inicial:
            return {
                "success": False,
                "message": "Data inicial é obrigatória",
                "quantidade": 0
            }
        
        # Verificar conexão com MySQL
        sucesso, mensagem = await testar_conexao_mysql(database)
        if not sucesso:
            return {
                "success": False,
                "message": f"Erro na conexão com MySQL: {mensagem}",
                "quantidade": 0
            }
        
        # Formatação correta da data para o formato MySQL (YYYY-MM-DD HH:MM:SS)
        data_formatada = None
        if data_inicial:
            try:
                # Se uma data ISO for fornecida, converter para o formato MySQL
                if 'T' in data_inicial:
                    dt_obj = parser.parse(data_inicial)
                    data_formatada = dt_obj.strftime('%Y-%m-%d 00:00:00')
                else:
                    # Se for apenas uma data (sem hora), adicione 00:00:00
                    data_formatada = f"{data_inicial} 00:00:00"
                    
                logger.info(f"Data formatada para consulta MySQL: {data_formatada}")
            except Exception as e:
                logger.error(f"Erro ao formatar data: {str(e)}")
                data_formatada = data_inicial
        
        # Configuração MySQL para conexão *final* (via túnel)
        config_final = {
            'host': '127.0.0.1',
            'port': 3307,
            'user': MYSQL_CONFIG['user'],
            'password': MYSQL_CONFIG['password'],
            'database': database, # 'database' foi extraído dos 'dados'
            'charset': MYSQL_CONFIG['charset'],
            'cursorclass': MYSQL_CONFIG['cursorclass']
        }

        logger.info(f"Abrindo túnel SSH para {SSH_CONFIG['host']}:{SSH_CONFIG['port']}...")
        # Criar túnel SSH (CORRIGIDO - usa remote_bind_address do MYSQL_CONFIG)
        tunnel = sshtunnel.SSHTunnelForwarder(
            (SSH_CONFIG['host'], SSH_CONFIG['port']),
            ssh_username=SSH_CONFIG['user'],
            ssh_password=SSH_CONFIG['password'],
            remote_bind_address=(MYSQL_CONFIG['remote_host'], MYSQL_CONFIG['remote_port']), # Usa host/porta MySQL remotos
            local_bind_address=('127.0.0.1', 3307)
        )
        tunnel.start()

        # Conectar ao MySQL (usando config_final)
        conexao = pymysql.connect(**config_final)
        
        # Construir a consulta SQL para contar
        sql = f"SELECT COUNT(*) as total FROM {tabela} WHERE schedule_date_start >= %s"
        params = [data_formatada]
        
        # Adicionar limite de data final se fornecido
        data_final = dados.get("data_final")
        if data_final:
            try:
                # Formatar a data final
                if 'T' in data_final:
                    dt_obj = parser.parse(data_final)
                    data_final_formatada = dt_obj.strftime('%Y-%m-%d 23:59:59')
                else:
                    # Se for apenas uma data (sem hora), adicione 23:59:59
                    data_final_formatada = f"{data_final} 23:59:59"
                
                sql += " AND schedule_date_start <= %s"
                params.append(data_final_formatada)
                logger.info(f"Usando data final fornecida: {data_final_formatada}")
            except Exception as e:
                logger.error(f"Erro ao formatar data final: {str(e)}")
                # Usar o limite padrão de 7 dias se houver erro
                data_limite = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d 23:59:59')
                sql += " AND schedule_date_start <= %s"
                params.append(data_limite)
                logger.info(f"Usando data limite padrão: {data_limite}")
        else:
            # Usar o limite padrão de 7 dias se não for fornecido
            data_limite = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime('%Y-%m-%d 23:59:59')
            sql += " AND schedule_date_start <= %s"
            params.append(data_limite)
            logger.info(f"Usando data limite padrão: {data_limite}")
        
        # Log completo da consulta para debug
        logger.debug(f"Consulta SQL para contagem: {sql} - Parâmetros: {params}")
        
        # Executar a consulta de contagem
        with conexao.cursor() as cursor:
            cursor.execute(sql, params)
            resultado = cursor.fetchone()
            quantidade = resultado['total'] if resultado and 'total' in resultado else 0
            
        logger.info(f"Encontrados {quantidade} agendamentos para importação a partir de {data_formatada}")
        
        return {
            "success": True,
            "message": f"Encontrados {quantidade} agendamentos a partir de {data_inicial}",
            "quantidade": quantidade,
            "data_inicial": data_inicial
        }
    
    except Exception as e:
        logger.error(f"Erro ao verificar quantidade de agendamentos: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao verificar quantidade de agendamentos: {str(e)}",
            "quantidade": 0
        }
    
    finally:
        # Fechar conexão e túnel
        if 'conexao' in locals() and conexao:
            conexao.close()
        if tunnel and tunnel.is_active:
            tunnel.close()

# Definir modelo para agendamento
class AgendamentoBase(BaseModel):
    paciente_id: str
    procedimento_id: str
    data_agendamento: str
    hora_inicio: str
    hora_fim: str
    status: str
    observacoes: Optional[str] = None

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoUpdate(BaseModel):
    paciente_id: Optional[str] = None
    procedimento_id: Optional[str] = None
    data_agendamento: Optional[str] = None
    hora_inicio: Optional[str] = None
    hora_fim: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class Agendamento(AgendamentoBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    paciente_nome: Optional[str] = None
    procedimento_nome: Optional[str] = None

# Colunas válidas para ordenação direta no Supabase (colunas da tabela agendamentos)
VALID_DB_ORDER_COLUMNS = {
    "id", "created_at", "updated_at", "paciente_id", "procedimento_id",
    "data_agendamento", "hora_inicio", "hora_fim", "status", "observacoes",
    "sala_id_supabase", "local_id_supabase", "schedule_profissional_id",
    "especialidade_id_supabase", "importado", "id_origem",
    "schedule_codigo_faturamento", "schedule_date_start", "schedule_date_end",
    "schedule_registration_date", "schedule_lastupdate", "created_by", "updated_by"
    # Adicione outras colunas diretas se houver
}

# Mapeamento de nomes de coluna do frontend/API para nomes de campo no dict `item` pós-processado
# Ajuste conforme necessário com base nos nomes usados em adicionar_dados_relacionados
COLUMN_MAPPING = {
    "profissional": "profissional_nome",
    "paciente": "paciente_nome",
    "procedimento": "procedimento_nome",
    "sala": "sala_nome",
    "local": "local_nome",
    "especialidade": "especialidade_nome",
    "profissao": "profissao" # Adicionado mapeamento para profissão
    # Adicionar outros mapeamentos se o nome da coluna na API for diferente da chave no dict final
}


@router.get(
    "",
    summary="Listar agendamentos",
    description="Retorna uma lista paginada de agendamentos com opções de filtro e ordenação, incluindo status de vinculação."
)
async def listar_agendamentos(
    offset: int = Query(0, description="Número de registros para pular (paginação)"),
    limit: int = Query(10, description="Número máximo de registros para retornar"),
    search: Optional[str] = Query(None, description="Termo de busca para filtrar agendamentos (nome paciente, procedimento, status)"),
    status_vinculacao: Optional[str] = Query(None, description="Filtrar por status de vinculação específico (Pendente, Ficha OK, Unimed OK, Completo)"), 
    order_column: str = Query("data_agendamento", description="Coluna para ordenação"),
    order_direction: str = Query("desc", description="Direção da ordenação (asc ou desc)"),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    """
    Lista agendamentos usando a função func_listar_agendamentos_view via RPC.
    """
    try:
        logger.info(f"Listando agendamentos via RPC: offset={offset}, limit={limit}, search={search}, order={order_column} {order_direction}, status_vinculacao={status_vinculacao}")

        # Parâmetros para a função RPC
        params = {
            "p_offset": offset,
            "p_limit": limit,
            "p_search": search,
            "p_status_vinculacao": status_vinculacao,
            "p_order_column": order_column,
            "p_order_direction": order_direction
        }
        params = {k: v for k, v in params.items() if v is not None}

        # --- INÍCIO DA ALTERAÇÃO: Usar asyncio.to_thread ---
        # Executa a chamada síncrona em um thread separado
        response = await asyncio.to_thread(
            lambda: supabase.rpc("func_listar_agendamentos_view", params).execute()
        )
        # --- FIM DA ALTERAÇÃO ---
        
        # Contagem total (simplificada para evitar erro de permissão na view)
        # Conta diretamente na tabela agendamentos (não reflete filtros da view/rpc)
        count_response = await asyncio.to_thread(
            lambda: supabase.table("agendamentos").select("id", count="exact").execute() 
        )
        total_count = count_response.count if count_response.count is not None else 0
        
        if not hasattr(response, 'data'):
             logger.error(f"Erro inesperado ao buscar agendamentos via RPC: resposta inválida {response}")
             raise HTTPException(status_code=500, detail="Erro ao buscar dados de agendamentos via RPC.")

        agendamentos = response.data

        logger.info(f"Consulta RPC executada. {len(agendamentos)} agendamentos retornados.")

        # Formatar datas e horas
        # Correção: Passar DATE_FIELDS como segundo argumento
        agendamentos_formatados = [format_date_fields(ag, DATE_FIELDS) for ag in agendamentos]

        # Serializar para JSON
        serializable_data = json.loads(json.dumps(agendamentos_formatados, cls=DateEncoder))

        return {
            "items": serializable_data,
            "total": total_count, 
            "offset": offset,
            "limit": limit
        }

    except HTTPException as http_exc:
         raise http_exc
    except Exception as e:
        logger.error(f"Erro ao listar agendamentos via RPC: {e}", exc_info=True)
        error_detail = str(e)
        if hasattr(e, 'details'): error_detail = e.details
        elif hasattr(e, 'message'): error_detail = e.message
        raise HTTPException(status_code=500, detail=f"Erro interno ao listar agendamentos via RPC: {error_detail}")

@router.get(
    "/{id}",
    summary="Obter agendamento por ID",
    description="Retorna os detalhes de um agendamento específico"
)
async def obter_agendamento(
    id: str = Path(..., description="ID do agendamento"),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Buscar o agendamento pelo ID
        result = supabase.table("agendamentos").select("*").eq("id", id).execute()

        # Verificar se o agendamento foi encontrado
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agendamento com ID {id} não encontrado"
            )

        # Obter o agendamento
        agendamento = result.data[0]
        
        # Buscar nome e carteirinha do paciente
        paciente_nome = None
        carteirinha = None
        if agendamento.get("paciente_id"):
            # Buscar dados do paciente
            paciente_result = supabase.table("pacientes").select("nome").eq("id", agendamento["paciente_id"]).execute()
            if paciente_result.data and len(paciente_result.data) > 0:
                paciente_nome = paciente_result.data[0].get("nome")
                
            # Buscar carteirinha do paciente
            carteirinha_result = supabase.table("carteirinhas").select("numero_carteirinha").eq("paciente_id", agendamento["paciente_id"]).execute()
            if carteirinha_result.data and len(carteirinha_result.data) > 0:
                carteirinha = carteirinha_result.data[0].get("numero_carteirinha")
        
        # Buscar nome do procedimento
        procedimento_nome = None
        if agendamento.get("procedimento_id"):
            procedimento_result = supabase.table("procedimentos").select("nome").eq("id", agendamento["procedimento_id"]).execute()
            if procedimento_result.data and len(procedimento_result.data) > 0:
                procedimento_nome = procedimento_result.data[0].get("nome")
        
        # Adicionar dados complementares ao agendamento
        agendamento["paciente_nome"] = paciente_nome
        agendamento["carteirinha"] = carteirinha
        agendamento["procedimento_nome"] = procedimento_nome
        agendamento["tipo_atend"] = procedimento_nome

        return {
            "success": True,
            "message": "Agendamento obtido com sucesso",
            "data": agendamento
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter agendamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter agendamento: {str(e)}"
        )

@router.post(
    "",
    summary="Criar agendamento",
    description="Cria um novo agendamento"
)
async def criar_agendamento(
    agendamento: AgendamentoCreate,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Preparar dados para inserção
        agendamento_dict = agendamento.model_dump()
        
        # Adicionar campos de auditoria
        agendamento_dict["created_at"] = datetime.datetime.now().isoformat()
        agendamento_dict["updated_at"] = agendamento_dict["created_at"]
        
        # Formatar campos de data
        agendamento_dict = format_date_fields(agendamento_dict, DATE_FIELDS)
        
        # Inserir no banco de dados
        result = supabase.table("agendamentos").insert(agendamento_dict).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao criar agendamento"
            )
        
        return {
            "success": True,
            "message": "Agendamento criado com sucesso",
            "data": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar agendamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar agendamento: {str(e)}"
        )

@router.put(
    "/{id}",
    summary="Atualizar agendamento",
    description="Atualiza um agendamento existente"
)
async def atualizar_agendamento(
    id: str = Path(..., description="ID do agendamento"),
    agendamento: AgendamentoUpdate = None,
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Verificar se o agendamento existe
        check_result = supabase.table("agendamentos").select("id").eq("id", id).execute()
        
        if not check_result.data or len(check_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agendamento com ID {id} não encontrado"
            )
        
        # Preparar dados para atualização
        agendamento_dict = agendamento.model_dump(exclude_unset=True)
        
        # Adicionar campo de atualização
        agendamento_dict["updated_at"] = datetime.datetime.now().isoformat()
        
        # Formatar campos de data
        agendamento_dict = format_date_fields(agendamento_dict, DATE_FIELDS)
        
        # Atualizar no banco de dados
        result = supabase.table("agendamentos").update(agendamento_dict).eq("id", id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao atualizar agendamento"
            )
        
        return {
            "success": True,
            "message": "Agendamento atualizado com sucesso",
            "data": result.data[0]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar agendamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar agendamento: {str(e)}"
        )

@router.delete(
    "/{id}",
    summary="Excluir agendamento",
    description="Exclui um agendamento existente"
)
async def excluir_agendamento(
    id: str = Path(..., description="ID do agendamento"),
    supabase: SupabaseClient = Depends(get_supabase_client)
):
    try:
        # Verificar se o agendamento existe
        check_result = supabase.table("agendamentos").select("id").eq("id", id).execute()
        
        if not check_result.data or len(check_result.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agendamento com ID {id} não encontrado"
            )
        
        # Excluir do banco de dados
        result = supabase.table("agendamentos").delete().eq("id", id).execute()
        
        return {
            "success": True,
            "message": "Agendamento excluído com sucesso",
            "data": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir agendamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir agendamento: {str(e)}"
        )