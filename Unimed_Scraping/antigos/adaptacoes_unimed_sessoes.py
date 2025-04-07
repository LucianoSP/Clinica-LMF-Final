"""
Adaptações para o script Unimed_Scraping/todas_as_fases_windows_final_com_execucoes.py
para utilizar a nova tabela intermediária unimed_sessoes_capturadas.

Este script contém apenas os métodos que precisam ser modificados para implementar
a nova abordagem de tabela intermediária.
"""

# ---- Substitua o método save_unimed_execution original por este: ----

def save_unimed_execution(self, guia_id: str, guide_details: dict):
    """
    Método adaptado para salvar primeiro na tabela intermediária unimed_sessoes_capturadas 
    e depois chamar a função do banco para processar e inserir na tabela execucoes
    """
    try:
        # Cria um código_ficha temporário baseado no número da guia e data de atendimento
        codigo_ficha = f"TEMP_{guide_details['numero_guia']}_{guide_details['data_atendimento'].replace('/', '')}_{guide_details['ordem_execucao']}"
        
        # Prepara os dados para a tabela intermediária
        sessao_data = {
            "numero_guia": guide_details["numero_guia"],
            "data_atendimento_completa": f"{guide_details['data_atendimento']} 00:00", # Formato dd/mm/aaaa hh:mm
            "data_execucao": guide_details["data_execucao"],
            "paciente_nome": guide_details["nome_beneficiario"],
            "paciente_carteirinha": guide_details["carteira"],
            "codigo_ficha": codigo_ficha,
            "profissional_executante": guide_details["nome_profissional"].strip(),
            "conselho_profissional": guide_details["conselho_profissional"].strip(),
            "numero_conselho": guide_details["numero_conselho"].strip(),
            "uf_conselho": guide_details["uf_conselho"].strip(),
            "codigo_cbo": guide_details["codigo_cbo"].strip(),
            "origem": "unimed_scraping",
            "status": "pendente",
            "task_id": self.task_id
        }
        
        # Salva na tabela intermediária
        response = supabase.table("unimed_sessoes_capturadas").insert(sessao_data).execute()
        
        if not response.data:
            print(f"Erro ao salvar na tabela intermediária: sem dados de retorno")
            return False
            
        sessao_id = response.data[0]['id']
        print(f"Sessão salva na tabela intermediária com ID: {sessao_id}")
        
        # Chama a função para processar e inserir na tabela execucoes
        rpc_response = supabase.rpc(
            'inserir_execucao_unimed', 
            {'sessao_id': sessao_id}
        ).execute()
        
        if rpc_response.data:
            # Se deu certo, a função retorna o ID da execução criada
            print(f"Execução processada com sucesso. ID: {rpc_response.data}")
            return True
        else:
            # Se não encontrou a guia no banco ou outra falha
            print(f"Aviso: A função inserir_execucao_unimed não retornou um ID")
            
            # Atualiza o status da sessão para indicar o problema
            supabase.table("unimed_sessoes_capturadas")\
                .update({"status": "erro", "error": "Guia não encontrada no banco de dados"})\
                .eq("id", sessao_id)\
                .execute()
                
            return False

    except Exception as e:
        print(f"Erro ao salvar execução da Unimed: {str(e)}")
        return False


# ---- Adicione este novo método para verificar o status do processamento: ----

def verificar_processamento_sessoes(self):
    """
    Verifica o status do processamento das sessões capturadas e gera um relatório
    """
    try:
        if not self.task_id:
            print("Não há task_id definido. Verificação de processamento ignorada.")
            return
            
        # Consulta todas as sessões desta task
        query = supabase.table('unimed_sessoes_capturadas')\
            .select('status, count(*)')\
            .eq('task_id', self.task_id)\
            .group('status')\
            .execute()
            
        if not query.data:
            print("Nenhuma sessão encontrada para esta task.")
            return
            
        # Formata o resultado
        estatisticas = {item['status']: item['count'] for item in query.data}
        
        total = sum(estatisticas.values())
        processadas = estatisticas.get('processado', 0)
        com_erro = estatisticas.get('erro', 0)
        pendentes = estatisticas.get('pendente', 0)
        
        # Atualiza o status_processing com as estatísticas
        supabase.table('processing_status')\
            .update({
                'processed_guides': processadas,
                'total_execucoes': total,
                'retry_guides': com_erro,
                'last_update': datetime.now().isoformat(),
                'completed_at': datetime.now().isoformat() if pendentes == 0 else None,
                'status': 'completed' if pendentes == 0 and com_erro == 0 else
                         'completed_with_errors' if pendentes == 0 and com_erro > 0 else
                         'processing'
            })\
            .eq('task_id', self.task_id)\
            .execute()
            
        # Exibe relatório no console
        print("\n=== RELATÓRIO DE PROCESSAMENTO ===")
        print(f"Total de sessões: {total}")
        print(f"Processadas com sucesso: {processadas}")
        print(f"Com erro: {com_erro}")
        print(f"Pendentes: {pendentes}")
        print("================================\n")
        
    except Exception as e:
        print(f"Erro ao verificar processamento: {str(e)}")


# ---- Modifique este método para chamar a verificação de processamento no final ----

def save_to_supabase(self, guide_details_list):
    """Salva os detalhes da guia no Supabase e atualiza o status da fila"""
    # Resto do método permanece igual, apenas adicione no final:
    
    # Após processar todas as guias, verificar o status das sessões
    self.verificar_processamento_sessoes()


# ---- Instruções para implementação ----
"""
Para implementar estas adaptações:

1. Substitua o método `save_unimed_execution` original pelo novo método
2. Adicione o método `verificar_processamento_sessoes` à classe UnimedAutomation
3. Modifique o método `save_to_supabase` para chamar a verificação no final

Certifique-se de que as tabelas `unimed_sessoes_capturadas` e `unimed_log_processamento`
já foram criadas no banco de dados antes de executar o script adaptado.

O script adaptado passará a:
1. Salvar as sessões capturadas na tabela intermediária
2. Usar a função do banco para processar e inserir na tabela execucoes
3. Manter registros detalhados de todo o processo
4. Gerar estatísticas do processamento no final
""" 