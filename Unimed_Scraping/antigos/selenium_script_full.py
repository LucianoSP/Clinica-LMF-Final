from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import os
import time
import random
from datetime import datetime
import subprocess
import glob


class UnimedAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.captured_guides = []


    def setup_driver(self):
        """Configura e inicializa o Chrome com configurações para bypass do Cloudflare"""
        print("Iniciando setup do driver...")

        options = Options()

        # Configurações básicas
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')

        # Headers e cookies importantes para o Cloudflare
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36')
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Configurações adicionais para bypass
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            print("Tentando inicializar o Chrome...")
            service = Service(executable_path='/usr/local/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=options)

            # Remove flags de automação
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
            })

            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("Driver inicializado com sucesso")

            # Configura timeouts mais longos para o Cloudflare
            driver.set_page_load_timeout(60)
            driver.set_script_timeout(60)

            self.driver = driver
            self.wait = WebDriverWait(self.driver, 60)

            return self.driver

        except Exception as e:
            print(f"Erro ao inicializar driver: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def login(self, username: str, password: str):
        """Realiza login no sistema com tratamento para Cloudflare"""
        try:
            print("Preparando para acessar página de login...")

            # Primeiro acessa o domínio principal para pegar cookies do Cloudflare
            print("Acessando domínio principal...")
            self.driver.get("https://sgucard.unimedgoiania.coop.br")
            time.sleep(10)  # Aguarda Cloudflare processar

            # Configura headers adicionais
            self.driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                'headers': {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="132", "Chromium";v="132"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Upgrade-Insecure-Requests': '1'
                }
            })

            print("Cookies atuais:", self.driver.get_cookies())

            # Agora tenta acessar a página de login
            print("Acessando página de login...")
            self.driver.get("https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do")
            time.sleep(5)

            print(f"Título da página: {self.driver.title}")
            print("URL atual:", self.driver.current_url)

            # Salva screenshot para debug
            #self.driver.save_screenshot("/app/login_page.png")

            # Procura campos de login
            login_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            login_field.send_keys(username)

            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "passwordTemp"))
            )
            password_field.send_keys(password)

            # Clica no botão
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "Button_DoLogin"))
            )
            login_button.click()

            time.sleep(5)
            print("URL após tentativa de login:", self.driver.current_url)

            if "Login.do" not in self.driver.current_url:
                print("Login bem sucedido!")
                return True
            else:
                print("Login falhou - ainda na página de login")
                return False

        except Exception as e:
            print(f"Erro no login: {str(e)}")
            print("URL no momento do erro:", self.driver.current_url)
            return False


    def random_wait(self, min_seconds: float = 0.5, max_seconds: float = 1):
        """Tempos reduzidos para teste"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def navigate_to_finished_exams(self):
        """Navega para a tela de exames finalizados"""
        try:
            # Primeira tentativa: procura pelo link dentro do td
            finished_exams = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "td#centro_21 a"))
            )
            print("Encontrou o link de exames finalizados")

            # Clica no elemento
            finished_exams.click()
            print("Clicou no link de exames finalizados")

            # Aguarda um momento para a página carregar
            self.random_wait()

            return True

        except Exception as e:
            print(f"Erro ao navegar para exames finalizados: {str(e)}")
            return False

    def search_guide(self, guide_number: str):
        """Busca uma guia específica usando o formulário de busca"""
        try:
            # Localiza o campo de número da guia usando o XPath correto
            guide_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="filtro"]/table/tbody/tr[3]/td[4]/input')
                )
            )

            # Limpa o campo e insere o número da guia
            guide_input.clear()
            self.random_wait(0.5, 1)
            guide_input.send_keys(guide_number)
            print(f"Número da guia {guide_number} inserido no campo de busca")

            # Localiza e clica no botão Filtrar usando o XPath correto
            filter_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="filtro"]/table/tbody/tr[7]/td/input[3]')
                )
            )
            filter_button.click()
            print("Botão Filtrar clicado")

            # Aguarda a tabela de resultados carregar
            self.random_wait()

            return True

        except Exception as e:
            print(f"Erro ao buscar guia: {str(e)}")
            return False

    def search_and_get_guide_dates(self, guide_number: str):
        """Busca uma guia específica e captura suas datas de atendimento"""
        try:
            # Realiza a busca da guia
            if not self.search_guide(guide_number):
                raise Exception("Falha ao buscar a guia")

            guide_dates = []

            # Aguarda a tabela aparecer usando o XPath mais específico
            base_xpath = '//*[@id="conteudo"]/form[2]/table/tbody'
            table = self.wait.until(
                EC.presence_of_element_located((By.XPATH, base_xpath))
            )

            # Encontrar todas as linhas, começando da segunda
            rows = table.find_elements(By.TAG_NAME, "tr")

            for row in rows[1:]:  # Ignora o cabeçalho
                try:
                    date_element = row.find_element(By.XPATH, "./td[1]")
                    guide_number_element = row.find_element(By.XPATH, "./td[2]/a")

                    # Mantém o texto completo com data e hora
                    date_time = date_element.text.strip()

                    # Armazena informações estáveis para localizar o link novamente
                    guide_dates.append(
                        {
                            "date": date_time,  # Agora mantém a data e hora completas
                            "guide_number_text": guide_number_element.text.strip(),
                        }
                    )
                    print(f"Data e hora encontradas: {date_time}")

                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"Erro ao processar uma linha: {str(e)}")
                    continue

            print(
                f"Datas de atendimento encontradas para guia {guide_number}: {[d['date'] for d in guide_dates]}"
            )
            return guide_dates

        except Exception as e:
            print(f"Erro ao buscar guia: {str(e)}")
            return []

    def get_execution_dates(self, data_atendimento: str):
        """Captura as datas de execução da tabela de Procedimentos em Série para um atendimento específico."""
        execution_dates = []

        try:
            print("Tentando localizar a tabela de 'Data de Procedimentos em Série'...")

            # Aumenta o tempo de espera temporariamente para esta operação
            original_wait = self.wait
            self.wait = WebDriverWait(self.driver, 30)  # Aumenta para 30 segundos

            # Aguarda um pouco mais para a página carregar completamente
            self.random_wait(2, 3)

            # Tenta localizar a tabela pela classe específica e título
            try:
                table = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//table[contains(@class, 'MagnetoFormTABLE')]//td[contains(text(), 'Data de Procedimentos em Série')]/ancestor::table[1]",
                        )
                    )
                )
            except:
                print(
                    "Não foi possível encontrar a tabela pela classe, tentando método alternativo"
                )
                table = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="conteudo"]/table[6]')
                    )
                )

            print("Tabela localizada com sucesso.")

            # Encontra todas as células de dados (ignorando o cabeçalho e a linha de observação)
            try:
                data_cells = table.find_elements(By.CLASS_NAME, "MagnetoDataTD")
                print(f"Encontradas {len(data_cells)} células de dados")

                # Processa cada célula
                for cell in data_cells:
                    try:
                        text = cell.text.strip().replace(
                            "\xa0", " "
                        )  # Remove non-breaking spaces

                        # Ignora a célula de observação
                        if "Observação" in text:
                            continue

                        print(f"Processando célula com texto: '{text}'")

                        # Verifica se o texto contém " - " e extrai a parte após o hífen
                        if " - " in text:
                            parts = text.split(" - ", 1)
                            if len(parts) == 2:
                                date_part = parts[1].strip()
                                # Verifica se a parte extraída é uma data válida (dd/mm/yyyy)
                                if date_part and self._is_valid_date(date_part):
                                    execution_dates.append(date_part)
                                    print(f"Data válida encontrada: {date_part}")
                                else:
                                    if date_part:
                                        print(f"Data inválida encontrada: {date_part}")
                            else:
                                print(f"Formato inesperado na célula: '{text}'")
                        else:
                            print(f"Formato inesperado na célula: '{text}'")

                    except Exception as e:
                        print(f"Erro ao processar célula: {str(e)}")
                        continue

            except Exception as e:
                print(f"Erro ao processar a tabela: {str(e)}")
                return execution_dates

            # Restaura o tempo de espera original
            self.wait = original_wait

            print(f"Datas de execução encontradas: {execution_dates}")
            return execution_dates

        except Exception as e:
            print(f"Erro ao capturar datas de execução: {str(e)}")
            return []

    def _is_valid_date(self, date_str: str) -> bool:
        """Verifica se a string fornecida está no formato de data dd/mm/yyyy."""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def process_single_guide(self, guide_data: dict):
        """Processa uma única guia e extrai todos os dados necessários"""
        try:
            print(f"\nProcessando guia: {guide_data['guide_number']}")

            # Navega para a tela de exames finalizados
            if not self.navigate_to_finished_exams():
                raise Exception("Falha ao navegar para exames finalizados")

            # Busca e captura todas as datas de atendimento
            guide_dates = self.search_and_get_guide_dates(guide_data["guide_number"])
            if not guide_dates:
                print("Nenhuma data de atendimento encontrada")
                return []

            guide_details_list = []

            # Para cada data de atendimento, processa a guia
            for index, guide_date in enumerate(guide_dates, start=1):
                print(f"\nProcessando atendimento {index}: {guide_date['date']}")

                # Inicializa as variáveis antes do try
                carteira, nome = "", ""
                professional_name = professional_council = council_number = (
                    council_state
                ) = cbo_code = ""

                try:
                    # Localiza o link da guia usando XPath mais específico que inclui a data
                    guide_link = self.wait.until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                f"//tr[td[1][contains(text(), '{guide_date['date']}')]]//a[contains(text(), '{guide_date['guide_number_text']}')]",
                            )
                        )
                    )
                    guide_link.click()
                    self.random_wait(1, 2)  # Aumentado o tempo de espera
                    print("Guia aberta")

                    # Extrai dados da carteira e beneficiário
                    beneficiary_info = self.wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//*[@id='conteudo']/table[1]/tbody/tr[6]/td[1]/span",
                            )
                        )
                    ).text

                    # Separa carteira e nome do beneficiário
                    if " - " in beneficiary_info:
                        carteira, nome = beneficiary_info.split(" - ", 1)
                        carteira = carteira.strip()
                        nome = nome.strip()

                    # Extrai código do procedimento
                    procedure_code = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@id='conteudo']/table[4]/tbody/tr[2]/td[5]")
                        )
                    ).text
                    print("Código do procedimento capturado")

                    # Extrai dados do profissional
                    try:
                        professional_name = self.wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[4]",
                                )
                            )
                        ).text
                        professional_council = self.wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[5]",
                                )
                            )
                        ).text
                        council_number = self.wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[6]",
                                )
                            )
                        ).text
                        council_state = self.wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[7]",
                                )
                            )
                        ).text
                        cbo_code = self.wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[8]",
                                )
                            )
                        ).text
                        print("Dados do profissional capturados")
                    except Exception as e:
                        print(f"Erro ao capturar dados do profissional: {str(e)}")

                    # Captura datas de execução
                    execution_dates = self.get_execution_dates(guide_date["date"])
                    if execution_dates:
                        for exec_date in execution_dates:
                            guide_details = {
                                "carteira": carteira,
                                "nome_beneficiario": nome,
                                "codigo_procedimento": procedure_code,
                                "data_atendimento": guide_date["date"],
                                "data_execucao": exec_date,
                                "numero_guia": guide_data["guide_number"],
                                "biometria": "",
                                "nome_profissional": professional_name,
                                "conselho_profissional": professional_council,
                                "numero_conselho": council_number,
                                "uf_conselho": council_state,
                                "codigo_cbo": cbo_code,
                            }
                            guide_details_list.append(guide_details)
                    else:
                        # Se não encontrou datas de execução, salva com a data de atendimento
                        guide_details = {
                            "carteira": carteira,
                            "nome_beneficiario": nome,
                            "codigo_procedimento": procedure_code,
                            "data_atendimento": guide_date["date"],
                            "data_execucao": "",
                            "numero_guia": guide_data["guide_number"],
                            "biometria": "",
                            "nome_profissional": professional_name,
                            "conselho_profissional": professional_council,
                            "numero_conselho": council_number,
                            "uf_conselho": council_state,
                            "codigo_cbo": cbo_code,
                        }
                        guide_details_list.append(guide_details)

                    # Clica no botão "Voltar"
                    back_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="Btn_Voltar"]'))
                    )
                    back_button.click()
                    print("Botão 'Voltar' clicado")

                    # Aguarda a página de lista de guias carregar
                    try:
                        self.wait.until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    '//*[@id="filtro"]/table/tbody/tr[3]/td[4]/input',
                                )
                            )
                        )
                        print("Página de lista de guias carregada novamente.")
                    except TimeoutException:
                        print(
                            "Timeout: Página de lista de guias não carregou corretamente após clicar em 'Voltar'."
                        )
                        continue  # Pula para o próximo atendimento

                    self.random_wait()

                except Exception as e:
                    print(
                        f"Erro ao processar atendimento {guide_date['date']}: {str(e)}"
                    )
                    continue  # Continua com a próxima data

            return guide_details_list

        except Exception as e:
            print(f"Erro ao processar guia {guide_data['guide_number']}: {str(e)}")
            raise

    def process_guide(self, guide_number):
        """Processa um guia específico"""
        try:
            print(f"\nProcessando guia {guide_number}...")

            # Login
            print("Fazendo login...")
            self.login(guide_number, guide_number)
            print("Login realizado com sucesso!")

            # Pesquisar guia
            print(f"Pesquisando guia {guide_number}...")
            self.search_guide(guide_number)
            print("Pesquisa realizada!")

            # Extrair dados
            print("Extraindo dados...")
            data = self.extract_data()
            print("Dados extraídos com sucesso!")
            print(f"Dados encontrados: {data}")

            return data

        except Exception as e:
            print(f"Erro ao processar guia {guide_number}: {str(e)}")
            import traceback

            print("Traceback completo:")
            print(traceback.format_exc())
            return None

    def close(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            print("Navegador fechado")

    def capture_guides(self, start_date: str, end_date: str, max_guides: int = None):
        """Captura guias dentro do período especificado"""
        try:
            if not self.navigate_to_finished_exams():
                raise Exception("Falha ao navegar para exames finalizados")

            # Preenche datas
            start_date_field = self.wait.until(EC.presence_of_element_located((By.NAME, "s_dt_ini")))
            end_date_field = self.wait.until(EC.presence_of_element_located((By.NAME, "s_dt_fim")))

            start_date_field.clear()
            start_date_field.send_keys(start_date)

            end_date_field.clear()
            end_date_field.send_keys(end_date)

            # Aplica filtro
            filter_button = self.wait.until(EC.element_to_be_clickable((By.NAME, "Button_FIltro")))
            filter_button.click()
            self.random_wait()

            guides_processed = 0
            page_num = 1
            self.captured_guides = []  # Reseta a lista de guias capturadas

            while True:
                print(f"Processando página {page_num}")
                guides_table = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="conteudo"]/form[2]/table/tbody'))
                )
                rows = guides_table.find_elements(By.TAG_NAME, "tr")[1:]  # Ignora cabeçalho

                for row in rows:
                    try:
                        date_time = row.find_element(By.XPATH, "./td[1]").text.strip()
                        guide_number = row.find_element(By.XPATH, "./td[2]/a").text.strip()

                        if date_time and guide_number:
                            guides_processed += 1
                            self.captured_guides.append({
                                "date": date_time,
                                "guide_number_text": guide_number
                            })
                            print(f"Capturada guia {guide_number} com data/hora: {date_time}")

                            if max_guides and guides_processed >= max_guides:
                                return self.captured_guides

                    except Exception as e:
                        print(f"Erro ao processar linha: {str(e)}")
                        continue

                try:
                    next_button = self.driver.find_element(By.LINK_TEXT, "Próxima")
                    if "disabled" in next_button.get_attribute("class"):
                        break
                    next_button.click()
                    self.random_wait()
                    page_num += 1
                except NoSuchElementException:
                    break

            return self.captured_guides

        except Exception as e:
            print(f"Erro na captura de guias: {str(e)}")
            raise

    def fill_date_fields(self, start_date: str, end_date: str):
        """Preenche os campos de data inicial e final"""
        try:
            start_date_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "s_dt_ini"))
            )
            end_date_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "s_dt_fim"))
            )

            start_date_field.clear()
            start_date_field.send_keys(start_date)

            end_date_field.clear()
            end_date_field.send_keys(end_date)
            print("Datas preenchidas!")

        except Exception as e:
            print(f"Erro ao preencher campos de data: {str(e)}")

    def search_exams(self):
        """Realiza a pesquisa de exames"""
        try:
            filter_button = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "Button_FIltro"))
            )
            filter_button.click()
            print("Filtro aplicado!")
            self.random_wait()

        except Exception as e:
            print(f"Erro ao realizar pesquisa: {str(e)}")

    def extract_guide_numbers(self):
        """Extrai os números das guias"""
        try:
            guides_table = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="conteudo"]/form[2]/table/tbody')
                )
            )
            rows = guides_table.find_elements(By.TAG_NAME, "tr")[1:]

            guides = []
            for row in rows:
                try:
                    guide_number = row.find_element(By.XPATH, "./td[2]/a").text.strip()
                    guides.append(guide_number)

                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"Erro ao processar linha: {str(e)}")
                    continue

            return guides

        except Exception as e:
            print(f"Erro ao extrair números das guias: {str(e)}")
            return []


    def test_google(self):
        """Testa o acesso ao Google pra ver se tá ok"""
        try:
            print("Iniciando teste do Google...")
            self.driver.get("https://www.google.com")
            print(f"Página acessada: {self.driver.current_url}")
            print(f"Título da página: {self.driver.title}")

            return {
                "success": True,
                "url": self.driver.current_url,
                "title": self.driver.title
            }
        except Exception as e:
            print(f"Erro ao acessar Google: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


    def test_urls(self):
        """Testa acesso a diferentes URLs da Unimed"""
        results = []
        urls = [
            "https://www.unimedgoiania.coop.br",
            "https://sgucard.unimedgoiania.coop.br",
            "https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do"
        ]

        for url in urls:
            try:
                print(f"\nTentando acessar: {url}")
                self.driver.get(url)
                time.sleep(5)  # Aguarda 5 segundos

                result = {
                    "url": url,
                    "success": True,
                    "title": self.driver.title,
                    "current_url": self.driver.current_url
                }

                print(f"Sucesso! Título: {self.driver.title}")

            except Exception as e:
                print(f"Erro ao acessar {url}: {str(e)}")
                result = {
                    "url": url,
                    "success": False,
                    "error": str(e)
                }

            results.append(result)
            print(f"Resultado para {url}:", result)
````