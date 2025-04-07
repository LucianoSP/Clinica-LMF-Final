import os
import json
import time
import logging
import base64
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import ValidationError

from config.config import get_supabase_client
from services.storage_r2 import storage
from utils.pdf_processor import extract_info_from_pdf
from utils.date_utils import formatar_data
from utils.json_encoder import CustomEncoder

# Configurar logger
logger = logging.getLogger(__name__)
router = APIRouter()

def format_filename(dados_ficha: dict) -> str:
    """
    Formata o nome do arquivo seguindo o padrão: codigo_ficha - nome_paciente - data_envio.pdf
    """
    data_envio = datetime.now().strftime("%Y-%m-%d")
    
    # Verificar se os campos necessários existem
    codigo_ficha = dados_ficha.get('codigo_ficha', 'sem_codigo')
    
    # O nome do paciente pode estar em 'paciente_nome' ou 'nome_paciente'
    nome_paciente = dados_ficha.get('paciente_nome', 
                   dados_ficha.get('nome_paciente', 'sem_nome'))
    
    # Log para depuração
    logger.info(f"Formatando nome do arquivo com: codigo={codigo_ficha}, nome={nome_paciente}, data={data_envio}")
    
    nome_arquivo = f"{codigo_ficha} - {nome_paciente} - {data_envio}.pdf"
    
    # Remove caracteres inválidos para nomes de arquivo
    nome_arquivo = "".join(c for c in nome_arquivo if c.isalnum() or c in "- _.")
    
    logger.info(f"Nome do arquivo formatado: {nome_arquivo}")
    return nome_arquivo

@router.post("/upload-pdf-unificado")
async def upload_pdf_unificado(
    files: List[UploadFile] = File(...),
    modelo_ia: str = Form("claude"),
    prompt_path: Optional[str] = Form(None)
):
    """
    Endpoint unificado para upload de PDF e extração de dados.
    
    Este endpoint verifica automaticamente se a guia existe no sistema:
    - Se existir: salva os dados na tabela 'fichas'
    - Se não existir: salva os dados na tabela 'fichas_pendentes'
    
    Args:
        files: Lista de arquivos PDF
        modelo_ia: Modelo de IA a ser usado (claude, gemini, mistral)
        prompt_path: Caminho para um arquivo de prompt personalizado (opcional)
    """
    resultados = []
    start_time = time.time()
    
    for file in files:
        try:
            resultado = await process_pdf_unificado(file, modelo_ia, prompt_path)
            resultados.append(resultado)
        except Exception as e:
            resultados.append({"arquivo": file.filename, "erro": str(e), "status": "falha"})
    
    end_time = time.time()
    logger.info(f"Tempo total de processamento: {end_time - start_time:.2f} segundos")
    
    return {"resultados": resultados}

async def process_pdf_unificado(file: UploadFile, modelo_ia: str = "claude", prompt_path: Optional[str] = None) -> Dict:
    """
    Processa um arquivo PDF para extrair informações e criar registros no banco de dados.
    Verifica automaticamente se a guia existe e salva na tabela apropriada.
    
    Args:
        file: Arquivo PDF para processamento
        modelo_ia: Modelo de IA a ser usado (claude, gemini, mistral)
        prompt_path: Caminho para um arquivo de prompt personalizado (opcional)
        
    Returns:
        Dicionário com os resultados do processamento
    """
    start_time = time.time()

    # Definir API key baseado no modelo selecionado
    api_key = None
    if modelo_ia == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
    elif modelo_ia == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
    elif modelo_ia == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
    else:
        raise HTTPException(
            status_code=400, detail=f"Modelo de IA não suportado: {modelo_ia}"
        )

    if not api_key:
        raise HTTPException(
            status_code=500, detail=f"Chave API para o modelo {modelo_ia} não configurada"
        )

    # Criar diretório temporário para arquivos se não existir
    temp_dir = "temp_pdf"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Salvar arquivo para processamento
    temp_file_path = f"{temp_dir}/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Extrair informações do PDF
        resultado_extracao = await extract_info_from_pdf(
            temp_file_path, api_key, modelo_ia, prompt_path
        )
        
        # Log da resposta completa da IA
        logger.info(f"Resposta da IA ({modelo_ia}) para {file.filename}:")
        logger.info(json.dumps(
            resultado_extracao,
            cls=CustomEncoder,
            indent=2,
            ensure_ascii=False
        ))
        
        if resultado_extracao["status_validacao"] == "sucesso":
            logger.info("Validação do resultado: sucesso")
            
            # Obter dados extraídos
            dados_ficha = resultado_extracao["dados_ficha"]
            
            # Formatar nome do arquivo
            nome_arquivo = format_filename(dados_ficha)
            
            # Verificar se o nome do arquivo foi gerado corretamente
            if not nome_arquivo or nome_arquivo == "sem_codigo - sem_nome - .pdf":
                logger.warning("Nome do arquivo não foi gerado corretamente. Usando formato alternativo.")
                # Usar um formato alternativo como fallback
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                codigo = dados_ficha.get('codigo_ficha', 'sem_codigo')
                nome_arquivo = f"{codigo}_{timestamp}.pdf"
            
            # Conectar ao Supabase
            supabase = get_supabase_client()
            
            # Verificar se a guia existe no sistema
            numero_guia = dados_ficha.get('numero_guia')
            
            guia_existe = False
            if numero_guia:
                # Buscar a guia no banco de dados
                guia_response = supabase.table("guias").select("id").eq("numero_guia", numero_guia).execute()
                
                if guia_response.data and len(guia_response.data) > 0:
                    guia_existe = True
                    guia_id = guia_response.data[0]["id"]
                    logger.info(f"Guia {numero_guia} encontrada com ID {guia_id}")
            
            # Caminho de armazenamento e destino no R2 depende da existência da guia
            if guia_existe:
                caminho_armazenamento = "fichas"
            else:
                caminho_armazenamento = "fichas_pendentes"
                
            dest_name = f"{caminho_armazenamento}/{nome_arquivo}"
            logger.info(f"Caminho completo no R2: {dest_name}")
            
            # Fazer upload para o R2
            url = storage.upload_file(temp_file_path, dest_name)
            
            if not url:
                logger.error(f"Falha no upload do arquivo para R2: {dest_name}")
                return {
                    "filename": file.filename,
                    "status": "error",
                    "message": "Falha no upload do arquivo para o armazenamento."
                }
                
            logger.info(f"Upload para R2 concluído. URL: {url}")
            
            # Registrar arquivo no Supabase (tabela storage)
            storage_data = {
                "nome": nome_arquivo,
                "url": url,
                "size": os.path.getsize(temp_file_path),
                "content_type": "application/pdf",
                "tipo_referencia": "ficha" if guia_existe else "ficha_pendente"
            }
            
            logger.info("Dados para storage:")
            logger.info(json.dumps(storage_data, cls=CustomEncoder, indent=2))
            
            # Criar registro na tabela storage
            storage_response = supabase.table("storage").insert(storage_data).execute()
            
            if not storage_response.data:
                logger.error("Falha ao registrar arquivo na tabela storage")
                return {
                    "filename": file.filename,
                    "status": "error",
                    "message": "Falha ao registrar arquivo no banco de dados."
                }
                
            storage_id = storage_response.data[0]["id"]
            
            # Adicionar URL do arquivo aos dados da ficha
            dados_ficha["arquivo_digitalizado"] = url
            
            # Converter datas se necessário
            if "data_atendimento" in dados_ficha and dados_ficha["data_atendimento"]:
                try:
                    data_br = formatar_data(dados_ficha["data_atendimento"])
                    data_obj = datetime.strptime(data_br, "%d/%m/%Y")
                    dados_ficha["data_atendimento"] = data_obj.strftime("%Y-%m-%d")
                except Exception as e:
                    logger.warning(f"Erro ao converter data: {str(e)}")
                    # Se falhar a conversão, mantém o valor original
            
            # Dependendo da existência da guia, salvar na tabela apropriada
            if guia_existe:
                # Salvar na tabela de fichas
                try:
                    ficha_data = {
                        "storage_id": storage_id,
                        "codigo_ficha": dados_ficha.get("codigo_ficha"),
                        "numero_guia": dados_ficha.get("numero_guia"),
                        "paciente_nome": dados_ficha.get("paciente_nome"),
                        "paciente_carteirinha": dados_ficha.get("paciente_carteirinha"),
                        "arquivo_digitalizado": url,
                        "status": "pendente",
                        "data_atendimento": dados_ficha.get("data_atendimento"),
                        "total_sessoes": dados_ficha.get("total_sessoes", 1)
                    }
                    
                    ficha_response = supabase.table("fichas").insert(ficha_data).execute()
                    
                    if ficha_response.data:
                        logger.info(f"Ficha criada com sucesso: {ficha_response.data[0].get('id')}")
                        return {
                            "filename": file.filename,
                            "status": "success",
                            "message": "Arquivo processado e ficha criada com sucesso.",
                            "ficha_id": ficha_response.data[0].get('id'),
                            "url": url
                        }
                    else:
                        logger.error("Falha ao criar ficha")
                        return {
                            "filename": file.filename,
                            "status": "error",
                            "message": "Falha ao criar ficha no banco de dados."
                        }
                except Exception as e:
                    logger.error(f"Erro ao criar ficha: {str(e)}")
                    return {
                        "filename": file.filename,
                        "status": "error",
                        "message": f"Erro ao criar ficha: {str(e)}"
                    }
            else:
                # Salvar na tabela de fichas_pendentes
                try:
                    pendente_data = {
                        "storage_id": storage_id,
                        "dados_extraidos": json.loads(json.dumps(dados_ficha, cls=CustomEncoder)),
                        "status": "pendente",
                        "arquivo_url": url,
                        "numero_guia": dados_ficha.get("numero_guia"),
                        "paciente_nome": dados_ficha.get("paciente_nome"),
                        "paciente_carteirinha": dados_ficha.get("paciente_carteirinha"),
                        "data_atendimento": dados_ficha.get("data_atendimento"),
                        "total_sessoes": dados_ficha.get("total_sessoes"),
                        "codigo_ficha": dados_ficha.get("codigo_ficha"),
                        "observacoes": "Guia não encontrada no sistema"
                    }
                    
                    pendente_response = supabase.table("fichas_pendentes").insert(pendente_data).execute()
                    
                    if pendente_response.data:
                        logger.info(f"Ficha pendente criada: {pendente_response.data[0].get('id')}")
                        return {
                            "filename": file.filename,
                            "status": "success",
                            "message": "Arquivo processado e armazenado como ficha pendente (guia não encontrada).",
                            "pendente_id": pendente_response.data[0].get('id'),
                            "url": url
                        }
                    else:
                        logger.error("Falha ao criar ficha pendente")
                        return {
                            "filename": file.filename,
                            "status": "error",
                            "message": "Falha ao criar ficha pendente no banco de dados."
                        }
                except Exception as e:
                    logger.error(f"Erro ao criar ficha pendente: {str(e)}")
                    return {
                        "filename": file.filename,
                        "status": "error",
                        "message": f"Erro ao criar ficha pendente: {str(e)}"
                    }
        else:
            # Falha na extração dos dados
            logger.warning(f"Falha na extração de dados: {resultado_extracao.get('erro', 'Erro desconhecido')}")
            return {
                "filename": file.filename,
                "status": "error",
                "message": f"Falha na extração de dados: {resultado_extracao.get('erro', 'Erro desconhecido')}"
            }
            
    except Exception as e:
        logger.error(f"Erro geral ao processar PDF {file.filename}: {str(e)}")
        return {
            "filename": file.filename,
            "status": "error",
            "message": f"Erro geral: {str(e)}"
        }
    finally:
        # Limpar arquivo temporário
        try:
            os.unlink(temp_file_path)
            logger.info(f"Arquivo temporário removido: {temp_file_path}")
        except Exception as e:
            logger.warning(f"Não foi possível remover arquivo temporário: {str(e)}")
        
        end_time = time.time()
        logger.info(f"Tempo de processamento para {file.filename}: {end_time - start_time:.2f} segundos") 