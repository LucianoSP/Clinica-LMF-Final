import sys
import os
import asyncio
from datetime import datetime, timedelta
import uuid

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import supabase
from repositories.database_supabase import get_supabase_client

async def gerar_sessoes_para_ficha(ficha_id: str, total_sessoes: int = 10):
    """
    Gera sessões para uma ficha existente
    """
    print(f"Gerando {total_sessoes} sessões para a ficha {ficha_id}")
    
    # Buscar a ficha para obter informações
    ficha = await supabase.from_("fichas").select("*").eq("id", ficha_id).execute()
    
    if not ficha.data:
        print(f"Ficha {ficha_id} não encontrada")
        return
    
    ficha_data = ficha.data[0]
    print(f"Ficha encontrada: {ficha_data['codigo_ficha']}")
    
    # Verificar se já existem sessões para esta ficha
    sessoes_existentes = await supabase.from_("sessoes").select("*").eq("ficha_id", ficha_id).execute()
    
    if sessoes_existentes.data:
        print(f"Já existem {len(sessoes_existentes.data)} sessões para esta ficha")
        return
    
    # Data base para as sessões (data da ficha)
    data_base = datetime.fromisoformat(ficha_data["data_atendimento"].replace("Z", "+00:00"))
    
    # Gerar sessões
    sessoes = []
    for i in range(total_sessoes):
        data_sessao = data_base + timedelta(days=i * 7)  # Uma sessão por semana
        
        sessao = {
            "ficha_id": ficha_id,
            "guia_id": ficha_data["guia_id"],
            "data_sessao": data_sessao.date().isoformat(),
            "possui_assinatura": False,
            "procedimento_id": str(uuid.uuid4()),  # Placeholder
            "profissional_executante": "Dr. Exemplo",
            "status": "pendente",
            "numero_guia": ficha_data["numero_guia"],
            "codigo_ficha": ficha_data["codigo_ficha"],
            "ordem_execucao": i + 1,
            "status_biometria": "nao_verificado",
            "created_by": "00000000-0000-0000-0000-000000000000",
            "updated_by": "00000000-0000-0000-0000-000000000000"
        }
        
        sessoes.append(sessao)
    
    # Inserir sessões no banco
    result = await supabase.from_("sessoes").insert(sessoes).execute()
    
    if result.data:
        print(f"Foram criadas {len(result.data)} sessões com sucesso")
    else:
        print("Erro ao criar sessões")
        print(result.error)

async def main():
    # Ficha de exemplo (substitua pelo ID real)
    ficha_id = "d522de8d-0fcb-4233-b46c-ddeb5a728b35"
    
    # Número de sessões a serem geradas
    total_sessoes = 7
    
    await gerar_sessoes_para_ficha(ficha_id, total_sessoes)

if __name__ == "__main__":
    asyncio.run(main()) 