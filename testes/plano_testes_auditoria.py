"""
Plano de Testes para o Sistema de Auditoria de Divergências
-----------------------------------------------------------

Este arquivo contém o plano de testes para a funcionalidade de auditoria 
de divergências, incluindo testes unitários, de integração e de sistema.

Autor: Equipe ClinicalMF
Data: Fevereiro 2024
"""

import pytest
import os
import sys
import json
from datetime import datetime, timedelta
import asyncio
from unittest.mock import patch, MagicMock

# Ajusta o path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os módulos a serem testados
from backend.services.auditoria import (
    verificar_datas,
    verificar_assinatura_ficha,
    verificar_duplicidade_execucoes,
    verificar_quantidade_execucaos,
    verificar_validade_guia,
    realizar_auditoria_fichas_execucoes
)

from backend.repositories.auditoria_repository import (
    registrar_divergencia,
    registrar_divergencia_detalhada,
    atualizar_status_divergencia,
    buscar_divergencias_view,
    calcular_estatisticas_divergencias,
    obter_ultima_auditoria
)

#######################################################
# Testes Unitários
#######################################################

class TestVerificacaoDatas:
    """Testes para a verificação de datas."""
    
    def test_datas_iguais(self):
        """Teste com datas iguais (deve passar)."""
        protocolo = {"dataExec": "01/01/2024"}
        execucao = {"data_execucao": "01/01/2024"}
        assert verificar_datas(protocolo, execucao) is True
    
    def test_datas_diferentes(self):
        """Teste com datas diferentes (deve falhar)."""
        protocolo = {"dataExec": "01/01/2024"}
        execucao = {"data_execucao": "02/01/2024"}
        assert verificar_datas(protocolo, execucao) is False
    
    def test_datas_invalidas(self):
        """Teste com datas inválidas."""
        protocolo = {"dataExec": "data_invalida"}
        execucao = {"data_execucao": "01/01/2024"}
        assert verificar_datas(protocolo, execucao) is False
    
    def test_datas_nulas(self):
        """Teste com datas nulas."""
        protocolo = {"dataExec": None}
        execucao = {"data_execucao": "01/01/2024"}
        assert verificar_datas(protocolo, execucao) is False
        
        protocolo = {"dataExec": "01/01/2024"}
        execucao = {"data_execucao": None}
        assert verificar_datas(protocolo, execucao) is False


class TestVerificacaoAssinatura:
    """Testes para a verificação de assinatura."""
    
    def test_ficha_assinada(self):
        """Teste com ficha assinada (deve passar)."""
        ficha = {"arquivo_url": "http://exemplo.com/ficha.pdf", "assinado": True}
        assert verificar_assinatura_ficha(ficha) is True
    
    def test_ficha_nao_assinada(self):
        """Teste com ficha não assinada (deve falhar)."""
        ficha = {"arquivo_url": "http://exemplo.com/ficha.pdf", "assinado": False}
        assert verificar_assinatura_ficha(ficha) is False
    
    def test_ficha_sem_arquivo(self):
        """Teste com ficha sem arquivo (deve falhar)."""
        ficha = {"assinado": True}
        assert verificar_assinatura_ficha(ficha) is False
    
    def test_ficha_sem_info_assinatura(self):
        """Teste com ficha sem informação de assinatura."""
        ficha = {"arquivo_url": "http://exemplo.com/ficha.pdf"}
        assert verificar_assinatura_ficha(ficha) is False


class TestVerificacaoDuplicidade:
    """Testes para a verificação de duplicidade."""
    
    def test_sem_duplicidade(self):
        """Teste com execuções sem duplicidade."""
        execucoes = [
            {"codigo_ficha": "F001", "sessao_id": "S001", "data_execucao": "01/01/2024"},
            {"codigo_ficha": "F002", "sessao_id": "S002", "data_execucao": "01/01/2024"}
        ]
        assert len(verificar_duplicidade_execucoes(execucoes)) == 0
    
    def test_com_duplicidade(self):
        """Teste com execuções duplicadas."""
        execucoes = [
            {"codigo_ficha": "F001", "sessao_id": "S001", "data_execucao": "01/01/2024"},
            {"codigo_ficha": "F001", "sessao_id": "S001", "data_execucao": "01/01/2024"},
            {"codigo_ficha": "F002", "sessao_id": "S002", "data_execucao": "01/01/2024"}
        ]
        duplicatas = verificar_duplicidade_execucoes(execucoes)
        assert len(duplicatas) == 1
        assert len(duplicatas[0]) == 2
    
    def test_varias_duplicidades(self):
        """Teste com várias execuções duplicadas."""
        execucoes = [
            {"codigo_ficha": "F001", "sessao_id": "S001", "data_execucao": "01/01/2024"},
            {"codigo_ficha": "F001", "sessao_id": "S001", "data_execucao": "01/01/2024"},
            {"codigo_ficha": "F002", "sessao_id": "S002", "data_execucao": "01/01/2024"},
            {"codigo_ficha": "F002", "sessao_id": "S002", "data_execucao": "01/01/2024"}
        ]
        duplicatas = verificar_duplicidade_execucoes(execucoes)
        assert len(duplicatas) == 2
        assert len(duplicatas[0]) == 2
        assert len(duplicatas[1]) == 2


class TestVerificacaoQuantidade:
    """Testes para a verificação de quantidade."""
    
    def test_quantidade_correta(self):
        """Teste com quantidade correta."""
        protocolo = {"quantidade": 2}
        execucaos = [{}, {}]
        assert verificar_quantidade_execucaos(protocolo, execucaos) is True
    
    def test_quantidade_menor(self):
        """Teste com quantidade menor que o esperado."""
        protocolo = {"quantidade": 2}
        execucaos = [{}]
        assert verificar_quantidade_execucaos(protocolo, execucaos) is False
    
    def test_quantidade_maior(self):
        """Teste com quantidade maior que o esperado."""
        protocolo = {"quantidade": 2}
        execucaos = [{}, {}, {}]
        assert verificar_quantidade_execucaos(protocolo, execucaos) is False
    
    def test_quantidade_nula(self):
        """Teste com quantidade nula."""
        protocolo = {}
        execucaos = [{}]
        assert verificar_quantidade_execucaos(protocolo, execucaos) is True  # Quantidade padrão é 1


class TestVerificacaoValidadeGuia:
    """Testes para a verificação de validade de guia."""
    
    def test_guia_valida(self):
        """Teste com guia válida."""
        # Data de validade no futuro
        data_futura = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        guia = {"data_validade": data_futura}
        assert verificar_validade_guia(guia) is True
    
    def test_guia_vencida(self):
        """Teste com guia vencida."""
        # Data de validade no passado
        data_passada = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        guia = {"data_validade": data_passada}
        assert verificar_validade_guia(guia) is False
    
    def test_guia_sem_data_validade(self):
        """Teste com guia sem data de validade."""
        guia = {}
        assert verificar_validade_guia(guia) is True  # Guias sem data de validade são consideradas válidas


#######################################################
# Testes de Integração
#######################################################

@pytest.mark.integration
class TestRegistroDivergencias:
    """Testes para o registro de divergências."""
    
    @patch('auditoria_repository.supabase')
    def test_registrar_divergencia(self, mock_supabase):
        """Teste de registro de divergência básica."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.data = [{"id": "123"}]
        mock_supabase.table().insert().execute.return_value = mock_response
        
        # Executa a função
        resultado = registrar_divergencia(
            numero_guia="G123",
            tipo_divergencia="execucao_sem_ficha",
            descricao="Teste de registro",
            paciente_nome="PACIENTE TESTE"
        )
        
        # Verifica o resultado
        assert resultado is True
        mock_supabase.table.assert_called_with("divergencias")
        mock_supabase.table().insert.assert_called_once()
    
    @patch('auditoria_repository.supabase')
    def test_registrar_divergencia_detalhada(self, mock_supabase):
        """Teste de registro de divergência detalhada."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.data = [{"id": "123"}]
        mock_supabase.table().insert().execute.return_value = mock_response
        
        # Executa a função
        resultado = registrar_divergencia_detalhada({
            "numero_guia": "G123",
            "tipo_divergencia": "execucao_sem_ficha",
            "descricao": "Teste de registro detalhado",
            "paciente_nome": "PACIENTE TESTE",
            "data_execucao": "2024-01-01",
            "prioridade": "ALTA"
        })
        
        # Verifica o resultado
        assert resultado is True
        mock_supabase.table.assert_called_with("divergencias")


@pytest.mark.integration
class TestAtualizacaoStatus:
    """Testes para a atualização de status de divergências."""
    
    @patch('auditoria_repository.supabase')
    def test_atualizar_status_pendente_para_analise(self, mock_supabase):
        """Teste de atualização de status de pendente para em_analise."""
        # Configura o mock para buscar a divergência
        divergencia_mock = MagicMock()
        divergencia_mock.data = [{"id": "123", "ficha_id": "F123"}]
        mock_supabase.table().select().eq().execute.return_value = divergencia_mock
        
        # Configura o mock para atualizar o status
        update_mock = MagicMock()
        update_mock.data = [{"id": "123", "status": "em_analise"}]
        mock_supabase.table().update().eq().execute.return_value = update_mock
        
        # Executa a função
        resultado = atualizar_status_divergencia(
            id="123",
            novo_status="em_analise",
            usuario_id="U001"
        )
        
        # Verifica o resultado
        assert resultado is True
        mock_supabase.table.assert_called_with("divergencias")
    
    @patch('auditoria_repository.supabase')
    def test_atualizar_status_para_resolvida(self, mock_supabase):
        """Teste de atualização de status para resolvida."""
        # Configura o mock para buscar a divergência
        divergencia_mock = MagicMock()
        divergencia_mock.data = [{"id": "123", "ficha_id": "F123"}]
        mock_supabase.table().select().eq().execute.return_value = divergencia_mock
        
        # Configura o mock para atualizar o status da divergência
        update_div_mock = MagicMock()
        update_div_mock.data = [{"id": "123", "status": "resolvida"}]
        
        # Configura o mock para atualizar o status da ficha
        update_ficha_mock = MagicMock()
        update_ficha_mock.data = [{"id": "F123", "status": "conferida"}]
        
        # Configura o comportamento dos mocks
        mock_supabase.table().update().eq().execute.side_effect = [
            update_div_mock,
            update_ficha_mock
        ]
        
        # Executa a função
        resultado = atualizar_status_divergencia(
            id="123",
            novo_status="resolvida",
            usuario_id="U001"
        )
        
        # Verifica o resultado
        assert resultado is True
        # Verifica se a tabela divergencias foi atualizada
        mock_supabase.table.assert_any_call("divergencias")
        # Verifica se a tabela fichas_presenca foi atualizada
        mock_supabase.table.assert_any_call("fichas_presenca")


@pytest.mark.integration
class TestListagemFiltros:
    """Testes para a listagem e filtros de divergências."""
    
    @patch('auditoria_repository.supabase')
    def test_buscar_divergencias_sem_filtros(self, mock_supabase):
        """Teste de busca de divergências sem filtros."""
        # Configura o mock para a contagem
        count_mock = MagicMock()
        count_mock.count = 10
        count_mock.data = []
        
        # Configura o mock para a busca
        select_mock = MagicMock()
        select_mock.data = [
            {"id": "1", "tipo_divergencia": "execucao_sem_ficha", "status": "pendente"},
            {"id": "2", "tipo_divergencia": "ficha_sem_execucao", "status": "pendente"}
        ]
        
        # Configura o comportamento dos mocks
        mock_supabase.table().select().count.return_value = "exact"
        mock_supabase.table().select().execute.return_value = count_mock
        mock_supabase.table().select().order().range().execute.return_value = select_mock
        
        # Executa a função
        resultado = buscar_divergencias_view(page=1, per_page=10)
        
        # Verifica o resultado
        assert "divergencias" in resultado
        assert len(resultado["divergencias"]) == 2
        assert resultado["total"] == 10
        assert resultado["pagina_atual"] == 1
        
    @patch('auditoria_repository.supabase')
    def test_buscar_divergencias_com_filtros(self, mock_supabase):
        """Teste de busca de divergências com filtros."""
        # Configura o mock para a contagem
        count_mock = MagicMock()
        count_mock.count = 5
        count_mock.data = []
        
        # Configura o mock para a busca
        select_mock = MagicMock()
        select_mock.data = [
            {"id": "1", "tipo_divergencia": "execucao_sem_ficha", "status": "pendente"}
        ]
        
        # Configura o comportamento dos mocks
        mock_supabase.table().select().eq().count.return_value = "exact"
        mock_supabase.table().select().eq().execute.return_value = count_mock
        mock_supabase.table().select().eq().order().range().execute.return_value = select_mock
        
        # Executa a função
        resultado = buscar_divergencias_view(
            page=1,
            per_page=10,
            status="pendente",
            tipo_divergencia="execucao_sem_ficha"
        )
        
        # Verifica o resultado
        assert "divergencias" in resultado
        assert len(resultado["divergencias"]) == 1
        assert resultado["total"] == 5
        assert resultado["pagina_atual"] == 1


@pytest.mark.integration
class TestEstatisticas:
    """Testes para o cálculo de estatísticas."""
    
    @patch('auditoria_repository.supabase')
    def test_calcular_estatisticas(self, mock_supabase):
        """Teste de cálculo de estatísticas."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "1", "tipo_divergencia": "execucao_sem_ficha", "status": "pendente", "prioridade": "ALTA"},
            {"id": "2", "tipo_divergencia": "ficha_sem_execucao", "status": "pendente", "prioridade": "ALTA"},
            {"id": "3", "tipo_divergencia": "data_divergente", "status": "resolvida", "prioridade": "MEDIA"}
        ]
        mock_supabase.table().select().execute.return_value = mock_response
        
        # Executa a função
        resultado = calcular_estatisticas_divergencias()
        
        # Verifica o resultado
        assert resultado["total"] == 3
        assert resultado["por_tipo"]["execucao_sem_ficha"] == 1
        assert resultado["por_tipo"]["ficha_sem_execucao"] == 1
        assert resultado["por_tipo"]["data_divergente"] == 1
        assert resultado["por_status"]["pendente"] == 2
        assert resultado["por_status"]["resolvida"] == 1
        assert resultado["por_prioridade"]["ALTA"] == 2
        assert resultado["por_prioridade"]["MEDIA"] == 1


#######################################################
# Testes de Sistema
#######################################################

@pytest.mark.system
class TestExecutarAuditoria:
    """Testes para a execução completa da auditoria."""
    
    @patch('auditoria.supabase')
    @patch('auditoria.limpar_divergencias_db')
    @patch('auditoria.registrar_divergencia_detalhada')
    @patch('auditoria.registrar_execucao_auditoria')
    def test_executar_auditoria_completa(self, mock_registrar_execucao, mock_registrar_divergencia, mock_limpar, mock_supabase):
        """Teste de execução completa da auditoria."""
        # Configura os mocks para as tabelas
        sessoes_mock = MagicMock()
        sessoes_mock.data = [
            {
                "id": "S001",
                "ficha_presenca_id": "F001",
                "data_sessao": "2024-01-01",
                "executado": True,
                "possui_assinatura": True,
                "fichas_presenca": {
                    "id": "F001",
                    "codigo_ficha": "FICHA001",
                    "numero_guia": "G001",
                    "paciente_nome": "PACIENTE TESTE",
                    "data_atendimento": "2024-01-01"
                }
            }
        ]
        
        execucoes_mock = MagicMock()
        execucoes_mock.data = [
            {
                "id": "E001",
                "codigo_ficha": "FICHA001",
                "numero_guia": "G001",
                "sessao_id": "S001",
                "data_execucao": "2024-01-01",
                "paciente_nome": "PACIENTE TESTE",
                "guias": {
                    "id": "G001",
                    "numero_guia": "G001",
                    "quantidade_autorizada": 10
                }
            }
        ]
        
        guias_mock = MagicMock()
        guias_mock.data = [
            {
                "id": "G001",
                "numero_guia": "G001",
                "quantidade_autorizada": 10,
                "data_validade": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "carteirinhas": {}
            }
        ]
        
        divergencias_count_mock = MagicMock()
        divergencias_count_mock.data = []
        
        # Configura o comportamento dos mocks
        mock_supabase.table().select().execute.side_effect = [
            sessoes_mock,
            execucoes_mock,
            guias_mock,
            divergencias_count_mock
        ]
        
        mock_limpar.return_value = True
        mock_registrar_divergencia.return_value = True
        mock_registrar_execucao.return_value = True
        
        # Executa a função
        resultado = realizar_auditoria_fichas_execucoes()
        
        # Verifica o resultado
        assert resultado["success"] is True
        assert "stats" in resultado
        mock_limpar.assert_called_once()
        mock_registrar_execucao.assert_called_once()
    
    @patch('auditoria.supabase')
    @patch('auditoria.limpar_divergencias_db')
    @patch('auditoria.registrar_divergencia_detalhada')
    def test_detectar_divergencias(self, mock_registrar_divergencia, mock_limpar, mock_supabase):
        """Teste de detecção de divergências específicas."""
        # Configura os mocks para criar cenários de divergências
        
        # 1. Data divergente
        sessoes_data_div = {
            "id": "S001",
            "ficha_presenca_id": "F001",
            "data_sessao": "2024-01-01",
            "executado": True,
            "possui_assinatura": True,
            "fichas_presenca": {
                "id": "F001",
                "codigo_ficha": "FICHA001",
                "numero_guia": "G001",
                "paciente_nome": "PACIENTE TESTE",
                "data_atendimento": "2024-01-01"
            }
        }
        
        execucoes_data_div = {
            "id": "E001",
            "codigo_ficha": "FICHA001",
            "numero_guia": "G001",
            "sessao_id": "S001",
            "data_execucao": "2024-01-02",  # Data diferente da sessão
            "paciente_nome": "PACIENTE TESTE"
        }
        
        # 2. Sessão sem assinatura
        sessoes_sem_assinatura = {
            "id": "S002",
            "ficha_presenca_id": "F002",
            "data_sessao": "2024-01-01",
            "executado": True,
            "possui_assinatura": False,  # Sem assinatura
            "fichas_presenca": {
                "id": "F002",
                "codigo_ficha": "FICHA002",
                "numero_guia": "G002",
                "paciente_nome": "PACIENTE TESTE 2",
                "data_atendimento": "2024-01-01"
            }
        }
        
        # 3. Execução sem ficha
        execucoes_sem_ficha = {
            "id": "E003",
            "codigo_ficha": "FICHA003",  # Não tem ficha correspondente
            "numero_guia": "G003",
            "sessao_id": "S003",
            "data_execucao": "2024-01-01",
            "paciente_nome": "PACIENTE SEM FICHA"
        }
        
        # Configura os mocks para as tabelas
        sessoes_mock = MagicMock()
        sessoes_mock.data = [sessoes_data_div, sessoes_sem_assinatura]
        
        execucoes_mock = MagicMock()
        execucoes_mock.data = [execucoes_data_div, execucoes_sem_ficha]
        
        guias_mock = MagicMock()
        guias_mock.data = [
            {
                "id": "G001",
                "numero_guia": "G001",
                "quantidade_autorizada": 10,
                "data_validade": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            }
        ]
        
        divergencias_count_mock = MagicMock()
        divergencias_count_mock.data = []
        
        # Configura o comportamento dos mocks
        mock_supabase.table().select().execute.side_effect = [
            sessoes_mock,
            execucoes_mock,
            guias_mock,
            divergencias_count_mock
        ]
        
        mock_limpar.return_value = True
        mock_registrar_divergencia.return_value = True
        
        # Executa a função
        realizar_auditoria_fichas_execucoes()
        
        # Verifica se registrou as divergências esperadas
        # Deve ter registrado ao menos 3 divergências:
        # 1. Data divergente
        # 2. Sessão sem assinatura
        # 3. Execução sem ficha
        assert mock_registrar_divergencia.call_count >= 3
        
        # Verifica os tipos específicos de chamadas
        tipos_divergencia = []
        for call in mock_registrar_divergencia.call_args_list:
            args, kwargs = call
            tipos_divergencia.append(args[0].get("tipo_divergencia"))
        
        assert "data_divergente" in tipos_divergencia
        assert "sessao_sem_assinatura" in tipos_divergencia
        assert "execucao_sem_ficha" in tipos_divergencia


if __name__ == "__main__":
    # Para executar os testes unitários:
    # pytest testes/plano_testes_auditoria.py -v
    
    # Para executar os testes de integração:
    # pytest testes/plano_testes_auditoria.py -v -m integration
    
    # Para executar os testes de sistema:
    # pytest testes/plano_testes_auditoria.py -v -m system
    
    # Para executar todos os testes:
    # pytest testes/plano_testes_auditoria.py -v
    pass 