#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import uuid
import os
import sys
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Configurar logging
log_dir = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"import_pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('import_pacientes')

# Adicionar o diretório raiz ao PATH para importar os módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.config.config import supabase

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de conexão MySQL
MYSQL_CONFIG = {
    'host': '64.23.227.147',
    'port': 3306,
    'user': 'root',
    'password': '591#2n4AO1Qp',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def conectar_mysql(database=None):
    """Estabelece conexão com o banco de dados MySQL."""
    config = MYSQL_CONFIG.copy()
    if database:
        config['database'] = database
    
    try:
        logger.info(f"Conectando ao MySQL em {config['host']}...")
        conexao = pymysql.connect(**config)
        logger.info("Conexão estabelecida com sucesso!")
        return conexao
    except Exception as e:
        logger.error(f"Erro ao conectar ao MySQL: {e}")
        return None

def buscar_pacientes_mysql(database, tabela, limite=None, offset=0):
    """Busca pacientes no banco de dados MySQL com opção de limite e paginação."""
    try:
        conexao = conectar_mysql(database)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        query = f"SELECT * FROM {tabela}"
        if limite:
            query += f" LIMIT {limite} OFFSET {offset}"
        
        logger.info(f"Executando query: {query}")
        cursor.execute(query)
        pacientes = cursor.fetchall()
        cursor.close()
        conexao.close()
        return pacientes
    except Exception as e:
        logger.error(f"Erro ao buscar pacientes: {e}")
        return []

def mapear_paciente(paciente_mysql):
    """Mapeia os dados do paciente do MySQL para o formato do Supabase."""
    # Ajuste o mapeamento conforme a estrutura das suas tabelas
    paciente_supabase = {
        'id': str(uuid.uuid4()),
        'nome': paciente_mysql.get('nome', '') or paciente_mysql.get('Nome', ''),
        'codigo_aba': str(paciente_mysql.get('codigo', '') or paciente_mysql.get('id', '')),
        'cpf': paciente_mysql.get('cpf', '') or paciente_mysql.get('CPF', ''),
        'data_nascimento': paciente_mysql.get('data_nascimento', None) or paciente_mysql.get('DataNascimento', None),
        'nome_responsavel': paciente_mysql.get('nome_responsavel', '') or paciente_mysql.get('Responsavel', ''),
        'nome_mae': paciente_mysql.get('nome_mae', '') or paciente_mysql.get('Mae', ''),
        'nome_pai': paciente_mysql.get('nome_pai', '') or paciente_mysql.get('Pai', ''),
        'sexo': paciente_mysql.get('sexo', '') or paciente_mysql.get('Sexo', ''),
        'endereco': paciente_mysql.get('endereco', '') or paciente_mysql.get('Endereco', ''),
        'bairro': paciente_mysql.get('bairro', '') or paciente_mysql.get('Bairro', ''),
        'cidade': paciente_mysql.get('cidade', '') or paciente_mysql.get('Cidade', ''),
        'estado': paciente_mysql.get('estado', '') or paciente_mysql.get('Estado', ''),
        'telefone': paciente_mysql.get('telefone', '') or paciente_mysql.get('Telefone', ''),
        'email': paciente_mysql.get('email', '') or paciente_mysql.get('Email', ''),
        'observacoes': paciente_mysql.get('observacoes', '') or paciente_mysql.get('Observacoes', '')
    }
    return paciente_supabase

def salvar_paciente_supabase(paciente):
    """Salva o paciente no Supabase."""
    try:
        response = supabase.table('pacientes').insert(paciente).execute()
        return response.data
    except Exception as e:
        logger.error(f"Erro ao salvar paciente no Supabase: {e}")
        return None

def verificar_paciente_existe(codigo_aba):
    """Verifica se o paciente já existe no Supabase pelo código ABA."""
    try:
        response = supabase.table('pacientes').select('id').eq('codigo_aba', codigo_aba).execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Erro ao verificar existência do paciente: {e}")
        return False

def importar_pacientes(database, tabela, modo='pular', limite=None, offset=0):
    """
    Importa pacientes do MySQL para o Supabase.
    
    Parâmetros:
    - database: Nome do banco de dados MySQL
    - tabela: Nome da tabela de pacientes
    - modo: Modo de importação ('pular', 'substituir')
    - limite: Número máximo de registros a importar
    - offset: Número de registros a pular
    """
    logger.info(f"Iniciando importação de pacientes da tabela {tabela} do banco {database}...")
    logger.info(f"Modo: {modo}, Limite: {limite}, Offset: {offset}")
    
    # Buscar pacientes no MySQL
    pacientes_mysql = buscar_pacientes_mysql(database, tabela, limite, offset)
    if not pacientes_mysql:
        logger.warning("Nenhum paciente encontrado para importação.")
        return 0
    
    logger.info(f"Encontrados {len(pacientes_mysql)} pacientes para importação.")
    
    # Importar cada paciente para o Supabase
    pacientes_importados = 0
    pacientes_pulados = 0
    
    for paciente_mysql in pacientes_mysql:
        try:
            paciente_supabase = mapear_paciente(paciente_mysql)
            codigo_aba = paciente_supabase['codigo_aba']
            
            # Verificar se paciente já existe
            existe = verificar_paciente_existe(codigo_aba)
            
            if existe and modo == 'pular':
                logger.info(f"Paciente com código {codigo_aba} já existe. Pulando...")
                pacientes_pulados += 1
                continue
            elif existe and modo == 'substituir':
                # Remover paciente existente
                logger.info(f"Substituindo paciente com código {codigo_aba}...")
                supabase.table('pacientes').delete().eq('codigo_aba', codigo_aba).execute()
            
            # Inserir paciente
            resultado = salvar_paciente_supabase(paciente_supabase)
            if resultado:
                pacientes_importados += 1
                logger.info(f"Paciente {paciente_supabase['nome']} (código: {codigo_aba}) importado com sucesso!")
            else:
                logger.error(f"Falha ao importar paciente {paciente_supabase['nome']} (código: {codigo_aba}).")
        except Exception as e:
            logger.error(f"Erro ao processar paciente: {e}")
    
    logger.info(f"Importação concluída. {pacientes_importados} de {len(pacientes_mysql)} pacientes importados.")
    if pacientes_pulados > 0:
        logger.info(f"{pacientes_pulados} pacientes foram pulados por já existirem.")
    
    return pacientes_importados

def main():
    """Função principal do script em lote."""
    parser = argparse.ArgumentParser(description='Importador de pacientes MySQL para Supabase')
    parser.add_argument('--database', '-d', required=True, help='Nome do banco de dados MySQL')
    parser.add_argument('--tabela', '-t', required=True, help='Nome da tabela de pacientes')
    parser.add_argument('--modo', '-m', choices=['pular', 'substituir'], default='pular',
                       help='Modo de importação: pular registros existentes ou substituí-los')
    parser.add_argument('--limite', '-l', type=int, help='Número máximo de registros a importar')
    parser.add_argument('--offset', '-o', type=int, default=0, help='Número de registros a pular')
    
    args = parser.parse_args()
    
    # Iniciar importação
    importar_pacientes(args.database, args.tabela, args.modo, args.limite, args.offset)

if __name__ == "__main__":
    main() 