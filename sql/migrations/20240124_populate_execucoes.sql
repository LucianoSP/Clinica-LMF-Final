-- Script para inserir dados de exemplo nas execuções
DO $$
DECLARE
    v_admin_id uuid;
    v_medico_id uuid;
    v_fisio_id uuid;
    v_admin_auth_id uuid;
    v_medico_auth_id uuid;
    v_fisio_auth_id uuid;
    v_guia record;
    v_sessao record;
BEGIN
    -- Recuperar IDs dos usuários
    SELECT id, auth_user_id INTO v_admin_id, v_admin_auth_id 
    FROM usuarios WHERE email = 'admin@clinica.com';
    
    SELECT id, auth_user_id INTO v_medico_id, v_medico_auth_id 
    FROM usuarios WHERE email = 'joao.silva@clinica.com';
    
    SELECT id, auth_user_id INTO v_fisio_id, v_fisio_auth_id 
    FROM usuarios WHERE email = 'maria.santos@clinica.com';

    -- Para cada guia autorizada
    FOR v_guia IN (
        SELECT g.*, p.nome as paciente_nome, c.numero_carteirinha
        FROM guias g
        JOIN pacientes p ON g.paciente_id = p.id
        JOIN carteirinhas c ON g.carteirinha_id = c.id
        WHERE g.status = 'autorizada'
        LIMIT 10
    )
    LOOP
        -- Para cada sessão da guia
        FOR v_sessao IN (
            SELECT s.*
            FROM sessoes s
            WHERE s.numero_guia = v_guia.numero_guia
            AND s.executado = true
            ORDER BY s.data_sessao
        )
        LOOP
            -- Inserir execução
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
                updated_by,
                ip_origem
            ) VALUES (
                v_guia.id,
                v_sessao.id,
                v_sessao.data_sessao,
                v_sessao.data_sessao,
                v_guia.paciente_nome,
                v_guia.numero_carteirinha,
                v_guia.numero_guia,
                v_sessao.codigo_ficha,
                CASE random() > 0.5 WHEN true THEN v_medico_auth_id ELSE v_fisio_auth_id END,
                CASE random() > 0.7 
                    WHEN true THEN 'importacao' 
                    WHEN random() > 0.5 THEN 'sistema' 
                    ELSE 'manual' 
                END,
                v_sessao.ordem_execucao,
                CASE random() 
                    WHEN random() > 0.7 THEN 'verificado'
                    WHEN random() > 0.4 THEN 'nao_verificado'
                    ELSE 'falha'
                END,
                CASE random() > 0.5 
                    WHEN true THEN 'CRM' 
                    ELSE 'CREFITO' 
                END,
                CASE random() > 0.5 
                    WHEN true THEN '123456' 
                    ELSE '654321' 
                END,
                (ARRAY['SP', 'RJ', 'MG', 'RS'])[floor(random() * 4 + 1)],
                CASE random() > 0.5 
                    WHEN true THEN '225120'  -- CBO Médico
                    ELSE '223605'  -- CBO Fisioterapeuta
                END,
                CASE random() > 0.5 
                    WHEN true THEN 'Dr. João Silva' 
                    ELSE 'Dra. Maria Santos' 
                END,
                v_admin_auth_id,
                v_admin_auth_id,
                '192.168.' || (floor(random() * 254 + 1))::text || '.' || (floor(random() * 254 + 1))::text
            );
        END LOOP;
    END LOOP;

    -- Atualizar algumas execuções com status diferentes para ter mais variedade
    UPDATE execucoes 
    SET status_biometria = 'falha',
        updated_at = now(),
        updated_by = v_admin_auth_id
    WHERE id IN (
        SELECT id FROM execucoes 
        ORDER BY random() 
        LIMIT (SELECT count(*) * 0.1 FROM execucoes)
    );

    -- Adicionar algumas execuções mais antigas
    INSERT INTO execucoes (
        SELECT 
            id,
            sessao_id,
            data_execucao - interval '3 months',
            data_atendimento - interval '3 months',
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
            now() - interval '3 months',
            now() - interval '3 months',
            null,
            created_by,
            updated_by,
            ip_origem
        FROM execucoes
        ORDER BY random()
        LIMIT 5
    );

END $$;