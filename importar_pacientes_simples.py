#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymysql
import uuid
import os
import sys
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client, Client
import json
from typing import Optional, Union, Dict, Any, List

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

# Configurações Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Criar cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def formatar_data(valor: Optional[Union[str, datetime, date]]) -> Optional[str]:
    """
    Formata uma data em string ISO 8601.
    
    Args:
        valor: Data em vários formatos possíveis (string, datetime, date)
        
    Returns:
        String formatada no padrão ISO 8601 ou None se a entrada for inválida
    """
    if valor is None:
        return None
        
    try:
        # Se já for um objeto datetime ou date
        if isinstance(valor, (datetime, date)):
            return valor.isoformat()
            
        # Se for string, tentar converter
        if isinstance(valor, str):
            # Tentar vários formatos comuns
            formatos = [
                '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', 
                '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S',
                '%d/%m/%Y %H:%M:%S'
            ]
            
            for formato in formatos:
                try:
                    return datetime.strptime(valor, formato).isoformat()
                except ValueError:
                    continue
                    
        # Se chegou aqui, formato não reconhecido
        return None
        
    except Exception:
        # Em caso de erro, retornar None
        return None

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

def buscar_pacientes_mysql(database, tabela, limite=None):
    """Busca pacientes no banco de dados MySQL."""
    try:
        conexao = conectar_mysql(database)
        if not conexao:
            return []
        
        cursor = conexao.cursor()
        query = f"SELECT * FROM {tabela}"
        if limite:
            query += f" LIMIT {limite}"
            
        cursor.execute(query)
        pacientes = cursor.fetchall()
        cursor.close()
        conexao.close()
        return pacientes
    except Exception as e:
        print(f"Erro ao buscar pacientes: {e}")
        return []

def mapear_paciente(paciente_mysql):
    """Mapeia os campos de um paciente do MySQL para o formato do Supabase."""
    # Converter dados para o formato esperado no Supabase
    
    # Usar client_id para id_origem
    id_origem = str(paciente_mysql.get('cliente_id', '')) or str(paciente_mysql.get('id', ''))
    
    paciente_supabase = {
        'nome': paciente_mysql.get('nome', '') or paciente_mysql.get('Nome', ''),
        'id_origem': id_origem,  # Usar como identificador principal
        'codigo_aba': id_origem,  # Manter temporariamente para compatibilidade
        'cpf': paciente_mysql.get('cpf', '') or paciente_mysql.get('CPF', ''),
        'data_nascimento': formatar_data(paciente_mysql.get('data_nascimento', None)) or formatar_data(paciente_mysql.get('DataNasc', None)),
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
        'observacoes': paciente_mysql.get('observacoes', '') or paciente_mysql.get('Observacoes', ''),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'importado': True,
        'data_registro_origem': formatar_data(paciente_mysql.get('data_cadastro', None)),
        'data_atualizacao_origem': formatar_data(paciente_mysql.get('data_atualizacao', None))
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

def verificar_paciente_existe(id_origem):
    """Verifica se o paciente já existe no Supabase pelo id_origem."""
    try:
        response = supabase.table('pacientes').select('id').eq('id_origem', id_origem).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Erro ao verificar existência do paciente: {e}")
        return False

def importar_pacientes(database, tabela, modo='pular', limite=None):
    """Importa pacientes do MySQL para o Supabase."""
    print(f"Iniciando importação de pacientes da tabela {tabela} do banco {database}...")
    
    # Buscar pacientes no MySQL
    pacientes_mysql = buscar_pacientes_mysql(database, tabela, limite)
    if not pacientes_mysql:
        print("Nenhum paciente encontrado para importação.")
        return 0
    
    print(f"Encontrados {len(pacientes_mysql)} pacientes para importação.")
    
    # Importar cada paciente para o Supabase
    pacientes_importados = 0
    pacientes_pulados = 0
    
    for paciente_mysql in pacientes_mysql:
        try:
            # Mapear dados do MySQL para o formato do Supabase
            paciente_supabase = mapear_paciente(paciente_mysql)
            
            # Verificar se o paciente já existe pelo id_origem
            id_origem = paciente_supabase.get('id_origem')
            if not id_origem:
                print(f"Paciente sem id_origem, gerando automático: {paciente_mysql.get('nome', 'Sem nome')}")
                id_origem = str(uuid.uuid4())
                paciente_supabase['id_origem'] = id_origem
            
            paciente_existe = verificar_paciente_existe(id_origem)
            
            if paciente_existe and modo == 'pular':
                print(f"Paciente já existe, pulando: {paciente_supabase.get('nome')} (ID: {id_origem})")
                pacientes_pulados += 1
                continue
                
            elif paciente_existe and modo == 'substituir':
                # Remover o paciente existente
                supabase.table('pacientes').delete().eq('id_origem', id_origem).execute()
                print(f"Paciente removido para substituição: {paciente_supabase.get('nome')} (ID: {id_origem})")
            
            # Salvar o paciente no Supabase
            resultado = salvar_paciente_supabase(paciente_supabase)
            if resultado:
                pacientes_importados += 1
                print(f"Paciente importado com sucesso: {paciente_supabase.get('nome')} (ID: {id_origem})")
            else:
                print(f"Falha ao importar paciente: {paciente_supabase.get('nome')}")
        
        except Exception as e:
            print(f"Erro ao processar paciente: {str(e)}")
            continue
    
    print(f"Importação concluída. {pacientes_importados} de {len(pacientes_mysql)} pacientes importados.")
    if pacientes_pulados > 0:
        print(f"{pacientes_pulados} pacientes foram pulados por já existirem.")
    
    return pacientes_importados

def main():
    """Função principal do script."""
    print("=== IMPORTADOR DE PACIENTES MYSQL -> SUPABASE ===")
    
    # Testar conexão com Supabase
    try:
        resp = supabase.table('pacientes').select('id').limit(1).execute()
        print("Conexão com Supabase estabelecida com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {e}")
        return
    
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
    
    # Perguntar modo de importação
    print("\nModos de importação:")
    print("1. Pular registros existentes")
    print("2. Substituir registros existentes")
    modo_index = int(input("Selecione o modo de importação: "))
    modo = "pular" if modo_index == 1 else "substituir"
    
    # Perguntar se deseja limitar o número de registros
    usar_limite = input("\nDeseja limitar o número de registros a importar? (s/n): ").lower() == 's'
    limite = None
    if usar_limite:
        limite = int(input("Número de registros a importar: "))
    
    # Confirmar importação
    confirmacao = input(f"\nDeseja iniciar a importação dos pacientes da tabela {tabela}? (s/n): ")
    if confirmacao.lower() != 's':
        print("Importação cancelada.")
        return
    
    # Iniciar importação
    importar_pacientes(database, tabela, modo, limite)

if __name__ == "__main__":
    main() 