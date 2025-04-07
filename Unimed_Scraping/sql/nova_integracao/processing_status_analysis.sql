-- Consulta para análise de registros na tabela processing_status
-- Esta consulta cria uma view com estatísticas consolidadas
CREATE OR REPLACE VIEW processing_status_report AS
SELECT 
    DATE(created_at) AS data,
    status,
    COUNT(*) AS total_tasks,
    SUM(total_guides) AS total_guias_encontradas,
    SUM(processed_guides) AS total_guias_processadas,
    SUM(retry_guides) AS total_guias_com_erro,
    SUM(total_execucoes) AS total_execucoes,
    ROUND(AVG(EXTRACT(EPOCH FROM (COALESCE(completed_at, NOW()) - started_at)) / 60), 2) AS tempo_medio_minutos
FROM 
    processing_status
WHERE 
    created_at >= NOW() - INTERVAL '30 days'
GROUP BY 
    DATE(created_at), status
ORDER BY 
    DATE(created_at) DESC, status;

-- Consulta para encontrar registros suspeitos (interrompidos)
SELECT 
    task_id,
    status,
    total_guides,
    processed_guides,
    total_execucoes,
    created_at,
    updated_at,
    started_at,
    error
FROM 
    processing_status
WHERE 
    (status IN ('iniciado', 'capturing', 'processing')
    AND created_at < NOW() - INTERVAL '1 day')
    OR
    (total_guides > 0 AND processed_guides = 0 AND status NOT IN ('pending', 'iniciado', 'capturing', 'queued'));

-- Consulta para análise de desempenho por dia
SELECT 
    DATE(created_at) AS data,
    COUNT(*) AS total_tasks,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS tasks_completed,
    SUM(CASE WHEN status = 'completed_with_errors' THEN 1 ELSE 0 END) AS tasks_partial,
    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) AS tasks_error,
    SUM(total_guides) AS total_guias,
    SUM(processed_guides) AS guias_processadas,
    ROUND(SUM(processed_guides)::numeric / NULLIF(SUM(total_guides), 0) * 100, 2) AS taxa_sucesso,
    ROUND(AVG(EXTRACT(EPOCH FROM (COALESCE(completed_at, NOW()) - started_at)) / 60), 2) AS tempo_medio_minutos
FROM 
    processing_status
WHERE 
    created_at >= NOW() - INTERVAL '30 days'
GROUP BY 
    DATE(created_at)
ORDER BY 
    DATE(created_at) DESC;

-- Consulta para verificar sessões pendentes há mais de 24 horas
SELECT 
    ps.task_id,
    ps.status AS task_status,
    ps.created_at AS task_created,
    ps.total_guides,
    ps.processed_guides,
    ps.total_execucoes,
    COUNT(usc.id) AS sessoes_pendentes
FROM 
    processing_status ps
JOIN 
    unimed_sessoes_capturadas usc ON ps.task_id = usc.task_id
WHERE 
    usc.status = 'pendente'
    AND usc.created_at < NOW() - INTERVAL '24 hours'
GROUP BY 
    ps.task_id, ps.status, ps.created_at, ps.total_guides, ps.processed_guides, ps.total_execucoes
ORDER BY 
    ps.created_at DESC; 