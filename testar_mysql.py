#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import sys
from dotenv import load_dotenv

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
        print(f"Conectando ao MySQL em {config['host']}...")
        conexao = pymysql.connect(**config)
        print("Conexão estabelecida com sucesso!")
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def listar_databases():
    """Lista todos os bancos de dados disponíveis no MySQL."""
    try:
        conexao = conectar_mysql()
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db['Database'] for db in cursor.fetchall()]
        cursor.close()
        conexao.close()
        
        print("Bancos de dados disponíveis:")
        for i, db in enumerate(databases):
            print(f"{i+1}. {db}")
            
        return databases
    except Exception as e:
        print(f"Erro ao listar bancos de dados: {e}")
        return []

if __name__ == "__main__":
    print("=== TESTE DE CONEXÃO MYSQL ===")
    listar_databases() 