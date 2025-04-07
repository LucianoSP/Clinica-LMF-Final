import sys
import os
import asyncio
from datetime import datetime, timedelta
import uuid
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import supabase

async def gerar_sessoes_para_todas_fichas():
    """
    Gera sessões para todas as fichas que não possuem sessões
    """
    logger.info("Iniciando geração de sessões para todas as fichas sem sessões")
    
    # Buscar fichas sem sessões
    query = """
    SELECT f.id, f.codigo_ficha, f.data_atendimento, f.total_sessoes, f.numero_guia, f.guia_id
    FROM fichas f
    LEFT JOIN (
        SELECT ficha_id, COUNT(*) as count
        FROM sessoes
        WHERE deleted_at IS NULL
        GROUP BY ficha_id
    ) s ON f.id = s.ficha_id
    WHERE s.count IS NULL OR s.count = 0
    """
    
    fichas = supabase.from_("fichas").select("id, codigo_ficha, data_atendimento, total_sessoes, numero_guia, guia_id").execute()
    
    logger.info(f"Encontradas {len(fichas.data)} fichas no total")
    
    count_fichas_sem_sessoes = 0
    count_fichas_com_sessoes = 0
    count_sessoes_criadas = 0
    
    for ficha in fichas.data:
        # Verificar se já existem sessões para esta ficha
        sessoes_existentes = supabase.from_("sessoes").select("id").eq("ficha_id", ficha["id"]).execute()
        
        if sessoes_existentes.data and len(sessoes_existentes.data) > 0:
            logger.info(f"Ficha {ficha['id']} já possui {len(sessoes_existentes.data)} sessões")
            count_fichas_com_sessoes += 1
            continue
        
        count_fichas_sem_sessoes += 1
        logger.info(f"Gerando sessões para ficha {ficha['id']} - {ficha['codigo_ficha']}")
        
        # Obter o total de sessões da ficha
        total_sessoes = ficha.get("total_sessoes", 1)
        if total_sessoes <= 0:
            total_sessoes = 1
            
        logger.info(f"Total de sessões a serem criadas: {total_sessoes}")
        
        # Data base para as sessões (data da ficha)
        data_atendimento = ficha.get("data_atendimento")
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
            for i in range(total_sessoes):
                data_sessao = data_base + timedelta(days=i * 7)  # Uma sessão por semana
                
                sessao = {
                    "ficha_id": ficha["id"],
                    "guia_id": ficha.get("guia_id"),
                    "data_sessao": data_sessao.date().isoformat(),
                    "possui_assinatura": False,
                    "procedimento_id": None,  # Placeholder
                    "profissional_executante": "",
                    "status": "pendente",
                    "numero_guia": ficha.get("numero_guia"),
                    "codigo_ficha": ficha.get("codigo_ficha"),
                    "ordem_execucao": i + 1,
                    "status_biometria": "nao_verificado",
                    "created_by": "00000000-0000-0000-0000-000000000000",
                    "updated_by": "00000000-0000-0000-0000-000000000000"
                }
                
                sessoes.append(sessao)
            
            # Inserir sessões no banco
            if sessoes:
                result = supabase.from_("sessoes").insert(sessoes).execute()
                logger.info(f"Sessões criadas para ficha {ficha['id']}: {len(result.data)}")
                count_sessoes_criadas += len(result.data)
            
        except Exception as e:
            logger.error(f"Erro ao processar ficha {ficha['id']}: {str(e)}")
    
    logger.info(f"Processamento concluído!")
    logger.info(f"Total de fichas processadas: {len(fichas.data)}")
    logger.info(f"Fichas que já tinham sessões: {count_fichas_com_sessoes}")
    logger.info(f"Fichas sem sessões processadas: {count_fichas_sem_sessoes}")
    logger.info(f"Total de sessões criadas: {count_sessoes_criadas}")

async def main():
    await gerar_sessoes_para_todas_fichas()

if __name__ == "__main__":
    asyncio.run(main()) 