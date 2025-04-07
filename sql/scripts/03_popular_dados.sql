-- Criar tipo enumerado para tipo de procedimento se não existir
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

-- Criar tipo status_ficha se não existir
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

-- Criar tipo status_sessao se não existir
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

-- Criar tipo status_biometria se não existir
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

-- Criar tabela de procedimentos se não existir
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
    created_by uuid REFERENCES auth.users(id),
    updated_by uuid REFERENCES auth.users(id),
    deleted_at timestamptz
);

-- Criar tabela de fichas se não existir
CREATE TABLE IF NOT EXISTS fichas (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_ficha text NOT NULL,
    guia_id uuid REFERENCES guias(id),
    numero_guia text NOT NULL,
    paciente_nome text NOT NULL,
    paciente_carteirinha text NOT NULL,
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
    CONSTRAINT fk_guia FOREIGN KEY (guia_id, numero_guia) 
        REFERENCES guias(id, numero_guia)
);

-- Criar tabela de sessoes se não existir
CREATE TABLE IF NOT EXISTS sessoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    ficha_id uuid REFERENCES fichas(id) ON DELETE CASCADE,
    guia_id uuid REFERENCES guias(id),
    data_sessao date NOT NULL,
    possui_assinatura boolean DEFAULT false,
    procedimento_id uuid REFERENCES procedimentos(id),
    profissional_executante text,
    status status_sessao DEFAULT 'pendente',
    numero_guia text NOT NULL,
    codigo_ficha text NOT NULL,
    origem text DEFAULT 'manual',
    ip_origem inet,
    ordem_execucao integer,
    status_biometria status_biometria DEFAULT 'nao_verificado',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES usuarios(id),
    updated_by uuid REFERENCES usuarios(id),
    CONSTRAINT fk_ficha FOREIGN KEY (ficha_id, codigo_ficha) 
        REFERENCES fichas(id, codigo_ficha)
);

-- Criar tabela de execucoes se não existir
CREATE TABLE IF NOT EXISTS execucoes (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    guia_id uuid REFERENCES guias(id) ON DELETE CASCADE,
    sessao_id uuid REFERENCES sessoes(id),
    data_execucao date NOT NULL,
    data_atendimento date,
    paciente_nome text NOT NULL,
    paciente_carteirinha text NOT NULL,
    numero_guia text NOT NULL,
    codigo_ficha text NOT NULL,
    codigo_ficha_temp boolean DEFAULT false,
    usuario_executante uuid REFERENCES auth.users(id),
    origem text DEFAULT 'manual',
    ip_origem text,
    ordem_execucao integer,
    status_biometria status_biometria DEFAULT 'nao_verificado',
    conselho_profissional text,
    numero_conselho text,
    uf_conselho text,
    codigo_cbo text,
    profissional_executante text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    deleted_at timestamptz,
    created_by uuid REFERENCES auth.users(id),
    updated_by uuid REFERENCES auth.users(id)
);

-- Criar índices para procedimentos se não existirem
CREATE INDEX IF NOT EXISTS idx_procedimentos_codigo ON procedimentos(codigo);
CREATE INDEX IF NOT EXISTS idx_procedimentos_nome ON procedimentos(nome);
CREATE INDEX IF NOT EXISTS idx_procedimentos_tipo ON procedimentos(tipo);
CREATE INDEX IF NOT EXISTS idx_procedimentos_deleted_at ON procedimentos(deleted_at);

-- Criar índices para fichas
CREATE INDEX IF NOT EXISTS idx_fichas_guia ON fichas(guia_id);
CREATE INDEX IF NOT EXISTS idx_fichas_codigo ON fichas(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_fichas_numero_guia ON fichas(numero_guia);
CREATE INDEX IF NOT EXISTS idx_fichas_data ON fichas(data_atendimento);
CREATE INDEX IF NOT EXISTS idx_fichas_status ON fichas(status);
CREATE INDEX IF NOT EXISTS idx_fichas_deleted_at ON fichas(deleted_at);

-- Criar índices para sessoes
CREATE INDEX IF NOT EXISTS idx_sessoes_ficha ON sessoes(ficha_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_guia ON sessoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_sessoes_data ON sessoes(data_sessao);
CREATE INDEX IF NOT EXISTS idx_sessoes_status ON sessoes(status);
CREATE INDEX IF NOT EXISTS idx_sessoes_deleted_at ON sessoes(deleted_at);

-- Criar índices para execucoes
CREATE INDEX IF NOT EXISTS idx_execucoes_guia ON execucoes(guia_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_sessao ON execucoes(sessao_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_data ON execucoes(data_execucao);
CREATE INDEX IF NOT EXISTS idx_execucoes_numero_guia ON execucoes(numero_guia);
CREATE INDEX IF NOT EXISTS idx_execucoes_codigo_ficha ON execucoes(codigo_ficha);
CREATE INDEX IF NOT EXISTS idx_execucoes_status ON execucoes(status_biometria);
CREATE INDEX IF NOT EXISTS idx_execucoes_deleted_at ON execucoes(deleted_at);

-- Habilitar RLS para procedimentos se ainda não estiver habilitado
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_tables
        WHERE tablename = 'procedimentos'
        AND rowsecurity = true
    ) THEN
        ALTER TABLE procedimentos ENABLE ROW LEVEL SECURITY;
    END IF;
END$$;

-- Habilitar RLS para fichas
ALTER TABLE fichas ENABLE ROW LEVEL SECURITY;

-- Habilitar RLS para sessoes
ALTER TABLE sessoes ENABLE ROW LEVEL SECURITY;

-- Habilitar RLS para execucoes
ALTER TABLE execucoes ENABLE ROW LEVEL SECURITY;

-- Criar políticas de segurança para execucoes
CREATE POLICY "Usuários podem ver execuções não deletadas" ON execucoes
    FOR SELECT USING (deleted_at IS NULL);

CREATE POLICY "Usuários autenticados podem inserir execuções" ON execucoes
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Usuários autenticados podem atualizar execuções" ON execucoes
    FOR UPDATE TO authenticated
    USING (deleted_at IS NULL)
    WITH CHECK (true);

-- Limpar dados existentes mantendo a estrutura
DO $$
BEGIN
    -- Desativa as verificações de chave estrangeira temporariamente
    SET session_replication_role = 'replica';

    -- Limpa as tabelas mantendo a estrutura
    TRUNCATE TABLE guias CASCADE;
    TRUNCATE TABLE procedimentos CASCADE;
    TRUNCATE TABLE carteirinhas CASCADE;
    TRUNCATE TABLE planos_saude CASCADE;
    TRUNCATE TABLE pacientes CASCADE;
    TRUNCATE TABLE fichas CASCADE;
    TRUNCATE TABLE sessoes CASCADE;

    -- Reativa as verificações de chave estrangeira
    SET session_replication_role = 'origin';
END$$;

-- Popular dados de exemplo
DO $$
DECLARE
    v_timestamp text := to_char(current_timestamp, 'YYYYMMDD_HH24MISS');
    v_admin_auth_id uuid;
    v_medico_auth_id uuid;
    v_fisio_auth_id uuid;
    v_operador_auth_id uuid;
    v_medico_id uuid;
    v_fisio_id uuid;
    v_procedimentos_ids uuid[];
    v_carteirinhas_ids uuid[];
    v_sessoes_ids uuid[];
BEGIN
    -- Recuperar IDs dos usuários já existentes
    SELECT id, auth_user_id INTO v_admin_auth_id, v_admin_auth_id 
    FROM usuarios WHERE email = 'admin@clinica.com';
    
    SELECT id, auth_user_id INTO v_medico_id, v_medico_auth_id 
    FROM usuarios WHERE email = 'joao.silva@clinica.com';
    
    SELECT id, auth_user_id INTO v_fisio_id, v_fisio_auth_id 
    FROM usuarios WHERE email = 'maria.santos@clinica.com';
    
    SELECT id, auth_user_id INTO v_operador_auth_id 
    FROM usuarios WHERE email = 'jose.operador@clinica.com';

    -- Criar procedimentos usando auth_user_id
    WITH procedimentos_inseridos AS (
        INSERT INTO procedimentos (
            codigo,
            nome,
            descricao,
            tipo,
            valor,
            valor_filme,
            valor_operacional,
            valor_total,
            tempo_medio_execucao,
            requer_autorizacao,
            observacoes,
            created_by,
            updated_by
        ) VALUES 
        (
            'CONS001',
            'Consulta Médica',
            'Consulta médica padrão',
            'consulta',
            150.00,
            0.00,
            0.00,
            150.00,
            '00:30:00',
            false,
            'Consulta padrão',
            v_admin_auth_id,
            v_admin_auth_id
        ),
        (
            'EX001',
            'Ressonância Magnética',
            'Exame de ressonância magnética',
            'exame',
            800.00,
            100.00,
            200.00,
            1100.00,
            '01:00:00',
            true,
            'Requer jejum',
            v_admin_auth_id,
            v_admin_auth_id
        ),
        (
            'PROC001',
            'Cirurgia Eletiva',
            'Procedimento cirúrgico',
            'procedimento',
            3000.00,
            0.00,
            1000.00,
            4000.00,
            '02:00:00',
            true,
            'Cirurgia',
            v_admin_auth_id,
            v_admin_auth_id
        ),
        (
            'INT001',
            'Internação',
            'Internação hospitalar',
            'internacao',
            5000.00,
            0.00,
            2000.00,
            7000.00,
            '24:00:00',
            true,
            'Internação',
            v_admin_auth_id,
            v_admin_auth_id
        ) RETURNING id
    )
    SELECT array_agg(id) INTO v_procedimentos_ids FROM procedimentos_inseridos;

    -- Criar planos de saúde
    WITH planos_inseridos AS (
        INSERT INTO planos_saude (
            codigo_operadora,
            registro_ans,
            nome,
            tipo_plano,
            abrangencia,
            observacoes,
            dados_contrato,
            created_by,
            updated_by
        )
        SELECT
            'PLANO' || num,
            'ANS' || num,
            'Plano ' || num,
            CASE (num % 3)
                WHEN 0 THEN 'Individual'
                WHEN 1 THEN 'Familiar'
                WHEN 2 THEN 'Empresarial'
            END,
            CASE (num % 2)
                WHEN 0 THEN 'Nacional'
                WHEN 1 THEN 'Regional'
            END,
            'Plano criado para testes ' || num,
            jsonb_build_object(
                'contrato', num::text,
                'vigencia', '2024',
                'cobertura', CASE (num % 2)
                    WHEN 0 THEN 'Total'
                    WHEN 1 THEN 'Parcial'
                END
            ),
            v_admin_auth_id,
            v_admin_auth_id
        FROM generate_series(1, 5) num
        RETURNING id
    )
    SELECT array_agg(id) INTO v_planos_ids FROM planos_inseridos;

    -- Criar pacientes
    WITH pacientes_inseridos AS (
        INSERT INTO pacientes (
            nome,
            cpf,
            rg,
            data_nascimento,
            nome_responsavel,
            nome_pai,
            nome_mae,
            sexo,
            cep,
            endereco,
            numero,
            complemento,
            bairro,
            cidade,
            cidade_id,
            estado,
            telefone,
            email,
            profissional_id,
            created_by,
            updated_by
        )
        SELECT
            'Paciente ' || num,
            lpad(num::text, 11, '0'),
            lpad(num::text, 8, '0'),
            CURRENT_DATE - ((20 + num) * interval '1 year'),
            CASE (num % 2)
                WHEN 0 THEN 'Responsável ' || num
                ELSE NULL
            END,
            'Pai ' || num,
            'Mãe ' || num,
            CASE (num % 2)
                WHEN 0 THEN 'M'
                ELSE 'F'
            END,
            '12345' || lpad(num::text, 3, '0'),
            'Rua ' || num,
            num,
            'Apto ' || num,
            'Bairro ' || num,
            'Cidade ' || num,
            num,
            'SP',
            '11' || lpad(num::text, 9, '9'),
            'paciente' || num || '@teste.com',
            CASE (num % 2)
                WHEN 0 THEN v_medico_id
                ELSE v_fisio_id
            END,
            v_admin_auth_id,
            v_admin_auth_id
        FROM generate_series(1, 10) num
        RETURNING id
    )
    SELECT array_agg(id) INTO v_pacientes_ids FROM pacientes_inseridos;

    -- Criar carteirinhas
    WITH carteirinhas_inseridas AS (
        INSERT INTO carteirinhas (
            paciente_id,
            plano_saude_id,
            numero_carteirinha,
            data_validade,
            status,
            motivo_inativacao,
            historico_status,
            titular,
            nome_titular,
            cpf_titular,
            observacoes,
            created_by,
            updated_by
        )
        SELECT
            paciente_id,
            plano_id,
            'CART' || num,
            CURRENT_DATE + interval '1 year',
            CASE (num % 4)
                WHEN 0 THEN 'ativa'::status_carteirinha
                WHEN 1 THEN 'ativa'::status_carteirinha
                WHEN 2 THEN 'suspensa'::status_carteirinha
                WHEN 3 THEN 'vencida'::status_carteirinha
            END,
            CASE (num % 4)
                WHEN 2 THEN 'Pagamento pendente'
                WHEN 3 THEN 'Contrato vencido'
                ELSE NULL
            END,
            jsonb_build_array(
                jsonb_build_object(
                    'status', 'ativa',
                    'data', CURRENT_TIMESTAMP,
                    'motivo', 'Criação inicial'
                )
            ),
            CASE (num % 2)
                WHEN 0 THEN true
                ELSE false
            END,
            CASE (num % 2)
                WHEN 0 THEN NULL
                ELSE 'Titular ' || num
            END,
            CASE (num % 2)
                WHEN 0 THEN NULL
                ELSE lpad((num + 100)::text, 11, '0')
            END,
            'Carteirinha teste ' || num,
            v_admin_auth_id,
            v_admin_auth_id
        FROM (
            SELECT 
                num,
                v_pacientes_ids[1 + (num % array_length(v_pacientes_ids, 1))] as paciente_id,
                v_planos_ids[1 + (num % array_length(v_planos_ids, 1))] as plano_id
            FROM generate_series(1, 15) num
        ) subq
        RETURNING id
    )
    SELECT array_agg(id) INTO v_carteirinhas_ids FROM carteirinhas_inseridas;

    -- Criar guias
    INSERT INTO guias (
        carteirinha_id,
        paciente_id,
        procedimento_id,
        numero_guia,
        data_solicitacao,
        data_autorizacao,
        status,
        tipo,
        quantidade_autorizada,
        quantidade_executada,
        motivo_negacao,
        codigo_servico,
        descricao_servico,
        quantidade,
        observacoes,
        dados_autorizacao,
        historico_status,
        created_by,
        updated_by
    )
    SELECT
        carteirinha_id,
        paciente_id,
        procedimento_id,
        'G-' || v_timestamp || '-' || num,
        CURRENT_DATE - (num % 30 || ' days')::interval,
        CASE 
            WHEN num % 4 = 0 THEN CURRENT_DATE - ((num % 15) || ' days')::interval
            ELSE NULL
        END,
        CASE (num % 5)
            WHEN 0 THEN 'rascunho'::status_guia
            WHEN 1 THEN 'pendente'::status_guia
            WHEN 2 THEN 'autorizada'::status_guia
            WHEN 3 THEN 'negada'::status_guia
            WHEN 4 THEN 'executada'::status_guia
        END,
        proc_tipo::tipo_procedimento,
        CASE 
            WHEN proc_tipo = 'procedimento' THEN (num % 3) + 1
            ELSE 1
        END,
        CASE 
            WHEN num % 4 = 1 AND proc_tipo = 'procedimento' THEN 1
            ELSE 0
        END,
        CASE 
            WHEN num % 5 = 2 THEN 'Fora da cobertura'
            ELSE NULL
        END,
        proc_codigo,
        proc_nome,
        1,
        'Guia teste ' || num,
        jsonb_build_object(
            'autorizador', CASE 
                WHEN num % 4 = 0 THEN 'Sistema'
                ELSE 'Manual'
            END,
            'protocolo', CASE 
                WHEN num % 4 = 0 THEN 'AUTH' || v_timestamp || num
                ELSE NULL
            END
        ),
        jsonb_build_array(
            jsonb_build_object(
                'status', 'pendente',
                'data', CURRENT_TIMESTAMP - interval '1 hour',
                'motivo', 'Criação inicial'
            ),
            CASE 
                WHEN num % 4 = 0 THEN jsonb_build_object(
                    'status', 'autorizada',
                    'data', CURRENT_TIMESTAMP,
                    'motivo', 'Autorização automática'
                )
                ELSE NULL
            END
        ),
        CASE (num % 2)
            WHEN 0 THEN v_medico_auth_id
            ELSE v_operador_auth_id
        END,
        CASE (num % 2)
            WHEN 0 THEN v_medico_auth_id
            ELSE v_operador_auth_id
        END
    FROM (
        SELECT 
            num,
            v_carteirinhas_ids[1 + (num % array_length(v_carteirinhas_ids, 1))] as carteirinha_id,
            (SELECT paciente_id FROM carteirinhas WHERE id = v_carteirinhas_ids[1 + (num % array_length(v_carteirinhas_ids, 1))]) as paciente_id,
            proc.id as procedimento_id,
            proc.tipo::text as proc_tipo,
            proc.codigo as proc_codigo,
            proc.nome as proc_nome
        FROM generate_series(1, 30) num
        CROSS JOIN LATERAL (
            SELECT id, tipo, codigo, nome 
            FROM procedimentos 
            ORDER BY random() 
            LIMIT 1
        ) proc
    ) subq;

    -- Criar fichas e sessões
    WITH guias_disponiveis AS (
        SELECT 
            g.id as guia_id, 
            g.numero_guia,
            p.nome as paciente_nome,
            c.numero_carteirinha,
            ROW_NUMBER() OVER (ORDER BY g.created_at DESC) as rn
        FROM guias g
        JOIN pacientes p ON p.id = g.paciente_id
        JOIN carteirinhas c ON c.id = g.carteirinha_id
        ORDER BY g.created_at DESC
        LIMIT 20
    ),
    fichas_inseridas AS (
        INSERT INTO fichas (
            codigo_ficha,
            guia_id,
            numero_guia,
            paciente_nome,
            paciente_carteirinha,
            arquivo_digitalizado,
            status,
            data_atendimento,
            total_sessoes,
            created_by,
            updated_by
        )
        SELECT DISTINCT ON (codigo_ficha)
            'FICHA-' || v_timestamp || '-G' || g.rn || '-F' || LPAD(((ROW_NUMBER() OVER (PARTITION BY g.guia_id ORDER BY num))::text), 3, '0'),
            g.guia_id,
            g.numero_guia,
            g.paciente_nome,
            g.numero_carteirinha,
            NULL, -- arquivo_digitalizado será preenchido depois
            CASE 
                WHEN num <= 3 THEN 'conferida'::status_ficha
                WHEN num <= 5 THEN 'faturada'::status_ficha
                ELSE 'pendente'::status_ficha
            END,
            CURRENT_DATE - ((num % 5) || ' days')::interval,
            CASE 
                WHEN num <= 5 THEN 5
                ELSE (num % 10) + 1
            END,
            v_admin_auth_id,
            v_admin_auth_id
        FROM generate_series(1, 20) num
        CROSS JOIN guias_disponiveis g
        RETURNING id, codigo_ficha, numero_guia, guia_id, created_at
    ),
    first_ficha AS (
        SELECT id, codigo_ficha, numero_guia
        FROM fichas_inseridas 
        ORDER BY created_at DESC
        LIMIT 1
    ),
    sessoes_inseridas AS (
        INSERT INTO sessoes (
            ficha_id,
            guia_id,
            data_sessao,
            possui_assinatura,
            procedimento_id,
            profissional_executante,
            status,
            numero_guia,
            codigo_ficha,
            origem,
            ordem_execucao,
            status_biometria,
            created_by,
            updated_by
        )
        SELECT
            f.id as ficha_id,
            f.guia_id,
            CASE 
                WHEN num <= 5 THEN CURRENT_DATE - ((num % 5) || ' days')::interval
                ELSE CURRENT_DATE + ((num % 10) || ' days')::interval
            END as data_sessao,
            CASE 
                WHEN num <= 5 THEN true 
                ELSE false
            END as possui_assinatura,
            v_procedimentos_ids[1 + (num % array_length(v_procedimentos_ids, 1))],
            CASE WHEN num % 2 = 0 THEN v_medico_id::text ELSE v_fisio_id::text END,
            CASE 
                WHEN num <= 3 THEN 'executada'::status_sessao
                WHEN num <= 5 THEN 'faturada'::status_sessao
                ELSE 'pendente'::status_sessao
            END,
            f.numero_guia,
            f.codigo_ficha,
            'manual',
            num,
            CASE 
                WHEN num <= 3 THEN 'verificado'::status_biometria
                ELSE 'nao_verificado'::status_biometria
            END,
            v_admin_auth_id,
            v_admin_auth_id
        FROM generate_series(1, 20) num
        CROSS JOIN first_ficha f
        RETURNING id
    )
    SELECT array_agg(id) INTO v_sessoes_ids FROM sessoes_inseridas;

    -- Popular dados de exemplo para execuções
    INSERT INTO execucoes (
        guia_id,
        sessao_id,
        data_execucao,
        data_atendimento,
        paciente_nome,
        paciente_carteirinha,
        numero_guia,
        codigo_ficha,
        usuario_executante,
        origem,
        ordem_execucao,
        status_biometria,
        conselho_profissional,
        numero_conselho,
        uf_conselho,
        codigo_cbo,
        profissional_executante,
        created_by,
        updated_by
    )
    SELECT 
        g.id as guia_id,
        s.id as sessao_id,
        s.data_sessao as data_execucao,
        s.data_sessao as data_atendimento,
        f.paciente_nome,
        f.paciente_carteirinha,
        g.numero_guia,
        f.codigo_ficha,
        s.usuario_executante,
        'manual' as origem,
        s.ordem_execucao,
        s.status_biometria,
        CASE 
            WHEN s.usuario_executante = v_medico_auth_id THEN 'CRM'
            ELSE 'CREFITO'
        END as conselho_profissional,
        CASE 
            WHEN s.usuario_executante = v_medico_auth_id THEN '123456'
            ELSE '654321'
        END as numero_conselho,
        'SP' as uf_conselho,
        CASE 
            WHEN s.usuario_executante = v_medico_auth_id THEN '225120'  -- CBO Médico
            ELSE '223605'  -- CBO Fisioterapeuta
        END as codigo_cbo,
        CASE 
            WHEN s.usuario_executante = v_medico_auth_id THEN 'Dr. João Silva'
            ELSE 'Dra. Maria Santos'
        END as profissional_executante,
        v_admin_auth_id as created_by,
        v_admin_auth_id as updated_by
    FROM sessoes s
    JOIN fichas f ON s.ficha_id = f.id
    JOIN guias g ON f.numero_guia = g.numero_guia
    WHERE s.status = 'executada'
    AND s.deleted_at IS NULL;

END $$;