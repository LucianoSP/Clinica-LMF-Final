-- Add total_sessoes column to fichas table
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fichas' 
        AND column_name = 'total_sessoes'
    ) THEN
        ALTER TABLE fichas 
        ADD COLUMN total_sessoes integer DEFAULT 1 CHECK (total_sessoes BETWEEN 1 AND 10);
    END IF;
END$$;