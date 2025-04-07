"""
Utilitários para manipulação de agendamentos.
Este módulo contém funções auxiliares para facilitar o trabalho com agendamentos.
"""
import logging
from typing import Dict, Any, List, Optional

# Configurar logger
logger = logging.getLogger(__name__)

def limpar_campos_invalidos(agendamento_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove campos que não existem na tabela agendamentos do Supabase.
    
    Args:
        agendamento_dict: Dicionário com dados do agendamento
        
    Returns:
        Dict[str, Any]: Dicionário limpo sem campos inválidos
    """
    # Lista de campos que não existem na tabela agendamentos
    campos_invalidos = [
        'carteirinha',
        'paciente_nome',
        'cod_paciente',
        'pagamento',
        'sala',
        'id_profissional',
        'profissional',
        'tipo_atend',
        'qtd_sess',
        'elegibilidade',
        'substituicao',
        'tipo_falta',
        'id_pai',
        'id_atendimento',
    ]
    
    # Remover campos inválidos
    for campo in campos_invalidos:
        if campo in agendamento_dict:
            agendamento_dict.pop(campo, None)
    
    return agendamento_dict


def adicionar_dados_relacionados(
    agendamentos,
    pacientes_map,
    procedimentos_map,
    salas_map,
    locais_map,
    profissionais_map,
    profissoes_map,
    especialidades_map,
    user_profissao_map,
    profissionais_userid_map
):
    """Adiciona dados relacionados aos agendamentos."""
    logger.debug(f"Entrando em adicionar_dados_relacionados com {len(agendamentos)} agendamentos.") # Log inicial
    for idx, agendamento in enumerate(agendamentos):
        logger.debug(f"Processando agendamento #{idx} (ID: {agendamento.get('id')})") # Log por agendamento
        # Adicionar dados do paciente
        if agendamento.get("paciente_id") and agendamento["paciente_id"] in pacientes_map:
            paciente_data = pacientes_map[agendamento["paciente_id"]]
            agendamento["paciente_nome"] = paciente_data.get("nome")
            agendamento["carteirinha"] = paciente_data.get("carteirinha")
            agendamento["plano_saude"] = paciente_data.get("plano_saude")

        # Adicionar dados do procedimento
        if agendamento.get("procedimento_id") and agendamento["procedimento_id"] in procedimentos_map:
            procedimento_data = procedimentos_map[agendamento["procedimento_id"]]
            agendamento["procedimento_nome"] = procedimento_data.get("nome")

        # Adicionar dados da sala
        if agendamento.get("sala_id_supabase") and agendamento["sala_id_supabase"] in salas_map:
            agendamento["sala_nome"] = salas_map[agendamento["sala_id_supabase"]]
            agendamento["sala"] = salas_map[agendamento["sala_id_supabase"]]

        # Adicionar dados do local/unidade
        if agendamento.get("local_id_supabase") and agendamento["local_id_supabase"] in locais_map:
            agendamento["local_nome"] = locais_map[agendamento["local_id_supabase"]]
            agendamento["unidade"] = locais_map[agendamento["local_id_supabase"]]

        # Adicionar dados do profissional e profissão
        if agendamento.get("schedule_profissional_id"):
            prof_id_str = str(agendamento["schedule_profissional_id"])
            logger.debug(f"  Agendamento ID {agendamento.get('id')}: Profissional UUID = {prof_id_str}") # Log UUID profissional
            
            # Usar mapa UUID -> user_id para obter o ID inteiro
            profissional_user_id = profissionais_userid_map.get(prof_id_str)
            agendamento["profissional_id"] = profissional_user_id 
            logger.debug(f"    -> Mapeado para User ID: {profissional_user_id}") # Log User ID

            # Usar mapa UUID -> nome para nome do profissional
            if prof_id_str in profissionais_map:
                profissional_nome = profissionais_map[prof_id_str]
                agendamento["profissional_nome"] = profissional_nome
                agendamento["profissional"] = profissional_nome
                logger.debug(f"    -> Nome Profissional: {profissional_nome}") # Log Nome Profissional
            else:
                 logger.debug(f"    -> Nome Profissional: Não encontrado no mapa.")
            
            # Buscar nome da profissão usando os mapas
            if prof_id_str in user_profissao_map:
                profissao_id = user_profissao_map[prof_id_str]
                logger.debug(f"    -> ID Profissao (via user_profissao_map): {profissao_id}") # Log ID Profissão
                if profissao_id in profissoes_map:
                    profissao_nome = profissoes_map[profissao_id]
                    agendamento["profissao"] = profissao_nome
                    logger.debug(f"      -> Nome Profissao: {profissao_nome}") # Log Nome Profissão
                else:
                    logger.debug(f"      -> Nome Profissao: ID {profissao_id} não encontrado no profissoes_map.")
            else:
                 logger.debug(f"    -> ID Profissao: Profissional UUID {prof_id_str} não encontrado no user_profissao_map.")
        else:
             logger.debug(f"  Agendamento ID {agendamento.get('id')}: Sem schedule_profissional_id.")

        # Adicionar dados da especialidade
        if agendamento.get("especialidade_id_supabase") and agendamento["especialidade_id_supabase"] in especialidades_map:
            agendamento["especialidade_nome"] = especialidades_map[agendamento["especialidade_id_supabase"]]
            agendamento["especialidade"] = especialidades_map[agendamento["especialidade_id_supabase"]]

        # Garantir que elegibilidade seja um booleano e mapear do campo original se existir
        if "schedule_elegibilidade" in agendamento:
            agendamento["elegibilidade"] = bool(agendamento["schedule_elegibilidade"])
        elif "elegibilidade" in agendamento: # Fallback se o campo já existir com nome antigo
             agendamento["elegibilidade"] = bool(agendamento["elegibilidade"])
        # else: # Se nenhum campo existir, pode ser necessário definir um valor padrão ou logar
            # logger.warning(f"Campo elegibilidade não encontrado para agendamento ID: {agendamento.get('id')}")
            # agendamento["elegibilidade"] = None # Ou False, dependendo da regra de negócio

    return agendamentos 