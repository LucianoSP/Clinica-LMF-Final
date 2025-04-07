-- Script para remover a coluna codigo_aba da tabela pacientes
-- ATENÇÃO: Esta operação é irreversível e pode afetar outros sistemas

-- Primeiro, verificamos se existem referências à coluna em outras tabelas
DO $$
DECLARE
    ref_count INTEGER;
BEGIN
    -- Verifica referências em constraints
    SELECT COUNT(*) INTO ref_count
    FROM pg_constraint c
    JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
    JOIN pg_class cl ON cl.oid = c.conrelid
    JOIN pg_namespace n ON n.oid = cl.relnamespace
    WHERE n.nspname = 'public'
    AND a.attname = 'codigo_aba'
    AND c.contype = 'f'; -- foreign key constraint

    IF ref_count > 0 THEN
        RAISE EXCEPTION 'Existem % referências à coluna codigo_aba em constraints de chave estrangeira. Remova-as antes de prosseguir.', ref_count;
    END IF;

    -- Verifica referências em triggers
    SELECT COUNT(*) INTO ref_count
    FROM pg_trigger t
    JOIN pg_class cl ON cl.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = cl.relnamespace
    WHERE n.nspname = 'public'
    AND t.tgname IN (
        SELECT tgname FROM pg_trigger
        WHERE tgname LIKE '%codigo_aba%'
    );

    IF ref_count > 0 THEN
        RAISE WARNING 'Existem % possíveis referências à coluna codigo_aba em triggers. Verifique-as manualmente.', ref_count;
    END IF;
END
$$;

-- Remover índice associado à coluna
DROP INDEX IF EXISTS idx_pacientes_codigo_aba;

-- Remover a restrição UNIQUE, se existir
ALTER TABLE public.pacientes DROP CONSTRAINT IF EXISTS pacientes_codigo_aba_key;

-- Remover a restrição NOT NULL, se existir
ALTER TABLE public.pacientes ALTER COLUMN codigo_aba DROP NOT NULL;

-- Finalmente, remover a coluna
ALTER TABLE public.pacientes DROP COLUMN IF EXISTS codigo_aba;

-- Atualizar comentário na coluna id_origem para refletir a mudança
COMMENT ON COLUMN public.pacientes.id_origem IS 'Código único para vinculação com sistemas externos (substituiu codigo_aba)';

-- Verificar se a coluna foi removida
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = 'pacientes'
        AND column_name = 'codigo_aba'
    ) THEN
        RAISE EXCEPTION 'A coluna codigo_aba ainda existe na tabela pacientes. Verifique se há algum problema.';
    ELSE
        RAISE NOTICE 'Coluna codigo_aba removida com sucesso da tabela pacientes';
    END IF;
END
$$; 