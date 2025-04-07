-- Remover funções existentes
DROP FUNCTION IF EXISTS listar_guias_com_detalhes;
DROP FUNCTION IF EXISTS obter_guia_com_detalhes;

-- Função para listar guias com detalhes do paciente e carteirinha
CREATE OR REPLACE FUNCTION listar_guias_com_detalhes(
    p_offset int,
    p_limit int,
    p_search text,
    p_status text,
    p_carteirinha_id text,
    p_paciente_id text,
    p_order_column text,
    p_order_direction text
)
RETURNS TABLE (
    carteirinha_id uuid,
    paciente_id uuid,
    procedimento_id uuid,
    numero_guia text,
    data_solicitacao date,
    data_autorizacao date,
    status status_guia,
    tipo tipo_guia,
    quantidade_autorizada int,
    quantidade_executada int,
    motivo_negacao text,
    codigo_servico text,
    descricao_servico text,
    quantidade int,
    observacoes text,
    dados_autorizacao jsonb,
    historico_status jsonb,
    id uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    created_by uuid,
    updated_by uuid,
    deleted_at timestamp with time zone,
    paciente_nome text,
    carteirinha_numero text
) 
LANGUAGE plpgsql
AS $$
#variable_conflict use_column
BEGIN
    RETURN QUERY
    SELECT 
        g.carteirinha_id,
        g.paciente_id,
        g.procedimento_id,
        g.numero_guia,
        COALESCE(g.data_solicitacao, g.created_at::date) as data_solicitacao,
        g.data_autorizacao,
        g.status::status_guia,
        COALESCE(g.tipo, 'procedimento')::tipo_guia as tipo,
        g.quantidade_autorizada,
        g.quantidade_executada,
        g.motivo_negacao,
        g.codigo_servico,
        g.descricao_servico,
        g.quantidade,
        g.observacoes,
        COALESCE(g.dados_autorizacao, '{}'::jsonb) as dados_autorizacao,
        COALESCE(g.historico_status, '[]'::jsonb) as historico_status,
        g.id,
        g.created_at,
        g.updated_at,
        g.created_by,
        g.updated_by,
        g.deleted_at,
        p.nome as paciente_nome,
        c.numero_carteirinha as carteirinha_numero
    FROM guias g
    LEFT JOIN pacientes p ON g.paciente_id = p.id AND p.deleted_at IS NULL
    LEFT JOIN carteirinhas c ON g.carteirinha_id = c.id AND c.deleted_at IS NULL
    WHERE g.deleted_at IS NULL
        AND (p_search IS NULL OR 
            g.numero_guia ILIKE '%' || p_search || '%' OR 
            g.codigo_servico ILIKE '%' || p_search || '%')
        AND (p_status IS NULL OR g.status::text = p_status)
        AND (p_carteirinha_id IS NULL OR g.carteirinha_id::text = p_carteirinha_id)
        AND (p_paciente_id IS NULL OR g.paciente_id::text = p_paciente_id)
    ORDER BY 
        CASE 
            WHEN p_order_direction = 'desc' THEN
                CASE 
                    WHEN p_order_column = 'data_solicitacao' THEN g.data_solicitacao::text
                    ELSE g.created_at::text
                END
        END DESC NULLS LAST,
        CASE 
            WHEN p_order_direction = 'asc' THEN
                CASE 
                    WHEN p_order_column = 'data_solicitacao' THEN g.data_solicitacao::text
                    ELSE g.created_at::text
                END
        END ASC NULLS LAST
    OFFSET p_offset
    LIMIT p_limit;
END;
$$;

-- Função para obter uma guia específica com detalhes
CREATE OR REPLACE FUNCTION obter_guia_com_detalhes(p_guia_id text)
RETURNS TABLE (
    carteirinha_id uuid,
    paciente_id uuid,
    procedimento_id uuid,
    numero_guia text,
    data_solicitacao date,
    data_autorizacao date,
    status status_guia,
    tipo tipo_guia,
    quantidade_autorizada int,
    quantidade_executada int,
    motivo_negacao text,
    codigo_servico text,
    descricao_servico text,
    quantidade int,
    observacoes text,
    dados_autorizacao jsonb,
    historico_status jsonb,
    id uuid,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    created_by uuid,
    updated_by uuid,
    deleted_at timestamp with time zone,
    paciente_nome text,
    carteirinha_numero text
)
LANGUAGE plpgsql
AS $$
#variable_conflict use_column
BEGIN
    RETURN QUERY
    SELECT 
        g.carteirinha_id,
        g.paciente_id,
        g.procedimento_id,
        g.numero_guia,
        COALESCE(g.data_solicitacao, g.created_at::date) as data_solicitacao,
        g.data_autorizacao,
        g.status::status_guia,
        COALESCE(g.tipo, 'procedimento')::tipo_guia as tipo,
        g.quantidade_autorizada,
        g.quantidade_executada,
        g.motivo_negacao,
        g.codigo_servico,
        g.descricao_servico,
        g.quantidade,
        g.observacoes,
        COALESCE(g.dados_autorizacao, '{}'::jsonb) as dados_autorizacao,
        COALESCE(g.historico_status, '[]'::jsonb) as historico_status,
        g.id,
        g.created_at,
        g.updated_at,
        g.created_by,
        g.updated_by,
        g.deleted_at,
        p.nome as paciente_nome,
        c.numero_carteirinha as carteirinha_numero
    FROM guias g
    LEFT JOIN pacientes p ON g.paciente_id = p.id AND p.deleted_at IS NULL
    LEFT JOIN carteirinhas c ON g.carteirinha_id = c.id AND c.deleted_at IS NULL
    WHERE g.deleted_at IS NULL
        AND g.id::text = p_guia_id;
END;
$$;

-- Conceder permissões de execução para todas as funções
DO $$
BEGIN
    -- Conceder permissão para listar_guias_com_detalhes com a assinatura correta
    EXECUTE 'GRANT EXECUTE ON FUNCTION listar_guias_com_detalhes(int, int, text, text, text, text, text, text) TO authenticated, anon, service_role';
    
    -- Conceder permissão para obter_guia_com_detalhes
    EXECUTE 'GRANT EXECUTE ON FUNCTION obter_guia_com_detalhes(text) TO authenticated, anon, service_role';
    
    RAISE NOTICE 'Permissões concedidas com sucesso para as funções de guias';
END $$;
