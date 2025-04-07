#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Carregar variáveis de ambiente
load_dotenv()

def testar_conexao_supabase():
    """Testa a conexão com o Supabase."""
    try:
        # Obter credenciais do ambiente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Erro: SUPABASE_URL ou SUPABASE_KEY não estão definidos no arquivo .env")
            return False
        
        print(f"Conectando ao Supabase em {supabase_url}...")
        
        # Criar cliente Supabase
        supabase = create_client(supabase_url, supabase_key)
        
        # Testar com uma consulta simples
        response = supabase.table("pacientes").select("id").limit(1).execute()
        
        print("Conexão com Supabase estabelecida com sucesso!")
        print(f"Número de pacientes encontrados na consulta de teste: {len(response.data)}")
        
        return True
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {e}")
        return False

def listar_tabelas_supabase():
    """Lista algumas tabelas do Supabase."""
    try:
        # Obter credenciais do ambiente
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        # Criar cliente Supabase
        supabase = create_client(supabase_url, supabase_key)
        
        # Lista de tabelas comuns para verificar
        tabelas_para_verificar = [
            "pacientes",
            "usuarios",
            "protocolos_excel",
            "procedimentos"
        ]
        
        print("\nVerificando tabelas no Supabase:")
        for tabela in tabelas_para_verificar:
            try:
                response = supabase.table(tabela).select("count").limit(1).execute()
                print(f"Tabela '{tabela}' encontrada.")
            except Exception as e:
                print(f"Tabela '{tabela}' não encontrada ou erro de acesso: {e}")
        
    except Exception as e:
        print(f"Erro ao listar tabelas: {e}")

if __name__ == "__main__":
    print("=== TESTE DE CONEXÃO SUPABASE ===")
    if testar_conexao_supabase():
        listar_tabelas_supabase()
    else:
        print("Não foi possível continuar os testes devido a falha na conexão.") 