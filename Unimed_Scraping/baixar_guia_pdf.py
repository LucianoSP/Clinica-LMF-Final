#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para baixar PDFs de guias da Unimed Goiânia.

Este script utiliza Playwright para navegar pelo site da Unimed,
fazer login, encontrar guias por número e data, e baixar os PDFs correspondentes.

Uso:
    python baixar_guia_pdf.py --numero_guia 123456789 --data_atendimento "01/01/2023"
"""

import os
import sys
import time
import shutil
import argparse
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def baixar_pdf_guia(numero_guia, data_atendimento):
    """
    Função principal para baixar o PDF de uma guia específica.
    
    Args:
        numero_guia (str): Número da guia a ser pesquisada
        data_atendimento (str): Data de atendimento no formato dd/mm/aaaa
        
    Returns:
        str: Caminho para o arquivo PDF baixado ou None se falhar
    """
    try:
        # Verifica se o Playwright está instalado
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("Playwright não está instalado. Execute: pip install playwright")
            print("E depois: playwright install")
            return None
            
        print(f"\n[PLAYWRIGHT] Tentando baixar PDF da guia {numero_guia} com data {data_atendimento}")
        
        # Prepara diretório para downloads
        pdf_dir = os.path.join(os.getcwd(), "guias_pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Nome do arquivo PDF final
        pdf_filename = f"{numero_guia}_{data_atendimento.replace('/', '_')}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        
        # Verifica se o PDF já existe
        if os.path.exists(pdf_path):
            print(f"[PLAYWRIGHT] PDF já existe em: {pdf_path}")
            return pdf_path
        
        # Registra os arquivos PDF que já existem para comparação posterior
        existing_pdfs_before = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
        print(f"[PLAYWRIGHT] Arquivos PDF existentes antes do download: {len(existing_pdfs_before)}")
        
        with sync_playwright() as p:
            # Inicia o navegador (usando o modo headless depende do ambiente)
            # Em produção, é recomendável usar headless=True
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                accept_downloads=True,
                viewport={"width": 1920, "height": 1080}
            )
            
            # Configura o diretório de download e timeout
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
                
                # 5. Localiza a linha da guia
                guide_found = False
                
                # Função para verificar se estamos na página correta e localizar a guia
                def find_guide_row():
                    rows = page.query_selector_all('#conteudo form table tbody tr')
                    for row in rows:
                        # Pula o cabeçalho
                        if row.query_selector('th'):
                            continue
                        
                        # Verifica se a célula da segunda coluna contém o número da guia
                        guide_cell = row.query_selector('td:nth-child(2) a')
                        if guide_cell and guide_cell.inner_text().strip() == numero_guia:
                            print(f"[PLAYWRIGHT] Guia {numero_guia} encontrada na tabela")
                            return row
                    return None
                
                # Procura pela guia na página atual
                guide_row = find_guide_row()
                
                # Se não encontrou, verifica se há mais páginas
                if not guide_row:
                    print("[PLAYWRIGHT] Guia não encontrada na primeira página, verificando próximas páginas...")
                    
                    # Loop para navegar por páginas adicionais
                    next_page_available = True
                    page_num = 1
                    
                    while next_page_available and not guide_row:
                        # Verifica se existe o botão de próxima página e está habilitado
                        next_button = page.query_selector('a:text("Próxima")')
                        
                        if next_button and "disabled" not in (next_button.get_attribute("class") or ""):
                            page_num += 1
                            print(f"[PLAYWRIGHT] Navegando para página {page_num}...")
                            next_button.click()
                            page.wait_for_load_state("networkidle")
                            
                            # Procura a guia na nova página
                            guide_row = find_guide_row()
                        else:
                            next_page_available = False
                            print("[PLAYWRIGHT] Não há mais páginas disponíveis")
                
                # Se encontrou a guia, procede com o download
                if guide_row:
                    guide_found = True
                    print("[PLAYWRIGHT] Encontrou a linha da guia, buscando o botão de impressão...")
                    
                    # 6. Encontra e clica no ícone/link de impressão na última coluna
                    last_cell = guide_row.query_selector('td:last-child')
                    
                    # Tenta encontrar o ícone de impressão ou qualquer link na última célula
                    print_icon = last_cell.query_selector('img[src*="Print.gif"]')
                    
                    # Remover a espera pelo popup que estava causando timeout
                    if print_icon:
                        print("[PLAYWRIGHT] Ícone de impressão encontrado")
                        print_icon.click()
                    else:
                        print("[PLAYWRIGHT] Ícone de impressão não encontrado, tentando links...")
                        links = last_cell.query_selector_all('a')
                        
                        if links:
                            # Procura por link específico de impressão
                            print_link = None
                            for link in links:
                                title = link.get_attribute('title') or ""
                                onclick = link.get_attribute('onclick') or ""
                                
                                if "imprimir" in title.lower() or "print" in onclick.lower():
                                    print_link = link
                                    print(f"[PLAYWRIGHT] Link de impressão encontrado: {title}")
                                    break
                            
                            if not print_link and links:
                                # Se não achou link específico, usa o primeiro link
                                print_link = links[0]
                                print("[PLAYWRIGHT] Usando primeiro link da última célula")
                            
                            if print_link:
                                print_link.click()
                            else:
                                raise Exception("Nenhum link encontrado na última célula")
                        else:
                            raise Exception("Nenhum link encontrado na última célula")
                    
                    # 7. Aguarda o menu popup aparecer
                    print("[PLAYWRIGHT] Aguardando popup aparecer...")
                    page.wait_for_timeout(3000)  # Espera 3 segundos para o popup aparecer
                    
                    # 8. Nova abordagem: vamos tentar localizar e clicar no link "Todas as guias" sem esperar popup
                    print("[PLAYWRIGHT] Buscando o link 'Todas as guias'...")
                    popup_opened = False
                    pdf_generated = False
                    
                    # Primeiro tenta capturar a popup caso tenha aberto uma
                    try:
                        # Vamos ver se encontramos o link "Todas as guias" diretamente
                        div_id = f"subpGuia{numero_guia}"
                        popup_div = page.query_selector(f"#{div_id}")
                        
                        if popup_div:
                            print(f"[PLAYWRIGHT] Div {div_id} encontrado!")
                            link_id = f"print_todas_guias_{numero_guia}"
                            todas_guias_link = popup_div.query_selector(f"#{link_id}")
                            
                            if todas_guias_link:
                                print(f"[PLAYWRIGHT] Link 'Todas as guias' encontrado com ID: {link_id}")
                                # Em vez de esperar popup, vamos apenas clicar no link
                                try:
                                    # Tenta clicar e gerar o PDF da página resultante
                                    todas_guias_link.click()
                                    print("[PLAYWRIGHT] Clique no link 'Todas as guias' realizado")
                                    
                                    # Aguarda carregamento após o clique
                                    page.wait_for_timeout(3000)
                                    
                                    # Tenta gerar PDF
                                    try:
                                        page.pdf(path=pdf_path)
                                        # Verifica se o arquivo foi gerado com tamanho adequado
                                        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
                                            print(f"[PLAYWRIGHT] PDF gerado com sucesso após clicar em 'Todas as guias': {pdf_path}")
                                            pdf_generated = True
                                            return pdf_path
                                    except Exception as pdf_error:
                                        print(f"[PLAYWRIGHT] Erro ao gerar PDF após clicar em 'Todas as guias': {str(pdf_error)}")
                                except Exception as click_error:
                                    print(f"[PLAYWRIGHT] Erro ao clicar no link 'Todas as guias': {str(click_error)}")
                    except Exception as e:
                        print(f"[PLAYWRIGHT] Erro ao tentar encontrar e clicar no link 'Todas as guias': {str(e)}")
                    
                    # Se não conseguiu pela abordagem principal, tenta alternativas
                    if not pdf_generated:
                        # Abordagem 1: Tentar clicar no link da guia para abrir detalhes
                        print("[PLAYWRIGHT] Tentando abrir a página de detalhes da guia...")
                        try:
                            # Localiza o link da guia na segunda coluna
                            guide_link = guide_row.query_selector('td:nth-child(2) a')
                            
                            if guide_link:
                                # Tenta primeiro capturar uma nova página se abrir
                                try:
                                    with page.expect_popup(timeout=5000) as popup_info:
                                        guide_link.click()
                                    
                                    # Se abriu popup, captura a página
                                    details_page = popup_info.value
                                    details_page.wait_for_load_state("networkidle")
                                    
                                    # Tenta gerar PDF dessa página de detalhes
                                    print("[PLAYWRIGHT] Gerando PDF da página de detalhes (popup)...")
                                    details_page.pdf(path=pdf_path)
                                    popup_opened = True
                                    
                                    # Verifica se o arquivo foi gerado com tamanho adequado
                                    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
                                        print(f"[PLAYWRIGHT] PDF gerado com sucesso da página de detalhes: {pdf_path}")
                                        pdf_generated = True
                                        return pdf_path
                                except Exception as popup_error:
                                    print(f"[PLAYWRIGHT] Não foi possível capturar popup: {str(popup_error)}")
                                    
                                    # Se não abriu popup, clica normalmente e usa a página atual
                                    try:
                                        guide_link.click()
                                        print("[PLAYWRIGHT] Clique na guia realizado, aguardando carregamento...")
                                        page.wait_for_load_state("networkidle")
                                        page.wait_for_timeout(2000)
                                        
                                        # Tenta gerar PDF da página atual
                                        print("[PLAYWRIGHT] Gerando PDF da página atual após clicar na guia...")
                                        page.pdf(path=pdf_path)
                                        
                                        # Verifica se o arquivo foi gerado com tamanho adequado
                                        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
                                            print(f"[PLAYWRIGHT] PDF gerado com sucesso: {pdf_path}")
                                            pdf_generated = True
                                            return pdf_path
                                    except Exception as click_error:
                                        print(f"[PLAYWRIGHT] Erro ao clicar/gerar PDF da guia: {str(click_error)}")
                        except Exception as e:
                            print(f"[PLAYWRIGHT] Erro geral ao tentar abrir detalhes da guia: {str(e)}")
                        
                        # Abordagem 2: Se ainda não conseguiu, tenta abrir qualquer link relacionado a impressão
                        if not pdf_generated:
                            print("[PLAYWRIGHT] Tentando encontrar e clicar em qualquer link de impressão...")
                            
                            try:
                                # Procura por links relacionados a impressão em toda a página
                                print_links = page.query_selector_all('a[id*="print"], a:text("imprimir"), a:text("Todas"), a:text("Guia")')
                                
                                for link in print_links:
                                    if pdf_generated:
                                        break
                                        
                                    try:
                                        # Tenta clicar no link e gerar PDF da página resultante
                                        print(f"[PLAYWRIGHT] Tentando link: {link.inner_text().strip()}")
                                        link.click()
                                        page.wait_for_timeout(2000)
                                        
                                        # Tenta gerar PDF
                                        try:
                                            print("[PLAYWRIGHT] Gerando PDF após clicar em link...")
                                            page.pdf(path=pdf_path)
                                            
                                            # Verifica se o arquivo foi gerado com tamanho adequado
                                            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
                                                print(f"[PLAYWRIGHT] PDF gerado com sucesso: {pdf_path}")
                                                pdf_generated = True
                                                return pdf_path
                                            else:
                                                print("[PLAYWRIGHT] PDF gerado, mas com tamanho inadequado")
                                        except Exception as pdf_error:
                                            print(f"[PLAYWRIGHT] Erro ao gerar PDF: {str(pdf_error)}")
                                    except Exception as click_error:
                                        print(f"[PLAYWRIGHT] Erro ao clicar no link: {str(click_error)}")
                            except Exception as e:
                                print(f"[PLAYWRIGHT] Erro ao procurar links de impressão: {str(e)}")
                        
                        # Abordagem 3: Último recurso - capturar a página atual
                        if not pdf_generated:
                            print("[PLAYWRIGHT] Último recurso: gerando PDF da página atual...")
                            try:
                                page.pdf(path=pdf_path)
                                
                                # Verifica se o arquivo foi gerado com tamanho adequado
                                if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 5000:
                                    print(f"[PLAYWRIGHT] PDF gerado com sucesso da página atual: {pdf_path}")
                                    pdf_generated = True
                                    return pdf_path
                                else:
                                    print("[PLAYWRIGHT] PDF gerado da página atual, mas com tamanho inadequado")
                            except Exception as pdf_error:
                                print(f"[PLAYWRIGHT] Erro ao gerar PDF da página atual: {str(pdf_error)}")
                        
                        # Se chegou aqui e não foi retornado, significa que não conseguiu gerar o PDF
                        return None
                
                if not guide_found:
                    print(f"[PLAYWRIGHT] Guia {numero_guia} não encontrada em nenhuma página")
                    return None
                
            except Exception as e:
                print(f"[PLAYWRIGHT] Erro durante o processo: {str(e)}")
                traceback.print_exc()
                return None
                
            finally:
                # Fecha o navegador
                browser.close()
                print("[PLAYWRIGHT] Navegador fechado")
        
        print("[PLAYWRIGHT] Nenhum arquivo PDF encontrado após tentativas")
        return None
    
    except Exception as e:
        print(f"[PLAYWRIGHT] Erro geral: {str(e)}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Baixa o PDF de uma guia específica da Unimed')
    parser.add_argument('--numero_guia', type=str, required=True, help='Número da guia')
    parser.add_argument('--data_atendimento', type=str, help='Data do atendimento no formato dd/mm/aaaa')
    
    args = parser.parse_args()
    
    # Se a data não for fornecida, usa a data atual
    if not args.data_atendimento:
        args.data_atendimento = datetime.now().strftime("%d/%m/%Y")
    
    # Executa o download
    pdf_path = baixar_pdf_guia(args.numero_guia, args.data_atendimento)
    
    if pdf_path:
        print(f"\nPDF baixado com sucesso: {pdf_path}")
        exit(0)
    else:
        print("\nFalha ao baixar o PDF")
        exit(1) 