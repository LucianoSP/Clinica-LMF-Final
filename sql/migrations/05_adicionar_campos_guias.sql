-- Adicionar novas colunas na tabela guias
ALTER TABLE guias
ADD COLUMN IF NOT EXISTS senha_autorizacao text,
ADD COLUMN IF NOT EXISTS data_emissao date,
ADD COLUMN IF NOT EXISTS data_validade date,
ADD COLUMN IF NOT EXISTS data_validade_senha date,
ADD COLUMN IF NOT EXISTS valor_autorizado decimal(10,2),
ADD COLUMN IF NOT EXISTS profissional_solicitante text,
ADD COLUMN IF NOT EXISTS profissional_executante text,
ADD COLUMN IF NOT EXISTS origem text DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS dados_adicionais jsonb DEFAULT '{}';

-- Atualizar colunas existentes para aceitar valores nulos onde apropriado
ALTER TABLE guias 
ALTER COLUMN data_solicitacao DROP NOT NULL,
ALTER COLUMN quantidade_autorizada SET DEFAULT 1;