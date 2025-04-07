{
  "tables": [
    {
      "name": "ps_schedule",
      "columns": [
        "schedule_id",
        "schedule_room_id",
        "schedule_especialidade_id",
        "schedule_local_id",
        "schedule_parent_id",
        "schedule_pacient_id",
        "schedule_pagamento_id",
        "schedule_date_start",
        "schedule_date_end",
        "schedule_qtd_sessions",
        "schedule_status",
        "schedule_room_rent_value",
        "schedule_fixed",
        "schedule_saldo_sessoes",
        "schedule_elegibilidade",
        "schedule_falta_do_profissional",
        "schedule_registration_date",
        "schedule_lastupdate",
        "parent_id"
      ]
    },
    {
      "name": "ws_users",
      "columns": [
        "user_id",
        "user_name",
        "user_lastname"
      ]
    },
    {
      "name": "ws_profissoes",
      "columns": [
        "profissao_id",
        "profissao_name",
        "profissao_status"
      ]
    },
    {
      "name": "ws_users_profissoes",
      "columns": [
        "profissao_id",
        "user_id"
      ]
    },
    {
      "name": "ws_especialidades",
      "columns": [
        "especialidade_id",
        "especialidade_name"
      ]
    },
    {
      "name": "ws_users_especialidades",
      "columns": [
        "especialidade_id",
        "user_id",
        "especialidade_status"
      ]
    },
    {
      "name": "ps_schedule_professionals",
      "columns": [
        "professional_id",
        "schedule_id",
        "substituido"
      ]
    },
    {
      "name": "ps_locales",
      "columns": [
        "local_id",
        "local_nome"
      ]
    },
    {
      "name": "ps_care_rooms",
      "columns": [
        "room_id",
        "room_local_id",
        "room_name"
      ]
    },
    {
      "name": "ps_clients_professional",
      "columns": [
        "professional_id",
        "user_id",
        "client_id"
      ]
    },
    {
      "name": "ws_pagamentos",
      "columns": [
        "pagamento_id",
        "pagamento_nome",
        "pagamento_descricao"
      ]
    },
    {
      "name": "ws_pagamentos_x_codigos_faturamento",
      "columns": [
        "id",
        "pagamento_id",
        "codigo_faturamento_id",
        "codigo_faturamento_descricao"
      ]
    }
  ]
}


| Português (PT-BR)          | Inglês (EN)                         | Notas                                                                 |
|----------------------------|-------------------------------------|-----------------------------------------------------------------------|
| agendamentos               | ps_schedule                         |                                                                       |
| usuarios_aba               | ws_users                            |                                                                       |
| profissoes                 | ws_profissoes                       |                                                                       |
| usuarios_profissoes        | ws_users_profissoes                 |                                                                       |
| especialidades             | ws_especialidades                   |                                                                       |
| usuarios_especialidades    | ws_users_especialidades             |                                                                       |
| agendamentos_profissionais | ps_schedule_professionals           |                                                                       |
| locais                     | ps_locales                          |                                                                       |
| salas                      | ps_care_rooms                       |                                                                       |
| usuarios_profissoes        | ps_clients_professional             | (**Atenção**: Duplicado? Verificar mapeamento correto)                  |
| tipo_pagamento             | ws_pagamentos                       | Nova tabela para armazenar tipos de pagamento                         |
| procedimentos (update)     | ws_pagamentos_x_codigos_faturamento | Atualiza `procedimentos` com `pagamento_id_origem` e `codigo_faturamento_id_origem` |


Tabela ps_schedule no MySql:


| Campo                        | Tipo              | Null | Chave | Padrão     |
|-----------------------------|-------------------|------|-------|------------|
| schedule_id                 | int               | NO   | PRI   | NULL       |
| schedule_date_start         | datetime          | NO   | MUL   | NULL       |
| schedule_date_end           | datetime          | NO   |       | NULL       |
| schedule_pacient_id         | int               | YES  | MUL   | NULL       |
| schedule_pagamento_id       | int               | YES  |       | NULL       |
| schedule_room_id            | int               | NO   | MUL   | NULL       |
| schedule_qtd_sessions       | int               | YES  |       | NULL       |
| schedule_status             | int               | YES  |       | 0          |
| schedule_room_rent_value    | decimal(11,2)     | YES  |       | 0.00       |
| schedule_fixed              | char(1)           | YES  |       | N          |
| schedule_especialidade_id   | int               | YES  | MUL   | NULL       |
| schedule_local_id           | int               | YES  |       | NULL       |
| schedule_saldo_sessoes      | int               | YES  |       | NULL       |
| schedule_eligibilidade      | enum('Sim','Não') | YES  |       | Não        |
| schedule_falta_do_profissional | enum('Sim','Não') | YES |    | Não        |
| schedule_parent_id          | int               | YES  |       | NULL       |
| schedule_registration_date  | datetime          | NO   |       | NULL       |
| schedule_lastupdate         | timestamp         | YES  |       | CURRENT_TIMESTAMP |
| parent_id                   | int unsigned      | YES  |       | NULL       |
| schedule_codigo_faturamento | varchar(45)       | YES  |       | NULL       |


Tabela salas (ps_care_rooms)

Segue a tabela extraída da nova imagem:

| Campo                  | Tipo            | Null | Chave | Padrão              |
|------------------------|------------------|------|-------|----------------------|
| room_id               | int              | NO   | PRI   | NULL                 |
| room_name             | varchar(255)     | YES  |       | NULL                 |
| room_description      | text             | YES  |       | NULL                 |
| room_type             | int              | YES  |       | 0                    |
| room_status           | int              | YES  |       | 0                    |
| room_registration_date| datetime         | NO   |       | NULL                 |
| room_lastupdate       | timestamp         | NO   |       | CURRENT_TIMESTAMP    |
| room_local_id         | int              | NO   |       | 1                    |
| multiple              | tinyint          | NO   |       | 0                    |
| room_capacidade       | int              | YES  |       | 1                    |

