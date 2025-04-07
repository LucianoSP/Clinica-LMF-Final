"""
Script para importar dados do MySQL para o Supabase

Este script conecta-se ao banco de dados MySQL local e
transfere os dados para o Supabase.
"""

import os
import mysql.connector
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("import_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do MySQL
mysql_config = {
    'host': os.getenv('MYSQL_IMPORT_HOST', 'localhost'),
    'user': os.getenv('MYSQL_IMPORT_USER', 'root'),
    'password': os.getenv('MYSQL_IMPORT_PASSWORD', ''),
    'database': os.getenv('MYSQL_IMPORT_DATABASE', 'clinica_lmf')
}

# Configurações do Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)


def connect_to_mysql():
    """Conecta ao banco de dados MySQL"""
    try:
        conn = mysql.connector.connect(**mysql_config)
        logger.info("Conexão com MySQL estabelecida com sucesso")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Erro ao conectar ao MySQL: {err}")
        return None


def fetch_data_from_mysql(conn, table_name):
    """Busca dados de uma tabela MySQL"""
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        cursor.close()
        logger.info(f"Dados obtidos com sucesso da tabela {table_name}: {len(rows)} registros")
        return rows
    except mysql.connector.Error as err:
        logger.error(f"Erro ao obter dados da tabela {table_name}: {err}")
        return []


def insert_to_supabase(table_name, data):
    """Insere dados no Supabase"""
    if not data:
        logger.warning(f"Nenhum dado para inserir na tabela {table_name}")
        return

    try:
        # Convertendo para DataFrame
        df = pd.DataFrame(data)
        
        # Ajustando nomes de colunas se necessário (MySQL e Postgres podem ter diferenças)
        
        # Inserindo no Supabase
        response = supabase.table(table_name).insert(data).execute()
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Erro ao inserir na tabela {table_name}: {response.error}")
        else:
            logger.info(f"Dados inseridos com sucesso na tabela {table_name}")
    
    except Exception as e:
        logger.error(f"Erro ao inserir dados no Supabase (tabela {table_name}): {str(e)}")


def main():
    """Função principal para executar a importação"""
    logger.info("Iniciando importação de dados do MySQL para o Supabase")
    
    # Conectar ao MySQL
    mysql_conn = connect_to_mysql()
    if not mysql_conn:
        return
    
    try:
        # Lista de tabelas para importar
        tables = ["pacientes", "medicos", "agendamentos", "consultas"]
        
        for table in tables:
            logger.info(f"Processando tabela: {table}")
            # Buscar dados do MySQL
            data = fetch_data_from_mysql(mysql_conn, table)
            
            # Inserir no Supabase
            insert_to_supabase(table, data)
            
        logger.info("Importação concluída com sucesso")
    
    except Exception as e:
        logger.error(f"Erro durante a importação: {str(e)}")
    
    finally:
        # Fechar conexão com MySQL
        if mysql_conn:
            mysql_conn.close()
            logger.info("Conexão com MySQL fechada")


if __name__ == "__main__":
    main()
