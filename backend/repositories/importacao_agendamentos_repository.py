from typing import Optional, Dict, Any, List
import uuid
from fastapi import HTTPException
from datetime import datetime
from ..config.config import supabase

class ImportacaoAgendamentosRepository:
    def __init__(self):
        self.table = 'controle_importacao_agendamentos'
        self.agendamentos_table = 'agendamentos'
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
                
            result = self.client.table(self.table).insert(dados_importacao).execute()
            
            if not result.data or len(result.data) == 0:
                raise HTTPException(status_code=500, detail="Falha ao registrar importação")
                
            return result.data[0]
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao registrar importação: {str(e)}")

    async def importar_agendamentos_mysql(self, agendamentos_dados: List[Dict[str, Any]], 
                                       usuario_id: str,
                                       ultima_data_registro: Optional[datetime] = None,
                                       ultima_data_atualizacao: Optional[datetime] = None) -> Dict[str, Any]:
        """Importa agendamentos do MySQL para o Supabase com controle de datas."""
        total = len(agendamentos_dados)
        importados = 0
        atualizados = 0
        erros = []
        
        # Rastrear datas máximas nesta importação
        data_registro_max = None
        data_atualizacao_max = None

        try:
            for agendamento_dados in agendamentos_dados:
                try:
                    # Verificar se o agendamento já existe por id_origem
                    result = self.client.table(self.agendamentos_table).select('*').eq('id_origem', agendamento_dados['id_origem']).execute()
                    
                    # Extrair as datas do registro original (se disponíveis)
                    data_registro_origem = None
                    data_atualizacao_origem = None
                    
                    if 'data_registro_origem' in agendamento_dados and agendamento_dados['data_registro_origem']:
                        data_registro_origem = agendamento_dados['data_registro_origem']
                        # Atualizar a data máxima de registro vista nesta importação
                        if data_registro_max is None or data_registro_origem > data_registro_max:
                            data_registro_max = data_registro_origem
                    
                    if 'data_atualizacao_origem' in agendamento_dados and agendamento_dados['data_atualizacao_origem']:
                        data_atualizacao_origem = agendamento_dados['data_atualizacao_origem']
                        # Atualizar a data máxima de atualização vista nesta importação
                        if data_atualizacao_max is None or data_atualizacao_origem > data_atualizacao_max:
                            data_atualizacao_max = data_atualizacao_origem
                    
                    # Pular este registro se ambas as datas forem mais antigas ou iguais às últimas importadas
                    if ultima_data_registro and ultima_data_atualizacao:
                        if (data_registro_origem and data_registro_origem <= ultima_data_registro and
                            data_atualizacao_origem and data_atualizacao_origem <= ultima_data_atualizacao):
                            continue
                    
                    # Adicionar campos de rastreamento
                    agendamento_dados['importado'] = True
                    agendamento_dados['created_by'] = usuario_id
                    agendamento_dados['updated_by'] = usuario_id
                    
                    # Adicionar timestamps
                    current_time = datetime.now().isoformat()
                    
                    if result.data and len(result.data) > 0:
                        # Agendamento já existe, atualizar
                        agendamento_id = result.data[0]['id']
                        agendamento_dados['updated_at'] = current_time
                        
                        update_result = self.client.table(self.agendamentos_table).update(agendamento_dados).eq('id', agendamento_id).execute()
                        if update_result.data and len(update_result.data) > 0:
                            atualizados += 1
                    else:
                        # Agendamento não existe, criar novo
                        agendamento_dados['created_at'] = current_time
                        agendamento_dados['updated_at'] = current_time
                        
                        # Garantir que temos um UUID como ID
                        if "id" not in agendamento_dados:
                            agendamento_dados["id"] = str(uuid.uuid4())
                        
                        insert_result = self.client.table(self.agendamentos_table).insert(agendamento_dados).execute()
                        if insert_result.data and len(insert_result.data) > 0:
                            importados += 1
                
                except Exception as e:
                    erros.append({
                        "agendamento": agendamento_dados.get('id_origem', 'Desconhecido'),
                        "erro": str(e)
                    })
            
            # Registrar a importação no controle
            await self.registrar_importacao({
                "ultima_data_registro_importada": data_registro_max,
                "ultima_data_atualizacao_importada": data_atualizacao_max,
                "quantidade_registros_importados": importados,
                "quantidade_registros_atualizados": atualizados,
                "usuario_id": usuario_id,
                "observacoes": f"Importação: {importados} importados, {atualizados} atualizados, {len(erros)} erros"
            })
            
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
            raise HTTPException(status_code=500, detail=f"Erro ao importar agendamentos: {str(e)}") 