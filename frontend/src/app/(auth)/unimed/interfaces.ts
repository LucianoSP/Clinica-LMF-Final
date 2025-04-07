// Interfaces para a página de monitoramento Unimed

// Interface para guias processadas
export interface GuiaProcessada {
  id: number;
  carteira: string;
  nome_beneficiario: string;
  codigo_procedimento: string;
  data_atendimento: string;
  data_execucao: string;
  numero_guia: string;
  biometria: string;
  nome_profissional: string;
  created_at: string;
}

// Interface para o status de processamento (atualizada)
export interface ProcessingStatus {
  id: string;
  task_id: string;
  status: string;
  total_guides: number;
  processed_guides: number;
  retry_guides: number;
  error: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  start_date: string | null;
  end_date: string | null;
  max_guides: number | null;
  started_at: string;
  error_at: string | null;
  last_update: string | null;
  total_execucoes: number | null;
}

// Interface para o status de captura
export interface CaptureStatus {
  status: string;
  total_guides: number;
  processed_guides: number;
  error: string | null;
  updated_at: string;
}

// Interface para o histórico de execução
export interface ExecutionHistory extends ProcessingStatus {
  duration_seconds: number | null;
}

// Interface para métricas por hora
export interface HourlyMetrics {
  hour: number;
  total_executions: number;
  total_guides: number;
  processed_guides: number;
  errors: number;
}

// Interface atualizada para sessões da Unimed
export interface UnimedSessao {
  id: string;
  numero_guia: string;
  data_atendimento_completa: string;
  data_execucao: string;
  paciente_nome: string;
  paciente_carteirinha: string;
  codigo_ficha: string;
  profissional_executante: string;
  conselho_profissional: string;
  numero_conselho: string;
  uf_conselho: string;
  codigo_cbo: string;
  origem: string;
  status: string;
  error: string | null;
  task_id: string;
  created_at: string;
  updated_at: string;
  processed_at: string | null;
}

// Interface para logs de processamento
export interface SessaoLog {
  id: string;
  sessao_id: string;
  execution_id: string | null;
  status: string;
  mensagem: string;
  detalhes: any;
  created_at: string;
  updated_at: string;
}

// Interface para o dashboard de resumo
export interface DashboardSummary {
  total_tasks: number;
  tasks_today: number;
  total_guides: number;
  total_processed: number;
  success_rate: number;
  avg_processing_time: number;
  pending_sessions: number;
  error_sessions: number;
}

// Interface para detalhes de execução
export interface ExecutionDetails {
  id: string;
  task_id: string;
  browser_info: string;
  system_info: string;
  created_at: string;
  updated_at: string;
} 