-- Script para recriar a tabela guias_queue
CREATE TABLE IF NOT EXISTS guias_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_guia TEXT NOT NULL,
    data_atendimento_completa TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    task_id TEXT,
    attempts INTEGER DEFAULT 0,
    error TEXT,
    processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Criar índices para melhorar a performance
CREATE INDEX IF NOT EXISTS idx_guias_queue_numero_guia ON guias_queue(numero_guia);
CREATE INDEX IF NOT EXISTS idx_guias_queue_task_id ON guias_queue(task_id);
CREATE INDEX IF NOT EXISTS idx_guias_queue_status ON guias_queue(status); 