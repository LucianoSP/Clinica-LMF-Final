import os
import sys
from pathlib import Path
import random
from datetime import datetime, timedelta
from faker import Faker
import logging
import traceback
import uuid
from dotenv import load_dotenv

## Para gerar os dados (criando guias se necessário)
# python backend/scripts/gerar_dados_vinculacao.py

# Para limpar dados de vinculação anteriores e gerar novos
# python backend/scripts/gerar_dados_vinculacao.py --clear




# Adicionar o diretório raiz do projeto ao PYTHONPATH
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Imports da nova estrutura
try:
    from backend.config.config import supabase
except ImportError:
    print("Erro: Não foi possível importar 'supabase' de 'backend.config.config'.")
    print("Certifique-se de que o PYTHONPATH está configurado corretamente e que a estrutura do projeto está intacta.")
    sys.exit(1)

# Carregar variáveis de ambiente
load_dotenv(project_root / '.env')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar Faker para português
fake = Faker('pt_BR')

# --- Constantes e Configurações ---
NUM_PACIENTES_PARA_TESTE = 5 # Usar apenas N pacientes para gerar dados
NUM_DIAS_RANGE = 30 # Gerar dados em um intervalo de +/- N dias a partir de hoje
ADMIN_ID = "f5ba3137-3ef6-4958-bf07-dfaa12d91db3" # TODO: Obter dinamicamente ou de config?

class VinculacaoDataGenerator:
    def __init__(self, supabase_client, admin_id):
        self.supabase = supabase_client
        self.admin_id = admin_id
        self.pacientes = []
        self.procedimentos = []
        self.guias = []
        self.carteirinhas = {} # {paciente_id: carteirinha_obj}
        self.agendamentos_gerados = []
        self.fichas_geradas = []
        self.sessoes_geradas = []
        self.execucoes_geradas = []
        self.profissional_aba_id = None # ID de um profissional da tabela usuarios_aba

    def _fetch_existing_data(self):
        """Busca dados essenciais existentes no banco."""
        logger.info("Buscando dados existentes (Pacientes, Procedimentos, Guias)...")
        try:
            # Pacientes (limitar para teste)
            pacientes_resp = self.supabase.table('pacientes').select('id, nome, id_origem').limit(NUM_PACIENTES_PARA_TESTE).execute()
            self.pacientes = pacientes_resp.data
            if not self.pacientes:
                raise Exception("Nenhum paciente encontrado no banco. Execute primeiro o script de população geral.")
            logger.info(f"✓ Encontrados {len(self.pacientes)} pacientes.")
            paciente_ids = [p['id'] for p in self.pacientes]

            # Procedimentos (buscar o de Fisioterapia, por exemplo)
            proc_resp = self.supabase.table('procedimentos').select('id, codigo, nome').eq('codigo', 'FISIO001').limit(1).execute()
            self.procedimentos = proc_resp.data
            if not self.procedimentos:
                 # Se FISIO001 não existe, tenta pegar qualquer um
                 proc_resp = self.supabase.table('procedimentos').select('id, codigo, nome').limit(1).execute()
                 self.procedimentos = proc_resp.data
                 if not self.procedimentos:
                     raise Exception("Nenhum procedimento encontrado. Execute o script de população geral.")
            logger.info(f"✓ Encontrado procedimento: {self.procedimentos[0]['nome']}")

            # Carteirinhas dos pacientes selecionados
            carteirinhas_resp = self.supabase.table('carteirinhas').select('*').in_('paciente_id', paciente_ids).execute()
            if not carteirinhas_resp.data:
                 logger.warning(f"Nenhuma carteirinha encontrada para os {NUM_PACIENTES_PARA_TESTE} pacientes selecionados. Algumas funcionalidades podem não gerar dados.")
            else:
                 self.carteirinhas = {c['paciente_id']: c for c in carteirinhas_resp.data}
                 logger.info(f"✓ Encontradas {len(self.carteirinhas)} carteirinhas.")

            # Guias (apenas para os pacientes selecionados e procedimento encontrado)
            guias_resp = self.supabase.table('guias').select('*').in_('paciente_id', paciente_ids).eq('procedimento_id', self.procedimentos[0]['id']).eq('status', 'autorizada').execute()
            self.guias = guias_resp.data
            if not self.guias:
                logger.warning(f"Nenhuma guia 'autorizada' encontrada para os pacientes/procedimento selecionados. A geração de Fichas/Sessões baseadas em Guias será limitada.")
                if not self.guias:
                    logger.warning("Nenhuma guia encontrada. Tentando gerar guias básicas para teste...")
                    self._generate_missing_guias()
            else:
                 logger.info(f"✓ Encontradas {len(self.guias)} guias autorizadas.")

            # ---> Buscar um Profissional da tabela usuarios_aba <--- 
            prof_resp = self.supabase.table('usuarios_aba').select('id').limit(1).execute()
            if prof_resp.data:
                self.profissional_aba_id = prof_resp.data[0]['id']
                logger.info(f"✓ Encontrado profissional ABA ID: {self.profissional_aba_id}")
            else:
                logger.warning("Nenhum profissional encontrado na tabela 'usuarios_aba'. Agendamentos podem falhar ao serem criados.")
                # O script tentará criar agendamentos com profissional_id = None

        except Exception as e:
            logger.error(f"Erro ao buscar dados existentes: {e}")
            raise

    def _generate_missing_guias(self):
        """Gera guias básicas se nenhuma adequada for encontrada."""
        logger.info("Gerando guias básicas faltantes...")
        if not self.pacientes or not self.procedimentos or not self.carteirinhas:
            logger.error("Dados insuficientes (pacientes, procedimentos ou carteirinhas) para gerar guias.")
            return

        guias_para_criar = []
        proc_id = self.procedimentos[0]['id']
        proc_codigo = self.procedimentos[0]['codigo']
        proc_nome = self.procedimentos[0]['nome']
        today = datetime.now().date()

        for i, paciente in enumerate(self.pacientes):
            paciente_id = paciente['id']
            carteirinha = self.carteirinhas.get(paciente_id)

            if carteirinha:
                # Criar uma guia básica para este paciente
                numero_guia_teste = f"G_VINC_TEST_{str(uuid.uuid4())[:4]}"
                data_solicitacao = today - timedelta(days=random.randint(5, 15))
                guia = {
                    "carteirinha_id": carteirinha['id'],
                    "paciente_id": paciente_id,
                    "procedimento_id": proc_id,
                    "numero_guia": numero_guia_teste,
                    "data_solicitacao": data_solicitacao.isoformat(),
                    "data_autorizacao": data_solicitacao.isoformat(), # Simples, mesma data
                    "status": "autorizada",
                    "tipo": "procedimento", # Assumindo tipo procedimento
                    "quantidade_autorizada": 10, # Quantidade padrão
                    "quantidade_executada": 0,
                    "codigo_servico": proc_codigo,
                    "descricao_servico": proc_nome,
                    "quantidade": 10,
                    "created_by": self.admin_id,
                    "updated_by": self.admin_id
                }
                guias_para_criar.append(guia)
            else:
                 logger.warning(f"Paciente {paciente.get('nome')} sem carteirinha encontrada. Não foi possível gerar guia de teste.")

        if guias_para_criar:
            try:
                logger.info(f"Inserindo {len(guias_para_criar)} guias de teste...")
                insert_resp = self.supabase.table('guias').insert(guias_para_criar).execute()
                # Atualiza self.guias com as guias recém-criadas
                self.guias.extend(insert_resp.data)
                logger.info(f"✓ Geradas e adicionadas {len(insert_resp.data)} guias básicas.")
            except Exception as e:
                logger.error(f"Erro ao inserir guias de teste: {e}")
                # Não levantar exceção, o script pode continuar com as guias que conseguiu buscar/criar
        else:
            logger.warning("Nenhuma guia básica pôde ser gerada.")

    def clear_test_data(self):
        """Limpa dados gerados anteriormente por este script nas tabelas relevantes."""
        logger.warning("Iniciando limpeza de dados de teste de vinculação...")
        tabelas_para_limpar = ['execucoes', 'sessoes', 'fichas', 'agendamentos'] # Ordem reversa de dependência FK
        for tabela in tabelas_para_limpar:
            try:
                # Tenta identificar registros criados por este script (ex: por um campo 'origem_teste' ou pelo admin_id específico)
                # Por simplicidade agora, vamos deletar tudo exceto IDs 'zerados' (se houver)
                # CUIDADO: Isso pode apagar dados não gerados por este script se não houver distinção clara.
                # Idealmente, adicionar um campo 'gerado_por_script_vinculacao' = TRUE
                logger.warning(f"Limpando tabela {tabela}...")
                # Exemplo de deleção mais segura (se admin_id for exclusivo do script):
                # delete_resp = self.supabase.table(tabela).delete().eq('created_by', self.admin_id).execute()
                # Deleção geral (MAIS PERIGOSA):
                delete_resp = self.supabase.table(tabela).delete().neq('id', uuid.UUID(int=0)).execute() # Deleta tudo exceto ID zero
                logger.info(f"✓ Tabela {tabela} limpa. Registros afetados: {len(delete_resp.data)}")
            except Exception as e:
                # Ignora erros se a tabela não existir ou não tiver o campo, mas loga
                logger.error(f"Erro ao limpar tabela {tabela}: {e}. Pulando...")
        logger.info("Limpeza de dados de teste concluída.")

    def generate_agendamentos_cenarios(self):
        """Gera agendamentos para os cenários de teste."""
        logger.info("Gerando agendamentos para cenários de vinculação...")
        if not self.pacientes or not self.procedimentos:
            logger.error("Pacientes ou procedimentos não carregados. Impossível gerar agendamentos.")
            return

        # Usar o ID do profissional ABA encontrado, ou None se não houver
        profissional_id_para_usar = self.profissional_aba_id

        agendamentos_para_criar = []
        today = datetime.now().date()
        proc_id = self.procedimentos[0]['id']

        for i, paciente in enumerate(self.pacientes):
            # Usar id_origem (INT) e converter para string para comparação com schedule_pacient_id (VARCHAR)
            id_origem_paciente = paciente.get('id_origem')
            if not id_origem_paciente:
                logger.warning(f"Paciente {paciente.get('nome')} sem id_origem. Pulando agendamentos para ele.")
                continue
            str_id_origem_paciente = str(id_origem_paciente)

            # Cenário 1: Agendamento que terá Ficha/Sessão e Execução correspondentes
            dt_cenario1 = today - timedelta(days=random.randint(1, NUM_DIAS_RANGE))
            agendamentos_para_criar.append({
                "schedule_date_start": dt_cenario1.strftime("%Y-%m-%dT09:00:00"),
                "schedule_date_end": dt_cenario1.strftime("%Y-%m-%dT10:00:00"),
                "schedule_pacient_id": str_id_origem_paciente, # Usar o id_origem como string
                "schedule_profissional_id": profissional_id_para_usar,
                "schedule_status": "realizado", # Deve ter sido realizado para ter ficha/execução
                "schedule_especialidade_id": None, # Preencher se souber a especialidade do FISIO001
                "schedule_codigo_faturamento": f"VINC_OK_{i}",
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            })

            # Cenário 2: Agendamento que terá apenas Execução (sem Ficha/Sessão)
            dt_cenario2 = today - timedelta(days=random.randint(1, NUM_DIAS_RANGE))
            # Evitar colisão de data com cenário 1 para o mesmo paciente
            if dt_cenario2 == dt_cenario1: dt_cenario2 += timedelta(days=1)
            agendamentos_para_criar.append({
                "schedule_date_start": dt_cenario2.strftime("%Y-%m-%dT10:00:00"),
                "schedule_date_end": dt_cenario2.strftime("%Y-%m-%dT11:00:00"),
                "schedule_pacient_id": str_id_origem_paciente, # Usar o id_origem como string
                "schedule_profissional_id": profissional_id_para_usar,
                "schedule_status": "realizado",
                "schedule_especialidade_id": None,
                "schedule_codigo_faturamento": f"VINC_AGEN_EXE_{i}",
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            })

            # Cenário 3: Agendamento que NÃO terá correspondência
            dt_cenario3 = today - timedelta(days=random.randint(1, NUM_DIAS_RANGE))
            while dt_cenario3 == dt_cenario1 or dt_cenario3 == dt_cenario2: dt_cenario3 += timedelta(days=1)
            agendamentos_para_criar.append({
                "schedule_date_start": dt_cenario3.strftime("%Y-%m-%dT11:00:00"),
                "schedule_date_end": dt_cenario3.strftime("%Y-%m-%dT12:00:00"),
                "schedule_pacient_id": str_id_origem_paciente, # Usar o id_origem como string
                "schedule_profissional_id": profissional_id_para_usar,
                "schedule_status": "realizado", # Pode ser realizado, mas não encontraremos ficha/exec
                "schedule_especialidade_id": None,
                "schedule_codigo_faturamento": f"VINC_ORF_{i}",
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            })

        if agendamentos_para_criar:
            try:
                insert_resp = self.supabase.table('agendamentos').insert(agendamentos_para_criar).execute()
                self.agendamentos_gerados = insert_resp.data
                logger.info(f"✓ Gerados {len(self.agendamentos_gerados)} agendamentos de teste.")
            except Exception as e:
                logger.error(f"Erro ao inserir agendamentos de teste: {e}")
                raise
        else:
            logger.warning("Nenhum agendamento de teste foi gerado.")

    def generate_fichas_sessoes_cenarios(self):
        """Gera fichas e sessões para os cenários de teste."""
        logger.info("Gerando Fichas/Sessões para cenários de vinculação...")
        if not self.guias and not self.agendamentos_gerados:
             logger.warning("Sem guias ou agendamentos gerados, não é possível criar fichas/sessões significativas para teste.")
             # Poderia criar fichas totalmente órfãs aqui se necessário
             return

        fichas_para_criar = []
        sessoes_para_criar = []
        today = datetime.now().date()

        # 1. Fichas/Sessões baseadas nos Agendamentos "VINC_OK"
        agendamentos_ok = [a for a in self.agendamentos_gerados if "VINC_OK" in a.get("schedule_codigo_faturamento", "")]
        for agendamento in agendamentos_ok:
            # Encontrar paciente pelo id_origem (string) comparando com schedule_pacient_id (string)
            paciente = next((p for p in self.pacientes if str(p.get('id_origem')) == agendamento.get('schedule_pacient_id')), None)
            if not paciente: continue
            paciente_id = paciente['id']

            # Tentar encontrar uma guia válida para este paciente
            guia_paciente = next((g for g in self.guias if g['paciente_id'] == paciente_id), None)
            if not guia_paciente:
                 logger.warning(f"Não encontrada guia para paciente {paciente_id} do agendamento {agendamento['id']}. Ficha/Sessão não será gerada para este cenário.")
                 continue # <<< PULAR SE NÃO ENCONTRAR GUIA

            # Se encontrou a guia, prosseguir com a criação
            guia_id = guia_paciente['id']
            numero_guia = guia_paciente['numero_guia']

            # Tentar obter dados da carteirinha
            carteirinha = self.carteirinhas.get(paciente_id)
            numero_carteirinha = carteirinha['numero_carteirinha'] if carteirinha else "N/A"
            paciente_nome = next((p['nome'] for p in self.pacientes if p['id'] == paciente_id), "N/A")
            data_atendimento = datetime.fromisoformat(agendamento['schedule_date_start']).date()

            # Criar Ficha
            ficha_id = uuid.uuid4()
            codigo_ficha = f"F_VINC_OK_{str(ficha_id)[:4]}"
            fichas_para_criar.append({
                "id": str(ficha_id),
                "codigo_ficha": codigo_ficha,
                "guia_id": guia_id,
                "agendamento_id": agendamento['id'], # << Vínculo direto com agendamento
                "paciente_id": paciente_id, # << Adicionado paciente_id
                "numero_guia": numero_guia,
                "data_atendimento": data_atendimento.isoformat(),
                "paciente_nome": paciente_nome,
                "paciente_carteirinha": numero_carteirinha,
                "total_sessoes": 1, # Apenas 1 sessão para simplificar
                "status": 'conferida', # Correção: Usar valor válido do ENUM status_ficha
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            })

            # Criar Sessão correspondente
            sessoes_para_criar.append({
                "ficha_id": str(ficha_id),
                "guia_id": guia_id,
                "agendamento_id": agendamento['id'], # << Vínculo direto com agendamento
                "data_sessao": data_atendimento.isoformat(),
                "status": "executada",
                "numero_guia": numero_guia,
                "codigo_ficha": codigo_ficha,
                "ordem_execucao": 1, # << Ordem da execução
                "created_by": self.admin_id,
                "updated_by": self.admin_id
            })

        # 2. Fichas/Sessões SEM Agendamento direto (para testar vínculo Sessão <-> Execução)
        # Usar guias que não foram usadas nos agendamentos VINC_OK
        guias_usadas_ids = [f['guia_id'] for f in fichas_para_criar if f.get('guia_id')]
        guias_disponiveis = [g for g in self.guias if g['id'] not in guias_usadas_ids]

        for guia in guias_disponiveis[:NUM_PACIENTES_PARA_TESTE]: # Limitar
             paciente_id = guia['paciente_id']
             carteirinha = self.carteirinhas.get(paciente_id)
             numero_carteirinha = carteirinha['numero_carteirinha'] if carteirinha else "N/A"
             paciente_nome = next((p['nome'] for p in self.pacientes if p['id'] == paciente_id), "N/A")
             data_atendimento = today - timedelta(days=random.randint(1, NUM_DIAS_RANGE))

             # Criar Ficha
             ficha_id = uuid.uuid4()
             codigo_ficha = f"F_VINC_SE_{str(ficha_id)[:4]}"
             fichas_para_criar.append({
                 "id": str(ficha_id),
                 "codigo_ficha": codigo_ficha,
                 "guia_id": guia['id'],
                 "agendamento_id": None, # << SEM vínculo direto com agendamento
                 "paciente_id": paciente_id,
                 "numero_guia": guia['numero_guia'],
                 "data_atendimento": data_atendimento.isoformat(),
                 "paciente_nome": paciente_nome,
                 "paciente_carteirinha": numero_carteirinha,
                 "total_sessoes": 1,
                 "status": 'conferida', # Correção: Usar valor válido do ENUM status_ficha
                 "created_by": self.admin_id,
                 "updated_by": self.admin_id
             })

             # Criar Sessão correspondente
             sessoes_para_criar.append({
                 "ficha_id": str(ficha_id),
                 "guia_id": guia['id'],
                 "agendamento_id": None, # << SEM vínculo direto com agendamento
                 "data_sessao": data_atendimento.isoformat(),
                 "status": "executada",
                 "numero_guia": guia['numero_guia'],
                 "codigo_ficha": codigo_ficha,
                 "ordem_execucao": random.randint(1, guia.get('quantidade_autorizada', 5)), # Ordem aleatória dentro do autorizado
                 "created_by": self.admin_id,
                 "updated_by": self.admin_id
             })


        # Inserir Fichas
        if fichas_para_criar:
            try:
                insert_resp = self.supabase.table('fichas').insert(fichas_para_criar).execute()
                self.fichas_geradas = insert_resp.data
                logger.info(f"✓ Geradas {len(self.fichas_geradas)} fichas de teste.")
            except Exception as e:
                logger.error(f"Erro ao inserir fichas de teste: {e}")
                # Não levantar exceção aqui para tentar inserir sessões
        else:
            logger.warning("Nenhuma ficha de teste foi gerada.")

        # Inserir Sessões
        if sessoes_para_criar:
             # Atualizar ficha_id nas sessoes caso a inserção de fichas tenha falhado mas queremos as sessoes
             if not self.fichas_geradas and fichas_para_criar:
                 fichas_map = {f['id']: f for f in fichas_para_criar}
                 for sessao in sessoes_para_criar:
                     if sessao['ficha_id'] not in [f_db.get('id') for f_db in self.fichas_geradas]:
                          # Se a ficha não foi criada no DB, tentar usar o ID gerado localmente
                          if sessao['ficha_id'] in fichas_map:
                              logger.debug(f"Usando ID local para ficha {sessao['ficha_id']}")
                          else:
                              logger.warning(f"Não foi possível encontrar ficha para sessão {sessao['codigo_ficha']}. Sessão pode ficar órfã.")
                              sessao['ficha_id'] = None # Ou remover a sessão da lista

             try:
                 insert_resp = self.supabase.table('sessoes').insert(sessoes_para_criar).execute()
                 self.sessoes_geradas = insert_resp.data
                 logger.info(f"✓ Geradas {len(self.sessoes_geradas)} sessões de teste.")
             except Exception as e:
                 logger.error(f"Erro ao inserir sessões de teste: {e}")
                 # Não levantar exceção
        else:
             logger.warning("Nenhuma sessão de teste foi gerada.")


    def generate_execucoes_cenarios(self):
        """Gera execuções simuladas para os cenários de teste."""
        logger.info("Gerando Execuções para cenários de vinculação...")
        today = datetime.now().date()

        execucoes_para_criar = []

        # 1. Execuções que devem vincular com Agendamentos "VINC_AGEN_EXE"
        agendamentos_agen_exe = [a for a in self.agendamentos_gerados if "VINC_AGEN_EXE" in a.get("schedule_codigo_faturamento", "")]
        for agendamento in agendamentos_agen_exe:
             # Encontrar paciente pelo id_origem (string) comparando com schedule_pacient_id (string)
             paciente = next((p for p in self.pacientes if str(p.get('id_origem')) == agendamento.get('schedule_pacient_id')), None)
             if not paciente: continue
             paciente_id = paciente['id']
             # Encontrar guia e carteirinha
             guia_paciente = next((g for g in self.guias if g['paciente_id'] == paciente_id), None)
             carteirinha = self.carteirinhas.get(paciente_id)
             paciente_nome = next((p['nome'] for p in self.pacientes if p['id'] == paciente_id), "N/A")
             data_execucao = datetime.fromisoformat(agendamento['schedule_date_start']).date()
             ordem = random.randint(1,5) # Ordem aleatória

             # Criar Execução
             execucao = {
                 "guia_id": guia_paciente['id'] if guia_paciente else None,
                 "sessao_id": None, # << SEM Sessão vinculada diretamente
                 "agendamento_id": agendamento['id'], # << Vínculo direto com agendamento
                 "paciente_id": paciente_id, # << Adicionado paciente_id
                 "data_execucao": data_execucao.isoformat(),
                 "data_atendimento": data_execucao.isoformat(), # Usar a mesma data
                 "paciente_nome": paciente_nome,
                 "paciente_carteirinha": carteirinha['numero_carteirinha'] if carteirinha else "N/A",
                 "numero_guia": guia_paciente['numero_guia'] if guia_paciente else None,
                 "codigo_ficha": None, # Ou um código temporário?
                 "codigo_ficha_temp": True if not guia_paciente else False, # Temporário se não achar guia
                 "ordem_execucao": ordem,
                 "origem": "simulado_scraping",
                 "created_by": self.admin_id,
                 "updated_by": self.admin_id
             }
             execucoes_para_criar.append(execucao)

             # Adicionar uma execução AMBÍGUA para o mesmo dia (mesmo paciente, mesma data, outra hora?)
             if random.random() < 0.3: # 30% de chance de criar ambiguidade
                execucao_ambigua = execucao.copy()
                # execucao_ambigua["id"] = str(uuid.uuid4()) # REMOVER: Deixar o DB gerar o ID
                execucao_ambigua["ordem_execucao"] = ordem + 1 # Ordem diferente
                execucao_ambigua["agendamento_id"] = None # Sem vínculo direto para forçar busca
                execucoes_para_criar.append(execucao_ambigua)


        # 2. Execuções que devem vincular com Sessões "VINC_SE"
        sessoes_se = [s for s in self.sessoes_geradas if "VINC_SE" in s.get("observacao_interna", "")]
        for sessao in sessoes_se:
            ficha = next((f for f in self.fichas_geradas if f['id'] == sessao['ficha_id']), None)
            if not ficha: continue
            paciente_id = ficha['paciente_id']
            carteirinha = self.carteirinhas.get(paciente_id)
            paciente_nome = ficha['paciente_nome']
            data_execucao = datetime.fromisoformat(sessao['data_sessao']).date()
            ordem = sessao['ordem_execucao'] # Usar a mesma ordem da sessão

            # Pequena variação na data para testar tolerância (10% de chance)
            if random.random() < 0.1:
                data_execucao += timedelta(days=random.choice([-1, 1]))

            # Criar Execução
            execucao = {
                 "guia_id": sessao['guia_id'],
                 "sessao_id": sessao['id'], # << Vínculo direto com sessão
                 "agendamento_id": None, # Sem vínculo direto com agendamento
                 "paciente_id": paciente_id,
                 "data_execucao": data_execucao.isoformat(),
                 "data_atendimento": sessao['data_sessao'], # Manter data original do atendimento
                 "paciente_nome": paciente_nome,
                 "paciente_carteirinha": carteirinha['numero_carteirinha'] if carteirinha else "N/A",
                 "numero_guia": sessao['numero_guia'],
                 "codigo_ficha": sessao['codigo_ficha'],
                 "codigo_ficha_temp": False,
                 "ordem_execucao": ordem,
                 "origem": "simulado_scraping",
                 "created_by": self.admin_id,
                 "updated_by": self.admin_id
             }
            execucoes_para_criar.append(execucao)

        # 3. Execuções Órfãs (não devem vincular com nada inicialmente)
        for i in range(NUM_PACIENTES_PARA_TESTE // 2): # Metade dos pacientes terão execuções órfãs
            paciente = random.choice(self.pacientes)
            paciente_id = paciente['id']
            guia_paciente = next((g for g in self.guias if g['paciente_id'] == paciente_id), None)
            carteirinha = self.carteirinhas.get(paciente_id)
            paciente_nome = paciente['nome']
            # Data bem distante para não coincidir
            data_execucao = today + timedelta(days=random.randint(30, 60))

            execucao = {
                 "guia_id": guia_paciente['id'] if guia_paciente else None,
                 "sessao_id": None,
                 "agendamento_id": None,
                 "paciente_id": paciente_id,
                 "data_execucao": data_execucao.isoformat(),
                 "data_atendimento": data_execucao.isoformat(),
                 "paciente_nome": paciente_nome,
                 "paciente_carteirinha": carteirinha['numero_carteirinha'] if carteirinha else "N/A",
                 "numero_guia": guia_paciente['numero_guia'] if guia_paciente else f"GUIA_ORFA_{i}",
                 "codigo_ficha": f"F_ORFA_{i}",
                 "codigo_ficha_temp": True,
                 "ordem_execucao": random.randint(1, 5),
                 "origem": "simulado_scraping",
                 "created_by": self.admin_id,
                 "updated_by": self.admin_id
             }
            execucoes_para_criar.append(execucao)


        # Inserir Execuções
        if execucoes_para_criar:
            try:
                insert_resp = self.supabase.table('execucoes').insert(execucoes_para_criar).execute()
                self.execucoes_geradas = insert_resp.data
                logger.info(f"✓ Geradas {len(self.execucoes_geradas)} execuções de teste.")
            except Exception as e:
                logger.error(f"Erro ao inserir execuções de teste: {e}")
                # Tentar inserir individualmente em caso de erro no lote
                logger.info("Tentando inserir execuções individualmente...")
                count = 0
                for execucao in execucoes_para_criar:
                    try:
                        self.supabase.table('execucoes').insert(execucao).execute()
                        count += 1
                    except Exception as e_ind:
                        logger.error(f"  Erro ao inserir execução: {e_ind}")
                logger.info(f"✓ Inseridas {count} execuções individualmente.")

        else:
             logger.warning("Nenhuma execução de teste foi gerada.")


    def run(self, clear_data=False):
        """Executa todo o processo de geração de dados."""
        try:
            if clear_data:
                self.clear_test_data()

            self._fetch_existing_data()
            self.generate_agendamentos_cenarios()
            self.generate_fichas_sessoes_cenarios()
            self.generate_execucoes_cenarios()

            logger.info("\n=== GERAÇÃO DE DADOS DE VINCULAÇÃO CONCLUÍDA ===")
            logger.info(f"Agendamentos Gerados: {len(self.agendamentos_gerados)}")
            logger.info(f"Fichas Geradas: {len(self.fichas_geradas)}")
            logger.info(f"Sessões Geradas: {len(self.sessoes_geradas)}")
            logger.info(f"Execuções Geradas: {len(self.execucoes_geradas)}")
            logger.info("\nExecute as funções de vinculação batch (SQL ou API) para testar.")

        except Exception as e:
            logger.error(f"Erro fatal durante a geração de dados de vinculação: {e}")
            logger.error(traceback.format_exc())
            raise

def main():
    """Função principal para executar o gerador de dados."""
    logger.info("Iniciando script para gerar dados de teste de vinculação...")

    # Argumento para limpar dados (--clear)
    clear_previous_data = '--clear' in sys.argv

    try:
        if not supabase:
            logger.error("Cliente Supabase não inicializado.")
            sys.exit(1)

        logger.info("Conectado ao Supabase.")

        # Verificar se o admin_id existe (opcional, mas bom)
        try:
            admin_check = supabase.table('usuarios').select('id').eq('id', ADMIN_ID).maybe_single().execute()
            if not admin_check.data:
                logger.warning(f"Usuário Admin com ID {ADMIN_ID} não encontrado. Verifique o ID ou use um existente.")
                # Poderia tentar buscar um admin qualquer aqui
        except Exception as e:
            logger.error(f"Erro ao verificar Admin ID: {e}")
            # Continuar mesmo assim? Ou sair? Decidi continuar.


        generator = VinculacaoDataGenerator(supabase, ADMIN_ID)
        generator.run(clear_data=clear_previous_data)

    except Exception as e:
        logger.error("Erro na execução principal do script.")
        # O erro já foi logado dentro do generator.run()
        sys.exit(1)

if __name__ == "__main__":
    main() 