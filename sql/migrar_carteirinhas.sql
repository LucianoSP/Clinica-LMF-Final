-- Função para migrar carteirinhas da tabela pacientes para a tabela carteirinhas
CREATE OR REPLACE FUNCTION migrar_carteirinhas_pacientes()
RETURNS TABLE (
    paciente_id UUID,
    nome_paciente TEXT,
    numero_carteirinha TEXT,
    plano_saude_id UUID,
    plano_saude_nome TEXT,
    status TEXT,
    resultado TEXT
) AS $$
DECLARE
    v_paciente RECORD;
    v_plano_saude_id UUID;
    v_plano_unimed_id UUID;
    v_plano_bradesco_id UUID;
    v_plano_sulamerica_id UUID;
    v_plano_amil_id UUID;
    v_plano_padrao_id UUID;
    v_carteirinha_existente UUID;
    v_resultado TEXT;
    v_contador_criados INTEGER := 0;
    v_contador_existentes INTEGER := 0;
    v_contador_erros INTEGER := 0;
    v_usuario_sistema_id UUID := '00000000-0000-0000-0000-000000000000';
BEGIN
    -- Obter IDs dos planos de saúde mais comuns
    SELECT id INTO v_plano_unimed_id FROM planos_saude WHERE nome ILIKE '%unimed%' LIMIT 1;
    SELECT id INTO v_plano_bradesco_id FROM planos_saude WHERE nome ILIKE '%bradesco%' LIMIT 1;
    SELECT id INTO v_plano_sulamerica_id FROM planos_saude WHERE nome ILIKE '%sulamerica%' LIMIT 1;
    SELECT id INTO v_plano_amil_id FROM planos_saude WHERE nome ILIKE '%amil%' LIMIT 1;
    
    -- Definir plano padrão (usar Unimed se disponível, senão usar o primeiro plano encontrado)
    IF v_plano_unimed_id IS NOT NULL THEN
        v_plano_padrao_id := v_plano_unimed_id;
    ELSE
        SELECT id INTO v_plano_padrao_id FROM planos_saude LIMIT 1;
    END IF;
    
    -- Verificar se o usuário sistema existe, se não, criar
    IF NOT EXISTS (SELECT 1 FROM usuarios WHERE id = v_usuario_sistema_id) THEN
        INSERT INTO usuarios (
            id, nome, email, tipo_usuario, created_at, updated_at
        ) VALUES (
            v_usuario_sistema_id, 'Sistema', 'sistema@sistema.com', 'sistema', NOW(), NOW()
        );
    END IF;

    -- Processar cada paciente com número de carteirinha
    FOR v_paciente IN 
        SELECT 
            p.id, 
            p.nome, 
            p.numero_carteirinha 
        FROM 
            pacientes p
        WHERE 
            p.numero_carteirinha IS NOT NULL 
            AND p.numero_carteirinha != ''
            AND NOT EXISTS (
                SELECT 1 
                FROM carteirinhas c 
                WHERE c.paciente_id = p.id 
                AND c.numero_carteirinha = p.numero_carteirinha
            )
    LOOP
        BEGIN
            -- Determinar o plano de saúde com base no prefixo da carteirinha
            CASE
                WHEN v_paciente.numero_carteirinha LIKE '0064%' THEN
                    v_plano_saude_id := v_plano_unimed_id;
                WHEN v_paciente.numero_carteirinha LIKE '0865%' THEN
                    v_plano_saude_id := v_plano_bradesco_id;
                WHEN v_paciente.numero_carteirinha LIKE '0994%' THEN
                    v_plano_saude_id := v_plano_sulamerica_id;
                WHEN v_paciente.numero_carteirinha LIKE '0970%' THEN
                    v_plano_saude_id := v_plano_amil_id;
                ELSE
                    v_plano_saude_id := v_plano_padrao_id;
            END CASE;
            
            -- Verificar se já existe uma carteirinha com o mesmo número para outro paciente
            SELECT id INTO v_carteirinha_existente 
            FROM carteirinhas 
            WHERE numero_carteirinha = v_paciente.numero_carteirinha
            AND paciente_id != v_paciente.id
            LIMIT 1;
            
            IF v_carteirinha_existente IS NOT NULL THEN
                v_resultado := 'ERRO: Carteirinha já existe para outro paciente';
                v_contador_erros := v_contador_erros + 1;
            ELSE
                -- Inserir a carteirinha
                INSERT INTO carteirinhas (
                    paciente_id,
                    plano_saude_id,
                    numero_carteirinha,
                    status,
                    created_at,
                    updated_at,
                    created_by,
                    updated_by
                ) VALUES (
                    v_paciente.id,
                    v_plano_saude_id,
                    v_paciente.numero_carteirinha,
                    'ativa',
                    NOW(),
                    NOW(),
                    v_usuario_sistema_id,
                    v_usuario_sistema_id
                );
                
                v_resultado := 'Carteirinha criada com sucesso';
                v_contador_criados := v_contador_criados + 1;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            v_resultado := 'ERRO: ' || SQLERRM;
            v_contador_erros := v_contador_erros + 1;
        END;
        
        -- Retornar informações sobre o processamento
        RETURN QUERY
        SELECT 
            v_paciente.id,
            v_paciente.nome,
            v_paciente.numero_carteirinha,
            v_plano_saude_id,
            (SELECT nome FROM planos_saude WHERE id = v_plano_saude_id),
            'ativa'::TEXT,
            v_resultado;
    END LOOP;
    
    -- Retornar um resumo final
    RETURN QUERY
    SELECT 
        NULL::UUID,
        'RESUMO'::TEXT,
        'Total'::TEXT,
        NULL::UUID,
        'Total'::TEXT,
        'Total'::TEXT,
        'Criadas: ' || v_contador_criados || ', Erros: ' || v_contador_erros;
END;
$$ LANGUAGE plpgsql;

-- Função para executar a migração em lotes
CREATE OR REPLACE FUNCTION migrar_carteirinhas_em_lotes(
    p_tamanho_lote INTEGER DEFAULT 100
)
RETURNS TEXT AS $$
DECLARE
    v_total INTEGER;
    v_processados INTEGER := 0;
    v_criados INTEGER := 0;
    v_erros INTEGER := 0;
    v_lote RECORD;
    v_resultado RECORD;
BEGIN
    -- Contar total de carteirinhas a migrar
    SELECT COUNT(*) INTO v_total
    FROM pacientes p
    WHERE 
        p.numero_carteirinha IS NOT NULL 
        AND p.numero_carteirinha != ''
        AND NOT EXISTS (
            SELECT 1 
            FROM carteirinhas c 
            WHERE c.paciente_id = p.id 
            AND c.numero_carteirinha = p.numero_carteirinha
        );
    
    -- Processar em lotes
    FOR v_lote IN 
        SELECT 
            p.id
        FROM 
            pacientes p
        WHERE 
            p.numero_carteirinha IS NOT NULL 
            AND p.numero_carteirinha != ''
            AND NOT EXISTS (
                SELECT 1 
                FROM carteirinhas c 
                WHERE c.paciente_id = p.id 
                AND c.numero_carteirinha = p.numero_carteirinha
            )
        LIMIT p_tamanho_lote
    LOOP
        -- Chamar a função de migração para cada paciente no lote
        FOR v_resultado IN 
            SELECT * FROM migrar_carteirinhas_pacientes() 
            WHERE paciente_id = v_lote.id
        LOOP
            v_processados := v_processados + 1;
            
            IF v_resultado.resultado LIKE 'ERRO%' THEN
                v_erros := v_erros + 1;
            ELSE
                v_criados := v_criados + 1;
            END IF;
        END LOOP;
    END LOOP;
    
    RETURN 'Migração concluída. Total: ' || v_total || 
           ', Processados: ' || v_processados || 
           ', Criados: ' || v_criados || 
           ', Erros: ' || v_erros;
END;
$$ LANGUAGE plpgsql;

-- Exemplo de uso:
-- SELECT * FROM migrar_carteirinhas_pacientes();
-- SELECT migrar_carteirinhas_em_lotes(100); 