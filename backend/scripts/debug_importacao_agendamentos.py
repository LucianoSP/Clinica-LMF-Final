import sys
import os
import asyncio
import logging
import json
from datetime import datetime

# --- Configuração do Caminho ---
# Adiciona o diretório raiz do projeto ao sys.path
# Isso permite importar módulos do backend como se estivesse executando a partir da raiz
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
# --- Fim da Configuração do Caminho ---

# --- Imports do Projeto ---
# Tentar importar os módulos necessários do projeto
try:
    from backend.routes.agendamento import buscar_agendamentos_mysql, mapear_agendamento, testar_conexao_mysql
    from backend.repositories.database_supabase import get_supabase_client, SupabaseClient
    from backend.config.config import Settings # Para carregar configurações se necessário
    from backend.utils.date_utils import DateEncoder # Para imprimir JSONs com datas
except ImportError as e:
    print(f"Erro ao importar módulos do projeto: {e}")
    print("Certifique-se de que o script está sendo executado a partir do diretório raiz do projeto")
    print("Ou que a estrutura de diretórios está correta.")
    sys.exit(1)
# --- Fim dos Imports do Projeto ---

# --- Configuração do Logging ---
# Configuração básica de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("debug_importacao")

# --- FILTRAR LOGS DE BIBLIOTECAS EXTERNAS ---
# Definir nível INFO ou WARNING para bibliotecas muito verbosas
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("hpack").setLevel(logging.INFO)
# Manter DEBUG para o seu código (se necessário, pode ser ajustado)
logging.getLogger("backend").setLevel(logging.DEBUG)
# --- Fim da Configuração do Logging ---

# --- Configurações da Execução ---
DATABASE_MYSQL = "abalarissa_db" # Substitua pelo nome do banco de dados MySQL
TABELA_MYSQL = "ps_schedule"     # Nome da tabela de agendamentos no MySQL
LIMITE_REGISTROS = 5            # Quantos registros buscar para teste
USUARIO_ID_DEBUG = "00000000-0000-0000-0000-000000000000" # UUID do usuário 'sistema' para testes
# --- Fim das Configurações da Execução ---

async def main():
    """Função principal para executar o debug da importação."""
    logger.info("--- Iniciando Script de Debug da Importação de Agendamentos ---")

    # 1. Testar Conexão MySQL
    logger.info(f"Testando conexão com MySQL DB: {DATABASE_MYSQL}")
    sucesso_conexao, msg_conexao = await testar_conexao_mysql(DATABASE_MYSQL)
    if not sucesso_conexao:
        logger.error(f"Falha na conexão com MySQL: {msg_conexao}")
        return
    logger.info(f"Conexão com MySQL estabelecida: {msg_conexao}")

    # 2. Obter Cliente Supabase (necessário para `mapear_agendamento`)
    try:
        supabase_client = get_supabase_client()
        logger.info("Cliente Supabase obtido com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao obter cliente Supabase: {e}")
        return

    # 3. Buscar Agendamentos do MySQL (sem filtro de data, apenas limite)
    logger.info(f"Buscando os últimos {LIMITE_REGISTROS} agendamentos de {DATABASE_MYSQL}.{TABELA_MYSQL}")
    try:
        agendamentos_mysql = await buscar_agendamentos_mysql(
            database=DATABASE_MYSQL,
            tabela=TABELA_MYSQL,
            limite=LIMITE_REGISTROS,
            ultima_data_registro=None, # Ignorar filtro de data
            ultima_data_atualizacao=None, # Ignorar filtro de data
            periodo_semanas=None # Ignorar filtro de semanas
        )
    except Exception as e:
        logger.error(f"Erro ao buscar agendamentos do MySQL: {e}")
        return

    if not agendamentos_mysql:
        logger.warning("Nenhum agendamento encontrado no MySQL para depuração.")
        return

    logger.info(f"Encontrados {len(agendamentos_mysql)} agendamentos. Processando...")

    # 4. Processar e Mapear cada Agendamento
    for i, agendamento_mysql in enumerate(agendamentos_mysql):
        logger.info(f"--- Processando Agendamento #{i+1} (ID Origem: {agendamento_mysql.get('schedule_id')}) ---")

        # Imprimir dados brutos do MySQL
        logger.debug("Dados Brutos do MySQL:")
        # Usar json.dumps com DateEncoder para lidar com tipos datetime/date
        try:
            logger.debug(json.dumps(agendamento_mysql, indent=2, cls=DateEncoder, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Erro ao serializar dados brutos: {e}")
            logger.debug(agendamento_mysql) # Fallback para print normal

        # Chamar a função de mapeamento
        logger.debug("Chamando mapear_agendamento...")
        try:
            agendamento_mapeado = mapear_agendamento(
                agendamento_mysql,
                USUARIO_ID_DEBUG,
                supabase_client
            )
            logger.debug("Dados Mapeados (prontos para Supabase):")
            # Usar json.dumps com DateEncoder para lidar com tipos datetime/date
            logger.debug(json.dumps(agendamento_mapeado, indent=2, cls=DateEncoder, ensure_ascii=False))

            # Opcional: Tentar inserir/atualizar no Supabase para ver se ocorre erro
            # try:
            #     id_origem = agendamento_mapeado.get('id_origem')
            #     if id_origem:
            #         logger.debug(f"Tentando Upsert no Supabase com id_origem: {id_origem}")
            #         response = supabase_client.table('agendamentos').upsert(agendamento_mapeado, on_conflict='id_origem').execute()
            #         if response.data:
            #             logger.info(f"Upsert no Supabase bem-sucedido para id_origem: {id_origem}")
            #         else:
            #             logger.error(f"Erro no Upsert para id_origem: {id_origem}. Resposta: {response}")
            #     else:
            #          logger.warning("Agendamento mapeado sem id_origem, não é possível fazer upsert.")
            # except Exception as e_upsert:
            #     logger.error(f"Erro durante o Upsert no Supabase: {e_upsert}")

        except Exception as e_map:
            logger.error(f"Erro ao mapear agendamento: {e_map}")

        logger.info("-" * 40) # Separador

    logger.info("--- Script de Debug da Importação de Agendamentos Concluído ---")

if __name__ == "__main__":
    # Executar a função main assíncrona
    asyncio.run(main()) 