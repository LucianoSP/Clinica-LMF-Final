import os
import base64
import json
import logging
import anthropic
from google import genai
from google.genai import types
from fastapi import HTTPException
from pydantic import ValidationError
import pandas as pd
import requests
from mistralai import Mistral
from ..models.execucao import DadosGuia
from ..utils.date_utils import formatar_data

logger = logging.getLogger(__name__)


# Função para carregar prompt de um arquivo
def carregar_prompt(prompt_path=None):
    """
    Carrega um prompt de um arquivo ou retorna o prompt padrão.
    
    Args:
        prompt_path: Caminho para o arquivo de prompt (opcional)
        
    Returns:
        String contendo o prompt
    """
    # Prompt padrão caso nenhum arquivo seja fornecido
    prompt_padrao = """
    Analise este documento PDF e extraia as seguintes informações em JSON válido:

    {
        "codigo_ficha": string,  // Campo 1 - FICHA no canto superior direito, formato XX-XXXXXXXX...
        "registros": [
            {
                "ordem_execucao": integer,       // Campo numérico da linha (1, 2, 3, etc.)
                "data_atendimento": string,         // Campo 11 - Data do atendimento no formato DD/MM/YYYY
                "paciente_carteirinha": string,  // Campo 12 - Número da carteira
                "paciente_nome": string,         // Campo 13 - Nome/Nome Social do Beneficiário
                "guia_id": string,              // Campo 14 - Número da Guia Principal
                "possui_assinatura": boolean     // Campo 15 - Indica se tem assinatura na linha
            }
        ]
    }

    Regras de extração:
    1. Cada linha numerada (1-, 2-, 3-, etc) representa uma sessão diferente do mesmo paciente
    2. O campo `ordem_execucao` DEVE ser o número inteiro correspondente à linha (1 para a primeira linha, 2 para a segunda, etc.).
    3. Inclua TODAS as linhas que têm data de atendimento preenchida, mesmo que não tenham assinatura
    4. IMPORTANTE: Todas as datas DEVEM estar no formato DD/MM/YYYY (com 4 dígitos no ano)
    5. Todas as datas devem ser válidas (30/02/2024 seria uma data inválida)
    6. Mantenha o número da carteirinha EXATAMENTE como está no documento, incluindo pontos e hífens
    7. Retorne APENAS o JSON, sem texto adicional
    """
    
    if not prompt_path:
        return prompt_padrao
    
    try:
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            logger.warning(f"Arquivo de prompt não encontrado: {prompt_path}. Usando prompt padrão.")
            return prompt_padrao
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo de prompt: {str(e)}. Usando prompt padrão.")
        return prompt_padrao


# Função para extrair informações de um PDF
async def extract_info_from_pdf(pdf_path: str, api_key: str, modelo: str = "claude", prompt_path: str = None):
    """
    Extrai informações de um arquivo PDF usando o modelo de IA especificado.
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        api_key: Chave da API do modelo selecionado
        modelo: Modelo de IA a ser usado ("claude", "gemini", "mistral")
        prompt_path: Caminho para o arquivo de prompt personalizado (opcional)
        
    Returns:
        Dicionário com as informações extraídas e status da validação
    """
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    pdf_data = None
    try:
        with open(pdf_path, "rb") as pdf_file:
            pdf_data = base64.b64encode(pdf_file.read()).decode("utf-8")
            pdf_binary = open(pdf_path, "rb").read()  # Para APIs que precisam do arquivo binário
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler PDF: {str(e)}")

    if not pdf_data:
        raise HTTPException(status_code=500, detail="Erro ao ler PDF: arquivo vazio")
    
    # Carregar o prompt personalizado ou usar o padrão
    prompt = carregar_prompt(prompt_path)
    
    # Usar o modelo especificado
    try:
        if modelo == "claude":
            return await extract_with_claude(pdf_data, api_key, prompt)
        elif modelo == "gemini":
            return await extract_with_gemini(pdf_binary, api_key, prompt)
        elif modelo == "mistral":
            return await extract_with_mistral(pdf_path, api_key, prompt)
        else:
            raise ValueError(f"Modelo não suportado: {modelo}")
    except Exception as e:
        logger.error(f"Erro ao extrair informações com o modelo {modelo}: {str(e)}")
        return {
            "erro": f"Erro ao extrair informações com o modelo {modelo}: {str(e)}",
            "status_validacao": "falha",
        }


async def extract_with_claude(pdf_data: str, api_key: str, prompt: str):
    """Extrai informações de PDF usando a API Claude da Anthropic"""
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            betas=["pdfs-2024-09-25"],
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )

        # Parse a resposta JSON
        dados_extraidos = json.loads(response.content[0].text)
        
        return processar_dados_extraidos(dados_extraidos, response)

    except Exception as e:
        logger.error(f"Erro ao processar com Claude: {str(e)}")
        return {
            "erro": f"Erro ao processar com Claude: {str(e)}",
            "status_validacao": "falha",
            "resposta_raw": (
                response.content[0].text if "response" in locals() else None
            ),
        }


async def extract_with_gemini(pdf_binary: bytes, api_key: str, prompt: str):
    """Extrai informações de PDF usando a API Gemini do Google"""
    try:
        # Criar o cliente com a API key
        client = genai.Client(api_key=api_key)
        
        # Preparar o conteúdo com o prompt e o PDF usando a abordagem correta para documentos
        contents = [
            types.Part.from_bytes(
                data=pdf_binary,
                mime_type='application/pdf',
            ),
            prompt
        ]
        
        # Fazer a chamada à API
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents
        )
        
        # Extrair o JSON da resposta
        response_text = response.text
        
        # Remover backticks se existirem (Gemini às vezes envolve JSON em ```)
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
            
        dados_extraidos = json.loads(response_text)
        
        # Processar os dados extraídos
        return processar_dados_extraidos(dados_extraidos, response)
        
    except Exception as e:
        logger.error(f"Erro ao processar com Gemini: {str(e)}")
        return {
            "erro": f"Erro ao processar com Gemini: {str(e)}",
            "status_validacao": "falha",
            "resposta_raw": response.text if "response" in locals() else None
        }


async def extract_with_mistral(pdf_path: str, api_key: str, prompt: str):
    """Extrai informações de PDF usando a API OCR do Mistral"""
    try:
        # Inicializar o cliente Mistral
        client = Mistral(api_key=api_key)
        
        # Fazer upload do arquivo PDF para o Mistral
        with open(pdf_path, "rb") as pdf_file:
            uploaded_file = client.files.upload(
                file={
                    "file_name": os.path.basename(pdf_path),
                    "content": pdf_file,
                },
                purpose="ocr"
            )
        
        # Obter URL assinada para o arquivo
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
        
        # Processar o documento com OCR
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url
            }
        )
        
        # Extrair o texto do documento processado
        document_text = "\n\n".join([f"### Página {i+1}\n{ocr_response.pages[i].markdown}" for i in range(len(ocr_response.pages))])
        
        # System prompt opcional para melhorar os resultados
        system_prompt = """
        Você é um assistente especializado em extrair informações estruturadas de documentos PDF.
        Sua tarefa é analisar documentos de fichas médicas e extrair dados específicos no formato JSON.
        Siga rigorosamente as regras de extração fornecidas e retorne apenas o JSON solicitado.
        """
        
        # Enviar o texto extraído para o modelo de chat com o prompt do usuário
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nConteúdo do documento:\n\n{document_text}"
            }
        ]
        
        # Obter a resposta do chat
        chat_response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=0.0,
            max_tokens=8000
        )
        
        # Extrair o conteúdo da resposta
        response_text = chat_response.choices[0].message.content
        
        # Remover backticks se existirem
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
            
        dados_extraidos = json.loads(response_text)
        
        # Processar os dados extraídos
        return processar_dados_extraidos(dados_extraidos, chat_response)
        
    except Exception as e:
        logger.error(f"Erro ao processar com Mistral: {str(e)}")
        return {
            "erro": f"Erro ao processar com Mistral: {str(e)}",
            "status_validacao": "falha",
            "resposta_raw": str(e)
        }


def processar_dados_extraidos(dados_extraidos, response_raw):
    """Processa os dados extraídos de qualquer modelo de IA e os formata consistentemente"""
    try:
        # Verificar se é necessário fazer a conversão do nome do campo
        # Se existir "data_execucao" mas não "data_atendimento", renomear o campo
        for registro in dados_extraidos["registros"]:
            if "data_execucao" in registro and "data_atendimento" not in registro:
                registro["data_atendimento"] = registro.pop("data_execucao")
            
            # Garantir que a data esteja no formato correto
            if "data_atendimento" in registro:
                registro["data_atendimento"] = formatar_data(registro["data_atendimento"])

        # Validar usando Pydantic
        dados_validados = DadosGuia(**dados_extraidos)

        # Criar DataFrame dos registros
        df = pd.DataFrame([registro.dict() for registro in dados_validados.registros])

        # Preparar dados para a tabela fichas
        dados_ficha = {
            "codigo_ficha": dados_validados.codigo_ficha,
            "numero_guia": dados_validados.registros[0].guia_id,
            "paciente_nome": dados_validados.registros[0].paciente_nome,
            "paciente_carteirinha": dados_validados.registros[0].paciente_carteirinha,
            "arquivo_digitalizado": None,  # Será atualizado após upload no R2
            "status": "pendente",
            "data_atendimento": dados_validados.registros[0].data_atendimento,
            "total_sessoes": len(dados_validados.registros),
        }

        return {
            "json": dados_validados.dict(),
            "dataframe": df,
            "dados_ficha": dados_ficha,
            "status_validacao": "sucesso",
        }
    except json.JSONDecodeError as e:
        return {
            "erro": f"Erro ao processar JSON: {str(e)}",
            "status_validacao": "falha",
            "resposta_raw": response_raw,
        }
    except ValidationError as e:
        return {
            "erro": str(e),
            "status_validacao": "falha",
            "resposta_raw": response_raw,
        }
    except Exception as e:
        return {
            "erro": str(e),
            "status_validacao": "falha",
            "resposta_raw": response_raw,
        }
