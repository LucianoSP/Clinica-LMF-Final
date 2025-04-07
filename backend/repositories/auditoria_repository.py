from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging
import traceback
from backend.config.config import supabase
from math import ceil
import uuid
from backend.utils.date_utils import formatar_data

# Configuração de logging
logging.basicConfig(level=logging.INFO)

"""
PADRONIZAÇÃO DE CAMPOS NA API DE DIVERGÊNCIAS:

- O campo 'tipo' é o padrão usado para o tipo de divergência
- Historicamente, algumas partes do sistema podem usar 'tipo_divergencia'
- As funções de mapeamento garantem compatibilidade entre 'tipo' e 'tipo_divergencia'
- O retorno da API usa 'items' como chave para a lista de divergências
"""

def registrar_execucao_auditoria(
    data_inicial: str = None,
    data_final: str = None,
    total_protocolos: int = 0,
    total_divergencias: int = 0,
    divergencias_por_tipo: dict = None,
    total_fichas: int = 0,
    total_execucoes: int = 0,
    total_resolvidas: int = 0,
) -> bool:
    """
    Registra uma nova execução de auditoria com seus metadados.
    
    Parâmetros:
    - data_inicial: Data início do período auditado
    - data_final: Data fim do período auditado
    - total_protocolos: Total de protocolos verificados
    - total_divergencias: Total de divergências encontradas
    - divergencias_por_tipo: Distribuição por tipo
    - total_fichas: Total de fichas verificadas
    - total_execucoes: Total de execuções verificadas
    - total_resolvidas: Total de divergências resolvidas
    
    Returns:
        bool: True se o registro foi bem-sucedido, False caso contrário
    """
    try:
        logging.info("Registrando execução de auditoria")
        logging.info(f"Dados recebidos: {locals()}")
        
        # Gerar UUID para o novo registro
        new_id = str(uuid.uuid4())
        
        # Tratar strings vazias de data
        data_inicial = None if not data_inicial else data_inicial
        data_final = None if not data_final else data_final
        
        # Garantir que todos os tipos de divergência existam no dicionário
        tipos_base = {
            "ficha_sem_execucao": 0,
            "execucao_sem_ficha": 0,
            "data_divergente": 0,
            "sessao_sem_assinatura": 0,
            "guia_vencida": 0,
            "quantidade_excedida": 0,
            "falta_data_execucao": 0,
            "duplicidade": 0
        }
        
        # Mesclar com os valores recebidos
        if divergencias_por_tipo:
            tipos_base.update(divergencias_por_tipo)

        # Preparar dados para inserção
        data = {
            "id": new_id,
            "data_execucao": datetime.now(timezone.utc).isoformat(),
            "data_inicial": data_inicial,
            "data_final": data_final,
            "total_protocolos": total_protocolos,
            "total_divergencias": total_divergencias,
            "total_fichas": total_fichas,
            "total_execucoes": total_execucoes,
            "total_resolvidas": total_resolvidas,
            "divergencias_por_tipo": tipos_base,
            "status": "finalizado"
        }

        logging.info(f"Tentando inserir dados: {data}")
        
        # Remover campos vazios antes da inserção
        insert_data = {k: v for k, v in data.items() if v != ""}
        
        # Inserir novo registro de auditoria
        response = supabase.table("auditoria_execucoes").insert(insert_data).execute()
        
        if response.data:
            logging.info("Execução de auditoria registrada com sucesso")
            return True
        else:
            logging.error("Erro ao registrar execução de auditoria: response.data está vazio")
            return False

    except Exception as e:
        logging.error(f"Erro ao registrar execução de auditoria: {str(e)}")
        traceback.print_exc()
        return False

def calcular_estatisticas_divergencias() -> Dict:
    """
    Calcula estatísticas das divergências para os cards.
    
    Returns:
        Dict: Dicionário com estatísticas das divergências
    """
    try:
        # Busca todas as divergências
        response = supabase.table("divergencias").select("*").execute()
        divergencias = response.data if response.data else []

        # Inicializa contadores
        por_tipo = {}
        por_prioridade = {"ALTA": 0, "MEDIA": 0}
        por_status = {"pendente": 0, "em_analise": 0, "resolvida": 0, "cancelada": 0}

        # Conta divergências por tipo, prioridade e status
        for div in divergencias:
            # Por tipo
            tipo = div.get("tipo", div.get("tipo_divergencia", "outros"))
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

            # Por prioridade
            prioridade = div.get("prioridade", "MEDIA")
            por_prioridade[prioridade] = por_prioridade.get(prioridade, 0) + 1

            # Por status
            status = div.get("status", "pendente")
            por_status[status] = por_status.get(status, 0) + 1

        # Garantir que todos os campos são inteiros
        por_tipo = {k: int(v) for k, v in por_tipo.items()}
        por_prioridade = {k: int(v) for k, v in por_prioridade.items()}
        por_status = {k: int(v) for k, v in por_status.items()}

        return {
            "total": len(divergencias),
            "por_tipo": por_tipo,
            "por_prioridade": por_prioridade,
            "por_status": por_status,
        }

    except Exception as e:
        logging.error(f"Erro ao calcular estatísticas: {str(e)}")
        logging.error(traceback.format_exc())
        return {
            "total": 0,
            "por_tipo": {},
            "por_prioridade": {"ALTA": 0, "MEDIA": 0},
            "por_status": {"pendente": 0, "em_analise": 0, "resolvida": 0, "cancelada": 0},
        }

def buscar_divergencias_view(
    page: int = 1,
    per_page: int = 10,
    status: Optional[str] = None,
    paciente_nome: Optional[str] = None,
    tipo: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    prioridade: Optional[str] = None,  # Adicionado parâmetro de prioridade
    order_column: str = "data_identificacao",  # Adicionado parâmetro de coluna de ordenação
    order_direction: str = "desc",  # Adicionado parâmetro de direção de ordenação
    execucao_id: Optional[str] = None  # Adicionado parâmetro de execução
) -> Dict:
    """
    Busca divergências com suporte a paginação e filtros.
    
    Args:
        page: Número da página
        per_page: Itens por página
        status: Filtro por status
        paciente_nome: Filtro por nome do paciente
        tipo: Filtro por tipo de divergência
        data_inicio: Filtro por data inicial
        data_fim: Filtro por data final
        prioridade: Filtro por prioridade
        order_column: Coluna para ordenação
        order_direction: Direção da ordenação (asc ou desc)
        execucao_id: Filtro por ID da execução
        
    Returns:
        Dict: Lista paginada de divergências
    """
    try:
        logging.info(f"Iniciando busca de divergências - página {page}, itens por página {per_page}")
        
        # Calcula offset para paginação
        offset = (page - 1) * per_page
        
        # Inicia query na tabela divergencias
        query = supabase.table("divergencias").select("*")
        
        # Aplica filtros
        filtros_aplicados = []
        
        if status and status.lower() != "todos":
            query = query.eq("status", status.lower())
            filtros_aplicados.append(f"status={status.lower()}")
            
        if paciente_nome:
            query = query.ilike("paciente_nome", f"%{paciente_nome.upper()}%")
            filtros_aplicados.append(f"paciente_nome like %{paciente_nome.upper()}%")
            
        if tipo and tipo.lower() != "todos":
            query = query.eq("tipo", tipo)
            filtros_aplicados.append(f"tipo={tipo}")
            
        if data_inicio:
            query = query.gte("data_identificacao", data_inicio)
            filtros_aplicados.append(f"data_identificacao>={data_inicio}")
            
        if data_fim:
            query = query.lte("data_identificacao", data_fim)
            filtros_aplicados.append(f"data_identificacao<={data_fim}")
            
        if prioridade and prioridade.upper() != "TODOS":
            query = query.eq("prioridade", prioridade.upper())
            filtros_aplicados.append(f"prioridade={prioridade.upper()}")
            
        if execucao_id:
            query = query.eq("execucao_id", execucao_id)
            filtros_aplicados.append(f"execucao_id={execucao_id}")
        
        logging.info(f"Filtros aplicados: {', '.join(filtros_aplicados) if filtros_aplicados else 'nenhum'}")
        
        # Ordena pelos parâmetros fornecidos
        is_desc = order_direction.lower() == "desc"
        query = query.order(order_column, desc=is_desc)
        logging.info(f"Ordenando por {order_column} {'DESC' if is_desc else 'ASC'}")
        
        # Busca total de registros com os mesmos filtros
        total_query = supabase.table("divergencias").select("id", count="exact")
        
        # Aplica os mesmos filtros na query de contagem
        if status and status.lower() != "todos":
            total_query = total_query.eq("status", status.lower())
            
        if paciente_nome:
            total_query = total_query.ilike("paciente_nome", f"%{paciente_nome.upper()}%")
            
        if tipo and tipo.lower() != "todos":
            total_query = total_query.eq("tipo", tipo)
            
        if data_inicio:
            total_query = total_query.gte("data_identificacao", data_inicio)
            
        if data_fim:
            total_query = total_query.lte("data_identificacao", data_fim)
            
        if prioridade and prioridade.upper() != "TODOS":
            total_query = total_query.eq("prioridade", prioridade.upper())
            
        if execucao_id:
            total_query = total_query.eq("execucao_id", execucao_id)
        
        # Executa a query de contagem
        total_response = total_query.execute()
        total_registros = total_response.count if total_response.count is not None else len(total_response.data)
        
        logging.info(f"Total de registros encontrados: {total_registros}")
        
        # Aplica paginação na query principal
        query = query.range(offset, offset + per_page - 1)
        
        # Executa a query principal
        response = query.execute()
        divergencias = response.data if response.data else []
        
        logging.info(f"Divergências retornadas na página atual: {len(divergencias)}")
        
        # Formata datas para exibição
        for div in divergencias:
            # Tratar data_identificacao separadamente pois é um timestamp
            if div.get("data_identificacao"):
                try:
                    dt = datetime.fromisoformat(div["data_identificacao"].replace("Z", "+00:00"))
                    div["data_identificacao"] = dt.strftime("%d/%m/%Y")
                except (ValueError, TypeError) as e:
                    logging.error(f"Data inválida em data_identificacao: {div['data_identificacao']}")
                    div["data_identificacao"] = None

            # Tratar datas regulares
            for campo in ["data_execucao", "data_atendimento", "data_resolucao"]:
                try:
                    if div.get(campo):
                        data = div[campo]
                        if isinstance(data, str):
                            if "T" in data:  # Formato ISO com hora
                                data = data.split("T")[0]
                            elif "-" in data:  # Formato YYYY-MM-DD
                                # Validar se é uma data válida
                                datetime.strptime(data, "%Y-%m-%d")
                                # Converter para DD/MM/YYYY
                                div[campo] = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
                            elif "/" in data:  # Já está no formato DD/MM/YYYY
                                # Validar a data
                                datetime.strptime(data, "%d/%m/%Y")
                                div[campo] = data
                            else:
                                div[campo] = None
                    else:
                        div[campo] = None
                except (ValueError, TypeError) as e:
                    logging.error(f"Data inválida em {campo}: {div.get(campo)}")
                    div[campo] = None

        # Atualizar divergências sem data_atendimento
        divergencias_para_atualizar = [
            d for d in divergencias 
            if d.get("codigo_ficha") and (not d.get("ficha_id") or not d.get("data_atendimento"))
        ]
        
        if divergencias_para_atualizar:
            # Buscar dados das fichas
            codigos_ficha = list(set(d["codigo_ficha"] for d in divergencias_para_atualizar))
            fichas_response = (
                supabase.table("fichas")
                .select("id,codigo_ficha,data_atendimento")
                .in_("codigo_ficha", codigos_ficha)
                .execute()
            )
            
            # Criar mapeamento
            fichas_map = {
                f["codigo_ficha"]: {
                    "id": f["id"],
                    "data_atendimento": f["data_atendimento"]
                }
                for f in fichas_response.data or []
            }
            
            # Atualizar divergências
            for div in divergencias:
                if div.get("codigo_ficha") in fichas_map:
                    ficha_data = fichas_map[div["codigo_ficha"]]
                    
                    # Atualizar no banco de dados
                    update_data = {
                        "ficha_id": ficha_data["id"],
                        "data_atendimento": ficha_data["data_atendimento"]
                    }
                    
                    try:
                        response = (
                            supabase.table("divergencias")
                            .update(update_data)
                            .eq("id", div["id"])
                            .execute()
                        )
                        
                        if response.data:
                            # Atualizar objeto local
                            div.update(update_data)
                            if div["data_atendimento"]:
                                # Formatar data para DD/MM/YYYY
                                div["data_atendimento"] = datetime.strptime(
                                    div["data_atendimento"], "%Y-%m-%d"
                                ).strftime("%d/%m/%Y")
                    except Exception as e:
                        logging.error(f"Erro ao atualizar divergência {div['id']}: {e}")

        return {
            "items": divergencias,
            "total": total_registros,
            "pagina_atual": page,
            "total_paginas": ceil(total_registros / per_page) if total_registros > 0 else 0,
            "por_pagina": per_page
        }

    except Exception as e:
        logging.error(f"Erro ao buscar divergências: {str(e)}")
        logging.error(traceback.format_exc())
        return {
            "items": [],
            "total": 0,
            "pagina_atual": page,
            "total_paginas": 0,
            "por_pagina": per_page
        }

def registrar_divergencia_detalhada(divergencia: Dict) -> bool:
    """
    Registra uma divergência com detalhes específicos.
    
    Nota: Esta função aceita tanto o campo "tipo" quanto "tipo_divergencia"
    para compatibilidade, mas internamente padroniza para usar "tipo".
    
    Args:
        divergencia: Dicionário com os dados da divergência
        
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Padronização do campo tipo
        if "tipo_divergencia" in divergencia and "tipo" not in divergencia:
            # Se só tem tipo_divergencia, usar como tipo
            divergencia["tipo"] = divergencia.pop("tipo_divergencia")
        elif "tipo_divergencia" in divergencia and "tipo" in divergencia:
            # Se tem os dois, remover tipo_divergencia e manter tipo
            divergencia.pop("tipo_divergencia")
            
        # Validação dos campos obrigatórios
        if not all([
            divergencia.get("numero_guia"),
            divergencia.get("tipo"),
            divergencia.get("descricao"),
            divergencia.get("paciente_nome")
        ]):
            logging.error(
                f"Campos obrigatórios faltando: {divergencia}")
            return False
            
        # Obter o tipo para definir prioridade
        tipo = divergencia.get("tipo")
        
        # Se não tiver prioridade definida, usa a padrão para o tipo
        if not divergencia.get("prioridade"):
            divergencia["prioridade"] = get_divergencia_priority(tipo)
            
        # Manter as datas no formato original (YYYY-MM-DD) do banco
        data_atendimento = divergencia.get("data_atendimento")
        data_execucao = divergencia.get("data_execucao")

        # Log das datas para debug
        logging.info(f"Datas recebidas - data_atendimento: {data_atendimento}, data_execucao: {data_execucao}")
        
        # Base comum para todos os tipos de divergência
        dados = {
            "numero_guia": divergencia.get("numero_guia"),
            "tipo": tipo,
            "paciente_nome": divergencia.get("paciente_nome"),
            "codigo_ficha": divergencia.get("codigo_ficha"),
            "data_atendimento": data_atendimento,  # Manter o formato YYYY-MM-DD
            "data_execucao": data_execucao,  # Manter o formato YYYY-MM-DD
            "carteirinha": divergencia.get("carteirinha"),
            "prioridade": divergencia.get("prioridade"),
            "status": divergencia.get("status", "pendente"),
            "descricao": divergencia.get("descricao"),
            "detalhes": divergencia.get("detalhes"),
            "ficha_id": divergencia.get("ficha_id"),
            "execucao_id": divergencia.get("execucao_id"),
            "sessao_id": divergencia.get("sessao_id"),
            "paciente_id": divergencia.get("paciente_id")
        }

        # Remover campos None para evitar erro de tipo no banco
        dados = {k: v for k, v in dados.items() if v is not None}

        # Log dos dados antes do insert para debug
        logging.info(f"Registrando divergência: {dados}")
        
        return registrar_divergencia(**dados)

    except Exception as e:
        logging.error(f"Erro ao registrar divergência detalhada: {e}")
        traceback.print_exc()
        return False

def limpar_divergencias_db() -> bool:
    """
    Limpa a tabela de divergências
    
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        logging.info("Iniciando limpeza da tabela divergencias...")
        
        # Simplificar o processo de exclusão
        response = (
            supabase.table("divergencias")
            .delete()
            .neq("id", "00000000-0000-0000-0000-000000000000")
            .execute()
        )
        
        logging.info("Tabela divergencias limpa com sucesso!")
        return True
            
    except Exception as e:
        logging.error(f"Erro ao limpar tabela divergencias: {e}")
        logging.error(traceback.format_exc())
        return False

def atualizar_status_divergencia(
    id: str, novo_status: str, usuario_id: Optional[str] = None
) -> bool:
    """
    Atualiza o status de uma divergência.
    
    Status possíveis:
    - pendente: Aguardando análise
    - em_analise: Em verificação
    - resolvida: Solucionada
    - cancelada: Divergência invalidada
    
    Args:
        id: ID da divergência
        novo_status: Novo status
        usuario_id: ID do usuário responsável (opcional)
        
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        logging.info(f"Tentando atualizar divergência {id} para status: {novo_status}")

        # Primeiro busca a divergência para obter o ficha_id
        divergencia = supabase.table("divergencias").select("*").eq("id", id).execute()
        
        if not divergencia.data:
            logging.error("Divergência não encontrada")
            return False
            
        ficha_id = divergencia.data[0].get("ficha_id")
        
        # Atualiza o status da divergência
        dados = {
            "status": novo_status,
            "data_resolucao": (
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                if novo_status == "resolvida"
                else None
            ),
            "resolvido_por": usuario_id if novo_status == "resolvida" else None,
        }
        
        response = supabase.table("divergencias").update(dados).eq("id", id).execute()
        
        # Se a divergência foi resolvida e temos um ficha_id, atualiza a ficha
        if novo_status == "resolvida" and ficha_id:
            logging.info(f"Atualizando status da ficha {ficha_id} para conferida")
            ficha_response = (
                supabase.table("fichas")
                .update({"status": "conferida"})
                .eq("id", ficha_id)
                .execute()
            )
            if not ficha_response.data:
                logging.warning("Erro ao atualizar status da ficha")
        
        return True

    except Exception as e:
        logging.error(f"Erro ao atualizar status da divergência: {e}")
        traceback.print_exc()
        return False

def obter_ultima_auditoria() -> Dict:
    """
    Obtém o resultado da última auditoria realizada
    
    Returns:
        Dict: Dados da última auditoria
    """
    try:
        response = (
            supabase.table("auditoria_execucoes")
            .select("*")
            .order("data_execucao", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return {
                "total_protocolos": 0,
                "total_divergencias": 0,
                "divergencias_por_tipo": {},
                "total_fichas": 0,
                "total_execucoes": 0,
                "total_resolvidas": 0,
                "data_execucao": None,
                "tempo_execucao": None
            }

        ultima_auditoria = response.data[0]

        # Calcula o tempo desde a última execução
        data_execucao = datetime.fromisoformat(ultima_auditoria["data_execucao"].replace("Z", "+00:00"))
        agora = datetime.now(timezone.utc)
        diferenca = agora - data_execucao

        # Formata o tempo de execução
        if diferenca.days > 0:
            tempo_execucao = f"Há {diferenca.days} dias"
        elif diferenca.seconds > 3600:
            tempo_execucao = f"Há {diferenca.seconds // 3600} horas"
        elif diferenca.seconds > 60:
            tempo_execucao = f"Há {diferenca.seconds // 60} minutos"
        else:
            tempo_execucao = f"Há {diferenca.seconds} segundos"

        return {
            "total_protocolos": ultima_auditoria.get("total_protocolos", 0),
            "total_divergencias": ultima_auditoria.get("total_divergencias", 0),
            "divergencias_por_tipo": ultima_auditoria.get("divergencias_por_tipo", {}),
            "total_fichas": ultima_auditoria.get("total_fichas", 0),
            "total_execucoes": ultima_auditoria.get("total_execucoes", 0),
            "total_resolvidas": ultima_auditoria.get("total_resolvidas", 0),
            "data_execucao": ultima_auditoria["data_execucao"],
            "tempo_execucao": tempo_execucao
        }

    except Exception as e:
        logging.error(f"Erro ao obter última auditoria: {str(e)}")
        return None

def listar_divergencias(
    page: int = 1,
    per_page: int = 10,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: Optional[str] = None,
    tipo: Optional[str] = None,
    prioridade: Optional[str] = None,
    order_column: str = "data_identificacao",
    order_direction: str = "desc"
) -> Dict:
    """
    Lista divergências com paginação e filtros.
    
    Args:
        page: Número da página
        per_page: Itens por página
        data_inicio: Filtro por data inicial
        data_fim: Filtro por data final
        status: Filtro por status
        tipo: Filtro por tipo de divergência
        prioridade: Filtro por prioridade
        order_column: Coluna para ordenação
        order_direction: Direção da ordenação (asc ou desc)
        
    Returns:
        Dict: Lista paginada de divergências
    """
    return buscar_divergencias_view(
        page=page,
        per_page=per_page,
        data_inicio=data_inicio,
        data_fim=data_fim,
        status=status,
        tipo=tipo,
        paciente_nome=None,  # Mantém compatibilidade com a interface existente
        prioridade=prioridade,  # Adicionado parâmetro de prioridade
        order_column=order_column,  # Adicionado parâmetro de coluna de ordenação
        order_direction=order_direction  # Adicionado parâmetro de direção de ordenação
    )


def registrar_divergencia(
    numero_guia: str,
    tipo: str,  # Padronizado para usar "tipo" em vez de "tipo_divergencia"
    descricao: str,
    paciente_nome: str,
    codigo_ficha: str = None,
    data_execucao: str = None,
    data_atendimento: str = None,
    carteirinha: str = None,
    prioridade: str = "MEDIA",
    status: str = "pendente",
    detalhes: Dict = None,
    ficha_id: str = None,
    execucao_id: str = None,
    sessao_id: str = None,
    paciente_id: str = None
) -> bool:
    """
    Registra uma divergência no banco de dados.
    
    Nota: Este método usa o campo "tipo" consistentemente em vez de "tipo_divergencia"
    para manter compatibilidade com o resto do sistema. Em alguns lugares do código
    ainda pode existir referência a "tipo_divergencia", que é tratada como alias
    de "tipo" através de mapeamentos.
    
    Args:
        numero_guia: Número da guia relacionada
        tipo: Tipo da divergência
        descricao: Descrição detalhada
        paciente_nome: Nome do paciente
        codigo_ficha: Código da ficha (opcional)
        data_execucao: Data de execução (opcional)
        data_atendimento: Data de atendimento (opcional)
        carteirinha: Número da carteirinha (opcional)
        prioridade: Prioridade da divergência (ALTA, MEDIA, BAIXA)
        status: Status inicial (pendente, em_analise, resolvida, ignorada)
        detalhes: Informações adicionais em formato JSON (opcional)
        ficha_id: ID da ficha relacionada (opcional)
        execucao_id: ID da execução relacionada (opcional)
        sessao_id: ID da sessão relacionada (opcional)
        paciente_id: ID do paciente (opcional)
        
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        # Validar campos obrigatórios
        if not all([numero_guia, tipo, descricao, paciente_nome]):
            logging.error("Campos obrigatórios não informados")
            return False

        # Função melhorada para parsear datas
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                # Se já estiver no formato YYYY-MM-DD
                if isinstance(date_str, str):
                    if len(date_str) == 10 and "-" in date_str:
                        # Validar formato da data
                        datetime.strptime(date_str, "%Y-%m-%d")
                        return date_str

                    # Se estiver no formato DD/MM/YYYY
                    if "/" in date_str:
                        day, month, year = date_str.split("/")
                        # Converter para YYYY-MM-DD
                        date_obj = datetime(int(year), int(month), int(day))
                        return date_obj.strftime("%Y-%m-%d")

                    # Se for timestamp, extrair apenas a data
                    if "T" in date_str:
                        return date_str.split("T")[0]

                return None
            except Exception as e:
                logging.error(f"Erro ao parsear data: {date_str} - {str(e)}")
                return None

        # Log adicional para busca de dados da ficha
        if codigo_ficha:
            try:
                logging.info(f"Buscando ficha com código: {codigo_ficha}")
                
                # Primeiro verificar se a ficha existe
                ficha_exists_response = (
                    supabase.table("fichas")
                    .select("count", count="exact")
                    .eq("codigo_ficha", codigo_ficha)
                    .execute()
                )
                
                total_fichas = ficha_exists_response.count
                logging.info(f"Total de fichas encontradas: {total_fichas}")

                # Então obter os dados reais
                ficha_response = (
                    supabase.table("fichas")
                    .select("*")  # Selecionar todos os campos para melhor debug
                    .eq("codigo_ficha", codigo_ficha)
                    .execute()
                )
                
                if ficha_response.data:
                    ficha = ficha_response.data[0]
                    logging.info(f"Dados da ficha encontrada: {ficha}")
                    
                    data_atendimento = ficha.get("data_atendimento")
                    if data_atendimento:
                        logging.info(f"Data de atendimento encontrada: {data_atendimento}")
                    else:
                        logging.warning("Data de atendimento não encontrada na ficha")
                        
                    carteirinha = ficha.get("paciente_carteirinha")
                    if carteirinha:
                        logging.info(f"Carteirinha encontrada: {carteirinha}")
                    else:
                        logging.warning("Carteirinha não encontrada na ficha")
                        
                    # Obter ficha_id para vinculação
                    ficha_id = ficha.get("id")
                    if ficha_id:
                        logging.info(f"ID da ficha encontrado: {ficha_id}")
                    else:
                        logging.warning("ID da ficha não encontrado")
                    
                else:
                    logging.warning(f"Nenhuma ficha encontrada com código: {codigo_ficha}")
                    
            except Exception as e:
                logging.error(f"Erro ao buscar dados da ficha: {str(e)}")
                logging.error(traceback.format_exc())

        # Formatar data_identificacao para ser apenas a parte da data
        data_identificacao = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Dados base da divergência
        dados = {
            "numero_guia": numero_guia,
            "tipo": tipo,
            "descricao": descricao,
            "paciente_nome": paciente_nome.upper(),
            "status": status,
            "data_identificacao": data_identificacao,
            "prioridade": prioridade,
            "codigo_ficha": codigo_ficha,
            "data_execucao": parse_date(data_execucao),
            "data_atendimento": parse_date(data_atendimento),
            "carteirinha": carteirinha,
            "detalhes": detalhes,
            "ficha_id": ficha_id if 'ficha_id' in locals() else None,
            "execucao_id": execucao_id,
            "sessao_id": sessao_id,
            "paciente_id": paciente_id
        }

        # Log de dados completos antes da inserção
        logging.info(f"Dados completos antes do insert: {dados}")

        # Remover valores None mas manter strings vazias para campos de texto
        dados = {k: (v if v is not None else '') for k, v in dados.items() 
                if k in ['carteirinha', 'codigo_ficha'] or v is not None}

        # Log de dados finais a serem inseridos
        logging.info(f"Dados finais para insert: {dados}")

        # Inserir no banco
        response = supabase.table("divergencias").insert(dados).execute()
        
        if response.data:
            logging.info(f"Divergência registrada com sucesso: {response.data[0]}")
            return True
        else:
            logging.error("Erro: Resposta vazia do Supabase")
            return False

    except Exception as e:
        logging.error(f"Erro ao registrar divergência: {e}")
        traceback.print_exc()
        return False

def atualizar_ficha_ids_divergencias(divergencias: Optional[List[Dict]] = None) -> bool:
    """
    Atualiza os ficha_ids e data_atendimento nas divergências.
    
    Args:
        divergencias: Lista de divergências a atualizar (opcional)
        
    Returns:
        bool: True se a operação foi bem-sucedida, False caso contrário
    """
    try:
        if divergencias == None:
            # Busca divergências sem ficha_id
            response = (
                supabase.table("divergencias")
                .select("*")
                .is_("ficha_id", "null")
                .not_.is_("codigo_ficha", "null")
                .execute()
            )
            divergencias = response.data if response.data else []

        if not divergencias:
            logging.info("Nenhuma divergência para atualizar")
            return True

        # Obter valores únicos de codigo_ficha
        codigos_ficha = list(set(
            div["codigo_ficha"] 
            for div in divergencias 
            if div.get("codigo_ficha")
        ))
        
        if not codigos_ficha:
            return True

        # Incluir data_atendimento no select
        fichas_response = (
            supabase.table("fichas")
            .select("id,codigo_ficha,data_atendimento")
            .in_("codigo_ficha", codigos_ficha)
            .execute()
        )
        
        # Mapear tanto id quanto data_atendimento
        mapa_fichas = {
            f["codigo_ficha"]: {
                "id": f["id"],
                "data_atendimento": f["data_atendimento"]
            }
            for f in fichas_response.data or []
        }

        count = 0
        for div in divergencias:
            if div.get("codigo_ficha") in mapa_fichas:
                ficha_data = mapa_fichas[div["codigo_ficha"]]
                try:
                    # Atualizar tanto ficha_id quanto data_atendimento
                    response = (
                        supabase.table("divergencias")
                        .update({
                            "ficha_id": ficha_data["id"],
                            "data_atendimento": ficha_data["data_atendimento"]
                        })
                        .eq("id", div["id"])
                        .execute()
                    )
                    if response.data:
                        count += 1
                except Exception as e:
                    logging.error(f"Erro ao atualizar divergência {div['id']}: {e}")
                    continue

        logging.info(f"Atualizadas {count} divergências com ficha_id e data_atendimento")
        return True

    except Exception as e:
        logging.error(f"Erro ao atualizar ficha_ids: {str(e)}")
        traceback.print_exc()
        return False