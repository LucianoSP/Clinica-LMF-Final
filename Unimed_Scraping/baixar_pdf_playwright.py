#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para baixar PDFs de guias da Unimed usando Playwright.
Este script pode ser usado independentemente ou chamado pelo captura_guias_via_pdf.py
"""

import os
import time
import re
import shutil
from datetime import datetime
import traceback
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def baixar_pdf_guia(numero_guia, data_atendimento):
    """
    Baixa o PDF de uma guia específica da Unimed usando Playwright
    
    Args:
        numero_guia (str): Número da guia a ser baixada
        data_atendimento (str): Data de atendimento no formato dd/mm/aaaa
        
    Returns:
        str: Caminho para o arquivo PDF baixado ou None se falhar
    """
    print(f"\n[PLAYWRIGHT] Iniciando download do PDF da guia {numero_guia} da data {data_atendimento}")
    
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
        # Inicia o navegador (usando o modo não-headless para facilitar debug)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080}
        )
        
        # Configura o diretório de download
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
                print("[PLAYWRIGHT] Credenciais não encontradas nas variáveis de ambiente")
                browser.close()
                return None
            
            page.fill("#login", username)
            page.fill("#passwordTemp", password)
            page.click("#Button_DoLogin")
            
            # Aguarda a página carregar completamente
            page.wait_for_load_state("networkidle")
            
            # 3. Navega para a página de exames finalizados
            print("[PLAYWRIGHT] Navegando para exames finalizados...")
            page.click("td#centro_21 a")
            page.wait_for_load_state("networkidle")
            
            # 4. Preenche o filtro de data
            print(f"[PLAYWRIGHT] Filtrando por data: {data_atendimento}")
            page.fill('input[name="s_dt_ini"]', data_atendimento)
            page.fill('input[name="s_dt_fim"]', data_atendimento)
            page.click('input[name="Button_FIltro"]')
            
            # Aguarda a tabela carregar
            page.wait_for_selector('#conteudo form table tbody')
            
            # 5. Localiza a linha da guia usando JavaScript
            print(f"[PLAYWRIGHT] Buscando a guia {numero_guia}...")
            
            # Função para encontrar a linha da guia em todas as páginas
            guide_found = False
            current_page = 1
            
            while not guide_found:
                # Verifica se a guia está na página atual
                row_found = page.evaluate(f'''() => {{
                    const rows = document.querySelectorAll('#conteudo form table tbody tr');
                    for (let i = 0; i < rows.length; i++) {{
                        // Pula a linha de cabeçalho
                        if (rows[i].querySelector('th')) continue;
                        
                        // Verifica se é a guia que procuramos
                        const guideCell = rows[i].querySelector('td:nth-child(2) a');
                        if (guideCell && guideCell.textContent.trim() === "{numero_guia}") {{
                            return i + 1; // Retorna o índice da linha (base 1)
                        }}
                    }}
                    return 0; // Não encontrou
                }}''')
                
                if row_found > 0:
                    guide_found = True
                    print(f"[PLAYWRIGHT] Guia {numero_guia} encontrada na página {current_page}, linha {row_found}")
                    
                    # 6. Clica no ícone de impressão na linha da guia
                    print("[PLAYWRIGHT] Clicando no ícone de impressão...")
                    
                    # Usando JavaScript para clicar no ícone/link de impressão na última coluna
                    clicked = page.evaluate(f'''(rowIndex) => {{
                        const rows = document.querySelectorAll('#conteudo form table tbody tr');
                        const row = rows[rowIndex];
                        const lastCell = row.querySelector('td:last-child');
                        
                        // Tenta encontrar o ícone de impressão
                        let printIcon = lastCell.querySelector('img[src*="Print.gif"]');
                        if (printIcon) {{
                            printIcon.click();
                            return "icon";
                        }}
                        
                        // Se não encontrar o ícone, tenta encontrar links
                        const links = lastCell.querySelectorAll('a');
                        if (links.length > 0) {{
                            // Procura por um link específico de impressão
                            for (let i = 0; i < links.length; i++) {{
                                const link = links[i];
                                if ((link.title && link.title.toLowerCase().includes("imprimir")) || 
                                    (link.onclick && link.onclick.toString().toLowerCase().includes("print"))) {{
                                    link.click();
                                    return "print-link";
                                }}
                            }}
                            
                            // Se não encontrou link específico, clica no primeiro link
                            links[0].click();
                            return "first-link";
                        }}
                        
                        return null; // Não encontrou nenhum elemento clicável
                    }}''', row_found)
                    
                    if clicked:
                        print(f"[PLAYWRIGHT] Elemento clicado: {clicked}")
                        
                        # 7. Aguarda o menu popup aparecer
                        page.wait_for_timeout(3000)  # Espera 3 segundos para o popup aparecer
                        
                        # 8. Procura e clica no link "Todas as guias" usando JavaScript
                        print("[PLAYWRIGHT] Procurando link 'Todas as guias'...")
                        link_clicked = page.evaluate(f'''() => {{
                            // Primeiro tenta encontrar o div específico
                            const divId = "subpGuia{numero_guia}";
                            const specificDiv = document.getElementById(divId);
                            
                            if (specificDiv) {{
                                console.log("Div específico encontrado:", divId);
                                
                                // Tenta encontrar o link específico
                                const linkId = "print_todas_guias_{numero_guia}";
                                const specificLink = document.getElementById(linkId);
                                
                                if (specificLink) {{
                                    console.log("Link específico encontrado:", linkId);
                                    specificLink.click();
                                    return "specific-link";
                                }}
                                
                                // Se não encontrou o link específico, procura por texto
                                const links = specificDiv.querySelectorAll('a');
                                for (let i = 0; i < links.length; i++) {{
                                    if (links[i].textContent.trim() === "Todas as guias") {{
                                        links[i].click();
                                        return "text-link-in-div";
                                    }}
                                }}
                            }}
                            
                            // Se não encontrou o div específico, procura qualquer div popup
                            const popupDivs = document.querySelectorAll('div[class*="guiaBarLeft"], div[id^="subp"]');
                            for (let i = 0; i < popupDivs.length; i++) {{
                                const links = popupDivs[i].querySelectorAll('a');
                                for (let j = 0; j < links.length; j++) {{
                                    const link = links[j];
                                    if (link.textContent.trim() === "Todas as guias" || 
                                        (link.id && link.id.includes("print_todas_guias")) ||
                                        link.textContent.toLowerCase().includes("todas")) {{
                                        link.click();
                                        return "popup-div-link";
                                    }}
                                }}
                            }}
                            
                            // Última tentativa: procura em toda a página
                            const allLinks = document.querySelectorAll('a');
                            for (let i = 0; i < allLinks.length; i++) {{
                                const link = allLinks[i];
                                if (link.textContent.trim() === "Todas as guias" || 
                                    (link.id && link.id.includes("print_todas_guias"))) {{
                                    link.click();
                                    return "page-wide-link";
                                }}
                            }}
                            
                            return null; // Não encontrou o link
                        }}''')
                        
                        if link_clicked:
                            print(f"[PLAYWRIGHT] Link 'Todas as guias' clicado: {link_clicked}")
                            
                            # 9. Aguarda o download ser iniciado e completado
                            print("[PLAYWRIGHT] Aguardando download do PDF...")
                            
                            # Verifica periodicamente o diretório
                            timeout = 60  # 60 segundos de timeout
                            start_time = time.time()
                            
                            while time.time() - start_time < timeout:
                                time.sleep(1)
                                
                                # Verifica se o arquivo esperado existe
                                if os.path.exists(pdf_path):
                                    print(f"[PLAYWRIGHT] PDF baixado com sucesso: {pdf_path}")
                                    browser.close()
                                    return pdf_path
                                
                                # Verifica se apareceu algum novo PDF no diretório
                                current_pdfs = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
                                new_pdfs = current_pdfs - existing_pdfs_before
                                
                                if new_pdfs:
                                    most_recent_pdf = max([os.path.join(pdf_dir, f) for f in new_pdfs], key=os.path.getctime)
                                    print(f"[PLAYWRIGHT] Novo PDF detectado: {os.path.basename(most_recent_pdf)}")
                                    
                                    # Verifica se o arquivo tem um tamanho razoável
                                    if os.path.getsize(most_recent_pdf) > 1000:  # pelo menos 1KB
                                        print(f"[PLAYWRIGHT] Arquivo possui tamanho adequado: {os.path.getsize(most_recent_pdf)} bytes")
                                        
                                        # Renomeia para o nome esperado se for diferente
                                        if most_recent_pdf != pdf_path:
                                            try:
                                                shutil.copy(most_recent_pdf, pdf_path)
                                                print(f"[PLAYWRIGHT] Arquivo copiado para: {pdf_path}")
                                                browser.close()
                                                return pdf_path
                                            except Exception as copy_error:
                                                print(f"[PLAYWRIGHT] Erro ao copiar arquivo: {str(copy_error)}")
                                                browser.close()
                                                return most_recent_pdf
                                        else:
                                            browser.close()
                                            return pdf_path
                            
                            print(f"[PLAYWRIGHT] Timeout atingido ({timeout}s) sem download completo")
                            
                            # Uma última verificação antes de desistir
                            current_pdfs = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
                            new_pdfs = current_pdfs - existing_pdfs_before
                            
                            if new_pdfs:
                                most_recent_pdf = max([os.path.join(pdf_dir, f) for f in new_pdfs], key=os.path.getctime)
                                print(f"[PLAYWRIGHT] PDF encontrado após timeout: {os.path.basename(most_recent_pdf)}")
                                
                                if os.path.getsize(most_recent_pdf) > 1000:
                                    if most_recent_pdf != pdf_path:
                                        try:
                                            shutil.copy(most_recent_pdf, pdf_path)
                                            browser.close()
                                            return pdf_path
                                        except:
                                            browser.close()
                                            return most_recent_pdf
                                    else:
                                        browser.close()
                                        return pdf_path
                        else:
                            print("[PLAYWRIGHT] Não foi possível clicar no link 'Todas as guias'")
                    else:
                        print("[PLAYWRIGHT] Não foi possível clicar no ícone/link de impressão")
                else:
                    # Tenta navegar para a próxima página
                    next_button = page.query_selector('a:text("Próxima")')
                    
                    if next_button and "disabled" not in (next_button.get_attribute("class") or ""):
                        current_page += 1
                        print(f"[PLAYWRIGHT] Navegando para a página {current_page}...")
                        next_button.click()
                        page.wait_for_load_state("networkidle")
                    else:
                        print("[PLAYWRIGHT] Guia não encontrada em nenhuma página")
                        break
            
            if not guide_found:
                print(f"[PLAYWRIGHT] Guia {numero_guia} não foi encontrada")
                
        except Exception as e:
            print(f"[PLAYWRIGHT] Erro durante o processo: {str(e)}")
            print(f"[PLAYWRIGHT] Traceback: {traceback.format_exc()}")
            
        finally:
            # Fecha o navegador
            browser.close()
            print("[PLAYWRIGHT] Navegador fechado")
    
    print("[PLAYWRIGHT] Falha ao baixar o PDF")
    return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Baixa PDF de guia da Unimed')
    parser.add_argument('--numero_guia', type=str, required=True, help='Número da guia')
    parser.add_argument('--data', type=str, required=True, help='Data de atendimento (dd/mm/aaaa)')
    
    args = parser.parse_args()
    
    pdf_path = baixar_pdf_guia(args.numero_guia, args.data)
    
    if pdf_path:
        print(f"PDF baixado com sucesso: {pdf_path}")
    else:
        print("Falha ao baixar o PDF")
        exit(1) 