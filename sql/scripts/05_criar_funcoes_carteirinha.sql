-- Remover funções existentes
DROP FUNCTION IF EXISTS listar_carteirinhas_com_detalhes;

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