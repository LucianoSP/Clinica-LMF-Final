-- Script para limpar dados de processamento
-- ATENÇÃO: Use com cautela, pois remove registros das tabelas

-- 1. Limpar guias que estão na fila com status específico
DELETE FROM guias_queue
WHERE status IN ('erro', 'pending');

-- 2. Limpar processamentos com erro ou pendentes
DELETE FROM processing_status
WHERE status IN ('error', 'pending') 
AND created_at < NOW() - INTERVAL '7 days';

-- 3. Reset de contadores em processamentos ativos (opcional)
-- UPDATE processing_status
-- SET processed_guides = 0, total_guides = 0
-- WHERE status = 'processing';

-- 4. Limpar execuções temporárias (opcional)
-- DELETE FROM execucoes
-- WHERE codigo_ficha_temp = true;
