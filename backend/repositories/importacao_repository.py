from typing import Optional, Dict, Any, List, Tuple
import uuid
from fastapi import HTTPException
from datetime import datetime
import logging
import json
from ..config.config import supabase
from ..utils.date_utils import DateEncoder, ensure_serializable

logger = logging.getLogger(__name__)

class ImportacaoRepository:
    def __init__(self):
        self.table = 'controle_importacao_pacientes'
        self.pacientes_table = 'pacientes'
        self.client = supabase

    async def obter_ultima_importacao(self) -> Optional[Dict[str, Any]]:
        """Obtém os dados da última importação feita."""
        try:
            result = self.client.table(self.table).select('*').order('timestamp_importacao', desc=True).limit(1).execute()
            
            if not result.data or len(result.data) == 0:
                return None
                
            return result.data[0]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao obter última importação: {str(e)}")

    async def registrar_importacao(self, dados_importacao: Dict[str, Any]) -> Dict[str, Any]:
        """Registra uma nova importação."""
        try:
            # Garantir que temos um UUID como ID
            if "id" not in dados_importacao:
                dados_importacao["id"] = str(uuid.uuid4())
            
            # Garantir que não há objetos datetime sem serializar
            dados_importacao = ensure_serializable(dados_importacao)
                
            result = self.client.table(self.table).insert(dados_importacao).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Falha ao registrar importação")
                
            return result.data[0]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao registrar importação: {str(e)}")

    async def importar_pacientes_mysql(self, pacientes_dados: List[Dict[str, Any]], 
                                     usuario_id: str,
                                     ultima_data_registro: Optional[datetime] = None,
                                     ultima_data_atualizacao: Optional[datetime] = None) -> Dict[str, Any]:
        """Importa pacientes do MySQL para o Supabase com controle de datas."""
        total = len(pacientes_dados)
        importados = 0
        atualizados = 0
        erros = []
        
        # Rastrear datas máximas nesta importação
        data_registro_max = None
        data_atualizacao_max = None

        try:
            for paciente_dados in pacientes_dados:
                try:
                    # Garantir que o paciente_dados não tem objetos datetime diretos
                    paciente_dados = ensure_serializable(paciente_dados)
                    
                    # Verificar se o paciente já existe por id_origem
                    id_origem = paciente_dados.get('id_origem') or paciente_dados.get('client_id', '')
                    result = self.client.table(self.pacientes_table).select('*').eq('id_origem', id_origem).execute()
                    
                    # Extrair as datas do registro original (se disponíveis)
                    data_registro_origem = None
                    data_atualizacao_origem = None
                    
                    if 'client_registration_date' in paciente_dados and paciente_dados['client_registration_date']:
                        data_registro_origem = paciente_dados['client_registration_date']
                        # Atualizar a data máxima de registro vista nesta importação
                        if data_registro_max is None or data_registro_origem > data_registro_max:
                            data_registro_max = data_registro_origem
                    
                    if 'client_update_date' in paciente_dados and paciente_dados['client_update_date']:
                        data_atualizacao_origem = paciente_dados['client_update_date']
                        # Atualizar a data máxima de atualização vista nesta importação
                        if data_atualizacao_max is None or data_atualizacao_origem > data_atualizacao_max:
                            data_atualizacao_max = data_atualizacao_origem
                    
                    # Pular este registro se ambas as datas forem mais antigas ou iguais às últimas importadas
                    if ultima_data_registro and ultima_data_atualizacao:
                        if (data_registro_origem and data_registro_origem <= ultima_data_registro and
                            data_atualizacao_origem and data_atualizacao_origem <= ultima_data_atualizacao):
                            continue
                    
                    # Adicionar campos de rastreamento
                    paciente_dados['importado'] = True
                    paciente_dados['id_origem'] = int(paciente_dados.get('id_origem', paciente_dados.get('client_id', 0)))
                    paciente_dados['data_registro_origem'] = data_registro_origem
                    paciente_dados['data_atualizacao_origem'] = data_atualizacao_origem
                    paciente_dados['created_by'] = usuario_id
                    paciente_dados['updated_by'] = usuario_id
                    
                    # Adicionar timestamps
                    current_time = datetime.now().isoformat()
                    
                    if result.data and len(result.data) > 0:
                        # Paciente já existe, atualizar
                        paciente_id = result.data[0]['id']
                        paciente_dados['updated_at'] = current_time
                        
                        # Verificar serialização final
                        paciente_dados = ensure_serializable(paciente_dados)
                            
                        update_result = self.client.table(self.pacientes_table).update(paciente_dados).eq('id', paciente_id).execute()
                        if update_result.data and len(update_result.data) > 0:
                            atualizados += 1
                    else:
                        # Paciente não existe, criar novo
                        paciente_dados['created_at'] = current_time
                        paciente_dados['updated_at'] = current_time
                        
                        # Garantir que temos um UUID como ID
                        if "id" not in paciente_dados:
                            paciente_dados["id"] = str(uuid.uuid4())
                        
                        # Verificar serialização final
                        paciente_dados = ensure_serializable(paciente_dados)
                            
                        insert_result = self.client.table(self.pacientes_table).insert(paciente_dados).execute()
                        if insert_result.data and len(insert_result.data) > 0:
                            importados += 1
                
                except Exception as e:
                    logger.error(f"Erro ao importar paciente: {str(e)}")
                    erros.append({
                        "paciente": paciente_dados.get('nome', 'Desconhecido'),
                        "erro": str(e)
                    })
            
            # Formatar datas para ISO
            data_registro_max_str = data_registro_max.isoformat() if isinstance(data_registro_max, datetime) else data_registro_max
            data_atualizacao_max_str = data_atualizacao_max.isoformat() if isinstance(data_atualizacao_max, datetime) else data_atualizacao_max
            
            # Registrar a importação no controle
            dados_importacao = {
                "ultima_data_registro_importada": data_registro_max_str,
                "ultima_data_atualizacao_importada": data_atualizacao_max_str,
                "quantidade_registros_importados": importados,
                "quantidade_registros_atualizados": atualizados,
                "usuario_id": usuario_id,
                "observacoes": f"Importação: {importados} importados, {atualizados} atualizados, {len(erros)} erros"
            }
            
            await self.registrar_importacao(dados_importacao)
            
            return {
                "success": True,
                "total": total,
                "importados": importados,
                "atualizados": atualizados,
                "erros": erros,
                "ultima_data_registro": data_registro_max,
                "ultima_data_atualizacao": data_atualizacao_max
            }
            
        except Exception as e:
            logger.error(f"Erro ao importar pacientes: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro ao importar pacientes: {str(e)}") 