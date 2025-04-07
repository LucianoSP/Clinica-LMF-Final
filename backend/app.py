import os
import logging
from fastapi import FastAPI, HTTPException, Request, status, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import List
import tempfile
from datetime import datetime
from .config.config import supabase
from .services.storage_r2 import storage
from .utils.pdf_processor import extract_info_from_pdf
from .repositories.database_supabase import create_execucao, create_storage, get_supabase_client
from .utils.date_utils import DateEncoder
import json
import time
from logging.config import dictConfig
from .config.logging_config import log_config

# Importar routers
from .routes.paciente import router as paciente_router
from .routes.carteirinha import router as carteirinha_router
from .routes.procedimento import router as procedimento_router
from .routes.plano_saude import router as plano_saude_router
from .routes.guia import router as guia_router
from .routes.ficha import router as ficha_router
from .routes.sessao import router as sessao_router
from .routes.execucao import router as execucao_router
from .routes.divergencia import router as divergencia_router
from .routes.storage import router as storage_router
from .routes.auditoria import router as auditoria_router
from .routes.auditoria_execucao import router as auditoria_execucao_router
from .routes.upload import router as upload_router
from .routes.agendamento import router as agendamento_router
from .routes.importacao_routes import router as importacao_router
from .routes.vinculacao import router as vinculacao_router
from .schemas.responses import StandardResponse
from .routes import importacao_routes
from .routes import tabelas_aba_routes

# Criar diretórios necessários
logs_dir = os.path.join(os.getcwd(), "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Criar diretório para arquivos temporários se não existir
temp_dir = os.path.join(os.getcwd(), "temp")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Configurar logging
dictConfig(log_config)
logger = logging.getLogger("backend")

# Criar diretório para arquivos temporários se não existir
TEMP_DIR = "temp"
GUIAS_RENOMEADAS_DIR = "guias_renomeadas"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
if not os.path.exists(GUIAS_RENOMEADAS_DIR):
    os.makedirs(GUIAS_RENOMEADAS_DIR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    try:
        yield
    finally:
        pass


# Configuração do FastAPI
app = FastAPI(
    title="Clinica API",
    description="API da Clínica",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=JSONResponse
)

# Configurar o encoder JSON padrão para lidar com datas
def custom_json_handler(obj):
    return json.dumps(obj, cls=DateEncoder)

app.json_encoder = DateEncoder

# Middleware para CORS - Permitir todas as origens para facilitar o desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} {response.status_code} {process_time:.2f}s")
    return response

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code,
                        content=StandardResponse(success=False,
                                                 error=exc.detail,
                                                 message=None).model_dump())

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": f"Erro interno do servidor: {str(exc)}",
            "data": None
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_msg = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        errors.append(error_msg)
    return JSONResponse(
        status_code=422,
        content={"detail": errors}
    )

@app.get("/")
async def root():
    return {"message": "API está funcionando"}

# Endpoint de health-check
@app.get("/health-check")
async def health_check():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "version": app.version
    }

# Registrar rotas
app.include_router(paciente_router,
                   prefix="/api/pacientes",
                   tags=["Pacientes"])
app.include_router(carteirinha_router,
                   prefix="/api/carteirinhas",
                   tags=["Carteirinhas"])
app.include_router(procedimento_router,
                   prefix="/api/procedimentos",
                   tags=["Procedimentos"])
app.include_router(plano_saude_router,
                   prefix="/api/planos-saude",
                   tags=["Planos de Saúde"])
app.include_router(guia_router, prefix="/api/guias", tags=["Guias"])
app.include_router(ficha_router, prefix="/api/fichas", tags=["Fichas"])
app.include_router(sessao_router, prefix="/api/sessoes", tags=["Sessões"])
app.include_router(execucao_router,
                   prefix="/api/execucoes",
                   tags=["Execuções"])
app.include_router(divergencia_router,
                   prefix="/api/divergencias",
                   tags=["Divergências"])
app.include_router(auditoria_router,
                   prefix="/api/auditoria",
                   tags=["Auditoria"])
app.include_router(auditoria_execucao_router,
                   prefix="/api/auditoria-execucoes",
                   tags=["Auditoria Execuções"])
app.include_router(storage_router,
                   prefix="/api/storage",
                   tags=["Storage"])
app.include_router(upload_router,
                   prefix="/api",
                   tags=["Upload PDF"],
                   include_in_schema=True)

app.include_router(agendamento_router,
                   prefix="/api/agendamentos",
                   tags=["Agendamentos"])
app.include_router(importacao_router,
                   prefix="/api/importacao",
                   tags=["Importação"])
app.include_router(tabelas_aba_routes.router, prefix="/api/tabelas-aba", tags=["Tabelas ABA"])

# Registrar o novo router de vinculação
app.include_router(vinculacao_router,
                   prefix="/api/vinculacoes",
                   tags=["Vinculações"])


# Rotas para documentação
@app.get("/docs/instrucoes", tags=["Documentação"])
async def listar_arquivos_documentacao():
    """Lista todos os arquivos de documentação disponíveis na pasta instrucoes"""
    try:
        # Lista arquivos na pasta instrucoes
        arquivos = os.listdir("instrucoes")
        # Filtra apenas arquivos markdown
        arquivos_md = [arquivo for arquivo in arquivos if arquivo.endswith(".md")]
        return arquivos_md
    except Exception as e:
        logger.error(f"Erro ao listar arquivos de documentação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar arquivos de documentação"
        )

@app.get("/docs/instrucoes/{nome_arquivo}", tags=["Documentação"])
async def obter_arquivo_documentacao(nome_arquivo: str):
    """Obtém o conteúdo de um arquivo de documentação específico da pasta instrucoes"""
    try:
        # Verifica se o arquivo solicitado existe
        caminho_arquivo = os.path.join("instrucoes", nome_arquivo)
        if not os.path.exists(caminho_arquivo):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo '{nome_arquivo}' não encontrado"
            )
        
        # Verifica se o arquivo solicitado é um markdown
        if not nome_arquivo.endswith(".md"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apenas arquivos markdown (.md) são permitidos"
            )
        
        # Lê o conteúdo do arquivo
        with open(caminho_arquivo, "r", encoding="utf-8") as file:
            conteudo = file.read()
        
        return PlainTextResponse(conteudo)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de documentação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao ler arquivo de documentação"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)