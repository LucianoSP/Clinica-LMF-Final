export interface Paciente {
  id: string;
  nome: string;
  id_origem?: string;
  numero: number | null;
  email?: string;
  cpf?: string;
  rg?: string;
  data_nascimento?: string;
  foto?: string;
  nome_responsavel?: string;
  nome_pai?: string;
  nome_mae?: string;
  sexo?: string;
  cep?: string;
  endereco?: string;
  complemento?: string;
  bairro?: string;
  cidade?: string;
  cidade_id?: number;
  estado?: string;
  forma_pagamento?: number;
  valor_consulta?: number;
  profissional_id?: string;  // Alterado de number para string para aceitar UUID
  escola_nome?: string;
  escola_ano?: string;
  escola_professor?: string;
  escola_periodo?: string;
  escola_contato?: string;
  patologia_id?: number;
  tem_supervisor?: boolean;
  supervisor_id?: number;
  tem_avaliacao_luria?: boolean;
  avaliacao_luria_data_inicio_treinamento?: string;
  avaliacao_luria_reforcadores?: string;
  avaliacao_luria_obs_comportamento?: string;
  numero_carteirinha?: string;
  cpf_responsavel?: string;
  crm_medico?: string;
  nome_medico?: string;
  pai_nao_declarado?: boolean;
  telefone?: string;
  observacoes?: string;
  status?: 'Ativo' | 'Inativo';
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  deleted_at?: string;
}

export interface PacientesResponse {
  success: boolean;
  data: null;
  error: null;
  message: null;
  items: Paciente[];
  total: number;
  page: number;
  total_pages: number;
  has_more: boolean;
}