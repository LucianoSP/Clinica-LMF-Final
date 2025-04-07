"""
Script de exemplo para captura e processamento de sessões da Unimed
----------------------------------------------------------------------
Este é um exemplo simplificado de como o processo de captura e processamento
de sessões da Unimed funcionaria, utilizando o schema de banco criado.
"""
import os
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração básica de log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('unimed_scraping')

# Exemplo de conexão com o banco usando Supabase
import supabase
from supabase import create_client, Client

# Configurações
URL = os.environ.get("SUPABASE_URL", "")
KEY = os.environ.get("SUPABASE_KEY", "")
UNIMED_USERNAME = os.environ.get("UNIMED_USERNAME", "")
UNIMED_PASSWORD = os.environ.get("UNIMED_PASSWORD", "")
UNIMED_URL = os.environ.get("UNIMED_URL", "https://portal.unimed.com.br")

# Inicializar cliente Supabase
supabase: Client = create_client(URL, KEY)

class UnimedScraper:
    """Classe para realizar o scraping do site da Unimed"""
    
    def __init__(self):
        self.driver = None
        self.task_id = str(uuid.uuid4())
        
    def inicializar_driver(self):
        """Inicializa o driver Selenium com configurações adequadas"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Driver Selenium inicializado")
        
    def criar_task(self, start_date: str, end_date: str, max_guides: int = 1000):
        """Cria um registro de task no banco de dados"""
        task_data = {
            'task_id': self.task_id,
            'status': 'iniciado',
            'start_date': start_date,
            'end_date': end_date,
            'max_guides': max_guides
        }
        
        result = supabase.table('processing_status').insert(task_data).execute()
        logger.info(f"Task criada com ID: {self.task_id}")
        return result.data
        
    def fazer_login(self):
        """Realiza login no site da Unimed"""
        try:
            self.driver.get(UNIMED_URL)
            logger.info("Acessando site da Unimed")
            
            # Exemplo simplificado, ajustar conforme HTML do site
            username_field = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(UNIMED_USERNAME)
            password_field.send_keys(UNIMED_PASSWORD)
            
            submit_button = self.driver.find_element(By.ID, "submit-button")
            submit_button.click()
            
            # Aguarda carregamento da página após login
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, "dashboard"))
            )
            
            logger.info("Login realizado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao fazer login: {str(e)}")
            return False
            
    def navegar_para_exames(self):
        """Navega para a tela de exames finalizados"""
        try:
            # Exemplo simplificado - ajustar para o site real
            exames_menu = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Exames')]"))
            )
            exames_menu.click()
            
            exames_finalizados = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Finalizados')]"))
            )
            exames_finalizados.click()
            
            logger.info("Navegação para exames finalizados realizada com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao navegar para exames: {str(e)}")
            return False
            
    def aplicar_filtro_data(self, data_inicio: str, data_fim: str):
        """Aplica filtro de data na tela de exames"""
        try:
            # Exemplo simplificado - ajustar para o site real
            data_inicio_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "data-inicio"))
            )
            data_fim_field = self.driver.find_element(By.ID, "data-fim")
            
            data_inicio_field.clear()
            data_inicio_field.send_keys(data_inicio)
            
            data_fim_field.clear()
            data_fim_field.send_keys(data_fim)
            
            filtrar_button = self.driver.find_element(By.ID, "filtrar")
            filtrar_button.click()
            
            # Aguarda carregamento dos resultados
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "resultado-exames"))
            )
            
            logger.info(f"Filtro aplicado: {data_inicio} a {data_fim}")
            return True
        except Exception as e:
            logger.error(f"Erro ao aplicar filtro: {str(e)}")
            return False
            
    def extrair_sessoes_pagina(self) -> List[Dict]:
        """Extrai as sessões presentes na página atual"""
        sessoes = []
        try:
            # Exemplo simplificado - ajustar para o site real
            linhas_tabela = self.driver.find_elements(By.XPATH, "//table[@id='exames-tabela']/tbody/tr")
            
            for linha in linhas_tabela:
                try:
                    # Extrai dados básicos da linha da tabela
                    numero_guia = linha.find_element(By.XPATH, "./td[1]").text.strip()
                    data_atendimento = linha.find_element(By.XPATH, "./td[2]").text.strip()
                    paciente = linha.find_element(By.XPATH, "./td[3]").text.strip()
                    
                    # Clica no botão de detalhes para abrir modal
                    botao_detalhes = linha.find_element(By.XPATH, "./td//button[contains(@class, 'detalhes')]")
                    botao_detalhes.click()
                    
                    # Aguarda o modal carregar
                    modal = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "modal-detalhes"))
                    )
                    
                    # Extrai dados adicionais do modal
                    carteirinha = modal.find_element(By.XPATH, "//span[@id='carteirinha']").text.strip()
                    codigo_ficha = modal.find_element(By.XPATH, "//span[@id='codigo-ficha']").text.strip()
                    profissional = modal.find_element(By.XPATH, "//span[@id='profissional']").text.strip()
                    conselho = modal.find_element(By.XPATH, "//span[@id='conselho']").text.strip()
                    numero_conselho = modal.find_element(By.XPATH, "//span[@id='numero-conselho']").text.strip()
                    uf_conselho = modal.find_element(By.XPATH, "//span[@id='uf-conselho']").text.strip()
                    codigo_cbo = modal.find_element(By.XPATH, "//span[@id='cbo']").text.strip()
                    
                    # Fechar o modal
                    botao_fechar = modal.find_element(By.XPATH, "//button[@class='fechar']")
                    botao_fechar.click()
                    
                    # Formata a data para banco
                    data_obj = datetime.strptime(data_atendimento, "%d/%m/%Y %H:%M")
                    data_execucao = data_obj.date().isoformat()
                    
                    sessao = {
                        "numero_guia": numero_guia,
                        "data_atendimento_completa": data_atendimento,
                        "data_execucao": data_execucao,
                        "paciente_nome": paciente,
                        "paciente_carteirinha": carteirinha,
                        "codigo_ficha": codigo_ficha,
                        "profissional_executante": profissional,
                        "conselho_profissional": conselho.split(" ")[0] if " " in conselho else conselho,
                        "numero_conselho": numero_conselho,
                        "uf_conselho": uf_conselho,
                        "codigo_cbo": codigo_cbo,
                        "task_id": self.task_id,
                        "status": "pendente"
                    }
                    
                    sessoes.append(sessao)
                except Exception as e:
                    logger.error(f"Erro ao processar linha da tabela: {str(e)}")
                    continue
                    
            logger.info(f"Extraídas {len(sessoes)} sessões da página atual")
            return sessoes
        except Exception as e:
            logger.error(f"Erro ao extrair sessões da página: {str(e)}")
            return []
            
    def tem_proxima_pagina(self) -> bool:
        """Verifica se existe próxima página de resultados"""
        try:
            botao_proximo = self.driver.find_element(By.XPATH, "//button[contains(@class, 'proxima-pagina')]")
            return not "disabled" in botao_proximo.get_attribute("class")
        except:
            return False
            
    def ir_para_proxima_pagina(self) -> bool:
        """Navega para a próxima página de resultados"""
        try:
            botao_proximo = self.driver.find_element(By.XPATH, "//button[contains(@class, 'proxima-pagina')]")
            botao_proximo.click()
            
            # Aguarda carregamento da nova página
            WebDriverWait(self.driver, 20).until(
                EC.staleness_of(self.driver.find_element(By.CLASS_NAME, "resultado-exames"))
            )
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "resultado-exames"))
            )
            
            logger.info("Navegado para próxima página")
            return True
        except Exception as e:
            logger.error(f"Erro ao navegar para próxima página: {str(e)}")
            return False
            
    def salvar_sessoes(self, sessoes: List[Dict]) -> int:
        """Salva as sessões capturadas no banco de dados"""
        if not sessoes:
            return 0
            
        try:
            result = supabase.table('unimed_sessoes_capturadas').insert(sessoes).execute()
            return len(result.data)
        except Exception as e:
            logger.error(f"Erro ao salvar sessões no banco: {str(e)}")
            return 0
            
    def processar_sessoes(self, limit: int = 100) -> Dict:
        """Processa as sessões pendentes inserindo na tabela de execuções"""
        resultados = {
            "processadas": 0,
            "com_erro": 0,
            "ignoradas": 0
        }
        
        try:
            # Busca sessões pendentes
            query = supabase.table('unimed_sessoes_capturadas')\
                .select('id')\
                .eq('status', 'pendente')\
                .eq('task_id', self.task_id)\
                .limit(limit)
                
            response = query.execute()
            
            if not response.data:
                logger.info("Nenhuma sessão pendente encontrada")
                return resultados
                
            for sessao in response.data:
                try:
                    # Chama a função do banco para processar a sessão
                    rpc_response = supabase.rpc(
                        'inserir_execucao_unimed', 
                        {'sessao_id': sessao['id']}
                    ).execute()
                    
                    if rpc_response.data:
                        resultados["processadas"] += 1
                    else:
                        # Significa que a função retornou NULL (guia não encontrada)
                        resultados["ignoradas"] += 1
                except Exception as e:
                    logger.error(f"Erro ao processar sessão {sessao['id']}: {str(e)}")
                    resultados["com_erro"] += 1
                    
                    # Marca a sessão com erro
                    supabase.table('unimed_sessoes_capturadas')\
                        .update({'status': 'erro', 'error': str(e)})\
                        .eq('id', sessao['id'])\
                        .execute()
                        
            logger.info(f"Processamento concluído: {resultados}")
            return resultados
        except Exception as e:
            logger.error(f"Erro geral no processamento de sessões: {str(e)}")
            return resultados
            
    def atualizar_status_task(self, status: str, error: Optional[str] = None):
        """Atualiza o status da task no banco de dados"""
        data = {
            'status': status
        }
        
        if error:
            data['error'] = error
            data['error_at'] = datetime.now().isoformat()
            
        supabase.table('processing_status')\
            .update(data)\
            .eq('task_id', self.task_id)\
            .execute()
            
        logger.info(f"Status da task atualizado para: {status}")
            
    def executar(self, start_date: str, end_date: str, max_guides: int = 1000):
        """Executa o processo completo de scraping"""
        try:
            # Inicializa driver e cria task
            self.inicializar_driver()
            self.criar_task(start_date, end_date, max_guides)
            
            # Atualiza status
            self.atualizar_status_task('iniciado')
            
            # Login e navegação
            if not self.fazer_login():
                self.atualizar_status_task('error', 'Falha ao fazer login')
                return False
                
            if not self.navegar_para_exames():
                self.atualizar_status_task('error', 'Falha ao navegar para tela de exames')
                return False
                
            # Aplicar filtro de data
            if not self.aplicar_filtro_data(start_date, end_date):
                self.atualizar_status_task('error', 'Falha ao aplicar filtro de data')
                return False
                
            # Atualiza status
            self.atualizar_status_task('capturing')
            
            # Captura sessões
            total_capturado = 0
            pagina_atual = 1
            
            while True:
                # Extrai sessões da página atual
                sessoes = self.extrair_sessoes_pagina()
                
                # Salva sessões no banco
                salvos = self.salvar_sessoes(sessoes)
                total_capturado += salvos
                
                logger.info(f"Página {pagina_atual}: {salvos} sessões salvas. Total: {total_capturado}")
                
                # Verifica se atingiu o limite máximo
                if total_capturado >= max_guides:
                    logger.info(f"Limite máximo de {max_guides} guias atingido")
                    break
                    
                # Verifica se tem próxima página
                if not self.tem_proxima_pagina():
                    logger.info("Última página atingida")
                    break
                    
                # Vai para próxima página
                if not self.ir_para_proxima_pagina():
                    logger.error("Erro ao navegar para próxima página")
                    break
                    
                pagina_atual += 1
                
            # Atualiza status para processamento
            self.atualizar_status_task('processing')
            
            # Processa as sessões capturadas
            resultados = self.processar_sessoes(limit=total_capturado)
            
            # Determina status final
            status_final = 'completed'
            if resultados["com_erro"] > 0 and resultados["processadas"] > 0:
                status_final = 'completed_with_errors'
            elif resultados["processadas"] == 0 and resultados["com_erro"] > 0:
                status_final = 'error'
                
            # Atualiza estatísticas e status final
            supabase.table('processing_status')\
                .update({
                    'status': status_final,
                    'total_guides': total_capturado,
                    'processed_guides': resultados["processadas"],
                    'completed_at': datetime.now().isoformat(),
                    'error': f"Processadas: {resultados['processadas']}, Erros: {resultados['com_erro']}, Ignoradas: {resultados['ignoradas']}"
                })\
                .eq('task_id', self.task_id)\
                .execute()
                
            logger.info(f"Processamento finalizado com status: {status_final}")
            return True
        except Exception as e:
            logger.error(f"Erro geral no processo: {str(e)}")
            self.atualizar_status_task('error', str(e))
            return False
        finally:
            # Fecha o driver
            if self.driver:
                self.driver.quit()

# Exemplo de uso
if __name__ == "__main__":
    # Define datas para scraping
    data_final = datetime.now().date()
    data_inicial = data_final - timedelta(days=7)  # Últimos 7 dias
    
    # Formata datas no padrão esperado pelo site
    start_date = data_inicial.strftime("%d/%m/%Y")
    end_date = data_final.strftime("%d/%m/%Y")
    
    # Executa o scraping
    scraper = UnimedScraper()
    scraper.executar(start_date, end_date, max_guides=500) 