from typing import Dict, List
from datetime import datetime
import pandas as pd
from io import BytesIO
from ..repositories.execucao import ExecucaoRepository

class ExecucaoExportService:
    def __init__(self, repository: ExecucaoRepository):
        self.repository = repository

    async def export_to_excel(self, execucoes: List[Dict]) -> BytesIO:
        """
        Exporta uma lista de execuções para Excel
        """
        # Prepara os dados para o Excel
        data = []
        for execucao in execucoes:
            data.append({
                'Data de Execução': execucao.get('data_execucao'),
                'Data de Atendimento': execucao.get('data_atendimento'),
                'Paciente': execucao.get('paciente_nome'),
                'Carteirinha': execucao.get('paciente_carteirinha'),
                'Número da Guia': execucao.get('numero_guia'),
                'Código da Ficha': execucao.get('codigo_ficha'),
                'Status Biometria': execucao.get('status_biometria'),
                'Origem': execucao.get('origem'),
                'Profissional': execucao.get('profissional_executante'),
                'Conselho': execucao.get('conselho_profissional'),
                'Nº Conselho': execucao.get('numero_conselho'),
                'UF Conselho': execucao.get('uf_conselho'),
                'Código CBO': execucao.get('codigo_cbo'),
                'Data de Criação': execucao.get('created_at')
            })

        # Cria o DataFrame
        df = pd.DataFrame(data)

        # Formata as datas
        date_columns = ['Data de Execução', 'Data de Atendimento', 'Data de Criação']
        for col in date_columns:
            df[col] = pd.to_datetime(df[col]).dt.strftime('%d/%m/%Y %H:%M')

        # Formata o status da biometria
        status_map = {
            'nao_verificado': 'Não Verificado',
            'verificado': 'Verificado',
            'falha': 'Falha'
        }
        df['Status Biometria'] = df['Status Biometria'].map(status_map)

        # Cria o arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Execuções', index=False)
            
            # Formata a planilha
            worksheet = writer.sheets['Execuções']
            workbook = writer.book
            
            # Define formatos
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'bg_color': '#D9EAD3',
                'border': 1
            })
            
            cell_format = workbook.add_format({
                'text_wrap': True,
                'border': 1
            })

            # Aplica os formatos
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15, cell_format)

        output.seek(0)
        return output