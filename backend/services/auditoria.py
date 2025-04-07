from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import traceback
from fastapi import APIRouter, HTTPException

# Importações necessárias
from backend.config.config import supabase

# Imports do database_supabase
from backend.repositories.database_supabase import (list_fichas, list_execucoes,
                               list_guias)
from backend.utils.date_utils import formatar_data

# Imports do auditoria_repository
from backend.repositories.auditoria_repository import (
    registrar_execucao_auditoria,
    buscar_divergencias_view,
    obter_ultima_auditoria,
    atualizar_status_divergencia,
    calcular_estatisticas_divergencias,
    registrar_divergencia_detalhada,
    registrar_divergencia,
    limpar_divergencias_db,
    listar_divergencias,
    atualizar_ficha_ids_divergencias
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Classe AuditoriaService
class AuditoriaService:
    def __init__(self, divergencia_repo, auditoria_repo):
        self.divergencia_repo = divergencia_repo
        self.auditoria_repo = auditoria_repo
        
    async def realizar_auditoria(self, data_inicial=None, data_final=None):
        return await realizar_auditoria_fichas_execucoes(data_inicial, data_final)
        
    async def listar_divergencias(
        self, 
        limit=10, 
        offset=0, 
        data_inicio=None, 
        data_fim=None, 
        status=None, 
        tipo=None, 
        prioridade=None,
        order_column="data_identificacao",
        order_direction="desc"
    ):
        # Convertendo offset/limit para page/per_page para compatibilidade
        page = (offset // limit) + 1 if limit > 0 else 1
        per_page = limit
        
        logging.info(f"Buscando divergências com parâmetros: page={page}, per_page={per_page}, " +
                     f"data_inicio={data_inicio}, data_fim={data_fim}, status={status}, " +
                     f"tipo={tipo}, prioridade={prioridade}, order_column={order_column}, " +
                     f"order_direction={order_direction}")
        
        # Chamando a função existente com os parâmetros convertidos
        result = listar_divergencias(
            page=page, 
            per_page=per_page, 
            data_inicio=data_inicio, 
            data_fim=data_fim, 
            status=status, 
            tipo=tipo, 
            prioridade=prioridade,
            order_column=order_column,
            order_direction=order_direction
        )
        
        # Log do resultado
        total_items = len(result.get("items", []))
        total_registros = result.get("total", 0)
        logging.info(f"Divergências encontradas: {total_items} itens retornados de um total de {total_registros} registros")
        
        # Ajustando o resultado para o formato esperado pelo frontend
        return {
            "items": result.get("items", []),
            "total": result.get("total", 0),
            "limit": limit,
            "offset": offset
        }
        
    def atualizar_status_divergencia(self, id, novo_status, usuario_id=None):
        return atualizar_status_divergencia(id, novo_status, usuario_id)
        
    def calcular_estatisticas_divergencias(self):
        return calcular_estatisticas_divergencias()
        
    def obter_ultima_auditoria(self):
        return obter_ultima_auditoria()

# Criar router com prefixo
router = APIRouter(prefix="/divergencias", tags=["divergencias"])

# Define os tipos de divergências conforme a documentação
tipos_divergencias = {
    "ficha_sem_execucao": "Ficha registrada sem execução correspondente",
    "execucao_sem_ficha": "Execução registrada sem ficha correspondente",
    "data_divergente": "Data da execução diferente da data da sessão",
    "sessao_sem_assinatura": "Sessão sem assinatura do paciente",
    "guia_vencida": "Guia com data de validade expirada",
    "quantidade_excedida": "Quantidade de execuções maior que autorizado",
    "falta_data_execucao": "Execução sem data registrada",
    "duplicidade": "Execução registrada em duplicidade"
}

def verificar_datas(protocolo: Dict, execucao: Dict) -> bool:
    """
    Verifica se as datas do protocolo e execução correspondem.
    
    Regras:
    1. Data da execução deve ser igual à data da sessão
    2. Data não pode ser futura
    3. Data deve estar dentro da validade da guia
    """
    try:
        data_protocolo = datetime.strptime(protocolo["data_atendimento"], "%Y-%m-%d")
        data_execucao = datetime.strptime(execucao["data_execucao"], "%Y-%m-%d")
        
        # Verificação 1: Datas devem corresponder
        if data_protocolo != data_execucao:
            return False
            
        # Verificação 2: Data não pode ser futura
        data_atual = datetime.now().date()
        if data_execucao.date() > data_atual:
            return False
            
        # A verificação 3 (validade da guia) é feita separadamente
        return True
    except (ValueError, KeyError, TypeError) as e:
        logging.error(f"Erro ao comparar datas: {e}")
        return False

def verificar_quantidade_execucoes(protocolo: Dict, execucoes: List[Dict]) -> bool:
    """
    Verifica se a quantidade de execuções está dentro do limite.
    
    Regras:
    1. Não pode exceder quantidade autorizada na guia
    2. Não pode haver duplicidade no mesmo dia
    3. Deve respeitar intervalo mínimo entre sessões
    """
    try:
        quantidade_autorizada = int(protocolo.get("quantidade_autorizada", 0))
        quantidade_executada = len(execucoes)
        
        # Verificação 1: Quantidade não pode exceder o autorizado
        if quantidade_executada > quantidade_autorizada:
            return False
            
        # Verificação 2: Não pode haver duplicidades (verificado separadamente)
        # Verificação 3: Intervalo entre sessões (implementação simplificada)
        return True
    except (ValueError, KeyError, TypeError) as e:
        logging.error(f"Erro ao verificar quantidade de execuções: {e}")
        return False

def formatar_data_iso(data_str: str) -> str:
    """
    Converte uma data no formato YYYY-MM-DD para DD/MM/YYYY para exibição.
    """
    try:
        data = datetime.strptime(data_str, "%Y-%m-%d")
        return data.strftime("%d/%m/%Y")
    except ValueError:
        return data_str

def verificar_validade_guia(guia: Dict) -> bool:
    """
    Verifica se a guia está dentro do prazo de validade.

    Args:
        guia: Dicionário contendo os dados da guia

    Returns:
        bool: True se a guia está válida, False caso contrário
    """
    try:
        if not guia.get("data_validade"):
            return True

        data_validade = datetime.strptime(guia["data_validade"], "%Y-%m-%d")
        return datetime.now().date() <= data_validade.date()
    except (ValueError, KeyError, TypeError) as e:
        logging.error(f"Erro ao verificar validade da guia: {e}")
        return False

def verificar_assinatura_sessao(sessao: Dict) -> bool:
    """
    Verifica se a sessão possui assinatura do paciente.
    
    Regras:
    1. Deve ter assinatura do paciente
    2. Sessão executada deve ter assinatura
    
    Args:
        sessao: Dicionário contendo os dados da sessão

    Returns:
        bool: True se a sessão está assinada, False caso contrário
    """
    # Verifica se a sessão foi executada e possui assinatura
    if sessao.get("status") == "executada" and not sessao.get("possui_assinatura", False):
        return False
    return True

def verificar_duplicidade_execucoes(execucoes: List[Dict]) -> List[Dict]:
    """
    Identifica execuções duplicadas.
    
    Regras:
    1. Mesma data
    2. Mesmo procedimento
    3. Mesmo paciente
    4. Mesma guia
    
    Args:
        execucoes: Lista de execuções a verificar

    Returns:
        List[Dict]: Lista de grupos de execuções duplicadas
    """
    duplicatas = {}
    for exec in execucoes:
        # Criar chave composta dos critérios de duplicidade
        codigo_ficha = exec.get("codigo_ficha")
        sessao_id = exec.get("sessao_id")
        numero_guia = exec.get("numero_guia")
        data_execucao = exec.get("data_execucao")
        
        if not codigo_ficha or not sessao_id:
            continue
            
        # Chave composta para identificar execuções idênticas
        chave = f"{codigo_ficha}_{sessao_id}_{numero_guia}_{data_execucao}"
        
        if chave in duplicatas:
            duplicatas[chave].append(exec)
        else:
            duplicatas[chave] = [exec]
    
    # Retorna apenas os grupos com mais de uma execução (duplicatas)
    return [execs for execs in duplicatas.values() if len(execs) > 1]

def verificar_falta_data_execucao(execucoes: List[Dict]) -> List[Dict]:
    """
    Identifica execuções sem data registrada.
    
    Args:
        execucoes: Lista de execuções a verificar

    Returns:
        List[Dict]: Lista de execuções sem data
    """
    return [exec for exec in execucoes if not exec.get("data_execucao")]

def safe_get_value(dict_obj: Dict, key: str, default=None):
    """
    Obtém valor de um dicionário de forma segura com logging.
    
    Args:
        dict_obj: Dicionário a ser consultado
        key: Chave a buscar
        default: Valor padrão se a chave não existir

    Returns:
        O valor da chave ou o valor padrão
    """
    try:
        return dict_obj.get(key, default)
    except (TypeError, AttributeError) as e:
        logging.warning(f"Erro ao acessar {key}: {e}")
        return default

def get_divergencia_priority(tipo: str) -> str:
    """
    Determina a prioridade de uma divergência com base no tipo.
    
    Args:
        tipo: Tipo da divergência
        
    Returns:
        str: Prioridade da divergência (ALTA ou MEDIA)
    """
    prioridades = {
        "execucao_sem_ficha": "ALTA",
        "ficha_sem_execucao": "ALTA",
        "data_divergente": "MEDIA",
        "ficha_sem_assinatura": "MEDIA",
        "sessao_sem_assinatura": "MEDIA",
        "guia_vencida": "ALTA",
        "quantidade_excedida": "ALTA",
        "duplicidade": "ALTA",
        "falta_data_execucao": "MEDIA"
    }
    
    return prioridades.get(tipo, "MEDIA")

async def realizar_auditoria_fichas_execucoes(
    data_inicial: str = None,
    data_final: str = None
):
    """
    Realiza auditoria comparando sessões e execuções diretamente das tabelas.
    
    Args:
        data_inicial: Data de início do período de auditoria (opcional)
        data_final: Data de fim do período de auditoria (opcional)
        
    Returns:
        Dict: Resultado da auditoria com estatísticas
    """
    try:
        # Limpa divergências antigas
        limpar_divergencias_db()

        # Busca os dados diretamente das tabelas
        try:
            # Buscar sessões com dados de fichas
            sessoes = supabase.table("sessoes") \
                .select("*, fichas!sessoes_ficha_id_fkey(*)") \
                .execute()

            # Buscar execuções com dados de guias
            execucoes = supabase.table("execucoes") \
                .select("*, guias!execucoes_guia_id_fkey(*)") \
                .execute()

            # Buscar guias com dados de carteirinhas
            guias_response = supabase.table("guias") \
                .select("*, carteirinhas!guias_carteirinha_id_fkey(*)") \
                .execute()
            guias = guias_response.data if guias_response and hasattr(
                guias_response, 'data') else []

            # Extrair dados das respostas
            sessoes_data = sessoes.data if sessoes and hasattr(
                sessoes, 'data') else []
            execucoes_data = execucoes.data if execucoes and hasattr(
                execucoes, 'data') else []

        except Exception as e:
            logging.error(f"Erro ao buscar dados das tabelas: {e}")
            raise Exception(f"Erro ao buscar dados: {e}")

        # Validar e formatar dados para processamento
        def validar_lista_dados(response, nome_item):
            """Valida se os dados foram carregados corretamente"""
            if not response:
                logging.warning(f"Nenhum dado encontrado para {nome_item}")
                return []

            if isinstance(response, list):
                dados = response
            elif isinstance(response, dict):
                dados = response.get('data', [])
            else:
                logging.error(
                    f"Formato inválido para {nome_item}: {type(response)}")
                return []

            # Validação adicional
            dados_validos = []
            for item in dados:
                if isinstance(item, dict):
                    dados_validos.append(item)
                else:
                    logging.warning(
                        f"Item inválido em {nome_item}: {type(item)}")

            return dados_validos

        fichas = validar_lista_dados(sessoes_data, "fichas")
        execucoes = validar_lista_dados(execucoes_data, "execucoes")

        # Logging detalhado
        logging.info(f"Fichas válidas carregadas: {len(fichas)}")
        logging.info(f"Execuções válidas carregadas: {len(execucoes)}")

        # Indexação por código_ficha para facilitar busca
        mapa_fichas = {}
        mapa_execucoes = {}
        execucoes_por_guia = {}

        # Mapear fichas por código
        for f in fichas:
            ficha_data = f.get("fichas", {})
            codigo = ficha_data.get("codigo_ficha")
            if codigo:
                mapa_fichas[codigo] = ficha_data
            else:
                logging.warning(f"Ficha sem código: {f}")

        # Mapear execuções por código e guia
        for e in execucoes:
            codigo = safe_get_value(e, "codigo_ficha")
            numero_guia = safe_get_value(e, "numero_guia")

            if codigo:
                mapa_execucoes[codigo] = e
            else:
                logging.warning(f"Execução sem código: {e}")

            if numero_guia:
                if numero_guia not in execucoes_por_guia:
                    execucoes_por_guia[numero_guia] = []
                execucoes_por_guia[numero_guia].append(e)

        # Inicializar contadores de divergências
        divergencias_encontradas = {
            "ficha_sem_execucao": 0,
            "execucao_sem_ficha": 0,
            "data_divergente": 0,
            "sessao_sem_assinatura": 0,
            "guia_vencida": 0,
            "quantidade_excedida": 0,
            "falta_data_execucao": 0,
            "duplicidade": 0
        }

        # 1. Verifica datas divergentes
        for codigo_ficha, execucao in mapa_execucoes.items():
            ficha = mapa_fichas.get(codigo_ficha)
            if ficha and ficha.get("data_atendimento") and ficha["data_atendimento"] != execucao["data_execucao"]:
                if not execucao.get("numero_guia"):
                    logging.warning(f"Execução sem número de guia: {codigo_ficha}")
                    continue

                registrar_divergencia_detalhada({
                    "numero_guia": execucao["numero_guia"],
                    "tipo": "data_divergente",
                    "descricao": f"Data de atendimento ({ficha['data_atendimento']}) diferente da execução ({execucao['data_execucao']})",
                    "paciente_nome": execucao["paciente_nome"] or ficha["paciente_nome"],
                    "codigo_ficha": codigo_ficha,
                    "data_execucao": execucao["data_execucao"],
                    "data_atendimento": ficha["data_atendimento"],
                    "prioridade": "MEDIA",
                    "status": "pendente",
                    "ficha_id": ficha.get("id"),
                    "execucao_id": execucao.get("id")
                })
                divergencias_encontradas["data_divergente"] += 1

        # 2. Verifica sessões sem assinatura
        for sessao in sessoes_data:
            ficha_dados = sessao.get("fichas", {})

            # Verifica se a sessão foi executada E não possui assinatura
            if sessao.get("status") == "executada" and not sessao.get("possui_assinatura"):
                # Usar data_sessao tanto para data_execucao quanto para data_atendimento
                data_sessao = sessao.get("data_sessao")

                logging.info(f"""
                    Registrando divergência sessão sem assinatura:
                    Sessão ID: {sessao.get('id')}
                    Data sessão: {data_sessao}
                    Ficha: {ficha_dados.get('codigo_ficha')}
                """)

                registrar_divergencia_detalhada({
                    "numero_guia": ficha_dados.get("numero_guia"),
                    "tipo": "sessao_sem_assinatura",
                    "descricao": f"Sessão do dia {data_sessao} executada sem assinatura",
                    "paciente_nome": ficha_dados.get("paciente_nome"),
                    "codigo_ficha": ficha_dados.get("codigo_ficha"),
                    "data_execucao": data_sessao,
                    "data_atendimento": data_sessao,
                    "prioridade": "ALTA",
                    "ficha_id": sessao.get("ficha_id"),
                    "detalhes": {
                        "sessao_id": sessao.get("id"),
                        "data_sessao": data_sessao
                    }
                })
                divergencias_encontradas["sessao_sem_assinatura"] += 1

        # 3. e 4. Verifica execuções sem ficha e fichas sem execução
        todos_codigos = set(list(mapa_fichas.keys()) + list(mapa_execucoes.keys()))
        for codigo_ficha in todos_codigos:
            execucao = mapa_execucoes.get(codigo_ficha)
            ficha = mapa_fichas.get(codigo_ficha)

            if execucao and not ficha:
                registrar_divergencia_detalhada({
                    "numero_guia": execucao.get("guias", {}).get("numero_guia"),
                    "tipo": "execucao_sem_ficha",
                    "descricao": "Execução sem ficha correspondente",
                    "paciente_nome": execucao.get("paciente_nome"),
                    "codigo_ficha": codigo_ficha,
                    "data_execucao": execucao.get("data_execucao"),
                    "prioridade": "ALTA",
                    "execucao_id": execucao.get("id")
                })
                divergencias_encontradas["execucao_sem_ficha"] += 1

            elif ficha and not execucao:
                ficha_data = ficha.get("fichas", {})
                registrar_divergencia_detalhada({
                    "numero_guia": ficha_data.get("numero_guia"),
                    "tipo": "ficha_sem_execucao",
                    "descricao": "Ficha sem execução correspondente",
                    "paciente_nome": ficha_data.get("paciente_nome"),
                    "codigo_ficha": codigo_ficha,
                    "data_atendimento": ficha_data.get("data_atendimento"),
                    "prioridade": "ALTA",
                    "ficha_id": ficha_data.get("id")
                })
                divergencias_encontradas["ficha_sem_execucao"] += 1

        # 5. Verifica quantidade excedida por guia
        for guia in guias:
            execucoes_guia = execucoes_por_guia.get(guia["numero_guia"], [])
            if len(execucoes_guia) > guia.get("quantidade_autorizada", 0):
                registrar_divergencia_detalhada({
                    "numero_guia": guia["numero_guia"],
                    "tipo": "quantidade_excedida",
                    "descricao": f"Quantidade de execuções ({len(execucoes_guia)}) excede o autorizado ({guia['quantidade_autorizada']})",
                    "paciente_nome": execucoes_guia[0]["paciente_nome"] if execucoes_guia else "",
                    "detalhes": {
                        "quantidade_autorizada": guia["quantidade_autorizada"],
                        "quantidade_executada": len(execucoes_guia)
                    },
                    "prioridade": "ALTA",
                    "status": "pendente"
                })
                divergencias_encontradas["quantidade_excedida"] += 1

            # 6. Verifica guia vencida
            if guia.get("data_validade"):
                data_validade = datetime.strptime(guia["data_validade"], "%Y-%m-%d")
                if datetime.now() > data_validade:
                    registrar_divergencia_detalhada({
                        "numero_guia": guia["numero_guia"],
                        "tipo": "guia_vencida",
                        "descricao": f"Guia vencida em {guia['data_validade']}",
                        "paciente_nome": execucoes_guia[0]["paciente_nome"] if execucoes_guia else "",
                        "detalhes": {
                            "data_validade": guia["data_validade"]
                        },
                        "prioridade": "ALTA",
                        "status": "pendente"
                    })
                    divergencias_encontradas["guia_vencida"] += 1

        # 7. Verifica falta de data de execução
        execucoes_sem_data = verificar_falta_data_execucao(execucoes_data)
        for execucao in execucoes_sem_data:
            registrar_divergencia_detalhada({
                "numero_guia": execucao.get("numero_guia"),
                "tipo": "falta_data_execucao",
                "descricao": "Execução sem data registrada",
                "paciente_nome": execucao.get("paciente_nome"),
                "codigo_ficha": execucao.get("codigo_ficha"),
                "prioridade": "ALTA",
                "execucao_id": execucao.get("id")
            })
            divergencias_encontradas["falta_data_execucao"] += 1

        # 8. Verifica duplicidades
        duplicatas = verificar_duplicidade_execucoes(execucoes_data)
        for grupo_duplicado in duplicatas:
            primeira_exec = grupo_duplicado[0]
            
            # Busca a ficha correspondente para obter dados complementares
            ficha = None
            if primeira_exec.get("codigo_ficha"):
                ficha_response = (
                    supabase.table("fichas")
                    .select("*")
                    .eq("codigo_ficha", primeira_exec["codigo_ficha"])
                    .execute()
                )
                if ficha_response.data:
                    ficha = ficha_response.data[0]

            registrar_divergencia_detalhada({
                "numero_guia": primeira_exec["numero_guia"],
                "tipo": "duplicidade",
                "descricao": (
                    f"Sessão {primeira_exec['sessao_id']} da ficha {primeira_exec['codigo_ficha']} "
                    f"processada {len(grupo_duplicado)} vezes"
                ),
                "paciente_nome": primeira_exec["paciente_nome"],
                "codigo_ficha": primeira_exec.get("codigo_ficha"),
                "data_execucao": primeira_exec["data_execucao"],
                "data_atendimento": ficha["data_atendimento"] if ficha else None,
                "carteirinha": primeira_exec.get("carteirinha"),
                "prioridade": "ALTA",
                "detalhes": {
                    "total_duplicatas": len(grupo_duplicado),
                    "execucoes_ids": [exec["id"] for exec in grupo_duplicado],
                    "datas_execucao": [exec["data_execucao"] for exec in grupo_duplicado],
                    "sessao_id": primeira_exec.get("sessao_id")
                }
            })
            divergencias_encontradas["duplicidade"] += 1

        # Calcular estatísticas finais
        total_divergencias = sum(divergencias_encontradas.values())
        total_resolvidas = 0

        # Buscar contagens da tabela de divergências para obter resolvidas
        divergencias_count = (
            supabase.table("divergencias")
            .select("status", count="exact")
            .eq("status", "resolvida")
            .execute()
        )

        if divergencias_count.data:
            total_resolvidas = divergencias_count.count

        # Registrar execução da auditoria com estatísticas completas
        registrar_execucao_auditoria(
            data_inicial=data_inicial,
            data_final=data_final,
            total_protocolos=len(fichas) + len(execucoes),
            total_divergencias=total_divergencias,
            divergencias_por_tipo=divergencias_encontradas,
            total_fichas=len(fichas),
            total_execucoes=len(execucoes),
            total_resolvidas=total_resolvidas
        )

        return {
            "success": True, 
            "stats": {
                "total_fichas": len(fichas),
                "total_execucoes": len(execucoes),
                "divergencias_por_tipo": divergencias_encontradas,
                "total_divergencias": total_divergencias,
                "total_resolvidas": total_resolvidas
            }
        }

    except Exception as e:
        logging.error(f"Erro na auditoria: {str(e)}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@router.get("/")
def listar_divergencias_route(
        page: int = 1,
        per_page: int = 10,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        status: Optional[str] = None,
        tipo: Optional[str] = None,
        prioridade: Optional[str] = None,
):
    """
    Lista as divergências encontradas na auditoria
    
    Args:
        page: Número da página
        per_page: Itens por página
        data_inicio: Filtro por data inicial
        data_fim: Filtro por data final
        status: Filtro por status
        tipo: Filtro por tipo de divergência
        prioridade: Filtro por prioridade
        
    Returns:
        Dict: Lista paginada de divergências
    """
    try:
        return listar_divergencias(
            page=page,
            per_page=per_page,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            tipo=tipo,
            prioridade=prioridade,
        )
    except Exception as e:
        logging.error(f"Erro ao listar divergências: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500,
                            detail=f"Erro ao listar divergências: {str(e)}")


@router.post("/auditoria/executar")
async def executar_auditoria_route(
    data_inicial: Optional[str] = None,
    data_final: Optional[str] = None
):
    """
    Executa a auditoria de divergências
    
    Args:
        data_inicial: Data de início do período (opcional)
        data_final: Data de fim do período (opcional)
        
    Returns:
        Dict: Resultado da auditoria
    """
    try:
        resultado = await realizar_auditoria_fichas_execucoes(
            data_inicial=data_inicial,
            data_final=data_final
        )
        return resultado
    except Exception as e:
        logging.error(f"Erro ao executar auditoria: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500,
                            detail=f"Erro ao executar auditoria: {str(e)}")


@router.put("/{id}/status")
async def atualizar_status_divergencia_route(
    id: str,
    novo_status: str,
    usuario_id: Optional[str] = None
):
    """
    Atualiza o status de uma divergência
    
    Args:
        id: ID da divergência
        novo_status: Novo status (pendente, em_analise, resolvida, cancelada)
        usuario_id: ID do usuário responsável (opcional)
        
    Returns:
        Dict: Resultado da operação
    """
    try:
        resultado = atualizar_status_divergencia(
            id=id,
            novo_status=novo_status,
            usuario_id=usuario_id
        )
        return {"success": resultado}
    except Exception as e:
        logging.error(f"Erro ao atualizar status: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500,
                            detail=f"Erro ao atualizar status: {str(e)}")


@router.get("/estatisticas")
async def obter_estatisticas_route():
    """
    Retorna estatísticas gerais das divergências
    
    Returns:
        Dict: Estatísticas das divergências
    """
    try:
        return calcular_estatisticas_divergencias()
    except Exception as e:
        logging.error(f"Erro ao obter estatísticas: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500,
                            detail=f"Erro ao obter estatísticas: {str(e)}")


@router.get("/ultima")
async def obter_ultima_auditoria_route():
    """
    Retorna dados da última auditoria executada
    
    Returns:
        Dict: Dados da última auditoria
    """
    try:
        return obter_ultima_auditoria()
    except Exception as e:
        logging.error(f"Erro ao obter última auditoria: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500,
                            detail=f"Erro ao obter última auditoria: {str(e)}")


if __name__ == "__main__":
    # Exemplo de uso: python auditoria.py
    import asyncio
    
    resultado = asyncio.run(realizar_auditoria_fichas_execucoes())
    
    print(f"""
    Resumo da Auditoria:
    - Total de divergências encontradas: {resultado['stats']['total_divergencias']}
    - Total de fichas processadas: {resultado['stats']['total_fichas']}
    - Total de execuções processadas: {resultado['stats']['total_execucoes']}
    
    Detalhamento por tipo:
    {resultado['stats']['divergencias_por_tipo']}
    
    Verifique o arquivo de log para mais detalhes.
    """)