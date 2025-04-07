#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from pathlib import Path

# Configurar para importar o módulo de configuração do sistema
try:
    from config.config import supabase
    logger_config = True
except ImportError:
    # Tentar caminho alternativo
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from config.config import supabase
        logger_config = True
    except ImportError:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
            from backend.config.config import supabase
            logger_config = True
        except ImportError:
            print("Erro ao importar supabase. Verifique o caminho de importação.")
            sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("verificar_pacientes_carteirinhas")

def verificar_pacientes_com_carteirinhas():
    """
    Verifica a quantidade de pacientes que possuem carteirinhas e a quantidade que não possuem.
    """
    try:
        logger.info("Iniciando verificação de pacientes com carteirinhas...")
        
        # Contar o total de pacientes ativos
        resultado_pacientes = supabase.from_('pacientes').select('count', count='exact').is_('deleted_at', 'null').execute()
        total_pacientes = resultado_pacientes.count
        logger.info(f"Total de pacientes ativos: {total_pacientes}")
        
        # Contar pacientes com carteirinhas ativas
        resultado_com_carteirinhas = supabase.from_('carteirinhas')\
            .select('paciente_id', count='exact')\
            .is_('deleted_at', 'null')\
            .execute()
        
        # Transformar a lista de resultados em um conjunto de IDs únicos de pacientes
        ids_pacientes_com_carteirinhas = set()
        if hasattr(resultado_com_carteirinhas, 'data'):
            for item in resultado_com_carteirinhas.data:
                if 'paciente_id' in item:
                    ids_pacientes_com_carteirinhas.add(item['paciente_id'])
        
        pacientes_com_carteirinhas = len(ids_pacientes_com_carteirinhas)
        logger.info(f"Pacientes com carteirinhas: {pacientes_com_carteirinhas}")
        
        # Calcular pacientes sem carteirinhas
        pacientes_sem_carteirinhas = total_pacientes - pacientes_com_carteirinhas
        logger.info(f"Pacientes sem carteirinhas: {pacientes_sem_carteirinhas}")
        
        # Verificar amostra de pacientes sem carteirinhas (abordagem alternativa)
        # Primeiro, obter todos os IDs de pacientes
        todos_pacientes = supabase.from_('pacientes')\
            .select('id, nome, cpf, numero_carteirinha')\
            .is_('deleted_at', 'null')\
            .limit(500)\
            .execute()
        
        # Depois, filtrar localmente aqueles que não têm carteirinhas
        pacientes_sem_carteirinha_lista = []
        if hasattr(todos_pacientes, 'data'):
            for paciente in todos_pacientes.data:
                if paciente['id'] not in ids_pacientes_com_carteirinhas:
                    pacientes_sem_carteirinha_lista.append(paciente)
                    if len(pacientes_sem_carteirinha_lista) >= 10:
                        break

        logger.info("Amostra de pacientes sem carteirinhas:")
        for paciente in pacientes_sem_carteirinha_lista[:10]:
            logger.info(f"ID: {paciente['id']}, Nome: {paciente['nome']}, CPF: {paciente['cpf']}, Número da carteirinha: {paciente.get('numero_carteirinha', 'N/A')}")
        
        # Gerar resumo
        print("\n===== RESUMO DA VERIFICAÇÃO =====")
        print(f"Total de pacientes ativos: {total_pacientes}")
        print(f"Pacientes com carteirinhas: {pacientes_com_carteirinhas} ({(pacientes_com_carteirinhas/total_pacientes*100):.2f}%)")
        print(f"Pacientes sem carteirinhas: {pacientes_sem_carteirinhas} ({(pacientes_sem_carteirinhas/total_pacientes*100):.2f}%)")
        print("================================\n")
        
        logger.info("Verificação concluída com sucesso.")
    
    except Exception as e:
        logger.error(f"Ocorreu um erro ao verificar pacientes com carteirinhas: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verificar_pacientes_com_carteirinhas() 