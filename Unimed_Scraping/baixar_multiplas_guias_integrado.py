#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script integrado para listar, capturar status de biometria e baixar PDFs de guias da Unimed.

Este script combina as funcionalidades de listagem de guias, 
captura de status de biometria e download de PDFs em um único fluxo.

Uso:
    python baixar_multiplas_guias_integrado.py --data_inicio "01/01/2024" --data_fim "31/01/2024" --max_guias 10
"""

import os
import sys
import time
import json
import uuid
import argparse
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError

# Carrega variáveis de ambiente
load_dotenv()

# Diretório para salvar PDFs
PDF_DIR = "guias_pdf"
os.makedirs(PDF_DIR, exist_ok=True)

# Diretório para cache
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def gerar_task_id():
    """Gera um ID único para a tarefa de processamento"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = str(uuid.uuid4())[:4]
    return f"task_{timestamp}_{random_suffix}"

def capturar_status_biometria(guia_row):
    """
    Captura o status de biometria de uma linha de guia na tabela de guias da Unimed.
    
    Args:
        guia_row: Elemento da linha da tabela (tr)
        
    Returns:
        dict: Dicionário com status_biometria e tipo_biometria
    """
    # Obtém todas as células
    cells = guia_row.query_selector_all('td')
    if len(cells) < 5:
        return {
            "status_biometria": "desconhecido",
            "tipo_biometria": "nenhum"
        }
    
    # A célula com informações de biometria geralmente é a penúltima ou última
    penultima_cell = cells[len(cells)-2]
    ultima_cell = cells[len(cells)-1]
    
    # Procura imagens que indicam status de biometria em ambas as células
    for cell in [penultima_cell, ultima_cell]:
        biometria_icon = cell.query_selector('img[src*="biometria"]')
        if biometria_icon:
            # Extrai o atributo alt e src para determinar o status
            alt_text = biometria_icon.get_attribute('alt') or ""
            src = biometria_icon.get_attribute('src') or ""
            
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
            elif "não realizada" in alt_text or "nao-realizada" in src:
                return {
                    "status_biometria": "nao_realizada",
                    "tipo_biometria": "nenhum"
                }
    
    # Se não encontrou ícones específicos de biometria
    return {
        "status_biometria": "desconhecido",
        "tipo_biometria": "nenhum"
    }

def listar_guias_disponiveis(page, data_atendimento, debug=False):
    """
    Lista as guias disponíveis para uma data específica, incluindo status de biometria.
    
    Args:
        page: Página do Playwright
        data_atendimento: Data no formato dd/mm/aaaa
        debug: Modo de depuração
        
    Returns:
        list: Lista de dicionários com informações das guias, incluindo status de biometria
    """
    try:
        # Configura a data de atendimento
        print(f"Configurando filtro para data: {data_atendimento}")
        
        # Preenche o filtro de data
        page.fill('input[name="s_dt_ini"]', data_atendimento)
        page.fill('input[name="s_dt_fim"]', data_atendimento)
        page.click('input[name="Button_FIltro"]')
        
        # Aguarda resultados carregarem
        page.wait_for_selector('#conteudo form table tbody')
        
        # Obtém as linhas da tabela (excluindo o cabeçalho)
        rows = page.query_selector_all('#conteudo form table tbody tr:not(:has(th))')
        total_guias = len(rows)
        print(f"Encontradas {total_guias} guias para a data {data_atendimento}")
        
        # Processa as linhas para extrair informações
        guias = []
        for i, row in enumerate(rows):
            # Extrai dados básicos da guia
            cells = row.query_selector_all('td')
            if len(cells) >= 5:  # Verifica se há células suficientes
                data_hora = cells[0].inner_text().strip()
                numero_guia_element = cells[1].query_selector('a')
                
                # Verifica se há elemento de link e texto válido
                if numero_guia_element:
                    numero_guia = numero_guia_element.inner_text().strip()
                    
                    # Verifica se o número da guia é válido (não é um cabeçalho ou texto não numérico)
                    if numero_guia and numero_guia != "Nº Guia" and not numero_guia.startswith("Nº") and any(c.isdigit() for c in numero_guia):
                        beneficiario = cells[2].inner_text().strip()
                        
                        # Capturar status de biometria
                        print(f"Processando guia {i+1}/{total_guias}: {numero_guia}")
                        biometria_info = capturar_status_biometria(row)
                        
                        guia_info = {
                            "numero_guia": numero_guia,
                            "data": data_hora.split()[0] if " " in data_hora else data_hora,
                            "hora": data_hora.split()[1] if " " in data_hora and len(data_hora.split()) > 1 else "",
                            "beneficiario": beneficiario,
                            "status_biometria": biometria_info["status_biometria"],
                            "tipo_biometria": biometria_info["tipo_biometria"]
                        }
                        
                        print(f"  Status Biometria: {biometria_info['status_biometria']} ({biometria_info['tipo_biometria']})")
                        guias.append(guia_info)
                    else:
                        print(f"Ignorando linha {i+1} com número de guia inválido: '{numero_guia}'")
                else:
                    print(f"Ignorando linha {i+1} sem link de número de guia")
            
        # Verifica se há mais páginas
        next_page = page.query_selector('a:text("Próxima")')
        page_num = 1
        
        while next_page and "disabled" not in (next_page.get_attribute("class") or ""):
            page_num += 1
            print(f"Passando para a página {page_num}...")
            next_page.click()
            page.wait_for_load_state("networkidle")
            
            # Obtém as novas linhas
            rows = page.query_selector_all('#conteudo form table tbody tr:not(:has(th))')
            
            for i, row in enumerate(rows):
                cells = row.query_selector_all('td')
                if len(cells) >= 5:
                    data_hora = cells[0].inner_text().strip()
                    numero_guia_element = cells[1].query_selector('a')
                    
                    # Verifica se há elemento de link e texto válido
                    if numero_guia_element:
                        numero_guia = numero_guia_element.inner_text().strip()
                        
                        # Verifica se o número da guia é válido (não é um cabeçalho ou texto não numérico)
                        if numero_guia and numero_guia != "Nº Guia" and not numero_guia.startswith("Nº") and any(c.isdigit() for c in numero_guia):
                            beneficiario = cells[2].inner_text().strip()
                            
                            print(f"Processando guia {i+1}/{len(rows)} (página {page_num}): {numero_guia}")
                            biometria_info = capturar_status_biometria(row)
                            
                            guia_info = {
                                "numero_guia": numero_guia,
                                "data": data_hora.split()[0] if " " in data_hora else data_hora,
                                "hora": data_hora.split()[1] if " " in data_hora and len(data_hora.split()) > 1 else "",
                                "beneficiario": beneficiario,
                                "status_biometria": biometria_info["status_biometria"],
                                "tipo_biometria": biometria_info["tipo_biometria"]
                            }
                            
                            print(f"  Status Biometria: {biometria_info['status_biometria']} ({biometria_info['tipo_biometria']})")
                            guias.append(guia_info)
                        else:
                            print(f"Ignorando linha {i+1} na página {page_num} com número de guia inválido: '{numero_guia}'")
                    else:
                        print(f"Ignorando linha {i+1} na página {page_num} sem link de número de guia")
            
            # Verifica próxima página
            next_page = page.query_selector('a:text("Próxima")')
        
        return guias
        
    except Exception as e:
        print(f"Erro ao listar guias para a data {data_atendimento}: {str(e)}")
        if debug:
            traceback.print_exc()
        
        # Em modo de depuração, mostra dados simulados
        if debug:
            print("Retornando dados simulados para fins de teste")
            return obter_guias_simuladas(data_atendimento)
        return []

def obter_guias_simuladas(data_atendimento):
    """
    Retorna dados simulados de guias com diferentes status de biometria.
    
    Args:
        data_atendimento: Data no formato dd/mm/aaaa
    
    Returns:
        list: Lista de dicionários com informações das guias, incluindo status de biometria
    """
    print("MODO DE SIMULAÇÃO: Gerando dados de teste para demonstração")
    
    # Guias simuladas com diferentes status de biometria
    guias_simuladas = [
        {
            "numero_guia": "58342506",
            "data": data_atendimento,
            "hora": "14:20",
            "beneficiario": "ARTHUR SANTOS NUNES",
            "status_biometria": "sucesso",
            "tipo_biometria": "facial"
        },
        {
            "numero_guia": "58896840",
            "data": data_atendimento,
            "hora": "14:08",
            "beneficiario": "RAFAEL MOREIRA DE PINA CARVALHO",
            "status_biometria": "sucesso",
            "tipo_biometria": "digital"
        },
        {
            "numero_guia": "58923595",
            "data": data_atendimento,
            "hora": "14:05",
            "beneficiario": "AURORA RODRIGUES MELO",
            "status_biometria": "erro",
            "tipo_biometria": "facial"
        },
        {
            "numero_guia": "57497114",
            "data": data_atendimento,
            "hora": "14:03",
            "beneficiario": "GABRIEL BATISTA JORGE MOREIRA",
            "status_biometria": "nao_realizada",
            "tipo_biometria": "nenhum"
        }
    ]
    
    return guias_simuladas

def baixar_pdf_guia(page, numero_guia, data_atendimento, debug=False):
    """
    Baixa o PDF de uma guia específica identificada por número e data.
    
    Args:
        page: Página do Playwright
        numero_guia: Número da guia para download
        data_atendimento: Data de atendimento no formato dd/mm/aaaa
        debug: Modo de depuração
    
    Returns:
        str: Caminho do arquivo PDF salvo ou None em caso de falha
    """
    try:
        # Verifica se o número da guia é válido
        if not numero_guia or numero_guia == "Nº Guia" or not any(c.isdigit() for c in numero_guia):
            print(f"Número de guia inválido: '{numero_guia}'")
            return None
        
        # Configura a data e número da guia
        print(f"Filtrando por data {data_atendimento} e guia {numero_guia}")
        
        # Primeiro, vamos navegar para garantir que estamos na página correta
        print("Navegando para página de exames finalizados...")
        try:
            # Navega para a página de exames finalizados (se já não estivermos nela)
            if "ExamesFinalizados" not in page.url:
                # Tenta acessar a página de exames finalizados
                page.click("css=td#centro_21 a")
                page.wait_for_load_state("networkidle")
                
                # Verificamos se estamos na página correta
                if "ExamesFinalizados" not in page.url:
                    print("Falha ao navegar para a página de exames finalizados. URL atual:", page.url)
        except Exception as nav_error:
            print(f"Erro durante a navegação: {str(nav_error)}")
            # Continua mesmo se houver erro, já que podemos já estar na página correta
        
        # Agora, devemos estar na página correta. Vamos preencher os campos de filtro.
        # Primeiro vamos verificar se os campos estão visíveis antes de preenchê-los
        try:
            # Aguarda que os campos de filtro estejam visíveis
            print("Verificando campos de filtro...")
            page.wait_for_selector('input[name="s_dt_ini"]', timeout=10000)  # timeout reduzido para 10 segundos
            page.wait_for_selector('input[name="s_dt_fim"]', timeout=10000)
            
            # Tentamos diferentes seletores para o campo de número da guia
            numero_guia_input = None
            for selector in ['input[name="s_numero_guia"]', 'input[name="numeroGuia"]', 'input[name*="guia"]', 'input[placeholder*="guia"]']:
                try:
                    if page.query_selector(selector):
                        numero_guia_input = selector
                        print(f"Campo de número da guia encontrado com seletor: {selector}")
                        break
                except:
                    continue
            
            if not numero_guia_input:
                print("Não foi possível localizar o campo de número da guia. Tentando continuar...")
                numero_guia_input = 'input[name="s_numero_guia"]'  # usar o padrão mesmo assim
            
            # Preenche os campos de filtro
            print("Preenchendo campos de filtro...")
            page.fill('input[name="s_dt_ini"]', data_atendimento)
            page.fill('input[name="s_dt_fim"]', data_atendimento)
            
            # Tenta preencher o campo de número da guia
            try:
                page.fill(numero_guia_input, numero_guia)
            except Exception as fill_error:
                print(f"Não foi possível preencher o campo de número da guia: {str(fill_error)}")
                print("Tentando continuar apenas com filtro de data...")
            
            # Clica no botão de filtro
            filter_button = None
            for selector in ['input[name="Button_FIltro"]', 'input[value="Filtrar"]', 'button:has-text("Filtrar")']:
                try:
                    if page.query_selector(selector):
                        filter_button = selector
                        break
                except:
                    continue
            
            if filter_button:
                print(f"Clicando no botão de filtro: {filter_button}")
                page.click(filter_button)
            else:
                print("Botão de filtro não encontrado. Tentando continuar...")
            
            # Aguarda resultados carregarem
            page.wait_for_selector('#conteudo form table tbody', timeout=30000)
        except Exception as filter_error:
            print(f"Erro ao configurar filtros: {str(filter_error)}")
            # Continua para tentar localizar a guia mesmo assim
        
        # Verifica se a guia foi encontrada
        print("Procurando a guia na tabela...")
        
        # Função auxiliar para encontrar a linha da guia
        def encontrar_linha_guia():
            rows = page.query_selector_all('#conteudo form table tbody tr:not(:has(th))')
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 2:
                    guia_element = cells[1].query_selector('a')
                    if guia_element and guia_element.inner_text().strip() == numero_guia:
                        return row
            return None
        
        # Tenta encontrar a linha da guia
        row = encontrar_linha_guia()
        
        # Se não encontrou e não filtramos por número, tenta procurar manualmente
        if not row:
            print(f"Guia {numero_guia} não encontrada diretamente. Procurando em todas as linhas...")
            rows = page.query_selector_all('#conteudo form table tbody tr:not(:has(th))')
            for r in rows:
                cells = r.query_selector_all('td')
                if len(cells) >= 2:
                    cell_text = cells[1].inner_text().strip()
                    if numero_guia in cell_text:
                        row = r
                        print(f"Guia {numero_guia} encontrada através de busca textual")
                        break
        
        if not row:
            print(f"Guia {numero_guia} não encontrada para a data {data_atendimento}")
            return None
        
        # Clica no botão de imprimir da guia
        print("Clicando no botão de impressão...")
        cells = row.query_selector_all('td')
        last_cell = cells[len(cells)-1]
        
        print_icon = last_cell.query_selector('img[src*="Print.gif"]')
        if not print_icon:
            links = last_cell.query_selector_all('a')
            print_link = None
            
            # Procura por link específico de impressão
            for link in links:
                title = link.get_attribute('title') or ""
                onclick = link.get_attribute('onclick') or ""
                
                if "imprimir" in title.lower() or "print" in onclick.lower():
                    print_link = link
                    print(f"Link de impressão encontrado: {title}")
                    break
            
            if not print_link and links:
                # Se não achou link específico, usa o primeiro link
                print_link = links[0]
                print("Usando primeiro link da última célula")
            
            if print_link:
                print_link.click()
            else:
                print("Nenhum link de impressão encontrado")
                return None
        else:
            print_icon.click()
        
        # Aguarda o menu popup aparecer
        print("Aguardando popup aparecer...")
        page.wait_for_timeout(3000)  # Espera 3 segundos para o popup aparecer
        
        # Procura o link "Todas as guias"
        try:
            # Tentamos encontrar o link "Todas as guias" diretamente
            div_id = f"subpGuia{numero_guia}"
            popup_div = page.query_selector(f"#{div_id}")
            
            if popup_div:
                print(f"Div {div_id} encontrado!")
                link_id = f"print_todas_guias_{numero_guia}"
                todas_guias_link = popup_div.query_selector(f"#{link_id}")
                
                if todas_guias_link:
                    print(f"Link 'Todas as guias' encontrado com ID: {link_id}")
                    todas_guias_link.click()
                    print("Clique no link 'Todas as guias' realizado")
                    
                    # Aguarda carregamento após o clique
                    page.wait_for_timeout(3000)
                
        except Exception as e:
            print(f"Erro ao buscar e clicar no link 'Todas as guias': {str(e)}")
            # Continua para tentar outras abordagens
        
        # Configura o download
        print("Aguardando download iniciar...")
        nome_arquivo = f"{numero_guia}_{data_atendimento.replace('/', '')}.pdf"
        caminho_arquivo = os.path.join(PDF_DIR, nome_arquivo)
        
        # Tentamos duas abordagens:
        
        # 1. Verificar se há botão de PDF para clicar
        pdf_button = page.query_selector('input[value="PDF"]')
        if pdf_button:
            print("Botão PDF encontrado. Clicando para download...")
            with page.expect_download() as download_info:
                pdf_button.click()
            
            # Aguarda o download e salva o arquivo
            download = download_info.value
            download.save_as(caminho_arquivo)
            print(f"PDF baixado com sucesso: {caminho_arquivo}")
            return caminho_arquivo
        
        # 2. Se não houver botão, tentar gerar PDF da página atual
        print("Tentando gerar PDF da página atual...")
        try:
            page.pdf(path=caminho_arquivo)
            
            # Verifica se o arquivo foi gerado corretamente
            if os.path.exists(caminho_arquivo) and os.path.getsize(caminho_arquivo) > 5000:
                print(f"PDF gerado com sucesso: {caminho_arquivo}")
                return caminho_arquivo
            else:
                print("PDF gerado com tamanho suspeito, pode estar incompleto")
                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                return None
        except Exception as pdf_error:
            print(f"Erro ao gerar PDF: {str(pdf_error)}")
            return None
    
    except Exception as e:
        print(f"Erro ao baixar PDF da guia {numero_guia}: {str(e)}")
        if debug:
            traceback.print_exc()
        return None

def registrar_guia_em_fila(task_id, guia_info, caminho_arquivo, conexao_db=None):
    """
    Registra a guia na tabela guias_queue.
    
    Args:
        task_id: ID da tarefa
        guia_info: Informações da guia
        caminho_arquivo: Caminho do arquivo PDF
        conexao_db: Conexão com o banco de dados
    
    Returns:
        bool: True se registro foi bem sucedido, False caso contrário
    """
    if conexao_db is None:
        # Se não temos conexão com BD, registramos em cache local
        cache_file = os.path.join(CACHE_DIR, f"guias_queue_{task_id}.json")
        try:
            # Carrega cache existente ou cria novo
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            else:
                cache = []
            
            # Adiciona nova guia
            guia_entry = {
                "id": str(uuid.uuid4()),
                "task_id": task_id,
                "numero_guia": guia_info["numero_guia"],
                "data_atendimento": f"{guia_info['data']} {guia_info['hora']}",
                "caminho_arquivo": caminho_arquivo,
                "status_biometria": guia_info["status_biometria"],
                "tipo_biometria": guia_info["tipo_biometria"],
                "status": "pendente_processamento",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            cache.append(guia_entry)
            
            # Salva cache atualizado
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            
            print(f"Guia {guia_info['numero_guia']} registrada no cache local")
            return True
        
        except Exception as e:
            print(f"Erro ao registrar guia {guia_info['numero_guia']} no cache: {str(e)}")
            return False
    
    else:
        # TODO: Implementar registro no Supabase quando disponível
        print("Registro em banco de dados não implementado ainda.")
        return False

def atualizar_status_processamento(task_id, total_encontradas, total_baixadas, falhas, conexao_db=None):
    """
    Atualiza o status de processamento na tabela processing_status.
    
    Args:
        task_id: ID da tarefa
        total_encontradas: Total de guias encontradas
        total_baixadas: Total de guias baixadas com sucesso
        falhas: Lista de falhas ocorridas
        conexao_db: Conexão com o banco de dados
    """
    if conexao_db is None:
        # Se não temos conexão com BD, registramos em cache local
        cache_file = os.path.join(CACHE_DIR, f"processing_status_{task_id}.json")
        try:
            status_entry = {
                "id": str(uuid.uuid4()),
                "task_id": task_id,
                "status": "completed" if not falhas else "completed_with_errors",
                "total_guides": total_encontradas,
                "total_pdfs_baixados": total_baixadas,
                "error": str(falhas) if falhas else None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            # Salva status em arquivo
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(status_entry, f, indent=2, ensure_ascii=False)
            
            print(f"Status de processamento atualizado no cache local")
        
        except Exception as e:
            print(f"Erro ao atualizar status de processamento: {str(e)}")
    
    else:
        # TODO: Implementar atualização no Supabase quando disponível
        print("Atualização em banco de dados não implementada ainda.")

def baixar_multiplas_guias(data_inicio, data_fim, max_guias=None, debug=False, conexao_db=None):
    """
    Função principal para baixar múltiplas guias em um período.
    
    Args:
        data_inicio: Data inicial no formato dd/mm/aaaa
        data_fim: Data final no formato dd/mm/aaaa
        max_guias: Número máximo de guias a baixar (opcional)
        debug: Modo de depuração
        conexao_db: Conexão com o banco de dados
    
    Returns:
        tuple: (total_encontradas, total_baixadas, falhas)
    """
    # Cria ID da tarefa
    task_id = gerar_task_id()
    print(f"\n=== Iniciando processamento {task_id} - período de {data_inicio} até {data_fim} ===")
    
    if max_guias:
        print(f"Limite máximo de guias: {max_guias}")
    
    # Inicializa contadores
    total_encontradas = 0
    total_baixadas = 0
    falhas = []
    
    try:
        # Em modo de depuração, usar dados simulados sem iniciar o navegador
        if debug:
            print("Executando em modo de depuração com dados simulados")
            
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
                print(f"\n=== Processando data: {data_atual} (SIMULADO) ===")
                
                # Obtém guias simuladas
                guias = obter_guias_simuladas(data_atual)
                
                if not guias:
                    print(f"Nenhuma guia encontrada para a data {data_atual}")
                    data_atual_obj += timedelta(days=1)
                    continue
                
                print(f"Encontradas {len(guias)} guias simuladas para a data {data_atual}")
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
                
                # Simula o download de cada guia
                for i, guia in enumerate(guias_a_baixar):
                    numero_guia = guia["numero_guia"]
                    print(f"\n[{i+1}/{len(guias_a_baixar)}] Simulando download da guia {numero_guia}")
                    
                    # Simula um arquivo PDF
                    nome_arquivo = f"{numero_guia}_{data_atual.replace('/', '')}.pdf"
                    caminho_arquivo = os.path.join(PDF_DIR, nome_arquivo)
                    
                    # Cria um arquivo vazio para simulação
                    with open(caminho_arquivo, 'w') as f:
                        f.write(f"Simulação de PDF da guia {numero_guia} - {data_atual}")
                    
                    # Mostra informações de biometria capturadas
                    print(f"  Status Biometria: {guia['status_biometria']} ({guia['tipo_biometria']})")
                    
                    # Registra guia na fila de processamento
                    registrar_guia_em_fila(task_id, guia, caminho_arquivo, conexao_db)
                    print(f"  PDF simulado e registrado: {caminho_arquivo}")
                    total_baixadas += 1
                    
                    # Pequena pausa entre downloads
                    time.sleep(1)
                    
                    # Verifica se atingiu o limite de guias
                    if max_guias is not None and total_baixadas >= max_guias:
                        print(f"Limite de {max_guias} guias atingido.")
                        break
                
                # Avança para o próximo dia
                data_atual_obj += timedelta(days=1)
        
        else:
            # Código original para acesso real ao site
            with sync_playwright() as p:
                # Inicia navegador com mais opções
                browser_type = p.chromium
                print("Iniciando navegador Chromium...")
                
                browser = browser_type.launch(
                    headless=False,  # headless=True para execução sem interface
                    args=['--disable-web-security', '--no-sandbox', '--disable-features=IsolateOrigins,site-per-process']
                )
                
                context = browser.new_context(
                    viewport={"width": 1280, "height": 800},
                    accept_downloads=True,
                    ignore_https_errors=True  # Ignora erros HTTPS
                )
                
                # Configurar timeout mais longo
                context.set_default_timeout(120000)  # 2 minutos
                
                page = context.new_page()
                
                try:
                    # Login no sistema (usando o domínio que funciona)
                    print("Realizando login na Unimed...")
                    
                    # Aqui está a correção: usando o mesmo domínio dos outros scripts
                    login_url = "https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do"
                    print(f"URL de login: {login_url}")
                    page.goto(login_url, timeout=60000)
                    
                    # Verificando se carregou a página de login corretamente
                    if "login" in page.url.lower():
                        print("Página de login carregada com sucesso")
                    else:
                        print(f"Página carregada: {page.url} - pode não ser a página de login")
                    
                    # Preenche credenciais (usando seletores corretos para esse site)
                    username = os.getenv("UNIMED_USERNAME")
                    password = os.getenv("UNIMED_PASSWORD")
                    
                    if not username or not password:
                        print("Credenciais não configuradas. Verifique as variáveis UNIMED_USERNAME e UNIMED_PASSWORD.")
                        return (0, 0, ["Credenciais não configuradas"])
                    
                    # Ajustando os seletores para a página correta
                    page.fill("#login", username)
                    page.fill("#passwordTemp", password)
                    page.click("#Button_DoLogin")
                    
                    # Aguarda login completar
                    print("Aguardando carregamento após login...")
                    page.wait_for_load_state("networkidle")
                    
                    # Navega para a página de exames finalizados
                    print("Navegando para exames finalizados...")
                    page.click("css=td#centro_21 a")
                    page.wait_for_load_state("networkidle")
                    
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
                            # Lista as guias disponíveis para esta data e captura status de biometria
                            guias = listar_guias_disponiveis(page, data_atual, debug)
                            
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
                                numero_guia = guia["numero_guia"]
                                print(f"\n[{i+1}/{len(guias_a_baixar)}] Baixando guia {numero_guia}")
                                
                                try:
                                    # Mostra informações de biometria capturadas
                                    print(f"  Status Biometria: {guia['status_biometria']} ({guia['tipo_biometria']})")
                                    
                                    # Baixa o PDF da guia
                                    caminho_arquivo = baixar_pdf_guia(page, numero_guia, data_atual, debug)
                                    
                                    if caminho_arquivo:
                                        # Registra guia na fila de processamento
                                        registrar_guia_em_fila(task_id, guia, caminho_arquivo, conexao_db)
                                        print(f"  PDF baixado e registrado: {caminho_arquivo}")
                                        total_baixadas += 1
                                    else:
                                        print(f"  Falha ao baixar o PDF da guia {numero_guia}")
                                        falhas.append(f"Guia {numero_guia} - Data: {data_atual}")
                                    
                                    # Pequena pausa entre downloads
                                    time.sleep(2)
                                    
                                except Exception as e:
                                    print(f"Erro ao processar guia {numero_guia}: {str(e)}")
                                    falhas.append(f"Guia {numero_guia} - Data: {data_atual} - Erro: {str(e)}")
                                    if debug:
                                        traceback.print_exc()
                                    continue
                                
                                # Verifica se atingiu o limite de guias
                                if max_guias is not None and total_baixadas >= max_guias:
                                    print(f"Limite de {max_guias} guias atingido.")
                                    break
                        
                        except Exception as e:
                            print(f"Erro ao processar data {data_atual}: {str(e)}")
                            falhas.append(f"Data: {data_atual} - Erro: {str(e)}")
                            if debug:
                                traceback.print_exc()
                        
                        # Avança para o próximo dia
                        data_atual_obj += timedelta(days=1)
                
                except Exception as e:
                    print(f"Erro durante o processamento: {str(e)}")
                    falhas.append(f"Erro geral: {str(e)}")
                    if debug:
                        traceback.print_exc()
                
                finally:
                    # Fecha o navegador
                    print("Fechando navegador...")
                    browser.close()
        
        # Atualiza status de processamento
        atualizar_status_processamento(task_id, total_encontradas, total_baixadas, falhas, conexao_db)
        
        print(f"\n=== Resumo da Operação ===")
        print(f"Task ID: {task_id}")
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
        if debug:
            traceback.print_exc()
        return (total_encontradas, total_baixadas, [f"Erro geral: {str(e)}"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Baixa múltiplas guias da Unimed em um período')
    parser.add_argument('--data_inicio', type=str, help='Data inicial no formato dd/mm/aaaa')
    parser.add_argument('--data_fim', type=str, help='Data final no formato dd/mm/aaaa')
    parser.add_argument('--max_guias', type=int, help='Número máximo de guias a baixar')
    parser.add_argument('--debug', action='store_true', help='Ativa modo de depuração com dados simulados')
    
    args = parser.parse_args()
    
    # Se a data inicial não for fornecida, usa a data atual
    if not args.data_inicio:
        args.data_inicio = datetime.now().strftime("%d/%m/%Y")
    
    # Se a data final não for fornecida, usa a mesma data inicial
    if not args.data_fim:
        args.data_fim = args.data_inicio
    
    # Executa o download das guias
    total_encontradas, total_baixadas, falhas = baixar_multiplas_guias(
        args.data_inicio, args.data_fim, args.max_guias, args.debug
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