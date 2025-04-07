import os
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao PYTHONPATH
# Isso permite que o script encontre o módulo 'backend' quando executado diretamente
script_dir = Path(__file__).resolve().parent  # diretório do script atual
project_root = script_dir.parent.parent  # diretório raiz do projeto (dois níveis acima)
sys.path.insert(0, str(project_root))

from supabase import create_client, Client
import random
from datetime import datetime, timedelta
from faker import Faker
import logging
import traceback
from postgrest.exceptions import APIError
import uuid
from dotenv import load_dotenv

# Imports da nova estrutura
from backend.config.config import supabase
from backend.repositories.database_supabase import get_supabase_client

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar Faker para português
fake = Faker('pt_BR')

class DatabasePopulator:
    def __init__(self, supabase, admin_id, preserve_users=True, generate_divergences=True):
        self.supabase = supabase
        self.admin_id = admin_id
        self.preserve_users = preserve_users
        self.generate_divergences = generate_divergences
        
        # Armazenar dados para referência
        self.pacientes = []
        self.carteirinhas = []
        self.planos_saude = []
        self.procedimentos = []
        self.especialidades = []
        self.guias = []
        self.fichas = []
        self.sessoes = []
        self.agendamentos = []
        
        # Verificar permissões antes de começar
        self.verificar_permissoes()
    
    def verificar_permissoes(self):
        """Verifica se o usuário autenticado tem as permissões necessárias para manipular os dados."""
        try:
            logger.info("Verificando permissões do usuário...")
            
            # Tentar fazer uma operação que requer permissões de escrita (INSERT/DELETE) em uma tabela pequena
            # Criando uma entrada temporária na tabela especialidades
            temp_id = str(uuid.uuid4())
            test_entry = {
                "id": temp_id,
                "nome": "TESTE_PERMISSAO_TEMPORARIO",
                "status": "ativo",
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            
            # Inserir entrada de teste
            try:
                self.supabase.table('especialidades').insert(test_entry).execute()
                logger.info("✓ Permissão de INSERT verificada com sucesso")
            except Exception as e:
                logger.error(f"✗ Erro ao inserir registro de teste: {str(e)}")
                logger.error("O usuário não tem permissões de INSERT. Verifique as permissões no Supabase.")
                logger.error("Execute os scripts de configuração de segurança (sql/02_desabilitar_seguranca.sql e sql/04_configurar_admin.sql)")
                raise Exception("Permissões insuficientes para prosseguir com a geração de dados de teste")
            
            # Excluir entrada de teste
            try:
                self.supabase.table('especialidades').delete().eq('id', temp_id).execute()
                logger.info("✓ Permissão de DELETE verificada com sucesso")
            except Exception as e:
                logger.error(f"✗ Erro ao excluir registro de teste: {str(e)}")
                logger.error("O usuário não tem permissões de DELETE. Verifique as permissões no Supabase.")
                raise Exception("Permissões insuficientes para prosseguir com a geração de dados de teste")
            
            logger.info("✓ Verificação de permissões concluída com sucesso")
        except Exception as e:
            logger.error("Erro durante a verificação de permissões")
            logger.error(str(e))
            raise

    def populate_especialidades(self):
        try:
            # Verificar admin
            admin = self.supabase.table('usuarios').select('*').eq('id', self.admin_id).execute()
            if not admin.data:
                raise Exception(f"Usuário admin com ID {self.admin_id} não encontrado")
            
            # Verificar existentes
            especialidades_existentes = self.supabase.table('especialidades').select('*').execute()
            if especialidades_existentes.data:
                logger.info(f"Encontradas {len(especialidades_existentes.data)} especialidades existentes")
                self.especialidades = especialidades_existentes.data
                return
            
            # Criar especialidades base
            especialidades_base = [
                {
                    "nome": "Fisioterapia",
                    "status": "ativo",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Clínica Geral",
                    "status": "ativo",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Ortopedia",
                    "status": "ativo",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Neurologia",
                    "status": "ativo",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Pediatria",
                    "status": "ativo",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Cardiologia",
                    "status": "ativo",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
            ]
            
            logger.info("Inserindo especialidades base...")
            result = self.supabase.table('especialidades').insert(especialidades_base).execute()
            self.especialidades = result.data
            logger.info(f"Criadas {len(self.especialidades)} especialidades")

            # Criar relações usuário-especialidade
            for esp in self.especialidades:
                rel_existente = self.supabase.table('usuarios_especialidades')\
                    .select('*')\
                    .eq('usuario_id', self.admin_id)\
                    .eq('especialidade_id', esp['id'])\
                    .execute()
                
                if not rel_existente.data:
                    relacao = {
                        "usuario_id": self.admin_id,
                        "especialidade_id": esp['id'],
                        "principal": esp['nome'] == "Fisioterapia",  # Principal apenas para Fisioterapia
                        "created_by": self.admin_id,
                        "updated_by": self.admin_id
                    }
                    
                    self.supabase.table('usuarios_especialidades').insert(relacao).execute()
                    logger.info(f"Criada relação para especialidade {esp['nome']}")

        except Exception as e:
            logger.error("Erro ao manipular especialidades")
            logger.error(str(e))
            raise

    def populate_procedimentos(self):
        try:
            # Verificar existentes
            procedimentos_existentes = self.supabase.table('procedimentos').select('*').execute()
            if procedimentos_existentes.data:
                logger.info(f"Encontrados {len(procedimentos_existentes.data)} procedimentos existentes")
                self.procedimentos = procedimentos_existentes.data
                return
            
            # Criar procedimentos base
            procedimentos_base = [
                {
                    "codigo": "CONS001",
                    "nome": "Consulta Médica",
                    "tipo": "consulta",
                    "descricao": "Consulta médica padrão",
                    "valor": 150.00,
                    "valor_total": 200.00,
                    "requer_autorizacao": True,
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo": "FISIO001",
                    "nome": "Sessão de Fisioterapia",
                    "tipo": "procedimento",
                    "descricao": "Sessão de fisioterapia convencional",
                    "valor": 80.00,
                    "valor_total": 100.00,
                    "requer_autorizacao": True,
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo": "ORTO001",
                    "nome": "Consulta Ortopédica",
                    "tipo": "consulta",
                    "descricao": "Consulta com ortopedista",
                    "valor": 200.00,
                    "valor_total": 250.00,
                    "requer_autorizacao": True,
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo": "NEURO001",
                    "nome": "Avaliação Neurológica",
                    "tipo": "consulta",
                    "descricao": "Avaliação neurológica completa",
                    "valor": 250.00,
                    "valor_total": 300.00,
                    "requer_autorizacao": True,
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo": "PED001",
                    "nome": "Consulta Pediátrica",
                    "tipo": "consulta",
                    "descricao": "Consulta pediátrica de rotina",
                    "valor": 180.00,
                    "valor_total": 220.00,
                    "requer_autorizacao": True,
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
            ]
            
            logger.info("Inserindo procedimentos base...")
            result = self.supabase.table('procedimentos').insert(procedimentos_base).execute()
            self.procedimentos = result.data
            logger.info(f"Criados {len(self.procedimentos)} procedimentos")
            
        except Exception as e:
            logger.error("Erro ao criar procedimentos")
            logger.error(str(e))
            raise

    def populate_planos_saude(self):
        try:
            # Verificar existentes
            planos_existentes = self.supabase.table('planos_saude').select('*').execute()
            if planos_existentes.data:
                logger.info(f"Encontrados {len(planos_existentes.data)} planos existentes")
                self.planos_saude = planos_existentes.data
                return
            
            # Criar planos base
            planos_base = [
                {
                    "codigo_operadora": "123456",
                    "registro_ans": "ANS001",
                    "nome": "Unimed Nacional",
                    "tipo_plano": "Individual",
                    "abrangencia": "Nacional",
                    "observacoes": "Plano completo com cobertura nacional",
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo_operadora": "789012",
                    "registro_ans": "ANS002",
                    "nome": "Bradesco Saúde",
                    "tipo_plano": "Empresarial",
                    "abrangencia": "Nacional",
                    "observacoes": "Plano empresarial premium",
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo_operadora": "345678",
                    "registro_ans": "ANS003",
                    "nome": "SulAmérica",
                    "tipo_plano": "Familiar",
                    "abrangencia": "Regional",
                    "observacoes": "Plano familiar básico",
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "codigo_operadora": "901234",
                    "registro_ans": "ANS004",
                    "nome": "Amil",
                    "tipo_plano": "Individual",
                    "abrangencia": "Nacional",
                    "observacoes": "Plano individual com cobertura odontológica",
                    "ativo": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
            ]
            
            logger.info("Inserindo planos de saúde base...")
            result = self.supabase.table('planos_saude').insert(planos_base).execute()
            self.planos_saude = result.data
            logger.info(f"Criados {len(self.planos_saude)} planos de saúde")
            
        except Exception as e:
            logger.error("Erro ao criar planos de saúde")
            logger.error(str(e))
            raise

    def populate_pacientes(self):
        try:
            # Verificar existentes
            pacientes_existentes = self.supabase.table('pacientes').select('*').execute()
            if pacientes_existentes.data:
                logger.info(f"Encontrados {len(pacientes_existentes.data)} pacientes existentes")
                self.pacientes = pacientes_existentes.data
                return
            
            # Verificar se a coluna codigo_aba existe
            coluna_codigo_aba_existe = True
            try:
                # Tentativa de consulta para verificar se a coluna existe
                self.supabase.table('pacientes').select('codigo_aba').limit(1).execute()
                logger.info("Coluna codigo_aba existe na tabela pacientes")
            except Exception as e:
                coluna_codigo_aba_existe = False
                logger.error("A coluna codigo_aba não existe na tabela pacientes!")
                logger.error("Esta coluna é necessária para o funcionamento correto do sistema.")
                logger.error("Execute o seguinte comando SQL para adicionar a coluna:")
                logger.error("ALTER TABLE pacientes ADD COLUMN codigo_aba character varying(20) UNIQUE;")
                logger.debug(f"Detalhes do erro: {str(e)}")
                raise Exception("Coluna codigo_aba não encontrada na tabela pacientes. Adicione a coluna e tente novamente.")
            
            # Criar pacientes base
            pacientes_base = [
                {
                    "nome": "Maria Silva",
                    "codigo_aba": "P00001",
                    "cpf": "123.456.789-00",
                    "data_nascimento": "1980-05-15",
                    "sexo": "F",
                    "telefone": "(11) 98765-4321",
                    "email": "maria.silva@email.com",
                    "cep": "01234-567",
                    "endereco": "Rua das Flores",
                    "numero": 123,
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "João Santos",
                    "codigo_aba": "P00002",
                    "cpf": "987.654.321-00",
                    "data_nascimento": "1975-08-20",
                    "sexo": "M",
                    "telefone": "(11) 91234-5678",
                    "email": "joao.santos@email.com",
                    "cep": "04567-890",
                    "endereco": "Av. Principal",
                    "numero": 456,
                    "bairro": "Jardins",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Ana Oliveira",
                    "codigo_aba": "P00003",
                    "cpf": "456.789.123-00",
                    "data_nascimento": "1990-03-10",
                    "sexo": "F",
                    "telefone": "(11) 97890-1234",
                    "email": "ana.oliveira@email.com",
                    "cep": "02345-678",
                    "endereco": "Rua do Parque",
                    "numero": 789,
                    "bairro": "Vila Nova",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Pedro Costa Junior",
                    "codigo_aba": "P00004",
                    "cpf": "234.567.890-00",
                    "data_nascimento": "1995-12-25",
                    "sexo": "M",
                    "telefone": "(11) 94567-8901",
                    "email": "pedro.costa@email.com",
                    "cep": "03456-789",
                    "endereco": "Rua das Palmeiras",
                    "numero": 1010,
                    "bairro": "Moema",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "nome_mae": "Maria Costa",
                    "nome_pai": "Pedro Costa",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "nome": "Carlos Ferreira",
                    "codigo_aba": "P00005",
                    "cpf": "345.678.901-00",
                    "data_nascimento": "1988-07-22",
                    "sexo": "M",
                    "telefone": "(11) 95678-9012",
                    "email": "carlos.ferreira@email.com",
                    "cep": "05678-901",
                    "endereco": "Rua dos Pinheiros",
                    "numero": 567,
                    "bairro": "Pinheiros",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
            ]
            
            logger.info("Inserindo pacientes base...")
            result = self.supabase.table('pacientes').insert(pacientes_base).execute()
            self.pacientes = result.data
            logger.info(f"Criados {len(self.pacientes)} pacientes base")
            
        except Exception as e:
            logger.error("Erro ao criar pacientes")
            logger.error(str(e))
            raise

    def populate_carteirinhas(self):
        try:
            # Verificar existentes
            carteirinhas_existentes = self.supabase.table('carteirinhas').select('*').execute()
            if carteirinhas_existentes.data:
                logger.info(f"Encontradas {len(carteirinhas_existentes.data)} carteirinhas existentes")
                self.carteirinhas = carteirinhas_existentes.data
                return
            
            # Verificar se temos pacientes e planos
            if not self.pacientes or not self.planos_saude:
                logger.error("Necessário ter pacientes e planos cadastrados primeiro")
                return
            
            # Verificar quantos pacientes temos disponíveis
            num_pacientes = len(self.pacientes)
            logger.info(f"Número de pacientes disponíveis: {num_pacientes}")
            
            # Criar carteirinhas base
            carteirinhas_base = [
                {
                    "paciente_id": self.pacientes[0]['id'],  # Maria Silva
                    "plano_saude_id": self.planos_saude[0]['id'],  # Unimed
                    "numero_carteirinha": "123456789",
                    "data_validade": "2025-12-31",
                    "status": "ativa",
                    "titular": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "paciente_id": self.pacientes[1]['id'],  # João Santos
                    "plano_saude_id": self.planos_saude[1]['id'],  # Bradesco
                    "numero_carteirinha": "987654321",
                    "data_validade": "2024-12-31",
                    "status": "ativa",
                    "titular": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "paciente_id": self.pacientes[2]['id'],  # Ana Oliveira
                    "plano_saude_id": self.planos_saude[2]['id'],  # SulAmérica
                    "numero_carteirinha": "456789123",
                    "data_validade": "2025-06-30",
                    "status": "ativa",
                    "titular": False,
                    "nome_titular": "Carlos Oliveira",
                    "cpf_titular": "111.222.333-44",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "paciente_id": self.pacientes[3]['id'],  # Pedro Costa Junior
                    "plano_saude_id": self.planos_saude[3]['id'],  # Amil
                    "numero_carteirinha": "234567890",
                    "data_validade": "2025-10-15",
                    "status": "ativa",
                    "titular": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                },
                {
                    "paciente_id": self.pacientes[4]['id'],  # Carlos Ferreira
                    "plano_saude_id": self.planos_saude[0]['id'],  # Unimed
                    "numero_carteirinha": "345678901",
                    "data_validade": "2023-12-31",  # Vencido intencionalmente para testar guia_vencida
                    "status": "ativa",
                    "titular": True,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
            ]
            
            logger.info("Inserindo carteirinhas base...")
            result = self.supabase.table('carteirinhas').insert(carteirinhas_base).execute()
            self.carteirinhas = result.data
            logger.info(f"Criadas {len(self.carteirinhas)} carteirinhas")
            
        except Exception as e:
            logger.error("Erro ao criar carteirinhas")
            logger.error(str(e))
            raise

    def populate_guias(self):
        try:
            # Verificar admin
            admin = self.supabase.table('usuarios').select('*').eq('id', self.admin_id).execute()
            if not admin.data:
                raise Exception(f"Usuário admin com ID {self.admin_id} não encontrado")
            
            # Verificar existentes
            guias_existentes = self.supabase.table('guias').select('*').execute()
            if guias_existentes.data:
                logger.info(f"Encontradas {len(guias_existentes.data)} guias existentes")
                self.guias = guias_existentes.data
                return
            
            # Verificar se temos carteirinhas e procedimentos
            if not self.carteirinhas or not self.procedimentos:
                logger.error("Dados insuficientes para criar guias")
                logger.error(f"Carteirinhas: {len(self.carteirinhas) if self.carteirinhas else 0}")
                logger.error(f"Procedimentos: {len(self.procedimentos) if self.procedimentos else 0}")
                return

            # Verificar quantas carteirinhas temos disponíveis
            num_carteirinhas = len(self.carteirinhas)
            logger.info(f"Número de carteirinhas disponíveis: {num_carteirinhas}")
            
            # Mapear procedimentos por código
            proc_map = {p['codigo']: p for p in self.procedimentos}
            
            # Data atual para uso em cálculos de datas
            data_atual = datetime.now()
            
            # Lista para armazenar todas as guias
            guias_para_inserir = []
            
            # Guias para Maria Silva (Fisioterapia)
            guia1 = {
                "carteirinha_id": self.carteirinhas[0]['id'],
                "paciente_id": self.carteirinhas[0]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024001",
                "data_solicitacao": data_atual.strftime("%Y-%m-%d"),
                "data_autorizacao": data_atual.strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 10,
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 10,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH001"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia1)
            
            # Guia para João Santos (Fisioterapia) - Para quantidade_excedida
            guia2 = {
                "carteirinha_id": self.carteirinhas[1]['id'],
                "paciente_id": self.carteirinhas[1]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024002",
                "data_solicitacao": data_atual.strftime("%Y-%m-%d"),
                "data_autorizacao": data_atual.strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 5,  # Autoriza apenas 5 para depois exceder
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 5,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH002"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia2)
            
            # Guia para Ana Oliveira (Fisioterapia) - Para ficha_sem_execucao e data_divergente
            guia3 = {
                "carteirinha_id": self.carteirinhas[2]['id'],
                "paciente_id": self.carteirinhas[2]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024003",
                "data_solicitacao": data_atual.strftime("%Y-%m-%d"),
                "data_autorizacao": data_atual.strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 8,
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 8,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH003"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia3)
            
            # Guia para Pedro Costa (Fisioterapia) - Para sessao_sem_assinatura
            guia4 = {
                "carteirinha_id": self.carteirinhas[3]['id'],
                "paciente_id": self.carteirinhas[3]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024004",
                "data_solicitacao": data_atual.strftime("%Y-%m-%d"),
                "data_autorizacao": data_atual.strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 7,
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 7,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH004"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia4)
            
            # Guia para Carlos Ferreira (Fisioterapia) - Com data vencida para guia_vencida
            guia5 = {
                "carteirinha_id": self.carteirinhas[4]['id'],
                "paciente_id": self.carteirinhas[4]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024005",
                "data_solicitacao": (data_atual - timedelta(days=120)).strftime("%Y-%m-%d"),
                "data_autorizacao": (data_atual - timedelta(days=120)).strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 6,
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 6,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH005"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia5)
            
            # Guia adicional para Carlos Ferreira (Fisioterapia) - Para execucao_sem_ficha e duplicidade
            guia6 = {
                "carteirinha_id": self.carteirinhas[4]['id'],  # Reutilizando Carlos Ferreira
                "paciente_id": self.carteirinhas[4]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024006",
                "data_solicitacao": data_atual.strftime("%Y-%m-%d"),
                "data_autorizacao": data_atual.strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 9,
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 9,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH006"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia6)
            
            # Guia adicional para Maria Silva (Fisioterapia) - Para falta_data_execucao
            guia7 = {
                "carteirinha_id": self.carteirinhas[0]['id'],  # Reutilizando Maria Silva
                "paciente_id": self.carteirinhas[0]['paciente_id'],
                "procedimento_id": proc_map['FISIO001']['id'],
                "numero_guia": "G2024007",
                "data_solicitacao": data_atual.strftime("%Y-%m-%d"),
                "data_autorizacao": data_atual.strftime("%Y-%m-%d"),
                "status": "autorizada",
                "tipo": "procedimento",
                "quantidade_autorizada": 4,
                "quantidade_executada": 0,
                "codigo_servico": "FISIO001",
                "descricao_servico": "Sessão de Fisioterapia",
                "quantidade": 4,
                "dados_autorizacao": {"autorizador": "Dr. Sistema", "codigo_autorizacao": "AUTH007"},
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            }
            guias_para_inserir.append(guia7)
            
            # Inserir todas as guias
            logger.info(f"Inserindo {len(guias_para_inserir)} guias...")
            
            # Verificar se há números de guias duplicados
            numeros_guias = [g['numero_guia'] for g in guias_para_inserir]
            duplicados = [num for num in set(numeros_guias) if numeros_guias.count(num) > 1]
            
            if duplicados:
                logger.error(f"Foram encontrados números de guias duplicados: {duplicados}")
                logger.error("Corrigindo números duplicados antes de inserir...")
                
                # Correção de duplicidades
                contador = 10000
                for i, guia in enumerate(guias_para_inserir):
                    if guia['numero_guia'] in duplicados:
                        # Se é duplicado, gerar um novo número
                        novo_numero = f"G{datetime.now().year}{contador}"
                        logger.info(f"Alterando guia duplicada: {guia['numero_guia']} -> {novo_numero}")
                        guia['numero_guia'] = novo_numero
                        contador += 1
            
            result = self.supabase.table('guias').insert(guias_para_inserir).execute()
            self.guias = result.data
            logger.info(f"Criadas {len(self.guias)} guias")
        
        except Exception as e:
            logger.error("Erro ao criar guias")
            logger.error(str(e))
            raise

    def populate_agendamentos(self):
        """Cria agendamentos de exemplo com base nos pacientes existentes, expandido para testes de auditoria"""
        try:
            # Verificar agendamentos existentes
            agendamentos_existentes = self.supabase.table('agendamentos').select('*').execute()
            if agendamentos_existentes.data:
                logger.info(f"Encontrados {len(agendamentos_existentes.data)} agendamentos existentes")
                self.agendamentos = agendamentos_existentes.data
                return
            
            # Verificar se temos pacientes
            if not self.pacientes:
                logger.error("Não há pacientes para criar agendamentos")
                return
            
            # Obter códigos ABA válidos dos pacientes
            codigos_aba_validos = [p['codigo_aba'] for p in self.pacientes if 'codigo_aba' in p and p['codigo_aba']]
            
            if not codigos_aba_validos:
                logger.error("Nenhum paciente tem código ABA válido. Não é possível criar agendamentos.")
                return
                
            logger.info(f"Encontrados {len(codigos_aba_validos)} códigos ABA válidos")
            
            # Restante do método permanece o mesmo...
            
            # Carregar pacientes e especialidades se necessário
            if not self.pacientes:
                pacientes = self.supabase.table('pacientes').select('id, nome, codigo_aba').execute().data
                self.pacientes = pacientes
            
            if not self.especialidades:
                especialidades = self.supabase.table('especialidades').select('id, nome').execute().data
                self.especialidades = especialidades
            
            # Verificar dados necessários
            if not self.pacientes or not self.especialidades:
                logger.error("Dados insuficientes para criar agendamentos")
                return
            
            # Encontrar especialidade de fisioterapia
            fisioterapia = next((e for e in self.especialidades if e['nome'] == 'Fisioterapia'), None)
            if not fisioterapia:
                logger.error("Especialidade 'Fisioterapia' não encontrada")
                return
            
            # Data atual para cálculo de datas
            data_atual = datetime.now()
            data_base = data_atual - timedelta(days=14)  # Duas semanas atrás para mais histórico
            
            agendamentos_base = []
            
            # Tipos de pagamento para diversificar
            tipos_pagamento = [
                "Unimed Nacional", 
                "Bradesco Saúde", 
                "SulAmérica", 
                "Amil", 
                "Notredame Intermédica"
            ]
            
            # Unidades disponíveis
            unidades = ["Unidade Oeste", "República do Líbano"]
            
            # Criar agendamentos para cada paciente
            for i, paciente in enumerate(self.pacientes):
                # Aumentar para 5 agendamentos por paciente em diferentes estados
                for j in range(5):
                    # Calcular data/hora - distribui no passado e futuro
                    dias_offset = random.randint(-30, 30)  # Últimos 30 dias até próximos 30 dias
                    data_agendamento = data_base + timedelta(days=dias_offset, hours=random.randint(8, 17))
                    
                    # Status com distribuição mais realista
                    if data_agendamento.date() < data_atual.date():
                        # Agendamentos passados
                        status_weights = [
                            ('realizado', 0.70),  # 70% realizados
                            ('faltou', 0.15),     # 15% faltou
                            ('cancelado', 0.15)   # 15% cancelados
                        ]
                        status = random.choices([s[0] for s in status_weights], 
                                              weights=[s[1] for s in status_weights], 
                                              k=1)[0]
                    else:
                        # Agendamentos futuros
                        status = 'agendado'

                    # Selecionar tipo de pagamento aleatório
                    pagamento = random.choice(tipos_pagamento)
                    
                    # Selecionar unidade aleatória
                    unidade = random.choice(unidades)
                    
                    # Definir código de faturamento
                    # Os códigos de faturamento podem ser importantes para análises
                    codigo_faturamento = f"FAT{i+1:03d}{j+1}"
                    
                    # Criar agendamento
                    agendamento = {
                        "schedule_date_start": data_agendamento.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "schedule_date_end": (data_agendamento + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "schedule_pacient_id": paciente['codigo_aba'],
                        "schedule_pagamento": pagamento,
                        "schedule_profissional_id": self.admin_id,
                        "schedule_profissional": "Dr. Sistema",
                        "schedule_unidade": unidade,
                        "schedule_qtd_sessions": random.randint(1, 5),  # Mais variabilidade
                        "schedule_status": status,
                        "schedule_especialidade_id": fisioterapia['id'],
                        "schedule_saldo_sessoes": 0 if status == 'realizado' else random.randint(1, 5),
                        "schedule_elegibilidade": True,
                        "schedule_codigo_faturamento": codigo_faturamento,
                        "created_by": self.admin_id,
                        "updated_by": self.admin_id
                    }
                    
                    agendamentos_base.append(agendamento)
            
            # Inserir agendamentos
            if agendamentos_base:
                logger.info(f"Inserindo {len(agendamentos_base)} agendamentos...")
                
                # Inserir em lotes para evitar problemas com tamanho de payload
                lote_size = 20
                total_inseridos = 0
                
                for i in range(0, len(agendamentos_base), lote_size):
                    lote = agendamentos_base[i:i+lote_size]
                    try:
                        result = self.supabase.table('agendamentos').insert(lote).execute()
                        total_inseridos += len(result.data)
                        logger.info(f"Lote {i//lote_size + 1}: Inseridos {len(result.data)} agendamentos")
                    except Exception as e:
                        logger.error(f"Erro ao inserir lote {i//lote_size + 1}: {str(e)}")
                
                # Obter todos os agendamentos inseridos
                all_agendamentos = self.supabase.table('agendamentos').select('*').execute()
                self.agendamentos = all_agendamentos.data
                
                logger.info(f"Total: Criados {total_inseridos} agendamentos")
        
        except Exception as e:
            logger.error("Erro ao criar agendamentos")
            logger.error(str(e))
            traceback.print_exc()

    def populate_fichas(self):
        """Cria fichas de exemplo com base nas guias existentes"""
        try:
            # Verificar fichas existentes
            fichas_existentes = self.supabase.table('fichas').select('*').execute()
            
            # Limpar fichas existentes
            if fichas_existentes.data:
                logger.info("Limpando fichas existentes para criar novas...")
                self.supabase.table('fichas').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                logger.info("Fichas antigas removidas com sucesso")
            
            # Obter pacientes
            pacientes = self.supabase.table('pacientes').select('id, nome').execute().data
            if not pacientes:
                logger.error("Não há pacientes para criar fichas")
                return
            
            # Obter carteirinhas para associar
            carteirinhas = self.supabase.table('carteirinhas').select('id, numero_carteirinha, paciente_id').execute().data
            if not carteirinhas:
                logger.error("Não há carteirinhas para associar às fichas")
                return
            
            # Verificar que todos os números de guia existam na tabela guias
            numeros_guia = list(set([g.get('numero_guia') for g in self.guias if g.get('numero_guia')]))
            guias_existentes = self.supabase.table('guias').select('id, numero_guia').in_('numero_guia', numeros_guia).execute()
            guias_validas = {g['numero_guia']: g['id'] for g in guias_existentes.data}
            
            # Filtrar guias válidas
            guias_filtradas = [g for g in self.guias if g.get('numero_guia') in guias_validas]
            
            if len(guias_filtradas) < len(self.guias):
                logger.warning(f"Ignorando {len(self.guias) - len(guias_filtradas)} guias inválidas")
                
            logger.info(f"Processando {len(guias_filtradas)} guias válidas")
            
            # Obter agendamentos para vinculação
            agendamentos = self.supabase.table('agendamentos').select('id, schedule_pacient_id, schedule_status').execute().data
            if not agendamentos:
                logger.info("Não há agendamentos para vincular às fichas, prosseguindo sem vinculação")
            
            logger.info(f"Inserindo {len(guias_filtradas)} fichas...")
            
            # Criar fichas
            fichas_para_inserir = []
            for i, guia in enumerate(guias_filtradas):
                # Encontrar carteirinha correspondente ao paciente da guia
                carteirinha = next((c for c in carteirinhas if c['paciente_id'] == guia['paciente_id']), None)
                if not carteirinha:
                    continue
                
                # Encontrar nome do paciente
                paciente_nome = next((p['nome'] for p in pacientes if p['id'] == guia['paciente_id']), "Nome não encontrado")
                
                # Encontrar um agendamento realizado para este paciente, se existir
                paciente_codigo_aba = next((p.get('codigo_aba') for p in self.pacientes if p['id'] == guia['paciente_id']), None)
                agendamento_id = None
                
                if paciente_codigo_aba:
                    agendamento = next((a for a in agendamentos if a['schedule_pacient_id'] == paciente_codigo_aba and a['schedule_status'] == 'realizado'), None)
                    if agendamento:
                        agendamento_id = agendamento['id']
                
                # Criar ficha
                ficha = {
                    'codigo_ficha': f"F{datetime.now().year}{1000 + i}",
                    'guia_id': guia['id'],
                    'agendamento_id': agendamento_id,  # Vincula ao agendamento, se encontrado
                    'numero_guia': guia['numero_guia'],
                    'data_atendimento': guia['data_solicitacao'],
                    'paciente_nome': paciente_nome,
                    'paciente_carteirinha': carteirinha['numero_carteirinha'],
                    'total_sessoes': random.randint(5, 10),
                    'status': 'pendente',  # Valor válido para o enum status_ficha
                    'storage_id': None,  # Será atualizado posteriormente
                    'arquivo_digitalizado': False,
                    'created_by': self.admin_id,
                    'updated_by': self.admin_id
                }
                
                fichas_para_inserir.append(ficha)
            
            # Inserir fichas no banco
            if fichas_para_inserir:
                resultado = self.supabase.table('fichas').insert(fichas_para_inserir).execute()
                self.fichas = resultado.data  # Guardamos as fichas com seus IDs
                logger.info(f"Criadas {len(self.fichas)} fichas")
            
        except Exception as e:
            logger.error("Erro ao criar fichas")
            logger.error(str(e))
            raise

    def populate_storage(self):
        """Cria registros na tabela storage simulando PDFs armazenados para as fichas"""
        try:
            # Verificar registros existentes
            storage_existentes = self.supabase.table('storage').select('*').execute()
            if storage_existentes.data:
                logger.info(f"Encontrados {len(storage_existentes.data)} registros de storage existentes")
                self.storage = storage_existentes.data
                return
            
            # Verificar se temos fichas
            if not self.fichas:
                logger.error("Necessário ter fichas cadastradas primeiro")
                return
            
            logger.info(f"Criando registros de storage para {len(self.fichas)} fichas...")
            
            # Criar registros para cada ficha
            storage_para_inserir = []
            for i, ficha in enumerate(self.fichas):
                storage = {
                    "nome": f"{ficha['codigo_ficha']}_{ficha['paciente_nome'].replace(' ', '_')}_{ficha['data_atendimento']}.pdf",
                    "url": f"https://r2.cloudflare.com/fichas/{ficha['codigo_ficha']}.pdf",
                    "size": random.randint(100000, 500000),  # Tamanho do arquivo em bytes
                    "content_type": "application/pdf",
                    "tipo_referencia": "ficha",
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
                storage_para_inserir.append(storage)
            
            # Inserir registros no banco
            if storage_para_inserir:
                resultado = self.supabase.table('storage').insert(storage_para_inserir).execute()
                self.storage = resultado.data
                logger.info(f"Criados {len(self.storage)} registros de storage")
                
                # Atualizar fichas com os IDs de storage
                for i, storage_item in enumerate(self.storage):
                    if i < len(self.fichas):
                        self.supabase.table('fichas').update({
                            "storage_id": storage_item['id'],
                            "arquivo_digitalizado": True
                        }).eq('id', self.fichas[i]['id']).execute()
                
                logger.info(f"Atualizadas {min(len(self.storage), len(self.fichas))} fichas com referência de storage")
            
        except Exception as e:
            logger.error("Erro ao criar registros de storage")
            logger.error(str(e))
            raise

    def populate_sessoes(self):
        """Cria sessões para cada ficha existente"""
        try:
            # Verificar sessões existentes
            sessoes_existentes = self.supabase.table('sessoes').select('*').execute()
            if sessoes_existentes.data:
                logger.info("Limpando sessões existentes para criar novas...")
                self.supabase.table('sessoes').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                logger.info("Sessões antigas removidas com sucesso")
            
            # Carregar fichas se necessário
            if not self.fichas:
                fichas = self.supabase.table('fichas').select('*').execute()
                self.fichas = fichas.data
            
            if not self.fichas:
                logger.error("Não há fichas para criar sessões")
                return
            
            logger.info(f"Criando sessões para {len(self.fichas)} fichas")
            
            # Verificar que todas as fichas têm id e codigo_ficha válidos
            fichas_validas = [f for f in self.fichas if f.get('id') and f.get('codigo_ficha')]
            
            if len(fichas_validas) < len(self.fichas):
                logger.warning(f"Ignorando {len(self.fichas) - len(fichas_validas)} fichas sem id ou codigo_ficha")
                
            logger.info(f"Processando {len(fichas_validas)} fichas válidas")

            # Mapear guias para obter suas quantidades autorizadas e procedimento_id
            guias_ids = list(set([f.get('guia_id') for f in fichas_validas if f.get('guia_id')]))
            guias_info = self.supabase.table('guias').select('id, quantidade_autorizada, procedimento_id').in_('id', guias_ids).execute()
            guias_map = {g['id']: g for g in guias_info.data}
            
            # Criar sessões para cada ficha
            todas_sessoes = []
            
            for idx, ficha in enumerate(fichas_validas):
                total_sessoes = ficha.get('total_sessoes', 10)  # Valor padrão de 10 sessões
                guia_id = ficha.get('guia_id')
                guia_info = guias_map.get(guia_id, {})
                
                # Usar data base para criar sessões espaçadas ao longo de um período
                data_base = datetime.now() - timedelta(days=15)
                
                for i in range(total_sessoes):
                    # Incrementar dias progressivamente (1 a cada 2 sessões)
                    data_sessao = (data_base + timedelta(days=i // 2)).strftime('%Y-%m-%d')
                    possui_assinatura = True
                    
                    # Variável para definir se a sessão está executada (apenas para lógica interna)
                    sessao_status = "executada"
                    
                    # Ficha específica para sessao_sem_assinatura
                    if "G2024004" in ficha.get('numero_guia', '') and i % 2 == 0:  # A cada 2 sessões da ficha com guia G2024004
                        possui_assinatura = False
                    
                    # Para ficha_sem_execucao, algumas sessões não serão executadas
                    if "G2024003" in ficha.get('numero_guia', '') and i >= 4:  # A partir da 5ª sessão da ficha com guia G2024003
                        sessao_status = "pendente"
                    
                    sessao = {
                        "ficha_id": ficha['id'],
                        "guia_id": ficha['guia_id'],
                        "data_sessao": data_sessao,
                        "possui_assinatura": possui_assinatura,
                        "procedimento_id": guia_info.get('procedimento_id'),
                        "status": sessao_status,
                        "numero_guia": ficha['numero_guia'],
                        "codigo_ficha": ficha['codigo_ficha'],
                        "origem": "manual",
                        "ordem_execucao": i + 1,
                        "status_biometria": "nao_verificado",
                        "profissional_executante": "Dr. Sistema",
                        "created_by": self.admin_id,
                        "updated_by": self.admin_id
                    }
                    
                    todas_sessoes.append(sessao)
            
            # Inserir sessões em lotes (máximo de 20 por vez)
            tamanho_lote = 20
            total_inseridos = 0
            
            for i in range(0, len(todas_sessoes), tamanho_lote):
                lote_atual = todas_sessoes[i:i+tamanho_lote]
                result = self.supabase.table('sessoes').insert(lote_atual).execute()
                total_inseridos += len(result.data)
            
            logger.info(f"Criadas {total_inseridos} sessões")
            
            # Guardar sessões para referência
            todas_sessoes_dados = self.supabase.table('sessoes').select('*').execute()
            self.sessoes = todas_sessoes_dados.data
            
        except Exception as e:
            logger.error("Erro ao criar sessões")
            logger.error(str(e))
            traceback.print_exc()

    def populate_execucoes(self):
        """Cria execuções de exemplo com base nas divergências documentadas"""
        try:
            # Verificar execuções existentes
            execucoes_existentes = self.supabase.table('execucoes').select('*').execute()
            if execucoes_existentes.data:
                logger.info("Limpando execuções existentes para criar novas...")
                self.supabase.table('execucoes').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                logger.info("Execuções antigas removidas com sucesso")
            
            # Carregar sessões se necessário
            todas_sessoes = self.supabase.table('sessoes').select('*').execute()
            sessoes_data = todas_sessoes.data if todas_sessoes else []
            
            if not sessoes_data:
                logger.error("Não há sessões para criar execuções")
                return
                
            logger.info(f"Carregadas {len(sessoes_data)} sessões")
            
            # Filtrar apenas sessões executadas
            sessoes_executadas = [s for s in sessoes_data if s.get('status') == 'executada']
            logger.info(f"Filtradas {len(sessoes_executadas)} sessões executadas")
            
            # Verificar se os números de guia existem na tabela guias
            numeros_guia = list(set([s.get('numero_guia') for s in sessoes_executadas if s.get('numero_guia')]))
            guias_existentes = self.supabase.table('guias').select('numero_guia').in_('numero_guia', numeros_guia).execute()
            guias_validas = [g['numero_guia'] for g in guias_existentes.data]
            
            # Filtrar sessões cujas guias existem
            sessoes_validas = [s for s in sessoes_executadas if s.get('numero_guia') in guias_validas]
            
            if len(sessoes_validas) < len(sessoes_executadas):
                logger.warning(f"Foram ignoradas {len(sessoes_executadas) - len(sessoes_validas)} sessões com números de guia inválidos")
            
            logger.info(f"Processando {len(sessoes_validas)} sessões válidas")

            # Carregando informações adicionais de fichas
            fichas_ids = list(set([s.get('ficha_id') for s in sessoes_validas if s.get('ficha_id')]))
            fichas_info = self.supabase.table('fichas').select('id, paciente_nome, paciente_carteirinha').in_('id', fichas_ids).execute()
            fichas_map = {f['id']: f for f in fichas_info.data}

            # Dados do profissional padrão
            profissional = {
                'id': self.admin_id,
                'nome': 'Dr. Sistema',
                'crm': '12345'
            }

            # Lista para execuções normais
            execucoes_normais = []
            # Lista para execuções com divergências específicas
            execucoes_com_divergencias = []
            # Lista para execuções duplicadas
            execucoes_duplicadas = []
            # Lista para execuções sem ficha
            execucoes_sem_ficha = []
            # Lista para execuções sem data
            execucoes_sem_data = []

            # 1. Criar execuções normais para a maioria das sessões
            for sessao in sessoes_executadas:
                ficha_id = sessao.get('ficha_id')
                ficha = fichas_map.get(ficha_id, {})
                
                # Execução normal, mesma data da sessão
                execucao = {
                    "guia_id": sessao['guia_id'],
                    "sessao_id": sessao['id'],
                    "data_execucao": sessao['data_sessao'],
                    "data_atendimento": sessao['data_sessao'],  # Mesmo valor para evitar divergência
                    "paciente_nome": ficha.get('paciente_nome', 'Paciente não identificado'),
                    "paciente_carteirinha": ficha.get('paciente_carteirinha', 'Carteirinha não identificada'),
                    "numero_guia": sessao['numero_guia'],
                    "codigo_ficha": sessao['codigo_ficha'],
                    "codigo_ficha_temp": False,
                    "usuario_executante": profissional['id'],
                    "origem": "manual",
                    "ip_origem": "127.0.0.1",
                    "ordem_execucao": sessao['ordem_execucao'],
                    "status_biometria": "nao_verificado",
                    "conselho_profissional": "CRM",
                    "numero_conselho": profissional['crm'],
                    "uf_conselho": "SP",
                    "codigo_cbo": "225125",
                    "profissional_executante": profissional['nome'],
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
                
                # Algumas lógicas específicas baseadas na guia ou sessão
                guia_num = sessao.get('numero_guia', '')
                
                # 2. Para guia G2024003 - data_divergente
                if guia_num == 'G2024003' and sessao['ordem_execucao'] > 3:
                    # Alterar a data da execução para 1 dia depois da sessão
                    data_sessao = datetime.strptime(sessao['data_sessao'], '%Y-%m-%d')
                    execucao['data_execucao'] = (data_sessao + timedelta(days=1)).strftime('%Y-%m-%d')
                    execucoes_com_divergencias.append(execucao)
                    continue
                
                # 3. Para guia G2024002 - quantidade_excedida
                if guia_num == 'G2024002':
                    # Armazenar todas normalmente, depois adicionaremos execuções extras
                    execucoes_normais.append(execucao)
                    
                    # Criar execuções extras para essa guia no final
                    if sessao['ordem_execucao'] == 5:  # Na última sessão autorizada
                        # Adicionar 3 execuções extras com datas subsequentes
                        data_base = datetime.strptime(sessao['data_sessao'], '%Y-%m-%d')
                        
                        for i in range(1, 4):  # 3 extras
                            execucao_extra = execucao.copy()
                            execucao_extra['data_execucao'] = (data_base + timedelta(days=i)).strftime('%Y-%m-%d')
                            execucao_extra['data_atendimento'] = execucao_extra['data_execucao']
                            execucao_extra['ordem_execucao'] = 5 + i
                            execucoes_com_divergencias.append(execucao_extra)
                    continue
                
                # 4. Para guia G2024006 - duplicidade
                if guia_num == 'G2024006' and 1 <= sessao['ordem_execucao'] <= 3:
                    # Criar uma duplicata exata
                    execucao_duplicada = execucao.copy()
                    execucoes_duplicadas.append(execucao_duplicada)
                
                # 5. Para guia G2024007 - falta_data_execucao
                if guia_num == 'G2024007' and 1 <= sessao['ordem_execucao'] <= 3:
                    # Criar execuções sem data
                    execucao_sem_data = execucao.copy()
                    execucao_sem_data['data_execucao'] = None  # Campo NULL
                    execucoes_sem_data.append(execucao_sem_data)
                    # Pular a execução normal para estas sessões
                    continue
                
                execucoes_normais.append(execucao)
            
            # 6. Criar execuções sem ficha correspondente para guia G2024006
            sessao_lucia = next((s for s in sessoes_data if s.get('numero_guia') == 'G2024006'), None)
            
            if sessao_lucia:
                ficha_id = sessao_lucia.get('ficha_id')
                ficha = fichas_map.get(ficha_id, {})
                
                # Criar 2 execuções sem ficha
                for i in range(1, 3):
                    data_exec = (datetime.now() + timedelta(days=30+i)).strftime('%Y-%m-%d')
                    
                    execucao_sem_ficha = {
                        "guia_id": sessao_lucia['guia_id'],
                        "sessao_id": None,  # Sem sessão correspondente
                        "data_execucao": data_exec,
                        "data_atendimento": data_exec,
                        "paciente_nome": ficha.get('paciente_nome', 'Paciente não identificado'),
                        "paciente_carteirinha": ficha.get('paciente_carteirinha', 'Carteirinha não identificada'),
                        "numero_guia": sessao_lucia['numero_guia'],
                        "codigo_ficha": "TEMP" + str(uuid.uuid4())[:8],  # Código temporário
                        "codigo_ficha_temp": True,
                        "usuario_executante": profissional['id'],
                        "origem": "manual",
                        "ip_origem": "127.0.0.1",
                        "ordem_execucao": 9 + i,  # Além do total autorizado
                        "status_biometria": "nao_verificado",
                        "conselho_profissional": "CRM",
                        "numero_conselho": profissional['crm'],
                        "uf_conselho": "SP",
                        "codigo_cbo": "225125",
                        "profissional_executante": profissional['nome'],
                        "created_by": self.admin_id,
                        "updated_by": self.admin_id
                    }
                    execucoes_sem_ficha.append(execucao_sem_ficha)
            
            # Juntar todas as execuções
            todas_execucoes = execucoes_normais + execucoes_com_divergencias + execucoes_duplicadas + execucoes_sem_ficha + execucoes_sem_data
            
            # Inserir execuções em lotes
            if todas_execucoes:
                logger.info(f"Inserindo {len(todas_execucoes)} execuções no total...")
                logger.info(f"  - Normais: {len(execucoes_normais)}")
                logger.info(f"  - Com divergências de data: {len(execucoes_com_divergencias)}")
                logger.info(f"  - Duplicadas: {len(execucoes_duplicadas)}")
                logger.info(f"  - Sem ficha: {len(execucoes_sem_ficha)}")
                logger.info(f"  - Sem data: {len(execucoes_sem_data)}")
                
                # Inserir em lotes para evitar problemas com tamanho de payload
                lote_size = 20
                for i in range(0, len(todas_execucoes), lote_size):
                    lote = todas_execucoes[i:i+lote_size]
                    try:
                        result = self.supabase.table('execucoes').insert(lote).execute()
                        logger.info(f"Lote {i//lote_size + 1}: Inseridas {len(result.data)} execuções")
                    except Exception as e:
                        logger.error(f"Erro ao inserir lote {i//lote_size + 1}: {str(e)}")
                        # Tentar inserir uma por uma no caso de erro
                        for j, exec_item in enumerate(lote):
                            try:
                                result = self.supabase.table('execucoes').insert(exec_item).execute()
                                logger.info(f"  Item {j+1} inserido individualmente")
                            except Exception as e2:
                                logger.error(f"  Erro ao inserir item {j+1}: {str(e2)}")
                
                # Carregar todas as execuções inseridas
                todas_exec_final = self.supabase.table('execucoes').select('*').execute()
                self.execucoes = todas_exec_final.data
                logger.info(f"Total: Criadas {len(self.execucoes)} execuções")
            
        except Exception as e:
            logger.error("Erro ao criar execuções")
            logger.error(str(e))
            traceback.print_exc()

    def populate_atendimentos_faturamento(self):
        """Popula tabela de atendimentos para faturamento a partir de agendamentos 'realizado'"""
        try:
            # Verificar se a tabela existe
            try:
                logger.info("Verificando se a tabela atendimentos_faturamento existe...")
                # Tentativa de consulta para verificar se a tabela existe
                self.supabase.table('atendimentos_faturamento').select('id').limit(1).execute()
                logger.info("Tabela atendimentos_faturamento existe, continuando com a população")
            except Exception as e:
                logger.warning("Tabela atendimentos_faturamento não existe ou não está acessível")
                logger.debug(f"Detalhes do erro: {str(e)}")
                logger.info("Pulando a população da tabela atendimentos_faturamento")
                return
            
            # Verificar registros existentes
            atendimentos_existentes = self.supabase.table('atendimentos_faturamento').select('*').execute()
            if atendimentos_existentes.data:
                logger.info(f"Encontrados {len(atendimentos_existentes.data)} registros de faturamento existentes")
                return
            
            # Carregar agendamentos 'realizado'
            agendamentos_realizados = self.supabase.table('agendamentos').select('*').eq('schedule_status', 'realizado').execute()
            if not agendamentos_realizados.data:
                logger.info("Não há agendamentos realizados para gerar faturamento")
                return
            
            # Verificar se a coluna codigo_aba existe na tabela pacientes
            try:
                # Tentativa de consulta para verificar se a coluna existe
                self.supabase.table('pacientes').select('codigo_aba').limit(1).execute()
                logger.info("Coluna codigo_aba existe na tabela pacientes")
            except Exception as e:
                logger.error("A coluna codigo_aba não existe na tabela pacientes!")
                logger.error("Esta coluna é necessária para o funcionamento correto do sistema.")
                logger.error("Execute o seguinte comando SQL para adicionar a coluna:")
                logger.error("ALTER TABLE pacientes ADD COLUMN codigo_aba character varying(20) UNIQUE;")
                logger.debug(f"Detalhes do erro: {str(e)}")
                raise Exception("Coluna codigo_aba não encontrada na tabela pacientes. Adicione a coluna e tente novamente.")
            
            # Mapear pacientes por código_aba
            pacientes_map = {}
            for p in self.pacientes:
                if p.get('codigo_aba'):
                    pacientes_map[p['codigo_aba']] = p
            
            # Mapear carteirinhas por paciente_id
            carteirinhas_map = {}
            for c in self.carteirinhas:
                carteirinhas_map[c['paciente_id']] = c
            
            atendimentos_para_inserir = []
            
            for agendamento in agendamentos_realizados.data:
                # Obter informações do paciente
                paciente_id = None
                paciente_nome = "Paciente não identificado"
                carteirinha_num = None
                
                # Obter paciente pelo código ABA
                paciente_key = agendamento.get('schedule_pacient_id')
                paciente = pacientes_map.get(paciente_key)
                
                if paciente:
                    paciente_id = paciente.get('id')
                    paciente_nome = paciente.get('nome', "Paciente não identificado")
                    
                    # Obter carteirinha
                    carteirinha = carteirinhas_map.get(paciente_id)
                    if carteirinha:
                        carteirinha_num = carteirinha.get('numero_carteirinha')
                
                # Criar registro de faturamento
                atendimento_faturamento = {
                    "id_atendimento": agendamento['id'],
                    "carteirinha": carteirinha_num,
                    "paciente_nome": paciente_nome,
                    "data_atendimento": datetime.fromisoformat(agendamento['schedule_date_start'].replace('Z', '+00:00')).date().isoformat(),
                    "hora_inicial": datetime.fromisoformat(agendamento['schedule_date_start'].replace('Z', '+00:00')).time().strftime('%H:%M:%S'),
                    "id_profissional": agendamento.get('schedule_profissional_id'),
                    "profissional_nome": agendamento.get('schedule_profissional', "Profissional não identificado"),
                    "status": "confirmado",  # Único valor permitido pelo CHECK constraint
                    "codigo_faturamento": agendamento.get('schedule_codigo_faturamento', f"FAT{random.randint(10000, 99999)}"),
                }
                
                atendimentos_para_inserir.append(atendimento_faturamento)
            
            # Inserir registros no banco
            if atendimentos_para_inserir:
                logger.info(f"Inserindo {len(atendimentos_para_inserir)} registros de faturamento...")
                resultado = self.supabase.table('atendimentos_faturamento').insert(atendimentos_para_inserir).execute()
                logger.info(f"Criados {len(resultado.data)} registros de faturamento")
            
        except Exception as e:
            logger.error("Erro ao criar registros de faturamento")
            logger.error(str(e))
            traceback.print_exc()

    def populate_divergencias_manual(self):
        """Cria registros de divergências manualmente para testes de interface e relatórios"""
        try:
            # Verificar divergências existentes
            divergencias_existentes = self.supabase.table('divergencias').select('*').execute()
            if divergencias_existentes.data:
                logger.info(f"Encontradas {len(divergencias_existentes.data)} divergências existentes")
                # Isso é normal, pois as divergências devem ser geradas pelo sistema de auditoria
                return
            
            # Esta função não insere divergências diretamente, apenas mostra como seria
            # As divergências devem ser geradas pelo processo de auditoria
            # Isso é apenas para documentação
            
            logger.info("IMPORTANTE: As divergências não são inseridas diretamente!")
            logger.info("Para gerar divergências, execute o processo de auditoria no sistema")
            logger.info("Os dados gerados contêm os seguintes cenários de divergência:")
            logger.info("  1. ficha_sem_execucao: Fichas sem execução correspondente (G2024003)")
            logger.info("  2. execucao_sem_ficha: Execuções sem ficha correspondente (G2024006)")
            logger.info("  3. data_divergente: Datas divergentes entre sessão e execução (G2024003)")
            logger.info("  4. sessao_sem_assinatura: Sessões sem assinatura (G2024004)")
            logger.info("  5. guia_vencida: Guias com data de validade expirada (G2024005)")
            logger.info("  6. quantidade_excedida: Quantidade de execuções excedida (G2024002)")
            logger.info("  7. duplicidade: Execuções duplicadas (G2024006)")
            logger.info("  8. falta_data_execucao: Execuções sem data registrada (G2024007)")
        
        except Exception as e:
            logger.error("Erro ao verificar divergências")
            logger.error(str(e))
            traceback.print_exc()

    def limpar_dados_antigos(self, preservar_usuarios=True):
        """Limpa dados antigos do banco antes de popular novamente"""
        try:
            logger.info("Limpando dados existentes no banco...")
            
            # Primeiro limpar tabelas que dependem de outras (ordem é importante)
            logger.info("Limpando tabela divergencias...")
            try:
                self.supabase.table('divergencias').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                logger.info("Tabela divergencias limpa com sucesso")
            except Exception as e:
                logger.error(f"Erro ao limpar tabela divergencias: {str(e)}")
                
            logger.info("Limpando tabela auditoria_execucoes...")
            try:
                self.supabase.table('auditoria_execucoes').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                logger.info("Tabela auditoria_execucoes limpa com sucesso")
            except Exception as e:
                logger.error(f"Erro ao limpar tabela auditoria_execucoes: {str(e)}")
            
            # Tabelas que serão limpas em ordem (da mais dependente para a menos dependente)
            tabelas = [
                'execucoes', 
                'sessoes',
                'fichas',
                'guias',
                'carteirinhas',
                'pacientes',
                'planos_saude',
                'procedimentos',
                'storage',
                'agendamentos'
            ]
            
            # Remover atendimentos_faturamento da lista principal e verificar se existe
            try:
                logger.info("Verificando se a tabela atendimentos_faturamento existe...")
                # Tentativa de consulta para verificar se a tabela existe
                self.supabase.table('atendimentos_faturamento').select('id').limit(1).execute()
                logger.info("Tabela atendimentos_faturamento existe, adicionando à lista de limpeza")
                # Se chegou aqui, a tabela existe e pode ser limpa
                tabelas.append('atendimentos_faturamento')
            except Exception as e:
                logger.warning("Tabela atendimentos_faturamento não existe ou não está acessível, ignorando")
                logger.debug(f"Detalhes do erro: {str(e)}")
            
            # Se não preservar usuários, adicionar tabelas relacionadas
            if not preservar_usuarios:
                tabelas.extend([
                    'usuarios_especialidades',
                    'especialidades',
                    'usuarios'
                ])
            
            logger.info(f"Iniciando limpeza de dados antigos, preservando usuários: {preservar_usuarios}")
            
            for tabela in tabelas:
                try:
                    logger.info(f"Limpando tabela {tabela}...")
                    self.supabase.table(tabela).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                    logger.info(f"Tabela {tabela} limpa com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao limpar tabela {tabela}: {str(e)}")
                    # Continuar tentando limpar as outras tabelas
            
            logger.info("Limpeza de dados concluída")
            
        except Exception as e:
            logger.error("Erro durante limpeza de dados")
            logger.error(str(e))
            raise

    def populate_all(self):
        """Popula todas as tabelas com dados de teste"""
        try:
            # Limpar dados antigos (exceto usuários se preserve_users=True)
            self.limpar_dados_antigos(preservar_usuarios=self.preserve_users)
            
            # Gerar dados em ordem de dependência
            self.populate_especialidades()
            self.populate_procedimentos()
            self.populate_planos_saude()
            self.populate_pacientes()
            self.populate_carteirinhas()
            self.populate_guias()
            self.populate_agendamentos()  # Melhorada para dados de auditoria
            self.populate_fichas()
            self.populate_storage()
            self.populate_sessoes()
            self.populate_execucoes()  # Gera as divergências nos dados
            self.populate_atendimentos_faturamento()
            self.populate_divergencias_manual()  # Documentação sobre divergências
            
            logger.info("Todos os dados de teste foram gerados com sucesso!")
            
            # Resumo final
            logger.info("=== RESUMO FINAL ===")
            logger.info(f"Especialidades: {len(self.especialidades)}")
            logger.info(f"Procedimentos: {len(self.procedimentos)}")
            logger.info(f"Planos de Saúde: {len(self.planos_saude)}")
            logger.info(f"Pacientes: {len(self.pacientes)}")
            logger.info(f"Carteirinhas: {len(self.carteirinhas)}")
            logger.info(f"Guias: {len(self.guias)}")
            logger.info(f"Agendamentos: {len(self.agendamentos)}")
            logger.info(f"Fichas: {len(self.fichas)}")
            logger.info(f"Sessões: {len(self.sessoes)}")
            logger.info(f"Execuções: {len(self.execucoes)}")
            logger.info(f"Storage: {len(self.storage)}")
            
            # Instruções para o usuário
            logger.info("\n=== PRÓXIMOS PASSOS ===")
            logger.info("1. Para gerar divergências, execute o processo de auditoria no sistema")
            logger.info("2. Use o endpoint /api/auditoria/executar para iniciar a auditoria")
            logger.info("3. Verifique as divergências no dashboard de auditoria")
            
        except Exception as e:
            logger.error("Erro ao popular banco de dados")
            logger.error(str(e))
            traceback.print_exc()
            raise

def main():
    try:
        # Parâmetros de configuração
        preserve_users = True  # Não apagar usuários existentes
        generate_divergences = True  # Gerar dados com divergências para testes de auditoria
        
        # Configuração
        supabase = get_supabase_client()
        logger.info("Conectado ao Supabase")
        
        # ID do admin
        admin_id = "f5ba3137-3ef6-4958-bf07-dfaa12d91db3"
        
        # Executar população
        populator = DatabasePopulator(
            supabase, 
            admin_id,
            preserve_users=preserve_users,
            generate_divergences=generate_divergences
        )
        populator.populate_all()
        
    except Exception as e:
        logger.error("Erro fatal na execução do script")
        logger.error(str(e))
        logger.error(traceback.format_exc())
        exit(1)

if __name__ == "__main__":
    main()