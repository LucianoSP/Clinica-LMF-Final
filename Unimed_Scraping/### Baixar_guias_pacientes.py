#!/usr/bin/env python3
"""
Script para extrair números de guias do sistema da Unimed.

Este script automatiza o processo de login no sistema da Unimed, navegação até a 
página de exames finalizados, filtragem por nome de paciente e extração dos números 
de guias associados. As guias são salvas em arquivos CSV para uso posterior.

Funcionalidades:
- Login automático no sistema da Unimed
- Navegação para a seção de Exames Finalizados
- Filtragem por nome de paciente e intervalo de datas
- Extração dos números de guias de todas as páginas de resultados
- Salvamento dos números das guias em arquivos CSV organizados

Requisitos:
- Python 3.6+
- Selenium
- ChromeDriver compatível com a versão do Chrome instalada

Uso básico:
    extrator = UnimedGuiasExtractor("seu_usuario", "sua_senha")
    guias, arquivo_csv = extrator.extrair_guias_paciente("NOME DO PACIENTE")
"""

import time
import os
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class UnimedGuiasExtractor:
    def __init__(self, usuario, senha, download_dir=None, headless=False):
        """
        Inicializa o extrator com credenciais e configurações
        
        Args:
            usuario: ID de usuário para login
            senha: Senha para login
            download_dir: Diretório para salvar os arquivos CSV com os números das guias
            headless: Se True, executa o navegador em modo headless (sem interface visual)
        """
        self.usuario = usuario
        self.senha = senha
        self.headless = headless
        
        # Configura o diretório de download
        if download_dir is None:
            self.download_dir = os.path.join(os.path.expanduser('~'), 'Downloads', 'unimed_guias')
        else:
            self.download_dir = download_dir
            
        # Cria o diretório se não existir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
        # URL de login
        self.url_login = "https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do"
        
        # Configura as opções do Chrome
        self.options = Options()
        self.options.add_experimental_option('prefs', {
            'download.default_directory': self.download_dir,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'plugins.always_open_pdf_externally': True
        })
        
        # Configurações adicionais para melhorar a estabilidade
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-features=NetworkService')
        self.options.add_argument('--window-size=1920x1080')
        self.options.add_argument('--disable-features=VizDisplayCompositor')
        self.options.add_argument('--disable-extensions')
        
        # Configuração de user-agent para evitar problemas de detecção
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        
        # Configuração para modo headless se solicitado
        if headless:
            self.options.add_argument('--headless=new')
        
        # Inicialmente, o driver é None
        self.driver = None
    
    def iniciar_navegador(self):
        """Inicializa o navegador Chrome com as opções configuradas"""
        print("Iniciando o navegador...")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.maximize_window()
        
    def fazer_login(self, max_tentativas=3):
        """
        Tenta fazer login no sistema da Unimed
        
        Args:
            max_tentativas: Número máximo de tentativas de login
            
        Returns:
            bool: True se o login foi bem-sucedido, False caso contrário
        """
        if self.driver is None:
            self.iniciar_navegador()
            
        print(f"Acessando a URL de login: {self.url_login}")
        
        for tentativa in range(max_tentativas):
            try:
                print(f"Tentativa de login {tentativa + 1}/{max_tentativas}")
                self.driver.get(self.url_login)
                
                # Aguarda a página carregar
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "login"))
                )
                
                # Preenche o formulário de login
                print("Preenchendo credenciais...")
                self.driver.find_element(By.NAME, "login").send_keys(self.usuario)
                self.driver.find_element(By.NAME, "passwordTemp").send_keys(self.senha)
                
                # Verifica se há captcha e alerta o usuário
                if "g-recaptcha" in self.driver.page_source and \
                   not self.driver.find_element(By.CLASS_NAME, "g-recaptcha").get_attribute("data-sitekey") == "key":
                    print("Detectado CAPTCHA! Aguardando 15 segundos para preenchimento manual...")
                    time.sleep(15)  # Dá tempo para o usuário resolver o captcha manualmente
                
                # Clica no botão de login
                print("Clicando no botão de login...")
                self.driver.find_element(By.NAME, "Button_DoLogin").click()
                
                # Aguarda o redirecionamento ou mensagem de erro
                time.sleep(2)
                
                # Verifica se o login foi bem-sucedido
                if "Usuário ou Senha inválidos" in self.driver.page_source:
                    print("Erro: Usuário ou senha inválidos")
                    continue  # Tenta novamente
                    
                # Verifica se estamos na página principal após o login
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "mainMenu"))
                    )
                    print("Login bem-sucedido!")
                    return True
                except TimeoutException:
                    if tentativa == max_tentativas - 1:
                        print("Não foi possível confirmar o login bem-sucedido.")
                        return False
                        
            except Exception as e:
                print(f"Erro ao tentar fazer login: {str(e)}")
                if tentativa == max_tentativas - 1:
                    print("Número máximo de tentativas alcançado.")
                    return False
                    
        return False
    
    def navegar_para_exames_finalizados(self):
        """Navega para a página de exames finalizados"""
        try:
            print("Navegando para a página de exames finalizados...")
            
            # Aguarda um pouco para a página carregar completamente
            time.sleep(3)
            
            # Tenta várias estratégias para encontrar o link
            try:
                # Primeira tentativa: por XPath mais preciso
                exames_finalizados = self.driver.find_element(By.XPATH, "//div[contains(@class, 'MagnetoSubMenuTittle') and contains(text(), 'Exames Finalizados')]/ancestor::a")
                print("Link localizado via XPath específico")
            except NoSuchElementException:
                try:
                    # Segunda tentativa: por texto parcial
                    exames_finalizados = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Exames Finalizados")
                    print("Link localizado via texto parcial")
                except NoSuchElementException:
                    try:
                        # Terceira tentativa: navegar diretamente via URL
                        print("Tentando navegar diretamente via URL...")
                        self.driver.get("https://sgucard.unimedgoiania.coop.br/cmagnet/exames/sadt/finalizadas.do")
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.NAME, "s_dt_ini"))
                        )
                        print("Navegação direta bem-sucedida!")
                        return True
                    except Exception as e:
                        raise Exception(f"Não foi possível encontrar o link ou navegar diretamente: {str(e)}")
            
            # Clica no link se encontrado por um dos métodos
            print("Clicando no link para Exames Finalizados...")
            exames_finalizados.click()
            
            # Aguarda a página carregar
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "s_dt_ini"))
            )
            print("Página de exames finalizados carregada com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao navegar para a página de exames finalizados: {str(e)}")
            # Tentativa de último recurso
            try:
                print("Tentando navegar diretamente como último recurso...")
                self.driver.get("https://sgucard.unimedgoiania.coop.br/cmagnet/exames/sadt/finalizadas.do")
                time.sleep(5)  # Espera mais tempo para garantir o carregamento
                if "finalizadas" in self.driver.current_url.lower():
                    print("Navegação direta de emergência bem-sucedida!")
                    return True
                return False
            except Exception as e2:
                print(f"Falha na navegação de emergência: {str(e2)}")
                return False
    
    def filtrar_por_paciente(self, nome_paciente, data_inicial="01/01/2025", data_final=""):
        """
        Filtra os exames finalizados por nome de paciente e período
        
        Args:
            nome_paciente: Nome do paciente para filtrar
            data_inicial: Data inicial para filtrar (formato: dd/mm/yyyy)
            data_final: Data final para filtrar (formato: dd/mm/yyyy)
            
        Returns:
            bool: True se o filtro foi aplicado com sucesso, False caso contrário
        """
        try:
            print(f"Aplicando filtro por paciente: {nome_paciente} e período: {data_inicial} até {data_final}")
            
            # Preenche a data inicial
            campo_data_inicial = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "s_dt_ini"))
            )
            campo_data_inicial.clear()
            campo_data_inicial.send_keys(data_inicial)
            
            # Preenche a data final (se fornecida)
            campo_data_final = self.driver.find_element(By.NAME, "s_dt_fim")
            campo_data_final.clear()
            if data_final:
                campo_data_final.send_keys(data_final)
            
            # Preenche o nome do paciente
            campo_nome = self.driver.find_element(By.NAME, "s_nm_benef")
            campo_nome.clear()
            campo_nome.send_keys(nome_paciente)
            
            # Clica no botão de filtrar
            botao_filtrar = self.driver.find_element(By.NAME, "Button_FIltro")
            botao_filtrar.click()
            
            # Aguarda o resultado do filtro
            time.sleep(3)
            
            print("Filtro aplicado com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao aplicar o filtro por paciente: {str(e)}")
            return False
    
    def extrair_numeros_guias(self):
        """
        Extrai os números das guias da tabela de resultados
        
        Returns:
            list: Lista com os números das guias encontradas
        """
        try:
            print("Extraindo números das guias...")
            
            # Aguarda a tabela de resultados com timeout maior
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "MagnetoFormTABLE"))
            )
            
            # Dá um tempo extra para carregar todos os dados
            time.sleep(3)
            
            # Extrai os números das guias
            numeros_guias = []
            
            # Tenta diferentes estratégias para extrair os números de guias
            try:
                # Estratégia 1: Usando JavaScript para extração direta
                print("Tentando extração via JavaScript...")
                script = """
                    const guias = [];
                    const linhas = document.querySelectorAll('table.MagnetoFormTABLE tr');
                    for (let i = 1; i < linhas.length; i++) {
                        const celulas = linhas[i].querySelectorAll('td');
                        if (celulas.length >= 2) {
                            const numeroGuia = celulas[1].textContent.trim();
                            if (numeroGuia && numeroGuia !== 'Nº Guia' && /^\\d+$/.test(numeroGuia)) {
                                guias.push(numeroGuia);
                            }
                        }
                    }
                    return guias;
                """
                numeros_guias = self.driver.execute_script(script)
                if numeros_guias and len(numeros_guias) > 0:
                    print(f"Extração via JavaScript bem-sucedida: {len(numeros_guias)} guias encontradas")
                    return numeros_guias
            except Exception as js_error:
                print(f"Falha na extração via JavaScript: {str(js_error)}")
            
            print("Tentando extração via Selenium...")
            # Estratégia 2: Usando Selenium normalmente
            # Obtém todas as linhas da tabela (exceto o cabeçalho e rodapé)
            linhas = self.driver.find_elements(By.CSS_SELECTOR, "table.MagnetoFormTABLE tr")
            
            for i in range(1, len(linhas) - 1):  # Ignora o cabeçalho (0) e rodapé (último)
                try:
                    colunas = linhas[i].find_elements(By.TAG_NAME, "td")
                    if len(colunas) >= 2:
                        numero_guia = colunas[1].text.strip()
                        if numero_guia and numero_guia != "Nº Guia" and numero_guia.isdigit():
                            numeros_guias.append(numero_guia)
                except Exception as e:
                    print(f"Erro ao processar linha {i}: {str(e)}")
                    continue
            
            # Se ainda não funcionou, tenta uma estratégia mais específica
            if not numeros_guias:
                print("Tentando estratégia alternativa...")
                try:
                    # Procura especificamente por células na segunda coluna
                    celulas_guia = self.driver.find_elements(By.XPATH, "//table[contains(@class, 'MagnetoFormTABLE')]/tbody/tr/td[2]")
                    for celula in celulas_guia:
                        numero = celula.text.strip()
                        if numero and numero.isdigit():
                            numeros_guias.append(numero)
                except Exception as e3:
                    print(f"Falha na estratégia alternativa: {str(e3)}")
            
            print(f"Encontradas {len(numeros_guias)} guias!")
            return numeros_guias
        except Exception as e:
            print(f"Erro ao extrair números das guias: {str(e)}")
            return []
    
    def salvar_guias_em_csv(self, numeros_guias, nome_paciente):
        """
        Salva os números das guias em um arquivo CSV
        
        Args:
            numeros_guias: Lista com os números das guias
            nome_paciente: Nome do paciente para usar no nome do arquivo
            
        Returns:
            str: Caminho do arquivo CSV salvo
        """
        if not numeros_guias:
            print("Nenhuma guia para salvar.")
            return None
            
        try:
            # Cria um nome de arquivo baseado no nome do paciente e data atual
            nome_arquivo = f"{nome_paciente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            caminho_arquivo = os.path.join(self.download_dir, nome_arquivo)
            
            # Salva os números das guias no arquivo CSV
            with open(caminho_arquivo, 'w', newline='') as arquivo:
                writer = csv.writer(arquivo)
                writer.writerow(['Número da Guia'])  # Cabeçalho
                for numero in numeros_guias:
                    writer.writerow([numero])
            
            print(f"Guias salvas com sucesso no arquivo: {caminho_arquivo}")
            return caminho_arquivo
        except Exception as e:
            print(f"Erro ao salvar guias em CSV: {str(e)}")
            return None
    
    def fechar_navegador(self):
        """Fecha o navegador e libera os recursos"""
        if self.driver:
            print("Fechando o navegador...")
            self.driver.quit()
            self.driver = None
    
    def navegar_proxima_pagina(self):
        """
        Navega para a próxima página de resultados se disponível
        
        Returns:
            bool: True se navegou para a próxima página, False se não existir próxima página
        """
        try:
            # Verifica se existe o link "Próxima"
            link_proxima = self.driver.find_element(By.XPATH, "//a[text()='Próxima']")
            
            # Verifica se o link está ativo (não desabilitado)
            classe_pai = link_proxima.find_element(By.XPATH, "..").get_attribute("class")
            if "Inactive" in classe_pai:
                print("Não há mais páginas para navegar.")
                return False
                
            print("Navegando para a próxima página...")
            link_proxima.click()
            
            # Aguarda o carregamento da nova página
            time.sleep(3)
            
            print("Próxima página carregada.")
            return True
        except NoSuchElementException:
            print("Link 'Próxima' não encontrado. Provavelmente é a última página.")
            return False
        except Exception as e:
            print(f"Erro ao navegar para a próxima página: {str(e)}")
            return False
    
    def extrair_guias_paciente(self, nome_paciente, data_inicial="01/01/2025", data_final=""):
        """
        Processo completo para extrair as guias de um paciente
        
        Args:
            nome_paciente: Nome do paciente para filtrar
            data_inicial: Data inicial para filtrar (formato: dd/mm/yyyy)
            data_final: Data final para filtrar (formato: dd/mm/yyyy)
            
        Returns:
            tuple: (lista de números de guias, caminho do arquivo CSV)
        """
        try:
            # Faz login
            if not self.fazer_login():
                raise Exception("Falha ao fazer login.")
            
            # Navega para exames finalizados
            if not self.navegar_para_exames_finalizados():
                raise Exception("Falha ao navegar para exames finalizados.")
            
            # Aplica o filtro por paciente
            if not self.filtrar_por_paciente(nome_paciente, data_inicial, data_final):
                raise Exception("Falha ao aplicar filtro por paciente.")
            
            # Extrai os números das guias da primeira página
            todos_numeros_guias = self.extrair_numeros_guias()
            
            # Verifica se há mais páginas e extrai delas também
            pagina = 1
            max_paginas = 20  # Evita loop infinito
            
            while self.navegar_proxima_pagina() and pagina < max_paginas:
                pagina += 1
                print(f"Processando página {pagina}...")
                numeros_pagina_atual = self.extrair_numeros_guias()
                todos_numeros_guias.extend(numeros_pagina_atual)
                print(f"Total acumulado: {len(todos_numeros_guias)} guias")
            
            print(f"Extração concluída. Foram encontradas {len(todos_numeros_guias)} guias em {pagina} página(s).")
            
            # Salva as guias em CSV
            caminho_csv = self.salvar_guias_em_csv(todos_numeros_guias, nome_paciente)
            
            return todos_numeros_guias, caminho_csv
        except Exception as e:
            print(f"Erro durante a extração de guias: {str(e)}")
            raise e
        finally:
            # Garante que o navegador seja fechado mesmo se ocorrer uma exceção
            self.fechar_navegador()


# Exemplo de uso
if __name__ == "__main__":
    import argparse
    
    # Configuração do parser de argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Extrai números de guias de pacientes do sistema da Unimed.")
    parser.add_argument("--usuario", default="REC2209525", help="Usuário para login no sistema")
    parser.add_argument("--senha", default="UnimedAba2024@", help="Senha para login no sistema")
    parser.add_argument("--data-inicial", default="01/01/2025", help="Data inicial para filtro (formato: dd/mm/yyyy)")
    parser.add_argument("--data-final", default="", help="Data final para filtro (formato: dd/mm/yyyy)")
    parser.add_argument("--paciente", help="Nome do paciente para buscar (se não especificado, usa a lista)")
    parser.add_argument("--lista-pacientes", help="Caminho para arquivo com lista de pacientes (um por linha)")
    parser.add_argument("--headless", action="store_true", help="Executa o navegador em modo headless (sem interface visual)")
    
    args = parser.parse_args()
    
    # Lista de pacientes para processar
    pacientes = []
    
    # Se foi especificado um paciente via argumento, usa apenas ele
    if args.paciente:
        pacientes = [args.paciente]
    # Se foi especificado um arquivo com lista de pacientes, carrega essa lista
    elif args.lista_pacientes:
        try:
            with open(args.lista_pacientes, 'r', encoding='utf-8') as f:
                pacientes = [linha.strip() for linha in f if linha.strip()]
            print(f"Carregados {len(pacientes)} pacientes do arquivo {args.lista_pacientes}")
        except Exception as e:
            print(f"Erro ao carregar lista de pacientes: {str(e)}")
            pacientes = ["ARTUR ROSA E SILVA RAMOS"]  # Fallback para paciente padrão
    else:
        # Lista padrão com um paciente para exemplo
        pacientes = ["ARTUR ROSA E SILVA RAMOS"]
    
    # Resultados totais
    resultados = {}
    
    # Processa cada paciente
    for nome_paciente in pacientes:
        print(f"\n{'='*20} Processando paciente: {nome_paciente} {'='*20}")
        
        try:
            # Cria nova instância do extrator para cada paciente (para evitar problemas de sessão)
            extrator = UnimedGuiasExtractor(
                args.usuario, 
                args.senha, 
                headless=args.headless
            )
            
            # Extrai as guias
            numeros_guias, caminho_csv = extrator.extrair_guias_paciente(
                nome_paciente,
                data_inicial=args.data_inicial,
                data_final=args.data_final
            )
            
            # Armazena os resultados
            resultados[nome_paciente] = {
                'guias': numeros_guias,
                'csv': caminho_csv,
                'status': 'Sucesso'
            }
            
            print(f"\n----- RESULTADO PARA {nome_paciente} -----")
            print(f"Total de guias encontradas: {len(numeros_guias)}")
            
            if len(numeros_guias) > 0:
                print("Números das guias:")
                for i, numero in enumerate(numeros_guias[:10], 1):  # Mostra apenas as 10 primeiras para não sobrecarregar o console
                    print(f"{i}. {numero}")
                
                if len(numeros_guias) > 10:
                    print(f"... e mais {len(numeros_guias) - 10} guias")
            
            if caminho_csv:
                print(f"\nOs números das guias foram salvos em: {caminho_csv}")
                
        except Exception as e:
            print(f"Erro durante a extração de guias para {nome_paciente}: {str(e)}")
            resultados[nome_paciente] = {
                'guias': [],
                'csv': None,
                'status': f'Erro: {str(e)}'
            }
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO DE PROCESSAMENTO")
    print("="*80)
    
    for paciente, dados in resultados.items():
        status = dados['status']
        guias = len(dados['guias'])
        print(f"{paciente}: {status} - {guias} guias encontradas")
        
    print("="*80)
    print("Processamento concluído!")