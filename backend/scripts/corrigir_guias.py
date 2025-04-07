import asyncio
import sys
import os
import logging
from datetime import datetime

# Adicionar o diretório pai ao path para importar os módulos do backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.database_supabase import get_supabase_client

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def corrigir_guias():
    """
    Corrige guias com valores nulos para data_solicitacao e dados_autorizacao.
    """
    try:
        # Obter cliente Supabase
        db = get_supabase_client()
        
        # Buscar guias com valores nulos
        logger.info("Buscando guias com valores nulos...")
        result = db.from_("guias").select("*").is_("deleted_at", "null").execute()
        
        guias_atualizadas = 0
        
        for guia in result.data:
            atualizar = False
            dados_atualizacao = {}
            
            # Verificar se data_solicitacao é nula
            if guia.get("data_solicitacao") is None:
                atualizar = True
                # Usar a data de criação como fallback
                dados_atualizacao["data_solicitacao"] = guia.get("created_at")
                logger.info(f"Guia {guia['id']} - Corrigindo data_solicitacao nula")
            
            # Verificar se dados_autorizacao é nulo
            if guia.get("dados_autorizacao") is None:
                atualizar = True
                dados_atualizacao["dados_autorizacao"] = {}
                logger.info(f"Guia {guia['id']} - Corrigindo dados_autorizacao nulo")
            
            # Atualizar a guia se necessário
            if atualizar:
                db.from_("guias").update(dados_atualizacao).eq("id", guia["id"]).execute()
                guias_atualizadas += 1
        
        logger.info(f"Processo concluído. {guias_atualizadas} guias foram atualizadas.")
        
    except Exception as e:
        logger.error(f"Erro ao corrigir guias: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(corrigir_guias()) 