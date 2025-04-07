--================ EXTENSÕES =================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


--================ TIPOS ENUM =================

-- Tipos enumerados
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_usuario') THEN
        CREATE TYPE tipo_usuario AS ENUM (
            'admin',
            'profissional',
            'operador',
            'sistema'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_registro') THEN
        CREATE TYPE status_registro AS ENUM (
            'ativo',
            'inativo',
            'pendente'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_carteirinha') THEN
        CREATE TYPE status_carteirinha AS ENUM (
            'ativa',
            'inativa',
            'suspensa',
            'vencida'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_guia') THEN
        CREATE TYPE status_guia AS ENUM (
            'rascunho',
            'pendente',
            'autorizada',
            'negada',
            'cancelada',
            'executada'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_procedimento') THEN
        CREATE TYPE tipo_procedimento AS ENUM (
            'consulta',
            'exame',
            'procedimento',
            'internacao'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_ficha') THEN
        CREATE TYPE status_ficha AS ENUM (
            'pendente',
            'conferida',
            'faturada',
            'cancelada'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_biometria') THEN
        CREATE TYPE status_biometria AS ENUM (
            'nao_verificado',
            'verificado',
            'falha'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_sessao') THEN
        CREATE TYPE status_sessao AS ENUM (
            'pendente',
            'executada',
            'faturada',
            'cancelada'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_divergencia') THEN
        CREATE TYPE tipo_divergencia AS ENUM (
            'ficha_sem_execucao',
            'execucao_sem_ficha',
            'sessao_sem_assinatura',
            'data_divergente',
            'guia_vencida',
            'quantidade_excedida',
            'falta_data_execucao',
            'duplicidade'
        );
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_divergencia') THEN
        CREATE TYPE status_divergencia AS ENUM ('pendente', 'em_analise', 'resolvida', 'cancelada');
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_guia') THEN
        CREATE TYPE tipo_guia AS ENUM (
            'consulta',
            'exame',
            'procedimento',
            'internacao'
        );
    END IF;
END$$;

-- Adicionar tipo enum para status de agendamento
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_agendamento') THEN
        CREATE TYPE status_agendamento AS ENUM (
            'agendado',
            'cancelado',
            'realizado',
            'faltou'
        );
    END IF;
END$$;

-- enum para tipo de unidade
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_unidade') THEN
        CREATE TYPE tipo_unidade AS ENUM (
            'Unidade Oeste',
            'República do Líbano'
        );
    END IF;
END$$;


--================ FUNÇÕES =================

-- Função para atualizar updated_at automaticamente (definida uma única vez)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';


-- 1. Tabelas base (sem foreign keys) - Corrigindo a tabela usuarios com NULL nas referências circulares
CREATE TABLE IF NOT EXISTS usuarios (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_user_id uuid UNIQUE,
    nome text NOT NULL,
    email text UNIQUE,
    tipo_usuario tipo_usuario DEFAULT 'operador'::tipo_usuario,
    ativo boolean DEFAULT true,
    ultimo_acesso timestamptz,
    permissoes jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id) NULL,
    updated_by uuid REFERENCES usuarios(id) NULL,
    crm character varying(15),
    telefone character varying(15),
    foto text
);

CREATE TABLE IF NOT EXISTS planos_saude (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_operadora character varying(20) UNIQUE,
    registro_ans character varying(20),
    nome character varying(255) NOT NULL,
    tipo_plano character varying(50),
    abrangencia character varying(50),
    observacoes text,
    ativo boolean DEFAULT true,
    dados_contrato jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz
);

CREATE TABLE IF NOT EXISTS especialidades (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome text NOT NULL,
    anexo text,
    status status_registro DEFAULT 'ativo'::status_registro,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    especialidade_id VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS procedimentos (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo character varying(20) NOT NULL UNIQUE,
    nome text NOT NULL,
    descricao text,
    tipo tipo_procedimento NOT NULL,
    valor decimal(10,2),
    valor_filme decimal(10,2),
    valor_operacional decimal(10,2),
    valor_total decimal(10,2),
    tempo_medio_execucao interval,
    requer_autorizacao boolean DEFAULT true,
    observacoes text,
    ativo boolean DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz
);

CREATE TABLE IF NOT EXISTS pacientes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome text NOT NULL,
    cpf character varying(14),
    rg character varying(15),
    data_nascimento date,
    foto text,
    nome_responsavel text,
    nome_pai text,
    nome_mae text,
    sexo character varying(1),
    cep character varying(9),
    endereco text,
    numero integer,
    complemento character varying(32),
    bairro character varying(64),
    cidade text,
    cidade_id integer,
    estado character(2),
    forma_pagamento integer,
    valor_consulta decimal(11,2),
    profissional_id uuid REFERENCES usuarios(id),
    escola_nome text,
    escola_ano text,
    escola_professor text,
    escola_periodo text,
    escola_contato text,
    patologia_id integer,
    tem_supervisor boolean DEFAULT false,
    supervisor_id uuid REFERENCES usuarios(id),
    tem_avaliacao_luria boolean DEFAULT false,
    avaliacao_luria_data_inicio_treinamento date,
    avaliacao_luria_reforcadores text,
    avaliacao_luria_obs_comportamento text,
    numero_carteirinha character varying(50),
    cpf_responsavel character varying(14),
    crm_medico character varying(15),
    nome_medico text,
    pai_nao_declarado boolean DEFAULT false,
    telefone character varying(15),
    email text,
    observacoes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    importado boolean DEFAULT false,
    id_origem INT,
    data_registro_origem timestamptz,
    data_atualizacao_origem timestamptz
);

CREATE TABLE IF NOT EXISTS storage (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome text NOT NULL,
    url text NOT NULL,
    size integer,
    content_type text,
    tipo_referencia text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id)
);


-- =====================================================
-- NOTA DE IMPLEMENTAÇÃO: Relação entre schedule_pagamento e planos_saude
-- =====================================================
-- 
-- IMPLEMENTAÇÃO ATUAL:
-- Atualmente, o campo schedule_pagamento armazena o nome do plano de saúde como texto 
-- sem restrição de chave estrangeira. Isso foi implementado desta forma para facilitar 
-- a migração de dados do sistema legado, onde schedule.pagamento contém valores de texto 
-- que correspondem ao campo nome na tabela planos_saude.
-- 
-- LIMITAÇÕES:
-- 1. Não há garantia de integridade referencial (nomes podem não corresponder)
-- 2. Mudanças no nome do plano na tabela planos_saude não são refletidas automaticamente
-- 3. Podem ocorrer inconsistências de dados devido à falta de validação
-- 
-- SUGESTÃO PARA IMPLEMENTAÇÃO FUTURA:
-- 1. Adicionar uma coluna schedule_plano_saude_id UUID que referencie planos_saude(id)
-- 2. Criar um processo de migração para associar os registros existentes
-- 3. Adicionar um trigger para manter os dois campos sincronizados durante o período de transição
-- 4. Eventualmente, remover o campo schedule_pagamento após a migração completa
-- 
-- Script para implementação futura:
-- 
-- -- Adicionar nova coluna
-- ALTER TABLE agendamentos ADD COLUMN schedule_plano_saude_id UUID REFERENCES planos_saude(id);
-- 
-- -- Processo de migração (executar uma única vez)
-- UPDATE agendamentos a
-- SET schedule_plano_saude_id = ps.id
-- FROM planos_saude ps
-- WHERE a.schedule_pagamento = ps.nome;
-- 
-- -- Criar trigger para sincronização bidirecional
-- CREATE OR REPLACE FUNCTION sync_plano_saude_agendamento()
-- RETURNS TRIGGER AS $$
-- BEGIN
--     IF TG_TABLE_NAME = 'agendamentos' THEN
--         -- Ao atualizar schedule_pagamento, atualizar schedule_plano_saude_id
--         IF NEW.schedule_pagamento IS NOT NULL THEN
--             NEW.schedule_plano_saude_id := (SELECT id FROM planos_saude WHERE nome = NEW.schedule_pagamento LIMIT 1);
--         END IF;
--     ELSIF TG_TABLE_NAME = 'planos_saude' THEN
--         -- Ao atualizar nome do plano, atualizar schedule_pagamento
--         IF NEW.nome <> OLD.nome THEN
--             UPDATE agendamentos SET schedule_pagamento = NEW.nome WHERE schedule_plano_saude_id = NEW.id;
--         END IF;
--     END IF;
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
-- 
-- CREATE TRIGGER sync_agendamento_plano
-- BEFORE INSERT OR UPDATE ON agendamentos
-- FOR EACH ROW EXECUTE FUNCTION sync_plano_saude_agendamento();
-- 
-- CREATE TRIGGER sync_plano_agendamento
-- AFTER UPDATE ON planos_saude
-- FOR EACH ROW EXECUTE FUNCTION sync_plano_saude_agendamento();
-- =====================================================

-- Tabela para agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Campos originais do MySQL (manter compatibilidade)
    schedule_id VARCHAR(255),
    schedule_date_start TIMESTAMPTZ,
    schedule_date_end TIMESTAMPTZ,
    schedule_pacient_id VARCHAR(255),
    schedule_pagamento_id VARCHAR(255),
    schedule_pagamento TEXT,
    schedule_profissional_id UUID REFERENCES usuarios_aba(id),
    schedule_profissional TEXT,
    schedule_unidade VARCHAR(50),
    schedule_room_id INTEGER,
    schedule_qtd_sessions INTEGER DEFAULT 1,
    schedule_status VARCHAR(50),
    schedule_room_rent_value DECIMAL(10,2),
    schedule_fixed BOOLEAN DEFAULT FALSE,
    schedule_especialidade_id INTEGER,
    schedule_local_id INTEGER,
    schedule_saldo_sessoes INTEGER DEFAULT 0,
    schedule_elegibilidade BOOLEAN DEFAULT TRUE,
    schedule_falha_do_profissional BOOLEAN DEFAULT FALSE,
    schedule_parent_id INTEGER,
    schedule_registration_date TIMESTAMPTZ,
    schedule_lastupdate TIMESTAMPTZ,
    parent_id UUID REFERENCES agendamentos(id),
    schedule_codigo_faturamento TEXT,
    
    -- Campos novos para o sistema (mantendo compatibilidade)
    paciente_id UUID REFERENCES pacientes(id),
    procedimento_id UUID REFERENCES procedimentos(id),
    data_agendamento DATE,
    hora_inicio TIME,
    hora_fim TIME,
    status VARCHAR(50),
    observacoes TEXT,
    
    -- Campos de auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    
    -- Campos para rastreamento de importação
    importado BOOLEAN DEFAULT FALSE,
    id_origem VARCHAR(255),
    data_registro_origem TIMESTAMPTZ,
    data_atualizacao_origem TIMESTAMPTZ,

    -- Colunas para relacionar com tabelas importadas do ABA (FKs para Supabase)
    sala_id_supabase UUID NULL REFERENCES public.salas(id) ON DELETE SET NULL ON UPDATE CASCADE,
    local_id_supabase UUID NULL REFERENCES public.locais(id) ON DELETE SET NULL ON UPDATE CASCADE,
    especialidade_id_supabase UUID NULL REFERENCES public.especialidades(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Adiciona comentários para clareza (opcional, mas boa prática)
COMMENT ON COLUMN public.agendamentos.sala_id_supabase IS 'FK para a tabela salas (importada do sistema ABA)';
COMMENT ON COLUMN public.agendamentos.local_id_supabase IS 'FK para a tabela locais (importada do sistema ABA)';
COMMENT ON COLUMN public.agendamentos.especialidade_id_supabase IS 'FK para a tabela especialidades (importada do sistema ABA)';

-- Índices para agendamentos (campos novos)
CREATE INDEX IF NOT EXISTS idx_agendamentos_paciente_id ON agendamentos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_procedimento_id ON agendamentos(procedimento_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data ON agendamentos(data_agendamento);
CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(status);
CREATE INDEX IF NOT EXISTS idx_agendamentos_importado ON agendamentos(importado);
CREATE INDEX IF NOT EXISTS idx_agendamentos_id_origem ON agendamentos(id_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_registro_origem ON agendamentos(data_registro_origem);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_atualizacao_origem ON agendamentos(data_atualizacao_origem);

-- Tabela para controlar importações de agendamentos
CREATE TABLE IF NOT EXISTS controle_importacao_agendamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp_importacao TIMESTAMPTZ DEFAULT NOW(),
    ultima_data_registro_importada TIMESTAMPTZ,
    ultima_data_atualizacao_importada TIMESTAMPTZ,
    quantidade_registros_importados INTEGER DEFAULT 0,
    quantidade_registros_atualizados INTEGER DEFAULT 0,
    usuario_id UUID REFERENCES usuarios(id),
    observacoes TEXT
);

-- Índices para controle de importação de agendamentos
CREATE INDEX IF NOT EXISTS idx_controle_importacao_agendamentos_datas 
    ON controle_importacao_agendamentos(ultima_data_registro_importada, ultima_data_atualizacao_importada);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_agendamentos_timestamp 
    ON controle_importacao_agendamentos(timestamp_importacao);

-- 2. Primeira camada de relacionamentos
CREATE TABLE IF NOT EXISTS usuarios_especialidades (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_aba_id uuid NOT NULL REFERENCES usuarios_aba(id),
    especialidade_id uuid NOT NULL REFERENCES especialidades(id),
    principal boolean DEFAULT false,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    UNIQUE (usuario_aba_id, especialidade_id)
);

CREATE TABLE IF NOT EXISTS carteirinhas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id uuid NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    plano_saude_id uuid NOT NULL REFERENCES planos_saude(id) ON DELETE RESTRICT,
    numero_carteirinha text NOT NULL,
    data_validade date,
    status status_carteirinha NOT NULL DEFAULT 'ativa',
    motivo_inativacao text,
    historico_status jsonb DEFAULT '[]',
    titular boolean DEFAULT false,
    nome_titular text,
    cpf_titular character varying(14),
    observacoes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    UNIQUE(plano_saude_id, numero_carteirinha)
);

-- 3. Segunda camada
CREATE TABLE IF NOT EXISTS guias (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    carteirinha_id uuid NOT NULL REFERENCES carteirinhas(id) ON DELETE RESTRICT,
    paciente_id uuid NOT NULL REFERENCES pacientes(id),
    procedimento_id uuid NOT NULL REFERENCES procedimentos(id),
    numero_guia text NOT NULL,
    data_solicitacao date DEFAULT CURRENT_DATE,
    data_autorizacao date,
    status status_guia DEFAULT 'rascunho'::status_guia,
    tipo tipo_guia NOT NULL,
    quantidade_autorizada int,
    quantidade_executada int DEFAULT 0,
    motivo_negacao text,
    codigo_servico text,
    descricao_servico text,
    quantidade int DEFAULT 1,
    observacoes text,
    dados_autorizacao jsonb DEFAULT '{}'::jsonb,
    historico_status jsonb DEFAULT '[]'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    UNIQUE(numero_guia)
);

-- 4. Terceira camada - Corrigindo a ordem de criação de tabelas (fichas agora está depois de agendamentos)
CREATE TABLE IF NOT EXISTS fichas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_ficha text NOT NULL,
    guia_id uuid REFERENCES guias(id),
    agendamento_id uuid REFERENCES agendamentos(id),
    numero_guia text NOT NULL,
    paciente_nome text NOT NULL,
    paciente_carteirinha text NOT NULL,
    paciente_id UUID NULL REFERENCES pacientes(id), -- Campo Adicionado - Fase 4.3 Plano
    arquivo_digitalizado text,
    storage_id uuid REFERENCES storage(id),
    status status_ficha DEFAULT 'pendente'::status_ficha,
    data_atendimento date NOT NULL,
    total_sessoes integer DEFAULT 1,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    UNIQUE(id, codigo_ficha),
    CONSTRAINT fk_guia_numero FOREIGN KEY (numero_guia) REFERENCES guias(numero_guia)
);

-- Adiciona um índice único parcial para garantir unicidade do codigo_ficha quando não excluído
CREATE UNIQUE INDEX IF NOT EXISTS idx_fichas_codigo_ficha_unique 
ON fichas (codigo_ficha) 
WHERE deleted_at IS NULL;

-- 5. Quarta camada
CREATE TABLE IF NOT EXISTS sessoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    ficha_id uuid REFERENCES fichas(id) ON DELETE CASCADE,
    guia_id uuid REFERENCES guias(id),
    numero_guia text,
    agendamento_id UUID NULL REFERENCES agendamentos(id), -- Campo Adicionado - Fase 4.1 Plano
    data_sessao date NOT NULL,
    hora_inicio time,
    hora_fim time,
    profissional_id uuid REFERENCES usuarios(id),
    assinatura_paciente text,
    assinatura_profissional text,
    status status_sessao DEFAULT 'pendente'::status_sessao,
    observacoes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    codigo_ficha text, -- Campo adicionado para denormalização e consulta
    codigo_ficha_temp boolean DEFAULT true, -- Indica se o codigo_ficha é temporário
    ordem_execucao INTEGER NULL -- Campo adicionado - Fase 1 Plano
    -- link_manual_necessario foi removido daqui - Fase 1 Plano
);

-- 6. Quinta camada
CREATE TABLE IF NOT EXISTS execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    guia_id uuid REFERENCES guias(id),
    sessao_id uuid REFERENCES sessoes(id) ON DELETE SET NULL, -- Permitir nulo para execuções sem sessão vinculada
    agendamento_id UUID NULL REFERENCES agendamentos(id), -- Campo Adicionado - Fase 4.2 Plano
    data_execucao date NOT NULL,
    data_atendimento date,
    paciente_nome text,
    paciente_carteirinha text,
    numero_guia text,
    codigo_ficha text, -- Pode ser preenchido pela sessão vinculada ou ser temporário
    codigo_ficha_temp boolean DEFAULT true, -- Indica se o codigo_ficha é temporário (não vinculado a uma sessão)
    origem text, -- Ex: 'unimed_scraping', 'sistema_interno'
    profissional_executante text,
    conselho_profissional text,
    numero_conselho text,
    uf_conselho text,
    codigo_cbo text,
    status_biometria status_biometria DEFAULT 'nao_verificado'::status_biometria,
    observacoes text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    deleted_at timestamptz,
    ordem_execucao INTEGER NULL, -- Campo adicionado - Fase 1 Plano
    link_manual_necessario BOOLEAN DEFAULT FALSE -- Campo adicionado - Fase 1 Plano (confirmado aqui)
);

CREATE TABLE IF NOT EXISTS divergencias (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia text NOT NULL,
    tipo tipo_divergencia NOT NULL,
    descricao text,
    paciente_nome text,
    codigo_ficha text,
    data_execucao date,
    data_atendimento date,
    carteirinha text,
    prioridade text DEFAULT 'MEDIA',
    status status_divergencia DEFAULT 'pendente',
    data_identificacao timestamptz DEFAULT now(),
    data_resolucao timestamptz,
    resolvido_por uuid REFERENCES usuarios(id),
    detalhes jsonb,
    ficha_id uuid REFERENCES fichas(id),
    execucao_id uuid REFERENCES execucoes(id) ON DELETE SET NULL,
    sessao_id uuid REFERENCES sessoes(id),
    paciente_id uuid REFERENCES pacientes(id) ON DELETE CASCADE,
    tentativas_resolucao integer DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    CONSTRAINT fk_divergencias_guia_numero FOREIGN KEY (numero_guia) REFERENCES guias(numero_guia)
);

CREATE TABLE IF NOT EXISTS auditoria_execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_execucao timestamptz NOT NULL,
    data_inicial date,
    data_final date,
    total_protocolos integer DEFAULT 0,
    total_divergencias integer DEFAULT 0,
    total_fichas integer DEFAULT 0,
    total_guias integer DEFAULT 0,
    total_resolvidas integer DEFAULT 0,
    total_execucoes integer DEFAULT 0,
    divergencias_por_tipo jsonb,
    metricas_adicionais jsonb,
    status text DEFAULT 'em_andamento',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id)
);

-- Criação da tabela simplificada para faturamento (sem depender de tabelas faltantes)
CREATE TABLE IF NOT EXISTS atendimentos_faturamento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_atendimento UUID REFERENCES agendamentos(id),
    carteirinha VARCHAR(255),
    paciente_nome VARCHAR(255),
    data_atendimento DATE,
    hora_inicial TIME,
    id_profissional UUID REFERENCES usuarios(id),
    profissional_nome VARCHAR(255),
    status VARCHAR(50) CHECK (status = 'confirmado'),
    codigo_faturamento VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabela para controlar importações de pacientes
CREATE TABLE IF NOT EXISTS controle_importacao_pacientes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    ultima_data_registro_importada timestamptz,
    ultima_data_atualizacao_importada timestamptz,
    quantidade_registros_importados integer,
    quantidade_registros_atualizados integer,
    timestamp_importacao timestamptz DEFAULT now(),
    usuario_id uuid REFERENCES usuarios(id),
    observacoes text
);

-- Tabela para armazenar os dados de atendimentos importados do faturamento
CREATE TABLE IF NOT EXISTS atendimentos_faturamento (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_atendimento integer NOT NULL,
    id_profissional integer NOT NULL,
    data_atendimento date,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id)
);

-- ================ TABELAS DO SISTEMA ABA =================

-- Tabela de profissões (ws_profissoes)
CREATE TABLE IF NOT EXISTS profissoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profissao_id VARCHAR(255) UNIQUE,
    profissao_name VARCHAR(255) NOT NULL,
    profissao_status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);

-- Tabela de locais (ps_locales)
CREATE TABLE IF NOT EXISTS locais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    local_id VARCHAR(255) UNIQUE,
    local_nome VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);
COMMENT ON COLUMN locais.local_id IS 'ID original da tabela ps_locales no MySQL';

-- Tabela para salas (ps_care_rooms)
CREATE TABLE IF NOT EXISTS salas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id VARCHAR(255) UNIQUE,
    room_local_id VARCHAR(255),
    room_name VARCHAR(255),
    room_description TEXT NULL,
    room_type INTEGER NULL,
    room_status INTEGER NULL,
    room_registration_date TIMESTAMPTZ NULL,
    room_lastupdate TIMESTAMPTZ NULL,
    multiple BOOLEAN NULL,
    room_capacidade INTEGER NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);
COMMENT ON COLUMN salas.room_id IS 'ID original (int) da tabela ps_care_rooms no MySQL';
COMMENT ON COLUMN salas.room_local_id IS 'ID original do local (int) associado a esta sala no MySQL';

-- Tabela de usuários do sistema Aba (ws_users)
CREATE TABLE IF NOT EXISTS usuarios_aba (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE,
    user_name VARCHAR(255) NOT NULL,
    user_lastname VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);

-- Recriar tabela usuarios_profissoes (com referência corrigida)
CREATE TABLE IF NOT EXISTS usuarios_profissoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_aba_id UUID NOT NULL REFERENCES usuarios_aba(id) ON DELETE CASCADE, -- Referencia usuarios_aba
    profissao_id UUID NOT NULL REFERENCES profissoes(id) ON DELETE CASCADE, -- Referencia profissoes
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ,
    UNIQUE(usuario_aba_id, profissao_id)
);


-- Tabela de relação agendamentos-profissionais (ps_schedule_professionals)
/* CREATE TABLE IF NOT EXISTS agendamentos_profissionais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    schedule_id UUID REFERENCES agendamentos(id),
    professional_id UUID REFERENCES usuarios_aba(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ,
    UNIQUE(schedule_id, professional_id)
); */

-- Adicione estes índices na seção de INDICES
CREATE INDEX IF NOT EXISTS idx_profissoes_id ON profissoes(profissao_id);
CREATE INDEX IF NOT EXISTS idx_especialidades_id ON especialidades(especialidade_id);
CREATE INDEX IF NOT EXISTS idx_locais_id ON locais(local_id);
CREATE INDEX IF NOT EXISTS idx_salas_room_local_id ON salas(room_local_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_aba_id ON usuarios_aba(user_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_room_id ON agendamentos(schedule_room_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_local_id ON agendamentos(schedule_local_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_especialidade_id ON agendamentos(schedule_especialidade_id);

-- Adicione estes triggers na seção de TRIGGERS
DROP TRIGGER IF EXISTS update_profissoes_updated_at ON profissoes;
CREATE TRIGGER update_profissoes_updated_at
    BEFORE UPDATE ON profissoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_locais_updated_at ON locais;
CREATE TRIGGER update_locais_updated_at
    BEFORE UPDATE ON locais
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_salas_updated_at ON salas;
CREATE TRIGGER update_salas_updated_at
    BEFORE UPDATE ON salas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_usuarios_aba_updated_at ON usuarios_aba;
CREATE TRIGGER update_usuarios_aba_updated_at
    BEFORE UPDATE ON usuarios_aba
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_usuarios_profissoes_updated_at ON usuarios_profissoes;
CREATE TRIGGER update_usuarios_profissoes_updated_at
    BEFORE UPDATE ON usuarios_profissoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    
DROP TRIGGER IF EXISTS update_agendamentos_profissionais_updated_at ON agendamentos_profissionais;
CREATE TRIGGER update_agendamentos_profissionais_updated_at
    BEFORE UPDATE ON agendamentos_profissionais
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


--================ INDICES =================

-- Índices (eliminando duplicações)
CREATE INDEX IF NOT EXISTS idx_controle_importacao_datas ON controle_importacao_pacientes(ultima_data_registro_importada, ultima_data_atualizacao_importada);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_timestamp ON controle_importacao_pacientes(timestamp_importacao);

CREATE INDEX IF NOT EXISTS idx_pacientes_nome ON pacientes(nome);
CREATE INDEX IF NOT EXISTS idx_pacientes_cpf ON pacientes(cpf);
CREATE INDEX IF NOT EXISTS idx_pacientes_deleted_at ON pacientes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_pacientes_importado ON pacientes(importado);
CREATE INDEX IF NOT EXISTS idx_pacientes_id_origem ON pacientes(id_origem);
CREATE INDEX IF NOT EXISTS idx_pacientes_data_registro_origem ON pacientes(data_registro_origem);
CREATE INDEX IF NOT EXISTS idx_pacientes_data_atualizacao_origem ON pacientes(data_atualizacao_origem);

CREATE INDEX IF NOT EXISTS idx_planos_saude_nome ON planos_saude(nome);
CREATE INDEX IF NOT EXISTS idx_planos_saude_codigo ON planos_saude(codigo_operadora);
CREATE INDEX IF NOT EXISTS idx_planos_saude_deleted_at ON planos_saude(deleted_at);

CREATE INDEX IF NOT EXISTS idx_especialidades_nome ON especialidades(nome);
CREATE INDEX IF NOT EXISTS idx_especialidades_deleted_at ON especialidades(deleted_at);

CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_usuario ON usuarios_especialidades(usuario_aba_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_especialidade ON usuarios_especialidades(especialidade_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_especialidades_deleted_at ON usuarios_especialidades(deleted_at);

CREATE INDEX IF NOT EXISTS idx_procedimentos_codigo ON procedimentos(codigo);
CREATE INDEX IF NOT EXISTS idx_procedimentos_nome ON procedimentos(nome);
CREATE INDEX IF NOT EXISTS idx_procedimentos_tipo ON procedimentos(tipo);
CREATE INDEX IF NOT EXISTS idx_procedimentos_deleted_at ON procedimentos(deleted_at);

CREATE INDEX IF NOT EXISTS idx_carteirinhas_paciente ON carteirinhas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_plano ON carteirinhas(plano_saude_id);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_numero ON carteirinhas(numero_carteirinha);
CREATE INDEX IF NOT EXISTS idx_carteirinhas_deleted_at ON carteirinhas(deleted_at);

CREATE INDEX IF NOT EXISTS idx_guias_carteirinha ON guias(carteirinha_id);
CREATE INDEX IF NOT EXISTS idx_guias_procedimento ON guias(procedimento_id);
CREATE INDEX IF NOT EXISTS idx_guias_numero ON guias(numero_guia);
CREATE INDEX IF NOT EXISTS idx_guias_status ON guias(status);
CREATE INDEX IF NOT EXISTS idx_guias_deleted_at ON guias(deleted_at);

CREATE INDEX IF NOT EXISTS idx_fichas_guia ON fichas(guia_id);
CREATE INDEX IF NOT EXISTS idx_fichas_codigo ON fichas(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_fichas_numero_guia ON fichas(numero_guia);
CREATE INDEX IF NOT EXISTS idx_fichas_data ON fichas(data_atendimento);
CREATE INDEX IF NOT EXISTS idx_fichas_status ON fichas(status);
CREATE INDEX IF NOT EXISTS idx_fichas_deleted_at ON fichas(deleted_at);
CREATE INDEX IF NOT EXISTS idx_fichas_paciente_id ON fichas(paciente_id); -- Índice Adicionado - Fase 4.4 Plano

CREATE INDEX IF NOT EXISTS idx_sessoes_ficha ON sessoes(ficha_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_guia ON sessoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_data ON sessoes(data_sessao);
CREATE INDEX IF NOT EXISTS idx_sessoes_status ON sessoes(status);
CREATE INDEX IF NOT EXISTS idx_sessoes_deleted_at ON sessoes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_sessoes_agendamento_id ON sessoes(agendamento_id); -- Índice Adicionado - Fase 4.4 Plano
CREATE INDEX IF NOT EXISTS idx_sessoes_ordem_execucao ON sessoes(ordem_execucao); -- Adicionado para otimizar buscas

CREATE INDEX IF NOT EXISTS idx_divergencias_numero_guia ON divergencias(numero_guia);
CREATE INDEX IF NOT EXISTS idx_divergencias_tipo ON divergencias(tipo);
CREATE INDEX IF NOT EXISTS idx_divergencias_codigo_ficha ON divergencias(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_divergencias_status ON divergencias(status);
CREATE INDEX IF NOT EXISTS idx_divergencias_paciente ON divergencias(paciente_id);
CREATE INDEX IF NOT EXISTS idx_divergencias_ficha ON divergencias(ficha_id);
CREATE INDEX IF NOT EXISTS idx_divergencias_sessao ON divergencias(sessao_id);
CREATE INDEX IF NOT EXISTS idx_divergencias_data_identificacao ON divergencias(data_identificacao);
CREATE INDEX IF NOT EXISTS idx_divergencias_deleted_at ON divergencias(deleted_at);

CREATE INDEX IF NOT EXISTS idx_execucoes_guia ON execucoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_sessao ON execucoes(sessao_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_execucoes_numero_guia ON execucoes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_execucoes_codigo_ficha ON execucoes(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_execucoes_carteirinha ON execucoes(paciente_carteirinha);
CREATE INDEX IF NOT EXISTS idx_execucoes_profissional ON execucoes(profissional_executante);
CREATE INDEX IF NOT EXISTS idx_execucoes_status_biometria ON execucoes(status_biometria);
CREATE INDEX IF NOT EXISTS idx_execucoes_deleted_at ON execucoes(deleted_at);
CREATE INDEX IF NOT EXISTS idx_execucoes_agendamento_id ON execucoes(agendamento_id); -- Índice Adicionado - Fase 4.4 Plano
CREATE INDEX IF NOT EXISTS idx_execucoes_ordem_execucao ON execucoes(ordem_execucao); -- Adicionado para otimizar buscas
CREATE INDEX IF NOT EXISTS idx_execucoes_link_manual ON execucoes(link_manual_necessario); -- Adicionado para otimizar buscas

CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_data ON auditoria_execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_periodo ON auditoria_execucoes(data_inicial, data_final);
CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_status ON auditoria_execucoes(status);
CREATE INDEX IF NOT EXISTS idx_auditoria_execucoes_deleted_at ON auditoria_execucoes(deleted_at);

CREATE INDEX IF NOT EXISTS idx_storage_nome ON storage(nome);
CREATE INDEX IF NOT EXISTS idx_storage_tipo ON storage(tipo_referencia);
CREATE INDEX IF NOT EXISTS idx_storage_deleted_at ON storage(deleted_at);

-- Índices para agendamentos
CREATE INDEX IF NOT EXISTS idx_agendamentos_paciente ON agendamentos(paciente_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_inicio ON agendamentos(schedule_date_start);
CREATE INDEX IF NOT EXISTS idx_agendamentos_data_fim ON agendamentos(schedule_date_end);
CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(schedule_status);
CREATE INDEX IF NOT EXISTS idx_agendamentos_especialidade ON agendamentos(schedule_especialidade_id);
CREATE INDEX IF NOT EXISTS idx_agendamentos_deleted_at ON agendamentos(deleted_at);

-- Índices para atendimentos_faturamento
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_data ON atendimentos_faturamento(data_atendimento);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_profissional ON atendimentos_faturamento(id_profissional);
CREATE INDEX IF NOT EXISTS idx_atendimentos_faturamento_id_atendimento ON atendimentos_faturamento(id_atendimento);

-- Índices para tabelas de mapeamento
CREATE INDEX IF NOT EXISTS idx_mapeamento_salas_id_supabase ON mapeamento_ids_salas(id_supabase); 
CREATE INDEX IF NOT EXISTS idx_mapeamento_especialidades_id_supabase ON mapeamento_ids_especialidades(id_supabase);
CREATE INDEX IF NOT EXISTS idx_mapeamento_locais_id_supabase ON mapeamento_ids_locais(id_supabase);
CREATE INDEX IF NOT EXISTS idx_mapeamento_pagamentos_id_supabase ON mapeamento_ids_pagamentos(id_supabase);

-- Índice para o campo id_origem na tabela pacientes
CREATE INDEX IF NOT EXISTS idx_pacientes_id_origem ON pacientes(id_origem);

-- Função para enriquecer agendamentos com dados de relacionamentos
CREATE OR REPLACE FUNCTION proc_agendamento_enriquecer_dados()
RETURNS TRIGGER AS $$
DECLARE
    v_paciente_id UUID;
    v_paciente_nome TEXT;
    v_carteirinha TEXT;
    v_procedimento_nome TEXT;
BEGIN
    -- Verificar se temos um paciente_id
    IF NEW.paciente_id IS NOT NULL THEN
        -- Buscar nome do paciente
        SELECT nome INTO v_paciente_nome
        FROM pacientes
        WHERE id = NEW.paciente_id;
        
        -- Buscar carteirinha do paciente (primeira encontrada)
        SELECT numero_carteirinha INTO v_carteirinha
        FROM carteirinhas
        WHERE paciente_id = NEW.paciente_id
        LIMIT 1;
    END IF;
    
    -- Verificar se temos um procedimento_id
    IF NEW.procedimento_id IS NOT NULL THEN
        -- Buscar nome do procedimento
        SELECT nome INTO v_procedimento_nome
        FROM procedimentos
        WHERE id = NEW.procedimento_id;
    END IF;
    
    -- Adicionar o resultado como campos virtuais (sem armazenar na tabela)
    NEW.paciente_nome_virtual := v_paciente_nome;
    NEW.carteirinha_virtual := v_carteirinha;
    NEW.procedimento_nome_virtual := v_procedimento_nome;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Função para limpar dados na importação
CREATE OR REPLACE FUNCTION fn_limpar_dados_importacao_agendamentos(dados JSONB)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    -- Criar uma cópia dos dados, removendo campos que não existem na tabela
    result := dados - 'carteirinha' - 'paciente_nome' - 'cod_paciente' - 'pagamento' - 'sala' - 
              'id_profissional' - 'profissional' - 'tipo_atend' - 'qtd_sess' - 'elegibilidade' - 
              'substituicao' - 'tipo_falta' - 'id_pai' - 'codigo_faturamento' - 'id_atendimento';
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Vista para agendamentos completos com dados de relacionamentos
CREATE OR REPLACE VIEW vw_agendamentos_completos AS
SELECT 
    a.*,
    p.nome AS paciente_nome,
    c.numero_carteirinha AS carteirinha,
    proc.nome AS procedimento_nome
FROM 
    agendamentos a
LEFT JOIN 
    pacientes p ON a.paciente_id = p.id
LEFT JOIN 
    carteirinhas c ON p.id = c.paciente_id
LEFT JOIN 
    procedimentos proc ON a.procedimento_id = proc.id;

-- Comentários para documentação
COMMENT ON FUNCTION proc_agendamento_enriquecer_dados() IS 'Trigger para enriquecer agendamentos com dados de pacientes e procedimentos através de relacionamentos';
COMMENT ON FUNCTION fn_limpar_dados_importacao_agendamentos(JSONB) IS 'Função para limpar dados redundantes na importação de agendamentos';
COMMENT ON VIEW vw_agendamentos_completos IS 'Visão que inclui dados completos de agendamentos com informações de pacientes e procedimentos';

-- Tabela para controle de importação de agendamentos



-- Função para listar carteirinhas com detalhes do paciente e plano de saúde
CREATE OR REPLACE FUNCTION listar_carteirinhas_com_detalhes(
    p_offset int,
    p_limit int,
    p_search text,
    p_status text,
    p_paciente_id text,
    p_plano_saude_id text,
    p_order_column text,
    p_order_direction text
)
RETURNS TABLE (
    id uuid,
    paciente_id uuid,
    plano_saude_id uuid,
    numero_carteirinha text,
    data_validade date,
    status text,
    motivo_inativacao text,
    historico_status jsonb,
    titular boolean,
    nome_titular text,
    cpf_titular character varying,
    observacoes text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    created_by uuid,
    updated_by uuid,
    deleted_at timestamp with time zone,
    paciente_nome text,
    plano_saude_nome character varying
) 
LANGUAGE plpgsql
AS $$
#variable_conflict use_column
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.paciente_id,
        c.plano_saude_id,
        c.numero_carteirinha,
        c.data_validade,
        c.status::text,
        c.motivo_inativacao,
        COALESCE(c.historico_status, '[]'::jsonb) as historico_status,
        COALESCE(c.titular, false) as titular,
        c.nome_titular,
        c.cpf_titular,
        c.observacoes,
        c.created_at,
        c.updated_at,
        c.created_by,
        c.updated_by,
        c.deleted_at,
        p.nome as paciente_nome,
        ps.nome as plano_saude_nome
    FROM carteirinhas c
    LEFT JOIN pacientes p ON c.paciente_id = p.id AND p.deleted_at IS NULL
    LEFT JOIN planos_saude ps ON c.plano_saude_id = ps.id AND ps.deleted_at IS NULL
    WHERE c.deleted_at IS NULL
        AND (p_search IS NULL OR 
            c.numero_carteirinha ILIKE '%' || p_search || '%' OR 
            p.nome ILIKE '%' || p_search || '%' OR
            ps.nome ILIKE '%' || p_search || '%')
        AND (p_status IS NULL OR c.status::text = p_status)
        AND (p_paciente_id IS NULL OR c.paciente_id::text = p_paciente_id)
        AND (p_plano_saude_id IS NULL OR c.plano_saude_id::text = p_plano_saude_id)
    ORDER BY 
        CASE WHEN p_order_direction = 'asc' THEN
            CASE 
                WHEN p_order_column = 'numero_carteirinha' THEN c.numero_carteirinha
                WHEN p_order_column = 'data_validade' THEN c.data_validade::text
                WHEN p_order_column = 'status' THEN c.status::text
                WHEN p_order_column = 'created_at' THEN c.created_at::text
                ELSE c.numero_carteirinha
            END
        END ASC,
        CASE WHEN p_order_direction = 'desc' THEN
            CASE 
                WHEN p_order_column = 'numero_carteirinha' THEN c.numero_carteirinha
                WHEN p_order_column = 'data_validade' THEN c.data_validade::text
                WHEN p_order_column = 'status' THEN c.status::text
                WHEN p_order_column = 'created_at' THEN c.created_at::text
                ELSE c.numero_carteirinha
            END
        END DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$; 


--================ TRIGGERS =================

-- Trigger para atualização automática de updated_at
DROP TRIGGER IF EXISTS update_agendamentos_updated_at ON agendamentos;
CREATE TRIGGER update_agendamentos_updated_at
    BEFORE UPDATE ON agendamentos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_pacientes_updated_at ON pacientes;
CREATE TRIGGER update_pacientes_updated_at
    BEFORE UPDATE ON pacientes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_planos_saude_updated_at ON planos_saude;
CREATE TRIGGER update_planos_saude_updated_at
    BEFORE UPDATE ON planos_saude
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_especialidades_updated_at ON especialidades;
CREATE TRIGGER update_especialidades_updated_at
    BEFORE UPDATE ON especialidades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_usuarios_especialidades_updated_at ON usuarios_especialidades;
CREATE TRIGGER update_usuarios_especialidades_updated_at
    BEFORE UPDATE ON usuarios_especialidades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_procedimentos_updated_at ON procedimentos;
CREATE TRIGGER update_procedimentos_updated_at
    BEFORE UPDATE ON procedimentos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_carteirinhas_updated_at ON carteirinhas;
CREATE TRIGGER update_carteirinhas_updated_at
    BEFORE UPDATE ON carteirinhas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_guias_updated_at ON guias;
CREATE TRIGGER update_guias_updated_at
    BEFORE UPDATE ON guias
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_fichas_updated_at ON fichas;
CREATE TRIGGER update_fichas_updated_at
    BEFORE UPDATE ON fichas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_sessoes_updated_at ON sessoes;
CREATE TRIGGER update_sessoes_updated_at
    BEFORE UPDATE ON sessoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_atendimentos_faturamento_updated_at ON atendimentos_faturamento;
CREATE TRIGGER update_atendimentos_faturamento_updated_at
    BEFORE UPDATE ON atendimentos_faturamento
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Função simplificada para preencher atendimentos de faturamento (sem referências a tabelas faltantes)
CREATE OR REPLACE FUNCTION trigger_preencher_atendimento_faturamento()
RETURNS TRIGGER AS $$
BEGIN
    -- Alterando a condição para verificar quando o status muda para 'realizado'
    -- já que é esse status que indica que o atendimento foi efetivamente realizado
    IF NEW.schedule_status = 'realizado' AND (OLD.schedule_status IS NULL OR OLD.schedule_status <> 'realizado') THEN
        INSERT INTO atendimentos_faturamento (
            id_atendimento,
            carteirinha,
            paciente_nome,
            data_atendimento,
            hora_inicial,
            id_profissional,
            profissional_nome,
            status,
            codigo_faturamento
        )
        SELECT 
            NEW.id AS id_atendimento,
            c.numero_carteirinha AS carteirinha,
            p.nome AS paciente_nome,
            DATE(NEW.schedule_date_start) AS data_atendimento,
            TO_CHAR(NEW.schedule_date_start, 'HH24:MI:SS')::TIME AS hora_inicial,
            NEW.schedule_profissional_id AS id_profissional,
            NEW.schedule_profissional AS profissional_nome,
            'confirmado' AS status, -- Mantendo o status como 'confirmado' para atender à restrição CHECK
            NEW.schedule_codigo_faturamento AS codigo_faturamento
        FROM 
            pacientes p
        LEFT JOIN 
            carteirinhas c ON p.id = c.paciente_id
        WHERE 
            p.id_origem = NEW.schedule_pacient_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criação do trigger na tabela de agendamentos
DROP TRIGGER IF EXISTS trigger_agendamento_confirmado ON agendamentos;
CREATE TRIGGER trigger_agendamento_confirmado
    AFTER UPDATE ON agendamentos
    FOR EACH ROW
    EXECUTE FUNCTION trigger_preencher_atendimento_faturamento();

--================ TABELA DE FICHAS PENDENTES =================

-- Tabela para armazenar fichas pendentes que não puderam ser inseridas normalmente
-- devido a problemas de integridade referencial (como guias inexistentes)
CREATE TABLE IF NOT EXISTS fichas_pendentes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    storage_id uuid REFERENCES storage(id),
    dados_extraidos jsonb NOT NULL,
    status text DEFAULT 'pendente',
    arquivo_url text,
    numero_guia text,
    paciente_nome text,
    paciente_carteirinha text,
    data_atendimento date,
    total_sessoes integer,
    codigo_ficha text,
    observacoes text,
    processado boolean DEFAULT false,
    data_processamento timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    created_by uuid REFERENCES usuarios(id)
);

-- Função para inserir ficha ignorando a restrição de chave estrangeira
-- Esta função deve ser usada com cuidado, pois pode criar inconsistências no banco de dados
CREATE OR REPLACE FUNCTION public.inserir_ficha_bypass_fk(
    p_dados_ficha jsonb,
    p_storage_id uuid,
    p_ignorar_fk boolean DEFAULT false
) RETURNS uuid AS $$
DECLARE
    v_ficha_id uuid;
    v_numero_guia text;
    v_guia_id uuid;
BEGIN
    -- Se p_ignorar_fk for true, tenta criar uma guia temporária
    IF p_ignorar_fk THEN
        v_numero_guia := p_dados_ficha->>'numero_guia';
        
        -- Se a guia não existir, cria uma registro temporário
        IF v_numero_guia IS NOT NULL THEN
            -- Verifica se a guia já existe
            SELECT id INTO v_guia_id FROM guias WHERE numero_guia = v_numero_guia;
            
            IF v_guia_id IS NULL THEN
                -- Primeiro registra a ficha em fichas_pendentes para processamento posterior
                INSERT INTO fichas_pendentes (
                    storage_id,
                    dados_extraidos,
                    status,
                    arquivo_url,
                    numero_guia,
                    paciente_nome,
                    paciente_carteirinha,
                    data_atendimento,
                    total_sessoes,
                    codigo_ficha,
                    observacoes
                ) VALUES (
                    p_storage_id,
                    p_dados_ficha,
                    'pendente',
                    p_dados_ficha->>'arquivo_digitalizado',
                    v_numero_guia,
                    p_dados_ficha->>'paciente_nome',
                    p_dados_ficha->>'paciente_carteirinha',
                    (p_dados_ficha->>'data_atendimento')::date,
                    (p_dados_ficha->>'total_sessoes')::integer,
                    p_dados_ficha->>'codigo_ficha',
                    'Ficha pendente de processamento manual - guia não encontrada'
                )
                RETURNING id INTO v_ficha_id;
                
                RETURN v_ficha_id;
            END IF;
        END IF;
    END IF;
    
    -- Se não tiver que ignorar FK ou se a guia existir, insere normalmente
    INSERT INTO fichas (
        storage_id,
        codigo_ficha,
        numero_guia,
        paciente_nome,
        paciente_carteirinha,
        arquivo_digitalizado,
        status,
        data_atendimento,
        total_sessoes
    ) VALUES (
        p_storage_id,
        p_dados_ficha->>'codigo_ficha',
        p_dados_ficha->>'numero_guia',
        p_dados_ficha->>'paciente_nome',
        p_dados_ficha->>'paciente_carteirinha',
        p_dados_ficha->>'arquivo_digitalizado',
        'pendente',
        (p_dados_ficha->>'data_atendimento')::date,
        (p_dados_ficha->>'total_sessoes')::integer
    )
    RETURNING id INTO v_ficha_id;
    
    RETURN v_ficha_id;
EXCEPTION
    WHEN OTHERS THEN
        -- Em caso de erro, salva na tabela de pendentes
        INSERT INTO fichas_pendentes (
            storage_id,
            dados_extraidos,
            status,
            arquivo_url,
            numero_guia,
            paciente_nome,
            paciente_carteirinha,
            data_atendimento,
            total_sessoes,
            codigo_ficha,
            observacoes
        ) VALUES (
            p_storage_id,
            p_dados_ficha,
            'erro',
            p_dados_ficha->>'arquivo_digitalizado',
            p_dados_ficha->>'numero_guia',
            p_dados_ficha->>'paciente_nome',
            p_dados_ficha->>'paciente_carteirinha',
            (p_dados_ficha->>'data_atendimento')::date,
            (p_dados_ficha->>'total_sessoes')::integer,
            p_dados_ficha->>'codigo_ficha',
            'Erro ao processar: ' || SQLERRM
        )
        RETURNING id INTO v_ficha_id;
        
        RETURN v_ficha_id;
END;
$$ LANGUAGE plpgsql;

--================ COMENTÁRIOS =================

COMMENT ON TABLE atendimentos_faturamento IS 'Tabela para armazenar informações consolidadas de atendimentos para faturamento';
COMMENT ON COLUMN atendimentos_faturamento.id IS 'Identificador único do registro';
COMMENT ON COLUMN atendimentos_faturamento.id_atendimento IS 'Referência ao agendamento que originou este registro';
COMMENT ON COLUMN atendimentos_faturamento.carteirinha IS 'Número da carteirinha do paciente';
COMMENT ON COLUMN atendimentos_faturamento.paciente_nome IS 'Nome do paciente (desnormalizado para facilitar consultas)';
COMMENT ON COLUMN atendimentos_faturamento.data_atendimento IS 'Data em que o atendimento foi realizado';
COMMENT ON COLUMN atendimentos_faturamento.hora_inicial IS 'Hora de início do atendimento';
COMMENT ON COLUMN atendimentos_faturamento.id_profissional IS 'ID do profissional que realizou o atendimento';
COMMENT ON COLUMN atendimentos_faturamento.profissional_nome IS 'Nome do profissional (desnormalizado para facilitar consultas)';
COMMENT ON COLUMN atendimentos_faturamento.status IS 'Status do atendimento (restrito a "confirmado")';
COMMENT ON COLUMN atendimentos_faturamento.codigo_faturamento IS 'Código utilizado para faturamento junto às operadoras';
COMMENT ON COLUMN atendimentos_faturamento.created_at IS 'Data e hora de criação do registro';
COMMENT ON COLUMN atendimentos_faturamento.updated_at IS 'Data e hora da última atualização do registro';

COMMENT ON TABLE fichas_pendentes IS 'Tabela para armazenar temporariamente fichas que não puderam ser inseridas diretamente na tabela fichas';
COMMENT ON COLUMN fichas_pendentes.id IS 'Identificador único do registro';
COMMENT ON COLUMN fichas_pendentes.storage_id IS 'Referência ao registro de armazenamento do arquivo';
COMMENT ON COLUMN fichas_pendentes.dados_extraidos IS 'Dados extraídos do PDF em formato JSON';
COMMENT ON COLUMN fichas_pendentes.status IS 'Status atual da ficha pendente (pendente, processado, erro)';
COMMENT ON COLUMN fichas_pendentes.arquivo_url IS 'URL do arquivo no storage';
COMMENT ON COLUMN fichas_pendentes.numero_guia IS 'Número da guia extraído do documento';
COMMENT ON COLUMN fichas_pendentes.paciente_nome IS 'Nome do paciente extraído do documento';
COMMENT ON COLUMN fichas_pendentes.paciente_carteirinha IS 'Número da carteirinha extraído do documento';
COMMENT ON COLUMN fichas_pendentes.data_atendimento IS 'Data de atendimento extraída do documento';
COMMENT ON COLUMN fichas_pendentes.total_sessoes IS 'Total de sessões extraído do documento';
COMMENT ON COLUMN fichas_pendentes.codigo_ficha IS 'Código da ficha extraído do documento';
COMMENT ON COLUMN fichas_pendentes.observacoes IS 'Observações sobre a ficha pendente';
COMMENT ON COLUMN fichas_pendentes.processado IS 'Indica se a ficha já foi processada';
COMMENT ON COLUMN fichas_pendentes.data_processamento IS 'Data e hora em que a ficha foi processada';
COMMENT ON COLUMN fichas_pendentes.created_at IS 'Data e hora de criação do registro';
COMMENT ON COLUMN fichas_pendentes.updated_at IS 'Data e hora da última atualização do registro';
COMMENT ON COLUMN fichas_pendentes.created_by IS 'Usuário que criou o registro';

COMMENT ON FUNCTION inserir_ficha_bypass_fk(jsonb, uuid, boolean) IS 'Função para inserir fichas ignorando restrições de chave estrangeira ou salvando como pendentes';

COMMENT ON COLUMN pacientes.id_origem IS 'Código opcional para vinculação com sistemas externos (antigo codigo_aba)';

--================ CONFIGURAÇÕES DE SEGURANÇA E PERMISSÕES =================

-- IMPORTANTE: No Supabase, o RLS (Row Level Security) é habilitado por padrão
-- e pode causar problemas de "permission denied" mesmo para administradores.
-- Execute o script 00_resolver_permissoes_supabase.sql se encontrar problemas de acesso.

-- Desabilitar Row Level Security (RLS) para desenvolvimento e teste
-- Em produção, considere manter o RLS e criar políticas apropriadas
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    -- Primeiro, tentar desabilitar RLS (abordagem mais segura)
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        BEGIN
            EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY;', r.tablename);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao desabilitar RLS para tabela %: %', r.tablename, SQLERRM;
        END;
    END LOOP;
    
    -- Como alternativa, criar políticas permissivas (abordagem mais compatível com Supabase)
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        BEGIN
            -- Primeiro habilitamos RLS (necessário para políticas funcionarem)
            EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', r.tablename);
            
            -- Remover políticas existentes para evitar conflitos
            BEGIN
                EXECUTE format('DROP POLICY IF EXISTS all_access ON public.%I;', r.tablename);
            EXCEPTION WHEN OTHERS THEN
                NULL; -- Ignorar erros
            END;
            
            -- Criar política que permite acesso total
            EXECUTE format(
                'CREATE POLICY all_access ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true);', 
                r.tablename
            );
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Erro ao configurar políticas para tabela %: %', r.tablename, SQLERRM;
        END;
    END LOOP;
END $$;

-- Conceder permissões para usuários
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Configurar service_role com todos os privilégios
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Permissões para anon (necessárias para o Supabase)
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;

-- Informações úteis para diagnóstico
DO $$
BEGIN
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'CONFIGURAÇÃO DE PERMISSÕES CONCLUÍDA';
    RAISE NOTICE '====================================================';
    RAISE NOTICE 'Se encontrar "permission denied", execute:';
    RAISE NOTICE 'psql -f sql/00_resolver_permissoes_supabase.sql';
    RAISE NOTICE '====================================================';
END $$;

-- Tabela para controle de importação das tabelas auxiliares ABA
CREATE TABLE IF NOT EXISTS controle_importacao_tabelas_auxiliares (
    nome_tabela VARCHAR(255) PRIMARY KEY, -- Nome da tabela auxiliar (ex: 'profissoes', 'salas')
    ultima_importacao TIMESTAMPTZ NOT NULL, -- Timestamp da última importação bem-sucedida
    registros_importados INTEGER NULL,      -- Opcional: quantos foram importados/atualizados na última vez
    observacoes TEXT NULL                     -- Opcional: detalhes ou erros da última importação
);
COMMENT ON TABLE controle_importacao_tabelas_auxiliares IS 'Registra a última vez que cada tabela auxiliar do sistema ABA foi importada/atualizada.';

-- ================ FUNÇÕES DE VINCULAÇÃO (Refatoradas - Fase 1 Plano) ================

CREATE OR REPLACE FUNCTION vincular_sessoes_execucoes()
RETURNS VOID AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    RAISE NOTICE 'Iniciando vinculação batch de execuções e sessões...';

    -- Passo 1: Vinculação Exata (Guia + Data + Ordem)
    -- Identifica execuções que têm EXATAMENTE UMA sessão correspondente com mesma guia, data e ordem (não nula).
    WITH exatas AS (
        SELECT
            e.id AS execucao_id,
            s.id AS sessao_id,
            s.codigo_ficha AS sessao_codigo_ficha
        FROM execucoes e
        JOIN sessoes s ON e.numero_guia = s.numero_guia
                      AND e.data_execucao = s.data_sessao
                      AND e.ordem_execucao = s.ordem_execucao
        WHERE e.sessao_id IS NULL
          AND e.ordem_execucao IS NOT NULL -- Garante que a ordem existe em ambos
          AND s.ordem_execucao IS NOT NULL
          AND s.deleted_at IS NULL
          AND e.deleted_at IS NULL
    ),
    contagem_exatas AS (
        SELECT execucao_id, count(*) as num_sessoes
        FROM exatas
        GROUP BY execucao_id
    ),
    vinculos_unicos_exatos AS (
        SELECT e.execucao_id, e.sessao_id, e.sessao_codigo_ficha
        FROM exatas e
        JOIN contagem_exatas ce ON e.execucao_id = ce.execucao_id
        WHERE ce.num_sessoes = 1
    )
    UPDATE execucoes e
    SET
        sessao_id = vu.sessao_id,
        codigo_ficha = vu.sessao_codigo_ficha,
        codigo_ficha_temp = FALSE,
        link_manual_necessario = FALSE -- Vinculado com sucesso
    FROM vinculos_unicos_exatos vu
    WHERE e.id = vu.execucao_id;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'Passo 1 (Exato - com ordem): % execuções vinculadas.', updated_count;

    -- Passo 1.1: Vinculação Exata (Guia + Data, SEM Ordem)
    -- Para os casos onde a ordem é NULL em ambos, vincula se houver exatamente uma sessão.
    WITH exatas_sem_ordem AS (
        SELECT
            e.id AS execucao_id,
            s.id AS sessao_id,
            s.codigo_ficha AS sessao_codigo_ficha
        FROM execucoes e
        JOIN sessoes s ON e.numero_guia = s.numero_guia
                      AND e.data_execucao = s.data_sessao
        WHERE e.sessao_id IS NULL -- Ainda não vinculada
          AND e.ordem_execucao IS NULL -- Ordem da execução é NULL
          AND s.ordem_execucao IS NULL -- Ordem da sessão é NULL
          AND s.deleted_at IS NULL
          AND e.deleted_at IS NULL
    ),
    contagem_exatas_sem_ordem AS (
        SELECT execucao_id, count(*) as num_sessoes
        FROM exatas_sem_ordem
        GROUP BY execucao_id
    ),
    vinculos_unicos_exatos_sem_ordem AS (
        SELECT e.execucao_id, e.sessao_id, e.sessao_codigo_ficha
        FROM exatas_sem_ordem e
        JOIN contagem_exatas_sem_ordem ce ON e.execucao_id = ce.execucao_id
        WHERE ce.num_sessoes = 1
    )
    UPDATE execucoes e
    SET
        sessao_id = vu.sessao_id,
        codigo_ficha = vu.sessao_codigo_ficha,
        codigo_ficha_temp = FALSE,
        link_manual_necessario = FALSE
    FROM vinculos_unicos_exatos_sem_ordem vu
    WHERE e.id = vu.execucao_id;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'Passo 1.1 (Exato - sem ordem): % execuções vinculadas.', updated_count;

    -- Passo 2: Vinculação Tolerância+Ordem (Guia + Data +/- 1d + Ordem)
    -- Identifica execuções (ainda não vinculadas) que têm EXATAMENTE UMA sessão correspondente
    -- com mesma guia, data próxima (+/- 1 dia) e mesma ordem (não nula).
    WITH tolerancia_ordem AS (
        SELECT
            e.id AS execucao_id,
            s.id AS sessao_id,
            s.codigo_ficha AS sessao_codigo_ficha,
            abs(e.data_execucao - s.data_sessao) as diff_dias
        FROM execucoes e
        JOIN sessoes s ON e.numero_guia = s.numero_guia
                      AND abs(e.data_execucao - s.data_sessao) <= 1
                      AND e.ordem_execucao = s.ordem_execucao
        WHERE e.sessao_id IS NULL -- Ainda não vinculada
          AND e.ordem_execucao IS NOT NULL
          AND s.ordem_execucao IS NOT NULL
          AND s.deleted_at IS NULL
          AND e.deleted_at IS NULL
    ),
    contagem_tolerancia_ordem AS (
        SELECT execucao_id, count(*) as num_sessoes
        FROM tolerancia_ordem
        GROUP BY execucao_id
    ),
    vinculos_unicos_tolerancia_ordem_temp AS (
        SELECT
            to_ord.execucao_id,
            to_ord.sessao_id,
            to_ord.sessao_codigo_ficha,
            to_ord.diff_dias,
            ROW_NUMBER() OVER (PARTITION BY to_ord.execucao_id ORDER BY to_ord.diff_dias ASC) as rn -- Prioriza menor diferença de dias
        FROM tolerancia_ordem to_ord
        JOIN contagem_tolerancia_ordem cto ON to_ord.execucao_id = cto.execucao_id
        WHERE cto.num_sessoes = 1 -- Só considera se houve apenas UMA sessão candidata na janela
    ),
    vinculos_unicos_tolerancia_ordem AS (
        SELECT execucao_id, sessao_id, sessao_codigo_ficha
        FROM vinculos_unicos_tolerancia_ordem_temp
        WHERE rn = 1
    )
    UPDATE execucoes e
    SET
        sessao_id = vu.sessao_id,
        codigo_ficha = vu.sessao_codigo_ficha,
        codigo_ficha_temp = FALSE,
        link_manual_necessario = FALSE
    FROM vinculos_unicos_tolerancia_ordem vu
    WHERE e.id = vu.execucao_id;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'Passo 2 (Tolerância+Ordem): % execuções vinculadas.', updated_count;

    -- Passo 3: Vinculação Tolerância s/ Ordem (Unicidade - Guia + Data +/- 1d)
    -- Identifica execuções (ainda não vinculadas) que têm EXATAMENTE UMA sessão correspondente
    -- com mesma guia e data próxima (+/- 1 dia), independentemente da ordem.
    WITH tolerancia_sem_ordem AS (
        SELECT
            e.id AS execucao_id,
            s.id AS sessao_id,
            s.codigo_ficha AS sessao_codigo_ficha,
            abs(e.data_execucao - s.data_sessao) as diff_dias
        FROM execucoes e
        JOIN sessoes s ON e.numero_guia = s.numero_guia
                      AND abs(e.data_execucao - s.data_sessao) <= 1
        WHERE e.sessao_id IS NULL -- Ainda não vinculada
          AND s.deleted_at IS NULL
          AND e.deleted_at IS NULL
    ),
    contagem_tolerancia_sem_ordem AS (
        SELECT execucao_id, count(*) as num_sessoes
        FROM tolerancia_sem_ordem
        GROUP BY execucao_id
    ),
    vinculos_unicos_tolerancia_sem_ordem_temp AS (
       SELECT
            tso.execucao_id,
            tso.sessao_id,
            tso.sessao_codigo_ficha,
            tso.diff_dias,
            ROW_NUMBER() OVER (PARTITION BY tso.execucao_id ORDER BY tso.diff_dias ASC) as rn -- Prioriza menor diferença
        FROM tolerancia_sem_ordem tso
        JOIN contagem_tolerancia_sem_ordem ctso ON tso.execucao_id = ctso.execucao_id
        WHERE ctso.num_sessoes = 1 -- Só considera se houve apenas UMA sessão candidata na janela
    ),
    vinculos_unicos_tolerancia_sem_ordem AS (
        SELECT execucao_id, sessao_id, sessao_codigo_ficha
        FROM vinculos_unicos_tolerancia_sem_ordem_temp
        WHERE rn = 1
    )
    UPDATE execucoes e
    SET
        sessao_id = vu.sessao_id,
        codigo_ficha = vu.sessao_codigo_ficha,
        codigo_ficha_temp = FALSE,
        link_manual_necessario = FALSE
    FROM vinculos_unicos_tolerancia_sem_ordem vu
    WHERE e.id = vu.execucao_id;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'Passo 3 (Tolerância s/ Ordem - Unicidade): % execuções vinculadas.', updated_count;

    RAISE NOTICE 'Vinculação batch concluída.';
END;
$$ LANGUAGE plpgsql;


-- ... possívelmente outras funções como vincular_sessoes_mesmo_dia ...

-- ================ FIM FUNÇÕES DE VINCULAÇÃO ================

CREATE OR REPLACE FUNCTION vincular_sessoes_mesmo_dia()
RETURNS VOID AS $$
DECLARE
    grupos_ambiguos RECORD;
    updated_count INTEGER := 0;
    flagged_count INTEGER := 0;
BEGIN
    RAISE NOTICE 'Iniciando vinculação batch para casos de MÚLTIPLAS sessões/execuções no mesmo dia/guia...';

    -- Identifica grupos (guia + data) onde há múltiplas execuções e múltiplas sessões ainda não vinculadas
    FOR grupos_ambiguos IN
        WITH execucoes_nao_vinculadas AS (
            SELECT e.numero_guia, e.data_execucao, e.id as execucao_id, e.ordem_execucao
            FROM execucoes e
            WHERE e.sessao_id IS NULL
              AND e.link_manual_necessario = FALSE -- Ignora os já marcados
              AND e.deleted_at IS NULL
        ),
        sessoes_disponiveis AS (
            SELECT s.numero_guia, s.data_sessao, s.id as sessao_id, s.ordem_execucao, s.codigo_ficha
            FROM sessoes s
            LEFT JOIN execucoes e ON s.id = e.sessao_id AND e.deleted_at IS NULL
            WHERE e.id IS NULL -- Garante que a sessão não está vinculada a nenhuma execução ativa
              AND s.deleted_at IS NULL
        ),
        contagem_por_grupo AS (
            SELECT
                COALESCE(en.numero_guia, sd.numero_guia) as numero_guia,
                COALESCE(en.data_execucao, sd.data_sessao) as data,
                COUNT(DISTINCT en.execucao_id) as qtd_execucoes,
                COUNT(DISTINCT sd.sessao_id) as qtd_sessoes,
                COUNT(DISTINCT en.ordem_execucao) FILTER (WHERE en.ordem_execucao IS NOT NULL) as qtd_ordem_exec_unicas,
                COUNT(DISTINCT sd.ordem_execucao) FILTER (WHERE sd.ordem_execucao IS NOT NULL) as qtd_ordem_sess_unicas
            FROM execucoes_nao_vinculadas en
            FULL OUTER JOIN sessoes_disponiveis sd ON en.numero_guia = sd.numero_guia AND en.data_execucao = sd.data_sessao
            GROUP BY 1, 2
        )
        SELECT *
        FROM contagem_por_grupo
        WHERE qtd_execucoes > 0 AND qtd_sessoes > 0 -- Garante que há ambos no grupo
          AND (qtd_execucoes > 1 OR qtd_sessoes > 1) -- Pega apenas casos múltiplos
    LOOP
        RAISE NOTICE 'Analisando grupo: Guia %, Data %', grupos_ambiguos.numero_guia, grupos_ambiguos.data;
        RAISE NOTICE '   Execuções: %, Sessões: %, Ordens Exec Únicas: %, Ordens Sess Únicas: %', 
                     grupos_ambiguos.qtd_execucoes, grupos_ambiguos.qtd_sessoes, 
                     grupos_ambiguos.qtd_ordem_exec_unicas, grupos_ambiguos.qtd_ordem_sess_unicas;

        -- Tenta vincular automaticamente SOMENTE SE:
        -- 1. Contagem de execuções == Contagem de sessões
        -- 2. Contagem de ordens únicas de execução == Contagem total de execuções (todas têm ordem única)
        -- 3. Contagem de ordens únicas de sessão == Contagem total de sessões (todas têm ordem única)
        IF grupos_ambiguos.qtd_execucoes = grupos_ambiguos.qtd_sessoes AND
           grupos_ambiguos.qtd_ordem_exec_unicas = grupos_ambiguos.qtd_execucoes AND
           grupos_ambiguos.qtd_ordem_sess_unicas = grupos_ambiguos.qtd_sessoes
        THEN
            -- Se todas as condições são atendidas, tenta vincular pela ordem
            RAISE NOTICE '   -> Tentando vincular automaticamente por ordem...';
            WITH vinculos_por_ordem AS (
                SELECT e.id as execucao_id, s.id as sessao_id, s.codigo_ficha
                FROM execucoes e
                JOIN sessoes s ON e.numero_guia = s.numero_guia
                              AND e.data_execucao = s.data_sessao
                              AND e.ordem_execucao = s.ordem_execucao -- Vincula pela ordem
                WHERE e.numero_guia = grupos_ambiguos.numero_guia
                  AND e.data_execucao = grupos_ambiguos.data
                  AND e.sessao_id IS NULL
                  AND e.ordem_execucao IS NOT NULL
                  AND s.ordem_execucao IS NOT NULL
                  AND s.deleted_at IS NULL
                  AND e.deleted_at IS NULL
            )
            UPDATE execucoes e
            SET
                sessao_id = vpo.sessao_id,
                codigo_ficha = vpo.codigo_ficha,
                codigo_ficha_temp = FALSE,
                link_manual_necessario = FALSE
            FROM vinculos_por_ordem vpo
            WHERE e.id = vpo.execucao_id;

            GET DIAGNOSTICS updated_count = ROW_COUNT;
            RAISE NOTICE '   -> Vinculação automática por ordem: % execuções atualizadas.', updated_count;
        ELSE
            -- Se qualquer condição falhar, MARCA para revisão manual
            RAISE NOTICE '   -> Condições para vínculo automático não atendidas. Marcando para revisão manual...';
            UPDATE execucoes e
            SET link_manual_necessario = TRUE
            WHERE e.numero_guia = grupos_ambiguos.numero_guia
              AND e.data_execucao = grupos_ambiguos.data
              AND e.sessao_id IS NULL -- Apenas as não vinculadas
              AND e.deleted_at IS NULL;
              
            GET DIAGNOSTICS flagged_count = ROW_COUNT;
             RAISE NOTICE '   -> % execuções marcadas para revisão manual.', flagged_count;
        END IF;

    END LOOP;

    RAISE NOTICE 'Vinculação de casos múltiplos concluída.';
END;
$$ LANGUAGE plpgsql;

-- ================ FIM FUNÇÕES DE VINCULAÇÃO ================

-- ================ TABELAS DE UNIMED SCRAPING ================

-- Tabela para controle do status do processamento
CREATE TABLE IF NOT EXISTS processing_status (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id text UNIQUE NOT NULL,
    status text DEFAULT 'pending',
    total_guides integer DEFAULT 0,
    processed_guides integer DEFAULT 0,
    error text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    completed_at timestamptz,
    start_date text,
    end_date text,
    max_guides integer,
    retry_guides integer DEFAULT 0,
    started_at timestamptz DEFAULT now(),
    error_at timestamptz,
    last_update timestamptz,
    total_execucoes INTEGER,
    CONSTRAINT valid_status CHECK (status IN ('pending', 'iniciado', 'capturing', 'processing', 'finalizado', 'completed', 'completed_with_errors', 'error'))
);

-- Tabela temporária para fila de processamento de guias
CREATE TABLE IF NOT EXISTS guias_queue (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia text NOT NULL,
    data_atendimento_completa text NOT NULL, -- Formato dd/mm/aaaa hh:mm
    status text DEFAULT 'pending',
    task_id text REFERENCES processing_status(task_id) ON DELETE SET NULL, -- Permite NULL ou cascata
    attempts integer DEFAULT 0,
    error text,
    processed_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(numero_guia, data_atendimento_completa),
    CONSTRAINT valid_queue_status CHECK (status IN ('pending', 'processado', 'erro', 'falha_permanente'))
);

-- Tabela para armazenar dados da sessão capturada da Unimed
CREATE TABLE IF NOT EXISTS unimed_sessoes_capturadas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia text NOT NULL,
    data_atendimento_completa text NOT NULL, -- Formato dd/mm/aaaa hh:mm
    data_execucao date,
    paciente_nome text,
    paciente_carteirinha text,
    codigo_ficha text,
    profissional_executante text,
    conselho_profissional text,
    numero_conselho text,
    uf_conselho text,
    codigo_cbo text,
    origem text DEFAULT 'unimed_scraping',
    status text DEFAULT 'pendente',
    error text,
    task_id text REFERENCES processing_status(task_id) ON DELETE SET NULL, -- Permite NULL ou cascata
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    processed_at timestamptz,
    ordem_execucao INTEGER NULL,
    UNIQUE(numero_guia, data_atendimento_completa),
    CONSTRAINT valid_unimed_status CHECK (status IN ('pendente', 'processado', 'erro'))
);

-- Tabela para log de processamento das sessões da Unimed
CREATE TABLE IF NOT EXISTS unimed_log_processamento (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    sessao_id uuid REFERENCES unimed_sessoes_capturadas(id) ON DELETE CASCADE,
    execucao_id uuid REFERENCES execucoes(id) ON DELETE SET NULL, -- Permite NULL ou cascata
    status text NOT NULL,
    mensagem text,
    detalhes jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- ================ FIM TABELAS DE UNIMED SCRAPING ================

--================ TRIGGERS =================

-- Trigger para atualização automática de updated_at
DROP TRIGGER IF EXISTS update_sessoes_updated_at ON sessoes;
CREATE TRIGGER update_sessoes_updated_at
    BEFORE UPDATE ON sessoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_execucoes_updated_at ON execucoes;
CREATE TRIGGER update_execucoes_updated_at
    BEFORE UPDATE ON execucoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_unimed_sessoes_updated_at ON unimed_sessoes_capturadas;
CREATE TRIGGER update_unimed_sessoes_updated_at
    BEFORE UPDATE ON unimed_sessoes_capturadas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_unimed_log_updated_at ON unimed_log_processamento;
CREATE TRIGGER update_unimed_log_updated_at
    BEFORE UPDATE ON unimed_log_processamento
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_atendimentos_faturamento_updated_at ON atendimentos_faturamento;
CREATE TRIGGER update_atendimentos_faturamento_updated_at
    BEFORE UPDATE ON atendimentos_faturamento
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Função para inserir dados na tabela execucoes a partir das sessões capturadas da Unimed (Refatorada - Fase 1 Plano)
-- Esta função foi movida para um arquivo separado (ex: sql/05_funcoes_vinculacao.sql)
-- para melhor organização, mas a definição da função usada no scraping é incluída aqui
-- para referência, caso necessário. A versão mais atualizada deve estar no arquivo dedicado.

CREATE OR REPLACE FUNCTION inserir_execucao_unimed(p_sessao_id uuid)
RETURNS uuid AS $$
DECLARE
    nova_execucao_id uuid;
    guia_id_encontrada uuid;
    sessao_id_encontrada uuid;
    sessao_rec RECORD;
    v_log_mensagem TEXT;
    v_log_status TEXT := 'sucesso';
    v_link_manual BOOLEAN := FALSE;
    v_codigo_ficha TEXT;
    v_codigo_ficha_temp BOOLEAN := TRUE;
    v_count INTEGER;
    v_paciente_id uuid;
    v_agendamento_id uuid;
BEGIN
    -- Busca dados da sessão capturada
    SELECT usc.*, g.paciente_id as guia_paciente_id
    INTO sessao_rec
    FROM unimed_sessoes_capturadas usc
    LEFT JOIN guias g ON usc.numero_guia = g.numero_guia -- Junta com guias para pegar paciente_id
    WHERE usc.id = p_sessao_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Sessão unimed_sessoes_capturadas com ID % não encontrada', p_sessao_id;
    END IF;
    
    v_paciente_id := sessao_rec.guia_paciente_id; -- Usa o paciente_id da guia

    -- Busca guia_id na tabela guias
    SELECT id INTO guia_id_encontrada FROM guias WHERE numero_guia = sessao_rec.numero_guia LIMIT 1;

    -- Se não encontrou guia no sistema principal, loga erro e sai
    IF guia_id_encontrada IS NULL THEN
        v_log_status := 'erro';
        v_log_mensagem := 'Erro: Guia ' || sessao_rec.numero_guia || ' não encontrada na tabela principal guias.';
        INSERT INTO unimed_log_processamento (sessao_id, status, mensagem) VALUES (p_sessao_id, v_log_status, v_log_mensagem);
        UPDATE unimed_sessoes_capturadas SET status = 'erro', error = v_log_mensagem, processed_at = now() WHERE id = p_sessao_id;
        RETURN NULL;
    END IF;

    -- Tenta encontrar a SESSAO correspondente com base nos critérios
    sessao_id_encontrada := NULL;

    -- Busca Primária (Alta Confiança): Guia + Data Exata + Ordem Exata (se disponível)
    IF sessao_rec.ordem_execucao IS NOT NULL THEN
        SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id -- Tenta pegar agendamento_id da sessão
        FROM sessoes s
        WHERE s.numero_guia = sessao_rec.numero_guia
          AND s.data_sessao = sessao_rec.data_execucao
          AND s.ordem_execucao = sessao_rec.ordem_execucao
          AND s.deleted_at IS NULL
        LIMIT 1;
    ELSE -- Se ordem não veio do scraping, busca só por guia e data
        SELECT count(*) INTO v_count -- Verifica ambiguidade primeiro
        FROM sessoes s
        WHERE s.numero_guia = sessao_rec.numero_guia
          AND s.data_sessao = sessao_rec.data_execucao
          AND s.ordem_execucao IS NULL
          AND s.deleted_at IS NULL;

        IF v_count = 1 THEN -- Só busca se for única
            SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id
            FROM sessoes s
            WHERE s.numero_guia = sessao_rec.numero_guia
              AND s.data_sessao = sessao_rec.data_execucao
              AND s.ordem_execucao IS NULL -- Considera apenas sessões sem ordem definida tbm
              AND s.deleted_at IS NULL
            LIMIT 1;
        ELSIF v_count > 1 THEN
            v_link_manual := TRUE;
            v_log_mensagem := 'Vinculação Exata falhou: Ambiguidade (múltiplas sessões sem ordem na mesma data/guia).';
        END IF;
    END IF;

    IF sessao_id_encontrada IS NOT NULL THEN
        v_log_mensagem := 'Vinculado por critério Exato (Guia+Data[+Ordem]).';
    ELSE
        -- Busca Secundária (Tolerância + Ordem - se disponível): Guia + Data +/- 1 dia + Ordem Exata
        IF sessao_rec.ordem_execucao IS NOT NULL THEN
            -- Verifica quantas candidatas existem na janela
            SELECT count(*) INTO v_count
            FROM sessoes s
            WHERE s.numero_guia = sessao_rec.numero_guia
              AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
              AND s.ordem_execucao = sessao_rec.ordem_execucao
              AND s.deleted_at IS NULL;

            IF v_count = 1 THEN -- Só vincula se for única
                SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id
                FROM sessoes s
                WHERE s.numero_guia = sessao_rec.numero_guia
                  AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
                  AND s.ordem_execucao = sessao_rec.ordem_execucao
                  AND s.deleted_at IS NULL
                ORDER BY abs(s.data_sessao - sessao_rec.data_execucao) -- Pega a mais próxima (já que é única)
                LIMIT 1;
                v_log_mensagem := 'Vinculado por Tolerância+Ordem (Guia+Data+/-1d+Ordem).';
            ELSIF v_count > 1 THEN
               v_link_manual := TRUE;
               v_log_mensagem := 'Vinculação Tolerância+Ordem falhou: Ambiguidade (múltiplas sessões com mesma ordem na janela de data).';
            END IF;
        END IF;

        -- Busca Terciária (Tolerância sem Ordem - Cuidado!): Guia + Data +/- 1 dia (Só se ÚNICA)
        IF sessao_id_encontrada IS NULL THEN
            SELECT count(*) INTO v_count
            FROM sessoes s
            WHERE s.numero_guia = sessao_rec.numero_guia
              AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
              AND s.deleted_at IS NULL;

            IF v_count = 1 THEN -- Só vincula se encontrou EXATAMENTE uma
                SELECT s.id, s.agendamento_id INTO sessao_id_encontrada, v_agendamento_id
                FROM sessoes s
                WHERE s.numero_guia = sessao_rec.numero_guia
                  AND abs(s.data_sessao - sessao_rec.data_execucao) <= 1
                  AND s.deleted_at IS NULL
                LIMIT 1;
                v_log_mensagem := 'Vinculado por Tolerância s/ Ordem (Única sessão na janela Guia+Data+/-1d).';
            ELSE
                -- Se v_count = 0 ou v_count > 1, não vincula e marca para revisão manual
                v_link_manual := TRUE;
                IF v_count = 0 THEN
                    v_log_mensagem := 'Vinculação falhou: Nenhuma sessão encontrada na janela Guia+Data+/-1d.';
                ELSE
                    v_log_mensagem := 'Vinculação falhou: Ambiguidade (múltiplas sessões encontradas na janela Guia+Data+/-1d sem ordem).';
                END IF;
            END IF;
        END IF;
    END IF;

    -- Define codigo_ficha e codigo_ficha_temp baseado na vinculação
    IF sessao_id_encontrada IS NOT NULL THEN
        SELECT codigo_ficha INTO v_codigo_ficha FROM sessoes WHERE id = sessao_id_encontrada;
        v_codigo_ficha_temp := FALSE; -- Vinculação bem sucedida
    ELSE
        v_codigo_ficha := sessao_rec.codigo_ficha; -- Usa o código temporário do scraping
        v_codigo_ficha_temp := TRUE;
        -- Se não vinculou a sessão, tenta buscar agendamento pelo paciente/data
        IF v_paciente_id IS NOT NULL AND sessao_rec.data_execucao IS NOT NULL THEN
             SELECT count(*) INTO v_count
             FROM agendamentos a
             WHERE a.paciente_id = v_paciente_id
               AND abs(a.data_agendamento - sessao_rec.data_execucao) <= 1; -- Tolerância de 1 dia

             IF v_count = 1 THEN -- Vincula agendamento se único
                 SELECT a.id INTO v_agendamento_id
                 FROM agendamentos a
                 WHERE a.paciente_id = v_paciente_id
                   AND abs(a.data_agendamento - sessao_rec.data_execucao) <= 1
                 LIMIT 1;
             END IF;
        END IF;
    END IF;

    -- Insere na tabela execucoes
    INSERT INTO execucoes (
        guia_id,
        sessao_id, -- Pode ser NULL se não vinculou
        agendamento_id, -- Preenche se encontrou
        data_execucao,
        data_atendimento, -- Usando a mesma data como data_atendimento por enquanto
        paciente_nome,
        paciente_carteirinha,
        numero_guia,
        codigo_ficha,
        codigo_ficha_temp,
        origem,
        profissional_executante,
        conselho_profissional,
        numero_conselho,
        uf_conselho,
        codigo_cbo,
        ordem_execucao,         -- Campo novo
        link_manual_necessario -- Campo novo
    ) VALUES (
        guia_id_encontrada,
        sessao_id_encontrada,
        v_agendamento_id,
        sessao_rec.data_execucao,
        sessao_rec.data_execucao,
        sessao_rec.paciente_nome,
        sessao_rec.paciente_carteirinha,
        sessao_rec.numero_guia,
        v_codigo_ficha,
        v_codigo_ficha_temp,
        'unimed_scraping',
        sessao_rec.profissional_executante,
        sessao_rec.conselho_profissional,
        sessao_rec.numero_conselho,
        sessao_rec.uf_conselho,
        sessao_rec.codigo_cbo,
        sessao_rec.ordem_execucao,
        v_link_manual
    )
    RETURNING id INTO nova_execucao_id;

    -- Atualiza o status da sessão capturada
    UPDATE unimed_sessoes_capturadas
    SET
        status = 'processado',
        processed_at = now()
    WHERE id = p_sessao_id;

    -- Registra log detalhado
    INSERT INTO unimed_log_processamento (
        sessao_id,
        execucao_id,
        status,
        mensagem,
        detalhes
    ) VALUES (
        p_sessao_id,
        nova_execucao_id,
        v_log_status, -- Será 'sucesso' se não houve erro de guia
        v_log_mensagem, -- Mensagem sobre a vinculação
        jsonb_build_object(
            'sessao_vinculada_id', sessao_id_encontrada,
            'agendamento_vinculado_id', v_agendamento_id,
            'link_manual_necessario', v_link_manual,
            'codigo_ficha_usado', v_codigo_ficha,
            'codigo_ficha_era_temp', v_codigo_ficha_temp
        )
    );

    RETURN nova_execucao_id;

EXCEPTION WHEN OTHERS THEN
    -- Em caso de erro inesperado, registra o log de erro
    v_log_status := 'erro';
    v_log_mensagem := 'Erro inesperado ao processar/inserir execução: ' || SQLERRM || ' | State: ' || SQLSTATE;
    INSERT INTO unimed_log_processamento (
        sessao_id,
        status,
        mensagem,
        detalhes
    ) VALUES (
        p_sessao_id,
        v_log_status,
        v_log_mensagem,
        jsonb_build_object('error', SQLERRM, 'state', SQLSTATE)
    );

    -- Atualiza o status da sessão capturada para erro
    UPDATE unimed_sessoes_capturadas
    SET
        status = 'erro',
        error = SQLERRM,
        processed_at = now()
    WHERE id = p_sessao_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ================ FIM FUNÇÕES DE VINCULAÇÃO ================

--================ ÍNDICES (Adicionando Índices do Scraping) =================

-- ... (índices existentes) ...

-- Índices para tabelas de Unimed Scraping
CREATE INDEX IF NOT EXISTS idx_processing_status_task_id ON processing_status(task_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_status ON processing_status(status);
CREATE INDEX IF NOT EXISTS idx_processing_status_dates ON processing_status(started_at, error_at, last_update);

CREATE INDEX IF NOT EXISTS idx_guias_queue_status ON guias_queue(status);
CREATE INDEX IF NOT EXISTS idx_guias_queue_task_id ON guias_queue(task_id);
CREATE INDEX IF NOT EXISTS idx_guias_queue_attempts ON guias_queue(attempts);

CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_numero_guia ON unimed_sessoes_capturadas(numero_guia);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_status ON unimed_sessoes_capturadas(status);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_datas ON unimed_sessoes_capturadas(data_execucao, processed_at);
CREATE INDEX IF NOT EXISTS idx_unimed_sessoes_task_id ON unimed_sessoes_capturadas(task_id);

CREATE INDEX IF NOT EXISTS idx_unimed_log_status ON unimed_log_processamento(status);
CREATE INDEX IF NOT EXISTS idx_unimed_log_sessao ON unimed_log_processamento(sessao_id);
CREATE INDEX IF NOT EXISTS idx_unimed_log_execucao ON unimed_log_processamento(execucao_id);

-- ... (restante dos índices existentes) ...

--================ FUNÇÕES AUXILIARES (Scraping) =================

-- Função para atualizar o timestamp last_update na tabela processing_status
CREATE OR REPLACE FUNCTION update_processing_status_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

--================ TRIGGERS =================

-- Trigger para atualização automática de updated_at

-- ... (triggers existentes para tabelas principais)

DROP TRIGGER IF EXISTS update_sessoes_updated_at ON sessoes;
CREATE TRIGGER update_sessoes_updated_at
    BEFORE UPDATE ON sessoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_execucoes_updated_at ON execucoes;
CREATE TRIGGER update_execucoes_updated_at
    BEFORE UPDATE ON execucoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Triggers para tabelas de Unimed Scraping
DROP TRIGGER IF EXISTS set_processing_status_timestamp ON processing_status;
CREATE TRIGGER set_processing_status_timestamp
    BEFORE UPDATE ON processing_status
    FOR EACH ROW
    EXECUTE FUNCTION update_processing_status_timestamp();

DROP TRIGGER IF EXISTS update_guias_queue_updated_at ON guias_queue;
CREATE TRIGGER update_guias_queue_updated_at
    BEFORE UPDATE ON guias_queue
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); -- Corrigido de PROCEDURE para FUNCTION

DROP TRIGGER IF EXISTS update_unimed_sessoes_updated_at ON unimed_sessoes_capturadas;
CREATE TRIGGER update_unimed_sessoes_updated_at
    BEFORE UPDATE ON unimed_sessoes_capturadas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); -- Corrigido de PROCEDURE para FUNCTION

DROP TRIGGER IF EXISTS update_unimed_log_updated_at ON unimed_log_processamento;
CREATE TRIGGER update_unimed_log_updated_at
    BEFORE UPDATE ON unimed_log_processamento
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); -- Corrigido de PROCEDURE para FUNCTION

DROP TRIGGER IF EXISTS update_atendimentos_faturamento_updated_at ON atendimentos_faturamento;
CREATE TRIGGER update_atendimentos_faturamento_updated_at
    BEFORE UPDATE ON atendimentos_faturamento
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ... (trigger trigger_agendamento_confirmado) ...

--================ TABELA DE FICHAS PENDENTES =================
-- ... (definição da tabela fichas_pendentes e função inserir_ficha_bypass_fk) ...

--================ COMENTÁRIOS =================
-- ... (comentários existentes) ...

--================ CONFIGURAÇÕES DE SEGURANÇA E PERMISSÕES =================
-- ... (configurações de segurança) ...

-- ================ FUNÇÕES DE VINCULAÇÃO (Refatoradas - Fase 1 Plano) ================ 
-- (Remover a definição da função inserir_execucao_unimed daqui)

CREATE OR REPLACE FUNCTION vincular_sessoes_execucoes()
-- ... (definição da função vincular_sessoes_execucoes permanece igual) ...
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION vincular_sessoes_mesmo_dia()
-- ... (definição da função vincular_sessoes_mesmo_dia permanece igual) ...
$$ LANGUAGE plpgsql;

-- REMOVER A PARTIR DAQUI --
-- Função para inserir dados na tabela execucoes a partir das sessões capturadas da Unimed (Refatorada - Fase 1 Plano)
-- Esta função foi movida para um arquivo separado (ex: sql/05_funcoes_vinculacao.sql)
-- para melhor organização, mas a definição da função usada no scraping é incluída aqui
-- para referência, caso necessário. A versão mais atualizada deve estar no arquivo dedicado.

-- CREATE OR REPLACE FUNCTION inserir_execucao_unimed(p_sessao_id uuid)
-- ... (definição completa da função que será removida) ...
-- $$ LANGUAGE plpgsql;
-- ATÉ AQUI --

-- ================ FIM DO SCRIPT ================ 
-- (Garantir que não há mais código após este ponto)