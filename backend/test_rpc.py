import sys
import os

# Adicionar o diretório pai ao sys.path para permitir importações relativas
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.repositories.database_supabase import get_supabase_client
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rpc():
    try:
        # Obter cliente Supabase
        client = get_supabase_client()
        logger.info("Cliente Supabase obtido com sucesso")
        
        # Parâmetros para a função RPC
        params = {
            "p_offset": 0,
            "p_limit": 10,
            "p_search": None,
            "p_status": None,  # Teste com status nulo
            "p_paciente_id": None,
            "p_plano_saude_id": None,
            "p_order_column": "numero_carteirinha",
            "p_order_direction": "asc"
        }
        
        logger.info(f"Chamando RPC com parâmetros: {params}")
        
        # Chamar a função RPC
        result = client.rpc("listar_carteirinhas_com_detalhes", params).execute()
        
        # Verificar o resultado
        logger.info(f"Resultado: {result.data}")
        
        # Testar com status específico
        params["p_status"] = "ativa"
        logger.info(f"Chamando RPC com status 'ativa': {params}")
        
        result = client.rpc("listar_carteirinhas_com_detalhes", params).execute()
        logger.info(f"Resultado com status 'ativa': {result.data}")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao testar RPC: {str(e)}")
        return False

if __name__ == "__main__":
    test_rpc() 