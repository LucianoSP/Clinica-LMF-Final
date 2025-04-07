from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import Optional, List, Dict, Any
from ..schemas.responses import StandardResponse
from ..services.importacao_service import ImportacaoService
from datetime import datetime, timedelta, timezone
import logging
from backend.repositories.database_supabase import get_supabase_client, SupabaseClient

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ultima-importacao", response_model=StandardResponse[Dict[str, Any]])
async def obter_ultima_importacao():
    """Obtém os dados da última importação registrada."""
    importacao_service = ImportacaoService()
    result = await importacao_service.obter_ultima_importacao()
    return StandardResponse(
        success=True,
        data=result,
        message="Última importação obtida com sucesso"
    )

@router.get("/limpar-datas-controle", response_model=StandardResponse[Dict[str, Any]])
async def limpar_datas_controle():
    """
    Limpa datas inválidas (futuras) nas tabelas de controle de importação.
    Útil quando há datas incorretas que impedem novas importações.
    """
    try:
        importacao_service = ImportacaoService()
        repository = importacao_service.repository
        
        # Obter última importação
        ultima_importacao = await repository.obter_ultima_importacao()
        
        # Verificar se há datas futuras
        agora = datetime.now(timezone.utc)  # Tornar a data atual offset-aware com UTC
        correcao_necessaria = False
        
        if ultima_importacao:
            logger.info(f"Última importação encontrada: {ultima_importacao}")
            
            ultima_data_registro = ultima_importacao.get('ultima_data_registro_importada')
            ultima_data_atualizacao = ultima_importacao.get('ultima_data_atualizacao_importada')
            
            # Verificar se são strings e converter para datetime
            if isinstance(ultima_data_registro, str):
                try:
                    # Garantir que a data tenha informação de timezone
                    if 'Z' in ultima_data_registro:
                        ultima_data_registro = datetime.fromisoformat(ultima_data_registro.replace('Z', '+00:00'))
                    elif '+' not in ultima_data_registro and '-' not in ultima_data_registro[-6:]:
                        # Se não tem informação de timezone, assumir UTC
                        ultima_data_registro = datetime.fromisoformat(ultima_data_registro).replace(tzinfo=timezone.utc)
                    else:
                        # Já tem timezone
                        ultima_data_registro = datetime.fromisoformat(ultima_data_registro.replace('Z', '+00:00'))
                except Exception as e:
                    logger.error(f"Erro ao converter data de registro: {str(e)}")
                    ultima_data_registro = None
                    
            if isinstance(ultima_data_atualizacao, str):
                try:
                    # Garantir que a data tenha informação de timezone
                    if 'Z' in ultima_data_atualizacao:
                        ultima_data_atualizacao = datetime.fromisoformat(ultima_data_atualizacao.replace('Z', '+00:00'))
                    elif '+' not in ultima_data_atualizacao and '-' not in ultima_data_atualizacao[-6:]:
                        # Se não tem informação de timezone, assumir UTC
                        ultima_data_atualizacao = datetime.fromisoformat(ultima_data_atualizacao).replace(tzinfo=timezone.utc)
                    else:
                        # Já tem timezone
                        ultima_data_atualizacao = datetime.fromisoformat(ultima_data_atualizacao.replace('Z', '+00:00'))
                except Exception as e:
                    logger.error(f"Erro ao converter data de atualização: {str(e)}")
                    ultima_data_atualizacao = None
            
            # Garantir que as datas são offset-aware para comparação
            if ultima_data_registro and not ultima_data_registro.tzinfo:
                ultima_data_registro = ultima_data_registro.replace(tzinfo=timezone.utc)
                
            if ultima_data_atualizacao and not ultima_data_atualizacao.tzinfo:
                ultima_data_atualizacao = ultima_data_atualizacao.replace(tzinfo=timezone.utc)
            
            # Verificar se são datas futuras
            data_futura_registro = ultima_data_registro and ultima_data_registro > agora
            data_futura_atualizacao = ultima_data_atualizacao and ultima_data_atualizacao > agora
            
            if data_futura_registro or data_futura_atualizacao:
                correcao_necessaria = True
                logger.warning(f"Datas futuras detectadas - Registro: {ultima_data_registro}, Atualização: {ultima_data_atualizacao}")
                
                # Criar uma data anterior (dois anos atrás) com timezone UTC
                data_anterior = (agora - timedelta(days=365*2)).isoformat()
                
                # Registrar nova entrada com datas corrigidas
                nova_importacao = {
                    "ultima_data_registro_importada": data_anterior,
                    "ultima_data_atualizacao_importada": data_anterior,
                    "quantidade_registros_importados": 0,
                    "quantidade_registros_atualizados": 0,
                    "usuario_id": ultima_importacao.get('usuario_id', '00000000-0000-0000-0000-000000000000'),
                    "observacoes": "Correção automática de datas futuras"
                }
                
                # Registrar nova entrada
                await repository.registrar_importacao(nova_importacao)
                return StandardResponse(
                    success=True,
                    data={
                        "corrigido": True,
                        "data_anterior": data_anterior,
                        "data_futura_registro": str(ultima_data_registro) if data_futura_registro else None,
                        "data_futura_atualizacao": str(ultima_data_atualizacao) if data_futura_atualizacao else None
                    },
                    message="Datas futuras corrigidas com sucesso"
                )
            
            # Mesmo que não seja futura, verificar se as datas são recentes demais
            uma_hora_atras = agora - timedelta(hours=1)
            data_muito_recente_registro = ultima_data_registro and uma_hora_atras < ultima_data_registro <= agora
            data_muito_recente_atualizacao = ultima_data_atualizacao and uma_hora_atras < ultima_data_atualizacao <= agora
            
            if data_muito_recente_registro or data_muito_recente_atualizacao:
                correcao_necessaria = True
                logger.warning(f"Datas muito recentes detectadas - Registro: {ultima_data_registro}, Atualização: {ultima_data_atualizacao}")
                
                # Criar uma data anterior (um dia atrás)
                data_anterior = (agora - timedelta(days=1)).isoformat()
                
                # Registrar nova entrada com datas corrigidas
                nova_importacao = {
                    "ultima_data_registro_importada": data_anterior,
                    "ultima_data_atualizacao_importada": data_anterior,
                    "quantidade_registros_importados": 0,
                    "quantidade_registros_atualizados": 0,
                    "usuario_id": ultima_importacao.get('usuario_id', '00000000-0000-0000-0000-000000000000'),
                    "observacoes": "Correção automática de datas muito recentes"
                }
                
                # Registrar nova entrada
                await repository.registrar_importacao(nova_importacao)
                return StandardResponse(
                    success=True,
                    data={
                        "corrigido": True,
                        "data_anterior": data_anterior,
                        "data_muito_recente_registro": str(ultima_data_registro) if data_muito_recente_registro else None,
                        "data_muito_recente_atualizacao": str(ultima_data_atualizacao) if data_muito_recente_atualizacao else None
                    },
                    message="Datas muito recentes corrigidas com sucesso"
                )
        
        if not correcao_necessaria:
            return StandardResponse(
                success=True,
                data={"corrigido": False, "ultima_importacao": ultima_importacao},
                message="Não foram encontradas datas futuras para corrigir"
            )
            
    except Exception as e:
        logger.error(f"Erro ao limpar datas de controle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar datas de controle: {str(e)}")

# Resto dos endpoints existentes... 