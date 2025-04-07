export interface PlanoSaude {
  id: string;
  codigo_operadora?: string;
  registro_ans?: string;
  nome: string;
  tipo_plano?: string;
  abrangencia?: string;
  observacoes?: string;
  ativo: boolean;
  dados_contrato?: any;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  deleted_at?: string;
}

export interface PlanoSaudeFormData {
  nome: string;
  codigo_operadora?: string;
  registro_ans?: string;
  tipo_plano?: string;
  abrangencia?: string;
  observacoes?: string;
  ativo?: boolean;
  dados_contrato?: any;
}