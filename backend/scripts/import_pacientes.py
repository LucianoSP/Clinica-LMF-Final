#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import uuid
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

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
        return databases
    except Exception as e:
        print(f"Erro ao listar bancos de dados: {e}")
        return []

def listar_tabelas(database):
    """Lista todas as tabelas do banco de dados especificado."""
    try:
        conexao = conectar_mysql(database)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        cursor.execute("SHOW TABLES")
        tabelas = [tabela[f'Tables_in_{database}'] for tabela in cursor.fetchall()]
        cursor.close()
        conexao.close()
        return tabelas
    except Exception as e:
        print(f"Erro ao listar tabelas: {e}")
        return []

def mostrar_estrutura_tabela(database, tabela):
    """Mostra a estrutura da tabela especificada."""
    try:
        conexao = conectar_mysql(database)
        if not conexao:
            return None
        
        cursor = conexao.cursor()
        cursor.execute(f"DESCRIBE {tabela}")
        estrutura = cursor.fetchall()
        cursor.close()
        conexao.close()
        return estrutura
    except Exception as e:
        print(f"Erro ao mostrar estrutura da tabela: {e}")
        return None

def buscar_pacientes_mysql(database, tabela):
    """Busca pacientes no banco de dados MySQL."""
    try:
        conexao = conectar_mysql(database)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        cursor.execute(f"SELECT * FROM {tabela}")
        pacientes = cursor.fetchall()
        cursor.close()
        conexao.close()
        return pacientes
    except Exception as e:
        print(f"Erro ao buscar pacientes: {e}")
        return []

def mapear_paciente(paciente_mysql):
    """Mapeia os dados do paciente do MySQL para o formato do Supabase."""
    # Ajuste o mapeamento conforme a estrutura das suas tabelas
    # Este é um exemplo que precisa ser adaptado aos seus campos específicos
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
        print(f"Erro ao salvar paciente no Supabase: {e}")
        return None

def importar_pacientes(database, tabela):
    """Importa pacientes do MySQL para o Supabase."""
    print(f"Iniciando importação de pacientes da tabela {tabela} do banco {database}...")
    
    # Buscar pacientes no MySQL
    pacientes_mysql = buscar_pacientes_mysql(database, tabela)
    if not pacientes_mysql:
        print("Nenhum paciente encontrado para importação.")
        return 0
    
    print(f"Encontrados {len(pacientes_mysql)} pacientes para importação.")
    
    # Importar cada paciente para o Supabase
    pacientes_importados = 0
    for paciente_mysql in pacientes_mysql:
        try:
            paciente_supabase = mapear_paciente(paciente_mysql)
            resultado = salvar_paciente_supabase(paciente_supabase)
            if resultado:
                pacientes_importados += 1
                print(f"Paciente {paciente_supabase['nome']} importado com sucesso!")
            else:
                print(f"Falha ao importar paciente {paciente_supabase['nome']}.")
        except Exception as e:
            print(f"Erro ao processar paciente: {e}")
    
    print(f"Importação concluída. {pacientes_importados} de {len(pacientes_mysql)} pacientes importados.")
    return pacientes_importados

def main():
    """Função principal do script."""
    print("=== IMPORTADOR DE PACIENTES MYSQL -> SUPABASE ===")
    
    # Listar databases disponíveis
    databases = listar_databases()
    if not databases:
        print("Não foi possível listar os bancos de dados. Verifique as configurações de conexão.")
        return
    
    print("\nBancos de dados disponíveis:")
    for i, db in enumerate(databases):
        print(f"{i+1}. {db}")
    
    # Usuário seleciona o banco de dados
    db_index = int(input("\nSelecione o número do banco de dados: ")) - 1
    if db_index < 0 or db_index >= len(databases):
        print("Seleção inválida!")
        return
    
    database = databases[db_index]
    
    # Listar tabelas do banco selecionado
    tabelas = listar_tabelas(database)
    if not tabelas:
        print(f"Não foi possível listar as tabelas do banco {database}.")
        return
    
    print(f"\nTabelas disponíveis no banco {database}:")
    for i, tabela in enumerate(tabelas):
        print(f"{i+1}. {tabela}")
    
    # Usuário seleciona a tabela
    tabela_index = int(input("\nSelecione o número da tabela que contém os pacientes: ")) - 1
    if tabela_index < 0 or tabela_index >= len(tabelas):
        print("Seleção inválida!")
        return
    
    tabela = tabelas[tabela_index]
    
    # Mostrar estrutura da tabela
    estrutura = mostrar_estrutura_tabela(database, tabela)
    if estrutura:
        print(f"\nEstrutura da tabela {tabela}:")
        for campo in estrutura:
            print(f"Campo: {campo['Field']}, Tipo: {campo['Type']}")
    
    # Confirmar importação
    confirmacao = input("\nDeseja iniciar a importação dos pacientes? (s/n): ")
    if confirmacao.lower() != 's':
        print("Importação cancelada.")
        return
    
    # Iniciar importação
    importar_pacientes(database, tabela)

if __name__ == "__main__":
    main() 