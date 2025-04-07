# Documentação de Esquemas CSV
Gerado em: 03/04/2025 11:32:52

Este documento contém a estrutura e amostras de dados de 96 arquivos CSV extraídos.

## Índice

1. [aba_areas.csv](#aba-areas-csv)
2. [aba_atividades.csv](#aba-atividades-csv)
3. [aba_atividades_x_programas.csv](#aba-atividades-x-programas-csv)
4. [aba_programas.csv](#aba-programas-csv)
5. [agendas_profissionais.csv](#agendas-profissionais-csv)
6. [anamnese_pergunta.csv](#anamnese-pergunta-csv)
7. [anamnese_resposta.csv](#anamnese-resposta-csv)
8. [bancos.csv](#bancos-csv)
9. [conselhos.csv](#conselhos-csv)
10. [contatos_emergencia.csv](#contatos-emergencia-csv)
11. [dados_bancarios.csv](#dados-bancarios-csv)
12. [filhos_usuarios.csv](#filhos-usuarios-csv)
13. [historico_titulacoes.csv](#historico-titulacoes-csv)
14. [lur_habilidades_luria.csv](#lur-habilidades-luria-csv)
15. [lur_habilidades_luria_clients.csv](#lur-habilidades-luria-clients-csv)
16. [mbm_aba_areas.csv](#mbm-aba-areas-csv)
17. [mbm_aba_atendimento.csv](#mbm-aba-atendimento-csv)
18. [mbm_aba_atividades.csv](#mbm-aba-atividades-csv)
19. [mbm_aba_atv_prg.csv](#mbm-aba-atv-prg-csv)
20. [mbm_aba_comportamentos.csv](#mbm-aba-comportamentos-csv)
21. [mbm_aba_patient_consults.csv](#mbm-aba-patient-consults-csv)
22. [mbm_aba_patient_programa_consultas.csv](#mbm-aba-patient-programa-consultas-csv)
23. [mbm_aba_programas.csv](#mbm-aba-programas-csv)
24. [mbm_aba_validate_answers.csv](#mbm-aba-validate-answers-csv)
25. [mbm_clients_videos.csv](#mbm-clients-videos-csv)
26. [mbm_clients_videos_tutorial.csv](#mbm-clients-videos-tutorial-csv)
27. [ps_anamnese.csv](#ps-anamnese-csv)
28. [ps_anamnese_itens.csv](#ps-anamnese-itens-csv)
29. [ps_avaliacoes.csv](#ps-avaliacoes-csv)
30. [ps_care_rooms.csv](#ps-care-rooms-csv)
31. [ps_clients.csv](#ps-clients-csv)
32. [ps_clients_atividades_digitalizadas.csv](#ps-clients-atividades-digitalizadas-csv)
33. [ps_clients_attachments.csv](#ps-clients-attachments-csv)
34. [ps_clients_avaliacoes.csv](#ps-clients-avaliacoes-csv)
35. [ps_clients_contatos.csv](#ps-clients-contatos-csv)
36. [ps_clients_evolution.csv](#ps-clients-evolution-csv)
37. [ps_clients_faltas.csv](#ps-clients-faltas-csv)
38. [ps_clients_pagamentos.csv](#ps-clients-pagamentos-csv)
39. [ps_clients_pro_history.csv](#ps-clients-pro-history-csv)
40. [ps_clients_professional.csv](#ps-clients-professional-csv)
41. [ps_clients_reports.csv](#ps-clients-reports-csv)
42. [ps_financial_accounts.csv](#ps-financial-accounts-csv)
43. [ps_financial_categories.csv](#ps-financial-categories-csv)
44. [ps_financial_expenses.csv](#ps-financial-expenses-csv)
45. [ps_financial_revenues.csv](#ps-financial-revenues-csv)
46. [ps_financial_suppliers.csv](#ps-financial-suppliers-csv)
47. [ps_locales.csv](#ps-locales-csv)
48. [ps_log_actions.csv](#ps-log-actions-csv)
49. [ps_registros_guias.csv](#ps-registros-guias-csv)
50. [ps_registros_guias_datas.csv](#ps-registros-guias-datas-csv)
51. [ps_schedule.csv](#ps-schedule-csv)
52. [ps_schedule_blocked.csv](#ps-schedule-blocked-csv)
53. [ps_schedule_pacients.csv](#ps-schedule-pacients-csv)
54. [ps_schedule_professionals.csv](#ps-schedule-professionals-csv)
55. [ps_schedule_professionals_blocked.csv](#ps-schedule-professionals-blocked-csv)
56. [ra_relatorio_medico.csv](#ra-relatorio-medico-csv)
57. [ra_relatorio_mensal_amil.csv](#ra-relatorio-mensal-amil-csv)
58. [ra_relatorio_mensal_ipasgo.csv](#ra-relatorio-mensal-ipasgo-csv)
59. [ra_tratativas_faltas.csv](#ra-tratativas-faltas-csv)
60. [sys_permissions.csv](#sys-permissions-csv)
61. [teste_perfil_sensorial.csv](#teste-perfil-sensorial-csv)
62. [teste_perfil_sensorial_pacientes.csv](#teste-perfil-sensorial-pacientes-csv)
63. [teste_perfil_sensorial_perguntas.csv](#teste-perfil-sensorial-perguntas-csv)
64. [teste_vineland.csv](#teste-vineland-csv)
65. [teste_vineland_pacientes.csv](#teste-vineland-pacientes-csv)
66. [ws_certificados.csv](#ws-certificados-csv)
67. [ws_config.csv](#ws-config-csv)
68. [ws_config_profiles.csv](#ws-config-profiles-csv)
69. [ws_config_profiles_permissions.csv](#ws-config-profiles-permissions-csv)
70. [ws_especialidades.csv](#ws-especialidades-csv)
71. [ws_lista_espera.csv](#ws-lista-espera-csv)
72. [ws_lista_espera_temp.csv](#ws-lista-espera-temp-csv)
73. [ws_mudanca_horario.csv](#ws-mudanca-horario-csv)
74. [ws_mudanca_horario_temp.csv](#ws-mudanca-horario-temp-csv)
75. [ws_noticias.csv](#ws-noticias-csv)
76. [ws_pagamentos.csv](#ws-pagamentos-csv)
77. [ws_pagamentos_x_codigos_faturamento.csv](#ws-pagamentos-x-codigos-faturamento-csv)
78. [ws_patologia.csv](#ws-patologia-csv)
79. [ws_patologia_cliente.csv](#ws-patologia-cliente-csv)
80. [ws_profissoes.csv](#ws-profissoes-csv)
81. [ws_profissoes_rooms.csv](#ws-profissoes-rooms-csv)
82. [ws_setores.csv](#ws-setores-csv)
83. [ws_siteviews_online.csv](#ws-siteviews-online-csv)
84. [ws_siteviews_views.csv](#ws-siteviews-views-csv)
85. [ws_tipos_desagendamentos.csv](#ws-tipos-desagendamentos-csv)
86. [ws_titulacoes.csv](#ws-titulacoes-csv)
87. [ws_users.csv](#ws-users-csv)
88. [ws_users_address.csv](#ws-users-address-csv)
89. [ws_users_attachments.csv](#ws-users-attachments-csv)
90. [ws_users_especialidades.csv](#ws-users-especialidades-csv)
91. [ws_users_locales.csv](#ws-users-locales-csv)
92. [ws_users_notes.csv](#ws-users-notes-csv)
93. [ws_users_pagamentos.csv](#ws-users-pagamentos-csv)
94. [ws_users_permissions.csv](#ws-users-permissions-csv)
95. [ws_users_profissoes.csv](#ws-users-profissoes-csv)
96. [ws_users_titulacoes.csv](#ws-users-titulacoes-csv)

---

## <a id='aba-areas-csv'></a>aba_areas.csv

**Total de Registros**: 0

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | area_id | object | NULL |
| 2 | area_nome | object | NULL |
| 3 | area_descricao | object | NULL |
| 4 | area_registration_date | object | NULL |
| 5 | area_lastupdate | object | NULL |


---

## <a id='aba-atividades-csv'></a>aba_atividades.csv

**Total de Registros**: 0

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | atividade_id | object | NULL |
| 2 | atividade_nome | object | NULL |
| 3 | atividade_descricao | object | NULL |
| 4 | atividade_image | object | NULL |
| 5 | atividade_brinquedo | object | NULL |
| 6 | atividade_registration_date | object | NULL |
| 7 | atividade_lastupdate | object | NULL |


---

## <a id='aba-atividades-x-programas-csv'></a>aba_atividades_x_programas.csv

**Total de Registros**: 0

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | object | NULL |
| 2 | programa_id | object | NULL |
| 3 | atividade_id | object | NULL |


---

## <a id='aba-programas-csv'></a>aba_programas.csv

**Total de Registros**: 0

**Total de Colunas**: 13

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | programa_id | object | NULL |
| 2 | area_id | object | NULL |
| 3 | programa_nome | object | NULL |
| 4 | programa_avaliacao | object | NULL |
| 5 | programa_objetivo | object | NULL |
| 6 | programa_procedimento | object | NULL |
| 7 | programa_imagem_procedimento | object | NULL |
| 8 | programa_descricao | object | NULL |
| 9 | programa_como_realizar | object | NULL |
| 10 | programa_resposta_da_crianca | object | NULL |
| 11 | programa_consequencia_reforcadora | object | NULL |
| 12 | programa_registration_date | object | NULL |
| 13 | programa_lastupdate | object | NULL |


---

## <a id='agendas-profissionais-csv'></a>agendas_profissionais.csv

**Total de Registros**: 0

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | agenda_profissional_id | object | NULL |
| 2 | agenda_profissional_user_id | object | NULL |
| 3 | agenda_profissional_unidade | object | NULL |
| 4 | agenda_profissional_dia | object | NULL |
| 5 | agenda_profissional_horario_inicial | object | NULL |
| 6 | agenda_profissional_horario_final | object | NULL |
| 7 | agenda_profissional_registration_date | object | NULL |
| 8 | agenda_profissional_lastupdate | object | NULL |


---

## <a id='anamnese-pergunta-csv'></a>anamnese_pergunta.csv

**Total de Registros**: 193

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | anamnese_pergunta_id | int64 | 1 |
| 2 | pergunta | object | Alguma doença genética? |
| 3 | tipo_resposta | object | ["sim_nao","discursiva"] |
| 4 | categoria_pergunta | object | historia_clinica |
| 5 | ativa | int64 | 1 |
| 6 | created_at | object | 2023-02-08 23:04:14 |
| 7 | updated_at | object | 2023-02-08 23:04:14 |

### Amostra de Dados

|   anamnese_pergunta_id | pergunta                                                                                                                                                                                   | tipo_resposta            | categoria_pergunta   |   ativa | created_at          | updated_at          |  
|-----------------------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------|:---------------------|--------:|:--------------------|:--------------------|  
|                      1 | Alguma doença genética?                                                                                                                                                                    | ["sim_nao","discursiva"] | historia_clinica     |       1 | 2023-02-08 23:04:14 | 2023-02-08 23:04:14 |  
|                      2 | Alguma má formação?                                                                                                                                                                        | ["sim_nao","discursiva"] | historia_clinica     |       1 | 2023-02-08 23:04:14 | 2023-02-08 23:04:14 |  
|                      3 | Já realizou cirurgias? Quais?                                                                                                                                                              | ["sim_nao","discursiva"] | historia_clinica     |       1 | 2023-02-08 23:04:14 | 2023-02-08 23:04:14 |  
|                      4 | Doenças Familiares? Quais?                                                                                                                                                                 | ["sim_nao","discursiva"] | historia_clinica     |       1 | 2023-02-08 23:04:14 | 2023-02-08 23:04:14 |  
|                      5 | Indicar idade do inicio da doença: <br> <small>(epilepsia, doenças mentais, alérgias, nervosas, endócrinas, hepáticas, refluxo gastresofágico, cardiopatias, pneumopatias, outros)</small> | ["discursiva"]           | historia_clinica     |       1 | 2023-02-08 23:04:14 | 2023-02-08 23:04:14 |

---

## <a id='anamnese-resposta-csv'></a>anamnese_resposta.csv

**Total de Registros**: 227,519

**Total de Colunas**: 9

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | anamnese_resposta_id | int64 | 1 |
| 2 | anamnese_pergunta_id | int64 | 7 |
| 3 | resposta | object | S |
| 4 | pergunta | object | Qual foi a primeira vez que procurou o especial... |
| 5 | tipo_resposta | object | sim_nao |
| 6 | anamnese_id | int64 | 596 |
| 7 | paciente_id | int64 | 2943 |
| 8 | created_at | object | 2023-02-08 20:15:08 |
| 9 | updated_at | object | 2023-02-08 20:15:08 |

### Amostra de Dados

|   anamnese_resposta_id |   anamnese_pergunta_id | resposta   | pergunta                                             | tipo_resposta   |   anamnese_id |   paciente_id | created_at          | updated_at          |  
|-----------------------:|-----------------------:|:-----------|:-----------------------------------------------------|:----------------|--------------:|--------------:|:--------------------|:--------------------|  
|                      1 |                      7 | S          | Qual foi a primeira vez que procurou o especialista? | sim_nao         |           596 |          2943 | 2023-02-08 20:15:08 | 2023-02-08 20:15:08 |  
|                      2 |                      7 | AQUI       | Qual foi a primeira vez que procurou o especialista? | discursiva      |           596 |          2943 | 2023-02-08 20:15:08 | 2023-02-08 20:15:08 |  
|                      3 |                      8 | S          | Buscou mais opniões médicas?                         | sim_nao         |           596 |          2943 | 2023-02-08 20:15:08 | 2023-02-08 20:15:08 |  
|                      4 |                     11 |            | Realizou exames de imagem? Quais?                    | sim_nao         |           596 |          2943 | 2023-02-08 20:15:08 | 2023-02-08 20:15:08 |  
|                      5 |                     11 |            | Realizou exames de imagem? Quais?                    | discursiva      |           596 |          2943 | 2023-02-08 20:15:08 | 2023-02-08 20:15:08 |

---

## <a id='bancos-csv'></a>bancos.csv

**Total de Registros**: 17

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | banco_id | int64 | 1 |
| 2 | banco_codigo | int64 | 1 |
| 3 | banco_name | object | Banco do Brasil |

### Amostra de Dados

|   banco_id |   banco_codigo | banco_name              |  
|-----------:|---------------:|:------------------------|  
|          1 |              1 | Banco do Brasil         |  
|          4 |            237 | Banco do Bradesco       |  
|          5 |             77 | Banco Inter             |  
|          6 |            104 | Caixa Econômica Federal |  
|          7 |             33 | Banco Santander         |

---

## <a id='conselhos-csv'></a>conselhos.csv

**Total de Registros**: 5

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | conselho_id | int64 | 1 |
| 2 | conselho_nome | object | CREFONO 5  |
| 3 | conselho_status | object | Ativo |

### Amostra de Dados

|   conselho_id | conselho_nome   | conselho_status   |  
|--------------:|:----------------|:------------------|  
|             1 | CREFONO 5       | Ativo             |  
|             2 | CRP 09          | Ativo             |  
|             3 | CREFITO 11      | Ativo             |  
|             4 | CREF14          | Ativo             |  
|             5 | AGMT            | Ativo             |

---

## <a id='contatos-emergencia-csv'></a>contatos_emergencia.csv

**Total de Registros**: 118

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | contato_emergencia_id | int64 | 1 |
| 2 | contato_emergencia_tipo | object | Mãe |
| 3 | contato_emergencia_nome | object | Ana Claudia |
| 4 | contato_emergencia_telefone | object | (62) 99989-7232 |
| 5 | contato_emergencia_email | float64 | NULL |
| 6 | contato_emergencia_user_id | int64 | 1822 |
| 7 | contato_emergencia_registration_date | object | 2024-02-09 15:04:15 |
| 8 | contato_emergencia_lastupdate | object | 2024-02-09 18:04:15 |

### Amostra de Dados

|   contato_emergencia_id | contato_emergencia_tipo   | contato_emergencia_nome   | contato_emergencia_telefone   |   contato_emergencia_email |   contato_emergencia_user_id | contato_emergencia_registration_date   | contato_emergencia_lastupdate   |  
|------------------------:|:--------------------------|:--------------------------|:------------------------------|---------------------------:|-----------------------------:|:---------------------------------------|:--------------------------------|  
|                       1 | Mãe                       | Ana Claudia               | (62) 99989-7232               |                        nan |                         1822 | 2024-02-09 15:04:15                    | 2024-02-09 18:04:15             |  
|                       2 | Cônjuge                   | Rhuan                     | (62) 99394-7182               |                        nan |                         1887 | 2024-02-09 15:23:45                    | 2024-02-09 18:23:45             |  
|                       3 | Filho(a)                  | Amanda                    | (62) 99436-3535               |                        nan |                          929 | 2024-02-09 16:49:09                    | 2024-02-09 19:49:09             |  
|                       4 | Irmão(ã)                  | Tiago                     | (62) 99995-7155               |                        nan |                          233 | 2024-02-09 16:56:34                    | 2024-02-09 19:56:34             |  
|                       5 | Mãe                       | Joyce                     | (64) 98115-1511               |                        nan |                         1713 | 2024-02-09 16:58:24                    | 2024-02-09 19:58:24             |

---

## <a id='dados-bancarios-csv'></a>dados_bancarios.csv

**Total de Registros**: 111

**Total de Colunas**: 10

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | dados_bancario_id | int64 | 1 |
| 2 | dados_bancario_client_id | int64 | 1822 |
| 3 | dados_bancario_banco_id | int64 | 6 |
| 4 | dados_bancario_agencia | int64 | 1842 |
| 5 | dados_bancario_conta | object | 8318339663 |
| 6 | dados_bancario_titular_cpf_cnpj | object | 70300506147 |
| 7 | dados_bancario_tipo_de_chave_pix | object | cpf |
| 8 | dados_bancario_chave_pix | object | 70300506147 |
| 9 | dados_bancario_registration_date | object | 2024-02-09 15:09:39 |
| 10 | dados_bancario_lastupdate | object | 2024-02-09 18:09:39 |

### Amostra de Dados

|   dados_bancario_id |   dados_bancario_client_id |   dados_bancario_banco_id |   dados_bancario_agencia | dados_bancario_conta   | dados_bancario_titular_cpf_cnpj   | dados_bancario_tipo_de_chave_pix   | dados_bancario_chave_pix   | dados_bancario_registration_date   | dados_bancario_lastupdate   |  
|--------------------:|---------------------------:|--------------------------:|-------------------------:|:-----------------------|:----------------------------------|:-----------------------------------|:---------------------------|:-----------------------------------|:----------------------------|  
|                   1 |                       1822 |                         6 |                     1842 | 8318339663             | 70300506147                       | cpf                                | 70300506147                | 2024-02-09 15:09:39                | 2024-02-09 18:09:39         |  
|                   2 |                       1887 |                        12 |                        1 | 80981688               | 022.708.981-15                    | cpf                                | 022.708.981-15             | 2024-02-09 15:25:24                | 2024-02-09 18:25:24         |  
|                   3 |                        929 |                        12 |                        1 | 83009386-9             | 77242114187                       | celular                            | 62981823174                | 2024-02-09 16:52:09                | 2024-02-09 19:52:09         |  
|                   4 |                       1195 |                        15 |                        1 | 55846664-8             | 70117228150                       | celular                            | 62992600588                | 2024-02-09 17:00:07                | 2024-02-09 20:00:07         |  
|                   5 |                         35 |                         5 |                        1 | 22781217-4             | 706.651.611-74                    | cpf                                | 706.651.611-74             | 2024-02-15 15:09:51                | 2024-02-15 18:09:51         |

---

## <a id='filhos-usuarios-csv'></a>filhos_usuarios.csv

**Total de Registros**: 16

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | filho_usuario_id | int64 | 1 |
| 2 | filho_usuario_user_id | int64 | 1887 |
| 3 | filho_usuario_nome | object | Elisa Santiago Severo Xavier |
| 4 | filho_usuario_sexo | object | Feminino |
| 5 | filho_usuario_data_nascimento | object | 2021-06-22 |

### Amostra de Dados

|   filho_usuario_id |   filho_usuario_user_id | filho_usuario_nome            | filho_usuario_sexo   | filho_usuario_data_nascimento   |  
|-------------------:|------------------------:|:------------------------------|:---------------------|:--------------------------------|  
|                  1 |                    1887 | Elisa Santiago Severo Xavier  | Feminino             | 2021-06-22                      |  
|                  2 |                     211 | ANTHONY HENRIQUE ISIDIO NUNES | Masculino            | 2022-07-31                      |  
|                  3 |                    1579 | Davi Sales Moreira            | Masculino            | 2014-03-04                      |  
|                  4 |                    1579 | Julia Sales Costa             | Feminino             | 2018-02-26                      |  
|                  5 |                    1579 | Helena Sales                  | Feminino             | 2019-08-31                      |

---

## <a id='historico-titulacoes-csv'></a>historico_titulacoes.csv

**Total de Registros**: 190

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | historico_titulacao_id | int64 | 1 |
| 2 | historico_titulacao_user_id | int64 | 2347 |
| 3 | historico_titulacao_titulacao_id | int64 | 8 |
| 4 | historico_titulacao_anexo | object | 600/2024/02/2347-2347-1708452324.png |
| 5 | historico_titulacao_data_conclusao | object | 2024-02-06 |
| 6 | historico_titulacao_registration_date | object | 2024-02-20 15:05:24 |
| 7 | historico_titulacao_lastupdate | object | 2024-02-20 18:05:24 |

### Amostra de Dados

|   historico_titulacao_id |   historico_titulacao_user_id |   historico_titulacao_titulacao_id | historico_titulacao_anexo            | historico_titulacao_data_conclusao   | historico_titulacao_registration_date   | historico_titulacao_lastupdate   |  
|-------------------------:|------------------------------:|-----------------------------------:|:-------------------------------------|:-------------------------------------|:----------------------------------------|:---------------------------------|  
|                        1 |                          2347 |                                  8 | 600/2024/02/2347-2347-1708452324.png | 2024-02-06                           | 2024-02-20 15:05:24                     | 2024-02-20 18:05:24              |  
|                        2 |                          1974 |                                  5 | 600/2024/02/1974-1974-1708456873.pdf | 2024-01-19                           | 2024-02-20 16:21:13                     | 2024-02-20 19:21:13              |  
|                        3 |                          2372 |                                  5 | 600/2024/02/2372-2372-1708530129.pdf | 2024-01-29                           | 2024-02-21 12:42:09                     | 2024-02-21 15:42:09              |  
|                        4 |                          2434 |                                  4 | 600/2024/02/2434-2434-1709120466.pdf | 2024-02-28                           | 2024-02-28 08:41:06                     | 2024-02-28 11:41:06              |  
|                        5 |                          2457 |                                  4 | 600/2024/03/2457-2457-1709918949.jpg | 2024-03-08                           | 2024-03-08 14:29:09                     | 2024-03-08 17:29:09              |

---

## <a id='lur-habilidades-luria-csv'></a>lur_habilidades_luria.csv

**Total de Registros**: 134

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | habilidade_id | int64 | 1 |
| 2 | habilidade_codigo | object | AT01 |
| 3 | habilidade_descricao | object | Habilidades de Atender Tarefas |
| 4 | habilidade_acao | object | A criança deverá manifestar interesse por um it... |
| 5 | habilidade_orientacao | object | Ex.Um brinquedo ou alimento de preferência da c... |

### Amostra de Dados

|   habilidade_id | habilidade_codigo   | habilidade_descricao           | habilidade_acao                                                                                                      | habilidade_orientacao                                 |  
|----------------:|:--------------------|:-------------------------------|:---------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------|  
|               1 | AT01                | Habilidades de Atender Tarefas | A criança deverá manifestar interesse por um item disponível na mesa.                                                | Ex.Um brinquedo ou alimento de preferência da criança |  
|               2 | AT02                | Habilidades de Atender Tarefas | A criança deverá sentar adequadamente com as mãos na mesa (ou no colo) e pés posicionados.                           | nan                                                   |  
|               3 | AT03                | Habilidades de Atender Tarefas | A criança deverá sentar em um lugar designado pelo terapeuta (mês, chão ou tatame) e completar a atividade proposta. | nan                                                   |  
|               4 | AT04                | Habilidades de Atender Tarefas | A criança deverá sentar e responder pelo nome, fazendo contato visual.                                               | nan                                                   |  
|               5 | IM01                | Habilidades de Imitação        | A criança deverá imitar um movimento simples do terapeuta.                                                           | Ex. Dar um toque na mesa, apertar uma campainha.      |

---

## <a id='lur-habilidades-luria-clients-csv'></a>lur_habilidades_luria_clients.csv

**Total de Registros**: 17,831

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | habilidade_luria_client_id | int64 | 1 |
| 2 | habilidade_id | int64 | 51 |
| 3 | ps_cliente_id | int64 | 576 |
| 4 | habilidade_luria_client_data_inicio | object | 2021-02-24 |
| 5 | habilidade_luria_client_data_andamento | float64 | NULL |
| 6 | habilidade_luria_client_data_dominio | object | 2021-02-24 |
| 7 | habilidade_luria_client_registration_date | object | 2021-02-24 09:16:50 |
| 8 | habilidade_luria_client_lastupdate | object | 2021-02-24 12:16:50 |

### Amostra de Dados

|   habilidade_luria_client_id |   habilidade_id |   ps_cliente_id | habilidade_luria_client_data_inicio   |   habilidade_luria_client_data_andamento | habilidade_luria_client_data_dominio   | habilidade_luria_client_registration_date   | habilidade_luria_client_lastupdate   |  
|-----------------------------:|----------------:|----------------:|:--------------------------------------|-----------------------------------------:|:---------------------------------------|:--------------------------------------------|:-------------------------------------|  
|                            1 |              51 |             576 | 2021-02-24                            |                                      nan | 2021-02-24                             | 2021-02-24 09:16:50                         | 2021-02-24 12:16:50                  |  
|                            2 |              51 |             589 | 2021-03-10                            |                                      nan | 2021-03-10                             | 2021-03-10 09:48:03                         | 2021-03-10 12:48:03                  |  
|                            3 |             101 |             589 | 2021-03-10                            |                                      nan | 2021-03-10                             | 2021-03-10 09:49:41                         | 2021-03-10 12:49:41                  |  
|                            4 |               1 |             589 | 2021-02-09                            |                                      nan | 2021-02-09                             | 2021-03-10 09:50:04                         | 2021-03-10 12:50:04                  |  
|                            5 |               2 |             589 | 2021-02-09                            |                                      nan | 2021-02-09                             | 2021-03-10 09:50:19                         | 2021-03-10 12:50:19                  |

---

## <a id='mbm-aba-areas-csv'></a>mbm_aba_areas.csv

**Total de Registros**: 15

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | area_id | int64 | 1 |
| 2 | area_nome | object | Atenção |
| 3 | area_descricao | object | A terapeuta deverá realizar a ação antes para q... |
| 4 | area_registration_date | object | 2018-10-15 14:31:47 |
| 5 | area_lastupdate | object | 2018-10-15 17:31:47 |

### Amostra de Dados

|   area_id | area_nome            | area_descricao                                                                                                                      | area_registration_date   | area_lastupdate     |  
|----------:|:---------------------|:------------------------------------------------------------------------------------------------------------------------------------|:-------------------------|:--------------------|  
|         1 | Atenção              | nan                                                                                                                                 | 2018-10-15 14:31:47      | 2018-10-15 17:31:47 |  
|         2 | Imitação             | A terapeuta deverá realizar a ação antes para que a criança realize/imite a ação que acabou de visualizar                           | 2018-10-15 14:53:55      | 2018-10-15 17:53:55 |  
|         7 | Linguagem Receptiva  | A terapeuta deve dar o comando verbal, para que a criança compreenda o que está sendo realizado e execute a ação que foi solicitada | 2019-01-11 11:42:46      | 2019-01-11 13:42:46 |  
|         8 | Linguagem Expressiva | nan                                                                                                                                 | 2019-01-11 11:43:34      | 2019-01-11 13:43:34 |  
|        10 | Pré Acadêmico        | nan                                                                                                                                 | 2019-01-11 11:46:18      | 2019-01-11 13:46:18 |

---

## <a id='mbm-aba-atendimento-csv'></a>mbm_aba_atendimento.csv

**Total de Registros**: 654,423

**Total de Colunas**: 10

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | atendimento_id | int64 | 1 |
| 2 | atendimento_data | object | 2019-01-16 00:00:00 |
| 3 | atendimento_user_id | int64 | 4 |
| 4 | atendimento_qtd_sessoes | int64 | 0 |
| 5 | atendimento_paciente_id | int64 | 5 |
| 6 | atendimento_insert_user_id | int64 | 0 |
| 7 | schedule_id | float64 | NULL |
| 8 | atendimento_hr_inicial | float64 | NULL |
| 9 | atendimento_hr_final | float64 | NULL |
| 10 | atendimento_nova_data | float64 | NULL |

### Amostra de Dados

|   atendimento_id | atendimento_data    |   atendimento_user_id |   atendimento_qtd_sessoes |   atendimento_paciente_id |   atendimento_insert_user_id |   schedule_id |   atendimento_hr_inicial |   atendimento_hr_final |   atendimento_nova_data |  
|-----------------:|:--------------------|----------------------:|--------------------------:|--------------------------:|-----------------------------:|--------------:|-------------------------:|-----------------------:|------------------------:|  
|                1 | 2019-01-16 00:00:00 |                     4 |                         0 |                         5 |                            0 |           nan |                      nan |                    nan |                     nan |  
|                2 | 2019-01-18 00:00:00 |                     4 |                         2 |                         5 |                            0 |           nan |                      nan |                    nan |                     nan |  
|                3 | 2019-01-21 00:00:00 |                     4 |                         1 |                        43 |                            0 |           nan |                      nan |                    nan |                     nan |  
|                4 | 2019-01-21 00:00:00 |                     4 |                         1 |                        43 |                            0 |           nan |                      nan |                    nan |                     nan |  
|                5 | 2019-01-22 00:00:00 |                     4 |                         2 |                        37 |                            0 |           nan |                      nan |                    nan |                     nan |

---

## <a id='mbm-aba-atividades-csv'></a>mbm_aba_atividades.csv

**Total de Registros**: 1,924

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | atividade_id | int64 | 33 |
| 2 | atividade_nome | object | Alternar o olhar entre dois objetos |
| 3 | atividade_descricao | float64 | NULL |
| 4 | atividade_image | float64 | NULL |
| 5 | atividade_brinquedo | int64 | 0 |
| 6 | atividade_registration_date | object | 2019-01-16 15:23:32 |
| 7 | atividade_lastupdate | object | 2019-01-16 17:23:32 |

### Amostra de Dados

|   atividade_id | atividade_nome                      |   atividade_descricao |   atividade_image |   atividade_brinquedo | atividade_registration_date   | atividade_lastupdate   |  
|---------------:|:------------------------------------|----------------------:|------------------:|----------------------:|:------------------------------|:-----------------------|  
|             33 | Alternar o olhar entre dois objetos |                   nan |               nan |                     0 | 2019-01-16 15:23:32           | 2019-01-16 17:23:32    |  
|             34 | Exploração do rosto                 |                   nan |               nan |                     0 | 2019-01-16 15:24:42           | 2019-01-16 17:24:42    |  
|             35 | Mexer no que vê                     |                   nan |               nan |                     0 | 2019-01-16 15:25:05           | 2019-01-16 17:25:05    |  
|             37 | Seguir objetos com o olhar          |                   nan |               nan |                     0 | 2019-01-16 17:55:45           | 2019-01-16 19:55:45    |  
|             38 | Fazer sombras na parede             |                   nan |               nan |                     0 | 2019-01-16 17:56:19           | 2019-01-16 19:56:19    |

---

## <a id='mbm-aba-atv-prg-csv'></a>mbm_aba_atv_prg.csv

**Total de Registros**: 2,877

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 52 |
| 2 | programa_id | int64 | 12 |
| 3 | atividade_id | int64 | 54 |

### Amostra de Dados

|   id |   programa_id |   atividade_id |  
|-----:|--------------:|---------------:|  
|   52 |            12 |             54 |  
|   54 |            12 |             56 |  
|   94 |            12 |             57 |  
|  595 |            74 |            365 |  
|  596 |            73 |            365 |

---

## <a id='mbm-aba-comportamentos-csv'></a>mbm_aba_comportamentos.csv

**Total de Registros**: 60

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | comportamento_id | int64 | 4 |
| 2 | comportamento_nome | object | Tolerância à frustração  |
| 3 | comportamento_descricao | float64 | NULL |
| 4 | comportamento_registration_date | object | 2019-05-15 18:29:59 |
| 5 | comportamento_lastupdate | object | 2019-05-15 21:29:59 |

### Amostra de Dados

|   comportamento_id | comportamento_nome            |   comportamento_descricao | comportamento_registration_date   | comportamento_lastupdate   |  
|-------------------:|:------------------------------|--------------------------:|:----------------------------------|:---------------------------|  
|                  4 | Tolerância à frustração       |                       nan | 2019-05-15 18:29:59               | 2019-05-15 21:29:59        |  
|                  6 | Chorar durante a atividade    |                       nan | 2019-05-15 18:30:38               | 2019-05-15 21:30:38        |  
|                  7 | Recusar fazer a atividade     |                       nan | 2019-05-15 18:30:57               | 2019-05-15 21:30:57        |  
|                  8 | Jogar objeto no chão          |                       nan | 2019-05-15 18:31:13               | 2019-05-15 21:31:13        |  
|                  9 | Levantar no meio da atividade |                       nan | 2019-05-15 18:31:26               | 2019-05-15 21:31:26        |

---

## <a id='mbm-aba-patient-consults-csv'></a>mbm_aba_patient_consults.csv

**Total de Registros**: 30,324

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | consult_id | int64 | 2298 |
| 2 | consult_pacient | int64 | 5 |
| 3 | consult_date_start | object | 2019-01-15 |
| 4 | consult_date_end | object | 2019-01-31 |
| 5 | last_consult_id | float64 | 20.0 |

### Amostra de Dados

|   consult_id |   consult_pacient | consult_date_start   | consult_date_end   |   last_consult_id |  
|-------------:|------------------:|:---------------------|:-------------------|------------------:|  
|         2298 |                 5 | 2019-01-15           | 2019-01-31         |                20 |  
|         2299 |                 5 | 2019-01-15           | 2019-01-31         |                20 |  
|         2300 |                 5 | 2019-01-15           | 2019-01-31         |                20 |  
|         2301 |                 5 | 2019-01-15           | 2019-01-31         |                20 |  
|         2302 |                 5 | 2019-01-21           | 2019-01-25         |                28 |

---

## <a id='mbm-aba-patient-programa-consultas-csv'></a>mbm_aba_patient_programa_consultas.csv

**Total de Registros**: 28,943

**Total de Colunas**: 12

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | prog_cons_id | int64 | 196138 |
| 2 | programa_id | float64 | 53.0 |
| 3 | consulta_id | int64 | 2298 |
| 4 | area_profissional_id | float64 | NULL |
| 5 | responsavel_id | float64 | NULL |
| 6 | area_id | float64 | 2.0 |
| 7 | atividade_id | float64 | NULL |
| 8 | status | object | Intervenção |
| 9 | del | object | NAO |
| 10 | user_id | float64 | NULL |
| 11 | registration_date | float64 | NULL |
| 12 | lastupdate | float64 | NULL |

### Amostra de Dados

|   prog_cons_id |   programa_id |   consulta_id |   area_profissional_id |   responsavel_id |   area_id |   atividade_id | status      | del   |   user_id |   registration_date |   lastupdate |  
|---------------:|--------------:|--------------:|-----------------------:|-----------------:|----------:|---------------:|:------------|:------|----------:|--------------------:|-------------:|  
|         196138 |            53 |          2298 |                    nan |              nan |         2 |            nan | Intervenção | NAO   |       nan |                 nan |          nan |  
|         196139 |            50 |          2299 |                    nan |              nan |         1 |            nan | Intervenção | NAO   |       nan |                 nan |          nan |  
|         196140 |            44 |          2300 |                    nan |              nan |        10 |            nan | Intervenção | NAO   |       nan |                 nan |          nan |  
|         196141 |            45 |          2301 |                    nan |              nan |        10 |            nan | Intervenção | NAO   |       nan |                 nan |          nan |  
|         196142 |            45 |          2302 |                    nan |              nan |        10 |            nan | Intervenção | NAO   |       nan |                 nan |          nan |

---

## <a id='mbm-aba-programas-csv'></a>mbm_aba_programas.csv

**Total de Registros**: 231

**Total de Colunas**: 13

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | programa_id | int64 | 10 |
| 2 | area_id | int64 | 1 |
| 3 | programa_nome | object | Desempenho Visual (Área: Atenção) |
| 4 | programa_avaliacao | int64 | 1 |
| 5 | programa_objetivo | object | Esse programa tem o objetivo de trabalhar a cap... |
| 6 | programa_procedimento | object | Retirar contato visual por três segundos, repet... |
| 7 | programa_imagem_procedimento | float64 | NULL |
| 8 | programa_descricao | float64 | NULL |
| 9 | programa_como_realizar | object | A aplicadora deverá certificar que a criança es... |
| 10 | programa_resposta_da_crianca | object | A criança deverá colocar o estímulo junto ao ou... |
| 11 | programa_consequencia_reforcadora | object | Elogio + item reforçador. |
| 12 | programa_registration_date | object | 2019-01-11 11:46:51 |
| 13 | programa_lastupdate | object | 2019-01-11 13:46:51 |

### Amostra de Dados

|   programa_id |   area_id | programa_nome                          |   programa_avaliacao | programa_objetivo                                                                                                                                                 | programa_procedimento                                                                                                                                                                                |   programa_imagem_procedimento |   programa_descricao | programa_como_realizar                                                                  | programa_resposta_da_crianca                                    | programa_consequencia_reforcadora   | programa_registration_date   | programa_lastupdate   |  
|--------------:|----------:|:---------------------------------------|---------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------:|---------------------:|:----------------------------------------------------------------------------------------|:----------------------------------------------------------------|:------------------------------------|:-----------------------------|:----------------------|  
|            10 |         1 | Desempenho Visual (Área: Atenção)      |                    1 | Esse programa tem o objetivo de trabalhar a capacidade da criança de percepção visual, associação de imagens iguais e reprodução de um padrão.                    | Retirar contato visual por três segundos, repetir a instrução e dar ajuda física para a criança olhar. A criança não ganha elogios nem item reforçador. Esperar três segundos e repetir a instrução. |                            nan |                  nan | A aplicadora deverá certificar que a criança está olhando e dizer “coloca com o igual”. | A criança deverá colocar o estímulo junto ao outro igual a ele. | Elogio + item reforçador.           | 2019-01-11 11:46:51          | 2019-01-11 13:46:51   |  
|               |           |                                        |                      | Obs: As ajudas são oferecidas de acordo com a habilidade da criança, começando com mais ajuda para menos, até estar realizando a atividade de forma independente. |                                                                                                                                                                                                      |                                |                      |                                                                                         |                                                                 |                                     |                              |                       |  
|            11 |        23 | Percepção Auditiva (Área: Sensorial)   |                    1 | nan                                                                                                                                                               | nan                                                                                                                                                                                                  |                            nan |                  nan | nan                                                                                     | nan                                                             | nan                                 | 2019-01-11 11:51:22          | 2019-01-11 13:51:22   |  
|            12 |        23 | Percepção Tátil  (Área: Sensorial)     |                    1 | nan                                                                                                                                                               | nan                                                                                                                                                                                                  |                            nan |                  nan | nan                                                                                     | nan                                                             | nan                                 | 2019-01-11 11:51:51          | 2019-01-11 13:51:51   |  
|            14 |        23 | Percepção Gustativa  (Área: Sensorial) |                    1 | nan                                                                                                                                                               | nan                                                                                                                                                                                                  |                            nan |                  nan | nan                                                                                     | nan                                                             | nan                                 | 2019-01-11 13:36:40          | 2019-01-11 15:36:40   |  
|            15 |        23 | Percepção Olfativa  (Área: Sensorial)  |                    1 | nan                                                                                                                                                               | nan                                                                                                                                                                                                  |                            nan |                  nan | nan                                                                                     | nan                                                             | nan                                 | 2019-01-11 13:37:11          | 2019-01-11 15:37:11   |

---

## <a id='mbm-aba-validate-answers-csv'></a>mbm_aba_validate_answers.csv

**Total de Registros**: 698,914

**Total de Colunas**: 22

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | validate_id | int64 | 36 |
| 2 | validate_paciente | int64 | 43 |
| 3 | validate_programa | int64 | 20 |
| 4 | validate_atividade | int64 | 519 |
| 5 | validate_comportamento | float64 | NULL |
| 6 | validate_comportamento_qtd | float64 | NULL |
| 7 | validate_tempo_espera | float64 | 0.0 |
| 8 | validate_tipo_tempo_espera | float64 | 2.0 |
| 9 | validate_qtd_recusa | float64 | 0.0 |
| 10 | validate_qtd_fisica_total | float64 | 0.0 |
| 11 | validate_qtd_fisica_parcial | float64 | 0.0 |
| 12 | validate_qtd_dica_fisica | float64 | 0.0 |
| 13 | validate_qtd_dica_verbal | float64 | 0.0 |
| 14 | validate_qtd_indep | float64 | 22.0 |
| 15 | validate_consulta_id | int64 | 30 |
| 16 | validate_obs | float64 | NULL |
| 17 | validate_atendimento_id | int64 | 4 |
| 18 | validate_habilidade_adquirida | float64 | 0.0 |
| 19 | validate_habilidade_adquirida_aprovada | object | NAO |
| 20 | validate_qtd_dica_gestual | float64 | 0.0 |
| 21 | validate_frequencia | int64 | 0 |
| 22 | validate_duracao_comportamento | object | 0 days |

### Amostra de Dados

|   validate_id |   validate_paciente |   validate_programa |   validate_atividade |   validate_comportamento |   validate_comportamento_qtd |   validate_tempo_espera |   validate_tipo_tempo_espera |   validate_qtd_recusa |   validate_qtd_fisica_total |   validate_qtd_fisica_parcial |   validate_qtd_dica_fisica |   validate_qtd_dica_verbal |   validate_qtd_indep |   validate_consulta_id |   validate_obs |   validate_atendimento_id |   validate_habilidade_adquirida | validate_habilidade_adquirida_aprovada   |   validate_qtd_dica_gestual |   validate_frequencia | validate_duracao_comportamento   |  
|--------------:|--------------------:|--------------------:|---------------------:|-------------------------:|-----------------------------:|------------------------:|-----------------------------:|----------------------:|----------------------------:|------------------------------:|---------------------------:|---------------------------:|---------------------:|-----------------------:|---------------:|--------------------------:|--------------------------------:|:-----------------------------------------|----------------------------:|----------------------:|:---------------------------------|  
|            36 |                  43 |                  20 |                  519 |                      nan |                          nan |                       0 |                            2 |                     0 |                           0 |                             0 |                          0 |                          0 |                   22 |                     30 |            nan |                         4 |                               0 | NAO                                      |                           0 |                     0 | 0 days                           |  
|            43 |                  37 |                  57 |                  216 |                      nan |                          nan |                       0 |                            1 |                     0 |                           0 |                             0 |                          0 |                          0 |                    1 |                     34 |            nan |                         6 |                               0 | NAO                                      |                           0 |                     0 | 0 days                           |  
|            44 |                  37 |                  57 |                  219 |                      nan |                          nan |                       0 |                            1 |                     0 |                           0 |                             0 |                          0 |                          0 |                    1 |                     34 |            nan |                         6 |                               0 | NAO                                      |                           0 |                     0 | 0 days                           |  
|            45 |                  37 |                  57 |                  217 |                      nan |                          nan |                       0 |                            1 |                     0 |                           0 |                             0 |                          0 |                          0 |                    1 |                     34 |            nan |                         6 |                               0 | NAO                                      |                           0 |                     0 | 0 days                           |  
|            46 |                  37 |                  57 |                  213 |                      nan |                          nan |                       0 |                            1 |                     0 |                           0 |                             0 |                          0 |                          0 |                    1 |                     34 |            nan |                         6 |                               0 | NAO                                      |                           0 |                     0 | 0 days                           |

---

## <a id='mbm-clients-videos-csv'></a>mbm_clients_videos.csv

**Total de Registros**: 2,962

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | video_id | int64 | 3 |
| 2 | client_id | int64 | 36 |
| 3 | video_date | object | 2019-04-15 |
| 4 | video_url | int64 | 330490363 |
| 5 | video_description | object | Imitando o leão e ouvindo a musica "leãozinho". |
| 6 | video_registration_date | object | 2019-04-16 07:35:39 |
| 7 | video_lastupdate | object | 2019-04-16 10:35:39 |

### Amostra de Dados

|   video_id |   client_id | video_date   |   video_url | video_description                               | video_registration_date   | video_lastupdate    |  
|-----------:|------------:|:-------------|------------:|:------------------------------------------------|:--------------------------|:--------------------|  
|          3 |          36 | 2019-04-15   |   330490363 | nan                                             | 2019-04-16 07:35:39       | 2019-04-16 10:35:39 |  
|          9 |          36 | 2019-04-14   |   330490286 | nan                                             | 2019-04-16 07:36:51       | 2019-04-16 10:36:51 |  
|         11 |          36 | 2019-04-15   |   330490363 | nan                                             | 2019-04-17 21:22:20       | 2019-04-18 00:22:20 |  
|         14 |          36 | 2019-04-29   |   333112149 | Imitando o leão e ouvindo a musica "leãozinho". | 2019-04-29 10:56:44       | 2019-04-29 13:56:44 |  
|         16 |          36 | 2019-04-29   |   333123880 | Batendo a mão na minha no balanço               | 2019-04-29 11:51:30       | 2019-04-29 14:51:30 |

---

## <a id='mbm-clients-videos-tutorial-csv'></a>mbm_clients_videos_tutorial.csv

**Total de Registros**: 86

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | video_id | int64 | 5 |
| 2 | client_id | float64 | NULL |
| 3 | video_title | object | Visualizar documentos paciente |
| 4 | video_date | object | 2020-06-23 |
| 5 | video_url | int64 | 431916935 |
| 6 | video_description | object | Como visualizar os documentos anexados do paciente |
| 7 | video_registration_date | object | 2020-06-23 16:22:23 |
| 8 | video_lastupdate | object | 2020-06-23 19:22:23 |

### Amostra de Dados

|   video_id |   client_id | video_title                                                   | video_date   |   video_url | video_description                                  | video_registration_date   | video_lastupdate    |  
|-----------:|------------:|:--------------------------------------------------------------|:-------------|------------:|:---------------------------------------------------|:--------------------------|:--------------------|  
|          5 |         nan | Visualizar documentos paciente                                | 2020-06-23   |   431916935 | Como visualizar os documentos anexados do paciente | 2020-06-23 16:22:23       | 2020-06-23 19:22:23 |  
|          6 |         nan | Visualizar os dados principais do paciente                    | 2020-06-23   |   431921310 | nan                                                | 2020-06-23 16:33:11       | 2020-06-23 19:33:11 |  
|          8 |         nan | Visualizar os brinquedos e cartas de identificação e nomeação | 2020-06-23   |   431923890 | nan                                                | 2020-06-23 16:46:38       | 2020-06-23 19:46:38 |  
|          9 |         nan | Colocar os videos no VIMEO                                    | 2020-06-23   |   431928140 | nan                                                | 2020-06-23 16:56:46       | 2020-06-23 19:56:46 |  
|         10 |         nan | Visualizar e realizar evolução qualitativa                    | 2020-06-23   |   431931124 | nan                                                | 2020-06-23 17:06:42       | 2020-06-23 20:06:42 |

---

## <a id='ps-anamnese-csv'></a>ps_anamnese.csv

**Total de Registros**: 8,231

**Total de Colunas**: 15

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | anamnese_id | int64 | 1 |
| 2 | anamnese_paciente_id | int64 | 19 |
| 3 | anamnese_data_medicamentos | object | 2022-01-10 |
| 4 | anamnese_medicamentos | object | medicamento |
| 5 | anamnese_medico | object | NOME DO MEDICO |
| 6 | anamnese_plano_terapeutico | object | Plano |
| 7 | anamnese_consideracoes_supervisor | object | OBJETIVOS GERAIS VBMAPP (AGOSTO/JANEIRO)- BREND... |
| 8 | anamnese_profissional_id | float64 | 606.0 |
| 9 | anamnese_registration_date | object | 2021-03-19 18:36:36 |
| 10 | anamnese_lastupdate | object | 2021-03-19 21:45:45 |
| 11 | anamnese_tempo_meta | float64 | NULL |
| 12 | anamnese_psicologia_qtde | float64 | NULL |
| 13 | anamnese_fonoaudiologia_qtde | float64 | NULL |
| 14 | anamnese_terapia_ocupacional_qtde | float64 | NULL |
| 15 | anamnese_outros_qtde | float64 | NULL |

### Amostra de Dados

|   anamnese_id |   anamnese_paciente_id | anamnese_data_medicamentos   | anamnese_medicamentos   | anamnese_medico                            | anamnese_plano_terapeutico                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | anamnese_consideracoes_supervisor                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |   anamnese_profissional_id | anamnese_registration_date   | anamnese_lastupdate   |   anamnese_tempo_meta |   anamnese_psicologia_qtde |   anamnese_fonoaudiologia_qtde |   anamnese_terapia_ocupacional_qtde |   anamnese_outros_qtde |  
|--------------:|-----------------------:|:-----------------------------|:------------------------|:-------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------:|:-----------------------------|:----------------------|----------------------:|---------------------------:|-------------------------------:|------------------------------------:|-----------------------:|  
|             1 |                     19 | nan                          | nan                     | nan                                        | nan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | nan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                        nan | 2021-03-19 18:36:36          | 2021-03-19 21:45:45   |                   nan |                        nan |                            nan |                                 nan |                    nan |  
|             2 |                    708 | 2022-01-10                   | medicamento             | NOME DO MEDICO                             | Plano                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | nan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                        nan | 2021-03-22 08:23:47          | 2023-02-09 16:41:35   |                   nan |                        nan |                            nan |                                 nan |                    nan |  
|             3 |                    666 | 1969-12-31                   | nan                     | nan                                        | OBJETIVOS GERAIS VBMAPP (AGOSTO/JANEIRO)- BRENDA                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | OBJETIVOS GERAIS VBMAPP (AGOSTO/JANEIRO)- BRENDA                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                        606 | 2021-03-22 18:37:43          | 2023-10-17 19:18:10   |                   nan |                        nan |                            nan |                                 nan |                    nan |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | MANDO:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | MANDO:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Espontaneamente pedir por diferentes informações verbais usando pronomes interrogativos ou uma palavra interrogativa (ex. Qual o seu nome? Onde eu vou?) – Aumentar repertório e dar função.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | -Espontaneamente pedir por diferentes informações verbais usando pronomes interrogativos ou uma palavra interrogativa (ex. Qual o seu nome? Onde eu vou?) – Aumentar repertório e dar função.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Dá direções, instruções ou explanações sobre como fazer algo ou como participar de uma atividade (ex. Você coloca primeiro a cola, então cole. Você sente aqui enquanto eu pego um livro) - reduzir dicas.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | -Dá direções, instruções ou explanações sobre como fazer algo ou como participar de uma atividade (ex. Você coloca primeiro a cola, então cole. Você sente aqui enquanto eu pego um livro) - reduzir dicas.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | TATO:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | TATO:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Tato de diferentes preposições (ex. em, fora, sobre, embaixo) e pronomes (ex. eu, você e meu)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | -Tato de diferentes preposições (ex. em, fora, sobre, embaixo) e pronomes (ex. eu, você e meu)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Tato de adjetivos diferentes, excluindo cores e formas (ex. grande, pequeno, longo, curto) e de advérbios (ex. rápido, devagar, silenciosamente, gentilmente) /opostos.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | -Tato de adjetivos diferentes, excluindo cores e formas (ex. grande, pequeno, longo, curto) e de advérbios (ex. rápido, devagar, silenciosamente, gentilmente) /opostos.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | LINGUAGEM RECEPTIVA (Comportamento de ouvinte):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | LINGUAGEM RECEPTIVA (Comportamento de ouvinte):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Seguimento de instruções de 3 passos (ex.: Pegue seu casaco, pendure-o e sente.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Seguimento de instruções de 3 passos (ex.: Pegue seu casaco, pendure-o e sente.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Aumentar repertorio de ouvinte (nomes, verbos, adjetivos, etc.).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Aumentar repertorio de ouvinte (nomes, verbos, adjetivos, etc.).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | HABILIDADE DE PERCEPÇÃO VISUAL E ESCOLHA DE ACORDO COM O MODELO (VP/MTS):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | HABILIDADE DE PERCEPÇÃO VISUAL E ESCOLHA DE ACORDO COM O MODELO (VP/MTS):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Demonstrar pareamento generalizado de não-idêntico, num arranjo não organizado de 10, com 3 estímulos similares (i.e. pareia novos itens na primeira tentativa).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Demonstrar pareamento generalizado de não-idêntico, num arranjo não organizado de 10, com 3 estímulos similares (i.e. pareia novos itens na primeira tentativa).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Completar tipos de blocos diferentes, parquety, quebra-cabeças de formas, ou tarefas similares em pelo menos 8 peças diferentes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Completar tipos de blocos diferentes, parquety, quebra-cabeças de formas, ou tarefas similares em pelo menos 8 peças diferentes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Categorização com arranjo de 5, sem um modelo (ex.: animais, roupas, mobílias).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | -Categorização com arranjo de 5, sem um modelo (ex.: animais, roupas, mobílias).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Continuar 20 padrões de três passos, sequências, ou tarefas de seriação (ex.: estrela, triângulo, coração, estrela, triângulo...).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | -Continuar 20 padrões de três passos, sequências, ou tarefas de seriação (ex.: estrela, triângulo, coração, estrela, triângulo...).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | BRINCAR INDEPENDENTE:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | BRINCAR INDEPENDENTE:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Independentemente desenhar ou escrever em livros de atividades pré-acadêmicas por 5 minutos (ex. ponto-aponto, jogo de pareamento, labirinto, traça letras e números).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | - Independentemente desenhar ou escrever em livros de atividades pré-acadêmicas por 5 minutos (ex. ponto-aponto, jogo de pareamento, labirinto, traça letras e números).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | COMPORTAMENTO E BRINCAR SOCIAL:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | COMPORTAMENTO E BRINCAR SOCIAL:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Iniciar interação física com um colega (ex.: um empurrão em um carro, segura a mão, brinca de roda).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | -Iniciar interação física com um colega (ex.: um empurrão em um carro, segura a mão, brinca de roda).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Espontaneamente emitir mando aos colegas (ex.: minha vez, empurre-me, olhe! Venha.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | -Espontaneamente emitir mando aos colegas (ex.: minha vez, empurre-me, olhe! Venha.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Engajar em brincadeira social continuada com colegas sem dicas de adultos ou reforçamento (ex.: cooperativamente cria um conjunto de jogo, joga água).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | -Engajar em brincadeira social continuada com colegas sem dicas de adultos ou reforçamento (ex.: cooperativamente cria um conjunto de jogo, joga água).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Espontaneamente responde a mandos de colegas (ex.: puxe-me no carrinho. Eu quero o trem).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | -Espontaneamente responde a mandos de colegas (ex.: puxe-me no carrinho. Eu quero o trem).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Espontaneamente pedir aos colegas para participar de jogos, brincadeira social etc., (ex. Vamos garotos. Vamos cavar um buraco.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Espontaneamente pedir aos colegas para participar de jogos, brincadeira social etc., (ex. Vamos garotos. Vamos cavar um buraco.)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Espontaneamente cooperar com um par para atingir um resultado específico (Uma criança segura um balde enquanto o coloca a água).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Espontaneamente cooperar com um par para atingir um resultado específico (Uma criança segura um balde enquanto o coloca a água).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Espontaneamente emitir mandos para colegas com um pronome interrogativo (ex. Onde você está indo? O que é isto? Quem você está sendo?).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | -Espontaneamente emitir mandos para colegas com um pronome interrogativo (ex. Onde você está indo? O que é isto? Quem você está sendo?).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Intraverbalmente responder a 5 diferentes perguntas ou afirmações de um colega (ex., verbalmente responde a Do que você quer brincar?).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | -Intraverbalmente responder a 5 diferentes perguntas ou afirmações de um colega (ex., verbalmente responde a Do que você quer brincar?).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Engajar-se em atividades de brincadeira social de faz de conta, com colegas , sem dicas de adultos ou reforçamento (ex. brincar de se vestir, acting out vídeos, brincar de casinha).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | -Engajar-se em atividades de brincadeira social de faz de conta, com colegas , sem dicas de adultos ou reforçamento (ex. brincar de se vestir, acting out vídeos, brincar de casinha).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Engaja-se em trocas verbais de tópico com colegas (ex. a criança volta e fala sobre fazer um riacho em uma caixa de areia).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | -Engaja-se em trocas verbais de tópico com colegas (ex. a criança volta e fala sobre fazer um riacho em uma caixa de areia).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | INTRAVERBAL:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | INTRAVERBAL:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Responder duas questões após ler trechos curtos em um livro (+15 palavras).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | -Responder duas questões após ler trechos curtos em um livro (+15 palavras).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | -Aumentar repertorio intravebal, relatos maiores e com coerência.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | -Aumentar repertorio intravebal, relatos maiores e com coerência.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | HABILIDADES DE GRUPO E ROTINA DE SALA DE AULA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | HABILIDADES DE GRUPO E ROTINA DE SALA DE AULA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Sentar em um pequeno grupo sem comportamento inadequado ou tentar sair do grupo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | - Sentar em um pequeno grupo sem comportamento inadequado ou tentar sair do grupo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Sentar em um pequeno grupo, atentar ao professor ou material por 50% do período e responder a 5 SDs do professor.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | - Sentar em um pequeno grupo, atentar ao professor ou material por 50% do período e responder a 5 SDs do professor.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Responder a grupos diferentes de instruções ou questões sem dicas diretas em um grupo de crianças (ex. Todos de pé. Alguém está usando uma camisa vermelha?)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | - Responder a grupos diferentes de instruções ou questões sem dicas diretas em um grupo de crianças (ex. Todos de pé. Alguém está usando uma camisa vermelha?)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Trabalhar independentemente por em um grupo e se mantém engajado na tarefa por 50% do período.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | - Trabalhar independentemente por em um grupo e se mantém engajado na tarefa por 50% do período.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Adquirir novos comportamentos em um formato de ensino em grupo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | - Adquirir novos comportamentos em um formato de ensino em grupo.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Sentar-se em uma sessão em grupo sem comportamentos disruptivos e responder a questões intraverbais.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | - Sentar-se em uma sessão em grupo sem comportamentos disruptivos e responder a questões intraverbais.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | HABILIDADE DE LEITURA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | HABILIDADE DE LEITURA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Realizar leitura de palavras simples e parear palavra/figura correspondentes (ex. pareia a palavra escrita pássaro à figura de um pássaro).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | - Realizar leitura de palavras simples e parear palavra/figura correspondentes (ex. pareia a palavra escrita pássaro à figura de um pássaro).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | HABILIDADE DE ESCRITA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | HABILIDADE DE ESCRITA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Soletrar e escrever de forma legível seu próprio nome sem fazer cópia.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | - Soletrar e escrever de forma legível seu próprio nome sem fazer cópia.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | HABILIDADE MATEMÁTICA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | HABILIDADE MATEMÁTICA:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | - Identificar como ouvinte comparações diferentes envolvendo medidas (ex.: Me mostre o mais ou o menos, o grande ou o pequeno, o muito ou o pouco, o cheio ou o vazio, o alto ou o baixo).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | - Identificar como ouvinte comparações diferentes envolvendo medidas (ex.: Me mostre o mais ou o menos, o grande ou o pequeno, o muito ou o pouco, o cheio ou o vazio, o alto ou o baixo).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | METAS VINELAND                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | METAS VINELAND                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |                            |                              |                       |                       |                            |                                |                                     |                        |  
|               |                        |                              |                         |                                            | Compreender significado das palavras (principalmente emoções e situações do dia a dia), aumentar tempo de atenção, (intraverbal) relatar experiências espontânea, transmitir recados simples, realizar perguntas (o que, onde, quem, porque, quando), relatar experiências com detalhes, dias da semana, mês e ano, relatar número de telefone e endereço, flexibilidade/exprimir ideias em mais de uma versão, letras do alfabeto, sinais/simbolos(mais, menos, vezes, vírgula, ponto, interrogação...), escrever nome completo, leitura de palavras simples, escrever palavras simples, compreender função de objetos (dinheiro e relogio), realizar imitação complexa após algum tempo, verbalizar emoções, socialização (interação social), seguimento de passos de instrução mais complexos, planejamento, capacidade de decisão e resolução de problemas.                                                                                                                            | Compreender significado das palavras (principalmente emoções e situações do dia a dia), aumentar tempo de atenção, (intraverbal) relatar experiências espontânea, transmitir recados simples, realizar perguntas (o que, onde, quem, porque, quando), relatar experiências com detalhes, dias da semana, mês e ano, relatar número de telefone e endereço, flexibilidade/exprimir ideias em mais de uma versão, letras do alfabeto, sinais/símbolos(mais, menos, vezes, vírgula, ponto, interrogação...), escrever nome completo, leitura de palavras simples, escrever palavras simples, compreender função de objetos (dinheiro e relógio), realizar imitação complexa após algum tempo, verbalizar emoções, socialização (interação social), seguimento de passos de instrução mais complexos, planejamento, capacidade de decisão e resolução de problemas. |                            |                              |                       |                       |                            |                                |                                     |                        |  
|             4 |                    976 | nan                          | Depakene                | Dr. Hélio Van Der Linden / Dr. Paulo Edson | Gabriela, setembro/22: tolerância à frustração, tempo de espera, troca de turno, quebra-cabeça 30 peças, responder corretamente ¨sim¨ ou ¨não¨ para uma pergunta, responder saudações, iniciar saudações, sequência lógica, reconto de histórias, se portar de forma adequada perto dos pares, nomear um som do ambiente (animais, meios de transporte, instrumentos musicais), nomear peças do vestuário, nomear objetos do cotidiano, nomear objetos e móveis, nomear lugares, nomear ações, solicitar objetos utilizando frases mais complexas, faz de conta, alfabetização, consciência fonológica, se vestir e despir-se sozinho, assoar o nariz, comer usando garfo e faca, realizar atividades motoras finas (abrir garrafas, abotoar e desabotoar botões, abrir e fechar zíper, amarrar cadarços), nomear profissões, nomear lugares, leitura, escrita, matemática, intraverbal, interação social, agitação psicomotora, participar de uma canção demostrando as ações e cantando. | nan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                        606 | 2021-04-08 17:13:36          | 2024-01-30 18:04:24   |                   nan |                        nan |                            nan |                                 nan |                    nan |  
|             5 |                    629 | 1969-12-31                   | nan                     | nan                                        | FRANCIELY outubro/2022: Leitura, matemática, raciocínio lógico, escrita, intraverbal;                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | nan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |                        nan | 2021-04-09 15:09:21          | 2023-05-10 22:54:47   |                   nan |                        nan |                            nan |                                 nan |                    nan |

---

## <a id='ps-anamnese-itens-csv'></a>ps_anamnese_itens.csv

**Total de Registros**: 35,644

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | anamnese_item_id | int64 | 7 |
| 2 | anamnese_item_descricao | object | A |
| 3 | anamnese_id | int64 | 2 |

### Amostra de Dados

|   anamnese_item_id | anamnese_item_descricao          |   anamnese_id |  
|-------------------:|:---------------------------------|--------------:|  
|                  7 | A                                |             2 |  
|                  8 | B                                |             2 |  
|                  9 | Médico: Dr. Helio Van Der Linden |             4 |  
|                 10 | Parto ok                         |             4 |  
|                 11 | gestação ok                      |             4 |

---

## <a id='ps-avaliacoes-csv'></a>ps_avaliacoes.csv

**Total de Registros**: 6

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | avaliacao_id | int64 | 1 |
| 2 | avaliacao_nome | object | Turma da Lúria |
| 3 | avaliacao_status | object | A |
| 4 | avaliacao_registration_date | object | 2021-07-08 15:27:27 |
| 5 | avaliacao_lastupdate | object | 2021-07-08 18:27:46 |

### Amostra de Dados

|   avaliacao_id | avaliacao_nome         | avaliacao_status   | avaliacao_registration_date   | avaliacao_lastupdate   |  
|---------------:|:-----------------------|:-------------------|:------------------------------|:-----------------------|  
|              1 | Turma da Lúria         | A                  | 2021-07-08 15:27:27           | 2021-07-08 18:27:46    |  
|              2 | Anamnese               | I                  | 2021-07-08 15:35:25           | 2021-07-08 18:36:52    |  
|              3 | Teste Perfil Sensorial | A                  | 2022-01-18 09:38:55           | 2022-01-18 12:39:24    |  
|              4 | Teste Vineland         | A                  | 2022-01-18 09:38:55           | 2022-01-18 12:39:24    |  
|              5 | Relatório Mensal Amil  | A                  | 2022-08-26 11:39:02           | 2022-08-29 18:56:11    |

---

## <a id='ps-care-rooms-csv'></a>ps_care_rooms.csv

**Total de Registros**: 109

**Total de Colunas**: 10

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | room_id | int64 | 1 |
| 2 | room_name | object | C 01 |
| 3 | room_description | object | teste |
| 4 | room_type | int64 | 1 |
| 5 | room_status | int64 | 1 |
| 6 | room_registration_date | object | 2020-09-18 01:44:33 |
| 7 | room_lastupdate | object | 2020-09-18 04:44:33 |
| 8 | room_local_id | int64 | 1 |
| 9 | multiple | int64 | 0 |
| 10 | room_capacidade | int64 | 1 |

### Amostra de Dados

|   room_id | room_name   | room_description   |   room_type |   room_status | room_registration_date   | room_lastupdate     |   room_local_id |   multiple |   room_capacidade |  
|----------:|:------------|:-------------------|------------:|--------------:|:-------------------------|:--------------------|----------------:|-----------:|------------------:|  
|         1 | C 01        | teste              |           1 |             1 | 2020-09-18 01:44:33      | 2020-09-18 04:44:33 |               1 |          0 |                 1 |  
|         2 | C 02        | nan                |           1 |             1 | 2019-05-22 11:44:33      | 2019-05-22 17:44:33 |               1 |          0 |                 1 |  
|         4 | C 03        | nan                |           1 |             1 | 2019-05-22 11:44:33      | 2019-05-22 17:44:33 |               1 |          0 |                 1 |  
|         5 | C 04        | nan                |           1 |             1 | 2019-05-22 11:45:19      | 2019-05-22 17:45:19 |               1 |          0 |                 1 |  
|         6 | HOME 1      | nan                |           0 |             1 | 2019-05-22 11:46:24      | 2019-05-22 14:46:24 |               3 |          0 |                 1 |

---

## <a id='ps-clients-csv'></a>ps_clients.csv

**Total de Registros**: 4,284

**Total de Colunas**: 41

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | client_id | int64 | 14 |
| 2 | client_cpf | object | 029.486.441-51 |
| 3 | client_rg | float64 | 3730154.0 |
| 4 | client_nome | object | JOAQUIM EMANUEL DE SOUZA CARDOSO |
| 5 | client_data_nascimento | object | 2011-11-07 |
| 6 | client_thumb | float64 | NULL |
| 7 | client_nome_responsavel | object | Fernando Castro Morais |
| 8 | client_nome_pai | object | Fernando Henrique Ferreira Cardoso |
| 9 | client_nome_mae | object | Aliene Mayara de Souza Cardoso |
| 10 | client_sexo | object | nao_definido |
| 11 | client_cep | float64 | 76200000.0 |
| 12 | client_endereco | object | Rua Paineiras |
| 13 | client_numero | float64 | 0.0 |
| 14 | client_complemento | object | Qd.04 Lt.03 |
| 15 | client_bairro | object | Brisa da Mata |
| 16 | client_cidade_nome | object | Iporá |
| 17 | client_cidade | float64 | 5210208.0 |
| 18 | client_state | object | GO |
| 19 | client_payment | int64 | 4 |
| 20 | consult_value | float64 | 170.0 |
| 21 | client_professional | float64 | 2.0 |
| 22 | client_escola_nome | object | Colegio Integração |
| 23 | client_escola_ano | object | Segundo Ano do Ensino Fundamental |
| 24 | client_escola_professor | object | Hellen/Sara  |
| 25 | client_escola_periodo | object | Vespertino |
| 26 | client_escola_contato | object | 39281150 |
| 27 | client_registration_date | object | 2023-11-27 11:44:16 |
| 28 | client_update_date | object | 2023-11-27 14:44:16 |
| 29 | client_status | int64 | 3 |
| 30 | client_patalogia_id | float64 | 2.0 |
| 31 | client_tem_supervisor | object | NAO |
| 32 | client_supervisor_id | float64 | 999.0 |
| 33 | client_tem_avaliacao_luria | object | NAO |
| 34 | client_avaliacao_luria_data_inicio_treinamento | object | 2020-12-08 |
| 35 | client_avaliacao_luria_reforcadores | object | Théo, se interessa por dinossauros, carinhos, s... |
| 36 | client_avaliacao_luria_obs_comportamento | object | Théo é uma criança tranquila e simpática. Em co... |
| 37 | client_numero_carteirinha | object | 0064.8000.207541.00-4 |
| 38 | client_cpf_cli | float64 | NULL |
| 39 | client_crm_medico | float64 | NULL |
| 40 | client_nome_medico | float64 | NULL |
| 41 | client_pai_nao_declarado | object | Não |

### Amostra de Dados

|   client_id | client_cpf     |     client_rg | client_nome                      | client_data_nascimento   |   client_thumb | client_nome_responsavel        | client_nome_pai                    | client_nome_mae                   | client_sexo   |    client_cep | client_endereco                            |   client_numero | client_complemento       | client_bairro        | client_cidade_nome   |   client_cidade | client_state   |   client_payment |   consult_value |   client_professional | client_escola_nome   | client_escola_ano                 | client_escola_professor       | client_escola_periodo   | client_escola_contato   | client_registration_date   | client_update_date   |   client_status |   client_patalogia_id | client_tem_supervisor   |   client_supervisor_id | client_tem_avaliacao_luria   | client_avaliacao_luria_data_inicio_treinamento   | client_avaliacao_luria_reforcadores                                      | client_avaliacao_luria_obs_comportamento                                                                                                                                                                                                                                                                                                                                                                                 | client_numero_carteirinha   |   client_cpf_cli |   client_crm_medico |   client_nome_medico | client_pai_nao_declarado   |  
|------------:|:---------------|--------------:|:---------------------------------|:-------------------------|---------------:|:-------------------------------|:-----------------------------------|:----------------------------------|:--------------|--------------:|:-------------------------------------------|----------------:|:-------------------------|:---------------------|:---------------------|----------------:|:---------------|-----------------:|----------------:|----------------------:|:---------------------|:----------------------------------|:------------------------------|:------------------------|:------------------------|:---------------------------|:---------------------|----------------:|----------------------:|:------------------------|-----------------------:|:-----------------------------|:-------------------------------------------------|:-------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------|-----------------:|--------------------:|---------------------:|:---------------------------|  
|          14 | 029.486.441-51 | nan           | JOAQUIM EMANUEL DE SOUZA CARDOSO | nan                      |            nan | nan                            | Fernando Henrique Ferreira Cardoso | Aliene Mayara de Souza Cardoso    | nao_definido  | nan           | nan                                        |             nan | nan                      | nan                  | nan                  |   nan           | nan            |                4 |             nan |                     2 | nan                  | nan                               | nan                           | nan                     | nan                     | 2023-11-27 11:44:16        | 2023-11-27 14:44:16  |               3 |                   nan | NAO                     |                    999 | NAO                          | nan                                              | nan                                                                      | nan                                                                                                                                                                                                                                                                                                                                                                                                                      | nan                         |              nan |                 nan |                  nan | nan                        |  
|          19 | 908.138.981-53 |   3.73015e+06 | PEDRO BARCELOS MORAIS            | 2011-11-07               |            nan | Fernando Castro Morais         | Fernando Castro Morais             | Ilza Barcelos da Silva Morais     | nao_definido  |   7.62e+07    | Rua Paineiras                              |               0 | Qd.04 Lt.03              | Brisa da Mata        | Iporá                |     5.21021e+06 | GO             |                1 |             170 |                     2 | Colegio Integração   | Segundo Ano do Ensino Fundamental | Hellen/Sara                   | Vespertino              | nan                     | 2019-01-18 14:52:38        | 2022-10-13 20:37:48  |               3 |                   nan | NAO                     |                    nan | NAO                          | nan                                              | nan                                                                      | nan                                                                                                                                                                                                                                                                                                                                                                                                                      | nan                         |              nan |                 nan |                  nan | nan                        |  
|          32 | 777.053.431-34 |   3.24251e+13 | MARIA RIBEIRO PARENTE            | 2013-10-11               |            nan | MONICA MARIA DE AQUINO RIBEIRO | Fabiano de Moura Parente           | Monica Maria de Aquino Ribeiro    | nao_definido  |   7.41801e+07 | Rua 1141                                   |             574 | Apartamento 2104         | Setor Marista        | Goiânia              |     5.20871e+06 | GO             |                2 |             nan |                    26 | Colegio Marista      | Infantil 5                        | Ver com a Monica              | Vespertino              | nan                     | 2023-02-08 13:37:31        | 2023-02-08 16:37:31  |               3 |                   nan | NAO                     |                    nan | NAO                          | nan                                              | nan                                                                      | nan                                                                                                                                                                                                                                                                                                                                                                                                                      | nan                         |              nan |                 nan |                  nan | nan                        |  
|          34 | 006.819.001-80 | nan           | THEO BARBOSA BRANDAO             | 2014-09-11               |            nan | nan                            | Starley Vinicius Barbosa           | Karine Duarte Brandão             | nao_definido  |   7.43676e+07 | Avenida Nápoli Qd.1 C/ Roma Edificio Ambar |             380 | Apartamento 202 Bloco 03 | Residencial Eldorado | Goiânia              |     5.20871e+06 | GO             |                4 |             nan |                    25 | Fractal Kids         | Jardim I                          | Gleyce/Marielle -Coordenadora | Vespertino              | 39281150                | 2024-02-22 11:02:09        | 2024-02-22 14:02:09  |               3 |                     2 | NAO                     |                    999 | SIM                          | 2020-12-08                                       | Théo, se interessa por dinossauros, carinhos, slime e quebra-cabeça.     | Théo é uma criança tranquila e simpática. Em contrapartida foram observados comportamentos de fuga de demanda se recusando a realizar atividades de folha, de conteúdo pedagógico. Apresenta ainda baixo contato visual e necessita de ajuda para manter a atenção compartilhada durante os atendimentos.                                                                                                                | nan                         |              nan |                 nan |                  nan | Não                        |  
|          36 | 044.433.234-06 | nan           | MATHEUS VIEIRA CARNIEL SANTOS    | 2015-08-05               |            nan | nan                            | Robson dos Santos                  | Ana Maria Vieira de Castro Santos | nao_definido  |   7.48432e+07 | Rua Manaus                                 |            1230 | Apartamento 1702 SB      | Parque Amazônia      | Goiânia              |     5.20871e+06 | GO             |                4 |               0 |                     2 | Le Petit             | Infantil 4                        | Camila                        | Vespertino              | 3988-8167               | 2024-07-15 13:08:37        | 2024-07-15 13:08:37  |               1 |                     2 | NAO                     |                    999 | SIM                          | 2020-12-08                                       | Matheus Santos, se interessa por miniaturas de carros, letras e números. | Matheus Santos, foi diagnosticado com TEA (Transtorno do Espectro Autista) pelo médico responsável Dr. Hélio van der Linden Júnior. Atualmente Matheus Santos, encontra-se em acompanhamento multidisciplinar com nossa equipe desde agosto de 2018 fazendo 10 horas semanais de aplicação do programa de intervenção da Análise do Comportamento Aplicada – ABA.                                                        | 0064.8000.207541.00-4       |              nan |                 nan |                  nan | Não                        |  
|             |                |               |                                  |                          |                |                                |                                    |                                   |               |               |                                            |                 |                          |                      |                      |                 |                |                  |                 |                       |                      |                                   |                               |                         |                         |                            |                      |                 |                       |                         |                        |                              |                                                  |                                                                          |                                                                                                                                                                                                                                                                                                                                                                                                                          |                             |                  |                     |                      |                            |  
|             |                |               |                                  |                          |                |                                |                                    |                                   |               |               |                                            |                 |                          |                      |                      |                 |                |                  |                 |                       |                      |                                   |                               |                         |                         |                            |                      |                 |                       |                         |                        |                              |                                                  |                                                                          | Em relação ao comportamento Matheus Santos é uma criança tranquila e simpática. Em contrapartida, foram verificados padrões rígidos de comportamento em relação ao ¨tchau¨, dificuldades na socialização, atraso na linguagem verbal e não verbal e presença de estereotipias que podem comprometer seu desempenho nas atividades, desatenção e um perídio de latência longo para dar respostas as atividades propostas. |                             |                  |                     |                      |                            |

---

## <a id='ps-clients-atividades-digitalizadas-csv'></a>ps_clients_atividades_digitalizadas.csv

**Total de Registros**: 570

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | atividade_digitalizada_id | int64 | 1 |
| 2 | client_id | int64 | 818 |
| 3 | atividade_digitalizada_nome | object | Grafomotor  |
| 4 | atividade_digitalizada_data | object | 2021-07-06 |
| 5 | atividade_digitalizada_registration_date | object | 2021-07-06 11:55:51 |
| 6 | atividade_digitalizada_path | object | images/2021/07/anexo-pietro-lucas-cunha-de-oliv... |
| 7 | atividade_digitalizada_type | int64 | 1 |

### Amostra de Dados

|   atividade_digitalizada_id |   client_id | atividade_digitalizada_nome                 | atividade_digitalizada_data   | atividade_digitalizada_registration_date   | atividade_digitalizada_path                                         |   atividade_digitalizada_type |  
|----------------------------:|------------:|:--------------------------------------------|:------------------------------|:-------------------------------------------|:--------------------------------------------------------------------|------------------------------:|  
|                           1 |         818 | Grafomotor                                  | 2021-07-06                    | 2021-07-06 11:55:51                        | images/2021/07/anexo-pietro-lucas-cunha-de-oliveira.jpeg            |                             1 |  
|                           2 |         818 | Grafomotor                                  | 2021-07-06                    | 2021-07-06 11:56:24                        | images/2021/07/anexo-pietro-lucas-cunha-de-oliveira-1625583401.jpeg |                             1 |  
|                           3 |         492 | Grafomotora/ pré acadêmico/ cópia de vogais | 2021-07-08                    | 2021-07-08 09:35:45                        | images/2021/07/anexo-heitor-maia-machado-1625747771.jpeg            |                             1 |  
|                           4 |         605 | Marco Túlio                                 | 2021-07-08                    | 2021-07-08 18:53:12                        | files/2021/07/anexo-marco-tulio-lemes-de-sousa-paiva.pdf            |                             2 |  
|                           5 |         605 | Marco Túlio                                 | 2021-07-01                    | 2021-07-08 18:55:58                        | files/2021/07/anexo-marco-tulio-lemes-de-sousa-paiva-1625781392.pdf |                             2 |

---

## <a id='ps-clients-attachments-csv'></a>ps_clients_attachments.csv

**Total de Registros**: 2,624

**Total de Colunas**: 6

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | attachment_id | int64 | 11 |
| 2 | client_id | int64 | 120 |
| 3 | attachment_name | object | Avaliação Neuro |
| 4 | attachment_registration_date | object | 2019-05-16 13:50:48 |
| 5 | attachment_path | object | files/2019/05/anexo-alaor-souza-figueiredo-de-c... |
| 6 | attachment_type | int64 | 2 |

### Amostra de Dados

|   attachment_id |   client_id | attachment_name        | attachment_registration_date   | attachment_path                                                         |   attachment_type |  
|----------------:|------------:|:-----------------------|:-------------------------------|:------------------------------------------------------------------------|------------------:|  
|              11 |         120 | Avaliação Neuro        | 2019-05-16 13:50:48            | files/2019/05/anexo-alaor-souza-figueiredo-de-carvalho.pages            |                 2 |  
|              12 |         120 | Relatório Justiça      | 2019-05-16 13:51:49            | files/2019/05/anexo-alaor-souza-figueiredo-de-carvalho-1558025530.pages |                 2 |  
|              21 |         407 | 20032020115855_338.pdf | 2020-04-16 09:05:47            | files/2020/04/anexo-walison-jose-de-deus.pdf                            |                 2 |  
|              22 |         407 | download.jpeg          | 2020-04-16 09:06:01            | images/2020/04/anexo-walison-jose-de-deus.jpeg                          |                 1 |  
|              23 |         407 | 20032020115855_338.pdf | 2020-04-16 09:07:19            | files/2020/04/anexo-walison-jose-de-deus-1587038839.pdf                 |                 2 |

---

## <a id='ps-clients-avaliacoes-csv'></a>ps_clients_avaliacoes.csv

**Total de Registros**: 545

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | client_avaliacao_id | int64 | 3 |
| 2 | avaliacao_id | int64 | 1 |
| 3 | client_id | int64 | 576 |

### Amostra de Dados

|   client_avaliacao_id |   avaliacao_id |   client_id |  
|----------------------:|---------------:|------------:|  
|                     3 |              1 |         576 |  
|                     4 |              1 |         589 |  
|                     5 |              1 |         458 |  
|                     6 |              1 |         785 |  
|                     7 |              1 |         666 |

---

## <a id='ps-clients-contatos-csv'></a>ps_clients_contatos.csv

**Total de Registros**: 2,479

**Total de Colunas**: 9

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | client_contato_id | int64 | 2 |
| 2 | client_id | int64 | 9 |
| 3 | client_contato_tipo | int64 | 0 |
| 4 | client_contato_nome | object | Fernando Castro Morais |
| 5 | client_contato_email | object | fernandocastromoarais@hotmail.com |
| 6 | client_contato_senha | float64 | NULL |
| 7 | client_contato_telefone | object | (64) 99699-0485 |
| 8 | client_contato_cpf | float64 | NULL |
| 9 | client_contato_status | float64 | NULL |

### Amostra de Dados

|   client_contato_id |   client_id |   client_contato_tipo | client_contato_nome            | client_contato_email              |   client_contato_senha | client_contato_telefone   |   client_contato_cpf |   client_contato_status |  
|--------------------:|------------:|----------------------:|:-------------------------------|:----------------------------------|-----------------------:|:--------------------------|---------------------:|------------------------:|  
|                   2 |           9 |                     0 | nan                            | nan                               |                    nan | nan                       |                  nan |                     nan |  
|                   3 |           9 |                     0 | nan                            | nan                               |                    nan | nan                       |                  nan |                     nan |  
|                   5 |          16 |                     0 | nan                            | nan                               |                    nan | nan                       |                  nan |                     nan |  
|                   6 |          19 |                     1 | Fernando Castro Morais         | fernandocastromoarais@hotmail.com |                    nan | (64) 99699-0485           |                  nan |                     nan |  
|                   8 |          32 |                     1 | MONICA MARIA DE AQUINO RIBEIRO | monicaribeiro@outlook.com         |                    nan | (62) 98123-2311           |                  nan |                     nan |

---

## <a id='ps-clients-evolution-csv'></a>ps_clients_evolution.csv

**Total de Registros**: 142,570

**Total de Colunas**: 11

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | evolution_id | int64 | 2 |
| 2 | client_id | float64 | 5.0 |
| 3 | professional_id | float64 | 4.0 |
| 4 | schedule_id | float64 | NULL |
| 5 | evolution_date | object | 2019-04-05 00:00:00 |
| 6 | evolution_description | object | fgnfbg fgfbfgb |
| 7 | evolution_registration_date | object | 2019-04-05 19:54:43 |
| 8 | evolution_lastupdate | object | 2019-04-05 22:54:43 |
| 9 | evolution_new_date | float64 | NULL |
| 10 | evolution_hour_start | float64 | NULL |
| 11 | evolution_hour_end | float64 | NULL |

### Amostra de Dados

|   evolution_id |   client_id |   professional_id |   schedule_id | evolution_date      | evolution_description                                                                                                                                               | evolution_registration_date   | evolution_lastupdate   |   evolution_new_date |   evolution_hour_start |   evolution_hour_end |  
|---------------:|------------:|------------------:|--------------:|:--------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------|:-----------------------|---------------------:|-----------------------:|---------------------:|  
|              2 |           5 |                 4 |           nan | 2019-04-05 00:00:00 | fgnfbg fgfbfgb                                                                                                                                                      | 2019-04-05 19:54:43           | 2019-04-05 22:54:43    |                  nan |                    nan |                  nan |  
|              5 |         204 |               nan |           nan | 2019-04-05 00:00:00 | nan                                                                                                                                                                 | 2019-04-05 20:21:24           | 2019-04-05 23:21:24    |                  nan |                    nan |                  nan |  
|              6 |         205 |               nan |           nan | 2019-04-05 00:00:00 | nan                                                                                                                                                                 | 2019-04-05 20:22:09           | 2019-04-05 23:22:09    |                  nan |                    nan |                  nan |  
|              7 |         206 |                 4 |           nan | 2019-04-04 00:00:00 | Pedro ficou mais irritado na presença da mãe.                                                                                                                       | 2019-04-05 20:23:59           | 2019-04-05 23:23:59    |                  nan |                    nan |                  nan |  
|                |             |                   |               |                     |                                                                                                                                                                     |                               |                        |                      |                        |                      |  
|                |             |                   |               |                     | Aceitou perder no jogo da velha                                                                                                                                     |                               |                        |                      |                        |                      |  
|                |             |                   |               |                     |                                                                                                                                                                     |                               |                        |                      |                        |                      |  
|                |             |                   |               |                     | fizemos quadro de comportamento, ele ajudou na elaboração.                                                                                                          |                               |                        |                      |                        |                      |  
|                |             |                   |               |                     |                                                                                                                                                                     |                               |                        |                      |                        |                      |  
|                |             |                   |               |                     | Queria jogar mais o jogo do pula macaco, queria pular no pula sem autorização e pontuei para ele a necessidade de realizar o que eu estava solicitando verbalmente. |                               |                        |                      |                        |                      |  
|              8 |         143 |               nan |           nan | 2019-04-05 00:00:00 | teste                                                                                                                                                               | 2019-04-05 20:30:46           | 2019-04-05 23:30:46    |                  nan |                    nan |                  nan |

---

## <a id='ps-clients-faltas-csv'></a>ps_clients_faltas.csv

**Total de Registros**: 91,371

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | falta_id | int64 | 1 |
| 2 | falta_client_id | int64 | 836 |
| 3 | falta_schedule_id | int64 | 84850 |
| 4 | falta_attachment_id | float64 | 1029.0 |
| 5 | falta_tipo | int64 | 1 |
| 6 | falta_registration_date | object | 2021-08-24 17:37:10 |
| 7 | falta_lastupdate | object | 2021-08-24 20:37:10 |

### Amostra de Dados

|   falta_id |   falta_client_id |   falta_schedule_id |   falta_attachment_id |   falta_tipo | falta_registration_date   | falta_lastupdate    |  
|-----------:|------------------:|--------------------:|----------------------:|-------------:|:--------------------------|:--------------------|  
|          1 |               836 |               84850 |                  1029 |            1 | 2021-08-24 17:37:10       | 2021-08-24 20:37:10 |  
|          2 |              1148 |               87723 |                   nan |            4 | 2021-08-25 11:56:54       | 2021-08-25 14:56:54 |  
|          3 |              1148 |               78554 |                   nan |            4 | 2021-08-25 11:57:09       | 2021-08-25 14:57:09 |  
|          4 |              1148 |               78060 |                   nan |            4 | 2021-08-25 11:57:25       | 2021-08-25 14:57:25 |  
|          5 |               322 |               77626 |                   nan |            2 | 2021-08-25 16:26:08       | 2021-08-25 19:26:08 |

---

## <a id='ps-clients-pagamentos-csv'></a>ps_clients_pagamentos.csv

**Total de Registros**: 2,994

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | client_pagamento_id | int64 | 2260 |
| 2 | client_id | int64 | 605 |
| 3 | pagamento_id | int64 | 3 |

### Amostra de Dados

|   client_pagamento_id |   client_id |   pagamento_id |  
|----------------------:|------------:|---------------:|  
|                  2260 |         605 |              3 |  
|                     2 |        1303 |              3 |  
|                  2385 |        1304 |              3 |  
|                  7893 |        1086 |              3 |  
|                 10966 |         596 |              3 |

---

## <a id='ps-clients-pro-history-csv'></a>ps_clients_pro_history.csv

**Total de Registros**: 87

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | pro_id | int64 | 3 |
| 2 | client_id | int64 | 5 |
| 3 | pro_type | object | psicologa |
| 4 | pro_name | object | larissa |
| 5 | pro_obs | object | teste   |
| 6 | pro_registration_date | object | 2019-01-17 17:13:03 |
| 7 | pro_lastupdate | object | 2019-01-17 19:13:21 |

### Amostra de Dados

|   pro_id |   client_id | pro_type      | pro_name                 | pro_obs   | pro_registration_date   | pro_lastupdate      |  
|---------:|------------:|:--------------|:-------------------------|:----------|:------------------------|:--------------------|  
|        3 |           5 | psicologa     | larissa                  | teste     | 2019-01-17 17:13:03     | 2019-01-17 19:13:21 |  
|        4 |          32 | Neuropediatra | DR. Helio Van Der Linden | nan       | 2019-01-21 09:11:08     | 2019-01-21 11:15:36 |  
|        5 |          34 | Neuropediatra | DR. Fabio Pessoa         | nan       | 2019-01-21 09:41:20     | 2019-01-21 12:15:22 |  
|        6 |          36 | Neuropediatra | DR. Helio Van Der Linden | nan       | 2019-01-21 10:08:04     | 2019-01-21 12:09:35 |  
|        7 |          19 | Neuropediatra | DR. Fabio Pessoa         | nan       | 2019-01-21 10:13:32     | 2019-01-21 12:14:18 |

---

## <a id='ps-clients-professional-csv'></a>ps_clients_professional.csv

**Total de Registros**: 106,098

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | professional_id | int64 | 7984 |
| 2 | user_id | int64 | 389 |
| 3 | client_id | int64 | 604 |

### Amostra de Dados

|   professional_id |   user_id |   client_id |  
|------------------:|----------:|------------:|  
|              7984 |       389 |         604 |  
|             15932 |       417 |         434 |  
|             13288 |       302 |         588 |  
|             13367 |       300 |         723 |  
|              6128 |         4 |         404 |

---

## <a id='ps-clients-reports-csv'></a>ps_clients_reports.csv

**Total de Registros**: 6,145

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | laudo_id | int64 | 5 |
| 2 | client_id | int64 | 120 |
| 3 | laudo_nome | object | Laudo Alaor |
| 4 | laudo_tipo | float64 | NULL |
| 5 | laudo_data | object | 2019-06-14 |
| 6 | laudo_registration_date | object | 2019-06-14 18:52:58 |
| 7 | laudo_path | object | files/2019/06/anexo-alaor-souza-figueiredo-de-c... |
| 8 | laudo_type | int64 | 2 |

### Amostra de Dados

|   laudo_id |   client_id | laudo_nome                   |   laudo_tipo | laudo_data   | laudo_registration_date   | laudo_path                                                              |   laudo_type |  
|-----------:|------------:|:-----------------------------|-------------:|:-------------|:--------------------------|:------------------------------------------------------------------------|-------------:|  
|          5 |         120 | Laudo Alaor                  |          nan | 2019-06-14   | 2019-06-14 18:52:58       | files/2019/06/anexo-alaor-souza-figueiredo-de-carvalho.pages            |            2 |  
|          6 |         120 | Relatório Alaor para justiça |          nan | 2019-06-14   | 2019-06-14 18:53:48       | files/2019/06/anexo-alaor-souza-figueiredo-de-carvalho-1560549258.pages |            2 |  
|         10 |         120 | Anamnese                     |          nan | 2020-05-12   | 2020-05-12 16:06:42       | files/2020/05/anexo-alaor-souza-figueiredo-de-carvalho-1589310421.pdf   |            2 |  
|         12 |          72 | Anamnese                     |          nan | 2020-05-12   | 2020-05-12 16:12:00       | files/2020/05/anexo-antonella-ferreira-arantes-barros-1589310733.pdf    |            2 |  
|         13 |         380 | Anamnese                     |          nan | 2020-05-12   | 2020-05-12 16:12:52       | files/2020/05/anexo-antonio-iron-rosendo-filho.pdf                      |            2 |

---

## <a id='ps-financial-accounts-csv'></a>ps_financial_accounts.csv

**Total de Registros**: 2

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | account_id | int64 | 1 |
| 2 | account_name | object | Caixa |
| 3 | account_registration_date | object | 2019-05-15 08:07:50 |
| 4 | account_lastupdate | float64 | NULL |

### Amostra de Dados

|   account_id | account_name   | account_registration_date   |   account_lastupdate |  
|-------------:|:---------------|:----------------------------|---------------------:|  
|            1 | Caixa          | 2019-05-15 08:07:50         |                  nan |  
|            2 | Sicoob         | 2019-05-15 08:08:44         |                  nan |

---

## <a id='ps-financial-categories-csv'></a>ps_financial_categories.csv

**Total de Registros**: 2

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | category_id | int64 | 1 |
| 2 | category_type | int64 | 1 |
| 3 | category_parent | float64 | 1.0 |
| 4 | category_name | object | consultorio |
| 5 | category_title | object | Consultório |
| 6 | category_content | object | Despesas relacionadas ao gestão do consultório ... |
| 7 | category_date | object | 2019-05-15 11:13:54 |

### Amostra de Dados

|   category_id |   category_type |   category_parent | category_name   | category_title   | category_content                                          | category_date       |  
|--------------:|----------------:|------------------:|:----------------|:-----------------|:----------------------------------------------------------|:--------------------|  
|             1 |               1 |               nan | consultorio     | Consultório      | Despesas relacionadas ao gestão do consultório no dia dia | 2019-05-15 11:13:54 |  
|             2 |               1 |                 1 | agua            | Água             | Gastos relacionados a companhia de saneamento             | 2019-05-15 11:25:59 |

---

## <a id='ps-financial-expenses-csv'></a>ps_financial_expenses.csv

**Total de Registros**: 133,061

**Total de Colunas**: 15

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | expense_id | int64 | 7 |
| 2 | expense_title | object | Água Sala 903 |
| 3 | expense_supplier | float64 | 1.0 |
| 4 | expense_category_id | float64 | 2.0 |
| 5 | expense_value | float64 | 20.0 |
| 6 | expense_issue_date | object | 2019-04-11 |
| 7 | expense_due_date | object | 2019-04-19 |
| 8 | expense_payment_date | object | 2019-04-15 |
| 9 | expense_receipt_type | float64 | 2.0 |
| 10 | expense_receipt_number | float64 | 1111111.0 |
| 11 | expense_account_id | int64 | 2 |
| 12 | expense_description | object | Atendimento da Profissional: Ana Laura  Carneir... |
| 13 | expense_registration_date | object | 2019-05-15 08:27:58 |
| 14 | expense_lastupdate | object | 2019-05-15 11:27:58 |
| 15 | expense_status | int64 | 0 |

### Amostra de Dados

|   expense_id | expense_title                                          |   expense_supplier |   expense_category_id |   expense_value | expense_issue_date   | expense_due_date   | expense_payment_date   |   expense_receipt_type |   expense_receipt_number |   expense_account_id | expense_description                                                                      | expense_registration_date   | expense_lastupdate   |   expense_status |  
|-------------:|:-------------------------------------------------------|-------------------:|----------------------:|----------------:|:---------------------|:-------------------|:-----------------------|-----------------------:|-------------------------:|---------------------:|:-----------------------------------------------------------------------------------------|:----------------------------|:---------------------|-----------------:|  
|            7 | Água Sala 903                                          |                  1 |                     2 |              20 | 2019-04-11           | 2019-04-19         | 2019-04-15             |                      2 |              1.11111e+06 |                    2 | nan                                                                                      | 2019-05-15 08:27:58         | 2019-05-15 11:27:58  |                0 |  
|            9 | Água Sala 903                                          |                  1 |                     2 |              20 | 2019-04-11           | 2019-04-11         | 2019-04-11             |                      2 |         111111           |                    2 | nan                                                                                      | 2019-05-15 08:29:36         | 2019-05-15 11:29:36  |                1 |  
|           13 | Atendimento da Profissional: Ana Laura  Carneiro Gomes |                nan |                   nan |             110 | 2019-06-25           | 2019-07-25         | nan                    |                    nan |            nan           |                    0 | Atendimento da Profissional: Ana Laura  Carneiro Gomes . Data do Atendimento: 07/06/2019 | 2019-06-25 11:12:25         | 2019-06-25 14:12:25  |                0 |  
|           14 | Atendimento da Profissional: Ana Laura  Carneiro Gomes |                nan |                   nan |             110 | 2019-06-25           | 2019-07-25         | nan                    |                    nan |            nan           |                    0 | Atendimento da Profissional: Ana Laura  Carneiro Gomes . Data do Atendimento: 01/06/2019 | 2019-06-25 11:12:42         | 2019-06-25 14:12:42  |                0 |  
|           15 | Atendimento da Profissional: Ana Laura  Carneiro Gomes |                nan |                   nan |             110 | 2019-06-25           | 2019-07-25         | nan                    |                    nan |            nan           |                    0 | Atendimento da Profissional: Ana Laura  Carneiro Gomes . Data do Atendimento: 01/06/2019 | 2019-06-25 11:12:55         | 2019-06-25 14:12:55  |                0 |

---

## <a id='ps-financial-revenues-csv'></a>ps_financial_revenues.csv

**Total de Registros**: 126,601

**Total de Colunas**: 12

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | revenue_id | int64 | 2 |
| 2 | revenue_title | object | Atendimento do Paciente: Júlio Davi Martins Mor... |
| 3 | revenue_pacient_id | float64 | 281.0 |
| 4 | revenue_category_id | float64 | NULL |
| 5 | revenue_date | object | 2019-06-25 |
| 6 | revenue_receive_type | int64 | 5 |
| 7 | revenue_value | float64 | 2200.0 |
| 8 | revenue_account_id | int64 | 0 |
| 9 | revenue_description | object | Atendimento do Paciente: Júlio Davi Martins Mor... |
| 10 | revenue_status | int64 | 0 |
| 11 | revenue_registration_date | object | 2019-06-25 11:12:25 |
| 12 | revenue_lastupdate | object | 2019-06-25 14:12:25 |

### Amostra de Dados

|   revenue_id | revenue_title                                        |   revenue_pacient_id |   revenue_category_id | revenue_date   |   revenue_receive_type |   revenue_value |   revenue_account_id | revenue_description                                                                   |   revenue_status | revenue_registration_date   | revenue_lastupdate   |  
|-------------:|:-----------------------------------------------------|---------------------:|----------------------:|:---------------|-----------------------:|----------------:|---------------------:|:--------------------------------------------------------------------------------------|-----------------:|:----------------------------|:---------------------|  
|            2 | Atendimento do Paciente: Júlio Davi Martins Moreira  |                  281 |                   nan | 2019-06-25     |                      5 |            2200 |                    0 | Atendimento do Paciente: Júlio Davi Martins Moreira. Data do Atendimento: 07/06/2019  |                0 | 2019-06-25 11:12:25         | 2019-06-25 14:12:25  |  
|            3 | Atendimento do Paciente: Júlio Davi Martins Moreira  |                  281 |                   nan | 2019-06-25     |                      5 |            2200 |                    0 | Atendimento do Paciente: Júlio Davi Martins Moreira. Data do Atendimento: 01/06/2019  |                0 | 2019-06-25 11:12:42         | 2019-06-25 14:12:42  |  
|            4 | Atendimento do Paciente: Júlio Davi Martins Moreira  |                  281 |                   nan | 2019-06-25     |                      5 |            2200 |                    0 | Atendimento do Paciente: Júlio Davi Martins Moreira. Data do Atendimento: 01/06/2019  |                0 | 2019-06-25 11:12:55         | 2019-06-25 14:12:55  |  
|            5 | Atendimento do Paciente: Gabriel Ribeiro Vasconcelos |                   37 |                   nan | 2019-06-25     |                      5 |               0 |                    0 | Atendimento do Paciente: Gabriel Ribeiro Vasconcelos. Data do Atendimento: 03/06/2019 |                0 | 2019-06-25 11:13:10         | 2019-06-25 14:13:10  |  
|            6 | Atendimento do Paciente: João Vitor Pires Dos Santos |                  253 |                   nan | 2019-06-25     |                      5 |               0 |                    0 | Atendimento do Paciente: João Vitor Pires Dos Santos. Data do Atendimento: 04/06/2019 |                0 | 2019-06-25 11:13:26         | 2019-06-25 14:13:26  |

---

## <a id='ps-financial-suppliers-csv'></a>ps_financial_suppliers.csv

**Total de Registros**: 2

**Total de Colunas**: 9

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | supplier_id | int64 | 1 |
| 2 | supplier_name | object | SANEAGO (SANEAMENTO DE GOIÁS S.A.) |
| 3 | supplier_doc | object | 01616929000102 |
| 4 | supplier_responsible | object | s/n |
| 5 | supplier_phone | object | (08) 00645-0115 |
| 6 | supplier_address | object | Avenida Fuad José Sebba nº 1245 Jardim Goiás Go... |
| 7 | supplier_obs | float64 | NULL |
| 8 | supplier_registration_date | object | 2019-05-15 08:09:43 |
| 9 | supplier_lastupdate | object | 2019-05-15 11:09:43 |

### Amostra de Dados

|   supplier_id | supplier_name                      | supplier_doc       | supplier_responsible   | supplier_phone   | supplier_address                                           |   supplier_obs | supplier_registration_date   | supplier_lastupdate   |  
|--------------:|:-----------------------------------|:-------------------|:-----------------------|:-----------------|:-----------------------------------------------------------|---------------:|:-----------------------------|:----------------------|  
|             1 | SANEAGO (SANEAMENTO DE GOIÁS S.A.) | 01616929000102     | s/n                    | (08) 00645-0115  | Avenida Fuad José Sebba nº 1245 Jardim Goiás Goiânia Goiás |            nan | 2019-05-15 08:09:43          | 2019-05-15 11:09:43   |  
|             2 | Papelaria Tributaria LTDA          | 00.905.760/0001-48 | nan                    | nan              | nan                                                        |            nan | 2019-05-22 12:00:49          | 2019-05-22 15:00:49   |

---

## <a id='ps-locales-csv'></a>ps_locales.csv

**Total de Registros**: 5

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | local_id | int64 | 1 |
| 2 | local_nome | object | Unidade Oeste |
| 3 | local_endereco | object | Rua 15 |
| 4 | local_cidade | object | Goiânia |
| 5 | local_uf | object | GO |
| 6 | local_status | object | A |
| 7 | local_registration_date | object | 2021-04-04 17:17:00 |
| 8 | local_lastupdate | object | 2021-04-04 20:17:28 |

### Amostra de Dados

|   local_id | local_nome          | local_endereco   | local_cidade   | local_uf   | local_status   | local_registration_date   | local_lastupdate    |  
|-----------:|:--------------------|:-----------------|:---------------|:-----------|:---------------|:--------------------------|:--------------------|  
|          1 | Unidade Oeste       | Rua 15           | Goiânia        | GO         | A              | 2021-04-04 17:17:00       | 2021-04-04 20:17:28 |  
|          2 | Unidade Bueno       | nan              | Goiânia        | GO         | A              | 2021-06-18 09:16:28       | 2021-06-18 12:16:28 |  
|          3 | Unidade Externa     | nan              | Goiânia        | GO         | A              | 2021-06-18 09:16:28       | 2021-06-18 12:16:28 |  
|          4 | Hosp. do Coração    | nan              | Goiânia        | GO         | A              | 2023-05-11 22:14:35       | 2023-05-12 01:19:40 |  
|          5 | República do Líbano | nan              | Goiânia        | GO         | A              | 2024-09-11 13:34:18       | 2024-09-11 13:34:18 |

---

## <a id='ps-log-actions-csv'></a>ps_log_actions.csv

**Total de Registros**: 1,201,372

**Total de Colunas**: 9

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | log_id | int64 | 1 |
| 2 | log_operation | object | update |
| 3 | user_id | int64 | 4 |
| 4 | log_date | object | 2023-07-24 16:26:33 |
| 5 | log_table | object | mbm_aba_programas |
| 6 | log_description | object | alterou a atividade |
| 7 | log_row_before_complete | object | a:7:{s:12:"atividade_id";s:3:"331";s:14:"ativid... |
| 8 | log_row_complete | object | a:4:{s:12:"atividade_id";s:3:"331";s:14:"ativid... |
| 9 | log_reference_id | float64 | 331.0 |

### Amostra de Dados

|   log_id | log_operation   |   user_id | log_date            | log_table         | log_description             | log_row_before_complete                                                                                                                                                                                                                                                                      | log_row_complete                                                                                                                                    |   log_reference_id |  
|---------:|:----------------|----------:|:--------------------|:------------------|:----------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------|-------------------:|  
|        1 | update          |         4 | 2023-07-24 16:26:33 | mbm_aba_programas | alterou a atividade         | a:7:{s:12:"atividade_id";s:3:"331";s:14:"atividade_nome";s:13:"Helicóptero ";s:19:"atividade_descricao";N;s:15:"atividade_image";N;s:19:"atividade_brinquedo";s:1:"0";s:27:"atividade_registration_date";s:19:"2019-01-17 16:10:10";s:20:"atividade_lastupdate";s:19:"2019-01-17 18:10:10";} | a:4:{s:12:"atividade_id";s:3:"331";s:14:"atividade_nome";s:13:"Helicóptero ";s:19:"atividade_descricao";s:0:"";s:19:"atividade_brinquedo";s:1:"0";} |                331 |  
|        2 | update          |         4 | 2023-07-24 18:37:50 | ws_pagamentos     | alterou o pagamento         | a:3:{s:12:"pagamento_id";s:2:"27";s:14:"pagamento_name";s:0:"";s:16:"pagamento_status";s:1:"A";}                                                                                                                                                                                             | a:3:{s:12:"pagamento_id";s:2:"27";s:14:"pagamento_name";s:31:"UNIMED - NORTE MINAS - EVENTUAL";s:16:"pagamento_status";s:1:"A";}                    |                 27 |  
|        3 | update          |      1195 | 2023-07-24 20:05:55 | ws_users          | alterou o perfil do usuário | nan                                                                                                                                                                                                                                                                                          | a:1:{s:12:"user_profile";s:1:"3";}                                                                                                                  |               1829 |  
|        4 | update          |         4 | 2023-07-24 20:08:39 | ws_especialidades | alterou a especialidade     | a:3:{s:16:"especialidade_id";s:2:"32";s:18:"especialidade_name";s:0:"";s:20:"especialidade_status";s:1:"A";}                                                                                                                                                                                 | a:3:{s:16:"especialidade_id";s:2:"32";s:18:"especialidade_name";s:4:"TDCS";s:20:"especialidade_status";s:1:"A";}                                    |                 32 |  
|        5 | update          |      1195 | 2023-07-24 20:31:26 | ws_users          | alterou o perfil do usuário | nan                                                                                                                                                                                                                                                                                          | a:1:{s:12:"user_profile";s:1:"3";}                                                                                                                  |               1830 |

---

## <a id='ps-registros-guias-csv'></a>ps_registros_guias.csv

**Total de Registros**: 1,602

**Total de Colunas**: 22

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | registro_guia_id | int64 | 1 |
| 2 | registro_guia_pagamento_id | float64 | 3.0 |
| 3 | registro_guia_client_id | float64 | 605.0 |
| 4 | registro_guia_numero | float64 | 27057350.0 |
| 5 | registro_guia_data_autorizacao | object | 2021-04-26 |
| 6 | registro_guia_senha | float64 | 916332877.0 |
| 7 | registro_guia_data_validade_senha | object | 2021-06-25 |
| 8 | registro_guia_numero_sessoes_autorizada | float64 | 10.0 |
| 9 | registro_guia_status | object | I |
| 10 | registro_guia_finalizada | object | N |
| 11 | registro_guia_data_1 | float64 | NULL |
| 12 | registro_guia_data_2 | float64 | NULL |
| 13 | registro_guia_data_3 | float64 | NULL |
| 14 | registro_guia_data_4 | float64 | NULL |
| 15 | registro_guia_data_5 | float64 | NULL |
| 16 | registro_guia_data_6 | float64 | NULL |
| 17 | registro_guia_data_7 | float64 | NULL |
| 18 | registro_guia_data_8 | float64 | NULL |
| 19 | registro_guia_data_9 | float64 | NULL |
| 20 | registro_guia_data_10 | float64 | NULL |
| 21 | registro_guia_registration_date | object | 2021-05-17 |
| 22 | registro_guia_lastupdate | object | 2021-05-17 10:19:00 |

### Amostra de Dados

|   registro_guia_id |   registro_guia_pagamento_id |   registro_guia_client_id |   registro_guia_numero | registro_guia_data_autorizacao   |   registro_guia_senha | registro_guia_data_validade_senha   |   registro_guia_numero_sessoes_autorizada | registro_guia_status   | registro_guia_finalizada   |   registro_guia_data_1 |   registro_guia_data_2 |   registro_guia_data_3 |   registro_guia_data_4 |   registro_guia_data_5 |   registro_guia_data_6 |   registro_guia_data_7 |   registro_guia_data_8 |   registro_guia_data_9 |   registro_guia_data_10 | registro_guia_registration_date   | registro_guia_lastupdate   |  
|-------------------:|-----------------------------:|--------------------------:|-----------------------:|:---------------------------------|----------------------:|:------------------------------------|------------------------------------------:|:-----------------------|:---------------------------|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|-----------------------:|------------------------:|:----------------------------------|:---------------------------|  
|                  1 |                            3 |                       605 |            2.70574e+07 | 2021-04-26                       |           9.16333e+08 | 2021-06-25                          |                                        10 | I                      | N                          |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                     nan | 2021-05-17                        | 2021-05-17 10:19:00        |  
|                  2 |                          nan |                       nan |          nan           | nan                              |         nan           | nan                                 |                                       nan | A                      | N                          |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                     nan | 2021-05-18                        | 2021-05-18 14:25:43        |  
|                  3 |                            3 |                       458 |            2.73715e+07 | 2021-05-11                       |           9.16636e+08 | 2021-07-10                          |                                        10 | A                      | N                          |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                     nan | 2021-05-18                        | 2021-05-18 15:13:15        |  
|                  4 |                            3 |                       458 |            2.73715e+07 | 2021-05-11                       |           9.16636e+08 | 2021-07-10                          |                                         6 | A                      | N                          |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                     nan | 2021-05-18                        | 2021-05-18 15:17:52        |  
|                  5 |                            3 |                       765 |            2.73843e+07 | 2021-05-12                       |           1.33411e+08 | 2021-07-11                          |                                         4 | A                      | N                          |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                    nan |                     nan | 2021-05-18                        | 2021-05-18 15:22:08        |

---

## <a id='ps-registros-guias-datas-csv'></a>ps_registros_guias_datas.csv

**Total de Registros**: 5,954

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | registro_guia_data_id | int64 | 5 |
| 2 | registro_guia_data_numero | int64 | 27057350 |
| 3 | registro_guia_data | object | 2021-05-17 |

### Amostra de Dados

|   registro_guia_data_id |   registro_guia_data_numero | registro_guia_data   |  
|------------------------:|----------------------------:|:---------------------|  
|                       5 |                    27057350 | 2021-05-17           |  
|                       6 |                    27057350 | 2021-05-17           |  
|                       7 |                    27529181 | 2021-05-18           |  
|                       8 |                    27529181 | 2021-05-18           |  
|                      13 |                    27450124 | 2021-05-17           |

---

## <a id='ps-schedule-csv'></a>ps_schedule.csv

**Total de Registros**: 499,891

**Total de Colunas**: 20

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | schedule_id | int64 | 1 |
| 2 | schedule_date_start | object | 2019-05-21 07:00:00 |
| 3 | schedule_date_end | object | 2019-05-21 08:00:00 |
| 4 | schedule_pacient_id | int64 | 40 |
| 5 | schedule_pagamento_id | float64 | NULL |
| 6 | schedule_room_id | int64 | 1 |
| 7 | schedule_qtd_sessions | float64 | 1.0 |
| 8 | schedule_status | int64 | 1 |
| 9 | schedule_room_rent_value | float64 | 0.0 |
| 10 | schedule_fixed | float64 | NULL |
| 11 | schedule_especialidade_id | float64 | NULL |
| 12 | schedule_local_id | float64 | NULL |
| 13 | schedule_saldo_sessoes | float64 | 0.0 |
| 14 | schedule_elegibilidade | object | Nao |
| 15 | schedule_falta_do_profissional | object | Não |
| 16 | schedule_parent_id | float64 | NULL |
| 17 | schedule_registration_date | object | 2019-05-21 20:02:09 |
| 18 | schedule_lastupdate | object | 2019-05-21 23:02:09 |
| 19 | parent_id | float64 | NULL |
| 20 | schedule_codigo_faturamento | float64 | NULL |

### Amostra de Dados

|   schedule_id | schedule_date_start   | schedule_date_end   |   schedule_pacient_id |   schedule_pagamento_id |   schedule_room_id |   schedule_qtd_sessions |   schedule_status |   schedule_room_rent_value |   schedule_fixed |   schedule_especialidade_id |   schedule_local_id |   schedule_saldo_sessoes | schedule_elegibilidade   | schedule_falta_do_profissional   |   schedule_parent_id | schedule_registration_date   | schedule_lastupdate   |   parent_id |   schedule_codigo_faturamento |  
|--------------:|:----------------------|:--------------------|----------------------:|------------------------:|-------------------:|------------------------:|------------------:|---------------------------:|-----------------:|----------------------------:|--------------------:|-------------------------:|:-------------------------|:---------------------------------|---------------------:|:-----------------------------|:----------------------|------------:|------------------------------:|  
|             1 | 2019-05-21 07:00:00   | 2019-05-21 08:00:00 |                    40 |                     nan |                  1 |                       1 |                 1 |                          0 |              nan |                         nan |                 nan |                        0 | Nao                      | Não                              |                  nan | 2019-05-21 20:02:09          | 2019-05-21 23:02:09   |         nan |                           nan |  
|             2 | 2019-05-21 07:00:00   | 2019-05-21 08:00:00 |                    40 |                     nan |                  1 |                       1 |                 1 |                          0 |              nan |                         nan |                 nan |                        0 | Nao                      | Não                              |                  nan | 2019-05-21 20:02:40          | 2019-05-21 23:02:40   |         nan |                           nan |  
|             3 | 2019-05-21 15:00:00   | 2019-05-21 16:00:00 |                   128 |                     nan |                  2 |                       1 |                 1 |                          0 |              nan |                         nan |                 nan |                        0 | Nao                      | Não                              |                  nan | 2019-05-21 20:03:35          | 2019-05-21 23:03:35   |         nan |                           nan |  
|             5 | 2019-05-22 10:00:00   | 2019-05-22 11:00:00 |                    74 |                     nan |                  5 |                       1 |                 1 |                          0 |              nan |                         nan |                 nan |                        0 | Nao                      | Não                              |                  nan | 2019-05-22 11:57:08          | 2019-05-22 14:57:08   |         nan |                           nan |  
|             6 | 2019-05-02 13:30:00   | 2019-05-02 14:20:00 |                   206 |                     nan |                  1 |                       1 |                 1 |                          0 |              nan |                         nan |                 nan |                        0 | Nao                      | Não                              |                  nan | 2019-05-22 11:58:45          | 2019-05-22 14:58:45   |         nan |                           nan |

---

## <a id='ps-schedule-blocked-csv'></a>ps_schedule_blocked.csv

**Total de Registros**: 458,244

**Total de Colunas**: 13

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | schedule_id | int64 | 6 |
| 2 | schedule_professional_id | int64 | 4 |
| 3 | schedule_date_start | object | 2020-07-15 20:00:00 |
| 4 | schedule_date_end | object | 2020-07-15 21:00:00 |
| 5 | schedule_pacient_id | float64 | NULL |
| 6 | schedule_room_id | float64 | NULL |
| 7 | schedule_qtd_sessions | float64 | NULL |
| 8 | schedule_status | int64 | 0 |
| 9 | schedule_room_rent_value | float64 | 0.0 |
| 10 | schedule_fixed | object | N |
| 11 | schedule_registration_date | object | 2020-07-15 17:36:44 |
| 12 | schedule_lastupdate | object | 2020-07-15 20:36:44 |
| 13 | schedule_local_id | float64 | 0.0 |

### Amostra de Dados

|   schedule_id |   schedule_professional_id | schedule_date_start   | schedule_date_end   |   schedule_pacient_id |   schedule_room_id |   schedule_qtd_sessions |   schedule_status |   schedule_room_rent_value | schedule_fixed   | schedule_registration_date   | schedule_lastupdate   |   schedule_local_id |  
|--------------:|---------------------------:|:----------------------|:--------------------|----------------------:|-------------------:|------------------------:|------------------:|---------------------------:|:-----------------|:-----------------------------|:----------------------|--------------------:|  
|             6 |                          4 | 2020-07-15 20:00:00   | 2020-07-15 21:00:00 |                   nan |                nan |                     nan |                 0 |                          0 | N                | 2020-07-15 17:36:44          | 2020-07-15 20:36:44   |                   0 |  
|             7 |                         26 | 2020-07-24 15:10:00   | 2020-07-24 16:00:00 |                   nan |                nan |                     nan |                 0 |                          0 | N                | 2020-07-20 16:18:29          | 2020-07-20 19:18:29   |                   0 |  
|             8 |                         25 | 2020-07-24 14:00:00   | 2020-07-24 18:00:00 |                   nan |                nan |                     nan |                 0 |                          0 | N                | 2020-07-23 17:58:17          | 2020-07-23 20:58:17   |                   0 |  
|            17 |                          4 | 2020-09-21 11:00:00   | 2020-09-21 12:00:00 |                   nan |                nan |                     nan |                 0 |                          0 | N                | 2020-09-14 09:20:48          | 2020-09-14 12:20:48   |                   0 |  
|            18 |                          4 | 2020-09-28 11:00:00   | 2020-09-28 12:00:00 |                   nan |                nan |                     nan |                 0 |                          0 | N                | 2020-09-14 09:21:05          | 2020-09-14 12:21:05   |                   0 |

---

## <a id='ps-schedule-pacients-csv'></a>ps_schedule_pacients.csv

**Total de Registros**: 324,026

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 1249 |
| 2 | pacient_id | int64 | 2774 |
| 3 | schedule_id | int64 | 238402 |

### Amostra de Dados

|   id |   pacient_id |   schedule_id |  
|-----:|-------------:|--------------:|  
| 1249 |         2774 |        238402 |  
| 1248 |         2776 |        238401 |  
| 1247 |          538 |        238400 |  
| 1246 |         1393 |        238399 |  
| 1245 |         1577 |        238398 |

---

## <a id='ps-schedule-professionals-csv'></a>ps_schedule_professionals.csv

**Total de Registros**: 526,474

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 1 |
| 2 | professional_id | int64 | 4 |
| 3 | schedule_id | int64 | 1 |
| 4 | substituido | object | N |

### Amostra de Dados

|   id |   professional_id |   schedule_id | substituido   |  
|-----:|------------------:|--------------:|:--------------|  
|    1 |                 4 |             1 | N             |  
|    2 |                 4 |             2 | N             |  
|    3 |                27 |             3 | N             |  
|    5 |                 4 |             5 | N             |  
|    6 |                27 |             5 | N             |

---

## <a id='ps-schedule-professionals-blocked-csv'></a>ps_schedule_professionals_blocked.csv

**Total de Registros**: 467,125

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 6 |
| 2 | professional_id | int64 | 4 |
| 3 | schedule_id | int64 | 6 |

### Amostra de Dados

|   id |   professional_id |   schedule_id |  
|-----:|------------------:|--------------:|  
|    6 |                 4 |             6 |  
|   17 |                 4 |            17 |  
|   18 |                 4 |            18 |  
|   20 |                 4 |            20 |  
|   21 |                 4 |            21 |

---

## <a id='ra-relatorio-medico-csv'></a>ra_relatorio_medico.csv

**Total de Registros**: 2,390

**Total de Colunas**: 15

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | relatorio_id | int64 | 1 |
| 2 | relatorio_client_id | int64 | 2652 |
| 3 | relatorio_data_laudo | object | 2022-04-12 |
| 4 | relatorio_arquivo_laudo | object | images/2022/09/relatorio-medico-laudo-202209271... |
| 5 | relatorio_arquivo_laudo_id | float64 | 150.0 |
| 6 | relatorio_qtde_fisioterapia | int64 | 0 |
| 7 | relatorio_qtde_fonoaudiologia | int64 | 4 |
| 8 | relatorio_qtde_musicoterapia | int64 | 0 |
| 9 | relatorio_qtde_neuropedagogia | int64 | 0 |
| 10 | relatorio_qtde_psicopedagogia | int64 | 0 |
| 11 | relatorio_qtde_psicologia | int64 | 3 |
| 12 | relatorio_qtde_psicomoticidade | int64 | 0 |
| 13 | relatorio_qtde_terapia_ocupacional | int64 | 2 |
| 14 | relatorio_data_validade | object | 2022-10-12 |
| 15 | relatorio_registration_date | object | 2022-09-27 14:13:41 |

### Amostra de Dados

|   relatorio_id |   relatorio_client_id | relatorio_data_laudo   | relatorio_arquivo_laudo                                       |   relatorio_arquivo_laudo_id |   relatorio_qtde_fisioterapia |   relatorio_qtde_fonoaudiologia |   relatorio_qtde_musicoterapia |   relatorio_qtde_neuropedagogia |   relatorio_qtde_psicopedagogia |   relatorio_qtde_psicologia |   relatorio_qtde_psicomoticidade |   relatorio_qtde_terapia_ocupacional | relatorio_data_validade   | relatorio_registration_date   |  
|---------------:|----------------------:|:-----------------------|:--------------------------------------------------------------|-----------------------------:|------------------------------:|--------------------------------:|-------------------------------:|--------------------------------:|--------------------------------:|----------------------------:|---------------------------------:|-------------------------------------:|:--------------------------|:------------------------------|  
|              1 |                  2652 | 2022-04-12             | images/2022/09/relatorio-medico-laudo-202209271117202652.jpeg |                          150 |                             0 |                               4 |                              0 |                               0 |                               0 |                           3 |                                0 |                                    2 | 2022-10-12                | 2022-09-27 14:13:41           |  
|              2 |                  1963 | 2022-05-11             | images/2022/09/relatorio-medico-laudo-202209271120041963.jpg  |                          151 |                             0 |                               0 |                              0 |                               0 |                               0 |                           0 |                                0 |                                    0 | 2022-11-11                | 2022-09-27 14:20:04           |  
|              4 |                  1393 | 2022-05-19             | images/2022/09/relatorio-medico-laudo-202209271139121393.jpg  |                          153 |                             0 |                               3 |                              1 |                               0 |                               3 |                           6 |                                1 |                                    2 | 2022-11-19                | 2022-09-27 14:39:12           |  
|              5 |                  2051 | 2022-08-31             | files/2022/09/relatorio-medico-laudo-202209271153572051.pdf   |                          154 |                             0 |                               1 |                              0 |                               0 |                               1 |                           4 |                                0 |                                    1 | 2023-03-03                | 2022-09-27 14:53:57           |  
|              6 |                   681 | 2022-05-17             | files/2022/09/relatorio-medico-laudo-20220927115700681.pdf    |                          155 |                             0 |                               0 |                              0 |                               0 |                               0 |                           0 |                                0 |                                    0 | 2022-11-17                | 2022-09-27 14:57:00           |

---

## <a id='ra-relatorio-mensal-amil-csv'></a>ra_relatorio_mensal_amil.csv

**Total de Registros**: 0

**Total de Colunas**: 16

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | amil_id | object | NULL |
| 2 | amil_client_id | object | NULL |
| 3 | amil_client_carteirinha | object | NULL |
| 4 | amil_liminar | object | NULL |
| 5 | amil_patologia_id | object | NULL |
| 6 | amil_atividade_desenvolvida | object | NULL |
| 7 | amil_horas_mensais | object | NULL |
| 8 | amil_horas_psicologia | object | NULL |
| 9 | amil_horas_terapia_ocupacional | object | NULL |
| 10 | amil_horas_fonoaudiologia | object | NULL |
| 11 | amil_horas_fisioterapia | object | NULL |
| 12 | amil_horas_equoterapia | object | NULL |
| 13 | amil_outras_terapias | object | NULL |
| 14 | amil_outra_horas_semanal | object | NULL |
| 15 | amil_evolucao_paciente | object | NULL |
| 16 | amil_data_cadastro | object | NULL |


---

## <a id='ra-relatorio-mensal-ipasgo-csv'></a>ra_relatorio_mensal_ipasgo.csv

**Total de Registros**: 447

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | ipasgo_id | int64 | 1 |
| 2 | ipasgo_profissional_atendimento | float64 | 2.0 |
| 3 | ipasgo_tipo_terapia | float64 | 9.0 |
| 4 | ipasgo_justificativa_periodo_tratamento | object | TESTE DA JUSTIFICATIVA |
| 5 | ipasgo_evolucao_paciente | object | TESTE DA EVOLUÇÃO |
| 6 | ipasgo_data | object | 2023-10-18 |
| 7 | client_id | int64 | 3528 |
| 8 | user_id | int64 | 4 |

### Amostra de Dados

|   ipasgo_id |   ipasgo_profissional_atendimento |   ipasgo_tipo_terapia | ipasgo_justificativa_periodo_tratamento                                                                                | ipasgo_evolucao_paciente                     | ipasgo_data   |   client_id |   user_id |  
|------------:|----------------------------------:|----------------------:|:-----------------------------------------------------------------------------------------------------------------------|:---------------------------------------------|:--------------|------------:|----------:|  
|           1 |                                 2 |                     9 | TESTE DA JUSTIFICATIVA                                                                                                 | TESTE DA EVOLUÇÃO                            | 2023-10-18    |        3528 |         4 |  
|           2 |                                 3 |                    25 | Início das terapias dentro da disponibilidade da família. Com o andamento do tratamento será reajustado a necessidade. | Início de tratamento.                        | 2024-03-08    |        3028 |       884 |  
|           3 |                                 2 |                     1 | Início das terapias dentro da disponibilidade da família. Com o andamento do tratamento será reajustado a necessidade. | Inicio do tratamento.                        | 2024-02-28    |        3574 |      2057 |  
|           4 |                                 2 |                   nan | Início das terapias dentro da disponibilidade da família. Com o andamento do tratamento será reajustado a necessidade. | No período de tratamento com o procedimento. | 2024-01-05    |        3590 |       577 |  
|           5 |                                 1 |                   nan | Início das terapias dentro da disponibilidade da família. Com o andamento do tratamento será reajustado a necessidade. | Início de tratamento.                        | 2024-06-27    |        3604 |       772 |

---

## <a id='ra-tratativas-faltas-csv'></a>ra_tratativas_faltas.csv

**Total de Registros**: 124

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | tratativa_falta_id | int64 | 123 |
| 2 | tratativa_falta_termo_assinado | object | Sim |
| 3 | tratativa_falta_client_id | int64 | 43 |
| 4 | tratativa_falta_tipo_contato | object | Pessoalmente |
| 5 | tratativa_falta_quem_realizou | int64 | 233 |
| 6 | tratativa_falta_descricao | object | TESTE |
| 7 | tratativa_falta_definicao | object | Desligado |
| 8 | tratativa_falta_data | object | 2023-03-29 11:49:47 |

### Amostra de Dados

|   tratativa_falta_id | tratativa_falta_termo_assinado   |   tratativa_falta_client_id | tratativa_falta_tipo_contato   |   tratativa_falta_quem_realizou | tratativa_falta_descricao                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | tratativa_falta_definicao   | tratativa_falta_data   |  
|---------------------:|:---------------------------------|----------------------------:|:-------------------------------|--------------------------------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------|:-----------------------|  
|                  123 | Sim                              |                          43 | Pessoalmente                   |                             233 | TESTE                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Desligado                   | 2023-03-29 11:49:47    |  
|                    3 | Sim                              |                        1924 | Ligação Telefônica             |                            1204 | Teste ! Falamos com a Mãe, ela nos informou que o Matheus está muito gripado !                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Continuidade                | 2022-10-18 11:01:07    |  
|                    6 | Sim                              |                        2697 | Ligação Telefônica             |                            1195 | Teste                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Continuidade                | 2022-10-26 12:00:31    |  
|                    7 | Sim                              |                         567 | Ligação Telefônica             |                            1204 | Falamos com a Mãe Senhora Josehelli, e nos informou que o celular pegou fogo. E que tem comparecido nas terapias faltando somente 01 dia no mês de outubro. Constatamos que houve várias faltas em outubro .Estamos tentando falar novamente com a Mãe! Vamos solicitar assiduidade nas terapias, pois será notificada que o paciente será retirado das agendas.                                                                                                                                                                          | Desligado                   | 2022-10-27 17:44:13    |  
|                    8 | Sim                              |                         567 | Ligação Telefônica             |                            1361 | Foi realizada uma ligação com a responsável Josehelli, e explicamos que devido as ausências do Nicolas sem justificativas o primeiro passo foi retirar ele das agendas na segunda-feira, no entanto, nas quartas ele também não tem vindo, como isso não contribui para a evolução dele, foi decidido que o mesmo seria retirado da agenda e o colocaremos na lista de espera. A mãe ficou bem alterada na ligação e colocou a culpa na Clinica por não tê-la avisado, sendo que foi conversado anteriormente sobre a questão das faltas. | Desligado                   | 2022-12-14 13:38:46    |

---

## <a id='sys-permissions-csv'></a>sys_permissions.csv

**Total de Registros**: 101

**Total de Colunas**: 6

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 1 |
| 2 | name | object | APP_DASHBOARD |
| 3 | label | object | Dashboard |
| 4 | parent | float64 | 3.0 |
| 5 | permission | int64 | 1 |
| 6 | created_at | object | 2022-10-18 05:07:36 |

### Amostra de Dados

|   id | name                         | label            |   parent |   permission | created_at          |  
|-----:|:-----------------------------|:-----------------|---------:|-------------:|:--------------------|  
|    1 | APP_DASHBOARD                | Dashboard        |      nan |            1 | 2022-10-18 05:07:36 |  
|    2 | APP_CLIENTS                  | Pacientes        |      nan |            0 | 2022-10-18 05:09:59 |  
|    3 | APP_SCHEDULE                 | Agenda           |      nan |            0 | 2022-10-18 05:13:10 |  
|    4 | APP_SCHEDULE_BY_ROOM         | Por Sala         |        3 |            1 | 2022-10-18 05:23:03 |  
|    5 | APP_SCHEDULE_BY_PROFESSIONAL | Por Profissional |        3 |            1 | 2022-10-18 05:25:03 |

---

## <a id='teste-perfil-sensorial-csv'></a>teste_perfil_sensorial.csv

**Total de Registros**: 7

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | perfil_sensorial_id | int64 | 2 |
| 2 | perfil_sensorial_paciente_id | int64 | 533 |
| 3 | perfil_sensorial_serie_ecolar | object | 3 série |
| 4 | perfil_sensorial_respondido_por | object | Josivan de Oliveira |
| 5 | perfil_sensorial_parentesco_crianca | object | Pai |
| 6 | perfil_sensorial_data_avaliacao | object | 2022-06-24 |
| 7 | perfil_sensorial_registration_date | object | 2022-07-06 |

### Amostra de Dados

|   perfil_sensorial_id |   perfil_sensorial_paciente_id | perfil_sensorial_serie_ecolar   | perfil_sensorial_respondido_por   | perfil_sensorial_parentesco_crianca   | perfil_sensorial_data_avaliacao   | perfil_sensorial_registration_date   |  
|----------------------:|-------------------------------:|:--------------------------------|:----------------------------------|:--------------------------------------|:----------------------------------|:-------------------------------------|  
|                     2 |                            533 | 3 série                         | Josivan de Oliveira               | Pai                                   | 2022-06-24                        | 2022-07-06                           |  
|                     3 |                           1499 | nan                             | Leiliane                          | Mãe                                   | 2022-08-18                        | 2022-08-18                           |  
|                     4 |                            883 | Agrupamento V                   | Pamela                            | Mãe                                   | 2022-08-24                        | 2022-08-25                           |  
|                     7 |                           1662 | Agrupamento 3                   | Fabiana carneiro de Oliveira      | Mãe                                   | 2022-08-29                        | 2022-08-29                           |  
|                     8 |                            617 | nan                             | Luciana                           | Mãe                                   | 2022-09-23                        | 2022-09-23                           |

---

## <a id='teste-perfil-sensorial-pacientes-csv'></a>teste_perfil_sensorial_pacientes.csv

**Total de Registros**: 306

**Total de Colunas**: 7

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | sensorial_paciente_id | int64 | 500 |
| 2 | perfil_sensorial_id | float64 | NULL |
| 3 | sensorial_id | int64 | 114 |
| 4 | ps_client_id | int64 | 1662 |
| 5 | sensorial_paciente_ponto | int64 | 3 |
| 6 | sensorial_paciente_registration_date | object | 2022-09-27 09:23:32 |
| 7 | sensorial_paciente_lastupdate | object | 2022-09-27 12:23:32 |

### Amostra de Dados

|   sensorial_paciente_id |   perfil_sensorial_id |   sensorial_id |   ps_client_id |   sensorial_paciente_ponto | sensorial_paciente_registration_date   | sensorial_paciente_lastupdate   |  
|------------------------:|----------------------:|---------------:|---------------:|---------------------------:|:---------------------------------------|:--------------------------------|  
|                     500 |                   nan |            114 |           1662 |                          3 | 2022-09-27 09:23:32                    | 2022-09-27 12:23:32             |  
|                     499 |                   nan |            119 |           1662 |                          4 | 2022-09-27 09:23:11                    | 2022-09-27 12:23:11             |  
|                     498 |                   nan |            124 |           1662 |                          5 | 2022-09-27 09:22:57                    | 2022-09-27 12:22:57             |  
|                     497 |                   nan |            123 |           1662 |                          4 | 2022-09-27 09:22:43                    | 2022-09-27 12:22:43             |  
|                     496 |                   nan |            122 |           1662 |                          5 | 2022-09-27 09:22:32                    | 2022-09-27 12:22:32             |

---

## <a id='teste-perfil-sensorial-perguntas-csv'></a>teste_perfil_sensorial_perguntas.csv

**Total de Registros**: 124

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | sensorial_id | int64 | 1 |
| 2 | sensorial_classificacao | object | A – Audição |
| 3 | sensorial_item | object | Responde com irritação ou fica incomodado com s... |
| 4 | sensorial_fator | float64 | 5.0 |
| 5 | sensorial_sessao | int64 | 1 |

### Amostra de Dados

|   sensorial_id | sensorial_classificacao   | sensorial_item                                                                                |   sensorial_fator |   sensorial_sessao |  
|---------------:|:--------------------------|:----------------------------------------------------------------------------------------------|------------------:|-------------------:|  
|              1 | A – Audição               | Responde com irritação ou fica incomodado com sons inesperados ou altos                       |               nan |                  1 |  
|              2 | A – Audição               | Tampa os ouvidos com as mãos para se proteger dos sons                                        |               nan |                  1 |  
|              3 | A – Audição               | Tem dificuldade em completar tarefas quando o rádio está ligado                               |                 5 |                  1 |  
|              4 | A – Audição               | Distrai-se ou tem dificuldade em funcionar se há muito barulho ao redor, como um rádio ligado |                 5 |                  1 |  
|              5 | A – Audição               | Não consegue trabalhar com barulho de fundo                                                   |                 5 |                  1 |

---

## <a id='teste-vineland-csv'></a>teste_vineland.csv

**Total de Registros**: 297

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | vineland_id | int64 | 1 |
| 2 | vineland_area | object | Área da Comunicação |
| 3 | vineland_habilidade | object | Receptiva |
| 4 | vineland_item | object | Volta os olhos e a cabeça em direção ao som. |

### Amostra de Dados

|   vineland_id | vineland_area       | vineland_habilidade   | vineland_item                                                  |  
|--------------:|:--------------------|:----------------------|:---------------------------------------------------------------|  
|             1 | Área da Comunicação | Receptiva             | Volta os olhos e a cabeça em direção ao som.                   |  
|             2 | Área da Comunicação | Receptiva             | Ouve, pelo menos momentaneamente, quando o educador fala.      |  
|             3 | Área da Comunicação | Receptiva             | Estende os braços quando o educador diz: "Vem cá." Ou "Upa."   |  
|             4 | Área da Comunicação | Receptiva             | Demonstra compreender a palavra "não".                         |  
|             5 | Área da Comunicação | Receptiva             | Demonstra compreender o significado de pelo menos 10 palavras. |

---

## <a id='teste-vineland-pacientes-csv'></a>teste_vineland_pacientes.csv

**Total de Registros**: 717

**Total de Colunas**: 6

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | vineland_paciente_id | int64 | 1 |
| 2 | vineland_id | int64 | 151 |
| 3 | ps_client_id | int64 | 1132 |
| 4 | vineland_paciente_ponto | int64 | 0 |
| 5 | vineland_paciente_registration_date | object | 2022-01-18 09:42:19 |
| 6 | vineland_paciente_lastupdate | object | 2022-01-18 12:42:19 |

### Amostra de Dados

|   vineland_paciente_id |   vineland_id |   ps_client_id |   vineland_paciente_ponto | vineland_paciente_registration_date   | vineland_paciente_lastupdate   |  
|-----------------------:|--------------:|---------------:|--------------------------:|:--------------------------------------|:-------------------------------|  
|                      1 |           151 |           1132 |                         0 | 2022-01-18 09:42:19                   | 2022-01-18 12:42:19            |  
|                      2 |           138 |           1132 |                         0 | 2022-01-18 09:42:22                   | 2022-01-18 12:42:22            |  
|                      3 |           151 |            435 |                         0 | 2022-03-25 10:14:56                   | 2022-03-25 13:14:56            |  
|                      4 |            44 |           2511 |                         1 | 2022-03-25 11:21:32                   | 2022-03-25 14:21:32            |  
|                      5 |            35 |           2511 |                         0 | 2022-03-25 11:22:27                   | 2022-03-25 14:22:27            |

---

## <a id='ws-certificados-csv'></a>ws_certificados.csv

**Total de Registros**: 244

**Total de Colunas**: 11

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | certificado_id | int64 | 2 |
| 2 | certificado_ws_user_id | int64 | 610 |
| 3 | certificado_tipo | object | Curso |
| 4 | certificado_nome | object | Simpósio Clínica Larissa Martins Ferreira  |
| 5 | certificado_nome_instituicao | object | Clínica Larissa Martins Ferreira  |
| 6 | certificado_data_inicio | object | 2022-08-20 |
| 7 | certificado_data_fim | object | 2022-08-20 |
| 8 | certificado_qtde_horas | int64 | 9 |
| 9 | certificado_arquivo | object | files/2022/08/curso-simposio-clinica-larissa-ma... |
| 10 | certificado_arquivo_id | float64 | 83.0 |
| 11 | certificado_registration_date | object | 2022-08-26 14:15:30 |

### Amostra de Dados

|   certificado_id |   certificado_ws_user_id | certificado_tipo   | certificado_nome                          | certificado_nome_instituicao     | certificado_data_inicio   | certificado_data_fim   |   certificado_qtde_horas | certificado_arquivo                                               |   certificado_arquivo_id | certificado_registration_date   |  
|-----------------:|-------------------------:|:-------------------|:------------------------------------------|:---------------------------------|:--------------------------|:-----------------------|-------------------------:|:------------------------------------------------------------------|-------------------------:|:--------------------------------|  
|                2 |                      610 | Curso              | Simpósio Clínica Larissa Martins Ferreira | Clínica Larissa Martins Ferreira | 2022-08-20                | 2022-08-20             |                        9 | files/2022/08/curso-simposio-clinica-larissa-martins-ferreira.pdf |                       83 | 2022-08-26 14:15:30             |  
|                3 |                     1140 | Curso              | Aba e Estratégias Naturalistas            | Instituto Singular               | 2021-05-16                | 2021-06-16             |                      100 | files/2022/08/curso-aba-e-estrategias-naturalistas.pdf            |                       84 | 2022-08-31 19:22:20             |  
|                4 |                     1140 | Curso              | Apraxia de Fala na Infância- Introdutório | Abrapraxia                       | 2022-05-15                | 2022-05-15             |                        4 | files/2022/08/curso-apraxia-de-fala-na-infancia-introdutorio.pdf  |                       85 | 2022-08-31 19:25:31             |  
|                5 |                     1140 | Curso              | MultiGestos Fala                          | Multigestos por Cinthia Azevedo  | 2022-08-13                | 2022-08-13             |                       11 | files/2022/08/curso-multigestos-fala.pdf                          |                       86 | 2022-08-31 19:27:23             |  
|                6 |                     1140 | Curso              | Autismo e Seletividade Alimentar          | Instituto Neuro                  | 2022-06-22                | 2022-08-04             |                      120 | files/2022/08/curso-autismo-e-seletividade-alimentar.pdf          |                       87 | 2022-08-31 19:30:45             |

---

## <a id='ws-config-csv'></a>ws_config.csv

**Total de Registros**: 0

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | conf_id | object | NULL |
| 2 | conf_key | object | NULL |
| 3 | conf_value | object | NULL |
| 4 | conf_type | object | NULL |


---

## <a id='ws-config-profiles-csv'></a>ws_config_profiles.csv

**Total de Registros**: 15

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | profile_id | int64 | 1 |
| 2 | profile_name | object | Master |
| 3 | profile_registration_date | object | 2018-04-05 12:08:38 |
| 4 | profile_lastupdate | object | 2018-04-05 15:08:54 |
| 5 | profile_status | int64 | 1 |

### Amostra de Dados

|   profile_id | profile_name   | profile_registration_date   | profile_lastupdate   |   profile_status |  
|-------------:|:---------------|:----------------------------|:---------------------|-----------------:|  
|            1 | Master         | 2018-04-05 12:08:38         | 2018-04-05 15:08:54  |                1 |  
|            2 | Cliente        | 2018-04-16 15:08:14         | 2018-04-16 18:08:20  |                1 |  
|            3 | Profissional   | 2019-04-17 18:20:53         | 2019-04-17 21:21:05  |                1 |  
|            6 | Online         | 2020-04-10 18:45:34         | 2020-04-10 21:48:41  |                1 |  
|            8 | Administrador  | 2021-04-23 16:26:55         | 2021-04-23 19:27:12  |                1 |

---

## <a id='ws-config-profiles-permissions-csv'></a>ws_config_profiles_permissions.csv

**Total de Registros**: 776

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | pp_id | int64 | 1 |
| 2 | profile_id | int64 | 1 |
| 3 | pp_app | object | APP_DASHBOARD |
| 4 | pp_crud | int64 | 3 |

### Amostra de Dados

|   pp_id |   profile_id | pp_app                       |   pp_crud |  
|--------:|-------------:|:-----------------------------|----------:|  
|       1 |            1 | APP_DASHBOARD                |         3 |  
|       2 |            1 | APP_CLIENTS                  |         3 |  
|       3 |            1 | APP_SCHEDULE_BY_ROOM         |         3 |  
|       4 |            1 | APP_SCHEDULE_BY_PROFESSIONAL |         3 |  
|       5 |            1 | APP_SCHEDULE_BY_CLIENT       |         3 |

---

## <a id='ws-especialidades-csv'></a>ws_especialidades.csv

**Total de Registros**: 41

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | especialidade_id | int64 | 1 |
| 2 | especialidade_name | object | CONSULTA |
| 3 | especialidade_anexo | object | Não |
| 4 | especialidade_status | object | A |

### Amostra de Dados

|   especialidade_id | especialidade_name   | especialidade_anexo   | especialidade_status   |  
|-------------------:|:---------------------|:----------------------|:-----------------------|  
|                  1 | CONSULTA             | Não                   | A                      |  
|                  3 | PROMPT               | Sim                   | A                      |  
|                  4 | RELATORIO            | Não                   | A                      |  
|                  5 | NEUROFEEDBACK        | Não                   | A                      |  
|                  6 | P.E.I                | Não                   | A                      |

---

## <a id='ws-lista-espera-csv'></a>ws_lista_espera.csv

**Total de Registros**: 6,237

**Total de Colunas**: 21

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | ws_lista_id | int64 | 5 |
| 2 | ws_lista_data_solicitacao | object | 2022-07-26 |
| 3 | ws_lista_convenio | object | Unimed |
| 4 | ws_lista_nome_paciente | object | Hadassa Gonçalves Guimarães |
| 5 | ws_lista_nome_responsavel | object | Sara Gonsalves marra Guimarães |
| 6 | ws_lista_telefone_contato | int64 | 62999647576 |
| 7 | ws_lista_data_nascimento | object | 11/04/2019 |
| 8 | ws_lista_cpf | int64 | 10056310188 |
| 9 | ws_lista_periodo_atendimento | float64 | NULL |
| 10 | ws_lista_guia | object | Não |
| 11 | ws_lista_relatorio_medico_file | float64 | NULL |
| 12 | ws_lista_relatorio_medico | float64 | NULL |
| 13 | ws_lista_tea | float64 | NULL |
| 14 | ws_lista_pagamento_cooparticipacao | float64 | NULL |
| 15 | ws_lista_aplicativo | float64 | NULL |
| 16 | ws_lista_diagnostico | float64 | NULL |
| 17 | ws_lista_horas | float64 | NULL |
| 18 | ws_lista_situacao | object | Finalizado |
| 19 | ws_lista_observacao | object | ja é paciente da clinica.  |
| 20 | ws_lista_colaborador_responsavel | float64 | NULL |
| 21 | ws_lista_data_agendamento | float64 | NULL |

### Amostra de Dados

|   ws_lista_id | ws_lista_data_solicitacao   | ws_lista_convenio   | ws_lista_nome_paciente        | ws_lista_nome_responsavel            |   ws_lista_telefone_contato | ws_lista_data_nascimento   |   ws_lista_cpf |   ws_lista_periodo_atendimento | ws_lista_guia   |   ws_lista_relatorio_medico_file |   ws_lista_relatorio_medico |   ws_lista_tea |   ws_lista_pagamento_cooparticipacao |   ws_lista_aplicativo |   ws_lista_diagnostico |   ws_lista_horas | ws_lista_situacao   | ws_lista_observacao                                                                             |   ws_lista_colaborador_responsavel |   ws_lista_data_agendamento |  
|--------------:|:----------------------------|:--------------------|:------------------------------|:-------------------------------------|----------------------------:|:---------------------------|---------------:|-------------------------------:|:----------------|---------------------------------:|----------------------------:|---------------:|-------------------------------------:|----------------------:|-----------------------:|-----------------:|:--------------------|:------------------------------------------------------------------------------------------------|-----------------------------------:|----------------------------:|  
|             5 | 2022-07-26                  | Unimed              | Hadassa Gonçalves Guimarães   | Sara Gonsalves marra Guimarães       |                 62999647576 | 11/04/2019                 |    10056310188 |                            nan | Não             |                              nan |                         nan |            nan |                                  nan |                   nan |                    nan |              nan | Finalizado          | ja é paciente da clinica.                                                                       |                                nan |                         nan |  
|             6 | 2022-07-26                  | Unimed              | Luiz Augusto Santos Cunha     | Katilene da Silva Santos Cunha       |                  6295330365 | 01/12/2019                 |    10470542136 |                            nan | Não             |                              nan |                         nan |            nan |                                  nan |                   nan |                    nan |              nan | Finalizado          | entrei em contato coma mãe no dia 29/08 , e o paciente ja esta em atendimento em outra cliníca. |                                nan |                         nan |  
|             7 | 2022-07-26                  | Outros convênios    | Samuel  Henrique  Viana sousa | Sergiana Viana silva                 |                 62985032937 | 13/03/2019                 |     9990830150 |                            nan | Não             |                              nan |                         nan |            nan |                                  nan |                   nan |                    nan |              nan | Finalizado          | Paciente realizou o cadastro errado. Plano Unimed. Adicionado na lista.                         |                                nan |                         nan |  
|             8 | 2022-07-27                  | Unimed              | Joaquim Veloso Guimarães      | Tayssa Paula Borges Veloso Guimarães |                 62999822108 | 04/05/17                   |     8440317123 |                            nan | Não             |                              nan |                         nan |            nan |                                  nan |                   nan |                    nan |              nan | Finalizado          | mandei mensagem no dia 29, paciente ja esta sendo atendido em outra clínica.                    |                                nan |                         nan |  
|             9 | 2022-07-27                  | Unimed              | Rosangela Ramalho Soares      | Rosangela Ramalho Soares             |                 11946439387 | 28/03/1993                 |    40617657874 |                            nan | Não             |                              nan |                         nan |            nan |                                  nan |                   nan |                    nan |              nan | Não iniciado        | nan                                                                                             |                                nan |                         nan |

---

## <a id='ws-lista-espera-temp-csv'></a>ws_lista_espera_temp.csv

**Total de Registros**: 1,985

**Total de Colunas**: 14

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | object | wpclicb12686395larissamartins:244924389420 |
| 2 | convenio | object | Unimed |
| 3 | nome_paciente | object | Liz Machado Alves |
| 4 | nome_responsavel | object | Luciana Machado Alves |
| 5 | telefone_contato | object | +244 924 389 420 |
| 6 | data_nascimento | object | 14/12/2009 |
| 7 | cpf | object | 04/02/2019 |
| 8 | periodo_atendimento | object | Tarde |
| 9 | relatorio_medico | object | Sim |
| 10 | guia | float64 | NULL |
| 11 | tea | float64 | NULL |
| 12 | pagamento_cooparticipacao | float64 | NULL |
| 13 | aplicativo | float64 | NULL |
| 14 | created_at | object | 2023-08-03 10:47:48 |

### Amostra de Dados

| id                                          | convenio   | nome_paciente             | nome_responsavel                 | telefone_contato   | data_nascimento   | cpf            | periodo_atendimento   | relatorio_medico   |   guia |   tea |   pagamento_cooparticipacao |   aplicativo | created_at          |  
|:--------------------------------------------|:-----------|:--------------------------|:---------------------------------|:-------------------|:------------------|:---------------|:----------------------|:-------------------|-------:|------:|----------------------------:|-------------:|:--------------------|  
| wpclicb12686395larissamartins:244924389420  | Unimed     | Liz Machado Alves         | Luciana Machado Alves            | +244 924 389 420   | 14/12/2009        | nan            | nan                   | nan                |    nan |   nan |                         nan |          nan | 2023-08-03 10:47:48 |  
| wpclicb12686395larissamartins:5517991671180 | Unimed     | Joaquim crivellari mendes | Vick taynnara furtado crivellari | nan                | 17991671180       | 04/02/2019     | nan                   | nan                |    nan |   nan |                         nan |          nan | 2023-04-28 00:00:00 |  
| wpclicb12686395larissamartins:5534992188186 | Unimed     | Stenio Facioli Alves      | nan                              | nan                | nan               | nan            | nan                   | nan                |    nan |   nan |                         nan |          nan | 2023-05-16 00:00:00 |  
| wpclicb12686395larissamartins:5538991373076 | Unimed     | Francisco Farias Baliza   | Ângela Taynah Santana Farias     | 38991373076        | 04/02/21          | 186.967.816-86 | Tarde                 | Sim                |    nan |   nan |                         nan |          nan | 2023-04-18 00:00:00 |  
| wpclicb12686395larissamartins:5561996188195 | Unimed     | Julia Gomes Reviglio      | Angelica Gomes Reviglio          | 61 99618-8195      | nan               | 26/10/2015     | nan                   | nan                |    nan |   nan |                         nan |          nan | 2023-05-08 00:00:00 |

---

## <a id='ws-mudanca-horario-csv'></a>ws_mudanca_horario.csv

**Total de Registros**: 5,405

**Total de Colunas**: 13

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | ws_mudanca_id | int64 | 8 |
| 2 | ws_mudanca_data_solicitacao | object | 2022-07-26 |
| 3 | ws_mudanca_unidade | object | Oeste |
| 4 | ws_mudanca_nome_paciente | object | Vanessa |
| 5 | ws_mudanca_telefone_contato | int64 | 556296025937 |
| 6 | ws_mudanca_tipo | object | Agendamento - Alterar horario |
| 7 | ws_mudanca_especialidade | float64 | NULL |
| 8 | ws_mudanca_dia_semana | float64 | NULL |
| 9 | ws_mudanca_hora | float64 | NULL |
| 10 | ws_mudanca_descricao_solicitacao | object | Gentileza alterar meu horário |
| 11 | ws_mudanca_descricao_andamento | object | TESTE  |
| 12 | ws_mudanca_situacao | object | Finalizado |
| 13 | ws_mudanca_observacao | object | TESTE  |

### Amostra de Dados

|   ws_mudanca_id | ws_mudanca_data_solicitacao   | ws_mudanca_unidade   | ws_mudanca_nome_paciente          |   ws_mudanca_telefone_contato | ws_mudanca_tipo               |   ws_mudanca_especialidade |   ws_mudanca_dia_semana |   ws_mudanca_hora | ws_mudanca_descricao_solicitacao                                                                                                                                     | ws_mudanca_descricao_andamento                                                                                                     | ws_mudanca_situacao   | ws_mudanca_observacao   |  
|----------------:|:------------------------------|:---------------------|:----------------------------------|------------------------------:|:------------------------------|---------------------------:|------------------------:|------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|:----------------------|:------------------------|  
|               8 | 2022-07-26                    | Oeste                | Vanessa                           |                  556296025937 | Agendamento - Alterar horario |                        nan |                     nan |               nan | Gentileza alterar meu horário                                                                                                                                        | TESTE                                                                                                                              | Finalizado            | TESTE                   |  
|               9 | 2022-07-26                    | Oeste                | Rafael Tavares de Oliveira        |                  556284577130 | Agendamento - Remover horario |                        nan |                     nan |               nan | Retirar atendimento da psicóloga horlanda<br /><br />                                                                                                                | A profissional Brenda Psicóloga não tem disponibilidade de horários, sendo assim a mesma preferiu retirar a profissional Horlanda. | Finalizado            | nan                     |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   | E tentar colocar a psicóloga Brenda<br /><br />                                                                                                                      |                                                                                                                                    |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   | Na quarta ou na sexta<br /><br />                                                                                                                                    |                                                                                                                                    |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   | Junto com os outros atendimentos dele                                                                                                                                |                                                                                                                                    |                       |                         |  
|              10 | 2022-07-26                    | Oeste                | Otávio farias loiola Jordao Sousa |                  556281245757 | Agendamento - Alterar horario |                        nan |                     nan |               nan | Os horários da fono e Psicologa estão a tarde, porém ele vai começar na escola semana que vem, no período vespertino,… daí precisamos mudar os horários das terapias | Foi inserido na agenda na parte da manhã como o responsavel havia solicitado.                                                      | Finalizado            | nan                     |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   |                                                                                                                                                                      |                                                                                                                                    |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   |                                                                                                                                                                      | Alteração                                                                                                                          |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   |                                                                                                                                                                      |                                                                                                                                    |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   |                                                                                                                                                                      | Quinta as 10h com Adriele Fono                                                                                                     |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   |                                                                                                                                                                      |                                                                                                                                    |                       |                         |  
|                 |                               |                      |                                   |                               |                               |                            |                         |                   |                                                                                                                                                                      | Quinta as 11h com a Psicóloga                                                                                                      |                       |                         |  
|              11 | 2022-07-27                    | Oeste                | Vanessa                           |                  556296025937 | Agendamento - Alterar horario |                        nan |                     nan |               nan | Desejo trocar o horário                                                                                                                                              | TESTE                                                                                                                              | Finalizado            | TESTE                   |  
|              16 | 2022-07-28                    | Oeste                | Catiane de Jesus Barbosa          |                  556282524950 | Agendamento - Incluir horario |                        nan |                     nan |               nan | Quero agendamento de consultas com a psicóloga                                                                                                                       | nan                                                                                                                                | Finalizado            | nan                     |

---

## <a id='ws-mudanca-horario-temp-csv'></a>ws_mudanca_horario_temp.csv

**Total de Registros**: 319

**Total de Colunas**: 10

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | object | wp460793540449521:447862262095 |
| 2 | unidade | object | Bueno |
| 3 | nome_paciente | object | SOPHIA PASSOS SANTOS |
| 4 | tipo | object | Alterar |
| 5 | telefone_contato | float64 | NULL |
| 6 | especialidade | object | Bom dia |
| 7 | dia_semana | object | Quinta-feira |
| 8 | hora | float64 | NULL |
| 9 | descricao_solicitacao | object | Quero tentar a vaga com determinado profissiona... |
| 10 | created_at | object | 2025-01-13 20:18:05 |

### Amostra de Dados

| id                              | unidade            | nome_paciente              | tipo    |   telefone_contato | especialidade   | dia_semana                  |   hora | descricao_solicitacao                                                        | created_at          |  
|:--------------------------------|:-------------------|:---------------------------|:--------|-------------------:|:----------------|:----------------------------|-------:|:-----------------------------------------------------------------------------|:--------------------|  
| wp460793540449521:447862262095  | nan                | nan                        | nan     |                nan | nan             | Quinta-feira                |    nan | nan                                                                          | 2025-01-13 20:18:05 |  
| wp460793540449521:5562981135415 | Bueno              | SOPHIA PASSOS SANTOS       | Alterar |                nan | Bom dia         | nan                         |    nan | nan                                                                          | 2024-11-12 14:06:41 |  
| wp460793540449521:5562981366384 | Oeste              | Luna Sophia Nunes Ribeiro  | Alterar |                nan | Psicologia      | Terça-feira                 |    nan | Quero tentar a vaga com determinado profissional, não me lembro agora o nome | 2024-10-28 16:41:43 |  
| wp460793540449521:5562981480469 | Rua 10             | SABRINA ABIB CLÁUDIO       | Alterar |                nan | Psicopedagogia  | Quarta-feira                |    nan | O horário seria hoje mas não pode8comparecer hoje                            | 2025-01-14 13:06:05 |  
| wp460793540449521:5562981566102 | Av. Rep. do Líbado | João Miguel Santos Barbosa | Alterar |                nan | Psicologia      | Preciso falar com atendente |    nan | Preciso que seja com a Brenda vespertino em qualquer horário                 | 2024-11-27 16:19:42 |

---

## <a id='ws-noticias-csv'></a>ws_noticias.csv

**Total de Registros**: 0

**Total de Colunas**: 11

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | noticia_id | object | NULL |
| 2 | noticia_tipo | object | NULL |
| 3 | noticia_titulo | object | NULL |
| 4 | noticia_descricao | object | NULL |
| 5 | noticia_data | object | NULL |
| 6 | noticia_file | object | NULL |
| 7 | noticia_nivel | object | NULL |
| 8 | setor_id | object | NULL |
| 9 | noticia_carrossel | object | NULL |
| 10 | noticia_registration_date | object | NULL |
| 11 | noticia_lastupdate | object | NULL |


---

## <a id='ws-pagamentos-csv'></a>ws_pagamentos.csv

**Total de Registros**: 31

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | pagamento_id | int64 | 1 |
| 2 | pagamento_name | object | Particular |
| 3 | pagamento_carteirinha_obrigatoria | object | Nao |
| 4 | pagamento_status | object | A |

### Amostra de Dados

|   pagamento_id | pagamento_name         | pagamento_carteirinha_obrigatoria   | pagamento_status   |  
|---------------:|:-----------------------|:------------------------------------|:-------------------|  
|              1 | Particular             | Nao                                 | A                  |  
|              2 | Plano de Saúde         | Nao                                 | I                  |  
|              3 | Unimed Goiânia Guia    | nan                                 | A                  |  
|              4 | Unimed Goiânia Liminar | nan                                 | A                  |  
|              5 | Unimed Central         | Nao                                 | I                  |

---

## <a id='ws-pagamentos-x-codigos-faturamento-csv'></a>ws_pagamentos_x_codigos_faturamento.csv

**Total de Registros**: 104

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | codigo_faturamento_id | int64 | 4 |
| 2 | codigo_faturamento_numero | int64 | 10000001 |
| 3 | pagamento_id | int64 | 1 |
| 4 | codigo_faturamento_descricao | object | SESSAO PSICOTERAPIA |

### Amostra de Dados

|   codigo_faturamento_id |   codigo_faturamento_numero |   pagamento_id | codigo_faturamento_descricao   |  
|------------------------:|----------------------------:|---------------:|:-------------------------------|  
|                       4 |                    10000001 |              1 | SESSAO PSICOTERAPIA            |  
|                       5 |                       11193 |              6 | PSICOLOGIA - TEA               |  
|                       7 |                       11185 |              6 | FONOAUDIOLOGIA - TEA           |  
|                       8 |                       40045 |              6 | TERAPIA OCUPACIONAL - TEA      |  
|                       9 |                    50001221 |              6 | PSICOLOGIA - ANAMNESE          |

---

## <a id='ws-patologia-csv'></a>ws_patologia.csv

**Total de Registros**: 71

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | patologia_id | int64 | 1 |
| 2 | patologia_name | object | TDAH |
| 3 | patologia_status | object | A |

### Amostra de Dados

|   patologia_id | patologia_name        | patologia_status   |  
|---------------:|:----------------------|:-------------------|  
|              1 | TDAH                  | A                  |  
|              2 | TEA                   | A                  |  
|              3 | Apraxia de Fala       | A                  |  
|              5 | Atraso de Linguagem   | A                  |  
|              6 | Dificuldade Cognitiva | A                  |

---

## <a id='ws-patologia-cliente-csv'></a>ws_patologia_cliente.csv

**Total de Registros**: 1,947

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | patologia_cliente_id | int64 | 5 |
| 2 | client_id | int64 | 50 |
| 3 | patologia_id | int64 | 13 |

### Amostra de Dados

|   patologia_cliente_id |   client_id |   patologia_id |  
|-----------------------:|------------:|---------------:|  
|                      5 |          50 |             13 |  
|                      6 |          72 |              8 |  
|                     15 |         225 |             39 |  
|                     17 |         304 |              1 |  
|                     18 |         319 |              2 |

---

## <a id='ws-profissoes-csv'></a>ws_profissoes.csv

**Total de Registros**: 12

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | profissao_id | int64 | 1 |
| 2 | profissao_name | object | Psicologia |
| 3 | profissao_status | object | A |

### Amostra de Dados

|   profissao_id | profissao_name   | profissao_status   |  
|---------------:|:-----------------|:-------------------|  
|              1 | Psicologia       | A                  |  
|              2 | Fonoaudiologia   | A                  |  
|              3 | Fisioterapia     | A                  |  
|              4 | Musicoterapia    | A                  |  
|              5 | Neuropedagoga    | A                  |

---

## <a id='ws-profissoes-rooms-csv'></a>ws_profissoes_rooms.csv

**Total de Registros**: 293

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 1 |
| 2 | profissao_id | int64 | 8 |
| 3 | room_id | int64 | 17 |
| 4 | room_local_id | int64 | 1 |
| 5 | room_qtde | int64 | 0 |

### Amostra de Dados

|   id |   profissao_id |   room_id |   room_local_id |   room_qtde |  
|-----:|---------------:|----------:|----------------:|------------:|  
|    1 |              8 |        17 |               1 |           0 |  
|    2 |              8 |        42 |               1 |           0 |  
|    3 |              8 |        21 |               1 |           0 |  
|    4 |              8 |        35 |               1 |           0 |  
|    5 |              7 |        41 |               1 |           0 |

---

## <a id='ws-setores-csv'></a>ws_setores.csv

**Total de Registros**: 6

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | setor_id | int64 | 3 |
| 2 | setor_name | object | AGENDAMENTO  |
| 3 | setor_status | object | A |

### Amostra de Dados

|   setor_id | setor_name       | setor_status   |  
|-----------:|:-----------------|:---------------|  
|          3 | AGENDAMENTO      | A              |  
|          4 | CENTRAL DE GUIAS | A              |  
|          7 | AUDITORIA        | A              |  
|          6 | RECURSOS HUMANOS | A              |  
|          8 | ZELADORIA        | A              |

---

## <a id='ws-siteviews-online-csv'></a>ws_siteviews_online.csv

**Total de Registros**: 0

**Total de Colunas**: 8

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | online_id | object | NULL |
| 2 | online_user | object | NULL |
| 3 | online_name | object | NULL |
| 4 | online_startview | object | NULL |
| 5 | online_endview | object | NULL |
| 6 | online_ip | object | NULL |
| 7 | online_url | object | NULL |
| 8 | online_agent | object | NULL |


---

## <a id='ws-siteviews-views-csv'></a>ws_siteviews_views.csv

**Total de Registros**: 429,435

**Total de Colunas**: 5

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | views_id | int64 | 1 |
| 2 | views_date | object | 2018-02-19 |
| 3 | views_users | float64 | 1.0 |
| 4 | views_views | float64 | 1.0 |
| 5 | views_pages | float64 | 44.0 |

### Amostra de Dados

|   views_id | views_date   |   views_users |   views_views |   views_pages |  
|-----------:|:-------------|--------------:|--------------:|--------------:|  
|          1 | 2018-02-19   |             1 |             1 |            44 |  
|          2 | 2018-02-20   |             5 |             5 |         63451 |  
|          3 | 2018-02-21   |             1 |             1 |         32735 |  
|          4 | 2018-02-22   |             1 |             1 |           154 |  
|          5 | 2018-02-23   |             1 |             1 |            11 |

---

## <a id='ws-tipos-desagendamentos-csv'></a>ws_tipos_desagendamentos.csv

**Total de Registros**: 26

**Total de Colunas**: 6

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | desagendamento_id | int64 | 1 |
| 2 | desagendamento_nome | object | Atestado (anexar documento em sistema) |
| 3 | desagendamento_contabilizar | object | NAO |
| 4 | desagendamento_status | object | A |
| 5 | desagendamento_tipo | object | paciente |
| 6 | desagendamento_anexar | object | SIM |

### Amostra de Dados

|   desagendamento_id | desagendamento_nome                                   | desagendamento_contabilizar   | desagendamento_status   | desagendamento_tipo   | desagendamento_anexar   |  
|--------------------:|:------------------------------------------------------|:------------------------------|:------------------------|:----------------------|:------------------------|  
|                   1 | Atestado (anexar documento em sistema)                | NAO                           | A                       | paciente              | SIM                     |  
|                   2 | Férias (uma semana por ano)                           | NAO                           | A                       | paciente              | NÃO                     |  
|                   3 | Sintomas COVID (não enviou resultado teste)           | SIM                           | A                       | paciente              | NÃO                     |  
|                   4 | Sem Justificativa (não nos comunicou por nenhum meio) | SIM                           | A                       | paciente              | NÃO                     |  
|                   5 | Condições externas                                    | SIM                           | A                       | paciente              | NÃO                     |

---

## <a id='ws-titulacoes-csv'></a>ws_titulacoes.csv

**Total de Registros**: 12

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | titulacao_id | int64 | 2 |
| 2 | titulacao_nome | object | Estagiário |
| 3 | titulacao_supervirora | object | Não |
| 4 | titulacao_status | object | Ativa |

### Amostra de Dados

|   titulacao_id | titulacao_nome    | titulacao_supervirora   | titulacao_status   |  
|---------------:|:------------------|:------------------------|:-------------------|  
|              2 | Estagiário        | Não                     | Ativa              |  
|              3 | Estagiário RH     | Não                     | Ativa              |  
|              4 | Especializando I  | Não                     | Ativa              |  
|              5 | Especializando II | Não                     | Ativa              |  
|              6 | Especialista      | Não                     | Ativa              |

---

## <a id='ws-users-csv'></a>ws_users.csv

**Total de Registros**: 2,169

**Total de Colunas**: 42

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | user_id | int64 | 1 |
| 2 | user_thumb | object | images/2018/02/1-marcusmolinari-1519220212.png |
| 3 | user_name | object | MARCUS |
| 4 | user_lastname | object | MOLINARI |
| 5 | user_document | object | 019.385.021-40 |
| 6 | user_genre | float64 | 1.0 |
| 7 | user_datebirth | float64 | NULL |
| 8 | user_telephone | object | (62) 36120-899 |
| 9 | user_cell | object | (62) 99920-0887 |
| 10 | user_email | object | marcus@mbmdigital.com.br |
| 11 | user_password | object | 8e9181875d91792546d9bf6a44907f7944dfa1adaa7eeca... |
| 12 | user_channel | float64 | NULL |
| 13 | user_registration | object | 2018-02-19 22:40:17 |
| 14 | user_lastupdate | float64 | NULL |
| 15 | user_lastaccess | object | 2022-02-02 00:50:54 |
| 16 | user_login | float64 | 1643763054.0 |
| 17 | user_login_cookie | object | 04b37fef79ebd7fca5888e9194383c4f3f4d89251375da7... |
| 18 | user_client | int64 | 0 |
| 19 | user_level | int64 | 10 |
| 20 | user_profile | int64 | 1 |
| 21 | user_facebook | float64 | NULL |
| 22 | user_twitter | float64 | NULL |
| 23 | user_youtube | float64 | NULL |
| 24 | user_google | float64 | NULL |
| 25 | user_blocking_reason | float64 | NULL |
| 26 | user_franchise | int64 | 1 |
| 27 | user_price_external | float64 | 0.0 |
| 28 | user_price_internal | float64 | 0.0 |
| 29 | user_status | int64 | 1 |
| 30 | user_profission_name | object | Psicologia |
| 31 | user_supervisor | object | NAO |
| 32 | user_titulacao_id | float64 | NULL |
| 33 | user_sala_fixa | float64 | NULL |
| 34 | user_foto_assinatura | object | images/2023/12/4-larissamartins-ferreira-170242... |
| 35 | user_registro_conselho | float64 | NULL |
| 36 | user_conselho_id | float64 | NULL |
| 37 | user_conselho_uf | float64 | NULL |
| 38 | user_tipo_pagamento_id | float64 | NULL |
| 39 | user_escolaridade | float64 | NULL |
| 40 | user_data_admissao | object | 2018-02-19 |
| 41 | user_setor_id | float64 | NULL |
| 42 | user_estado_civil | float64 | NULL |

### Amostra de Dados

|   user_id | user_thumb                                              | user_name              | user_lastname    | user_document   |   user_genre |   user_datebirth | user_telephone   | user_cell       | user_email                        | user_password                                                                                                                    |   user_channel | user_registration   |   user_lastupdate | user_lastaccess     |    user_login | user_login_cookie                                                                                                                |   user_client |   user_level |   user_profile |   user_facebook |   user_twitter |   user_youtube |   user_google |   user_blocking_reason |   user_franchise |   user_price_external |   user_price_internal |   user_status | user_profission_name   | user_supervisor   |   user_titulacao_id |   user_sala_fixa | user_foto_assinatura                                    |   user_registro_conselho |   user_conselho_id |   user_conselho_uf |   user_tipo_pagamento_id |   user_escolaridade | user_data_admissao   |   user_setor_id |   user_estado_civil |  
|----------:|:--------------------------------------------------------|:-----------------------|:-----------------|:----------------|-------------:|-----------------:|:-----------------|:----------------|:----------------------------------|:---------------------------------------------------------------------------------------------------------------------------------|---------------:|:--------------------|------------------:|:--------------------|--------------:|:---------------------------------------------------------------------------------------------------------------------------------|--------------:|-------------:|---------------:|----------------:|---------------:|---------------:|--------------:|-----------------------:|-----------------:|----------------------:|----------------------:|--------------:|:-----------------------|:------------------|--------------------:|-----------------:|:--------------------------------------------------------|-------------------------:|-------------------:|-------------------:|-------------------------:|--------------------:|:---------------------|----------------:|--------------------:|  
|         1 | images/2018/02/1-marcusmolinari-1519220212.png          | MARCUS                 | MOLINARI         | 019.385.021-40  |            1 |              nan | (62) 36120-899   | (62) 99920-0887 | marcus@mbmdigital.com.br          | 8e9181875d91792546d9bf6a44907f7944dfa1adaa7eeca90c7d5827b31fac6889fce92738ce70239831c0f8ec51fd51b298051bfb14f94b4596ba3d9a824355 |            nan | 2018-02-19 22:40:17 |               nan | 2022-02-02 00:50:54 |   1.64376e+09 | 04b37fef79ebd7fca5888e9194383c4f3f4d89251375da75aa8243120297c7bd8004711aa5104465580b26d6bfd12cec16b1a9cbdfa6b122b881e750dc529bbb |             0 |           10 |              1 |             nan |            nan |            nan |           nan |                    nan |                1 |                   nan |                   nan |             1 | nan                    | nan               |                 nan |              nan | nan                                                     |                      nan |                nan |                nan |                      nan |                 nan | 2018-02-19           |             nan |                 nan |  
|         2 | nan                                                     | EDUARDO                | GUIMARAES        | 036.362.381-75  |            1 |              nan | nan              | nan             | eduardo.humberto1992@gmail.com    | ba3253876aed6bc22d4a6ff53d8406c6ad864195ed144ab5c87621b6c233b548baeae6956df346ec8c17f5ea10f35ee3cbc514797ed7ddd3145464e2a0bab413 |            nan | nan                 |               nan | 2019-01-21 12:09:34 |   1.54807e+09 | bc37232ec3075de1ab06ddcf6cb53068b07a02601aebd1e923b5d963043a67adb7ef889042f22a269f0f8b83ccd9fa2055fef8fca4b74008c97b4b583fea9cd1 |             0 |            0 |              1 |             nan |            nan |            nan |           nan |                    nan |                1 |                     0 |                     0 |             1 | nan                    | nan               |                 nan |              nan | nan                                                     |                      nan |                nan |                nan |                      nan |                 nan | nan                  |             nan |                 nan |  
|         4 | images/2023/07/4-larissamartins-ferreira-1690567278.jpg | LARISSA                | MARTINS FERREIRA | 029.486.441-51  |            2 |              nan | nan              | (62) 98111-9729 | larissaneuropsi@gmail.com         | 439c80295e9b897391ffe9f740d07b869940abbb00a49b565682132d5eeb74d1bbdc4b7010712e5d665bb8e02d7ad19eecfeed8770e7cd0ac0b59ae29ae91bc6 |            nan | 2019-01-11 13:07:49 |               nan | 2025-01-14 17:00:54 |   1.73687e+09 | c91dd7d43a677a1f1ae7bfea518d25c891cf73be32586c848919931bbef43bc703c6888546457fc34efd1578e907fe5fa851b3d3ef5e777144f9f232edaf5aaf |             0 |            9 |              1 |             nan |            nan |            nan |           nan |                    nan |                1 |                   nan |                   nan |             1 | Psicologia             | NAO               |                 nan |              nan | images/2023/12/4-larissamartins-ferreira-1702425725.jpg |                      nan |                nan |                nan |                      nan |                 nan | 2019-01-11           |             nan |                 nan |  
|         5 | nan                                                     | WALISON                | JOSE DE DEUS     | 025.783.061-84  |            1 |              nan | nan              | (62) 98173-1717 | walisonjosededeus@gmail.com       | 8875e52c1a9881bb0987b4d9cfba3a429fd39504267c349f8a774c373b5e74bbbdbdc16b57b6ef8112a5acce71b0e1e0aaf6c199ad736448181f904225bb09ed |            nan | 2019-01-11 13:14:23 |               nan | 2019-11-15 13:23:41 |   1.57382e+09 | 826eafb999985d2d1069a79f50362df41224dea2fc6f9365c53556b50358ac15d433ab957f9d86e6a2df3426940af6429ffe5fb477cad865bba1253c6d670765 |             0 |            0 |              1 |             nan |            nan |            nan |           nan |                    nan |                1 |                   nan |                   nan |             0 | nan                    | nan               |                 nan |              nan | nan                                                     |                      nan |                nan |                nan |                      nan |                 nan | 2019-01-11           |             nan |                 nan |  
|         7 | nan                                                     | FERNANDO CASTRO MORAIS | nan              | nan             |          nan |              nan | (64) 99699-0485  | nan             | fernandocastromoarais@hotmail.com | f701dadb9dfd474efd4d49751b3cdfb60944dc767782e0d5ab62830a74f40b5fd37fdacc0d13791dcff7000e681777cc234842808da694e4662be4cfef6dff32 |            nan | 2019-01-18 16:55:56 |               nan | nan                 | nan           | nan                                                                                                                              |            19 |            1 |              0 |             nan |            nan |            nan |           nan |                    nan |                0 |                     0 |                     0 |             1 | nan                    | nan               |                 nan |              nan | nan                                                     |                      nan |                nan |                nan |                      nan |                 nan | 2019-01-18           |             nan |                 nan |

---

## <a id='ws-users-address-csv'></a>ws_users_address.csv

**Total de Registros**: 201

**Total de Colunas**: 12

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | user_id | int64 | 1 |
| 2 | addr_id | int64 | 1 |
| 3 | addr_key | float64 | NULL |
| 4 | addr_name | object | Apartamento |
| 5 | addr_zipcode | object | 74823-430 |
| 6 | addr_street | object | Rua S 2 |
| 7 | addr_number | object | 598 |
| 8 | addr_complement | object | Ed. Hannover, Apto 404 |
| 9 | addr_district | object | Setor Bela Vista |
| 10 | addr_city | object | Goiânia |
| 11 | addr_state | object | GO |
| 12 | addr_country | object | Brasil |

### Amostra de Dados

|   user_id |   addr_id |   addr_key | addr_name     | addr_zipcode   | addr_street         | addr_number   | addr_complement                                     | addr_district        | addr_city      | addr_state   | addr_country   |  
|----------:|----------:|-----------:|:--------------|:---------------|:--------------------|:--------------|:----------------------------------------------------|:---------------------|:---------------|:-------------|:---------------|  
|         1 |         1 |        nan | Apartamento   | 74823-430      | Rua S 2             | 598           | Ed. Hannover, Apto 404                              | Setor Bela Vista     | Goiânia        | GO           | Brasil         |  
|        26 |         2 |        nan | Casa Fernanda | 74255-060      | Avenida C107        | 0             | Qd 51 lt 14                                         | Jardim América       | Goiânia        | GO           | Brasil         |  
|       161 |         8 |        nan | Residencial   | 74650-130      | Rua Dona Mariquinha | S/N           | Qd. 10 Lt 1 Cond. Portal Vale dos Rios Ap. 202A     | Setor Negrão de Lima | Goiânia        | GO           | Brasil         |  
|       133 |         9 |        nan | Minha casa    | 74810-210      | Rua 53              | 481           | Qd:B-10 Lt:24-28 Residencial Gran Espanã Aptº: 403A | Jardim Goiás         | Goiânia        | GO           | Brasil         |  
|       211 |        10 |        nan | Casa          | 75255-784      | Rua 1 A             | S/N           | QD. b LT. 13                                        | Parque Alvorada 2A   | Senador Canedo | GO           | Brasil         |

---

## <a id='ws-users-attachments-csv'></a>ws_users_attachments.csv

**Total de Registros**: 339

**Total de Colunas**: 6

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | attachments_id | int64 | 4 |
| 2 | user_id | int64 | 525 |
| 3 | attachments_name | object | Documentos  |
| 4 | attachments_registration_date | object | 2021-04-12 17:37:52 |
| 5 | attachments_path | object | files/2021/04/anexo-thaynara.pdf |
| 6 | attachments_type | int64 | 2 |

### Amostra de Dados

|   attachments_id |   user_id | attachments_name       | attachments_registration_date   | attachments_path                            |   attachments_type |  
|-----------------:|----------:|:-----------------------|:--------------------------------|:--------------------------------------------|-------------------:|  
|                4 |       525 | Documentos             | 2021-04-12 17:37:52             | files/2021/04/anexo-thaynara.pdf            |                  2 |  
|                5 |       525 | Documentos Certificado | 2021-04-12 17:39:10             | files/2021/04/anexo-thaynara-1618259972.pdf |                  2 |  
|                6 |       525 | Documentos             | 2021-04-12 17:39:39             | files/2021/04/anexo-thaynara-1618259997.pdf |                  2 |  
|                7 |       525 | Documentos             | 2021-04-12 17:40:04             | files/2021/04/anexo-thaynara-1618260018.pdf |                  2 |  
|                8 |       525 | Documentos             | 2021-04-12 17:40:26             | files/2021/04/anexo-thaynara-1618260039.pdf |                  2 |

---

## <a id='ws-users-especialidades-csv'></a>ws_users_especialidades.csv

**Total de Registros**: 182

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 5 |
| 2 | user_id | int64 | 1072 |
| 3 | especialidade_id | int64 | 25 |

### Amostra de Dados

|   id |   user_id |   especialidade_id |  
|-----:|----------:|-------------------:|  
|    5 |      1072 |                 25 |  
|    7 |       605 |                 25 |  
|   32 |      1805 |                 25 |  
|   33 |      1805 |                 29 |  
|   34 |      1805 |                 24 |

---

## <a id='ws-users-locales-csv'></a>ws_users_locales.csv

**Total de Registros**: 1,297

**Total de Colunas**: 2

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | user_id | int64 | 748 |
| 2 | local_id | int64 | 1 |

### Amostra de Dados

|   user_id |   local_id |  
|----------:|-----------:|  
|       748 |          1 |  
|      1060 |          1 |  
|       106 |          2 |  
|       708 |          1 |  
|      1385 |          1 |

---

## <a id='ws-users-notes-csv'></a>ws_users_notes.csv

**Total de Registros**: 0

**Total de Colunas**: 6

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | note_id | object | NULL |
| 2 | user_id | object | NULL |
| 3 | admin_id | object | NULL |
| 4 | note_text | object | NULL |
| 5 | note_datetime | object | NULL |
| 6 | note_status | object | NULL |


---

## <a id='ws-users-pagamentos-csv'></a>ws_users_pagamentos.csv

**Total de Registros**: 36

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 45 |
| 2 | user_id | int64 | 499 |
| 3 | pagamento_id | int64 | 6 |

### Amostra de Dados

|   id |   user_id |   pagamento_id |  
|-----:|----------:|---------------:|  
|   45 |       499 |              6 |  
|   47 |      1584 |              6 |  
|   50 |      1729 |              6 |  
|   54 |      1830 |              6 |  
|   88 |       609 |              6 |

---

## <a id='ws-users-permissions-csv'></a>ws_users_permissions.csv

**Total de Registros**: 25,182

**Total de Colunas**: 4

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | permission_id | int64 | 109 |
| 2 | user_id | int64 | 5 |
| 3 | permission_app | object | APP_USERS |
| 4 | permission_crud | int64 | 0 |

### Amostra de Dados

|   permission_id |   user_id | permission_app   |   permission_crud |  
|----------------:|----------:|:-----------------|------------------:|  
|             109 |         5 | APP_USERS        |                 0 |  
|             107 |         4 | APP_LOGS         |                 3 |  
|             106 |         4 | APP_REPORTS      |                 3 |  
|             105 |         4 | APP_CONFIG       |                 3 |  
|             104 |         4 | APP_CLIENTS      |                 3 |

---

## <a id='ws-users-profissoes-csv'></a>ws_users_profissoes.csv

**Total de Registros**: 296

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 18 |
| 2 | user_id | int64 | 421 |
| 3 | profissao_id | int64 | 1 |

### Amostra de Dados

|   id |   user_id |   profissao_id |  
|-----:|----------:|---------------:|  
|   18 |       421 |              1 |  
|   19 |       389 |              4 |  
|   20 |       878 |              7 |  
|   23 |      1072 |              3 |  
|   25 |       605 |              1 |

---

## <a id='ws-users-titulacoes-csv'></a>ws_users_titulacoes.csv

**Total de Registros**: 162

**Total de Colunas**: 3

### Esquema

| # | Nome da Coluna | Tipo de Dados | Exemplo |
|---|--------------|--------------|---------|
| 1 | id | int64 | 2 |
| 2 | user_id | int64 | 39 |
| 3 | titulacao_id | int64 | 7 |

### Amostra de Dados

|   id |   user_id |   titulacao_id |  
|-----:|----------:|---------------:|  
|    2 |        39 |              7 |  
|    9 |       240 |              6 |  
|   10 |       289 |              8 |  
|   18 |       426 |              8 |  
|   26 |       525 |              5 |

---

## Informações da Extração

- **Data e Hora**: 03/04/2025 11:32:55
- **Diretório**: D:\CODIGO\Clinica Larissa - tabelas aba\mysql_tables
- **Total de Arquivos**: 96
