from playwright.sync_api import sync_playwright
import os
import time
from datetime import datetime
import re
import shutil
from dotenv import load_dotenv

# Carrega variáveis do ambiente
load_dotenv()

# Credenciais da Unimed
UNIMED_USERNAME = os.getenv("UNIMED_USERNAME")
UNIMED_PASSWORD = os.getenv("UNIMED_PASSWORD")

def baixar_pdf_guia(numero_guia, data_filtro):
    """
    Função para acessar o site da Unimed e baixar o PDF de uma guia específica
    usando Playwright.
    
    Args:
        numero_guia (str): Número da guia para baixar o PDF
        data_filtro (str): Data no formato dd/mm/aaaa para filtrar
        
    Returns:
        str: Caminho para o arquivo PDF baixado ou None se falhar
    """
    print(f"Iniciando download do PDF para guia {numero_guia} com data {data_filtro}")
    
    # Prepara diretório para downloads
    pdf_dir = os.path.join(os.getcwd(), "guias_pdf")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Nome do arquivo PDF final
    pdf_filename = f"{numero_guia}_{data_filtro.replace('/', '_')}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    # Verifica se o PDF já existe
    if os.path.exists(pdf_path):
        print(f"PDF já existe em: {pdf_path}")
        return pdf_path
    
    # Registra os arquivos PDF que já existem para comparação posterior
    existing_pdfs_before = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    print(f"Arquivos PDF existentes antes do download: {len(existing_pdfs_before)}")
    
    with sync_playwright() as p:
        # Inicia o navegador
        browser = p.chromium.launch(headless=False)  # False para depuração, mude para True em produção
        context = browser.new_context(
            accept_downloads=True,
            # Configurações para garantir que PDFs sejam baixados, não abertos no navegador
            viewport={"width": 1920, "height": 1080}
        )
        
        # Configura o diretório de download
        context.set_default_timeout(60000)  # 60 segundos de timeout
        
        # Abre uma nova página
        page = context.new_page()
        
        try:
            # 1. Acessa a página de login
            print("Acessando página de login...")
            page.goto("https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do")
            page.wait_for_load_state("networkidle")
            
            # 2. Realiza o login
            print("Preenchendo credenciais...")
            page.fill("#login", UNIMED_USERNAME)
            page.fill("#passwordTemp", UNIMED_PASSWORD)
            page.click("#Button_DoLogin")
            print("Login realizado, aguardando carregamento da página...")
            
            # Aguarda a página carregar completamente
            page.wait_for_load_state("networkidle")
            
            # 3. Navega para a página de exames finalizados
            print("Navegando para exames finalizados...")
            page.click("css=td#centro_21 a")
            page.wait_for_load_state("networkidle")
            
            # 4. Preenche o filtro de data
            print(f"Filtrando por data: {data_filtro}")
            page.fill('input[name="s_dt_ini"]', data_filtro)
            page.fill('input[name="s_dt_fim"]', data_filtro)
            page.click('input[name="Button_FIltro"]')
            
            # Aguarda a tabela carregar
            page.wait_for_selector('#conteudo form table tbody')
            print("Tabela de guias carregada")
            
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
                        print(f"Guia {numero_guia} encontrada na tabela")
                        return row
                return None
            
            # Procura pela guia na página atual
            guide_row = find_guide_row()
            
            # Se não encontrou, verifica se há mais páginas
            if not guide_row:
                print("Guia não encontrada na primeira página, verificando próximas páginas...")
                
                # Loop para navegar por páginas adicionais
                next_page_available = True
                page_num = 1
                
                while next_page_available and not guide_row:
                    # Verifica se existe o botão de próxima página e está habilitado
                    next_button = page.query_selector('a:text("Próxima")')
                    
                    if next_button and "disabled" not in next_button.get_attribute("class") or "":
                        page_num += 1
                        print(f"Navegando para página {page_num}...")
                        next_button.click()
                        page.wait_for_load_state("networkidle")
                        
                        # Procura a guia na nova página
                        guide_row = find_guide_row()
                    else:
                        next_page_available = False
                        print("Não há mais páginas disponíveis")
            
            # Se encontrou a guia, procede com o download
            if guide_row:
                guide_found = True
                print("Encontrou a linha da guia, buscando o botão de impressão...")
                
                # 6. Encontra e clica no ícone/link de impressão na última coluna
                last_cell = guide_row.query_selector('td:last-child')
                
                # Tenta encontrar o ícone de impressão ou qualquer link na última célula
                print_icon = last_cell.query_selector('img[src*="Print.gif"]')
                
                if print_icon:
                    print("Ícone de impressão encontrado")
                    print_icon.click()
                else:
                    print("Ícone de impressão não encontrado, tentando links...")
                    links = last_cell.query_selector_all('a')
                    
                    if links:
                        # Procura por link específico de impressão
                        print_link = None
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
                            raise Exception("Nenhum link encontrado na última célula")
                    else:
                        raise Exception("Nenhum link encontrado na última célula")
                
                # 7. Aguarda o menu popup aparecer
                print("Aguardando popup aparecer...")
                page.wait_for_timeout(3000)  # Espera 3 segundos para o popup aparecer
                
                # 8. Procura e clica no link "Todas as guias"
                link_clicked = False
                
                # Tenta localizar o div específico com ID subpGuiaXXXXX
                div_id = f"subpGuia{numero_guia}"
                popup_div = page.query_selector(f"#{div_id}")
                
                if popup_div:
                    print(f"Div {div_id} encontrado!")
                    
                    # Procura o link específico dentro do div
                    link_id = f"print_todas_guias_{numero_guia}"
                    todas_guias_link = popup_div.query_selector(f"#{link_id}")
                    
                    if todas_guias_link:
                        print(f"Link 'Todas as guias' encontrado com ID: {link_id}")
                        
                        # Exibe informações sobre o link
                        print(f"Texto do link: {todas_guias_link.inner_text()}")
                        print(f"href: {todas_guias_link.get_attribute('href')}")
                        
                        # Clica no link
                        todas_guias_link.click()
                        link_clicked = True
                        print("Link clicado com sucesso")
                
                # Se não conseguiu pela abordagem principal, tenta alternativas
                if not link_clicked:
                    print("Link não encontrado pelo método principal, tentando alternativas...")
                    
                    # Procura por qualquer div que possa conter o menu
                    popup_divs = page.query_selector_all('div[class*="guiaBarLeft"], div[id^="subp"]')
                    
                    if popup_divs:
                        print(f"Encontrados {len(popup_divs)} divs popup potenciais")
                        
                        for div in popup_divs:
                            if link_clicked:
                                break
                                
                            div_id = div.get_attribute('id')
                            print(f"Verificando div: {div_id}")
                            
                            # Procura links dentro do div
                            links = div.query_selector_all('a')
                            
                            for link in links:
                                link_text = link.inner_text().strip()
                                link_id = link.get_attribute('id')
                                link_href = link.get_attribute('href') or ""
                                
                                # Verifica se o link parece ser o correto
                                if (link_text == "Todas as guias" or 
                                    (link_id and link_id == f"print_todas_guias_{numero_guia}") or
                                    "todas" in link_text.lower()):
                                    
                                    print(f"Link potencial encontrado: text='{link_text}', id='{link_id}'")
                                    
                                    # Clica no link
                                    link.click()
                                    link_clicked = True
                                    print("Link clicado com sucesso")
                                    break
                    
                    # Se ainda não encontrou, busca em toda a página
                    if not link_clicked:
                        print("Buscando link em toda a página...")
                        all_links = page.query_selector_all('a')
                        
                        for link in all_links:
                            link_text = link.inner_text().strip()
                            link_id = link.get_attribute('id') or ""
                            
                            if link_text == "Todas as guias" or "print_todas_guias" in link_id:
                                print(f"Link encontrado em toda a página: {link_id} - {link_text}")
                                link.click()
                                link_clicked = True
                                print("Link clicado com sucesso")
                                break
                
                # 9. Verifica se conseguiu clicar em algum link
                if not link_clicked:
                    print("ALERTA: Não foi possível encontrar ou clicar no link 'Todas as guias'")
                    raise Exception("Não foi possível encontrar o link para download")
                
                # 10. Aguarda o download ser iniciado e completado
                print("Aguardando download do PDF...")
                
                # O Playwright não tem uma forma direta de esperar pelo download, então precisamos
                # verificar o diretório periodicamente
                timeout = 60  # 60 segundos de timeout
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    time.sleep(1)
                    
                    # Verifica se o arquivo esperado existe
                    if os.path.exists(pdf_path):
                        print(f"PDF baixado com sucesso: {pdf_path}")
                        return pdf_path
                    
                    # Verifica se apareceu algum novo PDF no diretório
                    current_pdfs = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
                    new_pdfs = current_pdfs - existing_pdfs_before
                    
                    if new_pdfs:
                        most_recent_pdf = max([os.path.join(pdf_dir, f) for f in new_pdfs], key=os.path.getctime)
                        print(f"Novo PDF detectado: {os.path.basename(most_recent_pdf)}")
                        
                        # Verifica se o arquivo tem um tamanho razoável
                        if os.path.getsize(most_recent_pdf) > 1000:  # pelo menos 1KB
                            print(f"Arquivo possui tamanho adequado: {os.path.getsize(most_recent_pdf)} bytes")
                            
                            # Renomeia para o nome esperado se for diferente
                            if most_recent_pdf != pdf_path:
                                try:
                                    shutil.copy(most_recent_pdf, pdf_path)
                                    print(f"Arquivo copiado para: {pdf_path}")
                                    return pdf_path
                                except Exception as copy_error:
                                    print(f"Erro ao copiar arquivo: {str(copy_error)}")
                                    # Se não conseguir copiar, usa o arquivo original
                                    return most_recent_pdf
                            else:
                                return pdf_path
                
                # Se chegou aqui, o timeout foi atingido
                print(f"Timeout atingido ({timeout}s) sem download completo")
                
                # Última verificação por novos PDFs
                current_pdfs = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
                new_pdfs = current_pdfs - existing_pdfs_before
                
                if new_pdfs:
                    most_recent_pdf = max([os.path.join(pdf_dir, f) for f in new_pdfs], key=os.path.getctime)
                    print(f"PDF encontrado após timeout: {os.path.basename(most_recent_pdf)}")
                    
                    # Verifica se o arquivo tem um tamanho razoável
                    if os.path.getsize(most_recent_pdf) > 1000:  # pelo menos 1KB
                        # Renomeia para o nome esperado
                        if most_recent_pdf != pdf_path:
                            try:
                                shutil.copy(most_recent_pdf, pdf_path)
                                print(f"Arquivo copiado para: {pdf_path}")
                                return pdf_path
                            except:
                                return most_recent_pdf
                        else:
                            return pdf_path
            
            if not guide_found:
                print(f"Guia {numero_guia} não encontrada em nenhuma página")
                return None
            
        except Exception as e:
            print(f"Erro durante o processo: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None
            
        finally:
            # Fecha o navegador
            browser.close()
            print("Navegador fechado")
    
    print("Nenhum arquivo PDF encontrado após timeout")
    return None

# Função para testar o script
def main():
    # Número da guia e data para testar
    numero_guia = "57386507"
    data_filtro = "19/03/2025"
    
    pdf_path = baixar_pdf_guia(numero_guia, data_filtro)
    
    if pdf_path:
        print(f"PDF baixado com sucesso em: {pdf_path}")
    else:
        print("Falha ao baixar o PDF")

if __name__ == "__main__":
    main() 