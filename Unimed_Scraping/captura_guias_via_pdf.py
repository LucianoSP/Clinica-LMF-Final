from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel
import logging
import json
import argparse
from selenium.webdriver.common.action_chains import ActionChains
import PyPDF2
import io
import shutil
import tempfile
import os.path
import re
from typing import Dict


# Configurar logging
logging.basicConfig(level=logging.WARNING)  # Mudado de INFO para WARNING
logger = logging.getLogger(__name__)

# Desabilitar logs específicos do httpx e urllib3
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)

load_dotenv()

# Configurações Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Cliente Supabase
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class UnimedAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.captured_guides = []
        self.task_id = None  # Adicionar task_id como atributo da classe
        self.cache_file = "cache_unimed.json"
        self.cache_expiry_days = 7
        self.cache_cleanup_days = 30
        self.cache = self.load_cache()
        self.max_retry_attempts = 3  # Define máximo de tentativas

    ### 0.1 Configuração do cache ###
    def load_cache(self):
        """Carrega o cache do arquivo JSON com expiração"""
        default_cache = {
            "last_update": datetime.now().isoformat(),
            "carteirinhas": {},
            "pacientes": {},
            "procedimentos": {},
            "timestamps": {},  # Armazena timestamps de último uso
        }

        try:
            with open(self.cache_file, "r") as f:
                cache = json.load(f)

                # Verifica expiração do cache
                last_update = datetime.fromisoformat(
                    cache.get("last_update", "2000-01-01")
                )
                if (datetime.now() - last_update).days > self.cache_expiry_days:
                    print("Cache expirado. Criando novo cache.")
                    return default_cache

                # Garante que existe o dicionário de timestamps
                if "timestamps" not in cache:
                    cache["timestamps"] = {}

                print("Cache carregado com sucesso")
                return cache

        except (json.JSONDecodeError, FileNotFoundError):
            print("Criando novo cache")
            return default_cache

    def save_cache(self):
        """Salva o cache e remove entradas antigas"""
        try:
            # Atualiza timestamp geral do cache
            self.cache["last_update"] = datetime.now().isoformat()

            # Remove entradas não utilizadas há mais de 30 dias
            cutoff = datetime.now() - timedelta(days=self.cache_cleanup_days)

            for cache_type in ["carteirinhas", "pacientes", "procedimentos"]:
                keys_to_remove = []
                for key in list(
                    self.cache[cache_type].keys()
                ):  # Usa list() para evitar modificação durante iteração
                    timestamp_key = f"{cache_type}_{key}"
                    last_used = datetime.fromisoformat(
                        self.cache["timestamps"].get(timestamp_key, "2000-01-01")
                    )
                    if last_used < cutoff:
                        keys_to_remove.append(key)
                        if timestamp_key in self.cache["timestamps"]:
                            del self.cache["timestamps"][timestamp_key]

                # Remove as entradas antigas
                for key in keys_to_remove:
                    del self.cache[cache_type][key]

            # Salva o cache atualizado
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
            print("Cache salvo com sucesso")

        except Exception as e:
            print(f"Erro ao salvar cache: {str(e)}")

    def _update_cache_timestamp(self, cache_type: str, key: str):
        """Atualiza o timestamp de uso de uma entrada do cache"""
        try:
            timestamp_key = f"{cache_type}_{key}"
            self.cache["timestamps"][timestamp_key] = datetime.now().isoformat()
        except Exception as e:
            print(f"Erro ao atualizar timestamp do cache: {str(e)}")

    ### 0.2 Configuração do driver ###
    def setup_driver(self):
        """Configura e inicializa o Chrome em modo headless"""
        options = Options()
        #options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        
        # Configurar diretório de download
        pdf_dir = os.path.join(os.getcwd(), "guias_pdf")
        os.makedirs(pdf_dir, exist_ok=True)
        
        prefs = {
            "download.default_directory": pdf_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # Evita que o PDF abra no navegador
        }
        options.add_experimental_option("prefs", prefs)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)  # Aumentado para 20 segundos
        return self.driver

    ##### 1. Login #####
    def login(self, username: str, password: str):
        """Realiza login no sistema"""
        try:
            print("Iniciando processo de login...")
            self.driver.get("https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do")

            login_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            login_field.clear()
            self.random_typing(login_field, username)
            print("Usuário preenchido")

            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "passwordTemp"))
            )
            password_field.clear()
            self.random_typing(password_field, password)
            print("Senha preenchida")

            login_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "Button_DoLogin"))
            )
            self.random_wait(0.5, 1)
            login_button.click()
            print("Botão de login clicado")

            self.random_wait(2, 3)
            # self.driver.save_screenshot("login_result.png")
            # print("Login realizado e screenshot salvo")

            return True
        except Exception as e:
            print(f"Erro durante o login: {str(e)}")
            # self.driver.save_screenshot("login_error.png")
            return False

    ##### 2. Captura de guias #####
    def capture_guides(self, start_date=None, end_date=None, max_guides=None):
        """
        Captura as guias disponíveis na data especificada
        Args:
            start_date (str): Data inicial no formato dd/mm/aaaa
            end_date (str): Data final no formato dd/mm/aaaa
            max_guides (int): Número máximo de guias a processar
            
        Returns:
            None
        """
        try:
            print(f"Iniciando captura de guias entre {start_date} e {end_date}")
            
            if not start_date:
                start_date = datetime.now().strftime("%d/%m/%Y")  # Hoje
                
            if not end_date:
                end_date = start_date  # Mesmo dia, se não especificado
                
            # Valida as datas
            if not self.validate_date(start_date) or not self.validate_date(end_date):
                print("Formato de data inválido. Use dd/mm/aaaa")
                return
                
            # Navega para a tela de exames finalizados
            if not self.navigate_to_finished_exams():
                print("Falha ao navegar para a tela de exames finalizados")
                return
                
            # Percorre cada data no intervalo
            current_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date_obj = datetime.strptime(end_date, "%d/%m/%Y")
            
            guides_processed = 0
            
            while current_date <= end_date_obj:
                date_str = current_date.strftime("%d/%m/%Y")
                print(f"\nProcessando data: {date_str}")
                
                # Busca guias da data específica
                if not self.search_guide(None, date_filter=date_str):
                    print(f"Falha ao buscar guias para a data {date_str}")
                    current_date += timedelta(days=1)
                    continue
                
                # Coleta os números das guias na página
                guide_numbers = self.get_guide_numbers_from_page()
                
                if not guide_numbers:
                    print(f"Nenhuma guia encontrada para a data {date_str}")
                    current_date += timedelta(days=1)
                    continue
                    
                print(f"Encontradas {len(guide_numbers)} guias para a data {date_str}")
                
                # Limita o número de guias, se necessário
                if max_guides is not None:
                    guide_numbers = guide_numbers[:max_guides]
                    print(f"Processando apenas as primeiras {len(guide_numbers)} guias")
                
                # Salva as guias no Supabase para processamento
                for guide_number in guide_numbers:
                    try:
                        # Verifica se a guia já existe no banco
                        result = self.supabase.table('unimed_guias').select('*').eq('numero', guide_number).execute()
                        
                        if result.data:
                            print(f"Guia {guide_number} já existe no banco, verificando status")
                            
                            # Verifica o status da guia
                            guide_status = result.data[0].get('status')
                            
                            if guide_status == 'concluido':
                                print(f"Guia {guide_number} já foi processada com sucesso")
                                continue
                            elif guide_status in ['erro', 'pendente']:
                                print(f"Guia {guide_number} tem status '{guide_status}', tentando processar novamente")
                                
                                # Atualiza o status para 'pendente' se for 'erro'
                                if guide_status == 'erro':
                                    self.supabase.table('unimed_guias').update({"status": "pendente"}).eq("numero", guide_number).execute()
                            else:
                                print(f"Guia {guide_number} está em processamento, pulando")
                                continue
                        else:
                            # Insere nova guia no banco
                            new_guide = {
                                "numero": guide_number,
                                "data": date_str,
                                "status": "pendente",
                                "criado_em": datetime.now().isoformat()
                            }
                            
                            self.supabase.table('unimed_guias').insert(new_guide).execute()
                            print(f"Guia {guide_number} adicionada ao banco")
                            
                        # Processa a guia imediatamente
                        guide_data = self.process_single_guide(guide_number, date_str)
                        
                        if guide_data:
                            print(f"Guia {guide_number} processada com sucesso")
                            guides_processed += 1
                        else:
                            print(f"Falha ao processar guia {guide_number}")
                            
                        # Verifica se atingiu o limite de guias
                        if max_guides and guides_processed >= max_guides:
                            print(f"Limite de {max_guides} guias atingido")
                            return
                            
                    except Exception as e:
                        print(f"Erro ao processar guia {guide_number}: {str(e)}")
                        import traceback
                        print(f"Traceback: {traceback.format_exc()}")
                        continue
                
                # Avança para o próximo dia
                current_date += timedelta(days=1)
                
            print(f"\nCaptura de guias concluída. {guides_processed} guias processadas com sucesso.")
            
        except Exception as e:
            print(f"Erro durante a captura de guias: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    def get_guide_numbers_from_page(self):
        """
        Extrai os números das guias da página atual
        
        Returns:
            list: Lista de números de guias
        """
        try:
            guide_numbers = []
            
            # Espera a tabela carregar
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#conteudo form table tbody"))
            )
            
            # Encontra todas as linhas da tabela de guias
            rows = self.driver.find_elements(By.CSS_SELECTOR, "#conteudo form table tbody tr")
            
            for row in rows:
                # Ignora o cabeçalho
                if row.find_elements(By.TAG_NAME, "th"):
                    continue
                    
                # Extrai o número da guia da segunda coluna
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    guide_link = cells[1].find_elements(By.TAG_NAME, "a")
                    if guide_link:
                        guide_number = guide_link[0].text.strip()
                        if guide_number:
                            guide_numbers.append(guide_number)
            
            return guide_numbers
            
        except Exception as e:
            print(f"Erro ao extrair números das guias: {str(e)}")
            return []

    #### 3. Salva as guias capturadas na tabela guias_queue do Supabase ####
    def save_captured_guides(self):
        """Salva as guias capturadas na tabela guias_queue do Supabase"""
        if not supabase:
            print("Supabase não configurado corretamente.")
            return

        try:
            # Primeiro, busca guias antigas com status erro ou pendente
            old_guides = (
                supabase.table("guias_queue")
                .select("*")
                .in_("status", ["erro", "pending"])
                .execute()
            )
            if old_guides.data:
                print(
                    f"\nEncontradas {len(old_guides.data)} guias com erro ou pendentes de execuções anteriores"
                )
                # Atualiza o status das guias antigas para pending e associa ao task_id atual
                for guide in old_guides.data:
                    try:
                        supabase.table("guias_queue")\
                            .update({"status": "pending", "task_id": self.task_id})\
                            .eq("id", guide["id"])\
                            .execute()
                        print(f"Guia {guide['numero_guia']} com data {guide['data_atendimento_completa']} atualizada para processamento")
                    except Exception as e:
                        print(f"Erro ao atualizar guia antiga {guide['numero_guia']}: {str(e)}")

            # Inserir as guias na fila
            print(f"Inserindo {len(self.captured_guides)} guias na fila...")
            for guide in self.captured_guides:
                try:
                    # Verifica se a guia já existe na fila
                    existing_guide = supabase.table("guias_queue")\
                        .select("id")\
                        .eq("numero_guia", guide["guide_number"])\
                        .eq("data_atendimento_completa", guide["date"])\
                        .execute()
                        
                    if existing_guide.data and len(existing_guide.data) > 0:
                        print(f"Guia {guide['guide_number']} com data {guide['date']} já existe na fila. Atualizando status.")
                        # Atualiza o status para pending para garantir que será processada
                        supabase.table("guias_queue")\
                            .update({"status": "pending", "task_id": self.task_id})\
                            .eq("numero_guia", guide["guide_number"])\
                            .eq("data_atendimento_completa", guide["date"])\
                            .execute()
                        continue
                    
                    # Se não existe, insere nova guia
                    guide_data = {
                        "numero_guia": guide["guide_number"],
                        "data_atendimento_completa": guide["date"],
                        "status": "pending",
                        "task_id": self.task_id,
                        "attempts": 0,
                    }

                    response = (
                        supabase.table("guias_queue").insert(guide_data).execute()
                    )
                    print(
                        f"Guia {guide['guide_number']} adicionada à fila com sucesso"
                    )

                except Exception as e:
                    print(f"Erro ao processar guia {guide['guide_number']}: {str(e)}")
                    continue

            # Atualizar apenas o contador de guias totais no status existente
            if self.task_id:
                supabase.table("processing_status").update(
                    {
                        "total_guides": len(self.captured_guides),
                        "last_update": datetime.now().isoformat(),
                    }
                ).eq("task_id", self.task_id).execute()

            print(f"Total de {len(self.captured_guides)} guias na fila")

        except Exception as e:
            print(f"Erro ao salvar guias na fila: {str(e)}")
            if self.task_id:
                supabase.table("processing_status").update(
                    {
                        "status": "error",
                        "error": str(e),
                        "error_at": datetime.now().isoformat(),
                        "last_update": datetime.now().isoformat(),
                    }
                ).eq("task_id", self.task_id).execute()

    ### 4. Processamento de guias ###
    def process_single_guide(self, guide_number, date_str):
        """
        Processa uma única guia, baixando o PDF e extraindo informações
        
        Args:
            guide_number (str): Número da guia
            date_str (str): Data no formato dd/mm/aaaa
            
        Returns:
            dict: Dados extraídos ou None se falhar
        """
        try:
            print(f"\n====== Processando guia {guide_number} | Data: {date_str} ======")
            
            # Tenta baixar o PDF primeiro com o script dedicado Playwright
            try:
                from Unimed_Scraping.baixar_guia_pdf import baixar_pdf_guia
                print("Usando script dedicado para baixar o PDF")
                
                # Download do PDF
                pdf_path = baixar_pdf_guia(guide_number, date_str)
                
                if pdf_path and os.path.exists(pdf_path):
                    print(f"PDF baixado com sucesso: {pdf_path}")
                else:
                    print("Falha ao baixar o PDF usando o script dedicado")
                    # Cai para o método antigo
                    pdf_path = self.download_guide_pdf(guide_number, date_str)
                    
            except ImportError:
                print("Script dedicado não encontrado, usando método padrão")
                # Se não conseguir importar, usa o método antigo
                pdf_path = self.download_guide_pdf(guide_number, date_str)
            
            # Se não conseguiu baixar, retorna None
            if not pdf_path or not os.path.exists(pdf_path):
                print(f"Não foi possível baixar o PDF da guia {guide_number}")
                return None
            
            # Extrai dados do PDF baixado
            pdf_data = self.extract_pdf_data(pdf_path)
            
            if pdf_data:
                print(f"Dados extraídos com sucesso da guia {guide_number}")
                
                # Salva os dados extraídos
                data_dir = os.path.join(os.getcwd(), "dados_guias")
                os.makedirs(data_dir, exist_ok=True)
                
                json_path = os.path.join(data_dir, f"{guide_number}_{date_str.replace('/', '_')}.json")
                
                # Converte o dicionário para JSON com formatação legível
                with open(json_path, 'w', encoding='utf-8') as json_file:
                    json.dump(pdf_data, json_file, ensure_ascii=False, indent=2)
                    
                print(f"Dados salvos em: {json_path}")
                return pdf_data
            else:
                print(f"Não foi possível extrair dados do PDF da guia {guide_number}")
                return None
            
        except Exception as e:
            print(f"Erro ao processar guia {guide_number}: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return None

    ### 5. Navegação para exames finalizados ###
    def navigate_to_finished_exams(self):
        """Navega para a tela de exames finalizados"""
        try:
            # Primeira tentativa: procura pelo link dentro do td
            finished_exams = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "td#centro_21 a"))
            )
            # print("Encontrou o link de exames finalizados")

            # Clica no elemento
            finished_exams.click()
            # self.driver.save_screenshot("tela_exames_finalizados.png")
            # print("Clicou no link de exames finalizados")

            # Aguarda um momento para a página carregar
            self.random_wait()

            return True

        except Exception as e:
            print(f"Erro ao navegar para exames finalizados: {str(e)}")
            # self.driver.save_screenshot("erro_navegacao_exames_finalizados.png")
            return False

    ### 6. Busca e captura de datas de atendimento ###
    def search_and_get_guide_dates(self, guide_number: str, date_filter: str = None):
        """Busca uma guia específica e captura suas datas de atendimento"""
        print("Função search_and_get_guide_dates executada")
        try:
            # Realiza a busca da guia com o filtro de data - IMPORTANTE: sempre deve usar o filtro
            if not self.search_guide(guide_number, date_filter):
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

                    # Extrai a data e hora
                    date_time = date_element.text.strip()
                    date = date_time.split()[0]  # Pega apenas a parte da data
                    time = date_time.split()[1] if len(date_time.split()) > 1 else ""

                    # Se tiver filtro de data, verifica se a data corresponde
                    if date_filter and date != date_filter:
                        continue

                    guide_dates.append(
                        {
                            "date": date,
                            "time": time,
                            "guide_number_text": guide_number_element.text.strip(),
                            "row_index": rows.index(row),
                        }
                    )

                except NoSuchElementException:
                    continue
                except Exception as e:
                    print(f"Erro ao processar uma linha: {str(e)}")
                    continue

            print(
                f"Datas de atendimento encontradas para guia {guide_number}: {[f'{d['date']} {d['time']}'.strip() for d in guide_dates]}"
            )
            return guide_dates

        except Exception as e:
            print(f"Erro ao buscar guia: {str(e)}")
            return []

    ### 7. Busca e captura de datas de atendimento ###
    def search_guide(self, guide_number=None, date_filter=None):
        """
        Busca guias pelo número ou data
        
        Args:
            guide_number (str): Número da guia para buscar (opcional)
            date_filter (str): Data para filtragem no formato dd/mm/aaaa (opcional)
            
        Returns:
            bool: True se a busca foi bem-sucedida, False caso contrário
        """
        try:
            print(f"Buscando guias: número={guide_number}, data={date_filter}")
            
            # Verifica se está na tela de exames finalizados
            if "Exames Finalizados" not in self.driver.page_source:
                print("Página atual não é a de exames finalizados")
                return False
                
            # Localiza os campos de filtro
            try:
                if date_filter:
                    start_date_field = self.driver.find_element(By.NAME, "s_dt_ini")
                    end_date_field = self.driver.find_element(By.NAME, "s_dt_fim")
                    
                    # Limpa e preenche os campos de data
                    start_date_field.clear()
                    self.random_typing(start_date_field, date_filter)
                    
                    end_date_field.clear()
                    self.random_typing(end_date_field, date_filter)
                    
                # Se tiver número da guia, preenche o campo
                if guide_number:
                    guide_field = self.driver.find_element(By.NAME, "s_guia_id")
                    guide_field.clear()
                    self.random_typing(guide_field, guide_number)
                
                # Clica no botão de filtrar
                filter_button = self.driver.find_element(By.NAME, "Button_FIltro")
                filter_button.click()
                
                # Aguarda a tabela de resultados carregar
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#conteudo form table tbody"))
                )
                
                # Verifica se a busca retornou resultados
                error_msg = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Nenhum registro encontrado')]")
                if error_msg:
                    print("Busca não retornou resultados")
                    return False
                    
                print("Busca realizada com sucesso")
                return True
                
            except NoSuchElementException:
                print("Elementos de filtro não encontrados")
                return False
                
            except TimeoutException:
                print("Timeout aguardando resultados da busca")
                return False
                
        except Exception as e:
            print(f"Erro ao buscar guias: {str(e)}")
            return False

    ### 8. Captura de datas de execução ###
    def get_execution_dates(self, data_atendimento: str):
        """Captura as datas e ordens de execução da tabela de Procedimentos em Série."""
        execution_info = []
        original_wait = self.wait

        try:
            self.wait = WebDriverWait(self.driver, 30)
            self.random_wait(2, 3)

            try:
                table = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//table[contains(@class, 'MagnetoFormTABLE')]//td[contains(text(), 'Data de Procedimentos em Série')]/ancestor::table[1]")
                    )
                )
            except:
                table = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="conteudo"]/table[6]')
                    )
                )

            data_cells = table.find_elements(By.CLASS_NAME, "MagnetoDataTD")

            for cell in data_cells:
                try:
                    text = cell.text.strip().replace("\xa0", " ")
                    if "Observação" in text:
                        continue

                    if " - " in text:
                        # Extrai a ordem e a data
                        ordem_str, date_part = text.split(" - ", 1)
                        ordem = int(
                            ordem_str.strip().split()[0]
                        )  # Extrai apenas o número
                        date_part = date_part.strip()

                        if date_part and self._is_valid_date(date_part):
                            execution_info.append({"ordem": ordem, "data": date_part})

                except Exception as cell_error:
                    print(f"Erro ao processar célula: {str(cell_error)}")
                    continue

            if execution_info:
                print(f"Datas e ordens de execução encontradas: {execution_info}")
            return execution_info

        except Exception as e:
            print(f"Erro ao capturar datas de execução: {str(e)}")
            return []

        finally:
            self.wait = (
                original_wait  # Restaura o wait original independente do resultado
            )

    ##### 9. Salva execução da Unimed ####
    def save_unimed_execution(self, guia_id: str, guide_details: dict):
        """
        Método adaptado para salvar primeiro na tabela intermediária unimed_sessoes_capturadas 
        e depois chamar a função do banco para processar e inserir na tabela execucoes
        """
        try:
            # Cria um código_ficha temporário baseado no número da guia e data de atendimento
            codigo_ficha = f"TEMP_{guide_details['numero_guia']}_{guide_details['data_atendimento'].replace('/', '')}_{guide_details['ordem_execucao']}"
            
            print(f"Salvando execução para guia_id: {guia_id}")
            print(f"Detalhes da guia: {json.dumps(guide_details, indent=2)}")
            
            # Salva os detalhes da execução na tabela unimed_sessoes_capturadas
            self.supabase.table('unimed_sessoes_capturadas').insert(guide_details).execute()
            
            # Chama a função do banco para processar e inserir na tabela execucoes
            self.process_execution(guia_id, guide_details)
            
        except Exception as e:
            print(f"Erro ao salvar execução: {str(e)}")

    def validate_date(self, date_str: str) -> bool:
        """
        Valida se a string está no formato de data dd/mm/aaaa
        
        Args:
            date_str (str): String de data a ser validada
            
        Returns:
            bool: True se a data for válida, False caso contrário
        """
        try:
            if not date_str:
                return False
                
            # Verifica o formato
            if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
                return False
                
            # Valida a data
            day, month, year = map(int, date_str.split('/'))
            
            # Verifica valores básicos
            if month < 1 or month > 12:
                return False
                
            if day < 1:
                return False
                
            # Verifica os meses com 30 dias
            if month in [4, 6, 9, 11] and day > 30:
                return False
                
            # Verifica fevereiro e anos bissextos
            if month == 2:
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                if (is_leap and day > 29) or (not is_leap and day > 28):
                    return False
                    
            # Verifica os outros meses
            if month in [1, 3, 5, 7, 8, 10, 12] and day > 31:
                return False
                
            return True
            
        except Exception:
            return False

    def close(self):
        """
        Fecha o navegador e libera recursos
        """
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                print("Navegador fechado")
            except Exception as e:
                print(f"Erro ao fechar o navegador: {str(e)}")
                
        # Registra encerramento
        print("Automação encerrada")
            
    def download_guide_pdf_with_playwright_internal(self, guide_number: str, date_str: str):
        """
        Método interno alternativo para baixar PDF utilizando Playwright quando o método Selenium falhar.
        Este método é usado como fallback se o script baixar_pdf_playwright.py não estiver disponível.
        
        Args:
            guide_number (str): Número da guia
            date_str (str): Data no formato dd/mm/aaaa 
            
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
            
            print(f"\n[PLAYWRIGHT] Tentando baixar PDF da guia {guide_number} com Playwright")
            
            # Prepara diretório para downloads
            pdf_dir = os.path.join(os.getcwd(), "guias_pdf")
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Nome do arquivo PDF final
            pdf_filename = f"{guide_number}_{date_str.replace('/', '_')}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            # Verifica se o PDF já existe
            if os.path.exists(pdf_path):
                print(f"PDF já existe em: {pdf_path}")
                return pdf_path
            
            # Registra os arquivos PDF que já existem para comparação posterior
            existing_pdfs_before = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
            print(f"Arquivos PDF existentes antes do download: {len(existing_pdfs_before)}")
            
            with sync_playwright() as p:
                # Inicia o navegador (usando o modo headless depende do ambiente)
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
                        print("Credenciais não encontradas nas variáveis de ambiente")
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
                    print(f"[PLAYWRIGHT] Filtrando por data: {date_str}")
                    page.fill('input[name="s_dt_ini"]', date_str)
                    page.fill('input[name="s_dt_fim"]', date_str)
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
                            if guide_cell and guide_cell.inner_text().strip() == guide_number:
                                print(f"[PLAYWRIGHT] Guia {guide_number} encontrada na tabela")
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
                        
                        # 8. Procura e clica no link "Todas as guias"
                        link_clicked = False
                        
                        # Tenta localizar o div específico com ID subpGuiaXXXXX
                        div_id = f"subpGuia{guide_number}"
                        popup_div = page.query_selector(f"#{div_id}")
                        
                        if popup_div:
                            print(f"[PLAYWRIGHT] Div {div_id} encontrado!")
                            
                            # Procura o link específico dentro do div
                            link_id = f"print_todas_guias_{guide_number}"
                            todas_guias_link = popup_div.query_selector(f"#{link_id}")
                            
                            if todas_guias_link:
                                print(f"[PLAYWRIGHT] Link 'Todas as guias' encontrado com ID: {link_id}")
                                
                                # Exibe informações sobre o link
                                print(f"[PLAYWRIGHT] Texto do link: {todas_guias_link.inner_text()}")
                                print(f"[PLAYWRIGHT] href: {todas_guias_link.get_attribute('href')}")
                                
                                # Clica no link
                                todas_guias_link.click()
                                link_clicked = True
                                print("[PLAYWRIGHT] Link clicado com sucesso")
                        
                        # Se não conseguiu pela abordagem principal, tenta alternativas
                        if not link_clicked:
                            print("[PLAYWRIGHT] Link não encontrado pelo método principal, tentando alternativas...")
                            
                            # Procura por qualquer div que possa conter o menu
                            popup_divs = page.query_selector_all('div[class*="guiaBarLeft"], div[id^="subp"]')
                            
                            if popup_divs:
                                print(f"[PLAYWRIGHT] Encontrados {len(popup_divs)} divs popup potenciais")
                                
                                for div in popup_divs:
                                    if link_clicked:
                                        break
                                    
                                    div_id = div.get_attribute('id')
                                    print(f"[PLAYWRIGHT] Verificando div: {div_id}")
                                    
                                    # Procura links dentro do div
                                    links = div.query_selector_all('a')
                                    
                                    for link in links:
                                        link_text = link.inner_text().strip()
                                        link_id = link.get_attribute('id')
                                        link_href = link.get_attribute('href') or ""
                                        
                                        # Verifica se o link parece ser o correto
                                        if (link_text == "Todas as guias" or 
                                            (link_id and link_id == f"print_todas_guias_{guide_number}") or
                                            "todas" in link_text.lower()):
                                            
                                            print(f"[PLAYWRIGHT] Link potencial encontrado: text='{link_text}', id='{link_id}'")
                                            
                                            # Clica no link
                                            link.click()
                                            link_clicked = True
                                            print("[PLAYWRIGHT] Link clicado com sucesso")
                                            break
                            
                            # Se ainda não encontrou, busca em toda a página
                            if not link_clicked:
                                print("[PLAYWRIGHT] Buscando link em toda a página...")
                                all_links = page.query_selector_all('a')
                                
                                for link in all_links:
                                    link_text = link.inner_text().strip()
                                    link_id = link.get_attribute('id') or ""
                                    
                                    if link_text == "Todas as guias" or "print_todas_guias" in link_id:
                                        print(f"[PLAYWRIGHT] Link encontrado em toda a página: {link_id} - {link_text}")
                                        link.click()
                                        link_clicked = True
                                        print("[PLAYWRIGHT] Link clicado com sucesso")
                                        break
                        
                        # 9. Verifica se conseguiu clicar em algum link
                        if not link_clicked:
                            print("[PLAYWRIGHT] ALERTA: Não foi possível encontrar ou clicar no link 'Todas as guias'")
                            raise Exception("Não foi possível encontrar o link para download")
                        
                        # 10. Aguarda o download ser iniciado e completado
                        print("[PLAYWRIGHT] Aguardando download do PDF...")
                        
                        # Verifica periodicamente o diretório
                        timeout = 60  # 60 segundos de timeout
                        start_time = time.time()
                        
                        while time.time() - start_time < timeout:
                            time.sleep(1)
                            
                            # Verifica se o arquivo esperado existe
                            if os.path.exists(pdf_path):
                                print(f"[PLAYWRIGHT] PDF baixado com sucesso: {pdf_path}")
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
                                            return pdf_path
                                        except Exception as copy_error:
                                            print(f"[PLAYWRIGHT] Erro ao copiar arquivo: {str(copy_error)}")
                                            # Se não conseguir copiar, usa o arquivo original
                                            return most_recent_pdf
                                    else:
                                        return pdf_path
                    
                        # Se chegou aqui, o timeout foi atingido
                        print(f"[PLAYWRIGHT] Timeout atingido ({timeout}s) sem download completo")
                        
                        # Última verificação por novos PDFs
                        current_pdfs = set([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
                        new_pdfs = current_pdfs - existing_pdfs_before
                        
                        if new_pdfs:
                            most_recent_pdf = max([os.path.join(pdf_dir, f) for f in new_pdfs], key=os.path.getctime)
                            print(f"[PLAYWRIGHT] PDF encontrado após timeout: {os.path.basename(most_recent_pdf)}")
                            
                            # Verifica se o arquivo tem um tamanho razoável
                            if os.path.getsize(most_recent_pdf) > 1000:  # pelo menos 1KB
                                # Renomeia para o nome esperado
                                if most_recent_pdf != pdf_path:
                                    try:
                                        shutil.copy(most_recent_pdf, pdf_path)
                                        print(f"[PLAYWRIGHT] Arquivo copiado para: {pdf_path}")
                                        return pdf_path
                                    except:
                                        return most_recent_pdf
                                else:
                                    return pdf_path
                
                except Exception as e:
                    print(f"[PLAYWRIGHT] Erro durante o processo: {str(e)}")
                    import traceback
                    print(f"[PLAYWRIGHT] Traceback: {traceback.format_exc()}")
                    return None
                
            except Exception as e:
                print(f"[PLAYWRIGHT] Erro geral: {str(e)}")
                import traceback
                print(f"[PLAYWRIGHT] Traceback: {traceback.format_exc()}")
                return None
            
        except Exception as e:
            print(f"[PLAYWRIGHT] Erro geral: {str(e)}")
            import traceback
            print(f"[PLAYWRIGHT] Traceback: {traceback.format_exc()}")
            return None

    def download_guide_pdf_with_playwright(self, guide_number: str, date_str: str):
        """
        Método que tenta baixar o PDF da guia utilizando o script Playwright dedicado.
        Se o script não for encontrado, usa a implementação interna.
        
        Args:
            guide_number (str): Número da guia
            date_str (str): Data no formato dd/mm/aaaa
            
        Returns:
            str: Caminho para o arquivo PDF baixado ou None se falhar
        """
        try:
            # Tenta importar a função do script externo
            try:
                # Tenta importação direta
                from baixar_pdf_playwright import baixar_pdf_guia
                print("Usando script Playwright externo para download")
            except ImportError:
                # Tenta importação relativa
                try:
                    from Unimed_Scraping.baixar_pdf_playwright import baixar_pdf_guia
                    print("Usando script Playwright externo para download (importação relativa)")
                except ImportError:
                    print("Script baixar_pdf_playwright.py não encontrado, usando implementação interna")
                    return self.download_guide_pdf_with_playwright_internal(guide_number, date_str)
            
            # Data no formato esperado pela função
            data_atendimento = date_str
            
            # Chama a função importada
            pdf_path = baixar_pdf_guia(guide_number, data_atendimento)
            return pdf_path
            
        except Exception as e:
            print(f"Erro ao tentar usar script externo: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
            # Fallback para método interno
            print("Usando método interno como alternativa...")
            return self.download_guide_pdf_with_playwright_internal(guide_number, date_str)

    def executar_scraping(self, start_date=None, end_date=None, max_guides=None):
        """
        Executa o scraping de guias no período especificado.
        
        Args:
            start_date (str): Data inicial no formato dd/mm/aaaa
            end_date (str): Data final no formato dd/mm/aaaa
            max_guides (int): Número máximo de guias a processar
        """
        # Implementação do método
        return self.capture_guides(start_date, end_date, max_guides)
            