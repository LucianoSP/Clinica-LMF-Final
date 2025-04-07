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
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")

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
    def capture_guides(self, start_date: str, end_date: str, max_guides: int = None):
        """Captura todas as guias dentro do período especificado"""
        try:
            # Validate max_guides parameter
            if max_guides is not None:
                if not isinstance(max_guides, int) or max_guides <= 0:
                    raise ValueError("max_guides must be a positive integer")
                print(f"Will process up to {max_guides} guides")

            print(f"Iniciando captura de guias entre {start_date} e {end_date}")

            finished_exams = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="centro_21"]/a'))
            )
            finished_exams.click()
            # print("Acessou tela de exames finalizados")
            self.random_wait()

            start_date_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "s_dt_ini"))
            )
            end_date_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "s_dt_fim"))
            )

            start_date_field.clear()
            self.random_typing(start_date_field, start_date)

            end_date_field.clear()
            self.random_typing(end_date_field, end_date)
            # print("Datas preenchidas")

            filter_button = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "Button_FIltro"))
            )
            self.random_wait(0.5, 1)
            filter_button.click()
            # print("Filtro aplicado")
            self.random_wait()

            # self.driver.save_screenshot("busca_guias.png")

            guides_processed = 0
            page_num = 1
            while True:
                print(f"Processando página {page_num}")
                guides_table = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="conteudo"]/form[2]/table/tbody')
                    )
                )
                rows = guides_table.find_elements(By.TAG_NAME, "tr")[1:]

                for row in rows:
                    try:
                        # Captura o texto completo da data/hora usando o XPath específico para cada linha
                        # O tr[position()] é usado para pegar a linha correta dinamicamente
                        date_time = row.find_element(By.XPATH, "./td[1]").text.strip()

                        # Debug: imprimir o texto capturado para verificar o formato
                        # print(f"Data/Hora capturada (raw): '{date_time}'")

                        guide_number = row.find_element(
                            By.XPATH, "./td[2]/a"
                        ).text.strip()

                        # Adiciona captura de dados biométricos
                        biometric_data = self.get_biometric_data(row)

                        if date_time and guide_number:
                            guides_processed += 1
                            # Salva a data/hora exatamente como está no site
                            self.captured_guides.append(
                                {
                                    "date": date_time,  # Mantém o formato completo dd/mm/aaaa hh:mm
                                    "guide_number": guide_number,
                                    "biometric_data": biometric_data,  # Adiciona dados biométricos
                                }
                            )
                            print(
                                f"Guia capturada: {guide_number} - Data/Hora completa: {date_time} - Biometria: {biometric_data}"
                            )

                            # Check if we've reached the maximum number of guides
                            if (
                                max_guides is not None
                                and guides_processed >= max_guides
                            ):
                                print(
                                    f"Reached maximum number of guides ({max_guides}). Stopping capture."
                                )
                                break

                    except NoSuchElementException:
                        continue
                    except Exception as e:
                        print(f"Erro ao processar linha: {str(e)}")
                        continue

                # Break outer loop if max_guides reached
                if max_guides is not None and guides_processed >= max_guides:
                    break

                try:
                    next_button = self.driver.find_element(By.LINK_TEXT, "Próxima")
                    if "disabled" in next_button.get_attribute("class"):
                        print("Última página alcançada")
                        break
                    self.random_wait(0.5, 1)
                    next_button.click()
                    print(f"Indo para página {page_num + 1}")
                    self.random_wait()
                    page_num += 1
                except NoSuchElementException:
                    print("Não há mais páginas")
                    break

            print(f"Total de guias capturadas: {len(self.captured_guides)}")
            self.save_captured_guides()  # Agora salva no Supabase ao invés do Excel
            return self.captured_guides

        except Exception as e:
            print(f"Erro durante a captura de guias: {str(e)}")
            if self.task_id:
                supabase.table("processing_status").update(
                    {
                        "status": "error",
                        "error": f"Erro durante a captura: {str(e)}",
                    }
                ).eq("task_id", self.task_id).execute()
            raise

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
    def process_single_guide(self, guide_data: dict):
        """Processa uma única guia e extrai todos os dados necessários"""
        print("Função process_single_guide executada")
        try:
            print(f"\nProcessando guia: {guide_data['guide_number']}")

            # Verifica se a guia já foi processada com sucesso
            queue_status = (
                supabase.table("guias_queue")
                .select("status")
                .eq("numero_guia", guide_data["guide_number"])
                .eq("data_atendimento_completa", guide_data["date"])
                .execute()
            )

            if queue_status.data:
                status = queue_status.data[0]["status"]
                if status == "processado":
                    print(
                        f"Guia {guide_data['guide_number']} já foi processada anteriormente. Pulando processamento."
                    )
                    return []

            guide_details_list = []

            # Extrai a data da string completa (formato: dd/mm/yyyy HH:MM)
            data_execucao = (
                guide_data["date"].split()[0]
                if " " in guide_data["date"]
                else guide_data["date"]
            )

            # Navega para a tela de exames finalizados
            if not self.navigate_to_finished_exams():
                raise Exception("Falha ao navegar para exames finalizados")

            # Busca e captura todas as datas de atendimento
            guide_dates = self.search_and_get_guide_dates(
                guide_data["guide_number"], date_filter=data_execucao
            )
            if not guide_dates:
                print("Nenhuma data de atendimento encontrada")
                return []

            print(f"Encontrados {len(guide_dates)} atendimentos para processamento")

            # Para cada data de atendimento, processa a guia
            for index, guide_date in enumerate(guide_dates):
                print(
                    f"\nProcessando atendimento {index + 1}/{len(guide_dates)}: {guide_date['date']} {guide_date.get('time', '')}"
                )
                data_atendimento_completa = (
                    f"{guide_date['date']} {guide_date.get('time', '')}".strip()
                )

                try:
                    # Localiza o link da guia usando o índice específico da linha
                    row_index = index + 2
                    guide_link = self.wait.until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                f"//*[@id='conteudo']/form[2]/table/tbody/tr[{row_index}]/td[2]/a",
                            )
                        )
                    )
                    self.random_wait(0.5, 1)
                    guide_link.click()
                    self.random_wait(1, 2)

                    # Extrai dados básicos da guia
                    beneficiary_info = self.wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//*[@id='conteudo']/table[1]/tbody/tr[6]/td[1]/span",
                            )
                        )
                    ).text

                    carteira, nome = "", ""
                    if " - " in beneficiary_info:
                        carteira, nome = beneficiary_info.split(" - ", 1)
                        carteira = carteira.strip()
                        nome = nome.strip()

                    # Captura outros dados da guia
                    procedure_code = self.wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, "//*[@id='conteudo']/table[4]/tbody/tr[2]/td[5]")
                        )
                    ).text

                    # Captura dados do profissional
                    professional_data = self.get_professional_data()

                    # Captura datas e ordens de execução
                    execution_dates = self.get_execution_dates(guide_date["date"])
                    print(f"Execuções encontradas neste atendimento: {execution_dates}")

                    if execution_dates:
                        for exec_info in execution_dates:
                            guide_details = {
                                "carteira": carteira,
                                "nome_beneficiario": nome,
                                "codigo_procedimento": procedure_code,
                                "data_atendimento": data_atendimento_completa,
                                "data_execucao": exec_info["data"],
                                "ordem_execucao": exec_info["ordem"],
                                "numero_guia": guide_data["guide_number"],
                                **professional_data,
                            }
                            guide_details_list.append(guide_details)
                            print(
                                f"Nova execução adicionada: Atendimento {data_atendimento_completa}, Ordem {exec_info['ordem']} - Data {exec_info['data']}"
                            )
                    else:
                        print(
                            f"Nenhuma data de execução encontrada para o atendimento {data_atendimento_completa}"
                        )

                    # Volta para a lista de guias
                    self.navigate_back_to_guide_list()

                except Exception as e:
                    print(
                        f"Erro ao processar atendimento {data_atendimento_completa}: {str(e)}"
                    )
                    continue

            print(
                f"\nTotal de execuções processadas para guia {guide_data['guide_number']}: {len(guide_details_list)}"
            )
            
            # Atualiza o status de processamento após cada guia individual
            if self.task_id and guide_details_list:
                try:
                    print(f"\nAtualizando contador de guias processadas para task_id: {self.task_id}")
                    
                    # Primeiro, busca o valor atual de processed_guides
                    status_query = supabase.table("processing_status").select("processed_guides").eq("task_id", self.task_id).execute()
                    print(f"Resultado da consulta de status: {status_query}")
                    
                    if status_query.data and len(status_query.data) > 0:
                        current_processed = status_query.data[0].get("processed_guides", 0)
                        print(f"Valor atual de processed_guides: {current_processed}")
                        
                        # Atualiza o contador de guias processadas incrementando o valor atual
                        update_data = {
                            "processed_guides": current_processed + 1,
                            "last_update": datetime.now().isoformat(),
                        }
                        print(f"Atualizando para: {update_data}")
                        
                        update_response = supabase.table("processing_status").update(update_data).eq("task_id", self.task_id).execute()
                        print(f"Resposta da atualização: {update_response}")
                        
                        print(f"Status de processamento atualizado para a guia {guide_data['guide_number']}")
                except Exception as e:
                    print(f"Erro ao atualizar status de processamento: {str(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
            
            return guide_details_list

        except Exception as e:
            print(f"Erro ao processar guia {guide_data['guide_number']}: {str(e)}")
            raise

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
    def search_guide(self, guide_number: str, date_filter: str = None):
        """Busca uma guia específica usando o formulário de busca"""
        print("Função search_guide executada")
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
            self.random_typing(guide_input, guide_number)
            print(f"Número da guia {guide_number} inserido no campo de busca")

            # Se tiver data para filtrar, preenche os campos de data
            if date_filter:
                start_date_field = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "s_dt_ini"))
                )
                end_date_field = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "s_dt_fim"))
                )

                start_date_field.clear()
                self.random_typing(start_date_field, date_filter)

                end_date_field.clear()
                self.random_typing(end_date_field, date_filter)
                print(f"Filtro de data definido para {date_filter}")

            # Localiza e clica no botão Filtrar usando o XPath correto
            filter_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="filtro"]/table/tbody/tr[7]/td/input[3]')
                )
            )
            self.random_wait(0.5, 1)
            filter_button.click()

            self.random_wait()
            return True

        except Exception as e:
            print(f"Erro ao buscar guia: {str(e)}")
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
                        (
                            By.XPATH,
                            "//table[contains(@class, 'MagnetoFormTABLE')]//td[contains(text(), 'Data de Procedimentos em Série')]/ancestor::table[1]",
                        )
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
            
            # Prepara os dados para a tabela intermediária
            # Converte a data de execução do formato dd/mm/yyyy para yyyy-mm-dd
            data_execucao = guide_details["data_execucao"]
            if '/' in data_execucao:
                dia, mes, ano = data_execucao.split('/')
                data_execucao_formatada = f"{ano}-{mes}-{dia}"
            else:
                data_execucao_formatada = data_execucao
                
            sessao_data = {
                "numero_guia": guide_details["numero_guia"],
                "data_atendimento_completa": f"{guide_details['data_atendimento']} 00:00", # Formato dd/mm/aaaa hh:mm
                "data_execucao": data_execucao_formatada,
                "paciente_nome": guide_details["nome_beneficiario"],
                "paciente_carteirinha": guide_details["carteira"],
                "codigo_ficha": codigo_ficha,
                "profissional_executante": guide_details["nome_profissional"].strip(),
                "conselho_profissional": guide_details["conselho_profissional"].strip(),
                "numero_conselho": guide_details["numero_conselho"].strip(),
                "uf_conselho": guide_details["uf_conselho"].strip(),
                "codigo_cbo": guide_details["codigo_cbo"].strip(),
                "origem": "unimed_scraping",
                "status": "pendente",
                "task_id": self.task_id,
                "ordem_execucao": guide_details.get("ordem_execucao", None)
            }
            
            print(f"Dados da sessão a serem salvos: {json.dumps(sessao_data, indent=2)}")
            
            # Salva na tabela intermediária
            response = supabase.table("unimed_sessoes_capturadas").insert(sessao_data).execute()
            
            if not response.data:
                print(f"Erro ao salvar na tabela intermediária: sem dados de retorno")
                print(f"Resposta completa: {response}")
                return False
                
            sessao_id = response.data[0]['id']
            print(f"Sessão salva na tabela intermediária com ID: {sessao_id}")
            
            # Chama a função para processar e inserir na tabela execucoes
            print(f"Chamando função inserir_execucao_unimed com sessao_id: {sessao_id}")
            rpc_response = supabase.rpc(
                'inserir_execucao_unimed', 
                {'sessao_id': sessao_id}
            ).execute()
            
            print(f"Resposta da função RPC: {rpc_response}")
            
            if rpc_response.data:
                # Se deu certo, a função retorna o ID da execução criada
                print(f"Execução processada com sucesso. ID: {rpc_response.data}")
                return True
            else:
                # Se não encontrou a guia no banco ou outra falha
                print(f"Aviso: A função inserir_execucao_unimed não retornou um ID")
                print(f"Resposta completa: {rpc_response}")
                
                # Atualiza o status da sessão para indicar o problema
                supabase.table("unimed_sessoes_capturadas")\
                    .update({"status": "erro", "error": "Guia não encontrada no banco de dados"})\
                    .eq("id", sessao_id)\
                    .execute()
                    
                return False
        except Exception as e:
            print(f"Erro ao salvar execução da Unimed: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def verificar_processamento_sessoes(self):
        """
        Verifica o status do processamento das sessões capturadas e gera um relatório
        """
        try:
            if not self.task_id:
                print("Não há task_id definido. Verificação de processamento ignorada.")
                return
                
            print(f"\nVerificando processamento de sessões para task_id: {self.task_id}")
                
            # Consulta todas as sessões desta task - uma consulta para cada status
            processadas_query = supabase.table('unimed_sessoes_capturadas')\
                .select('id')\
                .eq('task_id', self.task_id)\
                .eq('status', 'processado')\
                .execute()
                
            erro_query = supabase.table('unimed_sessoes_capturadas')\
                .select('id')\
                .eq('task_id', self.task_id)\
                .eq('status', 'erro')\
                .execute()
                
            pendentes_query = supabase.table('unimed_sessoes_capturadas')\
                .select('id')\
                .eq('task_id', self.task_id)\
                .eq('status', 'pendente')\
                .execute()
                
            # Obtém as contagens
            processadas = len(processadas_query.data) if processadas_query.data else 0
            com_erro = len(erro_query.data) if erro_query.data else 0
            pendentes = len(pendentes_query.data) if pendentes_query.data else 0
            total = processadas + com_erro + pendentes
            
            print(f"Resultados das consultas:")
            print(f"Processadas: {processadas}")
            print(f"Com erro: {com_erro}")
            print(f"Pendentes: {pendentes}")
            print(f"Total: {total}")
            
            # Verifica se há guias na fila para esta task
            guias_queue_query = supabase.table('guias_queue')\
                .select('id')\
                .eq('task_id', self.task_id)\
                .execute()
                
            total_guias_queue = len(guias_queue_query.data) if guias_queue_query.data else 0
            print(f"Total de guias na fila: {total_guias_queue}")
            
            # Se não há sessões mas há guias na fila, pode ser que as sessões ainda não tenham sido criadas
            if total == 0 and total_guias_queue > 0:
                print("Não há sessões processadas ainda, mas há guias na fila. O processamento pode estar em andamento.")
                
                # Atualiza o status_processing com as estatísticas
                update_data = {
                    'processed_guides': 0,
                    'total_execucoes': 0,
                    'retry_guides': 0,
                    'last_update': datetime.now().isoformat(),
                    'status': 'processing'  # Mantém como "processing" enquanto há guias na fila
                }
            else:
                # Atualiza o status_processing com as estatísticas
                update_data = {
                    'processed_guides': processadas,
                    'total_execucoes': total,
                    'retry_guides': com_erro,
                    'last_update': datetime.now().isoformat(),
                    'completed_at': datetime.now().isoformat() if pendentes == 0 and total > 0 else None,
                    'status': 'completed' if pendentes == 0 and com_erro == 0 and total > 0 else
                             'completed_with_errors' if pendentes == 0 and com_erro > 0 else
                             'processing' if total > 0 else 'iniciado'  # Se não há sessões, mantém como "iniciado"
                }
            
            print(f"Atualizando processing_status com: {json.dumps(update_data, indent=2)}")
            
            update_response = supabase.table('processing_status')\
                .update(update_data)\
                .eq('task_id', self.task_id)\
                .execute()
                
            print(f"Resposta da atualização: {update_response}")
                
            # Exibe relatório no console
            print("\n=== RELATÓRIO DE PROCESSAMENTO ===")
            print(f"Total de sessões: {total}")
            print(f"Processadas com sucesso: {processadas}")
            print(f"Com erro: {com_erro}")
            print(f"Pendentes: {pendentes}")
            print(f"Total de guias na fila: {total_guias_queue}")
            print("================================\n")
            
        except Exception as e:
            print(f"Erro ao verificar processamento: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

    ##### 10. Salva no supabase ####
    def save_to_supabase(self, guide_details_list):
        if not supabase:
            print("Supabase não configurado corretamente.")
            return

        try:
            successful_executions = 0
            processed_guides = set()  # Guias únicas processadas
            all_guides_already_processed = (
                True  # Flag para verificar se todas as guias já estavam processadas
            )

            for guide_details in guide_details_list:
                try:
                    numero_guia = guide_details["numero_guia"]
                    print(f"Processando guia: {numero_guia}")

                    # Verifica se a guia já foi processada
                    queue_status = (
                        supabase.table("guias_queue")
                        .select("status")
                        .eq("numero_guia", numero_guia)
                        .eq("data_atendimento_completa", guide_details["data_atendimento"])
                        .execute()
                    )

                    if queue_status.data:
                        status = queue_status.data[0]["status"]
                        if status == "processado":
                            print(f"Guia {numero_guia} já processada anteriormente.")
                            continue

                    all_guides_already_processed = (
                        False  # Encontrou pelo menos uma guia para processar
                    )

                    # Process guide references
                    carteirinha_id = self.get_or_create_carteirinha(
                        guide_details["carteira"], guide_details["nome_beneficiario"]
                    )
                    paciente_id = self.get_or_create_paciente(
                        guide_details["nome_beneficiario"], guide_details["carteira"]
                    )
                    procedimento_id = self.get_or_create_procedimento(
                        guide_details["codigo_procedimento"]
                    )

                    if not all([carteirinha_id, paciente_id, procedimento_id]):
                        print(
                            f"Erro: Referências necessárias não encontradas para guia {numero_guia}"
                        )
                        continue

                    # Check/create guide
                    existing_guide = (
                        supabase.table("guias")
                        .select("id, quantidade_executada")
                        .eq("numero_guia", numero_guia)
                        .execute()
                    )

                    if existing_guide.data:
                        guia_id = existing_guide.data[0]["id"]
                        print(f"Guia existente encontrada: {guia_id}")
                    else:
                        guia_data = {
                            "numero_guia": numero_guia,
                            "carteirinha_id": carteirinha_id,
                            "paciente_id": paciente_id,
                            "procedimento_id": procedimento_id,
                            "quantidade_autorizada": guide_details.get(
                                "quantidade_autorizada", 1
                            ),
                            "quantidade_executada": 1,
                            "tipo": "procedimento",  # Valor válido para o enum tipo_guia
                            "status": "executada"    # Valor válido para o enum status_guia
                        }
                        print(f"Inserindo nova guia com dados: {guia_data}")
                        response = supabase.table("guias").insert(guia_data).execute()
                        guia_id = response.data[0]["id"]
                        print(f"Nova guia criada com ID: {guia_id}")

                    # Save execution
                    if self.save_unimed_execution(guia_id, guide_details):
                        successful_executions += 1
                        processed_guides.add(
                            numero_guia
                        )  # Adiciona à lista de guias processadas

                        # Update guias_queue status
                        supabase.table("guias_queue").update(
                            {
                                "status": "processado",
                                "processed_at": datetime.now().isoformat(),
                            }
                        ).eq("numero_guia", numero_guia).eq(
                            "data_atendimento_completa", guide_details["data_atendimento"]
                        ).execute()
                        
                        # Atualiza estatísticas em tempo real após cada guia processada
                        self.verificar_processamento_sessoes()

                except Exception as e:
                    print(f"\n[ERROR] Erro ao salvar guia {numero_guia}: {str(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    # Atualiza estatísticas mesmo em caso de erro
                    self.verificar_processamento_sessoes()
                    continue

            # Atualiza o status final
            if self.task_id:
                try:
                    num_unique_guides = len(processed_guides)

                    if all_guides_already_processed:
                        update_data = {
                            "status": "pulado",  # Novo status para indicar que não havia guias para processar
                            "processed_guides": 0,
                            "total_execucoes": 0,
                            "last_update": datetime.now().isoformat(),
                        }
                    else:
                        update_data = {
                            "status": "finalizado",
                            "processed_guides": num_unique_guides,
                            "total_execucoes": successful_executions,
                            "total_guides": num_unique_guides,
                            "last_update": datetime.now().isoformat(),
                        }

                    supabase.table("processing_status").update(update_data).eq(
                        "task_id", self.task_id
                    ).execute()

                    if all_guides_already_processed:
                        print(
                            "Execução pulada: todas as guias já haviam sido processadas anteriormente."
                        )
                    else:
                        print(
                            f"Status final atualizado: {num_unique_guides} guias processadas, "
                            f"{successful_executions} execuções"
                        )

                except Exception as e:
                    print(f"Erro ao atualizar status final: {str(e)}")
                    raise

        except Exception as e:
            print(f"\n[ERROR] Erro geral ao salvar no Supabase: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            if self.task_id:
                supabase.table("processing_status").update(
                    {
                        "status": "error",
                        "error": str(e),
                        "error_at": datetime.now().isoformat(),
                        "last_update": datetime.now().isoformat(),
                    }
                ).eq("task_id", self.task_id).execute()
        # Após processar todas as guias, verificar o status das sessões
        self.verificar_processamento_sessoes()

    def navigate_back_to_guide_list(self):
        """Navega de volta para a lista de guias"""
        try:
            # Clica no botão "Voltar" usando o XPath fornecido
            back_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="Btn_Voltar"]'))
            )
            self.random_wait(0.5, 1)
            back_button.click()

            # Aguarda a página de lista de guias carregar verificando a presença do campo de busca
            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="filtro"]/table/tbody/tr[3]/td[4]/input')
                    )
                )
                print("Voltou para a lista de guias com sucesso")
                self.random_wait()
                return True
            except TimeoutException:
                print(
                    "Timeout: Página de lista de guias não carregou corretamente após clicar em 'Voltar'"
                )
                return False

        except Exception as e:
            print(f"Erro ao navegar de volta para lista de guias: {str(e)}")
            return False

    def close(self):
        time.sleep(10)
        """Fecha o navegador e salva o cache"""
        self.save_cache()  # Salva o cache antes de fechar
        if self.driver:
            self.driver.quit()
            print("Navegador fechado")

    ######## FUNCOES AUXILIARES ########
    async def check_guia_exists(self, numero_guia):
        response = (
            await supabase.table("guias")
            .select("*")
            .eq("numero_guia", numero_guia)
            .execute()
        )
        return len(response.data) > 0

    async def check_guia_queue_exists(self, numero_guia, data_execucao):
        response = (
            await supabase.table("guias_queue")
            .select("*")
            .eq("numero_guia", numero_guia)
            .eq("data_atendimento_completa", data_execucao)
            .execute()
        )
        return len(response.data) > 0

    def get_or_create_carteirinha(self, numero_carteira: str, nome_beneficiario: str):
        """Versão atualizada com timestamp"""
        try:
            if numero_carteira in self.cache["carteirinhas"]:
                self._update_cache_timestamp("carteirinhas", numero_carteira)
                print(f"Cache hit: paciente {numero_carteira}")
                return self.cache["carteirinhas"][numero_carteira]

            # Primeiro busca o plano de saúde da Unimed (deve existir previamente)
            plano_response = (
                supabase.table("planos_saude")
                .select("id")
                .eq("nome", "UNIMED")
                .execute()
            )
            if not plano_response.data:
                raise Exception("Plano de saúde UNIMED não encontrado")
            plano_id = plano_response.data[0]["id"]

            # Tenta buscar carteirinha pela combinação única
            response = (
                supabase.table("carteirinhas")
                .select("id")
                .eq("numero_carteirinha", numero_carteira)
                .eq("plano_saude_id", plano_id)
                .execute()
            )

            if response.data:
                carteirinha_id = response.data[0]["id"]
                print(f"Carteirinha existente encontrada: {carteirinha_id}")
            else:
                # Primeiro cria o paciente apenas com campos obrigatórios
                paciente_data = {
                    "nome": nome_beneficiario,
                    "id_origem": f"UNIMED_{numero_carteira}"  # Valor padrão para id_origem
                }
                paciente_response = (
                    supabase.table("pacientes").insert(paciente_data).execute()
                )
                paciente_id = paciente_response.data[0]["id"]

                # Agora cria a carteirinha associada ao paciente e plano
                insert_data = {
                    "numero_carteirinha": numero_carteira,
                    "plano_saude_id": plano_id,
                    "paciente_id": paciente_id,
                    "status": "ativa",  # Este é do enum status_carteirinha
                }
                response = supabase.table("carteirinhas").insert(insert_data).execute()
                carteirinha_id = response.data[0]["id"]
                print(f"Nova carteirinha criada: {carteirinha_id}")

            # Guarda no cache e salva imediatamente
            self.cache["carteirinhas"][numero_carteira] = carteirinha_id
            self._update_cache_timestamp("carteirinhas", numero_carteira)
            self.save_cache()
            return carteirinha_id

        except Exception as e:
            print(f"Erro ao buscar/criar carteirinha {numero_carteira}: {str(e)}")
            return None

    def get_or_create_paciente(self, nome: str, numero_carteira: str):
        """
        Busca um paciente pelo número da carteirinha com cache persistente.
        Se não encontrar, cria um novo paciente associado à carteirinha.
        """
        cache_key = numero_carteira  # Usa o número da carteirinha como chave do cache
        if cache_key in self.cache["pacientes"]:
            self._update_cache_timestamp("pacientes", cache_key)
            print(f"Cache hit: paciente {cache_key}")
            return self.cache["pacientes"][cache_key]

        try:
            # Primeiro busca a carteirinha usando o número correto da coluna
            carteirinha_response = (
                supabase.table("carteirinhas")
                .select("id, paciente_id")
                .eq("numero_carteirinha", numero_carteira)
                .execute()
            )

            if carteirinha_response.data:
                carteirinha = carteirinha_response.data[0]
                if carteirinha.get("paciente_id"):
                    # Se a carteirinha já tem um paciente associado, usa ele
                    paciente_id = carteirinha["paciente_id"]
                    print(f"Paciente existente encontrado: {paciente_id}")
                else:
                    # Se a carteirinha existe mas não tem paciente, cria o paciente e atualiza a carteirinha
                    insert_data = {
                        "nome": nome, 
                        "status": "ativo",
                        "id_origem": f"UNIMED_{numero_carteira}"  # Valor padrão para id_origem
                    }
                    paciente_response = (
                        supabase.table("pacientes").insert(insert_data).execute()
                    )

                    # Atualiza a carteirinha com o paciente_id
                    supabase.table("carteirinhas").update(
                        {"paciente_id": paciente_id}
                    ).eq("id", carteirinha["id"]).execute()

                # Adiciona ao cache e salva
                self.cache["pacientes"][cache_key] = paciente_id
                self._update_cache_timestamp("pacientes", cache_key)
                self.save_cache()
                return paciente_id
            else:
                print(f"Carteirinha {numero_carteira} não encontrada")
                return None

        except Exception as e:
            print(
                f"Erro ao buscar/criar paciente para carteirinha {numero_carteira}: {str(e)}"
            )
            return None

    def get_or_create_procedimento(self, codigo: str):
        """
        Busca um procedimento pelo código com cache persistente.
        Se não encontrar, cria um novo procedimento com o código fornecido.
        """
        if codigo in self.cache["procedimentos"]:
            self._update_cache_timestamp("procedimentos", codigo)
            print(f"Cache hit: procedimento {codigo}")
            return self.cache["procedimentos"][codigo]

        try:
            response = (
                supabase.table("procedimentos")
                .select("id")
                .eq("codigo", codigo)
                .execute()
            )
            if response.data:
                procedimento_id = response.data[0]["id"]
                print(f"Procedimento existente encontrado: {procedimento_id}")
            else:
                # Cria um novo procedimento apenas com os campos que existem na tabela
                insert_data = {
                    "codigo": codigo,
                    "nome": f"Procedimento {codigo}",  # Nome temporário
                    "descricao": f"Procedimento importado automaticamente - código {codigo}",
                    "tipo": "procedimento",  # Adicionando o tipo obrigatório
                    "ativo": True,
                }
                response = supabase.table("procedimentos").insert(insert_data).execute()
                procedimento_id = response.data[0]["id"]
                print(f"Novo procedimento criado: {procedimento_id}")

            # Adiciona ao cache e salva
            self.cache["procedimentos"][codigo] = procedimento_id
            self._update_cache_timestamp("procedimentos", codigo)
            self.save_cache()
            return procedimento_id

        except Exception as e:
            print(f"Erro ao buscar/criar procedimento {codigo}: {str(e)}")
            return None

    def get_biometric_data(self, row):
        """Verifica o status da biometria baseado no ícone presente na página"""
        try:
            # Verifica primeiro se existe o ícone de sucesso
            success_icon = row.find_elements(
                By.XPATH, ".//img[@alt='Leitura biométrica efetuada com sucesso']"
            )
            if success_icon:
                return "sucesso"

            # Se não encontrou sucesso, verifica se existe o ícone de erro
            error_icon = row.find_elements(
                By.XPATH,
                ".//img[@alt='Problema ao efetuar a leitura biométrica facial']",
            )
            if error_icon:
                return "erro"

            # Se não encontrou nenhum dos dois
            return "nao_encontrado"

        except Exception as e:
            print(f"Erro ao verificar status da biometria: {str(e)}")
            return "erro_verificacao"

    def get_professional_data(self):
        """Extrai os dados do profissional da página de detalhes da guia"""
        try:
            professional_name = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[4]")
                )
            ).text
            professional_council = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[5]")
                )
            ).text
            council_number = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[6]")
                )
            ).text
            council_state = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[7]")
                )
            ).text
            cbo_code = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[@id='conteudo']/table[5]/tbody/tr[3]/td[8]")
                )
            ).text

            return {
                "nome_profissional": professional_name.strip(),
                "conselho_profissional": professional_council.strip(),
                "numero_conselho": council_number.strip(),
                "uf_conselho": council_state.strip(),
                "codigo_cbo": cbo_code.strip(),
            }

        except Exception as e:
            print(f"Erro ao capturar dados do profissional: {str(e)}")
            # Retorna valores vazios em caso de erro
            return {
                "nome_profissional": "",
                "conselho_profissional": "",
                "numero_conselho": "",
                "uf_conselho": "",
                "codigo_cbo": "",
            }

    def random_wait(self, min_seconds: float = 0.5, max_seconds: float = 1):
        """Tempos reduzidos para teste"""
        time.sleep(random.uniform(min_seconds, max_seconds))

    def random_typing(
        self, element, text: str, min_seconds: float = 0.05, max_seconds: float = 0.2
    ):
        """Digita o texto no elemento com delays aleatórios entre as teclas"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_seconds, max_seconds))

    def _is_valid_date(self, date_str: str) -> bool:
        """Verifica se a string fornecida está no formato de data dd/mm/yyyy."""
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False


def executar_scraping(start_date=None, end_date=None, max_guides=None):
    """Função principal que executa o scraping"""
    print("\n=== INICIANDO SCRAPING DA UNIMED ===")
    print(f"Período: {start_date} a {end_date}")
    print(f"Máximo de guias: {max_guides if max_guides else 'Sem limite'}")

    # Verifica se as datas foram fornecidas
    if not start_date or not end_date:
        start_date = end_date = datetime.now().strftime("%d/%m/%Y")
        print(f"Datas não fornecidas, usando data atual: {start_date}")

    automation = UnimedAutomation()
    try:
        # Configurar o driver
        automation.setup_driver()

        # Obter credenciais do arquivo .env
        username = os.getenv("UNIMED_USERNAME")
        password = os.getenv("UNIMED_PASSWORD")

        if not username or not password:
            print("Erro: Credenciais não encontradas no arquivo .env")
            return

        if automation.login(username, password):
            print("\nLogin realizado com sucesso")

            # Criar entrada inicial no processing_status
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            automation.task_id = task_id
            print(f"\nTask ID gerado: {task_id}")

            initial_status = {
                "status": "iniciado",
                "task_id": task_id,
                "start_date": start_date,
                "end_date": end_date,
                "max_guides": max_guides,
                "started_at": datetime.now().isoformat(),
                "total_guides": 0,
                "processed_guides": 0,
                "total_execucoes": 0,
            }
            
            print(f"Criando status inicial: {json.dumps(initial_status, indent=2)}")
            status_response = supabase.table("processing_status").insert(initial_status).execute()
            print(f"Resposta da criação de status: {status_response}")
            print(f"Status inicial criado com task_id: {task_id}")

            success = True
            try:
                guides = automation.capture_guides(
                    start_date, end_date, max_guides=max_guides
                )

                if not guides:
                    print("Nenhuma guia encontrada no período especificado")
                    update_data = {
                        "status": "finalizado",  # Mudado de 'sem_guias' para 'finalizado'
                        "error": "Nenhuma guia encontrada no período especificado",
                        "completed_at": datetime.now().isoformat(),
                        "last_update": datetime.now().isoformat(),
                    }
                    print(f"Atualizando status para: {json.dumps(update_data, indent=2)}")
                    update_response = supabase.table("processing_status").update(update_data).eq("task_id", task_id).execute()
                    print(f"Resposta da atualização: {update_response}")
                    return

                print(f"\nFase 1: Capturadas {len(guides)} guias")
                processed_guides = []
                skipped_count = 0

                for idx, guide in enumerate(guides, 1):
                    try:
                        print(f"\nProcessando guia {idx}/{len(guides)}: {guide['guide_number']}")
                        guide_details = automation.process_single_guide(guide)
                        if guide_details:
                            processed_guides.append(guide_details)
                        else:
                            skipped_count += 1
                    except Exception as e:
                        print(f"Erro ao processar guia {guide['guide_number']}: {str(e)}")
                        import traceback
                        print(f"Traceback: {traceback.format_exc()}")
                        continue

                print(f"\nFase 2: Processadas {len(processed_guides)} guias, {skipped_count} puladas")

                # Salva os detalhes das guias no Supabase
                if processed_guides:
                    flat_guide_details = [
                        item for sublist in processed_guides for item in sublist
                    ]
                    print(f"\nFase 3: Salvando {len(flat_guide_details)} execuções no Supabase")
                    automation.save_to_supabase(flat_guide_details)
                else:
                    print("\nNenhuma guia para salvar no Supabase")
                    update_data = {
                        "status": "finalizado",
                        "error": "Nenhuma guia processada com sucesso",
                        "completed_at": datetime.now().isoformat(),
                        "last_update": datetime.now().isoformat(),
                    }
                    print(f"Atualizando status para: {json.dumps(update_data, indent=2)}")
                    update_response = supabase.table("processing_status").update(update_data).eq("task_id", task_id).execute()
                    print(f"Resposta da atualização: {update_response}")

                # Verifica o processamento final das sessões
                print("\nVerificando processamento final das sessões")
                automation.verificar_processamento_sessoes()

            except Exception as e:
                print(f"\nErro durante a execução: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                success = False
                if automation and automation.task_id:
                    update_data = {
                        "status": "error",
                        "error": f"Erro durante a execução: {str(e)}",
                        "error_at": datetime.now().isoformat(),
                        "last_update": datetime.now().isoformat(),
                    }
                    print(f"Atualizando status para: {json.dumps(update_data, indent=2)}")
                    update_response = supabase.table("processing_status").update(update_data).eq("task_id", automation.task_id).execute()
                    print(f"Resposta da atualização: {update_response}")
        else:
            print("\nFalha no login")
            success = False
            update_data = {
                "status": "error",
                "error": "Falha no login",
                "completed_at": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat(),
            }
            print(f"Atualizando status para: {json.dumps(update_data, indent=2)}")
            update_response = supabase.table("processing_status").update(update_data).eq("task_id", task_id).execute()
            print(f"Resposta da atualização: {update_response}")

    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        success = False
        if automation and automation.task_id:
            update_data = {
                "status": "error",
                "error": f"Erro durante a execução: {str(e)}",
                "error_at": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat(),
            }
            print(f"Atualizando status para: {json.dumps(update_data, indent=2)}")
            update_response = supabase.table("processing_status").update(update_data).eq("task_id", automation.task_id).execute()
            print(f"Resposta da atualização: {update_response}")

    finally:
        if automation:
            automation.close()
        return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Executa o scraping da Unimed')
    parser.add_argument('--start_date', type=str, help='Data inicial no formato dd/mm/yyyy')
    parser.add_argument('--end_date', type=str, help='Data final no formato dd/mm/yyyy')
    parser.add_argument('--max_guides', type=int, help='Número máximo de guias a serem processadas')
    
    args = parser.parse_args()
    
    # Se não forem fornecidas datas, usa o dia atual
    if not args.start_date:
        args.start_date = datetime.now().strftime("%d/%m/%Y")
    if not args.end_date:
        args.end_date = args.start_date
        
    print(f"Executando scraping com parâmetros: start_date={args.start_date}, end_date={args.end_date}, max_guides={args.max_guides}")
    executar_scraping(args.start_date, args.end_date, args.max_guides)
