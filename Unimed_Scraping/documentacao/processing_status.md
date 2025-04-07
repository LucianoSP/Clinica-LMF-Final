# Tabela Processing Status - Documentação

## Propósito
A tabela processing_status serve como um "log de execução" do script, registrando cada vez que o script é executado e seu progresso.

## Campos Principais
- task_id: Identificador único de cada execução (ex: task_20250128_100118_1634)
- status: Estado atual do processamento
- total_guides: Número total de guias encontradas para processar
- processed_guides: Número de guias efetivamente processadas
- error: Mensagem de erro (se houver)
- completed_at: Timestamp de finalização

## Ciclo de Status
1. pending: Status inicial
2. capturing: Durante a captura das guias
3. queued: Guias capturadas e enfileiradas
4. processing: Processando as guias
5. completed/completed_with_errors/error: Status finais

## Análise dos Registros Atuais
```sql
| status  | total_guides | processed_guides | observação                               |
|---------|--------------|------------------|------------------------------------------|
| queued  | 2           | 0                | Script interrompido após enfileirar      |
| queued  | 2           | 0                | Script interrompido após enfileirar      |
| queued  | 2           | 0                | Script interrompido após enfileirar      |
| error   | 16          | 16               | Script completou mas com erros           |
```

### Interpretação
1. Os registros com status "queued" e processed_guides = 0:
   - Script conseguiu capturar 2 guias
   - Enfileirou na guias_queue
   - Não chegou a processar nenhuma
   - Possivelmente interrompido antes do processamento

2. O registro com status "error" e processed_guides = 16:
   - Script encontrou 16 guias para processar
   - Conseguiu processar todas (processed_guides = 16)
   - Mas encontrou erros durante o processamento
   - Provavelmente erros de duplicidade ou validação

## Recomendações
1. Limpar registros antigos periodicamente
2. Investigar registros com status "error" para identificar problemas
3. Monitorar registros "queued" que não progrediram
