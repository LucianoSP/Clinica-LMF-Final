--================ FUNÇÕES DE NEGÓCIO =================

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

-- Função para inserir ficha ignorando a restrição de chave estrangeira ou salvando como pendente
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
COMMENT ON FUNCTION inserir_ficha_bypass_fk(jsonb, uuid, boolean) IS 'Função para inserir fichas ignorando restrições de chave estrangeira ou salvando como pendentes';

-- ================ FUNÇÕES DE VINCULAÇÃO ================

CREATE OR REPLACE FUNCTION vincular_sessoes_execucoes()
RETURNS VOID AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    RAISE NOTICE 'Iniciando vinculação batch de execuções e sessões...';

    -- Passo 1: Vinculação Exata (Guia + Data + Ordem)
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
          AND e.ordem_execucao IS NOT NULL
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
        link_manual_necessario = FALSE
    FROM vinculos_unicos_exatos vu
    WHERE e.id = vu.execucao_id;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RAISE NOTICE 'Passo 1 (Exato - com ordem): % execuções vinculadas.', updated_count;

    -- Passo 1.1: Vinculação Exata (Guia + Data, SEM Ordem)
    WITH exatas_sem_ordem AS (
        SELECT
            e.id AS execucao_id,
            s.id AS sessao_id,
            s.codigo_ficha AS sessao_codigo_ficha
        FROM execucoes e
        JOIN sessoes s ON e.numero_guia = s.numero_guia
                      AND e.data_execucao = s.data_sessao
        WHERE e.sessao_id IS NULL
          AND e.ordem_execucao IS NULL
          AND s.ordem_execucao IS NULL
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
        WHERE e.sessao_id IS NULL
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
            ROW_NUMBER() OVER (PARTITION BY to_ord.execucao_id ORDER BY to_ord.diff_dias ASC) as rn
        FROM tolerancia_ordem to_ord
        JOIN contagem_tolerancia_ordem cto ON to_ord.execucao_id = cto.execucao_id
        WHERE cto.num_sessoes = 1
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
    WITH tolerancia_sem_ordem AS (
        SELECT
            e.id AS execucao_id,
            s.id AS sessao_id,
            s.codigo_ficha AS sessao_codigo_ficha,
            abs(e.data_execucao - s.data_sessao) as diff_dias
        FROM execucoes e
        JOIN sessoes s ON e.numero_guia = s.numero_guia
                      AND abs(e.data_execucao - s.data_sessao) <= 1
        WHERE e.sessao_id IS NULL
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
            ROW_NUMBER() OVER (PARTITION BY tso.execucao_id ORDER BY tso.diff_dias ASC) as rn
        FROM tolerancia_sem_ordem tso
        JOIN contagem_tolerancia_sem_ordem ctso ON tso.execucao_id = ctso.execucao_id
        WHERE ctso.num_sessoes = 1
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


CREATE OR REPLACE FUNCTION vincular_sessoes_mesmo_dia()
RETURNS VOID AS $$
DECLARE
    grupos_ambiguos RECORD;
    updated_count INTEGER := 0;
    flagged_count INTEGER := 0;
BEGIN
    RAISE NOTICE 'Iniciando vinculação batch para casos de MÚLTIPLAS sessões/execuções no mesmo dia/guia...';

    -- Identifica grupos (guia + data)
    FOR grupos_ambiguos IN
        WITH execucoes_nao_vinculadas AS (
            SELECT e.numero_guia, e.data_execucao, e.id as execucao_id, e.ordem_execucao
            FROM execucoes e
            WHERE e.sessao_id IS NULL
              AND e.link_manual_necessario = FALSE
              AND e.deleted_at IS NULL
        ),
        sessoes_disponiveis AS (
            SELECT s.numero_guia, s.data_sessao, s.id as sessao_id, s.ordem_execucao, s.codigo_ficha
            FROM sessoes s
            LEFT JOIN execucoes e ON s.id = e.sessao_id AND e.deleted_at IS NULL
            WHERE e.id IS NULL
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
        WHERE qtd_execucoes > 0 AND qtd_sessoes > 0
          AND (qtd_execucoes > 1 OR qtd_sessoes > 1)
    LOOP
        RAISE NOTICE 'Analisando grupo: Guia %, Data %', grupos_ambiguos.numero_guia, grupos_ambiguos.data;
        RAISE NOTICE '   Execuções: %, Sessões: %, Ordens Exec Únicas: %, Ordens Sess Únicas: %', 
                     grupos_ambiguos.qtd_execucoes, grupos_ambiguos.qtd_sessoes, 
                     grupos_ambiguos.qtd_ordem_exec_unicas, grupos_ambiguos.qtd_ordem_sess_unicas;

        -- Tenta vincular automaticamente SOMENTE SE as condições forem atendidas
        IF grupos_ambiguos.qtd_execucoes = grupos_ambiguos.qtd_sessoes AND
           grupos_ambiguos.qtd_ordem_exec_unicas = grupos_ambiguos.qtd_execucoes AND
           grupos_ambiguos.qtd_ordem_sess_unicas = grupos_ambiguos.qtd_sessoes
        THEN
            RAISE NOTICE '   -> Tentando vincular automaticamente por ordem...';
            WITH vinculos_por_ordem AS (
                SELECT e.id as execucao_id, s.id as sessao_id, s.codigo_ficha
                FROM execucoes e
                JOIN sessoes s ON e.numero_guia = s.numero_guia
                              AND e.data_execucao = s.data_sessao
                              AND e.ordem_execucao = s.ordem_execucao
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
            RAISE NOTICE '   -> Condições para vínculo automático não atendidas. Marcando para revisão manual...';
            UPDATE execucoes e
            SET link_manual_necessario = TRUE
            WHERE e.numero_guia = grupos_ambiguos.numero_guia
              AND e.data_execucao = grupos_ambiguos.data
              AND e.sessao_id IS NULL
              AND e.deleted_at IS NULL;
              
            GET DIAGNOSTICS flagged_count = ROW_COUNT;
             RAISE NOTICE '   -> % execuções marcadas para revisão manual.', flagged_count;
        END IF;

    END LOOP;

    RAISE NOTICE 'Vinculação de casos múltiplos concluída.';
END;
$$ LANGUAGE plpgsql; 

-- ================ FUNÇÃO DE VINCULAÇÃO DE AGENDAMENTOS ================

CREATE OR REPLACE FUNCTION vincular_agendamentos()
RETURNS JSONB AS $$
DECLARE
    v_sessoes_vinculadas INTEGER := 0;
    v_execucoes_vinculadas INTEGER := 0;
    v_sessoes_propagadas INTEGER := 0;
    v_execucoes_propagadas INTEGER := 0;
    result_json JSONB;
BEGIN
    RAISE NOTICE 'Iniciando vinculação batch de agendamentos...';

    -- Passo 1: Vincular Sessoes a Agendamentos únicos
    WITH sessoes_para_vincular AS (
        SELECT
            s.id as sessao_id,
            f.paciente_id,
            s.data_sessao,
            g.procedimento_id
        FROM sessoes s
        JOIN fichas f ON s.ficha_id = f.id
        JOIN guias g ON s.guia_id = g.id
        WHERE s.agendamento_id IS NULL
          AND s.deleted_at IS NULL
          AND f.paciente_id IS NOT NULL
          AND g.procedimento_id IS NOT NULL
    ),
    agendamentos_candidatos_sessao AS (
        SELECT
            spv.sessao_id,
            a.id as agendamento_id,
            COUNT(*) OVER (PARTITION BY spv.sessao_id) as contagem_matches
        FROM sessoes_para_vincular spv
        JOIN agendamentos a ON spv.paciente_id = a.paciente_id
                           AND spv.data_sessao = a.data_agendamento
                           AND spv.procedimento_id = a.procedimento_id
        WHERE a.deleted_at IS NULL
    ),
    vinculos_unicos_sessao AS (
        SELECT sessao_id, agendamento_id
        FROM agendamentos_candidatos_sessao
        WHERE contagem_matches = 1
    )
    UPDATE sessoes s
    SET agendamento_id = vu.agendamento_id
    FROM vinculos_unicos_sessao vu
    WHERE s.id = vu.sessao_id
      AND s.agendamento_id IS NULL; -- Evita re-atualizar

    GET DIAGNOSTICS v_sessoes_vinculadas = ROW_COUNT;
    RAISE NOTICE 'Passo 1 (Sessões -> Agendamentos): % sessoes vinculadas.', v_sessoes_vinculadas;

    -- Passo 2: Vincular Execucoes a Agendamentos únicos
    WITH execucoes_para_vincular AS (
        SELECT
            e.id as execucao_id,
            c.paciente_id,
            e.data_execucao,
            g.procedimento_id
        FROM execucoes e
        JOIN guias g ON e.guia_id = g.id
        JOIN carteirinhas c ON g.carteirinha_id = c.id
        WHERE e.agendamento_id IS NULL
          AND e.deleted_at IS NULL
          AND c.paciente_id IS NOT NULL
          AND g.procedimento_id IS NOT NULL
    ),
    agendamentos_candidatos_execucao AS (
        SELECT
            epv.execucao_id,
            a.id as agendamento_id,
            COUNT(*) OVER (PARTITION BY epv.execucao_id) as contagem_matches
        FROM execucoes_para_vincular epv
        JOIN agendamentos a ON epv.paciente_id = a.paciente_id
                           AND epv.data_execucao = a.data_agendamento
                           AND epv.procedimento_id = a.procedimento_id
        WHERE a.deleted_at IS NULL
    ),
    vinculos_unicos_execucao AS (
        SELECT execucao_id, agendamento_id
        FROM agendamentos_candidatos_execucao
        WHERE contagem_matches = 1
    )
    UPDATE execucoes e
    SET agendamento_id = vu.agendamento_id
    FROM vinculos_unicos_execucao vu
    WHERE e.id = vu.execucao_id
      AND e.agendamento_id IS NULL;

    GET DIAGNOSTICS v_execucoes_vinculadas = ROW_COUNT;
    RAISE NOTICE 'Passo 2 (Execuções -> Agendamentos): % execucoes vinculadas.', v_execucoes_vinculadas;

    -- Passo 3: Propagar vínculo de Sessão para Execução
    WITH sessoes_com_agendamento AS (
        SELECT id as sessao_id, agendamento_id
        FROM sessoes
        WHERE agendamento_id IS NOT NULL
          AND deleted_at IS NULL
    )
    UPDATE execucoes e
    SET agendamento_id = sca.agendamento_id
    FROM sessoes_com_agendamento sca
    WHERE e.sessao_id = sca.sessao_id
      AND e.agendamento_id IS NULL
      AND e.deleted_at IS NULL;

    GET DIAGNOSTICS v_execucoes_propagadas = ROW_COUNT;
    RAISE NOTICE 'Passo 3 (Sessão -> Execução): % execucoes atualizadas por propagação.', v_execucoes_propagadas;

    -- Passo 4: Propagar vínculo de Execução para Sessão
    WITH execucoes_com_agendamento AS (
        SELECT sessao_id, agendamento_id
        FROM execucoes
        WHERE sessao_id IS NOT NULL -- Só propaga se a execução estiver vinculada a uma sessão
          AND agendamento_id IS NOT NULL
          AND deleted_at IS NULL
    )
    UPDATE sessoes s
    SET agendamento_id = eca.agendamento_id
    FROM execucoes_com_agendamento eca
    WHERE s.id = eca.sessao_id
      AND s.agendamento_id IS NULL
      AND s.deleted_at IS NULL;

    GET DIAGNOSTICS v_sessoes_propagadas = ROW_COUNT;
    RAISE NOTICE 'Passo 4 (Execução -> Sessão): % sessoes atualizadas por propagação.', v_sessoes_propagadas;

    RAISE NOTICE 'Vinculação de agendamentos concluída.';

    result_json := jsonb_build_object(
        'sessoes_vinculadas_direto', v_sessoes_vinculadas,
        'execucoes_vinculadas_direto', v_execucoes_vinculadas,
        'execucoes_atualizadas_por_propagacao', v_execucoes_propagadas,
        'sessoes_atualizadas_por_propagacao', v_sessoes_propagadas,
        'total_vinculado_sessao', v_sessoes_vinculadas + v_sessoes_propagadas,
        'total_vinculado_execucao', v_execucoes_vinculadas + v_execucoes_propagadas
    );

    RETURN result_json;

END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION vincular_agendamentos() IS 'Tenta vincular automaticamente Sessoes e Execucoes a Agendamentos com base em paciente, data e procedimento. Propaga o vínculo entre Sessão e Execução.'; 


-- =============================================================================
-- Função: func_listar_agendamentos_view
-- Descrição: Lista agendamentos com informações agregadas (nomes de entidades
--            relacionadas, status de vinculação, etc.) utilizando a view
--            vw_agendamentos_com_status_vinculacao implicitamente (embora a query
--            seja refeita aqui para filtros dinâmicos). Suporta paginação, busca
--            por texto em várias colunas, ordenação e filtro por status_vinculacao.
--            A definição RETURNS TABLE foi cuidadosamente ajustada para corresponder
--            aos tipos de dados reais retornados pela consulta interna, resolvendo
--            erros 42804 (type mismatch).
-- Parâmetros:
--   p_offset: Número de registros a pular (para paginação).
--   p_limit: Número máximo de registros a retornar (para paginação).
--   p_search: Termo de busca (aplicado em várias colunas com ILIKE).
--   p_order_column: Coluna pela qual ordenar.
--   p_order_direction: Direção da ordenação ('ASC' ou 'DESC').
--   p_status_vinculacao: Filtra por um status de vinculação específico ('Pendente', 'Ficha OK', 'Unimed OK', 'Completo').
-- Retorna: Tabela com os dados dos agendamentos e informações agregadas.
-- =============================================================================

-- Remover a função antiga (se existir) para garantir a atualização
DROP FUNCTION IF EXISTS public.func_listar_agendamentos_view(integer, integer, text, text, text, text);

-- Recriar a função com a estrutura de retorno FINALMENTE CORRETA
CREATE OR REPLACE FUNCTION public.func_listar_agendamentos_view(
    p_offset integer,
    p_limit integer,
    p_search text DEFAULT NULL::text,
    p_order_column text DEFAULT 'data_agendamento'::text,
    p_order_direction text DEFAULT 'desc'::text,
    p_status_vinculacao text DEFAULT NULL::text
)
RETURNS TABLE(
    id uuid,
    schedule_id character varying,
    schedule_date_start timestamp with time zone,
    schedule_date_end timestamp with time zone,
    schedule_pacient_id character varying,
    schedule_pagamento_id character varying,
    schedule_pagamento text,
    schedule_profissional_id uuid,
    schedule_profissional text,
    schedule_unidade character varying,
    schedule_room_id character varying,
    schedule_qtd_sessions integer,
    schedule_status character varying,
    schedule_room_rent_value numeric,
    schedule_fixed boolean,
    schedule_especialidade_id character varying,
    schedule_local_id character varying,
    schedule_saldo_sessoes integer,
    schedule_elegibilidade boolean,
    schedule_falha_do_profissional boolean,
    schedule_parent_id character varying,
    schedule_registration_date timestamp with time zone,
    schedule_lastupdate timestamp with time zone,
    parent_id uuid,
    schedule_codigo_faturamento text,
    paciente_id uuid,
    procedimento_id uuid,
    data_agendamento date,
    hora_inicio time without time zone,
    hora_fim time without time zone,
    status character varying,
    observacoes text,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    created_by uuid,
    updated_by uuid,
    deleted_at timestamp with time zone,
    importado boolean,
    id_origem character varying,
    data_registro_origem timestamp with time zone,
    data_atualizacao_origem timestamp with time zone,
    sala_id_supabase uuid,
    local_id_supabase uuid,
    especialidade_id_supabase uuid,
    -- Colunas adicionadas pelos JOINs (tipos FINALMENTE revisados)
    paciente_nome text,
    procedimento_nome text,
    tipo_pagamento_nome text,
    sala_nome character varying,
    profissional_nome character varying,
    especialidade_nome text,
    carteirinha_numero text,
    plano_saude_nome character varying,
    local_nome character varying,
    status_vinculacao text,
    possui_sessao_vinculada boolean,
    possui_execucao_vinculada boolean
)
LANGUAGE plpgsql
AS $function$
DECLARE
    query_sql TEXT;
    valid_order_columns TEXT[] := ARRAY[
        'data_agendamento', 'paciente_nome', 'procedimento_nome', 'profissional_nome',
        'sala_nome', 'especialidade_nome', 'tipo_pagamento_nome', 'status_vinculacao',
        'schedule_date_start', 'status', 'local_nome'
    ];
    order_col TEXT;
    order_dir TEXT;
BEGIN
    -- Validação e sanitização dos parâmetros de ordenação
    order_col := lower(p_order_column);
    order_dir := upper(p_order_direction);

    IF NOT order_col = ANY(valid_order_columns) THEN
        order_col := 'data_agendamento'; -- Coluna padrão segura
    END IF;

    IF order_dir NOT IN ('ASC', 'DESC') THEN
        order_dir := 'DESC'; -- Direção padrão segura
    END IF;

    -- Construção da query SQL dinâmica
    query_sql := format('
        SELECT
            ag.*, -- Todas as colunas originais de agendamentos
            p.nome AS paciente_nome,
            proc.nome AS procedimento_nome,
            tp.nome AS tipo_pagamento_nome,
            sa.room_name AS sala_nome,
            ua.user_name AS profissional_nome,
            es.nome AS especialidade_nome,
            ca.numero_carteirinha AS carteirinha_numero,
            ps.nome AS plano_saude_nome,
            lo.local_nome AS local_nome,
            CASE
                WHEN s.id IS NOT NULL AND e.id IS NOT NULL THEN ''Completo''::text
                WHEN s.id IS NOT NULL THEN ''Ficha OK''::text
                WHEN e.id IS NOT NULL THEN ''Unimed OK''::text
                ELSE ''Pendente''::text
            END AS status_vinculacao,
            s.id IS NOT NULL AS possui_sessao_vinculada,
            e.id IS NOT NULL AS possui_execucao_vinculada
        FROM
            agendamentos ag
        LEFT JOIN pacientes p ON ag.paciente_id = p.id AND p.deleted_at IS NULL
        LEFT JOIN procedimentos proc ON ag.procedimento_id = proc.id AND proc.deleted_at IS NULL
        LEFT JOIN tipo_pagamento tp ON proc.pagamento_id_origem = tp.id_origem AND tp.deleted_at IS NULL
        LEFT JOIN sessoes s ON ag.id = s.agendamento_id AND s.deleted_at IS NULL
        LEFT JOIN execucoes e ON ag.id = e.agendamento_id AND e.deleted_at IS NULL
        LEFT JOIN salas sa ON ag.sala_id_supabase = sa.id AND sa.deleted_at IS NULL
        LEFT JOIN usuarios_aba ua ON ag.schedule_profissional_id = ua.id AND ua.deleted_at IS NULL
        LEFT JOIN especialidades es ON ag.especialidade_id_supabase = es.id AND es.deleted_at IS NULL
        LEFT JOIN carteirinhas ca ON ag.paciente_id = ca.paciente_id AND ca.deleted_at IS NULL
        LEFT JOIN planos_saude ps ON ca.plano_saude_id = ps.id AND ps.deleted_at IS NULL
        LEFT JOIN locais lo ON ag.local_id_supabase = lo.id AND lo.deleted_at IS NULL
        WHERE ag.deleted_at IS NULL ');

    -- Adiciona filtro de busca se p_search não for nulo ou vazio
    IF p_search IS NOT NULL AND p_search <> '' THEN
         -- CORREÇÃO: Usar %L para tratar p_search como literal e %% para os '%' do ILIKE
        query_sql := query_sql || format('
            AND (
                ag.status ILIKE ''%%%1$L%%'' OR
                ag.observacoes ILIKE ''%%%1$L%%'' OR
                p.nome ILIKE ''%%%1$L%%'' OR
                proc.nome ILIKE ''%%%1$L%%'' OR
                ua.user_name ILIKE ''%%%1$L%%'' OR
                es.nome ILIKE ''%%%1$L%%'' OR
                ca.numero_carteirinha ILIKE ''%%%1$L%%'' OR
                ps.nome ILIKE ''%%%1$L%%'' OR
                sa.room_name ILIKE ''%%%1$L%%'' OR
                lo.local_nome ILIKE ''%%%1$L%%'' OR
                 ag.id_origem::text ILIKE ''%%%1$L%%'' OR
                 ag.schedule_profissional_id::text ILIKE ''%%%1$L%%''
            )
        ', p_search); -- Passar p_search como argumento para %L
    END IF;

     -- Adiciona filtro de status_vinculacao se p_status_vinculacao não for nulo ou vazio
    IF p_status_vinculacao IS NOT NULL AND p_status_vinculacao <> '' THEN
        query_sql := query_sql || format('
             AND CASE
                 WHEN s.id IS NOT NULL AND e.id IS NOT NULL THEN ''Completo''::text
                 WHEN s.id IS NOT NULL THEN ''Ficha OK''::text
                 WHEN e.id IS NOT NULL THEN ''Unimed OK''::text
                 ELSE ''Pendente''::text
             END = %L ', p_status_vinculacao);
    END IF;

    -- Adiciona ordenação, offset e limit
    query_sql := query_sql || format('
        ORDER BY %I %s
        LIMIT %L OFFSET %L',
        order_col, order_dir, p_limit, p_offset
    );

    -- Log da query final (opcional, para debug)
    -- RAISE NOTICE 'Executing query: %', query_sql;

    -- Executa a query construída e retorna o resultado
    RETURN QUERY EXECUTE query_sql;
END;
$function$;

-- Adicionar Comentário
COMMENT ON FUNCTION public.func_listar_agendamentos_view(integer, integer, text, text, text, text)
    IS 'Lista agendamentos com informações agregadas (nomes, status de vinculação, etc.) com paginação, busca, ordenação e filtro por status de vinculação.';

-- Conceder permissão novamente (incluindo anon, como funcionou antes)
GRANT EXECUTE ON FUNCTION public.func_listar_agendamentos_view(integer, integer, text, text, text, text) TO authenticated, anon;
