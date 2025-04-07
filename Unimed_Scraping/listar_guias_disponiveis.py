#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para listar guias disponíveis na Unimed em uma data específica.
"""

import os
import sys
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def listar_guias_disponiveis(data_atendimento):
    """
    Lista todas as guias disponíveis na Unimed para uma data específica.
    
    Args:
        data_atendimento (str): Data de atendimento no formato dd/mm/aaaa
        
    Returns:
        list: Lista de dicionários com informações das guias encontradas
    """
    try:
        # Verifica se o Playwright está instalado
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("Playwright não está instalado. Execute: pip install playwright")
            print("E depois: playwright install")
            return None
            
        print(f"\n[PLAYWRIGHT] Buscando guias disponíveis para a data {data_atendimento}")
        
        guias_encontradas = []
        
        with sync_playwright() as p:
            # Inicia o navegador (usando o modo headless depende do ambiente)
            # Em produção, é recomendável usar headless=True
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            
            # Configura timeout
            context.set_default_timeout(60000)  # 60 segundos de timeout
            
            # Abre uma nova página
            page = context.new_page()
            
            try:
                # 1. Acessa a página de login
                print("[PLAYWRIGHT] Acessando página de login...")
                page.goto("https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do")
                page.wait_for_load_state("networkidle")
                
                # 2. Realiza o login
                print("[PLAYWRIGHT] Realizando login...")
                username = os.getenv("UNIMED_USERNAME")
                password = os.getenv("UNIMED_PASSWORD")
                
                if not username or not password:
                    print("[PLAYWRIGHT] Erro: Credenciais não encontradas nas variáveis de ambiente")
                    return None
                
                page.fill("#login", username)
                page.fill("#passwordTemp", password)
                page.click("#Button_DoLogin")
                
                # Aguarda a página carregar completamente
                page.wait_for_load_state("networkidle")
                
                # 3. Navega para a página de exames finalizados
                print("[PLAYWRIGHT] Navegando para exames finalizados...")
                page.click("css=td#centro_21 a")
                page.wait_for_load_state("networkidle")
                
                # 4. Preenche o filtro de data
                print(f"[PLAYWRIGHT] Filtrando por data: {data_atendimento}")
                page.fill('input[name="s_dt_ini"]', data_atendimento)
                page.fill('input[name="s_dt_fim"]', data_atendimento)
                page.click('input[name="Button_FIltro"]')
                
                # Aguarda a tabela carregar
                page.wait_for_selector('#conteudo form table tbody')
                
                # 5. Função para extrair dados das guias na página atual
                def extrair_guias_da_pagina():
                    rows = page.query_selector_all('#conteudo form table tbody tr')
                    guias_pagina = []
                    
                    for row in rows:
                        # Pula o cabeçalho
                        if row.query_selector('th'):
                            continue
                        
                        # Extrai dados das células
                        try:
                            # Primeiro verifica se a linha tem células suficientes
                            cells = row.query_selector_all('td')
                            if len(cells) < 2:
                                continue
                            
                            # Procura links nas células (o número da guia geralmente está num link)
                            links_found = False
                            for i, cell in enumerate(cells):
                                cell_links = cell.query_selector_all('a')
                                if cell_links:
                                    for link in cell_links:
                                        link_text = link.inner_text().strip() if link else ""
                                        
                                        # Verifica se o texto parece ser um número de guia
                                        if link_text and link_text.isdigit() and len(link_text) > 5:
                                            # Encontramos um possível número de guia
                                            numero_guia = link_text
                                            
                                            # Tenta encontrar a data em outras células (geralmente próxima)
                                            data_cell = cells[i+1] if i+1 < len(cells) else None
                                            data_hora = data_cell.inner_text().strip() if data_cell else ""
                                            
                                            # Extrai informações adicionais da última célula
                                            last_cell = cells[-1] if cells else None
                                            info_adicional = last_cell.inner_text().strip() if last_cell else ""
                                            
                                            # Ignora se encontramos texto padrão como "Nº Guia"
                                            if "Nº Guia" in numero_guia or "Número" in numero_guia:
                                                continue
                                            
                                            # Extrai informações da data/hora
                                            data = ""
                                            hora = ""
                                            if data_hora:
                                                partes = data_hora.split()
                                                if len(partes) > 0:
                                                    data = partes[0]
                                                if len(partes) > 1:
                                                    hora = partes[1]
                                            
                                            # Se não temos uma data, tenta extrair de outras células
                                            if not data:
                                                for j, c in enumerate(cells):
                                                    if j != i:  # Não a mesma célula do número
                                                        cell_text = c.inner_text().strip()
                                                        # Verifica se o texto parece ser uma data (dd/mm/aaaa)
                                                        if '/' in cell_text and len(cell_text) >= 8:
                                                            partes = cell_text.split()
                                                            data = partes[0]
                                                            if len(partes) > 1:
                                                                hora = partes[1]
                                                            break
                                            
                                            guia_info = {
                                                "numero_guia": numero_guia,
                                                "data": data,
                                                "hora": hora,
                                                "informacao_adicional": info_adicional
                                            }
                                            
                                            guias_pagina.append(guia_info)
                                            print(f"[PLAYWRIGHT] Guia encontrada: {numero_guia} - {data} {hora} - {info_adicional}")
                                            links_found = True
                                            break
                                    
                                if links_found:
                                    break
                            
                        except Exception as e:
                            print(f"[PLAYWRIGHT] Erro ao extrair dados da linha: {str(e)}")
                    
                    return guias_pagina
                
                # Processa todas as páginas
                page_num = 1
                next_page_available = True
                
                while next_page_available:
                    print(f"[PLAYWRIGHT] Processando página {page_num}...")
                    
                    # Extrai guias da página atual
                    guias_pagina = extrair_guias_da_pagina()
                    guias_encontradas.extend(guias_pagina)
                    
                    # Verifica se existe o botão de próxima página e está habilitado
                    next_button = page.query_selector('a:text("Próxima")')
                    
                    if next_button and "disabled" not in (next_button.get_attribute("class") or ""):
                        page_num += 1
                        print(f"[PLAYWRIGHT] Navegando para página {page_num}...")
                        next_button.click()
                        page.wait_for_load_state("networkidle")
                    else:
                        next_page_available = False
                        print("[PLAYWRIGHT] Não há mais páginas disponíveis")
                
                print(f"[PLAYWRIGHT] Total de guias encontradas: {len(guias_encontradas)}")
                
            except Exception as e:
                print(f"[PLAYWRIGHT] Erro durante o processo: {str(e)}")
                import traceback
                traceback.print_exc()
                
            finally:
                # Fecha o navegador
                browser.close()
                print("[PLAYWRIGHT] Navegador fechado")
        
        return guias_encontradas
    
    except Exception as e:
        print(f"[PLAYWRIGHT] Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lista guias disponíveis na Unimed para uma data específica')
    parser.add_argument('--data_atendimento', type=str, help='Data do atendimento no formato dd/mm/aaaa')
    parser.add_argument('--salvar', action='store_true', help='Salva os resultados em um arquivo CSV')
    
    args = parser.parse_args()
    
    # Se a data não for fornecida, usa a data atual
    if not args.data_atendimento:
        args.data_atendimento = datetime.now().strftime("%d/%m/%Y")
    
    # Lista as guias
    guias = listar_guias_disponiveis(args.data_atendimento)
    
    if guias:
        print(f"\nTotal de {len(guias)} guias encontradas para a data {args.data_atendimento}")
        
        # Exibe as guias encontradas
        for i, guia in enumerate(guias, 1):
            print(f"\n{i}. Guia: {guia['numero_guia']}")
            print(f"   Data: {guia['data']}")
            print(f"   Hora: {guia['hora']}")
            print(f"   Informação Adicional: {guia['informacao_adicional']}")
        
        # Salva os resultados em CSV se solicitado
        if args.salvar and guias:
            import csv
            from datetime import datetime
            
            # Cria diretório para os resultados
            output_dir = os.path.join(os.getcwd(), "resultados")
            os.makedirs(output_dir, exist_ok=True)
            
            # Nome do arquivo CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = os.path.join(output_dir, f"guias_{args.data_atendimento.replace('/', '_')}_{timestamp}.csv")
            
            # Escreve os dados no CSV
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csv_file:
                fieldnames = ['numero_guia', 'data', 'hora', 'informacao_adicional']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                writer.writeheader()
                for guia in guias:
                    writer.writerow(guia)
            
            print(f"\nResultados salvos em: {csv_filename}")
        
        # Retorna com sucesso
        exit(0)
    else:
        print(f"\nNenhuma guia encontrada para a data {args.data_atendimento}")
        exit(1) 