from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import pymysql
import sshtunnel
import json
from datetime import datetime
import os
from ..utils.date_utils import format_date_fields, DATE_FIELDS, format_date, DateEncoder
from ..repositories.importacao_repository import ImportacaoRepository

class ImportacaoService:
    def __init__(self):
        self.repository = ImportacaoRepository()

    # Definição de campos de data adicionais específicos para pacientes
    PACIENTES_DATE_FIELDS = [
        'data_nascimento',
        'client_registration_date',
        'client_update_date'
    ]
    
    async def obter_ultima_importacao(self):
        """Obtém os dados da última importação registrada."""
        return await self.repository.obter_ultima_importacao()
    
    async def _estabelecer_conexao_mysql(self, database: str) -> pymysql.Connection:
        """Estabelece conexão com o banco MySQL via SSH tunnel."""
        try:
            # Configurações de SSH do ambiente
            ssh_host = os.getenv("SSH_HOST")
            ssh_port = int(os.getenv("SSH_PORT", "22"))
            ssh_user = os.getenv("SSH_USER")
            ssh_password = os.getenv("SSH_PASSWORD")
            
            # Configurações do MySQL
            mysql_host = os.getenv("MYSQL_HOST", "127.0.0.1")
            mysql_port = int(os.getenv("MYSQL_PORT", "3306"))
            mysql_user = os.getenv("MYSQL_USER")
            mysql_password = os.getenv("MYSQL_PASSWORD")
            
            # Criar tunnel SSH
            tunnel = sshtunnel.SSHTunnelForwarder(
                (ssh_host, ssh_port),
                ssh_username=ssh_user,
                ssh_password=ssh_password,
                remote_bind_address=(mysql_host, mysql_port)
            )
            
            tunnel.start()
            
            # Conectar ao MySQL através do túnel
            connection = pymysql.connect(
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                user=mysql_user,
                password=mysql_password,
                database=database,
                cursorclass=pymysql.cursors.DictCursor
            )
            
            return {
                "connection": connection,
                "tunnel": tunnel,
                "success": True,
                "message": "Conexão estabelecida com sucesso!"
            }
            
        except Exception as e:
            if 'tunnel' in locals() and tunnel:
                tunnel.close()
                
            return {
                "connection": None,
                "tunnel": None,
                "success": False,
                "message": f"Erro ao estabelecer conexão: {str(e)}"
            }
    
    async def _mapear_dados_paciente(self, paciente_mysql: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia os dados do MySQL para o formato do Supabase."""
        # Pré-formatação das datas
        data_nascimento = None
        if paciente_mysql.get("client_data_nascimento"):
            try:
                data_nascimento = format_date(paciente_mysql.get("client_data_nascimento"))
            except:
                data_nascimento = None

        client_registration_date = None
        if paciente_mysql.get("client_registration_date"):
            try:
                client_registration_date = format_date(paciente_mysql.get("client_registration_date"))
            except:
                client_registration_date = None

        client_update_date = None
        if paciente_mysql.get("client_update_date"):
            try:
                client_update_date = format_date(paciente_mysql.get("client_update_date"))
            except:
                client_update_date = None
                
        paciente_supabase = {
            # Mapeamento de campos básicos
            "nome": paciente_mysql.get("client_nome", ""),
            "id_origem": str(paciente_mysql.get("client_id", "")),
            "cpf": paciente_mysql.get("client_cpf", ""),
            "rg": paciente_mysql.get("client_rg", ""),
            "data_nascimento": data_nascimento,
            "foto": paciente_mysql.get("client_thumb", ""),
            "nome_responsavel": paciente_mysql.get("client_nome_responsavel", ""),
            "nome_pai": paciente_mysql.get("client_nome_pai", ""),
            "nome_mae": paciente_mysql.get("client_nome_mae", ""),
            "sexo": paciente_mysql.get("client_sexo", "")[0:1] if paciente_mysql.get("client_sexo") else "",
            "cep": paciente_mysql.get("client_cep", ""),
            "endereco": paciente_mysql.get("client_endereco", ""),
            "numero": int(paciente_mysql.get("client_numero", 0)) if paciente_mysql.get("client_numero") and paciente_mysql.get("client_numero").isdigit() else None,
            "complemento": paciente_mysql.get("client_complemento", ""),
            "bairro": paciente_mysql.get("client_bairro", ""),
            "cidade": paciente_mysql.get("client_cidade_nome", ""),
            "estado": paciente_mysql.get("client_state", "")[0:2].upper() if paciente_mysql.get("client_state") else "",
            "telefone": paciente_mysql.get("client_telefone", ""),
            "email": paciente_mysql.get("client_email", ""),
            
            # Dados extras - preservar datas originais para rastreabilidade
            "client_registration_date": client_registration_date,
            "client_update_date": client_update_date,
            
            # ID original
            "id_origem": str(paciente_mysql.get("client_id", ""))
        }
        
        # Garantir que não há problemas de serialização
        try:
            # Testar serialização
            json.dumps(paciente_supabase)
            return paciente_supabase
        except TypeError:
            # Se houver problemas, aplicar serialização com DateEncoder
            paciente_json = json.dumps(paciente_supabase, cls=DateEncoder)
            return json.loads(paciente_json)
    
    async def importar_pacientes(
        self, 
        database: str,
        tabela: str,
        usuario_id: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Importa pacientes do MySQL para o Supabase, verificando datas de atualização/registro.
        
        Args:
            database: Nome do banco de dados MySQL
            tabela: Nome da tabela de pacientes no MySQL
            usuario_id: ID do usuário que está realizando a importação
            limit: Limite opcional de registros a importar
            
        Returns:
            Resultado da importação com estatísticas
        """
        # Verificar última importação para saber quais datas já foram importadas
        ultima_importacao = await self.repository.obter_ultima_importacao()
        ultima_data_registro = ultima_importacao.get("ultima_data_registro_importada") if ultima_importacao else None
        ultima_data_atualizacao = ultima_importacao.get("ultima_data_atualizacao_importada") if ultima_importacao else None
        
        # Estabelecer conexão com o MySQL
        conexao_result = await self._estabelecer_conexao_mysql(database)
        
        if not conexao_result["success"]:
            return {
                "success": False,
                "message": conexao_result["message"],
                "connection_status": conexao_result
            }
        
        connection = conexao_result["connection"]
        tunnel = conexao_result["tunnel"]
        
        try:
            with connection.cursor() as cursor:
                # Construir query para buscar registros NOVOS ou ATUALIZADOS
                query = f"SELECT * FROM {tabela} WHERE 1=1"
                
                # Filtrar com base na última data de importação, se disponível
                if ultima_data_registro and ultima_data_atualizacao:
                    query += " AND (client_registration_date > %s OR client_update_date > %s)"
                    params = [ultima_data_registro, ultima_data_atualizacao]
                else:
                    params = []
                
                # Aplicar limite, se especificado
                if limit is not None:
                    query += f" LIMIT {int(limit)}"
                
                # Executar a query
                cursor.execute(query, params if ultima_data_registro and ultima_data_atualizacao else None)
                
                # Obter todos os registros
                pacientes_mysql = cursor.fetchall()
                
                # Mapear registros para o formato Supabase
                pacientes_dados = []
                for paciente_mysql in pacientes_mysql:
                    paciente_dados = await self._mapear_dados_paciente(paciente_mysql)
                    pacientes_dados.append(paciente_dados)
                
                # Importar pacientes mapeados
                resultado_importacao = await self.repository.importar_pacientes_mysql(
                    pacientes_dados, 
                    usuario_id,
                    ultima_data_registro,
                    ultima_data_atualizacao
                )
                
                # Adicionar informações de conexão ao resultado
                resultado_importacao["connection_status"] = {
                    "success": True,
                    "message": "Conexão estabelecida com sucesso!"
                }
                
                return resultado_importacao
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro durante a importação: {str(e)}",
                "connection_status": conexao_result
            }
        finally:
            # Fechar conexão MySQL e túnel SSH
            if 'connection' in locals() and connection:
                connection.close()
            if 'tunnel' in locals() and tunnel:
                tunnel.close() 