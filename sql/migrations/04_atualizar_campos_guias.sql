-- Desabilitar temporariamente as restrições de chave estrangeira
SET session_replication_role = 'replica';

-- Adicionar os novos campos
ALTER TABLE guias
ADD COLUMN IF NOT EXISTS paciente_id uuid,
ADD COLUMN IF NOT EXISTS tipo tipo_procedimento,
ADD COLUMN IF NOT EXISTS quantidade_autorizada integer DEFAULT 1,
ADD COLUMN IF NOT EXISTS quantidade_executada integer DEFAULT 0;

-- Atualizar os campos com valores das tabelas relacionadas
UPDATE guias g
SET 
    paciente_id = c.paciente_id,
    tipo = p.tipo,
    quantidade_autorizada = g.quantidade,
    quantidade_executada = 0
FROM carteirinhas c
LEFT JOIN procedimentos p ON p.id = g.procedimento_id
WHERE g.carteirinha_id = c.id;

-- Adicionar as constraints NOT NULL
ALTER TABLE guias
ALTER COLUMN paciente_id SET NOT NULL,
ALTER COLUMN procedimento_id SET NOT NULL,
ALTER COLUMN tipo SET NOT NULL;

-- Adicionar a foreign key para pacientes
ALTER TABLE guias
ADD CONSTRAINT guias_paciente_id_fkey
FOREIGN KEY (paciente_id)
REFERENCES pacientes(id);

-- Reabilitar as restrições de chave estrangeira
SET session_replication_role = 'origin';

-- Comentário para rollback se necessário
-- Para reverter:
-- ALTER TABLE guias DROP CONSTRAINT guias_paciente_id_fkey;
-- ALTER TABLE guias ALTER COLUMN paciente_id DROP NOT NULL;
-- ALTER TABLE guias ALTER COLUMN procedimento_id DROP NOT NULL;
-- ALTER TABLE guias ALTER COLUMN tipo DROP NOT NULL;
-- ALTER TABLE guias DROP COLUMN IF EXISTS quantidade_executada;
-- ALTER TABLE guias DROP COLUMN IF EXISTS quantidade_autorizada;
-- ALTER TABLE guias DROP COLUMN IF EXISTS tipo;
-- ALTER TABLE guias DROP COLUMN IF EXISTS paciente_id; 