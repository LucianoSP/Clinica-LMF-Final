-- Consulta 1: Status atual dos processamentos
SELECT 
    task_id, 
    status, 
    total_guides, 
    processed_guides,
    total_execucoes,
    created_at,
    last_update,
    ROUND(EXTRACT(EPOCH FROM (last_update - created_at))/60) as duracao_minutos
FROM processing_status
ORDER BY created_at DESC
LIMIT 20;

-- Consulta 2: Guias por status
SELECT 
    status, 
    COUNT(*) as total
FROM guias_queue
GROUP BY status;

-- Consulta 3: Guias com mais tentativas
SELECT 
    numero_guia, 
    data_atendimento_completa, 
    attempts, 
    error
FROM guias_queue
WHERE attempts > 1
ORDER BY attempts DESC
LIMIT 20;

-- Consulta 4: Verificação de duplicidades - guias na fila
SELECT
    numero_guia,
    data_atendimento_completa,
    COUNT(*) as ocorrencias
FROM guias_queue
GROUP BY numero_guia, data_atendimento_completa
HAVING COUNT(*) > 1;

-- Consulta 5: Verificação de duplicidades - execuções
SELECT
    numero_guia,
    data_atendimento,
    ordem_execucao,
    COUNT(*) as ocorrencias
FROM execucoes
GROUP BY numero_guia, data_atendimento, ordem_execucao
HAVING COUNT(*) > 1;

-- Consulta 6: Guias por dia
SELECT 
    SUBSTRING(data_atendimento_completa, 1, 10) as data_atendimento,
    COUNT(*) as total_guias
FROM guias_queue
GROUP BY SUBSTRING(data_atendimento_completa, 1, 10)
ORDER BY data_atendimento DESC;

-- Consulta 7: Estatísticas gerais
SELECT
    (SELECT COUNT(*) FROM guias) as total_guias,
    (SELECT COUNT(*) FROM execucoes) as total_execucoes,
    (SELECT COUNT(*) FROM guias_queue WHERE status = 'processado') as guias_processadas,
    (SELECT COUNT(*) FROM guias_queue WHERE status = 'erro') as guias_erro,
    (SELECT COUNT(*) FROM guias_queue WHERE status = 'pending') as guias_pendentes;
