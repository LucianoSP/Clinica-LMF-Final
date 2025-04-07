import logging
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from supabase import AsyncClient # Correção: Importar AsyncClient da biblioteca principal
from ..repositories.database_supabase import get_supabase_client
from ..schemas.responses import StandardResponse
import json
from backend.utils.date_utils import DateEncoder # Para serializar JSON com datas/UUIDs

logger = logging.getLogger("backend")
router = APIRouter()

class VinculacaoManualRequest(BaseModel):
    execucao_id: str
    sessao_id: str

@router.post(
    "/manual",
    summary="Vincula manualmente uma execução a uma sessão",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    tags=["Vinculações"]
)
async def vincular_manual(
    vinculacao_data: VinculacaoManualRequest,
    supabase: AsyncClient = Depends(get_supabase_client) # Tipo correto
):
    """
    Realiza a vinculação manual de uma execução (geralmente originada do scraping)
    a uma sessão específica (geralmente originada da ficha de presença).

    Atualiza a execução com o ID da sessão, o código da ficha correspondente,
    e marca a vinculação como definitiva.
    """
    logger.info(f"Tentando vinculação manual: Execução ID {vinculacao_data.execucao_id} <-> Sessão ID {vinculacao_data.sessao_id}")
    try:
        # 1. Buscar o codigo_ficha da sessão
        sessao_response = await supabase.table("sessoes")\
            .select("codigo_ficha")\
            .eq("id", vinculacao_data.sessao_id)\
            .maybe_single()\
            .execute()

        if not sessao_response.data:
            logger.error(f"Sessão {vinculacao_data.sessao_id} não encontrada.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada")

        codigo_ficha_sessao = sessao_response.data.get("codigo_ficha")
        if not codigo_ficha_sessao:
             # Se codigo_ficha for nulo na sessão, pode gerar um ou usar um placeholder? Por ora, erro.
             logger.error(f"Sessão {vinculacao_data.sessao_id} não possui codigo_ficha.")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sessão não possui código de ficha")


        # 2. Atualizar a execução
        update_data = {
            "sessao_id": vinculacao_data.sessao_id,
            "codigo_ficha": codigo_ficha_sessao,
            "codigo_ficha_temp": False,
            "link_manual_necessario": False
        }
        execucao_response = await supabase.table("execucoes")\
            .update(update_data)\
            .eq("id", vinculacao_data.execucao_id)\
            .execute()

        # Verificar se a execução foi encontrada e atualizada
        if not execucao_response.data:
             logger.error(f"Execução {vinculacao_data.execucao_id} não encontrada para atualização.")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execução não encontrada")

        logger.info(f"Vinculação manual realizada com sucesso para Execução ID {vinculacao_data.execucao_id}")
        return StandardResponse(success=True, message="Vinculação manual realizada com sucesso.")

    except HTTPException as e:
        # Re-lança HTTPExceptions para que o handler global as capture
        raise e
    except Exception as e:
        logger.exception(f"Erro inesperado na vinculação manual: {e}") # Usar logger.exception para incluir traceback
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao processar a vinculação manual: {e}")


@router.post(
    "/batch",
    summary="Dispara as rotinas de vinculação automática em lote",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    tags=["Vinculações"]
)
async def vincular_batch(
    supabase: AsyncClient = Depends(get_supabase_client) # Tipo correto
):
    """
    Executa as funções SQL 'vincular_sessoes_execucoes' e 'vincular_sessoes_mesmo_dia'
    para tentar vincular automaticamente as execuções pendentes às sessões correspondentes
    com base nas regras de confiança definidas.
    """
    logger.info("Iniciando processo de vinculação em lote via RPC...")
    try:
        # Chamar a primeira função de vinculação batch
        logger.info("Executando RPC: vincular_sessoes_execucoes")
        rpc_response_1 = await supabase.rpc('vincular_sessoes_execucoes').execute()
        # Verificar se houve erro na chamada RPC (a função em si pode não retornar dados, mas a chamada pode falhar)
        # A biblioteca supabase-py v1 pode não levantar exceção em erro de RPC, verificar a resposta.
        # Em supabase-py v2, erros são levantados como PostgrestAPIError ou APIError.
        # Adapte a verificação de erro conforme a versão da sua biblioteca.
        # Exemplo genérico (pode precisar de ajuste):
        if hasattr(rpc_response_1, 'error') and rpc_response_1.error:
             logger.error(f"Erro ao executar RPC vincular_sessoes_execucoes: {rpc_response_1.error}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao executar vinculação em lote (passo 1): {rpc_response_1.error}")
        logger.info("RPC vincular_sessoes_execucoes concluída.")


        # Chamar a segunda função de vinculação batch para casos múltiplos
        logger.info("Executando RPC: vincular_sessoes_mesmo_dia")
        rpc_response_2 = await supabase.rpc('vincular_sessoes_mesmo_dia').execute()
        if hasattr(rpc_response_2, 'error') and rpc_response_2.error:
             logger.error(f"Erro ao executar RPC vincular_sessoes_mesmo_dia: {rpc_response_2.error}")
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao executar vinculação em lote (passo 2): {rpc_response_2.error}")
        logger.info("RPC vincular_sessoes_mesmo_dia concluída.")

        logger.info("Processo de vinculação em lote disparado com sucesso.")
        return StandardResponse(success=True, message="Processo de vinculação em lote disparado com sucesso.")

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Erro inesperado ao disparar vinculação em lote: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno ao disparar a vinculação em lote: {e}")

@router.post("/agendamentos/batch")
async def vincular_agendamentos_batch():
    """Endpoint para executar a função batch `vincular_agendamentos` no banco de dados."""
    supabase = get_supabase_client()
    try:
        # Chama a função SQL `vincular_agendamentos`
        response = await supabase.rpc("vincular_agendamentos").execute()

        # A função retorna um JSONB com as contagens
        if response.data:
             # Serializa o resultado usando o DateEncoder para garantir compatibilidade
            result_data = json.loads(json.dumps(response.data, cls=DateEncoder))
            logger.info(f"Resultado da vinculação de agendamentos: {result_data}")
            return {
                "message": "Processo de vinculação batch (agendamentos) executado com sucesso.",
                "details": result_data
            }
        else:
             # Log e retorno em caso de não haver dados (pode indicar erro na função SQL não capturado)
            logger.warning("Função vincular_agendamentos executada, mas não retornou dados.")
            return {"message": "Processo de vinculação batch (agendamentos) executado, mas sem detalhes de retorno."}

    except Exception as e:
        # Log detalhado do erro
        logger.error(f"Erro ao executar vinculação batch (agendamentos): {e}", exc_info=True)
        error_details = str(e)
        # Tenta extrair detalhes específicos de erros do Supabase/PostgREST
        if hasattr(e, 'details'):
            error_details = getattr(e, 'details')
        elif hasattr(e, 'message'):
             error_details = getattr(e, 'message')
             
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor ao vincular agendamentos: {error_details}") 