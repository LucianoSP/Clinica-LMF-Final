-- Script de migração para implementar o controle de importação de pacientes
-- Este script adiciona novos campos à tabela de pacientes existente
-- e cria a nova tabela de controle de importações

-- Iniciar uma transação para garantir consistência
BEGIN;

-- ==========================
-- 1. Adicionar novos campos à tabela pacientes existente
-- ==========================

-- Verificar e adicionar a coluna importado
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'pacientes' AND column_name = 'importado') THEN
        ALTER TABLE pacientes ADD COLUMN importado boolean DEFAULT false;
        RAISE NOTICE 'Coluna importado adicionada à tabela pacientes';
    ELSE
        RAISE NOTICE 'Coluna importado já existe na tabela pacientes';
    END IF;
END $$;

-- Verificar e adicionar a coluna id_origem
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'pacientes' AND column_name = 'id_origem') THEN
        ALTER TABLE pacientes ADD COLUMN id_origem character varying(50);
        RAISE NOTICE 'Coluna id_origem adicionada à tabela pacientes';
    ELSE
        RAISE NOTICE 'Coluna id_origem já existe na tabela pacientes';
    END IF;
END $$;

-- Verificar e adicionar a coluna data_registro_origem
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'pacientes' AND column_name = 'data_registro_origem') THEN
        ALTER TABLE pacientes ADD COLUMN data_registro_origem timestamptz;
        RAISE NOTICE 'Coluna data_registro_origem adicionada à tabela pacientes';
    ELSE
        RAISE NOTICE 'Coluna data_registro_origem já existe na tabela pacientes';
    END IF;
END $$;

-- Verificar e adicionar a coluna data_atualizacao_origem
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'pacientes' AND column_name = 'data_atualizacao_origem') THEN
        ALTER TABLE pacientes ADD COLUMN data_atualizacao_origem timestamptz;
        RAISE NOTICE 'Coluna data_atualizacao_origem adicionada à tabela pacientes';
    ELSE
        RAISE NOTICE 'Coluna data_atualizacao_origem já existe na tabela pacientes';
    END IF;
END $$;

-- ==========================
-- 2. Criar a tabela de controle de importação se não existir
-- ==========================

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

-- Tabela controle_importacao_pacientes criada/verificada

-- ==========================
-- 3. Adicionar índices para otimização
-- ==========================

-- Índices para a tabela de controle de importação
CREATE INDEX IF NOT EXISTS idx_controle_importacao_datas 
    ON controle_importacao_pacientes(ultima_data_registro_importada, ultima_data_atualizacao_importada);
CREATE INDEX IF NOT EXISTS idx_controle_importacao_timestamp 
    ON controle_importacao_pacientes(timestamp_importacao);

-- Índices para os novos campos na tabela de pacientes
CREATE INDEX IF NOT EXISTS idx_pacientes_importado ON pacientes(importado);
CREATE INDEX IF NOT EXISTS idx_pacientes_id_origem ON pacientes(id_origem);
CREATE INDEX IF NOT EXISTS idx_pacientes_data_registro_origem ON pacientes(data_registro_origem);
CREATE INDEX IF NOT EXISTS idx_pacientes_data_atualizacao_origem ON pacientes(data_atualizacao_origem);

-- ==========================
-- 4. Finalização e verificação
-- ==========================

-- Marcar os pacientes existentes, assumindo que não foram importados pelo novo sistema
UPDATE pacientes SET importado = false WHERE importado IS NULL;

-- Registrar um histórico de migração
DO $$
DECLARE
    admin_id uuid;
BEGIN
    -- Obter o ID do primeiro usuário disponível
    -- Não usamos mais a coluna 'role' que não existe
    SELECT id INTO admin_id
    FROM usuarios 
    ORDER BY created_at
    LIMIT 1;
    
    -- Se não encontrou nenhum usuário, usar um UUID fixo
    IF admin_id IS NULL THEN
        admin_id := '00000000-0000-0000-0000-000000000000'::uuid;
    END IF;
    
    -- Inserir o registro de migração
    INSERT INTO controle_importacao_pacientes (
        ultima_data_registro_importada,
        ultima_data_atualizacao_importada,
        quantidade_registros_importados,
        quantidade_registros_atualizados,
        observacoes,
        usuario_id
    ) VALUES (
        now(), -- Data atual como referência de início
        now(), -- Data atual como referência de início
        0, -- Nenhum paciente importado pela migração
        0, -- Nenhum paciente atualizado pela migração
        'Migração inicial do sistema de controle de importação',
        admin_id -- Usar o primeiro usuário como usuário da migração
    );
    
    RAISE NOTICE 'Migração registrada com sucesso';
END $$;

-- Confirmar a transação
COMMIT; 