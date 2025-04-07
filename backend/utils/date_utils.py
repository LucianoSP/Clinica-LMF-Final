from datetime import date, datetime, time
import re
import logging
import json
from typing import Any, Dict, Union, Optional, TypeVar, List, cast
from dateutil import parser
from uuid import UUID

logger = logging.getLogger(__name__)

# Definindo um tipo genérico para retorno de funções
T = TypeVar('T')

def formatar_data(data: Union[str, datetime, date]) -> str:
    """
    Formata uma data para o padrão DD/MM/YYYY, tentando interpretar vários formatos possíveis.
    Como a data pode vir de várias fontes (IA, usuário, etc), tentamos ser flexíveis na interpretação.
    
    Args:
        data: Pode ser string em vários formatos, datetime ou date
        
    Returns:
        str: Data formatada no padrão DD/MM/YYYY
        
    Raises:
        ValueError: Se não for possível interpretar a data
    """
    try:
        if isinstance(data, str):
            # Remove espaços extras
            data = data.strip()

            # Lista de possíveis formatos, do mais específico para o mais genérico
            formatos = [
                "%d/%m/%Y",  # 31/12/2024
                "%Y-%m-%d",  # 2024-12-31
                "%d-%m-%Y",  # 31-12-2024
                "%Y/%m/%d",  # 2024/12/31
                "%d.%m.%Y",  # 31.12.2024
                "%Y.%m.%d",  # 2024.12.31
                "%d %m %Y",  # 31 12 2024
                "%Y %m %d",  # 2024 12 31
            ]

            # Se a data tem 8 dígitos seguidos, pode ser DDMMYYYY ou YYYYMMDD
            if data.isdigit() and len(data) == 8:
                # Tenta interpretar como DDMMYYYY
                try:
                    data_obj = datetime.strptime(data, "%d%m%Y")
                    if data_obj.year >= 2000 and data_obj.year <= 2100:
                        return data_obj.strftime("%d/%m/%Y")
                except ValueError:
                    pass

                # Tenta interpretar como YYYYMMDD
                try:
                    data_obj = datetime.strptime(data, "%Y%m%d")
                    if data_obj.year >= 2000 and data_obj.year <= 2100:
                        return data_obj.strftime("%d/%m/%Y")
                except ValueError:
                    pass

            # Tenta todos os formatos conhecidos
            for formato in formatos:
                try:
                    data_obj = datetime.strptime(data, formato)
                    # Verifica se o ano está em um intervalo razoável
                    if data_obj.year >= 2000 and data_obj.year <= 2100:
                        return data_obj.strftime("%d/%m/%Y")
                except ValueError:
                    continue

            # Se chegou aqui, tenta trocar dia/mês se a data parece inválida
            partes = re.split(r"[/\-\. ]", data)
            if len(partes) == 3:
                # Se parece ser DD/MM/YYYY mas é inválida, tenta MM/DD/YYYY
                try:
                    data_obj = datetime.strptime(
                        f"{partes[1]}/{partes[0]}/{partes[2]}", "%d/%m/%Y")
                    if data_obj.year >= 2000 and data_obj.year <= 2100:
                        return data_obj.strftime("%d/%m/%Y")
                except ValueError:
                    pass

            raise ValueError(f"Não foi possível interpretar a data: {data}")

        elif isinstance(data, (datetime, date)):
            return data.strftime("%d/%m/%Y")
        else:
            raise ValueError(f"Tipo de data inválido: {type(data)}")

    except Exception as e:
        logger.error(f"Erro ao formatar data: {e}")
        raise ValueError(str(e))

def format_date(value: Union[date, datetime, T]) -> Union[str, T]:
    """Converte date ou datetime para string ISO se necessário"""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return cast(T, value)

def format_date_fields(data: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """
    Formata campos de data em um dicionário para string ISO.
    
    Args:
        data: Dicionário contendo os dados
        fields: Lista de campos que podem conter datas
        
    Returns:
        Dict: Dicionário com datas formatadas como strings ISO
    """
    result = dict(data)
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = format_date(result[field])
    
    # Tenta serializar para verificar se não há outros objetos datetime
    try:
        json.dumps(result)
    except TypeError:
        # Se houver erro, faz uma serialização completa
        result = json.loads(json.dumps(result, cls=DateEncoder))
        
    return result

# Lista de campos que são datas em toda a aplicação
# SEMPRE ATUALIZE ESTA LISTA ao adicionar novos campos de data!
DATE_FIELDS = [
    'data_nascimento',
    'avaliacao_luria_data_inicio_treinamento',
    'created_at',
    'updated_at',
    'deleted_at',
    'data_validade',  # Adicionado para carteirinhas
    'data_inicio',
    'data_fim',
    'data_atendimento',  # Adicionado para fichas de presença
    'data_registro_origem',  # Adicionado para rastreamento de importação
    'data_atualizacao_origem',  # Adicionado para rastreamento de importação
    'client_registration_date',  # Adicionado para importação de pacientes
    'client_update_date',  # Adicionado para importação de pacientes
    'data_sessao',  # Adicionado para sessões
    'data_execucao',  # Adicionado para execuções
    'data_identificacao',  # Adicionado para divergências
    'data_inicial',  # Adicionado para períodos
    'data_final',  # Adicionado para períodos
    'timestamp_importacao',  # Adicionado para controle de importação
    'schedule_registration_date',  # Adicionado para tabela pschedule
    'schedule_lastupdate',  # Adicionado para tabela pschedule
    'data_agendamento', # Adicionado para tabela agendamentos (apesar de ser timestamp)
    'schedule_date_start', # Adicionado para manter valor original
    'schedule_date_end',   # Adicionado para manter valor original
    # Campos de hora são tratados separadamente, não precisam estar aqui
    # 'hora_inicio',
    # 'hora_fim'
]

def format_datetime(dt: Union[datetime, str, None]) -> Optional[str]:
    """Converte datetime para string ISO format"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()

def format_time(time_value: Union[datetime, time, str, None]) -> Optional[str]:
    """
    Formata um valor de tempo para o formato HH:MM:SS.
    Aceita datetime, time ou string.
    
    Args:
        time_value: O valor de tempo a ser formatado
        
    Returns:
        str: Hora formatada ou None se não for possível formatar
    """
    if time_value is None:
        return None
        
    try:
        if isinstance(time_value, str):
            # Verificar se é uma string ISO completa ou apenas uma hora
            if 'T' in time_value:
                # Extrair parte da hora de um datetime ISO
                time_part = time_value.split('T')[1]
                # Remover timezone offset (+HH:MM ou Z) e milissegundos
                time_part = time_part.split('+')[0].split('Z')[0].split('.')[0]
                return time_part
            elif ' ' in time_value and len(time_value.split(' ')) == 2:
                # Extrair hora de um formato 'YYYY-MM-DD HH:MM:SS'
                return time_value.split(' ')[1].split('.')[0] # Remover milissegundos se houver
            elif ':' in time_value:
                 # Tenta parsear como hora HH:MM ou HH:MM:SS[.ms]
                try:
                    parsed_time = parser.parse(time_value).time()
                    return parsed_time.strftime('%H:%M:%S')
                except ValueError:
                     # Se falhar, pode ser uma string inválida, continua para o fallback
                    pass

        # Correção: Usar 'datetime' e 'time' diretamente
        elif isinstance(time_value, datetime):
            return time_value.strftime('%H:%M:%S')
        elif isinstance(time_value, time):
            return time_value.strftime('%H:%M:%S')
        
        # Tentativa de converter para datetime (fallback) e depois extrair a hora
        dt = parse_datetime(time_value)
        if dt:
            return dt.strftime('%H:%M:%S')
            
        logger.warning(f"Não foi possível formatar o valor de hora: {time_value} (Tipo: {type(time_value)})")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao formatar hora para '{time_value}': {e}")
        return None
        
def parse_datetime(value: Any) -> Optional[datetime]:
    """
    Tenta converter um valor para datetime.
    
    Args:
        value: Valor a ser convertido
        
    Returns:
        datetime: Objeto datetime ou None se falhar
    """
    if value is None:
        return None
        
    if isinstance(value, datetime):
        return value
        
    if isinstance(value, date):
        return datetime.combine(value, time())
        
    if isinstance(value, str):
        try:
            return parser.parse(value)
        except Exception as e:
            logger.debug(f"Falha ao usar dateutil.parser para '{value}': {e}")
            pass
            
    return None

class DateEncoder(json.JSONEncoder):
    """
    Encoder JSON personalizado para lidar com objetos date e datetime.
    Esta classe deve ser usada sempre que houver serialização de dados que podem conter datas.
    
    Exemplo de uso:
        json.dumps(data, cls=DateEncoder)
    """
    def default(self, obj: Any) -> Any:
        """Converte objetos date e datetime para string ISO"""
        from decimal import Decimal
        
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        # Adiciona tratamento para valores Decimal
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def ensure_serializable(data: Any) -> Any:
    """
    Garante que um objeto seja serializável para JSON, tratando especialmente objetos de data.
    Esta função deve ser usada antes de enviar dados para o Supabase ou outra API.
    
    Args:
        data: Qualquer tipo de dado (dict, list, date, etc)
        
    Returns:
        Any: Dados garantidamente serializáveis
    """
    if data is None:
        return None
        
    try:
        # Tenta serializar
        json.dumps(data)
        return data
    except TypeError:
        # Se falhar, aplica o DateEncoder
        return json.loads(json.dumps(data, cls=DateEncoder))

# --- Encoder adicionado daqui --- 
class DateUUIDEncoder(json.JSONEncoder):
    """Serializa objetos date, datetime e UUID para formatos JSON compatíveis."""
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)
# --- Fim da adição ---