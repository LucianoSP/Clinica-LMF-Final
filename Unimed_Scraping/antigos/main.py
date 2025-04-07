from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from selenium_script_full import UnimedAutomation
from pydantic import BaseModel
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



# Configurações Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Cliente Supabase
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load environment variables
UNIMED_USERNAME = os.getenv("UNIMED_USERNAME")
UNIMED_PASSWORD = os.getenv("UNIMED_PASSWORD")

# Models
class LoginData(BaseModel):
    username: str
    password: str

class GuideSearch(BaseModel):
    guide_number: str

# Add new model for guide search
class GuideSearchParams(BaseModel):
    start_date: str
    end_date: str
    max_guides: int = None

# Adicionar novo modelo para status de processamento
class ProcessingStatus(BaseModel):
    status: str
    total_guides: int
    processed_guides: int = 0
    error: str = None
    task_id: str = None

@app.get("/health")
def health_check():
    try:
        if supabase:
            response = supabase.table("processing_status").select("*").limit(1).execute()
            return {"status": "healthy", "database": "connected"}
        return {"status": "healthy", "database": "not configured"}
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/login")
async def test_login():
    """Testa o login no portal Unimed usando credenciais do ambiente"""
    automation = None
    try:
        if not UNIMED_USERNAME or not UNIMED_PASSWORD:
            raise HTTPException(
                status_code=500,
                detail="Credenciais não configuradas no ambiente"
            )

        automation = UnimedAutomation()
        automation.setup_driver()

        result = automation.login(UNIMED_USERNAME, UNIMED_PASSWORD)

        if result:
            return {"status": "success", "message": "Login realizado com sucesso"}
        else:
            raise HTTPException(status_code=401, detail="Login falhou")

    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()

@app.post("/exams")
async def get_finished_exams(params: GuideSearchParams):
    """Acessa a página de exames realizados e captura as guias"""
    automation = None
    try:
        if not UNIMED_USERNAME or not UNIMED_PASSWORD:
            raise HTTPException(
                status_code=500,
                detail="Credenciais não configuradas no ambiente"
            )

        automation = UnimedAutomation()
        automation.setup_driver()

        # Realiza login
        logger.info("Realizando login...")
        if not automation.login(UNIMED_USERNAME, UNIMED_PASSWORD):
            raise HTTPException(status_code=401, detail="Login falhou")

        # Navega para a página de exames realizados
        logger.info("Navegando para página de exames realizados...")
        if not automation.navigate_to_finished_exams():
            raise HTTPException(
                status_code=500, 
                detail="Falha ao navegar para página de exames"
            )

        # Captura as guias do período
        logger.info(f"Capturando guias de {params.start_date} até {params.end_date}...")
        guides = automation.capture_guides(
            params.start_date,
            params.end_date,
            params.max_guides
        )

        return {
            "status": "success",
            "message": f"Encontradas {len(guides)} guias",
            "guides": guides
        }

    except Exception as e:
        logger.error(f"Erro ao acessar exames: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()

@app.post("/capture-guides")
async def capture_guides(params: GuideSearchParams):
    """Captura guias dentro do período especificado e salva na fila"""
    automation = None
    task_id = None
    
    try:
        if not supabase:
            raise HTTPException(status_code=500, detail="Banco de dados não configurado")

        # Cria registro de status do processamento
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        processing_status = {
            "status": "processing",
            "total_guides": 0,
            "processed_guides": 0,
            "task_id": task_id,
            "error": None
        }
        
        # Insere status inicial
        status_response = supabase.table("processing_status").insert(processing_status).execute()
        
        automation = UnimedAutomation()
        automation.setup_driver()

        # Login e navegação
        if not automation.login(UNIMED_USERNAME, UNIMED_PASSWORD):
            raise HTTPException(status_code=401, detail="Login falhou")

        if not automation.navigate_to_finished_exams():
            raise HTTPException(status_code=500, detail="Falha ao navegar para exames")

        # Realiza busca
        guides_info = []
        automation.fill_date_fields(params.start_date, params.end_date)
        automation.search_exams()

        # Captura guias
        guide_dates = automation.search_and_get_guide_dates("")
        
        if guide_dates:
            for guide_data in guide_dates:
                queue_item = {
                    "numero_guia": guide_data["guide_number_text"],
                    "data_execucao": guide_data["date"],
                    "status": "pending",
                    "task_id": task_id,
                    "attempts": 0,
                    "error": None
                }
                guides_info.append(queue_item)

                # Verifica limite de guias
                if params.max_guides and len(guides_info) >= params.max_guides:
                    break

        # Insere guias na fila
        if guides_info:
            supabase.table("guias_queue").insert(guides_info).execute()

        # Atualiza status do processamento
        total_guides = len(guides_info)
        supabase.table("processing_status").update({
            "total_guides": total_guides,
            "status": "waiting_processing"
        }).eq("task_id", task_id).execute()

        return {
            "status": "success",
            "message": f"Encontradas {total_guides} guias",
            "task_id": task_id,
            "guides": guides_info
        }

    except Exception as e:
        logger.error(f"Erro na captura de guias: {str(e)}")
        if task_id:
            supabase.table("processing_status").update({
                "status": "failed",
                "error": str(e)
            }).eq("task_id", task_id).execute()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()

@app.get("/test-google")
async def test_google():
    """Testa o acesso ao Google"""
    automation = None
    try:
        automation = UnimedAutomation()
        automation.setup_driver()

        result = automation.test_google()
        return result

    except Exception as e:
        logger.error(f"Erro no teste do Google: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()


@app.get("/test-urls")
async def test_unimed_urls():
    """Testa acesso a diferentes URLs da Unimed"""
    automation = None
    try:
        automation = UnimedAutomation()
        automation.setup_driver()

        results = automation.test_urls()
        return {
            "status": "completed",
            "results": results
        }

    except Exception as e:
        logger.error(f"Erro no teste de URLs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if automation:
            automation.close()


@app.get("/check-cloudflare")
async def check_cloudflare():
    """Verifica se os sites estão usando Cloudflare"""
    import requests
    import socket

    urls = [
        "https://www.uol.com.br",
        "https://www.google.com",
        "https://www.unimed.coop.br/site/",
        "https://www.unimedgoiania.coop.br",
        "https://sgucard.unimedgoiania.coop.br"
    ]

    results = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/132.0.0.0 Safari/537.36'
    }

    for url in urls:
        try:
            print(f"\nVerificando: {url}")
            # Resolve IP
            domain = url.split("//")[1].split("/")[0]
            ip = socket.gethostbyname(domain)

            # Faz requisição
            response = requests.get(url, headers=headers, timeout=10)

            # Verifica headers do Cloudflare
            cloudflare_headers = {
                'cf-ray': response.headers.get('cf-ray'),
                'cf-cache-status': response.headers.get('cf-cache-status'),
                'server': response.headers.get('server')
            }

            result = {
                "url": url,
                "ip": ip,
                "status_code": response.status_code,
                "is_cloudflare": any([
                    'cloudflare' in str(response.headers.get('server', '')).lower(),
                    'cf-ray' in response.headers,
                    ip.startswith(('104.16.', '172.64.', '104.18.'))
                ]),
                "cloudflare_headers": cloudflare_headers
            }

            print(f"Status: {response.status_code}")
            print(f"IP: {ip}")
            print(f"Cloudflare headers: {cloudflare_headers}")

        except Exception as e:
            print(f"Erro ao verificar {url}: {str(e)}")
            result = {
                "url": url,
                "error": str(e)
            }

        results.append(result)

    return {
        "status": "completed",
        "results": results
    }

@app.get("/test-simple")
async def test_simple_request():
    """Testa acesso usando requests em vez de Selenium"""
    import requests

    urls = [
        "https://www.uol.com.br",
        "https://www.google.com",
        "https://www.unimed.coop.br/site/",
        "https://www.unimedgoiania.coop.br",
        "https://sgucard.unimedgoiania.coop.br",
        "https://sgucard.unimedgoiania.coop.br/cmagnet/Login.do"
    ]

    results = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/132.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    for url in urls:
        try:
            print(f"\nTentando acessar: {url}")
            response = requests.get(url, headers=headers, timeout=30)

            result = {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_length": len(response.content)
            }
            print(f"Status code: {response.status_code}")

        except Exception as e:
            print(f"Erro ao acessar {url}: {str(e)}")
            result = {
                "url": url,
                "error": str(e)
            }

        results.append(result)

    return {
        "status": "completed",
        "results": results,
        "server_ip": requests.get('https://api.ipify.org').text
    }