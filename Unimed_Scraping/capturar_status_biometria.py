#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para capturar status de biometria das guias da Unimed.

Este script implementa a funcionalidade de captura de status de biometria
das guias da Unimed, podendo ser usado em conjunto com o script de listagem
de guias e download de PDFs.

Utiliza a biblioteca Playwright para automação de navegador, oferecendo
melhor confiabilidade na extração dos dados.
"""

import os
import sys
from datetime import datetime

def capturar_status_biometria_simulado(alt_text, src=""):
    """
    Versão simulada da função de captura de status de biometria.
    
    Args:
        alt_text: Texto alternativo da imagem (simulado)
        src: Caminho da imagem (simulado)
        
    Returns:
        dict: Dicionário com status_biometria e tipo_biometria
    """
    if not alt_text:
        return {
            "status_biometria": "desconhecido",
            "tipo_biometria": "nenhum"
        }
    
    print(f"Texto ALT: {alt_text}")
    print(f"Fonte da imagem: {src}")
    
    # Analisa o status baseado no texto e imagem
    if "facial executada com sucesso" in alt_text or "facial-sucesso" in src:
        return {
            "status_biometria": "sucesso",
            "tipo_biometria": "facial"
        }
    elif "efetuada com sucesso" in alt_text or "digital-sucesso" in src:
        return {
            "status_biometria": "sucesso",
            "tipo_biometria": "digital"
        }
    elif "Problema" in alt_text or "erro" in src:
        return {
            "status_biometria": "erro",
            "tipo_biometria": "facial"
        }
    elif "não realizada" in alt_text:
        return {
            "status_biometria": "nao_realizada",
            "tipo_biometria": "nenhum"
        }
    else:
        return {
            "status_biometria": "desconhecido",
            "tipo_biometria": "nenhum"
        }

def obter_guias_simuladas(data_atendimento=None):
    """
    Retorna dados simulados de guias com diferentes status de biometria.
    
    Args:
        data_atendimento: Data no formato dd/mm/aaaa (opcional, apenas para compatibilidade)
    
    Returns:
        list: Lista de dicionários com informações das guias, incluindo status de biometria
    """
    print("MODO DE SIMULAÇÃO: Gerando dados de teste para demonstração")
    
    # Data para exibição (atual ou fornecida)
    if data_atendimento is None:
        data_atendimento = datetime.now().strftime("%d/%m/%Y")
    
    # Guias simuladas com diferentes status de biometria
    guias_simuladas = [
        {
            "numero_guia": "58342506",
            "data": data_atendimento,
            "hora": "14:20",
            "beneficiario": "ARTHUR SANTOS NUNES",
            "status_biometria": "sucesso",
            "tipo_biometria": "facial",
            "alt_text": "Leitura biométrica facial executada com sucesso",
            "src": "/cmagnet/Themes/Magneto2014/ico16biometria-facial-sucesso.png"
        },
        {
            "numero_guia": "58896840",
            "data": data_atendimento,
            "hora": "14:08",
            "beneficiario": "RAFAEL MOREIRA DE PINA CARVALHO",
            "status_biometria": "sucesso",
            "tipo_biometria": "digital",
            "alt_text": "Leitura biométrica efetuada com sucesso",
            "src": "/cmagnet/Themes/Magneto2014/ico16biometria-digital-sucesso.png"
        },
        {
            "numero_guia": "58923595",
            "data": data_atendimento,
            "hora": "14:05",
            "beneficiario": "AURORA RODRIGUES MELO",
            "status_biometria": "erro",
            "tipo_biometria": "facial",
            "alt_text": "Problema ao efetuar a leitura biométrica facial",
            "src": "/cmagnet/Themes/Magneto2014/ico16biometria-facial-erro.png"
        },
        {
            "numero_guia": "57497114",
            "data": data_atendimento,
            "hora": "14:03",
            "beneficiario": "GABRIEL BATISTA JORGE MOREIRA",
            "status_biometria": "nao_realizada",
            "tipo_biometria": "nenhum",
            "alt_text": "Leitura biométrica não realizada",
            "src": "/cmagnet/Themes/Magneto2014/ico16biometria-nao-realizada.png"
        }
    ]
    
    # Processar simulações para verificar a função capturar_status_biometria_simulado
    for i, guia in enumerate(guias_simuladas):
        print(f"\nProcessando guia simulada {i+1}/4: {guia['numero_guia']}")
        
        # Simular a função de captura
        info_biometria = capturar_status_biometria_simulado(guia["alt_text"], guia["src"])
        
        # Verifica se o resultado da função confere com o valor simulado
        if info_biometria["status_biometria"] == guia["status_biometria"] and \
           info_biometria["tipo_biometria"] == guia["tipo_biometria"]:
            print(f"✓ Status detectado corretamente: {info_biometria['status_biometria']} ({info_biometria['tipo_biometria']})")
        else:
            print(f"✗ Erro na detecção: Esperado {guia['status_biometria']} ({guia['tipo_biometria']}), " 
                  f"obtido {info_biometria['status_biometria']} ({info_biometria['tipo_biometria']})")
    
    print(f"\nSimulando {len(guias_simuladas)} guias para demonstração")
    
    # Remover os campos internos de simulação antes de retornar
    for guia in guias_simuladas:
        guia.pop("alt_text", None)
        guia.pop("src", None)
    
    return guias_simuladas

if __name__ == "__main__":
    # Data de hoje no formato dd/mm/aaaa
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    
    print(f"=== Capturando status de biometria das guias de hoje ({data_hoje}) ===")
    guias = obter_guias_simuladas(data_hoje)
    
    # Exibe resumo
    print("\n=== Resumo das Guias Capturadas ===")
    print(f"Total de guias processadas: {len(guias)}")
    
    if guias:
        print("\nDetalhes das guias processadas:")
        for i, guia in enumerate(guias):
            print(f"\n{i+1}. Guia: {guia['numero_guia']}")
            print(f"   Data/Hora: {guia['data']} {guia['hora']}")
            print(f"   Beneficiário: {guia['beneficiario']}")
            print(f"   Biometria: {guia['status_biometria']} ({guia['tipo_biometria']})")
    
    print("\nProcesso concluído!")
    
    # Explicação sobre a implementação real
    print("\n" + "-" * 60)
    print("NOTA: Este é um modo de simulação. Na implementação real, o script:")
    print("1. Acessa o portal da Unimed via Playwright")
    print("2. Navega até a página de guias")
    print("3. Extrai o status de biometria da página HTML")
    print("4. Atualiza a tabela guias_queue com essas informações")
    print("-" * 60) 