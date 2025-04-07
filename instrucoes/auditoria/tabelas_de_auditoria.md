  ```mermaid
  erDiagram
      FICHAS {
          uuid id PK
          string codigo_ficha
          uuid guia_id FK
          string numero_guia
          uuid agendamento_id FK
          enum status
          date data_atendimento
          uuid storage_id FK
      }

      SESSOES {
          uuid id PK
          uuid ficha_id FK
          uuid guia_id FK
          date data_sessao
          uuid procedimento_id FK
          enum status
          boolean possui_assinatura
          string numero_guia
          string codigo_ficha
          string profissional_executante
          enum status_biometria
      }

      EXECUCOES {
          uuid id PK
          uuid guia_id FK
          uuid sessao_id FK
          date data_execucao
          date data_atendimento
          string paciente_nome
          string paciente_carteirinha
          string numero_guia
          string codigo_ficha
          boolean codigo_ficha_temp
          uuid usuario_executante FK
          string origem
          string ip_origem
          integer ordem_execucao
          enum status_biometria
          string conselho_profissional
          string numero_conselho
          string uf_conselho
          string codigo_cbo
          string profissional_executante
      }

      GUIAS {
          uuid id PK
          string numero_guia
          enum status
          integer quantidade_autorizada
          integer quantidade_executada
          date data_validade
          date data_solicitacao
          date data_autorizacao
      }

      DIVERGENCIAS {
          uuid id PK
          string numero_guia
          enum tipo_divergencia
          string descricao
          string paciente_nome
          string codigo_ficha
          date data_execucao
          date data_atendimento
          string carteirinha
          string prioridade
          enum status
          timestamptz data_identificacao
          timestamptz data_resolucao
          uuid resolvido_por FK
          jsonb detalhes
          uuid ficha_id FK
          uuid execucao_id FK
          uuid sessao_id FK
          uuid paciente_id FK
          integer tentativas_resolucao
      }

      AUDITORIA_EXECUCOES {
          uuid id PK
          timestamptz data_execucao
          date data_inicial
          date data_final
          integer total_protocolos
          integer total_divergencias
          integer total_fichas
          integer total_guias
          integer total_execucoes
          integer total_resolvidas
          jsonb divergencias_por_tipo
          jsonb metricas_adicionais
          string status
      }

      STORAGE {
          uuid id PK
          string nome
          string url
          string tipo_referencia
          integer size
          string content_type
      }

      FICHAS ||--o{ SESSOES : "contém"
      GUIAS ||--o{ FICHAS : "gera"
      GUIAS ||--o{ SESSOES : "autoriza"
      GUIAS ||--o{ EXECUCOES : "registra"
      SESSOES ||--o{ EXECUCOES : "registra"
      SESSOES ||--o{ DIVERGENCIAS : "pode gerar"
      EXECUCOES ||--o{ DIVERGENCIAS : "pode gerar"
      FICHAS ||--o{ DIVERGENCIAS : "relaciona"
      STORAGE ||--o{ FICHAS : "armazena documentos"
      PACIENTES ||--o{ DIVERGENCIAS : "associado a"