import { Carteirinha } from "./carteirinha";
import { Ficha } from "./ficha";
import { Guia } from "./guia";
import { Paciente } from "./paciente";

export interface DashboardStats {
  total_carteirinhas: number;
  total_guias: number;
  total_fichas: number;
  fichas_pendentes: number;
  fichas_conferidas: number;
  fichas_faturadas: number;
  fichas_canceladas: number;
  sessoes_totais: number;
  sessoes_realizadas: number;
  sessoes_pendentes: number;
  valor_faturado: number;
}

export interface PacienteDashboard {
  paciente: Paciente | null;
  stats: {
    fichas_pendentes: number;
    fichas_conferidas: number;
    fichas_faturadas: number;
    fichas_canceladas: number;
    sessoes_totais: number;
    sessoes_realizadas: number;
    sessoes_pendentes: number;
    valor_faturado: number;
  };
  carteirinhas: Carteirinha[];
  guias: Guia[];
}

export type PacienteSearchResult = Pick<Paciente, 'id' | 'nome' | 'cpf' | 'data_nascimento' | 'foto'>;