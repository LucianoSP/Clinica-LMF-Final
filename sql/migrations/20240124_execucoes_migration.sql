-- Migration para adicionar e popular dados das execuções
\i migrations/20240124_add_profissional_columns_execucoes.sql
\i migrations/20240124_create_view_relatorio_execucoes.sql
\i migrations/20240124_populate_execucoes.sql