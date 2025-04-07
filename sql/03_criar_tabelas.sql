--================ TABELAS =================

-- 1. Tabelas base (sem foreign keys)
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
    deleted_at timestamptz,
    -- Colunas para mapeamento com ws_pagamentos_x_codigos_faturamento
    codigo_faturamento_id_origem INT UNIQUE, -- ID original: codigo_faturamento_id
    pagamento_id_origem INT -- ID original: pagamento_id
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
    id_origem INT, -- Referência ao ID do sistema legado ABA (ajustar tipo se necessário)
    data_registro_origem timestamptz,
    data_atualizacao_origem timestamptz
);
COMMENT ON COLUMN pacientes.id_origem IS 'Código opcional para vinculação com sistemas externos (antigo codigo_aba)';

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

-- Tabelas de Controle de Importação
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

CREATE TABLE IF NOT EXISTS controle_importacao_tabelas_auxiliares (
    nome_tabela VARCHAR(255) PRIMARY KEY, -- Nome da tabela auxiliar (ex: 'profissoes', 'salas')
    ultima_importacao TIMESTAMPTZ NOT NULL, -- Timestamp da última importação bem-sucedida
    registros_importados INTEGER NULL,      -- Opcional: quantos foram importados/atualizados na última vez
    observacoes TEXT NULL                     -- Opcional: detalhes ou erros da última importação
);
COMMENT ON TABLE controle_importacao_tabelas_auxiliares IS 'Registra a última vez que cada tabela auxiliar do sistema ABA foi importada/atualizada.';

-- Tabelas do Sistema ABA (importadas/referenciadas)
CREATE TABLE IF NOT EXISTS profissoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profissao_id VARCHAR(255) UNIQUE, -- ID original do sistema ABA
    profissao_name VARCHAR(255) NOT NULL,
    profissao_status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS locais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    local_id VARCHAR(255) UNIQUE, -- ID original do sistema ABA
    local_nome VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ DEFAULT NULL
);
COMMENT ON COLUMN locais.local_id IS 'ID original da tabela ps_locales no MySQL';

CREATE TABLE IF NOT EXISTS salas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_id VARCHAR(255) UNIQUE, -- ID original (int) do sistema ABA
    room_local_id VARCHAR(255), -- FK para locais.local_id (no sistema ABA)
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

CREATE TABLE IF NOT EXISTS usuarios_aba (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE, -- ID original do sistema ABA
    user_name VARCHAR(255) NOT NULL,
    user_lastname VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ
);

-- 2. Tabelas com dependências (primeira camada)
CREATE TABLE IF NOT EXISTS usuarios_especialidades (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_aba_id uuid NOT NULL REFERENCES usuarios_aba(id) ON DELETE CASCADE,
    especialidade_id uuid NOT NULL REFERENCES especialidades(id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS usuarios_profissoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_aba_id UUID NOT NULL REFERENCES usuarios_aba(id) ON DELETE CASCADE,
    profissao_id UUID NOT NULL REFERENCES profissoes(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ,
    UNIQUE(usuario_aba_id, profissao_id)
);

-- Tabela de Agendamentos (depende de usuarios_aba, pacientes, procedimentos, salas, locais, especialidades)
CREATE TABLE IF NOT EXISTS agendamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Campos originais do MySQL (manter compatibilidade)
    schedule_id VARCHAR(255), -- ID original
    schedule_date_start TIMESTAMPTZ,
    schedule_date_end TIMESTAMPTZ,
    schedule_pacient_id VARCHAR(255), -- FK para pacientes.id_origem (lógica na importação)
    schedule_pagamento_id VARCHAR(255),
    schedule_pagamento TEXT, -- Nome do plano (ver NOTA DE IMPLEMENTAÇÃO)
    schedule_profissional_id UUID REFERENCES usuarios_aba(id), -- FK para usuario ABA original
    schedule_profissional TEXT,
    schedule_unidade VARCHAR(50),
    schedule_room_id VARCHAR(255), -- FK para salas.room_id (lógica na importação)
    schedule_qtd_sessions INTEGER DEFAULT 1,
    schedule_status VARCHAR(50), -- Status do sistema ABA
    schedule_room_rent_value DECIMAL(10,2),
    schedule_fixed BOOLEAN DEFAULT FALSE,
    schedule_especialidade_id VARCHAR(255), -- FK para especialidades.especialidade_id (lógica na importação)
    schedule_local_id VARCHAR(255), -- FK para locais.local_id (lógica na importação)
    schedule_saldo_sessoes INTEGER DEFAULT 0,
    schedule_elegibilidade BOOLEAN DEFAULT TRUE,
    schedule_falha_do_profissional BOOLEAN DEFAULT FALSE,
    schedule_parent_id VARCHAR(255), -- ID original do agendamento pai
    schedule_registration_date TIMESTAMPTZ,
    schedule_lastupdate TIMESTAMPTZ,
    parent_id UUID REFERENCES agendamentos(id), -- FK para o agendamento pai no Supabase
    schedule_codigo_faturamento TEXT,
    
    -- Campos novos/principais para o sistema
    paciente_id UUID REFERENCES pacientes(id), -- FK para pacientes no Supabase
    procedimento_id UUID REFERENCES procedimentos(id), -- FK para procedimentos no Supabase
    data_agendamento DATE,
    hora_inicio TIME,
    hora_fim TIME,
    status VARCHAR(50), -- Status principal (ex: agendado, cancelado, realizado)
    observacoes TEXT,
    
    -- Campos de auditoria
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES usuarios(id),
    updated_by UUID REFERENCES usuarios(id),
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    
    -- Campos para rastreamento de importação
    importado BOOLEAN DEFAULT FALSE,
    id_origem VARCHAR(255), -- ID original do agendamento no sistema ABA
    data_registro_origem TIMESTAMPTZ,
    data_atualizacao_origem TIMESTAMPTZ,

    -- Colunas FK para Supabase (preenchidas via importação/mapeamento)
    sala_id_supabase UUID NULL REFERENCES public.salas(id) ON DELETE SET NULL ON UPDATE CASCADE,
    local_id_supabase UUID NULL REFERENCES public.locais(id) ON DELETE SET NULL ON UPDATE CASCADE,
    especialidade_id_supabase UUID NULL REFERENCES public.especialidades(id) ON DELETE SET NULL ON UPDATE CASCADE
);
COMMENT ON COLUMN public.agendamentos.sala_id_supabase IS 'FK para a tabela salas (importada do sistema ABA)';
COMMENT ON COLUMN public.agendamentos.local_id_supabase IS 'FK para a tabela locais (importada do sistema ABA)';
COMMENT ON COLUMN public.agendamentos.especialidade_id_supabase IS 'FK para a tabela especialidades (importada do sistema ABA)';
COMMENT ON COLUMN public.agendamentos.id_origem IS 'ID original do agendamento na tabela ps_schedule do MySQL';

-- 3. Tabelas com dependências (segunda camada)
CREATE TABLE IF NOT EXISTS guias (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    carteirinha_id uuid NOT NULL REFERENCES carteirinhas(id) ON DELETE RESTRICT,
    paciente_id uuid NOT NULL REFERENCES pacientes(id),
    procedimento_id uuid NOT NULL REFERENCES procedimentos(id),
    numero_guia text NOT NULL UNIQUE,
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
    deleted_at timestamptz
);

-- 4. Tabelas com dependências (terceira camada)
CREATE TABLE IF NOT EXISTS fichas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_ficha text NOT NULL,
    guia_id uuid REFERENCES guias(id) ON DELETE SET NULL, -- Permite guia nula temporariamente?
    agendamento_id uuid REFERENCES agendamentos(id) ON DELETE SET NULL,
    numero_guia text NOT NULL, -- Mantido para referência, mas FK principal é guia_id
    paciente_nome text NOT NULL, -- Denormalizado
    paciente_carteirinha text NOT NULL, -- Denormalizado
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
    updated_by uuid REFERENCES usuarios(id)
);
-- Cria o índice único parcial para garantir unicidade de codigo_ficha apenas para registros ativos
CREATE UNIQUE INDEX IF NOT EXISTS idx_fichas_codigo_ficha_unico_ativo ON fichas (codigo_ficha) WHERE deleted_at IS NULL;

-- Nota: Removida a FK direta em numero_guia para permitir guias não existentes temporariamente?
-- Se a regra é que a guia DEVE existir, usar: CONSTRAINT fk_guia_numero FOREIGN KEY (numero_guia) REFERENCES guias(numero_guia)

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
COMMENT ON TABLE fichas_pendentes IS 'Tabela para armazenar temporariamente fichas que não puderam ser inseridas diretamente na tabela fichas';

-- 5. Tabelas com dependências (quarta camada)
CREATE TABLE IF NOT EXISTS sessoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    ficha_id uuid REFERENCES fichas(id) ON DELETE CASCADE,
    guia_id uuid REFERENCES guias(id) ON DELETE SET NULL,
    numero_guia text, -- Denormalizado
    agendamento_id UUID NULL REFERENCES agendamentos(id) ON DELETE SET NULL, -- Campo Adicionado - Fase 4.1 Plano
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
);

-- 6. Tabelas com dependências (quinta camada)
CREATE TABLE IF NOT EXISTS execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    guia_id uuid REFERENCES guias(id) ON DELETE SET NULL,
    sessao_id uuid REFERENCES sessoes(id) ON DELETE SET NULL, -- Vinculo com a sessão da ficha
    agendamento_id UUID NULL REFERENCES agendamentos(id) ON DELETE SET NULL, -- Campo Adicionado - Fase 4.2 Plano
    paciente_id UUID NULL REFERENCES pacientes(id), -- Campo Adicionado - Fase 4.6 Plano
    data_execucao date NOT NULL,
    data_atendimento date, -- Data do atendimento registrada na Unimed/Origem
    paciente_nome text, -- Denormalizado da Unimed/Origem
    paciente_carteirinha text, -- Denormalizado da Unimed/Origem
    numero_guia text, -- Denormalizado da Unimed/Origem
    codigo_ficha text, -- Pode ser preenchido pela sessão vinculada ou ser temporário
    codigo_ficha_temp boolean DEFAULT true, -- Indica se o codigo_ficha é temporário (não vinculado a uma sessão)
    origem text, -- Ex: 'unimed_scraping', 'sistema_interno', 'manual'
    profissional_executante text, -- Denormalizado da Unimed/Origem
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
    link_manual_necessario BOOLEAN DEFAULT FALSE -- Campo adicionado - Fase 1 Plano
);

CREATE TABLE IF NOT EXISTS atendimentos_faturamento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_atendimento UUID REFERENCES agendamentos(id) ON DELETE SET NULL,
    agendamento_id_origem VARCHAR(255), -- ID original do agendamento no ABA
    execucao_id UUID REFERENCES execucoes(id) ON DELETE SET NULL,
    sessao_id UUID REFERENCES sessoes(id) ON DELETE SET NULL,
    ficha_id UUID REFERENCES fichas(id) ON DELETE SET NULL,
    carteirinha VARCHAR(255),
    paciente_id UUID REFERENCES pacientes(id),
    paciente_nome VARCHAR(255),
    data_atendimento DATE,
    hora_inicial TIME,
    hora_final TIME,
    id_profissional UUID REFERENCES usuarios(id),
    profissional_nome VARCHAR(255),
    procedimento_id UUID REFERENCES procedimentos(id),
    codigo_procedimento VARCHAR(20),
    nome_procedimento TEXT,
    status VARCHAR(50) DEFAULT 'pendente', -- Ex: pendente, confirmado, faturado, erro
    codigo_faturamento VARCHAR(255),
    valor_faturado DECIMAL(10,2),
    lote_faturamento_id UUID, -- Referência futura a um lote
    observacoes_faturamento TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
COMMENT ON TABLE atendimentos_faturamento IS 'Tabela consolidada para informações de faturamento, vinculando agendamentos, execuções e sessões.';

CREATE TABLE IF NOT EXISTS divergencias (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia text NOT NULL, -- FK para guias.numero_guia (pode não existir se for divergência de guia)
    tipo tipo_divergencia NOT NULL,
    descricao text,
    paciente_id uuid REFERENCES pacientes(id) ON DELETE SET NULL,
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
    ficha_id uuid REFERENCES fichas(id) ON DELETE SET NULL,
    execucao_id uuid REFERENCES execucoes(id) ON DELETE SET NULL,
    sessao_id uuid REFERENCES sessoes(id) ON DELETE SET NULL,
    tentativas_resolucao integer DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id)
);
-- Nota: Removida FK direta para guias.numero_guia para permitir divergências de guias inexistentes.

CREATE TABLE IF NOT EXISTS auditoria_execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    data_execucao timestamptz NOT NULL, -- Timestamp da execução da auditoria
    data_inicial date, -- Período analisado
    data_final date,   -- Período analisado
    total_protocolos integer DEFAULT 0,
    total_divergencias integer DEFAULT 0,
    total_fichas integer DEFAULT 0,
    total_guias integer DEFAULT 0,
    total_resolvidas integer DEFAULT 0,
    total_execucoes integer DEFAULT 0,
    divergencias_por_tipo jsonb,
    metricas_adicionais jsonb,
    status text DEFAULT 'em_andamento', -- Ex: em_andamento, concluido, erro
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id)
);

-- Tabelas de Unimed Scraping
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

-- Tabela para Tipos de Pagamento (Importada do ABA - ws_pagamentos)
CREATE TABLE IF NOT EXISTS tipo_pagamento (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    id_origem INT UNIQUE, -- ID original: pagamento_id
    nome TEXT NOT NULL,
    carteirinha_obrigatoria BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id)
);
COMMENT ON TABLE tipo_pagamento IS 'Tabela para armazenar os tipos de pagamento importados do sistema legado ABA (ws_pagamentos).';
COMMENT ON COLUMN tipo_pagamento.id_origem IS 'ID original da tabela ws_pagamentos no MySQL.';

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