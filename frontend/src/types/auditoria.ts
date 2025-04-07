export interface AuditoriaResultado {
  total_protocolos: number;
  total_divergencias: number;
  total_resolvidas: number;
  total_pendentes: number;
  total_fichas: number;
  total_execucoes: number;
  tempo_execucao: string;
  divergencias_por_tipo: {
    execucao_sem_ficha?: number;
    ficha_sem_execucao?: number;
    data_divergente?: number;
    ficha_sem_assinatura?: number;
    guia_vencida?: number;
    quantidade_excedida?: number;
    duplicidade?: number;
    [key: string]: number | undefined;
  };
  data_execucao: string;
}

export interface Divergencia {
  id: string;
  numero_guia: string;
  tipo: string;
  tipo_divergencia?: string;
  descricao: string;
  paciente_nome: string;
  codigo_ficha: string;
  data_execucao: string;
  data_atendimento: string;
  carteirinha: string;
  prioridade: string;
  status: string;
  data_identificacao: string;
  data_resolucao?: string;
  resolvido_por?: string;
  detalhes?: any;
  ficha_id?: string;
  execucao_id?: string;
  sessao_id?: string;
  created_at: string;
  updated_at: string;
} 