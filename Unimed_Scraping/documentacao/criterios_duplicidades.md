# Critérios de Duplicidade para Guias e Execuções

## Guias Queue (Tabela guias_queue)

Para verificar se uma guia já existe na fila de processamento, usamos a combinação:

- numero_guia
- data_atendimento_completa (formato dd/mm/aaaa hh:mm)

Exemplo:

```sql
SELECT * FROM guias_queue 
WHERE numero_guia = '58741438' 
AND data_atendimento_completa = '29/01/2025 17:55'
```

## Execuções (Tabela execucoes)

Para execuções, o critério é diferente. O número de execuções para cada guia é determinado pelo campo "Data de Procedimentos em Série" encontrado dentro da página da guia.

### Como as execuções são determinadas:

1. Após uma guia ser adicionada à fila (guias_queue), o sistema:

   - Acessa a tela de exames finalizados
   - Filtra pelo número da guia E data específica
   - Pode encontrar múltiplos registros da mesma guia em horários diferentes
   - Para cada registro encontrado, acessa a página da guia
2. No campo "Data de Procedimentos em Série", são listadas todas as datas de execução no formato:

   ```
   N - dd/mm/aaaa
   ```

   Onde:

   - N: é o número da ordem (1, 2, 3...)
   - dd/mm/aaaa: é a data da execução
3. Para cada atendimento (horário diferente), o sistema:

   - Extrai tanto a data quanto o número N diretamente do campo
   - O número N é usado como ordem_execucao
   - Gera uma execução para cada combinação de atendimento + ordem encontrada

### Como identificar execuções únicas:

Uma execução é única pela combinação de:

- numero_guia
- data_atendimento (com hora completa)
- ordem_execucao (número extraído do campo)

Exemplo:

```sql
SELECT * FROM execucoes
WHERE numero_guia = '58741438'
AND data_atendimento = '29/01/2025 17:55'
AND ordem_execucao = 1
```

### Observações importantes:

- NÃO verificamos duplicidade ao gravar na tabela execucoes - cada combinação de guia/atendimento/ordem gera um novo registro
- Uma guia terá tantas execuções quanto: número de atendimentos × número de datas em "Data de Procedimentos em Série"
- É possível ter múltiplas execuções no mesmo dia, cada uma com sua própria ordem
- A ordem é extraída diretamente do número que aparece no campo (ex: em "1 - 29/01/2025", a ordem é 1)
- O campo data_execucao (sem hora) não é usado como critério de duplicidade

### Exemplo real:

Guia: 59533336 com dois atendimentos no mesmo dia:

- Atendimento 1: 29/01/2025 18:00
- Atendimento 2: 29/01/2025 17:52

Campo "Data de Procedimentos em Série" em ambos os atendimentos:

```
1 - 29/01/2025  (ordem_execucao = 1)
```

Total de execuções geradas: 2 (uma para cada horário de atendimento)

## Código Temporário (codigo_ficha)

Para cada execução, geramos um código temporário único usando:

```python
codigo_ficha = f"TEMP_{numero_guia}_{data_atendimento.replace('/', '')}_{ordem_execucao}"
```

Este código garante unicidade baseado em todos os critérios relevantes para a execução.

## Atualizações Recentes

### Padronização de campos de data
- O campo `data_atendimento_completa` é agora consistentemente usado no formato "dd/mm/aaaa hh:mm"
- Este formato é mantido em todas as tabelas relacionadas para garantir consistência
- Ao comparar datas entre tabelas, sempre usamos o formato completo para evitar ambiguidades

### Identificação de pacientes
- Substituição do campo `codigo_aba` pelo campo `id_origem`
- Ao criar novos pacientes, utilizamos o formato padronizado: `id_origem: "UNIMED_{numero_carteira}"`
- Esta mudança simplifica a identificação de pacientes e alinha com a estrutura atual do banco

### Impacto nos critérios de duplicidade
- Os critérios de duplicidade para guias e execuções permanecem os mesmos
- A identificação de pacientes agora usa exclusivamente o campo `id_origem`
- Não há impacto na lógica de detecção de duplicidades nas tabelas `guias_queue` e `execucoes`

### Benefícios para detecção de duplicidades
- Maior consistência na identificação de registros
- Redução de falsos positivos/negativos na detecção de duplicidades
- Simplificação das consultas de verificação
