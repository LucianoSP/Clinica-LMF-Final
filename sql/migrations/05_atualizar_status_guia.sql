-- Primeiro criamos um tipo temporário com os novos valores
CREATE TYPE status_guia_novo AS ENUM (
    'rascunho',
    'pendente',
    'autorizada',
    'negada',
    'cancelada',
    'executada'
);

-- Criamos uma coluna temporária com o novo tipo
ALTER TABLE guias ADD COLUMN status_novo status_guia_novo;

-- Copiamos os dados, convertendo 'em_analise' para 'rascunho'
UPDATE guias SET status_novo = CASE 
    WHEN status = 'em_analise' THEN 'rascunho'::status_guia_novo
    ELSE status::text::status_guia_novo
END;

-- Removemos a coluna antiga
ALTER TABLE guias DROP COLUMN status;

-- Renomeamos a nova coluna
ALTER TABLE guias RENAME COLUMN status_novo TO status;

-- Removemos o tipo antigo
DROP TYPE status_guia;

-- Renomeamos o novo tipo para o nome original
ALTER TYPE status_guia_novo RENAME TO status_guia; 