# Instruções: Relacionamento de Agendamentos com Tabelas ABA

Este documento descreve o processo realizado pela funcionalidade "Relacionar Agendamentos com Tabelas Aba" encontrada na página "Tabelas Sistema ABA" do frontend.

## Propósito

A importação inicial de agendamentos do sistema legado (MySQL) traz referências a salas, locais e especialidades usando os IDs numéricos (`INTEGER`) do sistema de origem (armazenados nas colunas `schedule_room_id`, `schedule_local_id`, `schedule_especialidade_id` da tabela `agendamentos` no Supabase).

As tabelas auxiliares (`salas`, `locais`, `especialidades`) importadas do sistema ABA também contêm esses IDs originais, mas podem tê-los armazenado como texto (`VARCHAR`) nas colunas `room_local_id`, `local_id`, `especialidade_id`.

O processo de "Relacionar Agendamentos" serve para **vincular** os agendamentos existentes no Supabase com os registros correspondentes nas tabelas auxiliares (`salas`, `locais`, `especialidades`), preenchendo as colunas de chave estrangeira `sala_id_supabase`, `local_id_supabase`, `especialidade_id_supabase` (que são do tipo `UUID`) na tabela `agendamentos` com os IDs corretos do Supabase.

## Quando Utilizar

Execute esta funcionalidade **APÓS** ter realizado com sucesso:

1.  A importação completa das **tabelas auxiliares** ("Importar Todas as Tabelas ABA").
2.  A importação (ou re-importação) dos **agendamentos** do sistema legado, garantindo que as colunas `schedule_room_id`, `schedule_local_id`, `schedule_especialidade_id` na tabela `agendamentos` do Supabase estejam definidas como `INTEGER` e contenham os IDs numéricos corretos da origem.

## Como Funciona (Processo no Backend)

1.  **Carregamento dos Mapas:** O sistema primeiro carrega as tabelas auxiliares (`salas`, `locais`, `especialidades`) do Supabase. Ele cria "mapas" (dicionários Python) onde as **chaves são os IDs originais convertidos para `INTEGER`** (extraídos das colunas `room_local_id`, `local_id`, `especialidade_id`) e os **valores são os IDs internos do Supabase** (ex: `id` da tabela `salas`, que é um `UUID`). IDs não numéricos nas tabelas auxiliares são ignorados e um aviso é registrado.
2.  **Busca em Lotes:** Os registros da tabela `agendamentos` são buscados do Supabase em lotes (páginas).
3.  **Verificação e Mapeamento:** Para cada agendamento no lote, o sistema pega o valor `INTEGER` das colunas `schedule_room_id`, `schedule_local_id`, `schedule_especialidade_id`.
4.  **Busca no Mapa:** Ele usa esse valor `INTEGER` como chave para procurar a correspondência nos mapas criados no passo 1.
5.  **Comparação:** Se uma correspondência for encontrada no mapa, o sistema compara o ID Supabase (`UUID`) retornado pelo mapa com o valor atual nas colunas de destino (`sala_id_supabase`, `local_id_supabase`, `especialidade_id_supabase`).
6.  **Atualização (se necessário):** Se o ID mapeado for diferente do ID Supabase atual (ou se o atual for nulo), uma atualização é preparada para preencher a coluna de chave estrangeira correta (`sala_id_supabase`, etc.) com o `UUID` mapeado.
7.  **Atualização em Lote:** Todas as atualizações necessárias para o lote são enviadas ao Supabase de uma só vez.
8.  **Repetição:** O processo repete para o próximo lote até que todos os agendamentos tenham sido verificados.

## Resultado Esperado

Ao final do processo, a resposta indicará:

-   `success: true`
-   Uma mensagem de sucesso.
-   `salas_relacionadas`, `locais_relacionados`, `especialidades_relacionadas`: A quantidade de agendamentos que tiveram seus respectivos links (`UUID`) atualizados ou criados.
-   `total_agendamentos_verificados`: O número total de agendamentos que foram analisados.

Isso significa que os agendamentos agora estão corretamente vinculados às suas respectivas salas, locais e especialidades dentro do banco de dados Supabase através das colunas `*_id_supabase`.

## Solução de Problemas

-   **Nenhum relacionamento criado (0 relacionamentos):**
    -   **Verifique a Importação de Agendamentos:** Confirme se a importação mais recente dos agendamentos foi feita *depois* de corrigir a estrutura da tabela `agendamentos` para usar `INTEGER` nas colunas `schedule_room_id`, etc. Os dados podem estar desatualizados.
    -   **Verifique Tipos nas Tabelas Auxiliares:** Garanta que os IDs originais (`room_local_id`, `local_id`, `especialidade_id`) nas tabelas `salas`, `locais`, `especialidades` sejam de fato numéricos (mesmo que armazenados como `VARCHAR`). Se contiverem texto não numérico, a conversão para `INTEGER` no passo de mapeamento falhará, e eles não serão incluídos no mapa. Verifique os logs do backend por avisos de conversão.
    -   **Verifique a Importação das Tabelas Auxiliares:** Confirme se a importação das tabelas auxiliares foi bem-sucedida.
    -   **Verifique se os Relacionamentos Já Existem:** O script agora só atualiza se o ID mapeado for diferente do ID Supabase atual. Se o relacionamento já foi feito corretamente, o número de relacionados será 0.
-   **Erros durante o processo:** Verifique os logs do servidor backend (FastAPI) para mensagens de erro detalhadas. 