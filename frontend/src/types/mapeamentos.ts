export interface MapeamentoPaciente {
  id_mysql: number;
  id_supabase: string;
}

export interface MapeamentoSala {
  id_mysql: number;
  id_supabase: string;
}

export interface MapeamentoEspecialidade {
  id_mysql: number;
  id_supabase: string;
}

export interface MapeamentoLocal {
  id_mysql: number;
  id_supabase: string;
}

export interface MapeamentoPagamento {
  id_mysql: number;
  id_supabase: string;
}

export type TipoMapeamento = 'pacientes' | 'salas' | 'especialidades' | 'locais' | 'pagamentos';