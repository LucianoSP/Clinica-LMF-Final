-- Função para buscar pacientes que precisam ter suas carteirinhas migradas
CREATE OR REPLACE FUNCTION buscar_pacientes_para_migracao_carteirinhas(
    p_prefixo TEXT DEFAULT '0064',
    p_limite INTEGER DEFAULT 100
)
RETURNS TABLE (
    id UUID,
    nome TEXT,
    numero_carteirinha TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.nome::TEXT,
        p.numero_carteirinha::TEXT
    FROM 
        pacientes p
    WHERE 
        p.numero_carteirinha IS NOT NULL 
        AND p.numero_carteirinha != ''
        AND p.numero_carteirinha LIKE p_prefixo || '%'
        AND NOT EXISTS (
            SELECT 1 
            FROM carteirinhas c 
            WHERE c.paciente_id = p.id 
            AND c.numero_carteirinha = p.numero_carteirinha
        )
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql; 