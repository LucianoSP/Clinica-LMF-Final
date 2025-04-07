#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para baixar múltiplas guias da Unimed em um período especificado.

Este script utiliza a funcionalidade do módulo baixar_guia_pdf.py para baixar
várias guias da Unimed dentro de um período especificado, com possibilidade
de limitar o número total de guias.

Uso:
    python baixar_multiplas_guias.py --data_inicio "01/01/2024" --data_fim "31/01/2024" --max_guias 10
"""

import os
import sys
import time
import argparse
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Tenta importar a função de listar guias
try:
    from listar_guias_disponiveis import listar_guias_disponiveis
except ImportError:
    print("Erro: Não foi possível importar a função listar_guias_disponiveis.")
    print("Verifique se o arquivo listar_guias_disponiveis.py está disponível.")
    sys.exit(1)

# Tenta importar a função de baixar PDFs
try:
    from baixar_guia_pdf import baixar_pdf_guia
except ImportError:
    print("Erro: Não foi possível importar a função baixar_pdf_guia.")
    print("Verifique se o arquivo baixar_guia_pdf.py está disponível.")
    sys.exit(1)

# Carrega variáveis de ambiente
load_dotenv()

def baixar_multiplas_guias(data_inicio, data_fim, max_guias=None):
    """
    Função principal para baixar múltiplas guias em um período.
    
    Args:
        data_inicio (str): Data inicial no formato dd/mm/aaaa
        data_fim (str): Data final no formato dd/mm/aaaa
        max_guias (int): Número máximo de guias a baixar (opcional)
        
    Returns:
        tuple: (total_encontradas, total_baixadas, falhas)
    """
    print(f"\n=== Iniciando busca e download de guias do período {data_inicio} até {data_fim} ===")
    
    if max_guias:
        print(f"Limite máximo de guias: {max_guias}")
    
    # Inicializa contadores
    total_encontradas = 0
    total_baixadas = 0
    falhas = []
    
    try:
        # Converte strings de data para objetos de data para manipulação
        data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
        data_fim_obj = datetime.strptime(data_fim, "%d/%m/%Y")
        
        # Verifica se as datas são válidas
        if data_inicio_obj > data_fim_obj:
            print("Erro: Data inicial maior que data final.")
            return (0, 0, ["Data inicial maior que data final"])
        
        # Loop através de cada data no intervalo
        data_atual_obj = data_inicio_obj
        
        while data_atual_obj <= data_fim_obj:
            data_atual = data_atual_obj.strftime("%d/%m/%Y")
            print(f"\n=== Processando data: {data_atual} ===")
            
            try:
                # Lista as guias disponíveis para esta data
                guias = listar_guias_disponiveis(data_atual)
                
                if not guias:
                    print(f"Nenhuma guia encontrada para a data {data_atual}")
                    data_atual_obj += timedelta(days=1)
                    continue
                
                print(f"Encontradas {len(guias)} guias para a data {data_atual}")
                total_encontradas += len(guias)
                
                # Limita o número de guias, se necessário
                guias_a_baixar = guias
                if max_guias is not None:
                    guias_restantes = max_guias - total_baixadas
                    if guias_restantes <= 0:
                        print("Limite máximo de guias atingido.")
                        break
                    
                    guias_a_baixar = guias[:guias_restantes]
                    print(f"Processando apenas {len(guias_a_baixar)} das {len(guias)} guias devido ao limite")
                
                # Baixa cada guia
                for i, guia in enumerate(guias_a_baixar):
                    guia_numero = guia["numero_guia"]
                    print(f"\n[{i+1}/{len(guias_a_baixar)}] Baixando guia {guia_numero}")
                    
                    try:
                        pdf_path = baixar_pdf_guia(guia_numero, data_atual)
                        
                        if pdf_path and os.path.exists(pdf_path):
                            print(f"PDF baixado com sucesso: {pdf_path}")
                            total_baixadas += 1
                        else:
                            print(f"Falha ao baixar o PDF da guia {guia_numero}")
                            falhas.append(f"Guia {guia_numero} - Data: {data_atual}")
                        
                        # Pequena pausa entre downloads
                        time.sleep(2)
                        
                    except Exception as e:
                        print(f"Erro ao baixar guia {guia_numero}: {str(e)}")
                        falhas.append(f"Guia {guia_numero} - Data: {data_atual} - Erro: {str(e)}")
                        continue
                
                # Verifica se atingiu o limite de guias
                if max_guias is not None and total_baixadas >= max_guias:
                    print(f"Limite de {max_guias} guias atingido.")
                    break
                
            except Exception as e:
                print(f"Erro ao processar data {data_atual}: {str(e)}")
                traceback.print_exc()
                falhas.append(f"Data: {data_atual} - Erro: {str(e)}")
            
            # Avança para o próximo dia
            data_atual_obj += timedelta(days=1)
        
        print(f"\n=== Resumo da Operação ===")
        print(f"Total de guias encontradas: {total_encontradas}")
        print(f"Total de guias baixadas com sucesso: {total_baixadas}")
        print(f"Total de falhas: {len(falhas)}")
        
        if falhas:
            print("\nListagem de falhas:")
            for falha in falhas:
                print(f"- {falha}")
        
        return (total_encontradas, total_baixadas, falhas)
        
    except Exception as e:
        print(f"Erro geral: {str(e)}")
        traceback.print_exc()
        return (total_encontradas, total_baixadas, [f"Erro geral: {str(e)}"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Baixa múltiplas guias da Unimed em um período')
    parser.add_argument('--data_inicio', type=str, help='Data inicial no formato dd/mm/aaaa')
    parser.add_argument('--data_fim', type=str, help='Data final no formato dd/mm/aaaa')
    parser.add_argument('--max_guias', type=int, help='Número máximo de guias a baixar')
    
    args = parser.parse_args()
    
    # Se a data inicial não for fornecida, usa a data atual
    if not args.data_inicio:
        args.data_inicio = datetime.now().strftime("%d/%m/%Y")
    
    # Se a data final não for fornecida, usa a mesma data inicial
    if not args.data_fim:
        args.data_fim = args.data_inicio
    
    # Executa o download das guias
    total_encontradas, total_baixadas, falhas = baixar_multiplas_guias(
        args.data_inicio, args.data_fim, args.max_guias
    )
    
    # Define o código de saída com base no resultado
    if total_baixadas > 0:
        if len(falhas) == 0:
            print("\nProcesso concluído com sucesso!")
            sys.exit(0)
        else:
            print("\nProcesso concluído com algumas falhas.")
            sys.exit(1)
    else:
        print("\nProcesso concluído sem nenhum download bem-sucedido.")
        sys.exit(2) 