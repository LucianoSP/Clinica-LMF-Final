import os
import tempfile
import logging
import json
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.services.storage_r2 import storage
from backend.utils.pdf_processor import extract_info_from_pdf
from backend.utils.date_utils import formatar_data, format_date, DATE_FIELDS, DateEncoder
from backend.repositories.database_supabase import create_storage, get_supabase_client
from uuid import UUID
import time
from fastapi import HTTPException
import uuid

# Configurar logger com formato mais detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

# Lista de modelos de IA suportados
MODELOS_IA = ["claude", "gemini", "mistral"]

class CustomEncoder(DateEncoder):
    """
    Encoder JSON personalizado que estende DateEncoder para lidar também com DataFrames
    """
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        # Delega para o DateEncoder para datas e outros tipos
        return super().default(obj)

def is_valid_uuid(uuid_string: str) -> bool:
    try:
        UUID(uuid_string)
        return True
    except ValueError:
        return False

def convert_to_uuid(id_str: str) -> str:
    """Converte um ID numérico para UUID se necessário"""
    if is_valid_uuid(id_str):
        return id_str
    
    # Se não for UUID, cria um UUID v4 fixo baseado no número
    numeric_id = id_str.zfill(12)
    return f"00000000-0000-4000-8000-{numeric_id}"

def serialize_result(obj):
    """Serializa objetos para JSON, tratando tipos especiais como DataFrames"""
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    # DateEncoder já cuida de datas e UUIDs
    return str(obj)

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

def convert_all_date_fields(data: dict) -> dict:
    """
    Converte todos os campos de data conhecidos em um dicionário para o formato ISO.
    Utiliza as funções do date_utils.py.
    """
    # Lista de campos de data que podem estar presentes nos dados da ficha
    date_fields = [
        'data_atendimento',
        'data_nascimento',
        'data_execucao',
        'data_inicio',
        'data_fim',
        'data_validade'
    ] + DATE_FIELDS  # Adiciona os campos padrão definidos em date_utils.py
    
    # Remove duplicatas
    date_fields = list(set(date_fields))
    
    for field in date_fields:
        if field in data and data[field] and isinstance(data[field], str):
            original_value = data[field]
            try:
                # Primeiro formata para DD/MM/YYYY usando a função robusta
                data_br = formatar_data(data[field])
                # Depois converte para YYYY-MM-DD para o Supabase
                data_obj = datetime.strptime(data_br, "%d/%m/%Y")
                data[field] = data_obj.strftime("%Y-%m-%d")
                
                if original_value != data[field]:
                    logger.info(f"Campo '{field}' convertido de '{original_value}' para '{data[field]}'")
            except ValueError as e:
                logger.error(f"Erro ao converter data '{data[field]}': {str(e)}")
    
    return data

@router.post("/upload-pdf")
async def upload_pdf(
    files: List[UploadFile] = File(...),
    modelo_ia: str = Form("claude"),
    prompt_path: Optional[str] = Form(None)
):
    """
    Endpoint para upload de PDF e extração de dados.
    
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
            resultado = await process_pdf(file, modelo_ia, prompt_path)
            resultados.append(resultado)
        except Exception as e:
            resultados.append({"arquivo": file.filename, "erro": str(e), "status": "falha"})
    
    end_time = time.time()
    logger.info(f"Tempo total de processamento: {end_time - start_time:.2f} segundos")
    
    return {"resultados": resultados}

async def process_pdf(file: UploadFile, modelo_ia: str = "claude", prompt_path: Optional[str] = None) -> Dict:
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
            
            # Tentar obter o paciente_id a partir da carteirinha extraída
            paciente_id_encontrado = None
            numero_carteirinha_extraido = dados_ficha.get('paciente_carteirinha')
            supabase = get_supabase_client() # Garante que temos a conexão
            
            if numero_carteirinha_extraido:
                try:
                    carteirinha_response = supabase.table("carteirinhas") \
                        .select("paciente_id") \
                        .eq("numero_carteirinha", numero_carteirinha_extraido) \
                        .eq("status", "ativa") \
                        .limit(1) \
                        .execute()
                    
                    if carteirinha_response.data:
                        paciente_id_encontrado = carteirinha_response.data[0].get('paciente_id')
                        if paciente_id_encontrado:
                            logger.info(f"Paciente ID {paciente_id_encontrado} encontrado para a carteirinha {numero_carteirinha_extraido}")
                        else:
                             logger.warning(f"Carteirinha {numero_carteirinha_extraido} encontrada, mas sem paciente_id associado.")
                    else:
                        # Se não encontrar ativa, tenta qualquer uma com o número
                        carteirinha_response_any = supabase.table("carteirinhas") \
                            .select("paciente_id") \
                            .eq("numero_carteirinha", numero_carteirinha_extraido) \
                            .limit(1) \
                            .execute()
                        if carteirinha_response_any.data:
                             paciente_id_encontrado = carteirinha_response_any.data[0].get('paciente_id')
                             if paciente_id_encontrado:
                                logger.info(f"Paciente ID {paciente_id_encontrado} encontrado (carteirinha inativa?) para {numero_carteirinha_extraido}")
                             else:
                                logger.warning(f"Carteirinha {numero_carteirinha_extraido} (inativa?) encontrada, mas sem paciente_id.")
                        else:
                            logger.warning(f"Nenhuma carteirinha encontrada para o número {numero_carteirinha_extraido}")
                except Exception as e:
                    logger.error(f"Erro ao buscar paciente_id para carteirinha {numero_carteirinha_extraido}: {e}")
            else:
                logger.warning("Número da carteirinha não foi extraído do PDF, não foi possível buscar paciente_id.")

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
            
            # Converter todos os campos de data
            dados_ficha = convert_all_date_fields(dados_ficha)
            if 'sessoes' in dados_ficha:
                for sessao in dados_ficha['sessoes']:
                    sessao = convert_all_date_fields(sessao)

            # Fazer upload para R2
            storage_url = storage.upload(
                file_path=temp_file_path, 
                destination_blob_name=f"{caminho_armazenamento}/{nome_arquivo}"
            )
            
            # Criar registro no Supabase Storage
            storage_record = create_storage(
                nome=nome_arquivo,
                url=storage_url,
                size=file.size,
                content_type=file.content_type,
                tipo_referencia=caminho_armazenamento # 'fichas' ou 'fichas_pendentes'
            )
            
            storage_id = storage_record["id"]
            
            # Inserir dados no Supabase (tabela fichas ou fichas_pendentes)
            if guia_existe:
                # Preparar dados para inserção em 'fichas'
                dados_para_inserir_ficha = {
                    "storage_id": storage_id,
                    "codigo_ficha": dados_ficha.get('codigo_ficha'),
                    "numero_guia": numero_guia,
                    "guia_id": guia_id, # Usar o ID da guia encontrada
                    "paciente_nome": dados_ficha.get('paciente_nome'),
                    "paciente_carteirinha": dados_ficha.get('paciente_carteirinha'),
                    "arquivo_digitalizado": storage_url,
                    "status": "pendente",
                    "data_atendimento": dados_ficha.get('data_atendimento'),
                    "total_sessoes": dados_ficha.get('total_sessoes'),
                    # Adicionar o paciente_id encontrado
                    "paciente_id": paciente_id_encontrado 
                }
                
                # Remover chaves com valor None antes de inserir
                dados_para_inserir_ficha = {k: v for k, v in dados_para_inserir_ficha.items() if v is not None}

                response_ficha = supabase.table("fichas").insert(dados_para_inserir_ficha).execute()
                
                if response_ficha.data:
                    logger.info(f"Ficha criada com sucesso: {response_ficha.data[0].get('id')}")
                    
                    # Gerar sessões automaticamente para a ficha
                    try:
                        ficha_id = response_ficha.data[0].get('id')
                        logger.info(f"Gerando sessões automaticamente para a ficha: {ficha_id}")
                        
                        # Verificar se já existem sessões para esta ficha
                        sessoes_existentes = supabase.table("sessoes").select("*").eq("ficha_id", ficha_id).execute()
                        
                        if not sessoes_existentes.data or len(sessoes_existentes.data) == 0:
                            # Obter o total de sessões da ficha
                            total_sessoes = dados_ficha.get("total_sessoes", 1)
                            logger.info(f"Total de sessões a serem criadas: {total_sessoes}")
                            
                            if total_sessoes > 0:
                                # Data base para as sessões (data da ficha)
                                data_atendimento = dados_ficha.get("data_atendimento")
                                logger.info(f"Data de atendimento original: {data_atendimento}")
                                
                                try:
                                    # Tentar diferentes formatos de data
                                    if isinstance(data_atendimento, str):
                                        try:
                                            # Tentar formato ISO
                                            data_base = datetime.fromisoformat(data_atendimento.replace("Z", "+00:00")).replace(tzinfo=None)
                                        except ValueError:
                                            try:
                                                # Tentar formato brasileiro
                                                data_base = datetime.strptime(data_atendimento, "%d/%m/%Y")
                                            except ValueError:
                                                # Tentar formato americano
                                                data_base = datetime.strptime(data_atendimento, "%Y-%m-%d")
                                    else:
                                        # Se não for string, usar data atual
                                        data_base = datetime.now()
                                        
                                    logger.info(f"Data base usada para sessões: {data_base.isoformat()}")
                                    
                                    # Gerar sessões
                                    sessoes = []
                                    
                                    # Verificar se temos registros individuais de sessão no JSON
                                    registros = None
                                    
                                    # Checar os possíveis locais onde os registros podem estar
                                    if "registros" in resultado_extracao:
                                        registros = resultado_extracao["registros"]
                                    elif "json" in resultado_extracao and "registros" in resultado_extracao["json"]:
                                        registros = resultado_extracao["json"]["registros"]
                                    elif "dataframe" in resultado_extracao:
                                        registros = resultado_extracao["dataframe"]
                                    
                                    logger.info(f"Registros encontrados: {json.dumps(registros, default=str) if registros else 'Nenhum'}")
                                    
                                    if registros and len(registros) > 0 and len(registros) == int(total_sessoes):
                                        logger.info(f"Usando informações de {len(registros)} registros individuais de sessões")
                                        # Usar as informações de cada registro individual
                                        for i, registro in enumerate(registros):
                                            logger.info(f"Processando registro {i+1}/{len(registros)}: {json.dumps(registro, default=str)}")
                                            
                                            # Processar possui_assinatura
                                            possui_assinatura = registro.get("possui_assinatura", False)
                                            if isinstance(possui_assinatura, str):
                                                possui_assinatura = possui_assinatura.lower() in ["true", "sim", "yes", "1"]
                                            logger.info(f"Valor de possui_assinatura para sessão {i+1}: {possui_assinatura}")
                                            
                                            # Processar data da sessão - usar a data do registro se disponível
                                            data_registro = registro.get("data_atendimento") or registro.get("data_sessao")
                                            
                                            if data_registro:
                                                # Tentar converter a data do registro
                                                try:
                                                    logger.info(f"Usando data específica do registro: {data_registro}")
                                                    # Formatar para padrão ISO
                                                    data_br = formatar_data(data_registro)
                                                    data_sessao_obj = datetime.strptime(data_br, "%d/%m/%Y")
                                                    data_sessao_iso = data_sessao_obj.date().isoformat()
                                                except Exception as e:
                                                    logger.warning(f"Erro ao processar data do registro, usando data calculada: {str(e)}")
                                                    # Fallback para o cálculo padrão
                                                    data_sessao = data_base + timedelta(days=i * 7)
                                                    data_sessao_iso = data_sessao.date().isoformat()
                                            else:
                                                # Se não tiver data no registro, usar o cálculo padrão
                                                data_sessao = data_base + timedelta(days=i * 7)
                                                data_sessao_iso = data_sessao.date().isoformat()
                                            
                                            logger.info(f"Data final da sessão {i+1}: {data_sessao_iso}")
                                            
                                            sessao = {
                                                "ficha_id": ficha_id,
                                                "guia_id": guia_id if guia_existe else None,
                                                "data_sessao": data_sessao_iso,
                                                "possui_assinatura": possui_assinatura,
                                                "procedimento_id": None,  # Placeholder
                                                "profissional_executante": registro.get("profissional_executante", ""),
                                                "status": "pendente",
                                                "numero_guia": dados_ficha.get("numero_guia"),
                                                "codigo_ficha": dados_ficha.get("codigo_ficha"),
                                                "ordem_execucao": registro.get("ordem_execucao", i + 1),
                                                "status_biometria": "nao_verificado",
                                                "created_by": "00000000-0000-0000-0000-000000000000",
                                                "updated_by": "00000000-0000-0000-0000-000000000000"
                                            }
                                            
                                            sessoes.append(sessao)
                                    else:
                                        # Abordagem antiga: criar sessões genéricas
                                        logger.info(f"Usando abordagem genérica para criar {total_sessoes} sessões")
                                        for i in range(total_sessoes):
                                            data_sessao = data_base + timedelta(days=i * 7)  # Uma sessão por semana
                                            
                                            sessao = {
                                                "ficha_id": ficha_id,
                                                "guia_id": guia_id if guia_existe else None,
                                                "data_sessao": data_sessao.date().isoformat(),
                                                "possui_assinatura": False,
                                                "procedimento_id": None,  # Placeholder
                                                "profissional_executante": "",
                                                "status": "pendente",
                                                "numero_guia": dados_ficha.get("numero_guia"),
                                                "codigo_ficha": dados_ficha.get("codigo_ficha"),
                                                "ordem_execucao": i + 1,
                                                "status_biometria": "nao_verificado",
                                                "created_by": "00000000-0000-0000-0000-000000000000",
                                                "updated_by": "00000000-0000-0000-0000-000000000000"
                                            }
                                            
                                            sessoes.append(sessao)
                                    
                                    # Log das sessões criadas
                                    logger.info(f"Sessões a serem inseridas: {json.dumps(sessoes, default=str)}")
                                    
                                    # Inserir sessões no banco
                                    try:
                                        # Verificar se temos dados válidos para inserir
                                        for sessao in sessoes:
                                            # Verificar campos obrigatórios
                                            if not sessao.get("ficha_id"):
                                                logger.error(f"Sessão sem ficha_id: {sessao}")
                                            if not sessao.get("data_sessao"):
                                                logger.error(f"Sessão sem data_sessao: {sessao}")
                                            if not sessao.get("ordem_execucao"):
                                                logger.error(f"Sessão sem ordem_execucao: {sessao}")
                                        
                                        logger.info(f"Tentando inserir {len(sessoes)} sessões no banco")
                                        result = supabase.table("sessoes").insert(sessoes).execute()
                                        logger.info(f"Sessões criadas automaticamente: {len(result.data)} sessões")
                                        logger.info(f"Resposta da inserção: {json.dumps(result.data, default=str)}")
                                    except Exception as e:
                                        logger.error(f"Erro específico ao inserir sessões: {str(e)}")
                                        logger.exception(e)
                                
                                except Exception as e:
                                    logger.error(f"Erro ao processar data ou criar sessões: {str(e)}")
                                    logger.exception(e)  # Log do stack trace completo
                    except Exception as e:
                        logger.error(f"Erro ao gerar sessões: {str(e)}")
                        # Não impedimos o prosseguimento se falhar a geração de sessões
                        
                    return {
                        "filename": file.filename,
                        "status": "success",
                        "message": "Arquivo processado e ficha criada com sucesso.",
                        "ficha_id": response_ficha.data[0].get('id'),
                        "url": storage_url
                    }
                else:
                    logger.error("Falha ao criar ficha")
                    return {
                        "filename": file.filename,
                        "status": "error",
                        "message": "Falha ao criar ficha no banco de dados."
                    }
            else:
                # Salvar na tabela de fichas_pendentes
                try:
                    pendente_data = {
                        "storage_id": storage_id,
                        "dados_extraidos": json.loads(json.dumps(dados_ficha, cls=CustomEncoder)),
                        "status": "pendente",
                        "arquivo_url": storage_url,
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
                            "url": storage_url
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

@router.get("/prompts-disponiveis")
async def listar_prompts_disponiveis():
    """
    Lista todos os prompts personalizados disponíveis no sistema.
    
    Returns:
        Lista de prompts disponíveis com caminho, título e descrição
    """
    try:
        prompts = []
        prompts_dir = "prompts"
        
        # Verificar se o diretório existe
        if not os.path.exists(prompts_dir):
            return {"success": True, "prompts": []}
        
        # Percorrer a estrutura de diretórios
        for root, dirs, files in os.walk(prompts_dir):
            for file in files:
                if file.endswith(".md") or file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    relative_path = file_path.replace("\\", "/")  # Normalizar caminho para formato Unix
                    
                    # Extrair título e descrição do arquivo
                    title = file.replace(".md", "").replace(".txt", "").replace("_", " ").title()
                    description = ""
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            first_line = f.readline().strip()
                            if first_line.startswith("# "):
                                title = first_line[2:].strip()
                            
                            # Tentar encontrar uma descrição nas primeiras linhas
                            for _ in range(5):  # Ler até 5 linhas
                                line = f.readline().strip()
                                if line and not line.startswith("#") and not line.startswith("{"):
                                    description = line
                                    break
                    except Exception as e:
                        logger.error(f"Erro ao ler arquivo de prompt {file_path}: {str(e)}")
                    
                    prompts.append({
                        "path": relative_path,
                        "title": title,
                        "description": description[:100] + "..." if len(description) > 100 else description
                    })
        
        return {"success": True, "prompts": prompts}
    except Exception as e:
        logger.error(f"Erro ao listar prompts: {str(e)}")
        return {"success": False, "message": f"Erro ao listar prompts: {str(e)}"} 